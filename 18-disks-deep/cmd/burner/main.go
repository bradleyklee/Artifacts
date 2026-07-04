// burner produces streamed, exact two-body ledgers for the retained 12/24-gon
// seeds.  It is intentionally separate from cmd/lattice: lattice remains the
// broad reference implementation and this command is the profiled deep runner.
package main

import (
	"bufio"
	"compress/gzip"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"math/big"
	"os"
	"path/filepath"
	"runtime"
	"strconv"
	"strings"
	"time"

	"latticegeometry/internal/burner"
	"latticegeometry/internal/engine"
)

type scalar struct {
	A, B, C, D string `json:"a,omitempty"`
}

// scalar needs explicit field tags because Go cannot infer four distinct tags
// from a grouped declaration.
type scalarWire struct {
	A string `json:"a"`
	B string `json:"b"`
	C string `json:"c"`
	D string `json:"d"`
}
type vecWire struct {
	X scalarWire `json:"x"`
	Y scalarWire `json:"y"`
}
type bodyWire struct {
	Position vecWire `json:"position"`
	Velocity vecWire `json:"velocity"`
}
type eventWire struct {
	Kind   string  `json:"kind"`
	Bodies []int   `json:"bodies"`
	Face   *int    `json:"face,omitempty"`
	Wall   *string `json:"wall,omitempty"`
}
type metricWire struct {
	MaxAbsNumerator    string `json:"max_abs_numerator"`
	MaxDenominator     string `json:"max_denominator"`
	MaxNumeratorBits   int    `json:"max_numerator_bits"`
	MaxDenominatorBits int    `json:"max_denominator_bits"`
}
type stateWire struct {
	Positions  metricWire `json:"positions"`
	Velocities metricWire `json:"velocities"`
	All        metricWire `json:"all_coordinates"`
}
type ledgerWire struct {
	Step       int                   `json:"step"`
	ExactDT    scalarWire            `json:"exact_dt"`
	ExactT     scalarWire            `json:"exact_T"`
	EventClass string                `json:"event_class"`
	Batch      []eventWire           `json:"batch"`
	BatchCode  string                `json:"batch_code"`
	PreHash    string                `json:"pre_state_hash"`
	PostHash   string                `json:"post_state_hash"`
	Filter     burner.FilterStats    `json:"filter"`
	Time       burner.TimeComplexity `json:"time_complexity"`
	State      stateWire             `json:"state_complexity"`
}
type checkpointWire struct {
	Step      int        `json:"step"`
	ExactT    scalarWire `json:"exact_T"`
	State     []bodyWire `json:"state"`
	StateHash string     `json:"state_hash"`
}

func scalarOf(f engine.F) scalarWire {
	return scalarWire{f.C[0].RatString(), f.C[1].RatString(), f.C[2].RatString(), f.C[3].RatString()}
}

func ratFromText(s string) (*big.Rat, error) {
	r, ok := new(big.Rat).SetString(s)
	if !ok {
		return nil, fmt.Errorf("invalid rational %q", s)
	}
	return r, nil
}
func fFromWire(w scalarWire) (engine.F, error) {
	a, err := ratFromText(w.A)
	if err != nil {
		return engine.F{}, err
	}
	b, err := ratFromText(w.B)
	if err != nil {
		return engine.F{}, err
	}
	c, err := ratFromText(w.C)
	if err != nil {
		return engine.F{}, err
	}
	d, err := ratFromText(w.D)
	if err != nil {
		return engine.F{}, err
	}
	return engine.NewF(a, b, c, d), nil
}
func vecFromWire(w vecWire) (engine.Vec, error) {
	x, err := fFromWire(w.X)
	if err != nil {
		return engine.Vec{}, err
	}
	y, err := fFromWire(w.Y)
	if err != nil {
		return engine.Vec{}, err
	}
	return engine.Vec{X: x, Y: y}, nil
}
func bodiesFromWire(ws []bodyWire) ([]engine.Body, error) {
	out := make([]engine.Body, len(ws))
	for i, w := range ws {
		p, err := vecFromWire(w.Position)
		if err != nil {
			return nil, err
		}
		v, err := vecFromWire(w.Velocity)
		if err != nil {
			return nil, err
		}
		out[i] = engine.Body{Pos: p, Vel: v}
	}
	return out, nil
}

