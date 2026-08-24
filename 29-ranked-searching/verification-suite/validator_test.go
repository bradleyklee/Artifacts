package verification

import (
	"reflect"
	"testing"
	sl "verifiedskiplist/implementation/skiplist"
)

func TestValidatorRejectsDeliberateCorruption(t *testing.T) {
	build := func() *sl.List[int, int] {
		s := sl.New[int, int](intOrder)
		for i := 0; i < 8; i++ {
			s.Insert(i, i)
		}
		if err := s.Validate(); err != nil {
			t.Fatal(err)
		}
		return s
	}
	for _, kind := range []string{"backlink", "type", "tower", "orphan", "ordering"} {
		t.Run(kind, func(t *testing.T) {
			s := build()
			if err := s.CorruptForVerification(kind); err != nil {
				t.Fatal(err)
			}
			if err := s.Validate(); err == nil {
				t.Fatalf("corruption %q accepted", kind)
			}
		})
	}
}

func TestGarbageCollectAndInsertPosition(t *testing.T) {
	s := sl.New[int, int](intOrder)
	for _, x := range []int{10, 20, 30, 40, 50} {
		s.Insert(x, x)
	}
	l, lok, r, rok := s.InsertPosition(35)
	if !lok || !rok || l != 30 || r != 40 {
		t.Fatalf("position=(%d,%v,%d,%v)", l, lok, r, rok)
	}
	s.Delete(50)
	s.Delete(40)
	if !s.GarbageCollect() {
		t.Fatal("expected bookkeeping compaction")
	}
	if err := s.Validate(); err != nil {
		t.Fatal(err)
	}
}

func TestDescendingAndDuplicateValues(t *testing.T) {
	desc := func(a, b int) int { return -intOrder(a, b) }
	s := sl.New[string, int](desc)
	for _, e := range []struct {
		k string
		v int
	}{{"a", 2}, {"b", 1}, {"c", 2}, {"d", 3}} {
		s.Insert(e.k, e.v)
	}
	if err := s.Validate(); err != nil {
		t.Fatal(err)
	}
	if got := s.Values(); !reflect.DeepEqual(got, []int{3, 2, 2, 1}) {
		t.Fatalf("values=%v", got)
	}
	es := s.EntriesAt(1)
	if es[1].Key != "a" || es[2].Key != "c" {
		t.Fatalf("equal stability=%v", es)
	}
	if v, ok := s.PopFirst(); !ok || v != 3 {
		t.Fatalf("PopFirst=%d,%v", v, ok)
	}
	if v, ok := s.PopLast(); !ok || v != 1 {
		t.Fatalf("PopLast=%d,%v", v, ok)
	}
	if err := s.Validate(); err != nil {
		t.Fatal(err)
	}
}
