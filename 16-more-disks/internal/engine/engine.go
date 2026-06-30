// Package engine implements the canonical exact fixed-orientation regular-polygon
// billiard model used by artifact 16.  All production evolution happens here in
// Go; this package intentionally has no dependency on the legacy Python core.
package engine

import (
	"crypto/sha256"
	"fmt"
	"math/big"
	"sort"
	"strings"
)

// F is an element of Q(sqrt(2),sqrt(3)) in the fixed basis
// 1, sqrt(2), sqrt(3), sqrt(6).  The four supported models inhabit subfields.
// Values are immutable by convention: every operation returns fresh big.Rat values.
type F struct{ C [4]*big.Rat }

func rat(n, d int64) *big.Rat     { return new(big.Rat).SetFrac(big.NewInt(n), big.NewInt(d)) }
func ratInt(n int64) *big.Rat     { return new(big.Rat).SetInt64(n) }
func ratCopy(x *big.Rat) *big.Rat { return new(big.Rat).Set(x) }
func ratNeg(x *big.Rat) *big.Rat  { return new(big.Rat).Neg(x) }
func ratAdd(xs ...*big.Rat) *big.Rat {
	r := new(big.Rat)
	for _, x := range xs {
		r.Add(r, x)
	}
	return r
}
func ratSub(x, y *big.Rat) *big.Rat         { return new(big.Rat).Sub(x, y) }
func ratMul(x, y *big.Rat) *big.Rat         { return new(big.Rat).Mul(x, y) }
func ratScale(x *big.Rat, n int64) *big.Rat { return new(big.Rat).Mul(x, ratInt(n)) }

func NewF(a, b, c, d *big.Rat) F {
	return F{[4]*big.Rat{ratCopy(a), ratCopy(b), ratCopy(c), ratCopy(d)}}
}
func Q(n int64) F       { return NewF(ratInt(n), ratInt(0), ratInt(0), ratInt(0)) }
func Frac(n, d int64) F { return NewF(rat(n, d), ratInt(0), ratInt(0), ratInt(0)) }
func Sqrt2() F          { return NewF(ratInt(0), ratInt(1), ratInt(0), ratInt(0)) }
func Sqrt3() F          { return NewF(ratInt(0), ratInt(0), ratInt(1), ratInt(0)) }
func Zero() F           { return Q(0) }
func One() F            { return Q(1) }

func (x F) Clone() F { return NewF(x.C[0], x.C[1], x.C[2], x.C[3]) }
func (x F) Add(y F) F {
	return NewF(ratAdd(x.C[0], y.C[0]), ratAdd(x.C[1], y.C[1]), ratAdd(x.C[2], y.C[2]), ratAdd(x.C[3], y.C[3]))
}
func (x F) Neg() F    { return NewF(ratNeg(x.C[0]), ratNeg(x.C[1]), ratNeg(x.C[2]), ratNeg(x.C[3])) }
func (x F) Sub(y F) F { return x.Add(y.Neg()) }
func (x F) ScaleRat(n, d int64) F {
	s := rat(n, d)
	return NewF(ratMul(x.C[0], s), ratMul(x.C[1], s), ratMul(x.C[2], s), ratMul(x.C[3], s))
}
func (x F) Mul(y F) F {
	// (a+b r2+c r3+d r6)(e+f r2+g r3+h r6)
	a, b, c, d := x.C[0], x.C[1], x.C[2], x.C[3]
	e, f, g, h := y.C[0], y.C[1], y.C[2], y.C[3]
	A := ratAdd(ratMul(a, e), ratScale(ratMul(b, f), 2), ratScale(ratMul(c, g), 3), ratScale(ratMul(d, h), 6))
	B := ratAdd(ratMul(a, f), ratMul(b, e), ratScale(ratMul(c, h), 3), ratScale(ratMul(d, g), 3))
	C := ratAdd(ratMul(a, g), ratMul(c, e), ratScale(ratMul(b, h), 2), ratScale(ratMul(d, f), 2))
	D := ratAdd(ratMul(a, h), ratMul(d, e), ratMul(b, g), ratMul(c, f))
	return NewF(A, B, C, D)
}

// q2 represents a+b sqrt(2), used only inside exact sign and inverse routines.
type q2 struct{ a, b *big.Rat }