// loadCheckpoint selects a state written by this command.  A continuation is
// deliberately a new output segment rather than an in-place append, keeping
// its parent checkpoint and exact starting hash explicit in the new manifest.
func loadCheckpoint(path string, wantedStep int) (checkpointWire, error) {
	f, err := os.Open(path)
	if err != nil {
		return checkpointWire{}, err
	}
	defer f.Close()
	var r io.Reader = f
	var gz *gzip.Reader
	if strings.HasSuffix(strings.ToLower(path), ".gz") {
		gz, err = gzip.NewReader(f)
		if err != nil {
			return checkpointWire{}, err
		}
		defer gz.Close()
		r = gz
	}
	dec := json.NewDecoder(r)
	var found checkpointWire
	ok := false
	for {
		var cp checkpointWire
		err := dec.Decode(&cp)
		if err == io.EOF {
			break
		}
		if err != nil {
			return checkpointWire{}, err
		}
		if wantedStep < 0 || cp.Step == wantedStep {
			found, ok = cp, true
			if wantedStep >= 0 {
				break
			}
		}
	}
	if !ok {
		return checkpointWire{}, fmt.Errorf("checkpoint step %d not found in %s", wantedStep, path)
	}
	return found, nil
}
func vecOf(v engine.Vec) vecWire { return vecWire{scalarOf(v.X), scalarOf(v.Y)} }
func bodiesOf(bs []engine.Body) []bodyWire {
	out := make([]bodyWire, len(bs))
	for i, b := range bs {
		out[i] = bodyWire{vecOf(b.Pos), vecOf(b.Vel)}
	}
	return out
}
func eventsOf(es []engine.Event) []eventWire {
	out := make([]eventWire, len(es))
	for i, e := range es {
		var face *int
		var wall *string
		if e.Face >= 0 {
			x := e.Face
			face = &x
		}
		if e.Wall != "" {
			x := e.Wall
			wall = &x
		}
		out[i] = eventWire{e.Kind, append([]int{}, e.Bodies...), face, wall}
	}
	return out
}
func metricOf(g engine.MetricGroup) metricWire {
	return metricWire{g.MaxAbsNumerator.String(), g.MaxDenominator.String(), g.MaxNumeratorBits, g.MaxDenominatorBits}
}
func metricsOf(m engine.Metrics) stateWire {
	return stateWire{metricOf(m.Positions), metricOf(m.Velocities), metricOf(m.All)}
}

func die(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "ERROR: "+format+"\n", args...)
	os.Exit(2)
}
func must(err error) {
	if err != nil {
		die("%v", err)
	}
}
func parseInts(s string) []int {
	if strings.TrimSpace(s) == "" {
		return nil
	}
	ps := strings.Split(s, ",")
	out := make([]int, len(ps))
	for i, p := range ps {
		v, e := strconv.Atoi(strings.TrimSpace(p))
		if e != nil {
			die("bad integer %q", p)
		}
		out[i] = v
	}
	return out
}
func writeJSON(path string, v any) error {
	f, err := os.Create(path)
	if err != nil {
		return err
	}
	defer f.Close()
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	return enc.Encode(v)
}

