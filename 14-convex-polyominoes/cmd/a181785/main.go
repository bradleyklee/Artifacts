package main

import (
	"bufio"
	"flag"
	"fmt"
	"os"
	"runtime"
	"sort"
	"sync"
	"time"

	"a181785go/internal/poly"
)

type Key = poly.Key
type Bucket map[Key]struct{}

type Level struct {
	N          int
	Count      int
	Candidates uint64
	Stats      poly.Stats
	Seconds    float64
}

func workersDefault() int {
	n := runtime.NumCPU()
	if n > 12 {
		n = 12
	}
	if n < 1 {
		n = 1
	}
	return n
}

func keysOf(b Bucket) []Key {
	out := make([]Key, 0, len(b))
	for k := range b {
		out = append(out, k)
	}
	// Go intentionally randomizes map iteration.  Sorting makes work partitioning
	// and progress traces reproducible without changing the underlying set logic.
	sort.Slice(out, func(i, j int) bool { return poly.KeyLess(out[i], out[j]) })
	return out
}

func merge(dst Bucket, src Bucket) (fresh, dup uint64) {
	for k := range src {
		if _, ok := dst[k]; ok {
			dup++
		} else {
			dst[k] = struct{}{}
			fresh++
		}
	}
	return
}

func addStats(dst *poly.Stats, src poly.Stats) {
	dst.Active += src.Active
	dst.Extensions += src.Extensions
	dst.OrdinaryTransitions += src.OrdinaryTransitions
	dst.PromotedTransitions += src.PromotedTransitions
	dst.ScheduledNew += src.ScheduledNew
	dst.ScheduledDuplicate += src.ScheduledDuplicate
	dst.OverBoundDropped += src.OverBoundDropped
	if src.OverBoundMinTarget != 0 && (dst.OverBoundMinTarget == 0 || src.OverBoundMinTarget < dst.OverBoundMinTarget) {
		dst.OverBoundMinTarget = src.OverBoundMinTarget
	}
	if src.OverBoundMaxTarget > dst.OverBoundMaxTarget {
		dst.OverBoundMaxTarget = src.OverBoundMaxTarget
	}
	if src.MaxCompletionJump > dst.MaxCompletionJump {
		dst.MaxCompletionJump = src.MaxCompletionJump
	}
}

// Fast recurrence: discard a one-cell extension as soon as it is non-convex.
func fast(maxN, workers int) ([]Level, error) {
	if maxN < 1 || maxN > poly.MaxN {
		return nil, fmt.Errorf("max-n must be 1..%d", poly.MaxN)
	}
	levels := make([]Level, maxN+1)
	cur := Bucket{poly.Canonical([]poly.Point{{0, 0}}): {}}
	levels[1] = Level{N: 1, Count: 1}
	for n := 1; n < maxN; n++ {
		start := time.Now()
		source := keysOf(cur)
		chunks := workers
		if chunks > len(source) {
			chunks = len(source)
		}
		if chunks < 1 {
			chunks = 1
		}
		locals := make([]Bucket, chunks)
		var wg sync.WaitGroup
		for w := 0; w < chunks; w++ {
			lo := len(source) * w / chunks
			hi := len(source) * (w + 1) / chunks
			locals[w] = make(Bucket, (hi-lo)*3)
			wg.Add(1)
			go func(w, lo, hi int) {
				defer wg.Done()
				local := locals[w]
				for _, key := range source[lo:hi] {
					pts := poly.Decode(key, n)
					for _, add := range poly.BoundaryExtensions(pts) {
						h, count := poly.ChildHullCount(pts, add)
						_ = h
						if count != n+1 {
							continue
						}
						child := make([]poly.Point, n+1)
						copy(child, pts)
						child[n] = add
						local[poly.Canonical(child)] = struct{}{}
					}
				}
			}(w, lo, hi)
		}
		wg.Wait()
		next := make(Bucket, len(cur)*3)
		for _, local := range locals {
			merge(next, local)
		}
		// Store the cost against the source level being expanded.  This makes
		// fast and completion timings comparable in the terminal table.
		levels[n].Seconds = time.Since(start).Seconds()
		levels[n+1] = Level{N: n + 1, Count: len(next), Candidates: uint64(len(next))}
		cur = next
	}
	return levels, nil
}

type localCompletion struct {
	buckets map[int]Bucket
	stats   poly.Stats
}