func q2from(a, b *big.Rat) q2 { return q2{ratCopy(a), ratCopy(b)} }
func (x q2) add(y q2) q2      { return q2{ratAdd(x.a, y.a), ratAdd(x.b, y.b)} }
func (x q2) neg() q2          { return q2{ratNeg(x.a), ratNeg(x.b)} }
func (x q2) sub(y q2) q2      { return x.add(y.neg()) }
func (x q2) mul(y q2) q2 {
	return q2{ratAdd(ratMul(x.a, y.a), ratScale(ratMul(x.b, y.b), 2)), ratAdd(ratMul(x.a, y.b), ratMul(x.b, y.a))}
}
func (x q2) scale(n int64) q2 { return q2{ratScale(x.a, n), ratScale(x.b, n)} }
func (x q2) inv() q2 {
	den := ratSub(ratMul(x.a, x.a), ratScale(ratMul(x.b, x.b), 2))
	if den.Sign() == 0 {
		panic("inverse of zero q2")
	}
	return q2{new(big.Rat).Quo(x.a, den), new(big.Rat).Quo(ratNeg(x.b), den)}
}
func (x q2) sign() int {
	sa, sb := x.a.Sign(), x.b.Sign()
	if sa == 0 && sb == 0 {
		return 0
	}
	if sb == 0 {
		return sa
	}
	if sa == 0 {
		return sb
	}
	if (sa > 0) == (sb > 0) {
		if sa > 0 {
			return 1
		}
		return -1
	}
	delta := ratSub(ratMul(x.a, x.a), ratScale(ratMul(x.b, x.b), 2))
	sd := delta.Sign()
	if sa > 0 {
		return sd
	}
	return -sd
}

// Sign is an exact comparison with zero.  It avoids floating-point interval
// decisions by reducing Q(sqrt(2),sqrt(3)) comparisons to Q(sqrt(2)).
func (x F) Sign() int {
	A := q2from(x.C[0], x.C[1])
	B := q2from(x.C[2], x.C[3])
	sa, sb := A.sign(), B.sign()
	if sb == 0 {
		return sa
	}
	if sa == 0 {
		return sb
	}
	if (sa > 0) == (sb > 0) {
		if sa > 0 {
			return 1
		}
		return -1
	}
	// Compare A - |B| sqrt(3) by multiplying by its positive conjugate.
	D := A.mul(A).sub(B.mul(B).scale(3))
	sd := D.sign()
	if sa > 0 {
		return sd
	}
	return -sd
}
func (x F) IsZero() bool {
	return x.C[0].Sign() == 0 && x.C[1].Sign() == 0 && x.C[2].Sign() == 0 && x.C[3].Sign() == 0
}
func (x F) Eq(y F) bool {
	for i := 0; i < 4; i++ {
		if x.C[i].Cmp(y.C[i]) != 0 {
			return false
		}
	}
	return true
}
func (x F) Cmp(y F) int { return x.Sub(y).Sign() }
func (x F) Inv() F {
	A := q2from(x.C[0], x.C[1])
	B := q2from(x.C[2], x.C[3])
	den := A.mul(A).sub(B.mul(B).scale(3))
	if den.sign() == 0 {
		panic("inverse of zero field element")
	}
	di := den.inv()
	ai := A.mul(di)
	bi := B.mul(di).neg()
	return NewF(ai.a, ai.b, bi.a, bi.b)
}
func (x F) Div(y F) F { return x.Mul(y.Inv()) }
func (x F) String() string {
	return fmt.Sprintf("[%s,%s,%s,%s]", x.C[0].RatString(), x.C[1].RatString(), x.C[2].RatString(), x.C[3].RatString())
}
func (x F) Approx64() float64 {
	a, _ := x.C[0].Float64()
	b, _ := x.C[1].Float64()
	c, _ := x.C[2].Float64()
	d, _ := x.C[3].Float64()
	return a + b*1.4142135623730951 + c*1.7320508075688772 + d*2.449489742783178
}

type Vec struct{ X, Y F }

func (x Vec) Add(y Vec) Vec { return Vec{x.X.Add(y.X), x.Y.Add(y.Y)} }
func (x Vec) Sub(y Vec) Vec { return Vec{x.X.Sub(y.X), x.Y.Sub(y.Y)} }
func (x Vec) Scale(t F) Vec { return Vec{x.X.Mul(t), x.Y.Mul(t)} }
func Dot(a, b Vec) F        { return a.X.Mul(b.X).Add(a.Y.Mul(b.Y)) }

