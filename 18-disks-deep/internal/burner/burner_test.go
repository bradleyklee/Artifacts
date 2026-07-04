package burner

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"

	"latticegeometry/internal/engine"
)

type fixtureScalar struct {
	A string `json:"a"`
	B string `json:"b"`
	C string `json:"c"`
	D string `json:"d"`
}
type fixtureEvent struct {
	Step       int           `json:"step"`
	ExactDT    fixtureScalar `json:"exact_dt"`
	ExactT     fixtureScalar `json:"exact_T"`
	EventClass string        `json:"event_class"`
	BatchCode  string        `json:"batch_code"`
	PreHash    string        `json:"pre_state_hash"`
	PostHash   string        `json:"post_state_hash"`
}
type fixture struct {
	Evolution struct {
		Events []fixtureEvent `json:"events"`
	} `json:"evolution"`
	Result struct {
		Status         string `json:"status"`
		EventBatches   int    `json:"event_batches"`
		FinalStateHash string `json:"final_state_hash"`
	} `json:"result"`
}

func loadFixture(t *testing.T, rel string) fixture {
	t.Helper()
	p := filepath.Join("..", "..", rel)
	raw, err := os.ReadFile(p)
	if err != nil {
		t.Fatal(err)
	}
	var f fixture
	if err := json.Unmarshal(raw, &f); err != nil {
		t.Fatal(err)
	}
	return f
}
func fsOf(x engine.F) fixtureScalar {
	return fixtureScalar{x.C[0].RatString(), x.C[1].RatString(), x.C[2].RatString(), x.C[3].RatString()}
}
func compareFixture(t *testing.T, got []Record, out Outcome, f fixture, skipInitial int) {
	t.Helper()
	want := f.Evolution.Events[skipInitial:]
	if len(got) != len(want) {
		t.Fatalf("record count got=%d want=%d", len(got), len(want))
	}
	for i, r := range got {
		w := want[i]
		if r.Step != w.Step || string(r.Class) != w.EventClass || CanonicalBatchString(r.Batch) != w.BatchCode || r.PreHash != w.PreHash || r.PostHash != w.PostHash || fsOf(r.DT) != w.ExactDT || fsOf(r.T) != w.ExactT {
			t.Fatalf("fixture mismatch at step %d\n got class=%s batch=%s dt=%#v t=%#v pre=%s post=%s\nwant class=%s batch=%s dt=%#v t=%#v pre=%s post=%s", r.Step, r.Class, CanonicalBatchString(r.Batch), fsOf(r.DT), fsOf(r.T), r.PreHash, r.PostHash, w.EventClass, w.BatchCode, w.ExactDT, w.ExactT, w.PreHash, w.PostHash)
		}
	}
	if string(out.Status) != f.Result.Status || out.EventBatches != f.Result.EventBatches || out.FinalHash != f.Result.FinalStateHash {
		t.Fatalf("outcome mismatch got status=%s steps=%d hash=%s; want status=%s steps=%d hash=%s", out.Status, out.EventBatches, out.FinalHash, f.Result.Status, f.Result.EventBatches, f.Result.FinalStateHash)
	}
}
func runCapture(t *testing.T, m engine.Model, c engine.Container, start []engine.Body, cap int, initial []int) ([]Record, Outcome) {
	t.Helper()
	got := []Record{}
	out, err := Run(m, c, start, cap, Options{DetectReturn: true, InitialPairFaces: initial, OnRecord: func(r Record) error { got = append(got, r); return nil }})
	if err != nil {
		t.Fatal(err)
	}
	return got, out
}
func TestDodecagonFixtureParity(t *testing.T) {
	m := engine.BuildModel("dodecagon")
	c := engine.MakeContainer(m, 2)
	bs, _, ok := engine.CenteredPairStart(m, 2, 1, "E", "N")
	if !ok {
		t.Fatal("seed")
	}
	got, out := runCapture(t, m, c, bs, 500, []int{1})
	compareFixture(t, got, out, loadFixture(t, "fixtures/dodecagon/centered_dodecagon_f1_EN_cap500.json"), 1)
}
func Test24gonFixtureParity(t *testing.T) {
	m := engine.BuildModel("24gon")
	c := engine.MakeContainer(m, 2)
	cases := []struct{ name, velA, velB, file string }{
		{"A", "E", "S", "fixtures/24gon/24gon_L2_N2_class_A_ES_cap100.json"},
		{"B", "W", "N", "fixtures/24gon/24gon_L2_N2_class_B_WN_cap100.json"},
	}
	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			var bs []engine.Body
			for _, s := range engine.LatticeStarts(m, 2, 2) {
				if s.Sites[0] == 0 && s.Sites[1] == 1 && s.Velocities[0] == tc.velA && s.Velocities[1] == tc.velB {
					bs = s.Bodies
					break
				}
			}
			if bs == nil {
				t.Fatal("missing lattice start")
			}
			got, out := runCapture(t, m, c, bs, 100, nil)
			compareFixture(t, got, out, loadFixture(t, tc.file), 0)
		})
	}
}
func TestReverseStemFixtureParity(t *testing.T) {
	m := engine.BuildModel("dodecagon")
	c := engine.MakeContainer(m, 2)
	forward, _, ok := engine.CenteredPairStart(m, 2, 1, "E", "N")
	if !ok {
		t.Fatal("seed")
	}
	rev := make([]engine.Body, 2)
	for i, b := range forward {
		rev[i] = engine.Body{Pos: b.Pos, Vel: engine.Vec{X: b.Vel.X.Neg(), Y: b.Vel.Y.Neg()}}
	}
	got, out := runCapture(t, m, c, rev, 16, nil)
	compareFixture(t, got, out, loadFixture(t, "fixtures/dodecagon/centered_dodecagon_f1_EN_reverse_stem.json"), 0)
}

