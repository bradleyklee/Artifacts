package goldenhex

import "math/big"

// CountRow is one row of the integer substitution count table.
type CountRow struct {
	N              int
	Dimers         big.Int
	Hexagons       big.Int
	Objects        big.Int
	HexagonalCells big.Int
}

// CountTable returns rows for n=0..maxN for the D|H fixed-point seed.
//
// The object-count recurrence is
//
//	D' = 2D + H
//	H' = 9D + 5H
//
// and a(n)=2D(n)+H(n) is the total number of unit hexagonal cells.
func CountTable(maxN int) []CountRow {
	if maxN < 0 {
		return nil
	}

	d := big.NewInt(1)
	h := big.NewInt(1)
	rows := make([]CountRow, 0, maxN+1)

	for n := 0; n <= maxN; n++ {
		rows = append(rows, makeCountRow(n, d, h))

		nextD := new(big.Int).Add(new(big.Int).Mul(big.NewInt(2), d), h)
		nextH := new(big.Int).Add(new(big.Int).Mul(big.NewInt(9), d), new(big.Int).Mul(big.NewInt(5), h))
		d, h = nextD, nextH
	}
	return rows
}

func makeCountRow(n int, d, h *big.Int) CountRow {
	var row CountRow
	row.N = n
	row.Dimers.Set(d)
	row.Hexagons.Set(h)
	row.Objects.Add(&row.Dimers, &row.Hexagons)
	row.HexagonalCells.Add(new(big.Int).Mul(big.NewInt(2), &row.Dimers), &row.Hexagons)
	return row
}

// CellCounts returns only a(n)=2D(n)+H(n) for n=0..maxN.
func CellCounts(maxN int) []big.Int {
	rows := CountTable(maxN)
	counts := make([]big.Int, len(rows))
	for i, row := range rows {
		counts[i].Set(&row.HexagonalCells)
	}
	return counts
}
