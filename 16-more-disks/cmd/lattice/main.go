// lattice is the canonical Go producer for artifact 16.
// It writes exhaustive scan atlases and self-contained exact certificates.
package main

import (
	"flag"
	"fmt"
	"os"
	"strconv"
	"strings"
	"time"

	"latticegeometry/internal/artifact"
	"latticegeometry/internal/engine"
)

func die(format string, args ...any) {
	fmt.Fprintf(os.Stderr, "ERROR: "+format+"\n", args...)
	os.Exit(2)
}
func must(err error) {
	if err != nil {
		die("%v", err)
	}
}
func parseCSVInts(s string) []int {
	if strings.TrimSpace(s) == "" {
		return nil
	}
	parts := strings.Split(s, ",")
	out := make([]int, len(parts))
	for i, p := range parts {
		v, e := strconv.Atoi(strings.TrimSpace(p))
		if e != nil {
			die("bad integer %q", p)
		}
		out[i] = v
	}
	return out
}
func parseCSVWords(s string) []string {
	if strings.TrimSpace(s) == "" {
		return nil
	}
	parts := strings.Split(s, ",")
	for i := range parts {
		parts[i] = strings.TrimSpace(parts[i])
	}
	return parts
}
func hasOffcardinal(m engine.Model, word []int) bool {
	for _, f := range word {
		if !m.IsCardinalFace(f) {
			return true
		}
	}
	return false
}

func compactOutcome(o engine.Outcome) artifact.Outcome { return artifact.OutcomeOf(o, false) }
func recordStart(start engine.LatticeStart) artifact.LatticeStart {
	return artifact.LatticeStart{Sites: append([]int{}, start.Sites...), Velocities: append([]string{}, start.Velocities...), InitialState: artifact.BodiesOf(start.Bodies)}
}
func earliestAdd(dst map[string]string, m engine.Model, caseID string, out engine.Outcome) {
	status := string(out.Status)
	if _, ok := dst["EARLIEST_"+status]; !ok {
		dst["EARLIEST_"+status] = caseID
	}
	if hasOffcardinal(m, out.PairFaceWord) {
		if _, ok := dst["EARLIEST_OFFCARDINAL_PAIR_FACE"]; !ok {
			dst["EARLIEST_OFFCARDINAL_PAIR_FACE"] = caseID
		}
	}
	if out.FirstDenominatorPromotion != 0 {
		if _, ok := dst["EARLIEST_DENOMINATOR_PROMOTION"]; !ok {
			dst["EARLIEST_DENOMINATOR_PROMOTION"] = caseID
		}
	}
	if out.FirstNumeratorHeightGrowth != 0 {
		if _, ok := dst["EARLIEST_NUMERATOR_HEIGHT_GROWTH"]; !ok {
			dst["EARLIEST_NUMERATOR_HEIGHT_GROWTH"] = caseID
		}
	}
}

func cmdAtlas(args []string) {
	fs := flag.NewFlagSet("atlas", flag.ExitOnError)
	modelName := fs.String("model", "", "square|octagon|dodecagon|24gon")
	L := fs.Int("L", 2, "container cells per side")
	N := fs.Int("N", 2, "body count")
	cap := fs.Int("cap", 100, "event-batch horizon")
	outPath := fs.String("out", "", "output atlas JSON")
	experimentID := fs.String("id", "", "experiment ID")
	fs.Parse(args)
	if *modelName == "" || *outPath == "" {
		die("atlas requires --model and --out")
	}
	m := engine.BuildModel(*modelName)
	c := engine.MakeContainer(m, *L)
	startTime := time.Now()
	starts := engine.LatticeStarts(m, *L, *N)
	cases := make([]artifact.AtlasCase, 0, len(starts))
	counts := map[string]int{}
	earliest := map[string]string{}
	for _, s := range starts {
		r := engine.Run(m, c, s.Bodies, *cap, engine.TraceCompact, nil)
		caseID := fmt.Sprintf("%s-L%d-N%d-%06d", m.ID, *L, *N, s.Ordinal)
		counts[string(r.Status)]++
		earliestAdd(earliest, m, caseID, r)
		cases = append(cases, artifact.AtlasCase{CaseID: caseID, RawStartID: s.Ordinal, Start: recordStart(s), Outcome: compactOutcome(r)})
	}
	id := *experimentID
	if id == "" {
		id = fmt.Sprintf("%s_L%d_N%d_cardinal_lattice", m.ID, *L, *N)
	}
	scan := map[string]any{
		"family":             "lattice_centroid_cardinal_velocity",
		"raw_ordering":       "lexicographic unordered site combinations, then ordered velocity words E,W,N,S",
		"positions":          "all bodies start at distinct LxL square-cell centroids",
		"velocities":         "unit cardinal velocities only",
		"complete":           true,
		"wall_clock_seconds": fmt.Sprintf("%.6f", time.Since(startTime).Seconds()),
	}
	doc := artifact.Atlas{Schema: "lattice-chaos-atlas/v2", ExperimentID: id, Producer: artifact.ProducerOf(), Model: artifact.ModelOf(m), Container: artifact.ContainerOf(c), Dynamics: artifact.DynamicsContract(), Scan: scan, EventCap: *cap, RawStarts: len(starts), Counts: artifact.SortCounts(counts), Earliest: earliest, Results: cases}
	must(artifact.WriteJSON(*outPath, doc))
	fmt.Printf("atlas %s: %d starts in %s; counts=%v\n", id, len(starts), time.Since(startTime).Round(time.Millisecond), counts)
}

