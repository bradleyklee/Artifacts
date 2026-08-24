package discovery

import (
	"reflect"
	"testing"

	"verifiedskiplist/beads-usecase/model"
)

func TestSearchPageBinaryPredicateAndContinuation(t *testing.T) {
	m := []model.Memory{
		{ID: "a", Title: "alpha", Body: "no"},
		{ID: "b", Title: "beta", Body: "Needle here"},
		{ID: "c", Title: "needle title", Body: "x"},
		{ID: "d", Title: "delta", Body: "another NEEDLE"},
	}
	p1 := SearchPage(m, "needle", "id", 0, 2)
	if p1.Complete || p1.Continuation == nil || p1.Continuation.Cursor != 3 {
		t.Fatalf("bad first continuation: %#v", p1)
	}
	got := []string{p1.Summaries[0].ID, p1.Summaries[1].ID}
	if !reflect.DeepEqual(got, []string{"b", "c"}) {
		t.Fatalf("first page=%v", got)
	}
	p2 := SearchPage(m, "needle", "id", p1.Continuation.Cursor, 2)
	if !p2.Complete || p2.Continuation != nil || len(p2.Summaries) != 1 || p2.Summaries[0].ID != "d" {
		t.Fatalf("bad second page: %#v", p2)
	}
}
