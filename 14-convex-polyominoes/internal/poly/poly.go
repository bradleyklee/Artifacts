package poly

import (
	"fmt"
	"math"
	"sort"
)

// The benchmark horizon is intentionally bounded so that every normalized
// coordinate fits in six bits. A Key has 384 bits, enough for 32 points.
const MaxN = 32
const keyWords = 6

type Point struct{ X, Y int }
type Key [keyWords]uint64

type Stats struct {
	Active              uint64
	Extensions          uint64
	OrdinaryTransitions uint64
	PromotedTransitions uint64
	ScheduledNew        uint64
	ScheduledDuplicate  uint64
	OverBoundDropped    uint64
	OverBoundMinTarget  int
	OverBoundMaxTarget  int
	MaxCompletionJump   int
}

func (p Point) less(q Point) bool {
	if p.X != q.X {
		return p.X < q.X
	}
	return p.Y < q.Y
}

func cross(a, b, c Point) int64 {
	return int64(b.X-a.X)*int64(c.Y-a.Y) - int64(b.Y-a.Y)*int64(c.X-a.X)
}

// KeyLess orders canonical encodings lexicographically for deterministic work partitioning.
func KeyLess(a, b Key) bool {
	for i := 0; i < keyWords; i++ {
		if a[i] != b[i] {
			return a[i] < b[i]
		}
	}
	return false
}

func packPoint(k *Key, index int, p Point) {
	if p.X < 0 || p.Y < 0 || p.X >= 64 || p.Y >= 64 {
		panic(fmt.Sprintf("normalized coordinate out of 6-bit range: (%d,%d)", p.X, p.Y))
	}
	bit := index * 12
	word := bit >> 6
	off := bit & 63
	val := uint64(p.X | (p.Y << 6))
	k[word] |= val << off
	if off > 52 { // Presently impossible because 12 divides 64 only at offsets 0,12,...,60.
		k[word+1] |= val >> (64 - off)
	}
}

func unpackPoint(k Key, index int) Point {
	bit := index * 12
	word := bit >> 6
	off := bit & 63
	val := (k[word] >> off) & 0xfff
	if off > 52 {
		val |= (k[word+1] << (64 - off)) & 0xfff
	}
	return Point{int(val & 63), int((val >> 6) & 63)}
}

// Canonical returns the D4 + translation canonical representative of a set of
// distinct points. The input can be in any order.
func Canonical(pts []Point) Key {
	if len(pts) == 0 || len(pts) > MaxN {
		panic("canonical: unsupported size")
	}
	var best Key
	haveBest := false
	var q [MaxN]Point
	for symmetry := 0; symmetry < 8; symmetry++ {
		minX, minY := math.MaxInt, math.MaxInt
		for i, p := range pts {
			var x, y int
			switch symmetry {
			case 0:
				x, y = p.X, p.Y
			case 1:
				x, y = p.X, -p.Y
			case 2:
				x, y = -p.X, p.Y
			case 3:
				x, y = -p.X, -p.Y
			case 4:
				x, y = p.Y, p.X
			case 5:
				x, y = p.Y, -p.X
			case 6:
				x, y = -p.Y, p.X
			default:
				x, y = -p.Y, -p.X
			}
			q[i] = Point{x, y}
			if x < minX {
				minX = x
			}
			if y < minY {
				minY = y
			}
		}
		for i := range pts {
			q[i].X -= minX
			q[i].Y -= minY
		}
		// n is tiny; insertion sort avoids allocation and generic sort cost.
		for i := 1; i < len(pts); i++ {
			x := q[i]
			j := i
			for j > 0 && x.less(q[j-1]) {
				q[j] = q[j-1]
				j--
			}
			q[j] = x
		}
		var k Key
		for i := range pts {
			packPoint(&k, i, q[i])
		}
		if !haveBest || KeyLess(k, best) {
			best, haveBest = k, true
		}
	}
	return best
}

func Decode(k Key, n int) []Point {
	if n < 1 || n > MaxN {
		panic("decode: unsupported size")
	}
	out := make([]Point, n)
	for i := range out {
		out[i] = unpackPoint(k, i)
	}
	return out
}

func containsSorted(pts []Point, p Point) bool {
	i := sort.Search(len(pts), func(i int) bool {
		if pts[i].X != p.X {
			return pts[i].X >= p.X
		}
		return pts[i].Y >= p.Y
	})
	return i < len(pts) && pts[i] == p
}

func sortPoints(pts []Point) {
	for i := 1; i < len(pts); i++ {
		x := pts[i]
		j := i
		for j > 0 && x.less(pts[j-1]) {
			pts[j] = pts[j-1]
			j--
		}
		pts[j] = x
	}
}

// BoundaryExtensions returns each distinct, edge-adjacent vacant grid site.
// Input must be normalized/sorted, as Decode supplies.
func BoundaryExtensions(pts []Point) []Point {
	out := make([]Point, 0, 4*len(pts))
	dx := [4]int{1, -1, 0, 0}
	dy := [4]int{0, 0, 1, -1}
	for _, p := range pts {
		for d := 0; d < 4; d++ {
			q := Point{p.X + dx[d], p.Y + dy[d]}
			if containsSorted(pts, q) {
				continue
			}
			duplicate := false
			for _, prior := range out {
				if prior == q {
					duplicate = true
					break
				}
			}
			if !duplicate {
				out = append(out, q)
			}
		}
	}
	return out
}