// Complete is the forward-promoting breadth-first algorithm. An invalid child
// is never retained. Its exact lattice-hull closure is scheduled directly into
// the bucket equal to its completed cardinality, where it will later expand.
func complete(maxN, workers int) ([]Level, error) {
	if maxN < 1 || maxN > poly.MaxN {
		return nil, fmt.Errorf("max-n must be 1..%d", poly.MaxN)
	}
	buckets := make([]Bucket, maxN+1)
	for i := 1; i <= maxN; i++ {
		buckets[i] = make(Bucket)
	}
	buckets[1][poly.Canonical([]poly.Point{{0, 0}})] = struct{}{}
	levels := make([]Level, maxN+1)
	for n := 1; n <= maxN; n++ {
		start := time.Now()
		current := buckets[n]
		level := Level{N: n, Count: len(current)}
		// The stated bound is a true horizon: no expansion from final bucket.
		if n == maxN {
			level.Seconds = time.Since(start).Seconds()
			levels[n] = level
			continue
		}
		source := keysOf(current)
		chunks := workers
		if chunks > len(source) {
			chunks = len(source)
		}
		if chunks < 1 {
			chunks = 1
		}
		locals := make([]localCompletion, chunks)
		var wg sync.WaitGroup
		for w := 0; w < chunks; w++ {
			lo := len(source) * w / chunks
			hi := len(source) * (w + 1) / chunks
			locals[w].buckets = make(map[int]Bucket)
			wg.Add(1)
			go func(w, lo, hi int) {
				defer wg.Done()
				out := &locals[w]
				for _, key := range source[lo:hi] {
					pts := poly.Decode(key, n)
					for _, add := range poly.BoundaryExtensions(pts) {
						out.stats.Extensions++
						h, target := poly.ChildHullCount(pts, add)
						if target < n+1 {
							panic("closure cardinality decreased")
						}
						jump := target - (n + 1)
						if jump > out.stats.MaxCompletionJump {
							out.stats.MaxCompletionJump = jump
						}
						if target > maxN {
							out.stats.OverBoundDropped++
							if out.stats.OverBoundMinTarget == 0 || target < out.stats.OverBoundMinTarget {
								out.stats.OverBoundMinTarget = target
							}
							if target > out.stats.OverBoundMaxTarget {
								out.stats.OverBoundMaxTarget = target
							}
							continue
						}
						var ckey Key
						promoted := target > n+1
						if promoted {
							child := make([]poly.Point, n+1)
							copy(child, pts)
							child[n] = add
							closed := poly.Closure(child, h, target)
							if !poly.IsEdgeConnected(closed) || !poly.IsLatticeConvex(closed) {
								panic("completion invariant failure")
							}
							ckey = poly.Canonical(closed)
						} else {
							child := make([]poly.Point, n+1)
							copy(child, pts)
							child[n] = add
							ckey = poly.Canonical(child)
						}
						if promoted {
							out.stats.PromotedTransitions++
						} else {
							out.stats.OrdinaryTransitions++
						}
						dest := out.buckets[target]
						if dest == nil {
							dest = make(Bucket)
							out.buckets[target] = dest
						}
						dest[ckey] = struct{}{}
					}
				}
			}(w, lo, hi)
		}
		wg.Wait()
		var total poly.Stats
		total.Active = uint64(len(current))
		for w := range locals {
			addStats(&total, locals[w].stats)
			targets := make([]int, 0, len(locals[w].buckets))
			for t := range locals[w].buckets {
				targets = append(targets, t)
			}
			sort.Ints(targets)
			for _, t := range targets {
				fresh, _ := merge(buckets[t], locals[w].buckets[t])
				total.ScheduledNew += fresh
			}
		}
		total.ScheduledDuplicate = total.OrdinaryTransitions + total.PromotedTransitions - total.ScheduledNew
		level.Stats = total
		level.Candidates = total.Extensions
		level.Seconds = time.Since(start).Seconds()
		levels[n] = level
		// Processed bucket has no future role and can be reclaimed.
		buckets[n] = nil
	}
	return levels, nil
}

func writeFast(out *bufio.Writer, levels []Level) {
	fmt.Fprintln(out, "algorithm,n,count,candidates,seconds")
	for n := 1; n < len(levels); n++ {
		l := levels[n]
		fmt.Fprintf(out, "fast,%d,%d,%d,%.9f\n", n, l.Count, l.Candidates, l.Seconds)
	}
}

func writeComplete(out *bufio.Writer, levels []Level, horizon int) {
	fmt.Fprintln(out, "algorithm,max_n,n,count,extensions,ordinary_transitions,promoted_transitions,scheduled_new,scheduled_duplicate,over_bound_dropped,over_bound_min_target,over_bound_max_target,max_completion_jump,seconds")
	for n := 1; n < len(levels); n++ {
		l := levels[n]
		s := l.Stats
		fmt.Fprintf(out, "complete,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%.9f\n",
			horizon, n, l.Count, s.Extensions, s.OrdinaryTransitions, s.PromotedTransitions, s.ScheduledNew, s.ScheduledDuplicate, s.OverBoundDropped, s.OverBoundMinTarget, s.OverBoundMaxTarget, s.MaxCompletionJump, l.Seconds)
	}
}

func test() error {
	if !poly.IsLatticeConvex([]poly.Point{{0, 0}}) {
		return fmt.Errorf("single point")
	}
	if poly.IsLatticeConvex([]poly.Point{{0, 0}, {2, 2}}) {
		return fmt.Errorf("segment defect")
	}
	u := []poly.Point{{0, 0}, {0, 1}, {0, 2}, {1, 2}, {2, 2}}
	uh := poly.Hull(u)
	uc := poly.Closure(u, uh, poly.LatticePointCount(uh))
	if len(uc) != 6 || !poly.IsEdgeConnected(uc) || !poly.IsLatticeConvex(uc) {
		return fmt.Errorf("U completion")
	}
	if poly.Canonical(u) != poly.Canonical([]poly.Point{{0, 0}, {0, -1}, {0, -2}, {-1, -2}, {-2, -2}}) {
		return fmt.Errorf("D4 canonicalization")
	}
	return nil
}