type Body struct{ Pos, Vel Vec }

func (b Body) Clone() Body {
	return Body{Vec{b.Pos.X.Clone(), b.Pos.Y.Clone()}, Vec{b.Vel.X.Clone(), b.Vel.Y.Clone()}}
}

type Model struct {
	ID            string
	Sides         int
	Field         string
	Edge, Apothem F
	Normals       []Vec
}

func (m Model) CellSide() F { return m.Apothem.ScaleRat(4, 1) }
func (m Model) CardinalFaces() []int {
	stride := m.Sides / 4
	return []int{0, stride, 2 * stride, 3 * stride}
}
func (m Model) IsCardinalFace(face int) bool {
	for _, v := range m.CardinalFaces() {
		if v == face {
			return true
		}
	}
	return false
}
func (m Model) FaceAngleDegrees(face int) string { return fmt.Sprintf("%d/%d*360", face, m.Sides) }

func BuildModel(name string) Model {
	z := Zero()
	one := One()
	half := Frac(1, 2)
	s2 := Sqrt2()
	s3 := Sqrt3()
	switch name {
	case "square", "4gon", "4":
		return Model{ID: "square", Sides: 4, Field: "Q", Edge: Frac(1, 2), Apothem: Frac(1, 4), Normals: []Vec{{one, z}, {z, one}, {one.Neg(), z}, {z, one.Neg()}}}
	case "octagon", "8gon", "8":
		h := s2.ScaleRat(1, 2)
		return Model{ID: "octagon", Sides: 8, Field: "Q(sqrt(2))", Edge: Frac(1, 2), Apothem: one.Add(s2).ScaleRat(1, 4), Normals: []Vec{{one, z}, {h, h}, {z, one}, {h.Neg(), h}, {one.Neg(), z}, {h.Neg(), h.Neg()}, {z, one.Neg()}, {h, h.Neg()}}}
	case "dodecagon", "12gon", "12":
		h := s3.ScaleRat(1, 2)
		return Model{ID: "dodecagon", Sides: 12, Field: "Q(sqrt(3))", Edge: Frac(1, 2), Apothem: Frac(1, 2).Add(s3.ScaleRat(1, 4)), Normals: []Vec{{one, z}, {h, half}, {half, h}, {z, one}, {half.Neg(), h}, {h.Neg(), half}, {one.Neg(), z}, {h.Neg(), half.Neg()}, {half.Neg(), h.Neg()}, {z, one.Neg()}, {half, h.Neg()}, {h, half.Neg()}}}
	case "24gon", "icositetragon", "24":
		s6 := s2.Mul(s3)
		c15 := s6.Add(s2).ScaleRat(1, 4)
		s15 := s6.Sub(s2).ScaleRat(1, 4)
		c30 := s3.ScaleRat(1, 2)
		s30 := half
		c45 := s2.ScaleRat(1, 2)
		s45 := c45
		c60 := half
		s60 := s3.ScaleRat(1, 2)
		c75 := s6.Sub(s2).ScaleRat(1, 4)
		s75 := s6.Add(s2).ScaleRat(1, 4)
		base := []Vec{{one, z}, {c15, s15}, {c30, s30}, {c45, s45}, {c60, s60}, {c75, s75}, {z, one}}
		ns := make([]Vec, 24)
		for k := 0; k < 24; k++ {
			switch {
			case k <= 6:
				ns[k] = base[k]
			case k <= 12:
				p := base[12-k]
				ns[k] = Vec{p.X.Neg(), p.Y}
			case k <= 18:
				p := base[k-12]
				ns[k] = Vec{p.X.Neg(), p.Y.Neg()}
			default:
				p := base[24-k]
				ns[k] = Vec{p.X, p.Y.Neg()}
			}
		}
		tan75 := s15.Div(one.Add(c15))
		ap := Frac(1, 4).Div(tan75)
		return Model{ID: "24gon", Sides: 24, Field: "Q(sqrt(2),sqrt(3))", Edge: Frac(1, 2), Apothem: ap, Normals: ns}
	default:
		panic("unknown model " + name)
	}
}

type Container struct {
	Cells    int
	HalfSide F
}

