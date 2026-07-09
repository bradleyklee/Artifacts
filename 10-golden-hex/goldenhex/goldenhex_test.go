package goldenhex

import (
	"math/big"
	"reflect"
	"testing"
)

func TestCellCounts(t *testing.T) {
	want := []string{
		"3",
		"20",
		"137",
		"939",
		"6436",
		"44113",
		"302355",
		"2072372",
		"14204249",
		"97357371",
	}
	got := CellCounts(len(want) - 1)
	if len(got) != len(want) {
		t.Fatalf("got %d terms, want %d", len(got), len(want))
	}
	for i := range want {
		if got[i].String() != want[i] {
			t.Fatalf("term %d: got %s, want %s", i, got[i].String(), want[i])
		}
	}
}

func TestCountRows(t *testing.T) {
	rows := CountTable(3)
	checks := []struct {
		n       int
		d, h    string
		objects string
		cells   string
	}{
		{0, "1", "1", "2", "3"},
		{1, "3", "14", "17", "20"},
		{2, "20", "97", "117", "137"},
		{3, "137", "665", "802", "939"},
	}
	for i, check := range checks {
		row := rows[i]
		if row.N != check.n || row.Dimers.String() != check.d || row.Hexagons.String() != check.h || row.Objects.String() != check.objects || row.HexagonalCells.String() != check.cells {
			t.Fatalf("row %d mismatch: %+v", i, row)
		}
	}
}

func TestReplayPrefix(t *testing.T) {
	got, err := ReplaySequence(6)
	if err != nil {
		t.Fatal(err)
	}
	want := []int{0, 1, 2, 3, 4, 5, 8, 11, 14, 17, 20, 23}
	if len(got) < len(want) {
		t.Fatalf("got %d replay terms, want at least %d", len(got), len(want))
	}
	if !reflect.DeepEqual(got[:len(want)], want) {
		t.Fatalf("prefix mismatch: got %v, want %v", got[:len(want)], want)
	}
}

func TestScalarRecurrence(t *testing.T) {
	terms := CellCounts(20)
	for n := 2; n < len(terms); n++ {
		left := new(big.Int).Set(&terms[n])
		right := new(big.Int).Mul(big.NewInt(7), &terms[n-1])
		right.Sub(right, &terms[n-2])
		if left.Cmp(right) != 0 {
			t.Fatalf("recurrence failed at n=%d: got %s, want %s", n, left.String(), right.String())
		}
	}
}
