package engine

import "testing"

func countsFor(t *testing.T, shape string, L, N, cap int) map[BatchClass]int {
	t.Helper()
	m := BuildModel(shape)
	c := MakeContainer(m, L)
	out := map[BatchClass]int{}
	for _, start := range LatticeStarts(m, L, N) {
		res := Run(m, c, start.Bodies, cap, TraceNone, nil)
		out[res.Status]++
	}
	return out
}

func requireCounts(t *testing.T, got, want map[BatchClass]int) {
	t.Helper()
	if len(got) != len(want) {
		t.Fatalf("count category mismatch: got %#v want %#v", got, want)
	}
	for k, v := range want {
		if got[k] != v {
			t.Fatalf("count[%s]=%d want %d; all=%#v", k, got[k], v, got)
		}
	}
}

func TestFieldInverseAndSign(t *testing.T) {
	v := Frac(5, 7).Add(Sqrt2().ScaleRat(-3, 5)).Add(Sqrt3().ScaleRat(7, 11)).Add(Sqrt2().Mul(Sqrt3()).ScaleRat(-2, 13))
	if v.Sign() == 0 {
		t.Fatal("test value unexpectedly zero")
	}
	one := v.Mul(v.Inv())
	if !one.Eq(One()) {
		t.Fatalf("v*v^-1=%s, want 1", one.String())
	}
}

func TestSquareL2N2(t *testing.T) {
	requireCounts(t, countsFor(t, "square", 2, 2, 100), map[BatchClass]int{"RETURN": 48, PairCorner: 40, WallCorner: 8})
}

func TestDodecagonL2N2(t *testing.T) {
	requireCounts(t, countsFor(t, "dodecagon", 2, 2, 100), map[BatchClass]int{"RETURN": 64, PairCorner: 24, WallCorner: 8})
}

func TestDodecagonL3N2(t *testing.T) {
	requireCounts(t, countsFor(t, "dodecagon", 3, 2, 100), map[BatchClass]int{"RETURN": 424, PairCorner: 136, WallCorner: 16})
}

func Test24gonL2N2(t *testing.T) {
	requireCounts(t, countsFor(t, "24gon", 2, 2, 100), map[BatchClass]int{"RETURN": 72, "CAP": 16, WallCorner: 8})
}

func TestCenteredDodecagonEN(t *testing.T) {
	m := BuildModel("dodecagon")
	bs, rec, ok := CenteredPairStart(m, 2, 1, "E", "N")
	if !ok {
		t.Fatal("expected face-1 E/N to approach")
	}
	out := Run(m, MakeContainer(m, 2), bs, 100, TraceCompact, []EventRecord{rec})
	if out.Status != "CAP" {
		t.Fatalf("got %s", out.Status)
	}
	if len(out.PairFaceWord) == 0 || out.PairFaceWord[0] != 1 {
		t.Fatalf("unexpected word %#v", out.PairFaceWord)
	}
}

func TestCenteredDodecagonReverseStem(t *testing.T) {
	m := BuildModel("dodecagon")
	forward, _, ok := CenteredPairStart(m, 2, 1, "E", "N")
	if !ok {
		t.Fatal("source seed must be incoming")
	}
	reversed := make([]Body, len(forward))
	for i, b := range forward {
		reversed[i] = Body{
			Pos: Vec{X: b.Pos.X.Clone(), Y: b.Pos.Y.Clone()},
			Vel: Vec{X: b.Vel.X.Neg(), Y: b.Vel.Y.Neg()},
		}
	}
	out := Run(m, MakeContainer(m, 2), reversed, 16, TraceCompact, nil)
	if out.Status != PairCorner || out.EventBatches != 3 {
		t.Fatalf("reverse stem got status=%s steps=%d, want PAIR_CORNER at 3", out.Status, out.EventBatches)
	}
	if len(out.Events) != 3 || out.Events[0].Batch[0].Wall != "S" || out.Events[1].Batch[0].Wall != "W" || out.Events[2].Batch[0].Face != 10 {
		t.Fatalf("unexpected reverse stem events: %#v", out.Events)
	}
}