func centeredPreState(m engine.Model, face int, va, vb string) []engine.Body {
	n := m.Normals[face]
	vels := engine.CardinalVelocities()
	a := m.Apothem
	return []engine.Body{{Pos: n.Scale(a.Neg()), Vel: vels[va]}, {Pos: n.Scale(a), Vel: vels[vb]}}
}
func centeredStartWire(m engine.Model, face int, va, vb string, rec engine.EventRecord, post []engine.Body) artifact.CenteredStart {
	return artifact.CenteredStart{Face: face, FaceClassMod3: face % 3, Incoming: []string{va, vb}, PreTimeZeroState: artifact.BodiesOf(centeredPreState(m, face, va, vb)), TimeZeroEvent: artifact.EventRecordOf(rec, true), PostTimeZeroState: artifact.BodiesOf(post)}
}

func cmdCenteredAtlas(args []string) {
	fs := flag.NewFlagSet("centered-atlas", flag.ExitOnError)
	modelName := fs.String("model", "dodecagon", "shape")
	L := fs.Int("L", 2, "container cells per side")
	cap := fs.Int("cap", 500, "event-batch horizon")
	offcardinal := fs.Bool("offcardinal-only", false, "exclude cardinal face labels")
	outPath := fs.String("out", "", "output atlas JSON")
	experimentID := fs.String("id", "", "experiment ID")
	fs.Parse(args)
	if *outPath == "" {
		die("centered-atlas requires --out")
	}
	m := engine.BuildModel(*modelName)
	c := engine.MakeContainer(m, *L)
	starts := []struct {
		face   int
		va, vb string
		bs     []engine.Body
		rec    engine.EventRecord
	}{}
	for face := 0; face < m.Sides; face++ {
		if *offcardinal && m.IsCardinalFace(face) {
			continue
		}
		for _, va := range engine.CardinalNames() {
			for _, vb := range engine.CardinalNames() {
				bs, rec, ok := engine.CenteredPairStart(m, *L, face, va, vb)
				if ok {
					starts = append(starts, struct {
						face   int
						va, vb string
						bs     []engine.Body
						rec    engine.EventRecord
					}{face, va, vb, bs, rec})
				}
			}
		}
	}
	began := time.Now()
	counts := map[string]int{}
	earliest := map[string]string{}
	cases := make([]artifact.AtlasCase, 0, len(starts))
	for i, s := range starts {
		r := engine.Run(m, c, s.bs, *cap, engine.TraceCompact, []engine.EventRecord{s.rec})
		caseID := fmt.Sprintf("%s-center-f%d-%s%s", m.ID, s.face, s.va, s.vb)
		counts[string(r.Status)]++
		earliestAdd(earliest, m, caseID, r)
		cases = append(cases, artifact.AtlasCase{CaseID: caseID, RawStartID: i + 1, Start: centeredStartWire(m, s.face, s.va, s.vb, s.rec, s.bs), Outcome: compactOutcome(r)})
	}
	id := *experimentID
	if id == "" {
		id = fmt.Sprintf("%s_centered_cardinal_incoming", m.ID)
	}
	scan := map[string]any{"family": "prescribed_central_face_contact", "raw_ordering": "increasing face label, then ordered velocity words E,W,N,S", "positions": "body 0 at -apothem*n_face; body 1 at +apothem*n_face; resolved elastically at time zero", "velocities": "strict relative-closing ordered unit cardinal pairs", "offcardinal_only": *offcardinal, "complete": true, "wall_clock_seconds": fmt.Sprintf("%.6f", time.Since(began).Seconds())}
	doc := artifact.Atlas{Schema: "lattice-chaos-centered-atlas/v2", ExperimentID: id, Producer: artifact.ProducerOf(), Model: artifact.ModelOf(m), Container: artifact.ContainerOf(c), Dynamics: artifact.DynamicsContract(), Scan: scan, EventCap: *cap, RawStarts: len(starts), Counts: artifact.SortCounts(counts), Earliest: earliest, Results: cases}
	must(artifact.WriteJSON(*outPath, doc))
	fmt.Printf("centered atlas %s: %d starts in %s; counts=%v\n", id, len(starts), time.Since(began).Round(time.Millisecond), counts)
}

