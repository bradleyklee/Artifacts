package verification

import (
	"fmt"
	"sort"
	"testing"

	sl "verifiedskiplist/implementation/skiplist"
)

func TestAllDeletionOrdersThrough8FromEveryFullShape(t *testing.T) {
	const maxN = 8
	for n := 1; n <= maxN; n++ {
		keys := make([]int, n)
		for i := range keys {
			keys[i] = i
		}
		full := map[string]*sl.List[int, int]{}
		permute(keys, func(p []int) {
			s := sl.New[int, int](intOrder)
			for _, k := range p {
				s.Insert(k, k)
			}
			if err := s.Validate(); err != nil {
				t.Fatalf("n=%d insertion=%v: %v", n, p, err)
			}
			sig := s.ShapeSignature()
			if _, ok := full[sig]; !ok {
				full[sig] = s
			}
		})
		orders := 0
		steps := 0
		sigs := make([]string, 0, len(full))
		for sig := range full {
			sigs = append(sigs, sig)
		}
		sort.Strings(sigs)
		for _, sig := range sigs {
			base := full[sig]
			permute(keys, func(order []int) {
				s := base.CloneForVerification()
				ref := map[int]int{}
				for _, k := range keys {
					ref[k] = k
				}
				for _, k := range order {
					if !s.Delete(k) {
						t.Fatalf("n=%d shape=%s order=%v missing=%d", n, sig, order, k)
					}
					delete(ref, k)
					assertIntModel(t, s, ref)
					steps++
				}
				orders++
			})
		}
		t.Logf("n=%d full_shapes=%d deletion_orders=%d validated_steps=%d PASS", n, len(full), orders, steps)
	}
}

func TestExhaustiveFixedUniverseMixedGraph(t *testing.T) {
	const universe = 12
	start := sl.New[int, int](intOrder)
	q := []*sl.List[int, int]{start}
	seen := map[string]bool{start.DebugSignature(func(k int) string { return fmt.Sprint(k) }): true}
	transitions := 0
	maxDepth := 0
	branches := map[string]int{}
	for head := 0; head < len(q); head++ {
		cur := q[head]
		if cur.Depth() > maxDepth {
			maxDepth = cur.Depth()
		}
		for k := 0; k < universe; k++ {
			for _, ins := range []bool{true, false} {
				n := cur.CloneForVerification()
				n.SetVerificationTrace(func(ev string) { branches[ev]++ })
				if ins {
					n.Insert(k, k)
				} else {
					n.Delete(k)
				}
				transitions++
				if err := n.Validate(); err != nil {
					t.Fatalf("state=%s op insert=%v key=%d: %v", cur.DebugSignature(func(k int) string { return fmt.Sprint(k) }), ins, k, err)
				}
				sig := n.DebugSignature(func(k int) string { return fmt.Sprint(k) })
				if !seen[sig] {
					seen[sig] = true
					n.SetVerificationTrace(nil)
					q = append(q, n)
				}
			}
		}
	}
	if len(seen) != 14280 || transitions != 342720 {
		t.Fatalf("census drift: states=%d transitions=%d", len(seen), transitions)
	}
	for _, name := range []string{"D1_RECURSE", "D1_MERGE", "D2_TOP", "D2_MERGE_RIGHT", "D2_MERGE_LEFT", "D2_RECURSE_RIGHT", "D2_RECURSE_LEFT", "D3_SHIFT_RIGHT", "D4_LOCAL", "D5_LOCAL"} {
		if branches[name] == 0 {
			t.Fatalf("branch not exercised: %s", name)
		}
	}
	t.Logf("universe=%d states=%d transitions=%d max_depth=%d branches=%v PASS", universe, len(seen), transitions, maxDepth, branches)
}

func TestExhaustiveMixedKeyValueGraph(t *testing.T) {
	const keyUniverse = 5
	const valueUniverse = 4
	type state struct {
		s   *sl.List[int, int]
		ref map[int]int
	}
	cloneRef := func(m map[int]int) map[int]int {
		z := make(map[int]int, len(m))
		for k, v := range m {
			z[k] = v
		}
		return z
	}
	signature := func(s *sl.List[int, int], ref map[int]int) string {
		return s.DebugSignature(func(k int) string { return fmt.Sprintf("%d=%d", k, ref[k]) })
	}
	start := state{s: sl.New[int, int](intOrder), ref: map[int]int{}}
	q := []state{start}
	seen := map[string]bool{signature(start.s, start.ref): true}
	transitions := 0
	branches := map[string]int{}
	for head := 0; head < len(q); head++ {
		cur := q[head]
		for k := 0; k < keyUniverse; k++ {
			n := cur.s.CloneForVerification()
			n.SetVerificationTrace(func(ev string) { branches[ev]++ })
			nr := cloneRef(cur.ref)
			n.Delete(k)
			delete(nr, k)
			transitions++
			assertIntModel(t, n, nr)
			sig := signature(n, nr)
			if !seen[sig] {
				seen[sig] = true
				n.SetVerificationTrace(nil)
				q = append(q, state{n, nr})
			}
			for v := 0; v < valueUniverse; v++ {
				n := cur.s.CloneForVerification()
				n.SetVerificationTrace(func(ev string) { branches[ev]++ })
				nr := cloneRef(cur.ref)
				n.Insert(k, v)
				nr[k] = v
				transitions++
				assertIntModel(t, n, nr)
				sig := signature(n, nr)
				if !seen[sig] {
					seen[sig] = true
					n.SetVerificationTrace(nil)
					q = append(q, state{n, nr})
				}
			}
		}
	}
	t.Logf("keys=%d values=%d states=%d transitions=%d branches=%v PASS", keyUniverse, valueUniverse, len(seen), transitions, branches)
}