// Hull returns strict convex-hull vertices in CCW order. Collinear points on
// hull edges are omitted exactly as required by Pick-count evaluation.
func Hull(input []Point) []Point {
	if len(input) <= 1 {
		return append([]Point(nil), input...)
	}
	pts := append([]Point(nil), input...)
	sortPoints(pts)
	unique := pts[:0]
	for _, p := range pts {
		if len(unique) == 0 || unique[len(unique)-1] != p {
			unique = append(unique, p)
		}
	}
	if len(unique) <= 1 {
		return append([]Point(nil), unique...)
	}
	lower := make([]Point, 0, len(unique))
	for _, p := range unique {
		for len(lower) >= 2 && cross(lower[len(lower)-2], lower[len(lower)-1], p) <= 0 {
			lower = lower[:len(lower)-1]
		}
		lower = append(lower, p)
	}
	upper := make([]Point, 0, len(unique))
	for i := len(unique) - 1; i >= 0; i-- {
		p := unique[i]
		for len(upper) >= 2 && cross(upper[len(upper)-2], upper[len(upper)-1], p) <= 0 {
			upper = upper[:len(upper)-1]
		}
		upper = append(upper, p)
	}
	lower = lower[:len(lower)-1]
	upper = upper[:len(upper)-1]
	return append(lower, upper...)
}

func gcd(a, b int64) int64 {
	if a < 0 {
		a = -a
	}
	if b < 0 {
		b = -b
	}
	for b != 0 {
		a, b = b, a%b
	}
	return a
}

func signedArea2(h []Point) int64 {
	var sum int64
	for i, p := range h {
		q := h[(i+1)%len(h)]
		sum += int64(p.X)*int64(q.Y) - int64(p.Y)*int64(q.X)
	}
	return sum
}

// LatticePointCount applies Pick's theorem (and exact segment cases).
func LatticePointCount(h []Point) int {
	switch len(h) {
	case 0:
		return 0
	case 1:
		return 1
	case 2:
		return int(gcd(int64(h[1].X-h[0].X), int64(h[1].Y-h[0].Y)) + 1)
	}
	a2 := signedArea2(h)
	if a2 < 0 {
		a2 = -a2
	}
	var boundary int64
	for i, p := range h {
		q := h[(i+1)%len(h)]
		boundary += gcd(int64(q.X-p.X), int64(q.Y-p.Y))
	}
	return int((a2 + boundary + 2) / 2)
}

func inOrOnCCWConvexHull(p Point, h []Point) bool {
	for i, a := range h {
		if cross(a, h[(i+1)%len(h)], p) < 0 {
			return false
		}
	}
	return true
}

// Closure creates conv(pts) cap Z^2. Caller commonly avoids this work unless
// LatticePointCount says a completion fits inside the calculation horizon.
func Closure(pts []Point, h []Point, expected int) []Point {
	if len(h) == 0 {
		return nil
	}
	if len(h) == 1 {
		return []Point{h[0]}
	}
	if len(h) == 2 {
		dx, dy := h[1].X-h[0].X, h[1].Y-h[0].Y
		g := int(gcd(int64(dx), int64(dy)))
		sx, sy := dx/g, dy/g
		out := make([]Point, 0, g+1)
		for i := 0; i <= g; i++ {
			out = append(out, Point{h[0].X + i*sx, h[0].Y + i*sy})
		}
		return out
	}
	if signedArea2(h) < 0 {
		hh := append([]Point(nil), h...)
		for i, j := 0, len(hh)-1; i < j; i, j = i+1, j-1 {
			hh[i], hh[j] = hh[j], hh[i]
		}
		h = hh
	}
	minX, maxX, minY, maxY := h[0].X, h[0].X, h[0].Y, h[0].Y
	for _, p := range h[1:] {
		if p.X < minX {
			minX = p.X
		}
		if p.X > maxX {
			maxX = p.X
		}
		if p.Y < minY {
			minY = p.Y
		}
		if p.Y > maxY {
			maxY = p.Y
		}
	}
	out := make([]Point, 0, expected)
	for x := minX; x <= maxX; x++ {
		for y := minY; y <= maxY; y++ {
			if inOrOnCCWConvexHull(Point{x, y}, h) {
				out = append(out, Point{x, y})
			}
		}
	}
	if len(out) != expected {
		panic(fmt.Sprintf("closure raster mismatch: got %d want %d", len(out), expected))
	}
	return out
}

func IsLatticeConvex(pts []Point) bool { return LatticePointCount(Hull(pts)) == len(pts) }

func IsEdgeConnected(pts []Point) bool {
	if len(pts) == 0 {
		return false
	}
	occupied := make(map[Point]struct{}, len(pts))
	for _, p := range pts {
		occupied[p] = struct{}{}
	}
	stack := []Point{pts[0]}
	seen := map[Point]struct{}{pts[0]: {}}
	for len(stack) > 0 {
		p := stack[len(stack)-1]
		stack = stack[:len(stack)-1]
		for _, d := range [][2]int{{1, 0}, {-1, 0}, {0, 1}, {0, -1}} {
			q := Point{p.X + d[0], p.Y + d[1]}
			if _, ok := occupied[q]; !ok {
				continue
			}
			if _, ok := seen[q]; ok {
				continue
			}
			seen[q] = struct{}{}
			stack = append(stack, q)
		}
	}
	return len(seen) == len(pts)
}

// ChildHullCount is the hot exact predicate: it returns the convex hull and
// its total lattice-site count after adding one vacant boundary square.
func ChildHullCount(pts []Point, add Point) ([]Point, int) {
	child := make([]Point, len(pts)+1)
	copy(child, pts)
	child[len(pts)] = add
	h := Hull(child)
	return h, LatticePointCount(h)
}