func certificateBase(id string, m engine.Model, c engine.Container, instance any, cap int, o engine.Outcome, full bool) artifact.Certificate {
	cert := artifact.Certificate{Schema: "lattice-chaos-self-contained-certificate/v2", CertificateID: id, Producer: artifact.ProducerOf(), Model: artifact.ModelOf(m), Container: artifact.ContainerOf(c), Dynamics: artifact.DynamicsContract(), Instance: instance, StoppingRule: map[string]any{"event_cap": cap, "declared_terminal_classes": []string{"PAIR_CORNER", "WALL_CORNER", "COUPLED_SIMULTANEOUS", "NO_EVENT"}, "return_rule": "exact full labelled state equality after a resolved batch", "finite_prefix_rule": "CAP is a finite regular horizon survivor, not a chaos or aperiodicity proof."}}
	cert.Evolution.RecordEncoding = "append-only exact batch ledger; every row includes global earliest batch, exact dt/T, and complete pre/post labelled states"
	cert.Evolution.Events = make([]artifact.EventRecord, len(o.Events))
	for i, e := range o.Events {
		cert.Evolution.Events[i] = artifact.EventRecordOf(e, full)
	}
	cert.Result = artifact.OutcomeOf(o, full)
	cert.IndependentCheckContract = map[string]any{"sole_input": "A checker must use this file alone; it must not import or invoke the Go producer.", "required_recomputation": "Reconstruct geometry and initial state, enumerate every wall/pair candidate before each recorded batch, require exact earliest-time batch equality, and require exact post-state equality.", "contact_rule": "A regular pair contact has exactly one active support face. Pair corners and shared-body same-time batches are terminal; disjoint contacts commute.", "sequence_rule": "For the centered dodecagon family, the ternary face sequence is pair_face_word reduced modulo 3, including the time-zero face contact."}
	return cert
}

func cmdCertLattice(args []string) {
	fs := flag.NewFlagSet("cert-lattice", flag.ExitOnError)
	modelName := fs.String("model", "", "shape")
	L := fs.Int("L", 2, "L")
	sitesS := fs.String("sites", "", "comma site ids")
	velsS := fs.String("velocities", "", "comma velocities")
	cap := fs.Int("cap", 100, "cap")
	id := fs.String("id", "", "certificate ID")
	outPath := fs.String("out", "", "output JSON")
	fs.Parse(args)
	if *modelName == "" || *sitesS == "" || *velsS == "" || *id == "" || *outPath == "" {
		die("cert-lattice requires --model --sites --velocities --id --out")
	}
	m := engine.BuildModel(*modelName)
	c := engine.MakeContainer(m, *L)
	ids := parseCSVInts(*sitesS)
	names := parseCSVWords(*velsS)
	if len(ids) != len(names) || len(ids) == 0 {
		die("sites/velocities length mismatch")
	}
	siteList := engine.LatticeSites(m, *L)
	velMap := engine.CardinalVelocities()
	bs := make([]engine.Body, len(ids))
	seen := map[int]bool{}
	for i, site := range ids {
		if site < 0 || site >= len(siteList) || seen[site] {
			die("bad or duplicate site %d", site)
		}
		seen[site] = true
		v, ok := velMap[names[i]]
		if !ok {
			die("bad velocity %s", names[i])
		}
		bs[i] = engine.Body{Pos: siteList[site], Vel: v}
	}
	o := engine.Run(m, c, bs, *cap, engine.TraceFull, nil)
	inst := artifact.LatticeStart{Sites: ids, Velocities: names, InitialState: artifact.BodiesOf(bs)}
	cert := certificateBase(*id, m, c, inst, *cap, o, true)
	must(artifact.WriteJSON(*outPath, cert))
	fmt.Printf("certificate %s: status=%s steps=%d\n", *id, o.Status, o.EventBatches)
}

