package graphstats

import (
	"math"
	"testing"
	"verifiedskiplist/beads-usecase/model"
)

func TestConnectivityConcentrationAndReciprocity(t *testing.T) {
	m := []model.Memory{
		{ID: "a", References: []model.Reference{{TargetID: "b"}}},
		{ID: "b", References: []model.Reference{{TargetID: "a"}, {TargetID: "c"}}},
		{ID: "c"},
		{ID: "d"},
	}
	s := Analyze(m, nil)
	if s.Nodes != 4 || s.UniqueInternalEdges != 3 {
		t.Fatalf("bad census: %#v", s)
	}
	if s.WeakComponents != 2 || s.LargestWeakComponent != 3 {
		t.Fatalf("bad weak components: %#v", s)
	}
	if s.StrongComponents != 3 || s.LargestStrongComponent != 2 {
		t.Fatalf("bad SCCs: %#v", s)
	}
	if s.ReciprocatedEdges != 2 || math.Abs(s.Reciprocity-2.0/3.0) > 1e-12 {
		t.Fatalf("bad reciprocity: %#v", s)
	}
	if math.Abs(s.Top1InShare-1.0/3.0) > 1e-12 || math.Abs(s.Top1OutShare-2.0/3.0) > 1e-12 {
		t.Fatalf("bad concentration: %#v", s)
	}
}