func TestCheckpointContinuationMatchesUninterruptedRun(t *testing.T) {
	m := engine.BuildModel("dodecagon")
	c := engine.MakeContainer(m, 2)
	start, _, ok := engine.CenteredPairStart(m, 2, 1, "E", "N")
	if !ok {
		t.Fatal("seed")
	}

	var checkpointBodies []engine.Body
	var checkpointT engine.F
	var checkpointHash string
	direct, err := Run(m, c, start, 100, Options{
		CheckpointEvery: 40,
		OnCheckpoint: func(step int, t0 engine.F, bs []engine.Body, hash string) error {
			if step == 40 {
				checkpointBodies = copyBodies(bs)
				checkpointT = t0.Clone()
				checkpointHash = hash
			}
			return nil
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	if checkpointBodies == nil || checkpointHash != engine.StateHash(checkpointBodies) {
		t.Fatal("missing or invalid checkpoint")
	}
	var firstStep int
	resumed, err := Run(m, c, checkpointBodies, 60, Options{
		InitialTime: &checkpointT,
		StartStep:   40,
		OnRecord: func(r Record) error {
			if firstStep == 0 {
				firstStep = r.Step
			}
			return nil
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	if firstStep != 41 || resumed.StartStep != 40 || resumed.EndStep != 100 || resumed.EventBatches != 60 {
		t.Fatalf("bad continuation indexing: first=%d range=%d..%d batches=%d", firstStep, resumed.StartStep, resumed.EndStep, resumed.EventBatches)
	}
	if !resumed.T.Eq(direct.T) || resumed.FinalHash != direct.FinalHash || resumed.Status != direct.Status {
		t.Fatalf("checkpoint continuation diverged: t=%s vs %s hash=%s vs %s status=%s vs %s", resumed.T, direct.T, resumed.FinalHash, direct.FinalHash, resumed.Status, direct.Status)
	}
}

func TestContinuationCheckpointAnchorsAbsoluteStartAndEndpoint(t *testing.T) {
	m := engine.BuildModel("dodecagon")
	c := engine.MakeContainer(m, 2)
	start, _, ok := engine.CenteredPairStart(m, 2, 1, "E", "N")
	if !ok {
		t.Fatal("seed")
	}
	var at5 []engine.Body
	var t5 engine.F
	seedSteps := []int{}
	_, err := Run(m, c, start, 5, Options{
		CheckpointEvery: 5,
		OnCheckpoint: func(step int, tm engine.F, bs []engine.Body, _ string) error {
			seedSteps = append(seedSteps, step)
			if step == 5 {
				at5, t5 = copyBodies(bs), tm.Clone()
			}
			return nil
		},
	})
	if err != nil || at5 == nil {
		t.Fatalf("failed to make seed checkpoint: %v", err)
	}
	if len(seedSteps) != 2 || seedSteps[0] != 0 || seedSteps[1] != 5 {
		t.Fatalf("unexpected initial checkpoints: %v", seedSteps)
	}
	steps := []int{}
	_, err = Run(m, c, at5, 3, Options{
		InitialTime:     &t5,
		StartStep:       5,
		CheckpointEvery: 100, // neither 5 nor 8 is a cadence multiple
		OnCheckpoint: func(step int, _ engine.F, _ []engine.Body, _ string) error {
			steps = append(steps, step)
			return nil
		},
	})
	if err != nil {
		t.Fatal(err)
	}
	if len(steps) != 2 || steps[0] != 5 || steps[1] != 8 {
		t.Fatalf("continuation must write absolute start/end checkpoints, got %v", steps)
	}
}
