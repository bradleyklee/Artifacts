package crawl

import (
	"testing"

	"verifiedskiplist/beads-usecase/model"
	"verifiedskiplist/beads-usecase/rank"
)

func TestPerfectGuidanceTakesShortestVisibleRoute(t *testing.T) {
	m := []model.Memory{
		{ID: "s", References: []model.Reference{{TargetID: "dead"}, {TargetID: "good"}}},
		{ID: "dead", References: []model.Reference{{TargetID: "d2"}}},
		{ID: "d2"},
		{ID: "good", References: []model.Reference{{TargetID: "target"}}},
		{ID: "target"},
	}
	g := rank.BuildGraph(m)
	d := reverseDistances(g, g.Idx["target"])
	cost := crawlCost(g, d, g.Idx["s"], g.Idx["target"], 1, 1)
	if cost != 3 { // s -> good -> target
		t.Fatalf("guided cost=%d want 3", cost)
	}
}

func TestReachabilityCountsUnreachableTargetsAsFailures(t *testing.T) {
	m := []model.Memory{
		{ID: "a", References: []model.Reference{{TargetID: "b"}}},
		{ID: "b"},
		{ID: "island"},
	}
	r := Analyze(m, []float64{1}, []int{3}, 1)
	var a Node
	for _, n := range r.NodeMetrics {
		if n.ID == "a" {
			a = n
		}
	}
	if a.Reachable != 1 || a.Reachability != .5 {
		t.Fatalf("a reachability=%#v", a)
	}
}