func MakeContainer(m Model, L int) Container {
	if L < 2 {
		panic("L must be >=2")
	}
	return Container{L, m.CellSide().ScaleRat(int64(L), 2)}
}
func LatticeSites(m Model, L int) []Vec {
	d := m.CellSide()
	out := make([]Vec, 0, L*L)
	for y := 0; y < L; y++ {
		for x := 0; x < L; x++ {
			xf := d.ScaleRat(int64(2*x+1-L), 2)
			yf := d.ScaleRat(int64(2*y+1-L), 2)
			out = append(out, Vec{xf, yf})
		}
	}
	return out
}
func CardinalVelocities() map[string]Vec {
	z := Zero()
	o := One()
	return map[string]Vec{"E": {o, z}, "W": {o.Neg(), z}, "N": {z, o}, "S": {z, o.Neg()}}
}
func CardinalNames() []string { return []string{"E", "W", "N", "S"} }

type Event struct {
	DT     F
	Kind   string
	Bodies []int
	Face   int
	Wall   string
}

func (e Event) Key() string { return fmt.Sprintf("%s/%v/%d/%s", e.Kind, e.Bodies, e.Face, e.Wall) }

type BatchClass string

const (
	Regular              BatchClass = "REGULAR"
	IndependentBatch     BatchClass = "INDEPENDENT_BATCH"
	IndependentWallBatch BatchClass = "INDEPENDENT_WALL_BATCH"
	PairCorner           BatchClass = "PAIR_CORNER"
	WallCorner           BatchClass = "WALL_CORNER"
	CoupledSimultaneous  BatchClass = "COUPLED_SIMULTANEOUS"
	NoEvent              BatchClass = "NO_EVENT"
)

func (c BatchClass) Resolvable() bool {
	return c == Regular || c == IndependentBatch || c == IndependentWallBatch
}