// writeAtomicJSON makes each exact checkpoint independently resumable even if
// a long burn is interrupted before the append-only gzip streams are closed.
func writeAtomicJSON(path string, v any) error {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		return err
	}
	f, err := os.CreateTemp(dir, ".checkpoint-*.tmp")
	if err != nil {
		return err
	}
	tmp := f.Name()
	ok := false
	defer func() {
		if !ok {
			_ = f.Close()
			_ = os.Remove(tmp)
		}
	}()
	enc := json.NewEncoder(f)
	enc.SetIndent("", "  ")
	if err := enc.Encode(v); err != nil {
		return err
	}
	if err := f.Sync(); err != nil {
		return err
	}
	if err := f.Close(); err != nil {
		return err
	}
	if err := os.Rename(tmp, path); err != nil {
		return err
	}
	ok = true
	return nil
}
func openGzip(path string) (*gzip.Writer, *bufio.Writer, *os.File, error) {
	f, err := os.Create(path)
	if err != nil {
		return nil, nil, nil, err
	}
	gz := gzip.NewWriter(f)
	bw := bufio.NewWriterSize(gz, 1<<20)
	return gz, bw, f, nil
}
func closeGzip(gz *gzip.Writer, bw *bufio.Writer, f *os.File) error {
	if err := bw.Flush(); err != nil {
		return err
	}
	if err := gz.Close(); err != nil {
		return err
	}
	return f.Close()
}
func findLatticeStart(m engine.Model, L int, sites []int, velNames []string) ([]engine.Body, error) {
	if len(sites) != 2 || len(velNames) != 2 {
		return nil, fmt.Errorf("exactly two sites and velocities required")
	}
	for _, s := range engine.LatticeStarts(m, L, 2) {
		if s.Sites[0] == sites[0] && s.Sites[1] == sites[1] && s.Velocities[0] == velNames[0] && s.Velocities[1] == velNames[1] {
			return s.Bodies, nil
		}
	}
	return nil, fmt.Errorf("lattice start not found")
}

