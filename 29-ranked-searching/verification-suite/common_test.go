package verification

import (
	"fmt"
	"reflect"
	"sort"
	"testing"

	sl "verifiedskiplist/implementation/skiplist"
)

func intOrder(a, b int) int {
	switch {
	case a < b:
		return 1
	case a > b:
		return -1
	default:
		return 0
	}
}

func assertIntModel(t *testing.T, s *sl.List[int, int], ref map[int]int) {
	t.Helper()
	if err := s.Validate(); err != nil {
		t.Fatalf("Validate: %v; shape=%s", err, s.ShapeSignature())
	}
	want := make([]int, 0, len(ref))
	for _, v := range ref {
		want = append(want, v)
	}
	sort.Ints(want)
	got := s.Values()
	if len(want) == 0 {
		want = nil
	}
	if !reflect.DeepEqual(got, want) {
		t.Fatalf("values: got=%v want=%v", got, want)
	}
	if s.Len() != len(ref) {
		t.Fatalf("len=%d want=%d", s.Len(), len(ref))
	}
	for k, v := range ref {
		gv, ok := s.Lookup(k)
		if !ok || gv != v {
			t.Fatalf("lookup %d: got=%d,%v want=%d,true", k, gv, ok, v)
		}
	}
}

func permute(a []int, f func([]int)) {
	var rec func(int)
	rec = func(i int) {
		if i == len(a) {
			f(append([]int(nil), a...))
			return
		}
		for j := i; j < len(a); j++ {
			a[i], a[j] = a[j], a[i]
			rec(i + 1)
			a[i], a[j] = a[j], a[i]
		}
	}
	rec(0)
}

func factorial(n int) int {
	out := 1
	for i := 2; i <= n; i++ {
		out *= i
	}
	return out
}

func shapeWithKeys[K comparable, V any](s *sl.List[K, V]) string {
	return fmt.Sprintf("%s len=%d depth=%d", s.ShapeSignature(), s.Len(), s.Depth())
}