func activeFaces(m Model, d Vec) []int {
	out := []int{}
	threshold := m.Apothem.ScaleRat(2, 1)
	for k, n := range m.Normals {
		if Dot(n, d).Sub(threshold).Sign() == 0 {
			out = append(out, k)
		}
	}
	return out
}
func insideDifference(m Model, d Vec) bool {
	threshold := m.Apothem.ScaleRat(2, 1)
	for _, n := range m.Normals {
		if Dot(n, d).Sub(threshold).Sign() > 0 {
			return false
		}
	}
	return true
}
func pairCandidate(m Model, bs []Body, i, j int) *Event {
	d := bs[j].Pos.Sub(bs[i].Pos)
	rel := bs[j].Vel.Sub(bs[i].Vel)
	threshold := m.Apothem.ScaleRat(2, 1)
	var best *Event
	for face, n := range m.Normals {
		derivative := Dot(n, rel)
		gap := Dot(n, d).Sub(threshold)
		if derivative.Sign() >= 0 || gap.Sign() <= 0 {
			continue
		}
		dt := gap.Neg().Div(derivative)
		if dt.Sign() <= 0 {
			continue
		}
		loc := d.Add(rel.Scale(dt))
		if !insideDifference(m, loc) || Dot(n, loc).Sub(threshold).Sign() != 0 {
			continue
		}
		if best == nil || dt.Cmp(best.DT) < 0 {
			best = &Event{DT: dt, Kind: "PAIR_FACE", Bodies: []int{i, j}, Face: face, Wall: ""}
		}
	}
	if best == nil {
		return nil
	}
	if len(activeFaces(m, d.Add(rel.Scale(best.DT)))) != 1 {
		best.Kind = "PAIR_CORNER"
	}
	return best
}
func wallCandidates(m Model, c Container, bs []Body, i int) []Event {
	b := bs[i]
	out := []Event{}
	specs := []struct {
		coord, vel F
		wall       string
		sign       int
	}{
		{b.Pos.X, b.Vel.X, "E", 1}, {b.Pos.X, b.Vel.X, "W", -1}, {b.Pos.Y, b.Vel.Y, "N", 1}, {b.Pos.Y, b.Vel.Y, "S", -1},
	}
	for _, s := range specs {
		target := c.HalfSide.Sub(m.Apothem)
		if s.sign < 0 {
			target = c.HalfSide.Neg().Add(m.Apothem)
		}
		speed := s.vel
		if s.sign < 0 {
			speed = speed.Neg()
		}
		gap := target.Sub(s.coord)
		if s.sign < 0 {
			gap = s.coord.Sub(target)
		}
		if speed.Sign() > 0 && gap.Sign() > 0 {
			out = append(out, Event{DT: gap.Div(speed), Kind: "WALL_FACE", Bodies: []int{i}, Face: -1, Wall: s.wall})
		}
	}
	return out
}
func NextBatch(m Model, c Container, bs []Body) ([]Event, BatchClass) {
	es := []Event{}
	for i := range bs {
		es = append(es, wallCandidates(m, c, bs, i)...)
	}
	for i := 0; i < len(bs); i++ {
		for j := i + 1; j < len(bs); j++ {
			if e := pairCandidate(m, bs, i, j); e != nil {
				es = append(es, *e)
			}
		}
	}
	if len(es) == 0 {
		return nil, NoEvent
	}
	dt := es[0].DT
	for _, e := range es[1:] {
		if e.DT.Cmp(dt) < 0 {
			dt = e.DT
		}
	}
	batch := []Event{}
	for _, e := range es {
		if e.DT.Cmp(dt) == 0 {
			batch = append(batch, e)
		}
	}
	for _, e := range batch {
		if e.Kind == "PAIR_CORNER" {
			return batch, PairCorner
		}
	}
	wallSeen := map[int]bool{}
	for _, e := range batch {
		if e.Kind == "WALL_FACE" {
			id := e.Bodies[0]
			if wallSeen[id] {
				return batch, WallCorner
			}
			wallSeen[id] = true
		}
	}
	if len(batch) == 1 {
		return batch, Regular
	}
	involved := map[int]bool{}
	n := 0
	allWall := true
	for _, e := range batch {
		if e.Kind != "WALL_FACE" {
			allWall = false
		}
		for _, id := range e.Bodies {
			involved[id] = true
			n++
		}
	}
	if len(involved) == n {
		if allWall {
			return batch, IndependentWallBatch
		}
		return batch, IndependentBatch
	}
	return batch, CoupledSimultaneous
}
func Advance(bs []Body, dt F) {
	for i := range bs {
		bs[i].Pos = bs[i].Pos.Add(bs[i].Vel.Scale(dt))
	}
}
func Resolve(m Model, bs []Body, e Event) {
	if e.Kind == "WALL_FACE" {
		i := e.Bodies[0]
		if e.Wall == "E" || e.Wall == "W" {
			bs[i].Vel.X = bs[i].Vel.X.Neg()
		} else {
			bs[i].Vel.Y = bs[i].Vel.Y.Neg()
		}
		return
	}
	if e.Kind != "PAIR_FACE" || e.Face < 0 {
		panic("cannot resolve " + e.Kind)
	}
	i, j := e.Bodies[0], e.Bodies[1]
	n := m.Normals[e.Face]
	g := Dot(n, bs[j].Vel.Sub(bs[i].Vel))
	bs[i].Vel = bs[i].Vel.Add(n.Scale(g))
	bs[j].Vel = bs[j].Vel.Sub(n.Scale(g))
}

// Metrics contain both integer magnitudes and exact bit lengths.  They are
// carried in output as decimal strings so records do not depend on machine ints.
type MetricGroup struct {
	MaxAbsNumerator, MaxDenominator      *big.Int
	MaxNumeratorBits, MaxDenominatorBits int
}
type Metrics struct{ Positions, Velocities, All MetricGroup }