func cmdCertCentered(args []string) {
	fs := flag.NewFlagSet("cert-centered", flag.ExitOnError)
	modelName := fs.String("model", "dodecagon", "shape")
	L := fs.Int("L", 2, "L")
	face := fs.Int("face", -1, "face")
	va := fs.String("va", "", "body 0 incoming velocity")
	vb := fs.String("vb", "", "body 1 incoming velocity")
	cap := fs.Int("cap", 500, "cap")
	id := fs.String("id", "", "certificate ID")
	outPath := fs.String("out", "", "output JSON")
	fs.Parse(args)
	if *face < 0 || *va == "" || *vb == "" || *id == "" || *outPath == "" {
		die("cert-centered requires --face --va --vb --id --out")
	}
	m := engine.BuildModel(*modelName)
	c := engine.MakeContainer(m, *L)
	bs, rec, ok := engine.CenteredPairStart(m, *L, *face, *va, *vb)
	if !ok {
		die("non-approaching time-zero seed")
	}
	o := engine.Run(m, c, bs, *cap, engine.TraceFull, []engine.EventRecord{rec})
	inst := centeredStartWire(m, *face, *va, *vb, rec, bs)
	cert := certificateBase(*id, m, c, inst, *cap, o, true)
	must(artifact.WriteJSON(*outPath, cert))
	fmt.Printf("certificate %s: status=%s steps=%d pair_faces=%d\n", *id, o.Status, o.EventBatches, len(o.PairFaceWord))
}

func cmdCheckpointCentered(args []string) {
	fs := flag.NewFlagSet("checkpoint-centered", flag.ExitOnError)
	modelName := fs.String("model", "dodecagon", "shape")
	L := fs.Int("L", 2, "L")
	face := fs.Int("face", -1, "face")
	va := fs.String("va", "", "body 0 incoming velocity")
	vb := fs.String("vb", "", "body 1 incoming velocity")
	cap := fs.Int("cap", 12000, "cap")
	id := fs.String("id", "", "checkpoint ID")
	outPath := fs.String("out", "", "output JSON")
	fs.Parse(args)
	if *face < 0 || *va == "" || *vb == "" || *id == "" || *outPath == "" {
		die("checkpoint-centered requires --face --va --vb --id --out")
	}
	m := engine.BuildModel(*modelName)
	c := engine.MakeContainer(m, *L)
	bs, rec, ok := engine.CenteredPairStart(m, *L, *face, *va, *vb)
	if !ok {
		die("non-approaching time-zero seed")
	}
	began := time.Now()
	o := engine.Run(m, c, bs, *cap, engine.TraceCompact, []engine.EventRecord{rec})
	result := artifact.OutcomeOf(o, false)
	result.FinalState = artifact.BodiesOf(o.Final) // resume/checkpoint witness, not per-row state duplication.
	doc := map[string]any{
		"schema":               "lattice-chaos-compact-progress/v1",
		"checkpoint_id":        *id,
		"producer":             artifact.ProducerOf(),
		"model":                artifact.ModelOf(m),
		"container":            artifact.ContainerOf(c),
		"dynamics":             artifact.DynamicsContract(),
		"instance":             centeredStartWire(m, *face, *va, *vb, rec, bs),
		"stopping_rule":        map[string]any{"event_cap": *cap, "kind": "finite exact checkpoint", "warning": "A compact checkpoint stores every exact event batch and final state, but not the full pre/post state at every row. It is not a replacement for a full certificate."},
		"evolution":            map[string]any{"record_encoding": "append-only compact exact event ledger: batch, exact dt/T, state hashes, no per-row coordinates", "events": result.Events},
		"result":               result,
		"elapsed_wall_seconds": fmt.Sprintf("%.6f", time.Since(began).Seconds()),
	}
	must(artifact.WriteJSON(*outPath, doc))
	fmt.Printf("checkpoint %s: status=%s steps=%d pair_faces=%d in %s\n", *id, o.Status, o.EventBatches, len(o.PairFaceWord), time.Since(began).Round(time.Millisecond))
}

