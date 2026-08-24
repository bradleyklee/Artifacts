package verification

import (
	"math/rand"
	"testing"

	sl "verifiedskiplist/implementation/skiplist"
)

func TestBasicDeterministicSemantics(t *testing.T) {
	s := sl.New[int, int](intOrder)
	if !s.Insert(7, 20) {
		t.Fatal("fresh insert reported replacement")
	}
	if !s.Insert(2, 10) {
		t.Fatal("fresh insert reported replacement")
	}
	if !s.Insert(9, 30) {
		t.Fatal("fresh insert reported replacement")
	}
	if got := s.Values(); len(got) != 3 || got[0] != 10 || got[1] != 20 || got[2] != 30 {
		t.Fatalf("values=%v", got)
	}
	if s.Insert(7, 5) {
		t.Fatal("replacement reported fresh insert")
	}
	if got, ok := s.Lookup(7); !ok || got != 5 {
		t.Fatalf("replacement lookup=%d,%v", got, ok)
	}
	if !s.Delete(2) || s.Delete(2) {
		t.Fatal("delete semantics")
	}
	if err := s.Validate(); err != nil {
		t.Fatal(err)
	}
}

func TestAllInsertionPermutationsThrough9(t *testing.T) {
	for n := 1; n <= 9; n++ {
		a := make([]int, n)
		for i := range a {
			a[i] = i
		}
		count := 0
		permute(a, func(p []int) {
			s := sl.New[int, int](intOrder)
			ref := map[int]int{}
			for _, x := range p {
				s.Insert(x, x)
				ref[x] = x
				assertIntModel(t, s, ref)
			}
			count++
		})
		if count != factorial(n) {
			t.Fatalf("n=%d count=%d want=%d", n, count, factorial(n))
		}
		t.Logf("n=%d insertion histories=%d PASS", n, count)
	}
}

func TestDeterministicMixedReferenceWalk(t *testing.T) {
	const steps = 60000
	r := rand.New(rand.NewSource(0x51A7))
	s := sl.New[int, int](intOrder)
	ref := map[int]int{}
	for i := 0; i < steps; i++ {
		k := r.Intn(41)
		switch r.Intn(3) {
		case 0:
			s.Delete(k)
			delete(ref, k)
		default:
			v := r.Intn(101) - 50
			s.Insert(k, v)
			ref[k] = v
		}
		assertIntModel(t, s, ref)
	}
}

func FuzzOperations(f *testing.F) {
	for _, seed := range [][]byte{{}, {1, 2, 3}, {255, 0, 17, 44, 9}} {
		f.Add(seed)
	}
	f.Fuzz(func(t *testing.T, data []byte) {
		s := sl.New[int, int](intOrder)
		ref := map[int]int{}
		for i := 0; i+2 < len(data); i += 3 {
			k := int(data[i] % 17)
			if data[i+1]&1 == 0 {
				v := int(int8(data[i+2]))
				s.Insert(k, v)
				ref[k] = v
			} else {
				s.Delete(k)
				delete(ref, k)
			}
			assertIntModel(t, s, ref)
		}
	})
}