func emptyGroup() MetricGroup { return MetricGroup{big.NewInt(0), big.NewInt(1), 0, 1} }
func groupOf(xs []F) MetricGroup {
	g := emptyGroup()
	for _, x := range xs {
		for _, r := range x.C {
			n := new(big.Int).Abs(r.Num())
			d := new(big.Int).Set(r.Denom())
			if n.Cmp(g.MaxAbsNumerator) > 0 {
				g.MaxAbsNumerator = n
				g.MaxNumeratorBits = n.BitLen()
			}
			if d.Cmp(g.MaxDenominator) > 0 {
				g.MaxDenominator = d
				g.MaxDenominatorBits = d.BitLen()
			}
		}
	}
	return g
}
func StateMetrics(bs []Body) Metrics {
	p := []F{}
	v := []F{}
	for _, b := range bs {
		p = append(p, b.Pos.X, b.Pos.Y)
		v = append(v, b.Vel.X, b.Vel.Y)
	}
	a := append(append([]F{}, p...), v...)
	return Metrics{groupOf(p), groupOf(v), groupOf(a)}
}
func maxGroup(a, b MetricGroup) MetricGroup {
	r := a
	if b.MaxAbsNumerator.Cmp(r.MaxAbsNumerator) > 0 {
		r.MaxAbsNumerator = new(big.Int).Set(b.MaxAbsNumerator)
		r.MaxNumeratorBits = b.MaxNumeratorBits
	}
	if b.MaxDenominator.Cmp(r.MaxDenominator) > 0 {
		r.MaxDenominator = new(big.Int).Set(b.MaxDenominator)
		r.MaxDenominatorBits = b.MaxDenominatorBits
	}
	return r
}
func MaxMetrics(a, b Metrics) Metrics {
	return Metrics{maxGroup(a.Positions, b.Positions), maxGroup(a.Velocities, b.Velocities), maxGroup(a.All, b.All)}
}

func StateKey(bs []Body) string {
	var s strings.Builder
	for _, b := range bs {
		for _, v := range []F{b.Pos.X, b.Pos.Y, b.Vel.X, b.Vel.Y} {
			for _, r := range v.C {
				s.WriteString(r.RatString())
				s.WriteByte(',')
			}
		}
		s.WriteByte('|')
	}
	return s.String()
}
func StateHash(bs []Body) string {
	h := sha256.Sum256([]byte(StateKey(bs)))
	return fmt.Sprintf("%x", h[:])
}

// EventRecord is intentionally engine-level and exact; io.go supplies portable
// JSON conversion so no float can enter a certificate.
type EventRecord struct {
	Step              int
	DT, T             F
	Class             BatchClass
	Batch             []Event
	PreHash, PostHash string
	Pre, Post         []Body
	Metrics           Metrics
}
type Outcome struct {
	Status                                                BatchClass
	EventBatches                                          int
	T                                                     F
	Events                                                []EventRecord
	Final                                                 []Body
	FinalHash                                             string
	DistinctStates                                        int
	PairFaceWord                                          []int
	InitialMetrics, FinalMetrics, MaxMetrics              Metrics
	FirstDenominatorPromotion, FirstNumeratorHeightGrowth int
	ReturnPreperiod, ReturnPeriod                         int
}

type TraceMode int

const (
	TraceNone TraceMode = iota
	TraceCompact
	TraceFull
)

func copyBodies(bs []Body) []Body {
	out := make([]Body, len(bs))
	for i, b := range bs {
		out[i] = b.Clone()
	}
	return out
}
func Run(m Model, c Container, start []Body, cap int, mode TraceMode, initial []EventRecord) Outcome {
	bs := copyBodies(start)
	t := Zero()
	seen := map[string]int{StateKey(bs): 0}
	events := append([]EventRecord{}, initial...)
	pairWord := []int{}
	for _, r := range initial {
		for _, e := range r.Batch {
			if e.Kind == "PAIR_FACE" && e.Face >= 0 {
				pairWord = append(pairWord, e.Face)
			}
		}
	}
	initialMetrics := StateMetrics(bs)
	high := initialMetrics
	fd, fh := 0, 0
	finish := func(status BatchClass, step int) Outcome {
		final := StateMetrics(bs)
		return Outcome{Status: status, EventBatches: step, T: t, Events: events, Final: copyBodies(bs), FinalHash: StateHash(bs), DistinctStates: len(seen), PairFaceWord: pairWord, InitialMetrics: initialMetrics, FinalMetrics: final, MaxMetrics: high, FirstDenominatorPromotion: fd, FirstNumeratorHeightGrowth: fh}
	}
	for step := 1; step <= cap; step++ {
		batch, class := NextBatch(m, c, bs)
		if class == NoEvent {
			return finish(NoEvent, step-1)
		}
		dt := batch[0].DT
		preHash := StateHash(bs)
		var pre []Body
		if mode == TraceFull {
			pre = copyBodies(bs)
		}
		Advance(bs, dt)
		t = t.Add(dt)
		rec := EventRecord{Step: step, DT: dt, T: t, Class: class, Batch: batch, PreHash: preHash}
		if !class.Resolvable() {
			if mode == TraceFull {
				rec.Pre = pre
				rec.Post = copyBodies(bs)
			}
			if mode != TraceNone {
				events = append(events, rec)
			}
			return finish(class, step)
		}
		for _, e := range batch {
			Resolve(m, bs, e)
			if e.Kind == "PAIR_FACE" && e.Face >= 0 {
				pairWord = append(pairWord, e.Face)
			}
		}
		metrics := StateMetrics(bs)
		high = MaxMetrics(high, metrics)
		if fd == 0 && metrics.All.MaxDenominator.Cmp(initialMetrics.All.MaxDenominator) > 0 {
			fd = step
		}
		if fh == 0 && metrics.All.MaxAbsNumerator.Cmp(initialMetrics.All.MaxAbsNumerator) > 0 {
			fh = step
		}
		key := StateKey(bs)
		rec.PostHash = StateHash(bs)
		rec.Metrics = metrics
		if mode == TraceFull {
			rec.Pre = pre
			rec.Post = copyBodies(bs)
		}
		if mode != TraceNone {
			events = append(events, rec)
		}
		if prior, ok := seen[key]; ok {
			out := finish("RETURN", step)
			out.ReturnPreperiod = prior
			out.ReturnPeriod = step - prior
			return out
		}
		seen[key] = step
	}
	return finish("CAP", cap)
}