// cmdCertCenteredReverseStem produces the literal reverse-time continuation
// from the resolved t=0 contact.  It is kept separate from the forward
// centered family because the input state is the velocity-negated resolved
// collision state, not an incoming cardinal seed.
func cmdCertCenteredReverseStem(args []string) {
	fs := flag.NewFlagSet("cert-centered-reverse-stem", flag.ExitOnError)
	modelName := fs.String("model", "dodecagon", "shape")
	L := fs.Int("L", 2, "L")
	face := fs.Int("face", -1, "source centered face")
	va := fs.String("va", "", "source body 0 incoming velocity")
	vb := fs.String("vb", "", "source body 1 incoming velocity")
	cap := fs.Int("cap", 16, "event cap")
	id := fs.String("id", "", "certificate ID")
	outPath := fs.String("out", "", "output JSON")
	fs.Parse(args)
	if *face < 0 || *va == "" || *vb == "" || *id == "" || *outPath == "" {
		die("cert-centered-reverse-stem requires --face --va --vb --id --out")
	}
	m := engine.BuildModel(*modelName)
	c := engine.MakeContainer(m, *L)
	forward, rec, ok := engine.CenteredPairStart(m, *L, *face, *va, *vb)
	if !ok {
		die("non-approaching source time-zero seed")
	}
	// Physical time reversal at the resolved t=0 state: positions fixed,
	// every velocity negated.  Evolving this state forward is the past branch.
	reversed := make([]engine.Body, len(forward))
	for i, b := range forward {
		reversed[i] = engine.Body{Pos: engine.Vec{X: b.Pos.X.Clone(), Y: b.Pos.Y.Clone()}, Vel: engine.Vec{X: b.Vel.X.Neg(), Y: b.Vel.Y.Neg()}}
	}
	o := engine.Run(m, c, reversed, *cap, engine.TraceFull, nil)
	inst := map[string]any{
		"family":                  "time_reversal_continuation_from_resolved_centered_contact",
		"source_centered_contact": centeredStartWire(m, *face, *va, *vb, rec, forward),
		"initial_state":           artifact.BodiesOf(reversed),
		"time_parameter":          "positive time in this record equals negative physical time of the original centered forward seed",
	}
	cert := certificateBase(*id, m, c, inst, *cap, o, true)
	cert.IndependentCheckContract["reverse_time_rule"] = "Start from the resolved forward t=0 state with all velocities negated; do not insert a second t=0 pair collision."
	must(artifact.WriteJSON(*outPath, cert))
	fmt.Printf("reverse stem certificate %s: status=%s steps=%d pair_faces=%d\n", *id, o.Status, o.EventBatches, len(o.PairFaceWord))
}

func usage() {
	fmt.Fprintln(os.Stderr, "usage: lattice <atlas|centered-atlas|cert-lattice|cert-centered|cert-centered-reverse-stem|checkpoint-centered> [flags]")
}
func main() {
	if len(os.Args) < 2 {
		usage()
		os.Exit(2)
	}
	switch os.Args[1] {
	case "atlas":
		cmdAtlas(os.Args[2:])
	case "centered-atlas":
		cmdCenteredAtlas(os.Args[2:])
	case "cert-lattice":
		cmdCertLattice(os.Args[2:])
	case "cert-centered":
		cmdCertCentered(os.Args[2:])
	case "cert-centered-reverse-stem":
		cmdCertCenteredReverseStem(os.Args[2:])
	case "checkpoint-centered":
		cmdCheckpointCentered(os.Args[2:])
	default:
		usage()
		os.Exit(2)
	}
}
