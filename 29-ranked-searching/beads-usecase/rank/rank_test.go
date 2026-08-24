package rank

import (
	"math"
	"reflect"
	"testing"

	"verifiedskiplist/beads-usecase/model"
)

func TestPageRankNormalizedAndDeterministic(t *testing.T) {
	m := []model.Memory{
		{ID: "a", References: []model.Reference{{TargetID: "b"}}},
		{ID: "b", References: []model.Reference{{TargetID: "c"}}},
		{ID: "c", References: []model.Reference{{TargetID: "b"}}},
	}
	a := PageRank(m, .85, 100)
	b := PageRank(m, .85, 100)
	if !reflect.DeepEqual(a, b) {
		t.Fatal("pagerank is not deterministic")
	}
	s := 0.0
	for _, v := range a {
		s += v
	}
	if math.Abs(s-1) > 1e-12 {
		t.Fatalf("rank sum=%g", s)
	}
	if !(a["b"] > a["a"]) {
		t.Fatalf("expected linked node b above a: %#v", a)
	}
}

func TestIndexStableTieBreak(t *testing.T) {
	x := NewIndex()
	x.Upsert("b", 1)
	x.Upsert("a", 1)
	x.Upsert("c", 2)
	if err := x.Validate(); err != nil {
		t.Fatal(err)
	}
	got := x.IDs()
	want := []string{"c", "a", "b"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("got %v want %v", got, want)
	}
	x.Upsert("b", 3)
	if err := x.Validate(); err != nil {
		t.Fatal(err)
	}
	got = x.IDs()
	want = []string{"b", "c", "a"}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("after update got %v want %v", got, want)
	}
}

func TestHubAndAuthorityDirectionsRemainDistinct(t *testing.T) {
	m := []model.Memory{
		{ID: "hub", References: []model.Reference{{TargetID: "a"}, {TargetID: "b"}, {TargetID: "c"}}},
		{ID: "a"}, {ID: "b"}, {ID: "c"},
	}
	pr := PageRank(m, .85, 100)
	rpr := ReversePageRank(m, .85, 100)
	if !(pr["a"] > pr["hub"]) {
		t.Fatalf("ordinary PageRank should favor cited authority: %#v", pr)
	}
	if !(rpr["hub"] > rpr["a"]) {
		t.Fatalf("reverse PageRank should favor original hub: %#v", rpr)
	}
	_, hub := HITS(m, 100)
	if !(hub["hub"] > hub["a"]) {
		t.Fatalf("HITS hub should favor outlink source: %#v", hub)
	}
}

func TestCorpusPriorsAreQueryIndependent(t *testing.T) {
	// Ranking is computed from the frozen graph only. Queries are deliberately
	// absent from Scores/Ordered; lexical matching is a later discovery step.
	m := []model.Memory{
		{ID: "hub", Title: "alpha", References: []model.Reference{{TargetID: "a"}, {TargetID: "b"}}},
		{ID: "a", Title: "beta"},
		{ID: "b", Title: "gamma"},
	}
	for _, strategy := range []string{"indegree", "outdegree", "pagerank", "reverse-pagerank", "global-hits-authority", "global-hits-hub"} {
		first := Ordered(m, strategy)
		second := Ordered(m, strategy)
		if !reflect.DeepEqual(first, second) {
			t.Fatalf("%s corpus prior changed without graph change", strategy)
		}
	}
}