func comma(n uint64) string {
	text := fmt.Sprintf("%d", n)
	first := len(text) % 3
	if first == 0 {
		first = 3
	}
	out := make([]byte, 0, len(text)+(len(text)-1)/3)
	out = append(out, text[:first]...)
	for i := first; i < len(text); i += 3 {
		out = append(out, ',')
		out = append(out, text[i:i+3]...)
	}
	return string(out)
}

func elapsed(seconds float64) string {
	return fmt.Sprintf("%.3fs", seconds)
}

// runBoth prints a terminal-oriented fixed-width report.  The final output
// line is deliberately an unlabelled OEIS-ready comma-separated sequence.
func runBoth(out *bufio.Writer, maxN, workers int) error {
	allStart := time.Now()
	fastStart := time.Now()
	f, err := fast(maxN, workers)
	if err != nil {
		return err
	}
	fastSeconds := time.Since(fastStart).Seconds()
	completeStart := time.Now()
	c, err := complete(maxN, workers)
	if err != nil {
		return err
	}
	completeSeconds := time.Since(completeStart).Seconds()
	totalSeconds := time.Since(allStart).Seconds()

	for n := 1; n <= maxN; n++ {
		if f[n].Count != c[n].Count {
			return fmt.Errorf("CHECK FAIL at n=%d: fast=%d complete=%d", n, f[n].Count, c[n].Count)
		}
	}

	fmt.Fprintf(out, "A181785 dual BFS | horizon=%d | workers=%d of %d logical CPUs\n", maxN, workers, runtime.NumCPU())
	fmt.Fprintln(out, "--------------------------------------------------------------------------------")
	fmt.Fprintf(out, "%2s | %10s | %-5s | %10s | %4s | %10s | %9s | %9s\n",
		"n", "a(n)", "check", "promoted", "jump", ">horizon", "fast(s)", "full(s)")
	fmt.Fprintln(out, "--------------------------------------------------------------------------------")
	for n := 1; n <= maxN; n++ {
		count := comma(uint64(f[n].Count))
		promoted, jump, dropped, fastTime, fullTime := "--", "--", "--", "--", "--"
		if n < maxN {
			s := c[n].Stats
			promoted = comma(s.PromotedTransitions)
			jump = fmt.Sprintf("%d", s.MaxCompletionJump)
			dropped = comma(s.OverBoundDropped)
			fastTime = elapsed(f[n].Seconds)
			fullTime = elapsed(c[n].Seconds)
		}
		fmt.Fprintf(out, "%2d | %10s | %-5s | %10s | %4s | %10s | %9s | %9s\n",
			n, count, "OK", promoted, jump, dropped, fastTime, fullTime)
	}
	fmt.Fprintln(out, "--------------------------------------------------------------------------------")
	fmt.Fprintf(out, "all checks OK | fast=%s | full=%s | total=%s\n",
		elapsed(fastSeconds), elapsed(completeSeconds), elapsed(totalSeconds))
	fmt.Fprintf(out, "OEIS copy/paste (n=1..%d):\n", maxN)
	for n := 1; n <= maxN; n++ {
		if n > 1 {
			fmt.Fprint(out, ",")
		}
		fmt.Fprint(out, f[n].Count)
	}
	fmt.Fprintln(out)
	return nil
}

func main() {
	mode := flag.String("mode", "both", "fast | complete | both | compare | test")
	maxN := flag.Int("max-n", 24, "calculation horizon")
	workers := flag.Int("workers", workersDefault(), "worker count")
	flag.Parse()
	if *workers < 1 {
		fmt.Fprintln(os.Stderr, "workers must be positive")
		os.Exit(2)
	}
	runtime.GOMAXPROCS(*workers)
	if err := test(); err != nil {
		fmt.Fprintln(os.Stderr, "self-test failed:", err)
		os.Exit(3)
	}
	out := bufio.NewWriter(os.Stdout)
	defer out.Flush()
	if *mode != "both" && *mode != "compare" {
		fmt.Fprintf(out, "config,mode=%s,max_n=%d,workers=%d,num_cpu=%d\n", *mode, *maxN, *workers, runtime.NumCPU())
	}
	switch *mode {
	case "test":
		fmt.Fprintln(out, "hull utility tests: PASS")
	case "fast":
		l, err := fast(*maxN, *workers)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		writeFast(out, l)
	case "complete":
		l, err := complete(*maxN, *workers)
		if err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(2)
		}
		writeComplete(out, l, *maxN)
	case "both", "compare":
		if err := runBoth(out, *maxN, *workers); err != nil {
			// Flush the configuration line and any verified prefix before reporting
			// the discrepancy, then return a distinct failure status.
			out.Flush()
			fmt.Fprintln(os.Stderr, err)
			os.Exit(4)
		}
	default:
		fmt.Fprintln(os.Stderr, "unknown mode", *mode)
		os.Exit(2)
	}
}