func run(args []string) {
	fs := flag.NewFlagSet("run", flag.ExitOnError)
	seed := fs.String("seed", "centered", "centered|lattice")
	modelName := fs.String("model", "dodecagon", "dodecagon|24gon")
	L := fs.Int("L", 2, "container cells per side")
	cap := fs.Int("cap", 7500, "event-batch cap")
	outDir := fs.String("out-dir", "", "output directory")
	face := fs.Int("face", 1, "centered contact face")
	va := fs.String("va", "E", "centered body-A incoming cardinal velocity")
	vb := fs.String("vb", "N", "centered body-B incoming cardinal velocity")
	sitesText := fs.String("sites", "0,1", "lattice ordered site ids")
	velocitiesText := fs.String("velocities", "E,S", "lattice ordered velocities")
	checkpointEvery := fs.Int("checkpoint", 500, "checkpoint interval; 0 disables")
	detectReturn := fs.Bool("detect-return", false, "retain exact StateKey map and terminate on a repeated full state")
	requireRegular := fs.Bool("require-regular", false, "write terminal evidence but exit nonzero unless status is CAP or RETURN after singleton regular batches")
	resumeCheckpoint := fs.String("resume-checkpoint", "", "checkpoint NDJSON or NDJSON.GZ; create a continuation segment from it")
	resumeStep := fs.Int("resume-step", -1, "checkpoint step to resume; -1 selects the final checkpoint in the file")
	fs.Parse(args)
	if *outDir == "" {
		die("run requires --out-dir")
	}
	if *cap < 1 {
		die("--cap must be positive")
	}
	m := engine.BuildModel(*modelName)
	c := engine.MakeContainer(m, *L)
	var start []engine.Body
	var initialTime *engine.F
	startStep := 0
	initialFaces := []int{}
	seedMeta := map[string]any{}
	if *resumeCheckpoint != "" {
		cp, err := loadCheckpoint(*resumeCheckpoint, *resumeStep)
		must(err)
		bs, err := bodiesFromWire(cp.State)
		must(err)
		if len(bs) != 2 {
			die("checkpoint has %d bodies; burner requires exactly 2", len(bs))
		}
		if got := engine.StateHash(bs); got != cp.StateHash {
			die("checkpoint state hash mismatch: encoded=%s reconstructed=%s", cp.StateHash, got)
		}
		t0, err := fFromWire(cp.ExactT)
		must(err)
		start, initialTime, startStep = bs, &t0, cp.Step
		seedMeta = map[string]any{
			"kind":              "checkpoint",
			"parent_checkpoint": *resumeCheckpoint,
			"parent_step":       cp.Step,
			"parent_exact_T":    scalarOf(t0),
			"parent_state_hash": cp.StateHash,
		}
	} else {
		switch *seed {
		case "centered":
			bs, _, ok := engine.CenteredPairStart(m, *L, *face, *va, *vb)
			if !ok {
				die("centered seed does not strictly close: face=%d velocities=(%s,%s)", *face, *va, *vb)
			}
			start = bs
			initialFaces = []int{*face}
			seedMeta = map[string]any{"kind": "centered", "face": *face, "incoming": []string{*va, *vb}, "time_zero_pair_face": *face}
		case "lattice":
			names := strings.Split(*velocitiesText, ",")
			for i := range names {
				names[i] = strings.TrimSpace(names[i])
			}
			bs, err := findLatticeStart(m, *L, parseInts(*sitesText), names)
			must(err)
			start = bs
			seedMeta = map[string]any{"kind": "lattice", "sites": parseInts(*sitesText), "velocities": names}
		default:
			die("unknown --seed %q", *seed)
		}
	}
	must(os.MkdirAll(*outDir, 0755))
	// v2 portability: every segment carries an explicit full start state,
	// rather than relying on an upstream checkpoint path being available.
	initialT := engine.Zero()
	if initialTime != nil {
		initialT = *initialTime
	}
	startHash := engine.StateHash(start)
	startCheckpoint := checkpointWire{startStep, scalarOf(initialT), bodiesOf(start), startHash}
	must(writeAtomicJSON(filepath.Join(*outDir, "start_state.json"), startCheckpoint))
	ledgerPath := filepath.Join(*outDir, "ledger.ndjson.gz")
	checkpointPath := filepath.Join(*outDir, "checkpoints.ndjson.gz")
	checkpointDir := filepath.Join(*outDir, "checkpoints")
	facesPath := filepath.Join(*outDir, "pair_faces.csv")
	gz, lb, lf, err := openGzip(ledgerPath)
	must(err)
	cgz, cb, cf, err := openGzip(checkpointPath)
	must(err)
	faces, err := os.Create(facesPath)
	must(err)
	fw := bufio.NewWriterSize(faces, 1<<20)
	_, err = fw.WriteString("pair_contact_index,event_step,face_label,ternary_face_class_mod_3\n")
	must(err)
	pairIndex := 0
	for _, f := range initialFaces {
		_, err = fmt.Fprintf(fw, "%d,0,%d,%d\n", pairIndex, f, f%3)
		must(err)
		pairIndex++
	}
	started := time.Now()
	opt := burner.Options{InitialTime: initialTime, StartStep: startStep, DetectReturn: *detectReturn, InitialPairFaces: initialFaces, CheckpointEvery: *checkpointEvery}
	opt.OnRecord = func(r burner.Record) error {
		row := ledgerWire{r.Step, scalarOf(r.DT), scalarOf(r.T), string(r.Class), eventsOf(r.Batch), burner.CanonicalBatchString(r.Batch), r.PreHash, r.PostHash, r.Filter, r.Time, metricsOf(r.State)}
		if err := json.NewEncoder(lb).Encode(row); err != nil {
			return err
		}
		for _, e := range r.Batch {
			if e.Kind == "PAIR_FACE" && e.Face >= 0 {
				if _, err := fmt.Fprintf(fw, "%d,%d,%d,%d\n", pairIndex, r.Step, e.Face, e.Face%3); err != nil {
					return err
				}
				pairIndex++
			}
		}
		return nil
	}
	opt.OnCheckpoint = func(step int, t engine.F, bs []engine.Body, hash string) error {
		cp := checkpointWire{step, scalarOf(t), bodiesOf(bs), hash}
		// Snapshot first: this is the crash-resilient continuation anchor.
		if err := writeAtomicJSON(filepath.Join(checkpointDir, fmt.Sprintf("%010d.json", step)), cp); err != nil {
			return err
		}
		return json.NewEncoder(cb).Encode(cp)
	}
	out, err := burner.Run(m, c, start, *cap, opt)
	must(err)
	must(fw.Flush())
	must(faces.Close())
	must(closeGzip(gz, lb, lf))
	must(closeGzip(cgz, cb, cf))
	elapsed := time.Since(started)
	manifest := map[string]any{
		"schema":        "exact-two-body-burner/v1",
		"producer":      map[string]any{"language": "Go", "runtime": runtime.Version(), "command": "go run ./cmd/burner run", "module": "latticegeometry"},
		"model":         map[string]any{"id": m.ID, "sides": m.Sides, "field": m.Field, "edge": scalarOf(m.Edge), "apothem": scalarOf(m.Apothem), "face_convention": "face k outward normal angle 360*k/sides degrees"},
		"container":     map[string]any{"cells_per_side": *L, "half_side": scalarOf(c.HalfSide)},
		"seed":          seedMeta,
		"physics":       map[string]any{"arithmetic": "exact Q(sqrt(2),sqrt(3)) coefficients; no floating decisions", "pair": "equal-mass elastic reflection on active contact normal", "wall": "axis-aligned specular reflection", "two_body_only": true},
		"filters":       map[string]any{"aabb": "exact swept physical AABB reject", "parabolic": "exact circumscribed-disk minimum over [0,Twall], reject-only", "facet_scan": "all exposed facets; quotient comparisons cross-multiplied"},
		"output":        map[string]any{"ledger": "ledger.ndjson.gz", "codec": "gzip NDJSON", "start_state": "start_state.json (atomic)", "end_state": "end_state.json (atomic)", "checkpoints": "checkpoints.ndjson.gz", "checkpoint_snapshots": "checkpoints/<absolute-step>.json (atomic)", "pair_faces": "pair_faces.csv", "pair_face_index": "segment-relative", "checkpoint_interval": *checkpointEvery, "return_detection": *detectReturn},
		"stopping_rule": map[string]any{"event_cap": *cap, "terminal_classes": []string{"PAIR_CORNER", "WALL_CORNER", "COUPLED_SIMULTANEOUS", "NO_EVENT"}, "require_regular": *requireRegular, "policy": "wall+pair, wall-corner, pair-corner, and coupled shared-body ties are recorded then terminal; they are never resolved by order"},
	}
	regularOnlyCompleted := out.Status == "CAP" || out.Status == "RETURN"
	// v2 portability: the output state is an explicit standalone artifact.
	endCheckpoint := checkpointWire{out.EndStep, scalarOf(out.T), bodiesOf(out.Final), out.FinalHash}
	must(writeAtomicJSON(filepath.Join(*outDir, "end_state.json"), endCheckpoint))
	summary := map[string]any{
		"status": string(out.Status), "regular_only_completed": regularOnlyCompleted, "event_batches": out.EventBatches, "segment_start_step": out.StartStep, "segment_end_step": out.EndStep, "exact_T": scalarOf(out.T), "final_state_hash": out.FinalHash,
		"pair_contacts": pairIndex, "max_collision_time_bits": out.MaxTime, "filter_totals": out.Filters,
		"initial_state_metrics": metricsOf(out.InitialState), "final_state_metrics": metricsOf(out.FinalState), "max_state_metrics": metricsOf(out.MaxState),
		"elapsed_seconds": elapsed.Seconds(), "events_per_second": float64(out.EventBatches) / elapsed.Seconds(),
	}
	must(writeJSON(filepath.Join(*outDir, "manifest.json"), manifest))
	must(writeJSON(filepath.Join(*outDir, "summary.json"), summary))
	fmt.Printf("burner %s %s: status=%s segment=%d..%d batches=%d pair_contacts=%d elapsed=%s rate=%.1f/s max_T_bits=(%d,%d) filters=(aabb=%d parabola=%d facets=%d/%d)\n", *seed, m.ID, out.Status, out.StartStep+1, out.EndStep, out.EventBatches, pairIndex, elapsed.Round(time.Millisecond), float64(out.EventBatches)/elapsed.Seconds(), out.MaxTime.MaxNumeratorBits, out.MaxTime.MaxDenominatorBits, out.Filters.AABBRejects, out.Filters.ParabolaRejects, out.Filters.FacetsTested, out.Filters.FacetsExposed)
	if *requireRegular && !regularOnlyCompleted {
		die("regular-only policy stopped at %s; terminal evidence is in %s", out.Status, *outDir)
	}
}
func usage() { fmt.Fprintln(os.Stderr, "usage: burner run [flags]") }
func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	switch os.Args[1] {
	case "run":
		run(os.Args[2:])
	default:
		usage()
		os.Exit(2)
	}
}
