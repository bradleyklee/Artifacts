package verification

import (
	"sort"
	"testing"
	sl "verifiedskiplist/implementation/skiplist"
)

func BenchmarkBuildSkipList1000(b *testing.B) {
	for i := 0; i < b.N; i++ {
		s := sl.New[int, int](intOrder)
		for k := 0; k < 1000; k++ {
			s.Insert(k, k)
		}
	}
}
func BenchmarkBuildMapSort1000(b *testing.B) {
	for i := 0; i < b.N; i++ {
		m := make(map[int]int, 1000)
		for k := 0; k < 1000; k++ {
			m[k] = k
		}
		a := make([]int, 0, 1000)
		for _, v := range m {
			a = append(a, v)
		}
		sort.Ints(a)
	}
}