// LatticeStarts is the exact exhaustive raw ordering: increasing lexicographic
// combinations of site IDs followed by E,W,N,S velocity words.
type LatticeStart struct {
	Sites      []int
	Velocities []string
	Bodies     []Body
	Ordinal    int
}

func LatticeStarts(m Model, L, N int) []LatticeStart {
	sites := LatticeSites(m, L)
	names := CardinalNames()
	vels := CardinalVelocities()
	out := []LatticeStart{}
	ordinal := 0
	comb := make([]int, N)
	var walk func(int, int)
	walk = func(pos, start int) {
		if pos == N {
			var velocities func(int, []string)
			velocities = func(k int, word []string) {
				if k == N {
					ordinal++
					bs := make([]Body, N)
					for i := 0; i < N; i++ {
						bs[i] = Body{sites[comb[i]], vels[word[i]]}
					}
					out = append(out, LatticeStart{append([]int{}, comb...), append([]string{}, word...), bs, ordinal})
					return
				}
				for _, name := range names {
					velocities(k+1, append(word, name))
				}
			}
			velocities(0, nil)
			return
		}
		for x := start; x <= len(sites)-(N-pos); x++ {
			comb[pos] = x
			walk(pos+1, x+1)
		}
	}
	walk(0, 0)
	return out
}

// CenteredPairStart returns the post-time-zero collision state plus the
// self-contained time-zero record.  Initial incoming velocities must approach
// the prescribed face strictly.
func CenteredPairStart(m Model, L, face int, va, vb string) ([]Body, EventRecord, bool) {
	if face < 0 || face >= m.Sides {
		panic("bad face")
	}
	vels := CardinalVelocities()
	n := m.Normals[face]
	a := m.Apothem
	bs := []Body{{n.Scale(a.Neg()), vels[va]}, {n.Scale(a), vels[vb]}}
	g := Dot(n, bs[1].Vel.Sub(bs[0].Vel))
	if g.Sign() >= 0 {
		return nil, EventRecord{}, false
	}
	e := Event{DT: Zero(), Kind: "PAIR_FACE", Bodies: []int{0, 1}, Face: face}
	Resolve(m, bs, e)
	rec := EventRecord{Step: 0, DT: Zero(), T: Zero(), Class: "INITIAL_PAIR_FACE", Batch: []Event{e}, PostHash: StateHash(bs), Post: copyBodies(bs)}
	return bs, rec, true
}

// CanonicalBatchString gives compact, stable event identifiers for sequence and
// scan files.  Pair faces are written Pij:f; walls Wij:D.
func CanonicalBatchString(batch []Event) string {
	parts := make([]string, len(batch))
	for i, e := range batch {
		if e.Kind == "PAIR_FACE" || e.Kind == "PAIR_CORNER" {
			parts[i] = fmt.Sprintf("P%d%d:%d", e.Bodies[0], e.Bodies[1], e.Face)
		} else {
			parts[i] = fmt.Sprintf("W%d:%s", e.Bodies[0], e.Wall)
		}
	}
	sort.Strings(parts)
	return strings.Join(parts, "+")
}
