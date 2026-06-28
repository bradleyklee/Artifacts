// n3-three-body is an exact Q(sqrt(2)) D4-reduced search over three
// unit-edge octagons in the N=3 square 4.8.8 container.
// No floating point arithmetic is used in dynamics or recurrence.
package main

import (
	"crypto/sha256"
	"encoding/json"
	"flag"
	"fmt"
	"math/big"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

// Q2 represents a + b*sqrt(2), a,b rational.
type Q2 struct{ A, B *big.Rat }

func q(a, b int64) Q2            { return Q2{big.NewRat(a, 1), big.NewRat(b, 1)} }
func qrats(a, b *big.Rat) Q2     { return Q2{new(big.Rat).Set(a), new(big.Rat).Set(b)} }
func (x Q2) add(y Q2) Q2         { return qrats(new(big.Rat).Add(x.A, y.A), new(big.Rat).Add(x.B, y.B)) }
func (x Q2) sub(y Q2) Q2         { return qrats(new(big.Rat).Sub(x.A, y.A), new(big.Rat).Sub(x.B, y.B)) }
func (x Q2) scale(r *big.Rat) Q2 { return qrats(new(big.Rat).Mul(x.A, r), new(big.Rat).Mul(x.B, r)) }
func (x Q2) div(r *big.Rat) Q2   { return qrats(new(big.Rat).Quo(x.A, r), new(big.Rat).Quo(x.B, r)) }
func (x Q2) eq(y Q2) bool        { return x.A.Cmp(y.A) == 0 && x.B.Cmp(y.B) == 0 }
func (x Q2) sign() int {
	as, bs := x.A.Sign(), x.B.Sign()
	if bs == 0 {
		return as
	}
	if as == 0 {
		return bs
	}
	if as == bs {
		return as
	}
	aa := new(big.Rat).Mul(x.A, x.A)
	bb := new(big.Rat).Mul(x.B, x.B)
	bb.Mul(bb, big.NewRat(2, 1))
	c := aa.Cmp(bb)
	if as > 0 && bs < 0 {
		return c
	}
	return -c
}
func (x Q2) cmp(y Q2) int { return x.sub(y).sign() }
func (x Q2) key() string  { return x.A.RatString() + ";" + x.B.RatString() }

type Q2Wire struct {
	A string `json:"a"`
	B string `json:"b"`
}

func (x Q2) wire() Q2Wire { return Q2Wire{x.A.RatString(), x.B.RatString()} }

type RatVec struct{ X, Y *big.Rat }

func rv(x, y int64) RatVec  { return RatVec{big.NewRat(x, 1), big.NewRat(y, 1)} }
func (v RatVec) cp() RatVec { return RatVec{new(big.Rat).Set(v.X), new(big.Rat).Set(v.Y)} }
func (v RatVec) sub(w RatVec) RatVec {
	return RatVec{new(big.Rat).Sub(v.X, w.X), new(big.Rat).Sub(v.Y, w.Y)}
}
func (v RatVec) key() string { return v.X.RatString() + "," + v.Y.RatString() }

type VecQ2 struct{ X, Y Q2 }

func (v VecQ2) sub(w VecQ2) VecQ2 { return VecQ2{v.X.sub(w.X), v.Y.sub(w.Y)} }
func (v VecQ2) addVel(w RatVec, t Q2) VecQ2 {
	return VecQ2{v.X.add(t.scale(w.X)), v.Y.add(t.scale(w.Y))}
}
func (v VecQ2) key() string { return v.X.key() + "," + v.Y.key() }

type Face struct {
	Name    string
	NX, NY  int64
	Support Q2
}

var faces = []Face{
	{"E", 1, 0, q(1, 1).scale(big.NewRat(1, 4))},
	{"NE", 1, 1, q(1, 1).scale(big.NewRat(1, 4)).add(q(1, 0).scale(big.NewRat(1, 4)))},
	{"N", 0, 1, q(1, 1).scale(big.NewRat(1, 4))},
	{"NW", -1, 1, q(1, 1).scale(big.NewRat(1, 4)).add(q(1, 0).scale(big.NewRat(1, 4)))},
	{"W", -1, 0, q(1, 1).scale(big.NewRat(1, 4))},
	{"SW", -1, -1, q(1, 1).scale(big.NewRat(1, 4)).add(q(1, 0).scale(big.NewRat(1, 4)))},
	{"S", 0, -1, q(1, 1).scale(big.NewRat(1, 4))},
	{"SE", 1, -1, q(1, 1).scale(big.NewRat(1, 4)).add(q(1, 0).scale(big.NewRat(1, 4)))},
}

// The diagonal support simplifies to 1 + sqrt(2)/2; spelling it as above
// preserves the construction directly from the cardinal support.
func dotQ(f Face, v VecQ2) Q2 {
	return v.X.scale(big.NewRat(f.NX, 1)).add(v.Y.scale(big.NewRat(f.NY, 1)))
}
func dotR(f Face, v RatVec) *big.Rat {
	a := new(big.Rat).Mul(v.X, big.NewRat(f.NX, 1))
	return a.Add(a, new(big.Rat).Mul(v.Y, big.NewRat(f.NY, 1)))
}
func bound(f Face) Q2 { return f.Support.scale(big.NewRat(2, 1)) }
func inside(d VecQ2) bool {
	for _, f := range faces {
		if dotQ(f, d).cmp(bound(f)) > 0 {
			return false
		}
	}
	return true
}
func active(d VecQ2) []Face {
	out := []Face{}
	for _, f := range faces {
		if dotQ(f, d).eq(bound(f)) {
			out = append(out, f)
		}
	}
	return out
}

type P struct {
	ID, Site string
	Pos      VecQ2
	Vel      RatVec
}

func (p P) cp() P { return P{p.ID, p.Site, p.Pos, p.Vel.cp()} }

type State struct{ Ps []P }

func (s State) cp() State {
	out := State{Ps: make([]P, len(s.Ps))}
	for i, p := range s.Ps {
		out.Ps[i] = p.cp()
	}
	return out
}
func (s State) key() string {
	out := ""
	for _, p := range s.Ps {
		out += p.ID + ":" + p.Site + ":" + p.Pos.key() + ":" + p.Vel.key() + "|"
	}
	return out
}
func advance(s *State, t Q2) {
	for i := range s.Ps {
		s.Ps[i].Pos = s.Ps[i].Pos.addVel(s.Ps[i].Vel, t)
	}
}

type Kind string

const (
	pair Kind = "pair"
	wall Kind = "wall"
)

type Event struct {
	T      Q2
	K      Kind
	I, J   int
	F      Face
	Wall   string
	Corner bool
}

func (e Event) key(s State) string {
	if e.K == wall {
		return "wall:" + s.Ps[e.I].ID + ":" + e.Wall
	}
	if e.Corner {
		return "pair-corner:" + s.Ps[e.I].ID + ":" + s.Ps[e.J].ID
	}
	return "pair:" + s.Ps[e.I].ID + ":" + s.Ps[e.J].ID + ":" + e.F.Name
}

func pairCandidate(s State, i, j int) (Event, bool, error) {
	a, b := s.Ps[i], s.Ps[j]
	d := b.Pos.sub(a.Pos)
	rel := b.Vel.sub(a.Vel)
	var best *Q2
	var bestF Face
	for _, f := range faces {
		der := dotR(f, rel)
		if der.Sign() >= 0 {
			continue
		}
		gap := dotQ(f, d).sub(bound(f))
		if gap.sign() <= 0 {
			continue
		}
		t := gap.div(new(big.Rat).Neg(der))
		if t.sign() <= 0 {
			continue
		}
		loc := d.addVel(rel, t)
		if !inside(loc) || !dotQ(f, loc).eq(bound(f)) {
			continue
		}
		if best == nil || t.cmp(*best) < 0 {
			z := t
			best = &z
			bestF = f
		}
	}
	if best == nil {
		return Event{}, false, nil
	}
	af := active(d.addVel(rel, *best))
	if len(af) == 1 {
		return Event{T: *best, K: pair, I: i, J: j, F: bestF}, true, nil
	}
	if len(af) == 2 {
		return Event{T: *best, K: pair, I: i, J: j, F: bestF, Corner: true}, true, nil
	}
	return Event{}, false, fmt.Errorf("multi-face pair %s/%s", a.ID, b.ID)
}
func wallCandidates(s State, i int, box Q2) []Event {
	p := s.Ps[i]
	out := []Event{}
	add := func(f Face, w string, gap Q2, speed *big.Rat) {
		if speed.Sign() > 0 && gap.sign() > 0 {
			t := gap.div(speed)
			if t.sign() > 0 {
				out = append(out, Event{T: t, K: wall, I: i, F: f, Wall: w})
			}
		}
	}
	r := faces[0].Support
	neg := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	if p.Vel.X.Sign() > 0 {
		add(faces[0], "E", box.sub(p.Pos.X).sub(r), p.Vel.X)
	}
	if p.Vel.X.Sign() < 0 {
		add(faces[4], "W", p.Pos.X.sub(neg).sub(r), new(big.Rat).Neg(p.Vel.X))
	}
	if p.Vel.Y.Sign() > 0 {
		add(faces[2], "N", box.sub(p.Pos.Y).sub(r), p.Vel.Y)
	}
	if p.Vel.Y.Sign() < 0 {
		add(faces[6], "S", p.Pos.Y.sub(neg).sub(r), new(big.Rat).Neg(p.Vel.Y))
	}
	return out
}
func nextBatch(s State, box Q2) ([]Event, error) {
	es := []Event{}
	for i := range s.Ps {
		es = append(es, wallCandidates(s, i, box)...)
		for j := i + 1; j < len(s.Ps); j++ {
			e, ok, err := pairCandidate(s, i, j)
			if err != nil {
				return nil, err
			}
			if ok {
				es = append(es, e)
			}
		}
	}
	if len(es) == 0 {
		return nil, nil
	}
	sort.Slice(es, func(i, j int) bool { return es[i].T.cmp(es[j].T) < 0 })
	min := es[0].T
	batch := []Event{}
	for _, e := range es {
		if e.T.eq(min) {
			batch = append(batch, e)
		}
	}
	// A pair-corner event has no declared continuation.  It takes priority
	// over any simultaneous-batch bookkeeping so callers can record the
	// terminal UNKNOWN_CORNER event rather than manufacture an ordering.
	for _, e := range batch {
		if e.K == pair && e.Corner {
			return batch, nil
		}
	}
	use := map[int][]Event{}
	for _, e := range batch {
		use[e.I] = append(use[e.I], e)
		if e.K == pair {
			use[e.J] = append(use[e.J], e)
		}
	}
	for body, hits := range use {
		pairs, walls := 0, 0
		wf := []Face{}
		for _, e := range hits {
			if e.K == pair {
				pairs++
			} else {
				walls++
				wf = append(wf, e.F)
			}
		}
		if pairs > 0 && len(hits) > 1 {
			return nil, fmt.Errorf("shared-body batch body %s", s.Ps[body].ID)
		}
		if walls > 2 {
			return nil, fmt.Errorf("three-wall batch body %s", s.Ps[body].ID)
		}
		if walls == 2 && wf[0].NX*wf[1].NX+wf[0].NY*wf[1].NY != 0 {
			return nil, fmt.Errorf("nonperpendicular double wall body %s", s.Ps[body].ID)
		}
	}
	return batch, nil
}

// activeConstraints returns every zero-gap exclusion constraint at the
// current exact state, regardless of whether its current velocity is inward,
// tangent, or outward.  This is deliberately broader than nextBatch: a
// tangent wall or pair can be part of the same event component as a scheduled
// impact even though it does not itself have a positive-gap event time.
func activeConstraints(s State, box Q2) ([]Event, error) {
	out := []Event{}
	r := faces[0].Support
	neg := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	for i, p := range s.Ps {
		if p.Pos.X.add(r).eq(box) {
			out = append(out, Event{K: wall, I: i, F: faces[0], Wall: "E"})
		}
		if p.Pos.X.sub(r).eq(neg) {
			out = append(out, Event{K: wall, I: i, F: faces[4], Wall: "W"})
		}
		if p.Pos.Y.add(r).eq(box) {
			out = append(out, Event{K: wall, I: i, F: faces[2], Wall: "N"})
		}
		if p.Pos.Y.sub(r).eq(neg) {
			out = append(out, Event{K: wall, I: i, F: faces[6], Wall: "S"})
		}
	}
	for i := range s.Ps {
		for j := i + 1; j < len(s.Ps); j++ {
			d := s.Ps[j].Pos.sub(s.Ps[i].Pos)
			if !inside(d) {
				continue
			}
			af := active(d)
			if len(af) == 0 {
				return nil, fmt.Errorf("overlap %s/%s", s.Ps[i].ID, s.Ps[j].ID)
			}
			if len(af) > 2 {
				return nil, fmt.Errorf("multi-face active pair %s/%s", s.Ps[i].ID, s.Ps[j].ID)
			}
			out = append(out, Event{K: pair, I: i, J: j, F: af[0], Corner: len(af) == 2})
		}
	}
	return out, nil
}

// checkActiveComponents enforces the event-boundary contract before any
// impulse is applied.  A scheduled impact may be accompanied by a wall or
// pair contact that was already zero-gap and tangential; serializing those
// constraints would manufacture a trajectory.  Hence a pair sharing its
// body with any other active constraint is a terminal shared-body component.
// Perpendicular double-wall reflections remain the only declared compound
// wall operation.
func checkActiveComponents(s State, box Q2) error {
	cs, err := activeConstraints(s, box)
	if err != nil {
		return err
	}
	for _, c := range cs {
		if c.K == pair && c.Corner {
			return fmt.Errorf("unknown active pair-corner contact %s/%s", s.Ps[c.I].ID, s.Ps[c.J].ID)
		}
	}
	use := map[int][]Event{}
	for _, c := range cs {
		use[c.I] = append(use[c.I], c)
		if c.K == pair {
			use[c.J] = append(use[c.J], c)
		}
	}
	for body, hits := range use {
		pairs, walls := 0, 0
		wf := []Face{}
		for _, c := range hits {
			if c.K == pair {
				pairs++
			} else {
				walls++
				wf = append(wf, c.F)
			}
		}
		if pairs > 0 && len(hits) > 1 {
			return fmt.Errorf("same-time shared-body active component body %s", s.Ps[body].ID)
		}
		if walls > 2 {
			return fmt.Errorf("three-wall active component body %s", s.Ps[body].ID)
		}
		if walls == 2 && wf[0].NX*wf[1].NX+wf[0].NY*wf[1].NY != 0 {
			return fmt.Errorf("nonperpendicular double-wall active component body %s", s.Ps[body].ID)
		}
	}
	return nil
}

func resolvePair(s *State, e Event) {
	a, b := &s.Ps[e.I], &s.Ps[e.J]
	if e.Corner {
		a.Vel, b.Vel = b.Vel.cp(), a.Vel.cp()
		return
	}
	n2 := e.F.NX*e.F.NX + e.F.NY*e.F.NY
	g := dotR(e.F, b.Vel.sub(a.Vel))
	c := new(big.Rat).Quo(g, big.NewRat(n2, 1))
	a.Vel.X.Add(a.Vel.X, new(big.Rat).Mul(c, big.NewRat(e.F.NX, 1)))
	a.Vel.Y.Add(a.Vel.Y, new(big.Rat).Mul(c, big.NewRat(e.F.NY, 1)))
	b.Vel.X.Sub(b.Vel.X, new(big.Rat).Mul(c, big.NewRat(e.F.NX, 1)))
	b.Vel.Y.Sub(b.Vel.Y, new(big.Rat).Mul(c, big.NewRat(e.F.NY, 1)))
}
func resolveBatch(s *State, b []Event) {
	for _, e := range b {
		if e.K == pair {
			resolvePair(s, e)
		}
	}
	for _, e := range b {
		if e.K == wall {
			p := &s.Ps[e.I]
			if e.F.NX != 0 {
				p.Vel.X.Neg(p.Vel.X)
			}
			if e.F.NY != 0 {
				p.Vel.Y.Neg(p.Vel.Y)
			}
		}
	}
}

// validPost is the exact state contract after a positive-time batch. All
// active exclusion faces must be separating or tangent, not merely the first.
func validPost(s State, box Q2) error {
	r := faces[0].Support
	neg := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	for _, p := range s.Ps {
		if p.Pos.X.sub(r).cmp(neg) < 0 || p.Pos.X.add(r).cmp(box) > 0 || p.Pos.Y.sub(r).cmp(neg) < 0 || p.Pos.Y.add(r).cmp(box) > 0 {
			return fmt.Errorf("wall escape %s", p.ID)
		}
		// A state exactly on a wall must already be post-reflection. Leaving
		// an outward component here would make the next positive-time search
		// miss a zero-time wall event and manufacture an escape.
		if p.Pos.X.add(r).eq(box) && p.Vel.X.Sign() > 0 {
			return fmt.Errorf("outward E wall contact %s", p.ID)
		}
		if p.Pos.X.sub(r).eq(neg) && p.Vel.X.Sign() < 0 {
			return fmt.Errorf("outward W wall contact %s", p.ID)
		}
		if p.Pos.Y.add(r).eq(box) && p.Vel.Y.Sign() > 0 {
			return fmt.Errorf("outward N wall contact %s", p.ID)
		}
		if p.Pos.Y.sub(r).eq(neg) && p.Vel.Y.Sign() < 0 {
			return fmt.Errorf("outward S wall contact %s", p.ID)
		}
	}
	for i := range s.Ps {
		for j := i + 1; j < len(s.Ps); j++ {
			d := s.Ps[j].Pos.sub(s.Ps[i].Pos)
			if inside(d) {
				af := active(d)
				if len(af) == 0 {
					return fmt.Errorf("overlap %s/%s", s.Ps[i].ID, s.Ps[j].ID)
				}
				for _, f := range af {
					if dotR(f, s.Ps[j].Vel.sub(s.Ps[i].Vel)).Sign() < 0 {
						return fmt.Errorf("approaching contact %s/%s at %s", s.Ps[i].ID, s.Ps[j].ID, f.Name)
					}
				}
			}
		}
	}
	return nil
}

// The user-specified raw directions are post-contact directions. A start
// already on a wall must therefore be inward or tangent; outward starts are
// rejected rather than silently repaired by a zero-time bounce.
func validInitial(s State, box Q2) error {
	r := faces[0].Support
	neg := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	for _, p := range s.Ps {
		if p.Pos.X.add(r).eq(box) && p.Vel.X.Sign() > 0 {
			return fmt.Errorf("initial outward E wall %s", p.ID)
		}
		if p.Pos.X.sub(r).eq(neg) && p.Vel.X.Sign() < 0 {
			return fmt.Errorf("initial outward W wall %s", p.ID)
		}
		if p.Pos.Y.add(r).eq(box) && p.Vel.Y.Sign() > 0 {
			return fmt.Errorf("initial outward N wall %s", p.ID)
		}
		if p.Pos.Y.sub(r).eq(neg) && p.Vel.Y.Sign() < 0 {
			return fmt.Errorf("initial outward S wall %s", p.ID)
		}
	}
	return validPost(s, box)
}

func ratBits(r *big.Rat) int {
	a := r.Num().BitLen()
	b := r.Denom().BitLen()
	if b > a {
		return b
	}
	return a
}
func q2Bits(x Q2) int {
	a := ratBits(x.A)
	b := ratBits(x.B)
	if b > a {
		return b
	}
	return a
}

type StateMetrics struct{ PositionBits, VelocityBits, StateBits int }

func stateMetrics(s State) StateMetrics {
	m := StateMetrics{}
	for _, p := range s.Ps {
		for _, x := range []Q2{p.Pos.X, p.Pos.Y} {
			if z := q2Bits(x); z > m.PositionBits {
				m.PositionBits = z
			}
		}
		for _, r := range []*big.Rat{p.Vel.X, p.Vel.Y} {
			if z := ratBits(r); z > m.VelocityBits {
				m.VelocityBits = z
			}
		}
	}
	m.StateBits = m.PositionBits
	if m.VelocityBits > m.StateBits {
		m.StateBits = m.VelocityBits
	}
	return m
}

func stateBits(s State) int { return stateMetrics(s).StateBits }

// L=4, N=3 search.  Coordinates use the exact centered half-pitch atlas:
// coordinate z means z*D/2, where D=2+sqrt(2).  The L=4 finite 4.8.8
// container has A[0..3,0..3] at odd z coordinates and B[0..2,0..2] at
// even z coordinates.  This is the SW-indexed atlas used in the clock plots.
type Site struct {
	Label string
	U, V  int
	X, Y  Q2
}

type RawParticle struct {
	U, V   int
	VX, VY int
}
type RawStart []RawParticle

type Mat struct{ A, B, C, D int }

var d4 = []Mat{
	{1, 0, 0, 1}, {0, -1, 1, 0}, {-1, 0, 0, -1}, {0, 1, -1, 0},
	{-1, 0, 0, 1}, {1, 0, 0, -1}, {0, 1, 1, 0}, {0, -1, -1, 0},
}

func apply(m Mat, x, y int) (int, int) { return m.A*x + m.B*y, m.C*x + m.D*y }
func lessRawParticle(a, b RawParticle) bool {
	if a.U != b.U {
		return a.U < b.U
	}
	if a.V != b.V {
		return a.V < b.V
	}
	if a.VX != b.VX {
		return a.VX < b.VX
	}
	return a.VY < b.VY
}
func orderRaw(s RawStart) RawStart {
	for i := 0; i < len(s); i++ {
		for j := i + 1; j < len(s); j++ {
			if lessRawParticle(s[j], s[i]) {
				s[i], s[j] = s[j], s[i]
			}
		}
	}
	return s
}
func rawKey(s RawStart) string {
	s = orderRaw(s)
	out := ""
	for i, p := range s {
		if i > 0 {
			out += "|"
		}
		out += fmt.Sprintf("%+d,%+d:%+d,%+d", p.U, p.V, p.VX, p.VY)
	}
	return out
}
func transformRaw(s RawStart, m Mat) RawStart {
	// Do not mutate the caller's trial state: canonicalization applies all
	// D4 elements to the same raw start and must therefore be pure.
	out := make(RawStart, len(s))
	for i, p := range s {
		out[i] = p
		out[i].U, out[i].V = apply(m, p.U, p.V)
		out[i].VX, out[i].VY = apply(m, p.VX, p.VY)
	}
	return orderRaw(out)
}
func canonicalRaw(s RawStart) (RawStart, string) {
	best := transformRaw(s, d4[0])
	bestK := rawKey(best)
	for _, m := range d4[1:] {
		z := transformRaw(s, m)
		if k := rawKey(z); k < bestK {
			best, bestK = z, k
		}
	}
	return best, bestK
}
func orbitSize(s RawStart) int {
	set := map[string]bool{}
	for _, m := range d4 {
		set[rawKey(transformRaw(s, m))] = true
	}
	return len(set)
}
func velocityLabel(vx, vy int) string {
	switch {
	case vx == 1 && vy == 0:
		return "+x"
	case vx == -1 && vy == 0:
		return "-x"
	case vx == 0 && vy == 1:
		return "+y"
	case vx == 0 && vy == -1:
		return "-y"
	}
	return fmt.Sprintf("(%d,%d)", vx, vy)
}

var activeAtlasL int

// siteFromUV retains the exact centered half-pitch atlas used by the original
// search.  For a general L patch, the outer chart has the parity of L-1 and
// the inner chart has the opposite parity.  Coordinate z means z*(2+sqrt(2))/2.
func siteFromUV(u, v int) Site {
	qcoord := func(z int) Q2 { return Q2{big.NewRat(int64(z), 1), big.NewRat(int64(z), 2)} }
	kind := "A"
	if ((u-(activeAtlasL-1))&1) != 0 || ((v-(activeAtlasL-1))&1) != 0 {
		kind = "B"
	}
	return Site{fmt.Sprintf("%s[%+d,%+d]", kind, u, v), u, v, qcoord(u), qcoord(v)}
}

func lSites(L int) []Site {
	activeAtlasL = L
	out := []Site{}
	outer := L - 1
	for u := -outer; u <= outer; u += 2 {
		for v := -outer; v <= outer; v += 2 {
			out = append(out, siteFromUV(u, v))
		}
	}
	inner := L - 2
	for u := -inner; u <= inner; u += 2 {
		for v := -inner; v <= inner; v += 2 {
			out = append(out, siteFromUV(u, v))
		}
	}
	sort.Slice(out, func(i, j int) bool {
		if out[i].U != out[j].U {
			return out[i].U < out[j].U
		}
		return out[i].V < out[j].V
	})
	return out
}

func halfEdgeBox(L int) Q2 {
	// Background unit-edge L-by-L 4.8.8 square patch: H=L-1/2+(L/2)sqrt(2).
	return Q2{big.NewRat(int64(2*L-1), 2), big.NewRat(int64(L), 2)}
}

// cleanPlacement excludes every initial body-body tangency or overlap.
func cleanPlacement(ss ...Site) bool {
	for i := range ss {
		for j := i + 1; j < len(ss); j++ {
			d := VecQ2{ss[j].X.sub(ss[i].X), ss[j].Y.sub(ss[i].Y)}
			if inside(d) {
				return false
			}
		}
	}
	return true
}

// cleanRawStart also rejects an outward raw velocity at a wall-tangent site.
// This keeps every enumerated start genuinely post-contact and avoids using a
// zero-time wall bounce as an arbitrary phase convention.
func cleanRawStart(raw RawStart, box Q2) bool {
	r := faces[0].Support
	neg := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	for _, rp := range raw {
		si := siteFromUV(rp.U, rp.V)
		if si.X.add(r).eq(box) && rp.VX > 0 {
			return false
		}
		if si.X.sub(r).eq(neg) && rp.VX < 0 {
			return false
		}
		if si.Y.add(r).eq(box) && rp.VY > 0 {
			return false
		}
		if si.Y.sub(r).eq(neg) && rp.VY < 0 {
			return false
		}
	}
	return true
}

func rawWire(s RawStart) []string {
	s = orderRaw(s)
	out := make([]string, len(s))
	for i, p := range s {
		out[i] = fmt.Sprintf("%s %s", siteFromUV(p.U, p.V).Label, velocityLabel(p.VX, p.VY))
	}
	return out
}

type EventWire struct {
	Batch  int      `json:"batch"`
	Time   Q2Wire   `json:"time"`
	Events []string `json:"events"`
}
type Trial struct {
	Class              int         `json:"class"`
	OrbitSize          int         `json:"orbit_size"`
	RawRepresentative  []string    `json:"raw_representative"`
	PostContactStart   []string    `json:"post_contact_start"`
	ZeroTimeEvents     []string    `json:"zero_time_events,omitempty"`
	Status             string      `json:"status"`
	Detail             string      `json:"detail,omitempty"`
	ReturnKind         string      `json:"return_kind,omitempty"`
	Batches            int         `json:"batches"`
	Time               Q2Wire      `json:"time"`
	MaxStateBits       int         `json:"max_state_bits"`
	MaxPositionBits    int         `json:"max_position_bits"`
	MaxVelocityBits    int         `json:"max_velocity_bits"`
	PreperiodBatches   int         `json:"preperiod_batches,omitempty"`
	PreperiodTime      *Q2Wire     `json:"preperiod_time,omitempty"`
	PeriodBatches      int         `json:"period_batches,omitempty"`
	PeriodTime         *Q2Wire     `json:"period_time,omitempty"`
	FirstBatches       []EventWire `json:"first_batches,omitempty"`
	PositiveWallEvents int         `json:"positive_wall_events"`
	PositivePairEvents int         `json:"positive_pair_events"`
	PositivePairEdges  []string    `json:"positive_pair_edges,omitempty"`
}
type Summary struct {
	Status      string `json:"status"`
	Classes     int    `json:"classes"`
	RawInitials int    `json:"raw_initials"`
}
type Report struct {
	Schema               string         `json:"schema"`
	Purpose              string         `json:"purpose"`
	Arithmetic           string         `json:"arithmetic"`
	ContainerSide        string         `json:"container_side_exact"`
	HalfBox              Q2Wire         `json:"half_box"`
	SiteCount            int            `json:"site_count"`
	CleanPlacements      int            `json:"clean_placements"`
	CleanRawInitials     int            `json:"clean_raw_initials"`
	UnreducedRawInitials int            `json:"unreduced_raw_initials"`
	PlacementPairs       int            `json:"placement_triples"`
	VelocitiesPerPair    int            `json:"velocities_per_pair"`
	D4InitialClasses     int            `json:"d4_initial_classes"`
	D4OrbitSizeHistogram map[string]int `json:"d4_orbit_size_histogram"`
	ZeroTimeContract     string         `json:"zero_time_contract"`
	MaxBatches           int            `json:"max_batches"`
	MaxQ2Bits            int            `json:"max_position_bits"`
	ScanOrder            string         `json:"scan_order"`
	StopAfterFirstCutoff bool           `json:"stop_after_first_coordinate_cutoff"`
	TriageBatches        int            `json:"triage_batches"`
	ScannedClasses       int            `json:"scanned_classes"`
	EligibleClasses      int            `json:"eligible_classes"`
	DeepTrials           int            `json:"deep_trials"`
	Results              []Trial        `json:"deep_trial_results"`
	Summary              []Summary      `json:"triage_summary"`
}
type Seen struct {
	Batch int
	Time  Q2
}

func stateUnlabelledKey(s State) string {
	z := []string{}
	for _, p := range s.Ps {
		z = append(z, p.Pos.key()+":"+p.Vel.key())
	}
	sort.Strings(z)
	return strings.Join(z, "|")
}
func rawFromStateAtInitial(s State) (RawStart, bool) {
	out := make(RawStart, len(s.Ps))
	for i, p := range s.Ps {
		u, v := p.Pos.X, p.Pos.Y
		// Pointers/rationals must match D*(integer/2), so a=u and b=u/2.
		if u.A.Denom().Cmp(big.NewInt(1)) != 0 || v.A.Denom().Cmp(big.NewInt(1)) != 0 {
			return out, false
		}
		ux := int(u.A.Num().Int64())
		uy := int(v.A.Num().Int64())
		wantX := big.NewRat(int64(ux), 2)
		wantY := big.NewRat(int64(uy), 2)
		if u.B.Cmp(wantX) != 0 || v.B.Cmp(wantY) != 0 {
			return out, false
		}
		if p.Vel.X.Denom().Cmp(big.NewInt(1)) != 0 || p.Vel.Y.Denom().Cmp(big.NewInt(1)) != 0 {
			return out, false
		}
		out[i] = RawParticle{ux, uy, int(p.Vel.X.Num().Int64()), int(p.Vel.Y.Num().Int64())}
		if (abs(out[i].VX) + abs(out[i].VY)) != 1 {
			return out, false
		}
	}
	return orderRaw(out), true
}
func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}

// normalizeZeroTime makes the t=0 contact convention explicit.  It closes
// any raw outward wall direction by specular reflection, then resolves only
// unambiguous one-face initial pair contacts.  Any incoming pair-corner hit
// is terminal UNKNOWN_CORNER; no corner impulse is invented.
//
// protected contains every body already participating at this timestamp.
// Start it empty for an initial state; after a positive-time batch, seed it
// with every body in that batch.  Every zero-time wall reflection and pair
// resolution adds its own bodies.  An active contact made incoming afterward
// is part of the same simultaneous component, not a second serial collision.
// We have no joint rule for that component, so it is an exact shared-body
// rejection.
func normalizeZeroTime(s *State, box Q2, protected map[int]bool) ([]string, error) {
	if protected == nil {
		protected = map[int]bool{}
	}
	trace := []string{}
	r := faces[0].Support
	neg := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	for pass := 0; pass < 32; pass++ {
		changed := false
		// Deterministic closure convention: specularly reflect every active
		// outward wall component, then resolve the remaining disjoint incoming
		// pair contacts. Repeat until no zero-time continuation remains.
		for i := range s.Ps {
			p := &s.Ps[i]
			if p.Pos.X.add(r).eq(box) && p.Vel.X.Sign() > 0 {
				p.Vel.X.Neg(p.Vel.X)
				protected[i] = true
				trace = append(trace, "0 wall:"+p.ID+":E")
				changed = true
			}
			if p.Pos.X.sub(r).eq(neg) && p.Vel.X.Sign() < 0 {
				p.Vel.X.Neg(p.Vel.X)
				protected[i] = true
				trace = append(trace, "0 wall:"+p.ID+":W")
				changed = true
			}
			if p.Pos.Y.add(r).eq(box) && p.Vel.Y.Sign() > 0 {
				p.Vel.Y.Neg(p.Vel.Y)
				protected[i] = true
				trace = append(trace, "0 wall:"+p.ID+":N")
				changed = true
			}
			if p.Pos.Y.sub(r).eq(neg) && p.Vel.Y.Sign() < 0 {
				p.Vel.Y.Neg(p.Vel.Y)
				protected[i] = true
				trace = append(trace, "0 wall:"+p.ID+":S")
				changed = true
			}
		}
		pairs := []Event{}
		use := map[int]int{}
		for i := range s.Ps {
			for j := i + 1; j < len(s.Ps); j++ {
				d := s.Ps[j].Pos.sub(s.Ps[i].Pos)
				if !inside(d) {
					continue
				}
				af := active(d)
				if len(af) == 0 {
					return trace, fmt.Errorf("overlap %s/%s", s.Ps[i].ID, s.Ps[j].ID)
				}
				incoming := []Face{}
				for _, f := range af {
					if dotR(f, s.Ps[j].Vel.sub(s.Ps[i].Vel)).Sign() < 0 {
						incoming = append(incoming, f)
					}
				}
				if len(incoming) > 1 {
					return trace, fmt.Errorf("unknown zero-time corner collision %s/%s", s.Ps[i].ID, s.Ps[j].ID)
				}
				if len(incoming) == 1 {
					if len(af) == 2 {
						return trace, fmt.Errorf("unknown zero-time corner collision %s/%s", s.Ps[i].ID, s.Ps[j].ID)
					}
					if protected != nil && (protected[i] || protected[j]) {
						return trace, fmt.Errorf("same-time shared-body contact %s/%s", s.Ps[i].ID, s.Ps[j].ID)
					}
					pairs = append(pairs, Event{K: pair, I: i, J: j, F: incoming[0]})
					use[i]++
					use[j]++
				}
			}
		}
		for i, n := range use {
			if n > 1 {
				return trace, fmt.Errorf("zero-time shared-body pair batch %s", s.Ps[i].ID)
			}
		}
		for _, e := range pairs {
			resolvePair(s, e)
			protected[e.I] = true
			protected[e.J] = true
			trace = append(trace, "0 pair:"+s.Ps[e.I].ID+":"+s.Ps[e.J].ID+":"+e.F.Name)
			changed = true
		}
		if !changed {
			return trace, validPost(*s, box)
		}
	}
	return trace, fmt.Errorf("zero-time closure did not stabilize in 32 passes")
}

func statusForError(err error) string {
	if strings.Contains(err.Error(), "corner") {
		return "UNKNOWN_CORNER"
	}
	return "REJECT"
}

func searchTrial(class, oSize int, raw RawStart, box Q2, maxPositionBits int, watchBatches int) Trial {
	raw = orderRaw(raw)
	ps := make([]P, len(raw))
	for i, rp := range raw {
		si := siteFromUV(rp.U, rp.V)
		ps[i] = P{fmt.Sprintf("P%d", i), si.Label, VecQ2{si.X, si.Y}, rv(int64(rp.VX), int64(rp.VY))}
	}
	s := State{Ps: ps}
	m0 := stateMetrics(s)
	out := Trial{Class: class, OrbitSize: oSize, RawRepresentative: rawWire(raw), Status: "RUNNING", Time: q(0, 0).wire(), MaxStateBits: m0.StateBits, MaxPositionBits: m0.PositionBits, MaxVelocityBits: m0.VelocityBits}
	if err := checkActiveComponents(s, box); err != nil {
		out.Status = statusForError(err)
		out.Detail = "exact initial active-component violation: " + err.Error()
		return out
	}
	trace, err := normalizeZeroTime(&s, box, map[int]bool{})
	out.ZeroTimeEvents = trace
	if post, ok := rawFromStateAtInitial(s); ok {
		out.PostContactStart = rawWire(post)
	} else {
		out.PostContactStart = []string{"non-cardinal or non-atlas post-contact state"}
	}
	if err != nil {
		out.Status = statusForError(err)
		out.Detail = "exact zero-time rule violation: " + err.Error()
		return out
	}
	if m := stateMetrics(s); m.StateBits > out.MaxStateBits || m.PositionBits > out.MaxPositionBits || m.VelocityBits > out.MaxVelocityBits {
		if m.StateBits > out.MaxStateBits {
			out.MaxStateBits = m.StateBits
		}
		if m.PositionBits > out.MaxPositionBits {
			out.MaxPositionBits = m.PositionBits
		}
		if m.VelocityBits > out.MaxVelocityBits {
			out.MaxVelocityBits = m.VelocityBits
		}
	}
	now := q(0, 0)
	seenL := map[string]Seen{stateUnlabelledKey(s): {0, now}}
	pairEdges := map[string]bool{}
	finalizeEdges := func() {
		keys := make([]string, 0, len(pairEdges))
		for k := range pairEdges {
			keys = append(keys, k)
		}
		sort.Strings(keys)
		out.PositivePairEdges = keys
	}
	for batchNo := 1; ; batchNo++ {
		batch, err := nextBatch(s, box)
		if err != nil {
			out.Batches = batchNo - 1
			out.Time = now.wire()
			out.Status = "REJECT"
			out.Detail = "exact batch-rule violation: " + err.Error()
			return out
		}
		if len(batch) == 0 {
			out.Status = "REJECT"
			out.Detail = "exact batch-rule violation: no future event"
			out.Batches = batchNo - 1
			out.Time = now.wire()
			return out
		}
		dt := batch[0].T
		// No pair-corner impact law is declared.  Record the exact first hit and
		// terminate before any impulse or state update is manufactured.
		for _, e := range batch {
			if e.K == pair && e.Corner {
				names := make([]string, len(batch))
				for k, ev := range batch {
					names[k] = ev.key(s)
				}
				sort.Strings(names)
				if len(out.FirstBatches) < 8 {
					out.FirstBatches = append(out.FirstBatches, EventWire{batchNo, now.add(dt).wire(), names})
				}
				out.Status = "UNKNOWN_CORNER"
				out.Detail = "exact pair-corner hit; no declared continuation"
				out.Batches = batchNo
				out.Time = now.add(dt).wire()
				return out
			}
		}
		advance(&s, dt)
		now = now.add(dt)
		// Before any impulse, inspect the complete zero-gap constraint graph.
		// This catches both directions of the old serialization bug: a wall
		// reflection activating a tangent pair, and a tangent wall made outward
		// by a pending pair impulse.
		if err := checkActiveComponents(s, box); err != nil {
			out.Status = statusForError(err)
			out.Detail = "exact pre-resolution active-component violation: " + err.Error()
			out.Batches = batchNo
			out.Time = now.wire()
			return out
		}
		for _, e := range batch {
			if e.K == wall {
				out.PositiveWallEvents++
			} else {
				out.PositivePairEvents++
				a, b := s.Ps[e.I].ID, s.Ps[e.J].ID
				if a > b {
					a, b = b, a
				}
				pairEdges[a+"/"+b] = true
			}
		}
		finalizeEdges()
		resolveBatch(&s, batch)
		names := make([]string, len(batch))
		for i, e := range batch {
			names[i] = e.key(s)
		}
		sort.Strings(names)
		if len(out.FirstBatches) < 8 {
			out.FirstBatches = append(out.FirstBatches, EventWire{batchNo, now.wire(), names})
		}
		if err := validPost(s, box); err != nil {
			out.Status = "REJECT"
			out.Detail = "exact joint-contact rule violation after batch: " + err.Error()
			out.Batches = batchNo
			out.Time = now.wire()
			return out
		}
		if m := stateMetrics(s); m.StateBits > out.MaxStateBits || m.PositionBits > out.MaxPositionBits || m.VelocityBits > out.MaxVelocityBits {
			if m.StateBits > out.MaxStateBits {
				out.MaxStateBits = m.StateBits
			}
			if m.PositionBits > out.MaxPositionBits {
				out.MaxPositionBits = m.PositionBits
			}
			if m.VelocityBits > out.MaxVelocityBits {
				out.MaxVelocityBits = m.VelocityBits
			}
		}
		if out.MaxStateBits > maxPositionBits {
			out.Status = "COMPLEXITY_CUTOFF"
			out.Detail = fmt.Sprintf("full-state coefficient bit length %d exceeds cap %d (position=%d, velocity=%d)", out.MaxStateBits, maxPositionBits, out.MaxPositionBits, out.MaxVelocityBits)
			out.Batches = batchNo
			out.Time = now.wire()
			return out
		}
		if prev, ok := seenL[stateUnlabelledKey(s)]; ok {
			out.Status = "RETURN"
			out.ReturnKind = "unlabelled"
			out.Batches = batchNo
			out.Time = now.wire()
			out.PreperiodBatches = prev.Batch
			w := prev.Time.wire()
			out.PreperiodTime = &w
			out.PeriodBatches = batchNo - prev.Batch
			pt := now.sub(prev.Time).wire()
			out.PeriodTime = &pt
			out.Detail = "exact unlabelled event-endpoint recurrence"
			return out
		}

		seenL[stateUnlabelledKey(s)] = Seen{batchNo, now}
		if watchBatches > 0 && batchNo >= watchBatches {
			out.Status = "LOW_COMPLEXITY_WATCH"
			out.Detail = fmt.Sprintf("still valid, unlabelled-nonrepeating, and at or below full-state cap %d after exact observation checkpoint of %d batches (position=%d, velocity=%d)", maxPositionBits, watchBatches, out.MaxPositionBits, out.MaxVelocityBits)
			out.Batches = batchNo
			out.Time = now.wire()
			return out
		}
	}
	panic("unreachable")
}

// Portable L=4,N=3 certificate emitter for class 1489.
type CertBodyWire struct {
	ID       string `json:"id"`
	Position struct {
		X Q2Wire `json:"x"`
		Y Q2Wire `json:"y"`
	} `json:"position"`
	Velocity struct {
		VX string `json:"vx"`
		VY string `json:"vy"`
	} `json:"velocity"`
}
type LedgerWire struct {
	Index      int            `json:"index"`
	Time       Q2Wire         `json:"time"`
	Events     []string       `json:"events"`
	Pre        []CertBodyWire `json:"pre"`
	Post       []CertBodyWire `json:"post"`
	Complexity struct {
		Pre  int `json:"pre_state_bits"`
		Post int `json:"post_state_bits"`
	} `json:"complexity"`
}
type Certificate struct {
	Schema                   string `json:"schema"`
	CertificateID            string `json:"certificate_id"`
	Model                    any    `json:"model"`
	Instance                 any    `json:"instance"`
	Evolution                any    `json:"evolution"`
	IndependentCheckContract any    `json:"independent_check_contract"`
}

func bodyWire(s State) []CertBodyWire {
	out := make([]CertBodyWire, len(s.Ps))
	for i, p := range s.Ps {
		out[i].ID = p.ID
		out[i].Position.X = p.Pos.X.wire()
		out[i].Position.Y = p.Pos.Y.wire()
		out[i].Velocity.VX = p.Vel.X.RatString()
		out[i].Velocity.VY = p.Vel.Y.RatString()
	}
	return out
}
func stateKeyHash(s State) string {
	h := sha256.Sum256([]byte(s.key()))
	return fmt.Sprintf("%x", h[:])
}

type SeedSpec struct {
	Class int
	Raw   []string
	Ps    []P
}

func ratstr(s string) *big.Rat {
	r, ok := new(big.Rat).SetString(s)
	if !ok {
		panic("bad rational: " + s)
	}
	return r
}
func qstr(a, b string) Q2 { return Q2{ratstr(a), ratstr(b)} }

var seedSpecs = map[int]SeedSpec{
	1643: {Class: 1643, Raw: []string{"B[1,2] -x", "B[2,0] -y", "B[2,2] +y"}, Ps: []P{{ID: "P0", Site: "B[1,2]", Pos: VecQ2{qstr("0", "0"), qstr("2", "1")}, Vel: rv(-1, 0)}, {ID: "P1", Site: "B[2,0]", Pos: VecQ2{qstr("2", "1"), qstr("-2", "-1")}, Vel: rv(0, -1)}, {ID: "P2", Site: "B[2,2]", Pos: VecQ2{qstr("2", "1"), qstr("2", "1")}, Vel: rv(0, 1)}}},
	1489: {Class: 1489, Raw: []string{"B[1,2] -x", "A[2,1] -y", "B[2,2] +x"}, Ps: []P{{ID: "P0", Site: "B[1,2]", Pos: VecQ2{qstr("0", "0"), qstr("2", "1")}, Vel: rv(-1, 0)}, {ID: "P1", Site: "A[2,1]", Pos: VecQ2{qstr("1", "1/2"), qstr("-1", "-1/2")}, Vel: rv(0, -1)}, {ID: "P2", Site: "B[2,2]", Pos: VecQ2{qstr("2", "1"), qstr("2", "1")}, Vel: rv(1, 0)}}},
	2142: {Class: 2142, Raw: []string{"A[2,2] +x", "B[2,0] +y", "A[3,2] -x"}, Ps: []P{{ID: "P0", Site: "A[2,2]", Pos: VecQ2{qstr("1", "1/2"), qstr("1", "1/2")}, Vel: rv(1, 0)}, {ID: "P1", Site: "B[2,0]", Pos: VecQ2{qstr("2", "1"), qstr("-2", "-1")}, Vel: rv(0, 1)}, {ID: "P2", Site: "A[3,2]", Pos: VecQ2{qstr("3", "3/2"), qstr("1", "1/2")}, Vel: rv(-1, 0)}}},
	1529: {Class: 1529, Raw: []string{"B[1,2] -x", "A[2,0] +y", "A[2,1] +y"}, Ps: []P{{ID: "P0", Site: "B[1,2]", Pos: VecQ2{qstr("0", "0"), qstr("2", "1")}, Vel: rv(-1, 0)}, {ID: "P1", Site: "A[2,0]", Pos: VecQ2{qstr("1", "1/2"), qstr("-3", "-3/2")}, Vel: rv(0, 1)}, {ID: "P2", Site: "A[2,1]", Pos: VecQ2{qstr("1", "1/2"), qstr("-1", "-1/2")}, Vel: rv(0, 1)}}},
	5722: {Class: 5722, Raw: []string{"A[1,0] +y", "A[1,3] -y", "B[2,2] +x"}, Ps: []P{{ID: "P0", Site: "A[1,0]", Pos: VecQ2{qstr("-1", "-1/2"), qstr("-3", "-3/2")}, Vel: rv(0, 1)}, {ID: "P1", Site: "A[1,3]", Pos: VecQ2{qstr("-1", "-1/2"), qstr("3", "3/2")}, Vel: rv(0, -1)}, {ID: "P2", Site: "B[2,2]", Pos: VecQ2{qstr("2", "1"), qstr("2", "1")}, Vel: rv(1, 0)}}},
	2925: {Class: 2925, Raw: []string{"B[2,0] +y", "B[2,1] -y", "B[2,2] -x"}, Ps: []P{{ID: "P0", Site: "B[2,0]", Pos: VecQ2{qstr("2", "1"), qstr("-2", "-1")}, Vel: rv(0, 1)}, {ID: "P1", Site: "B[2,1]", Pos: VecQ2{qstr("2", "1"), qstr("0", "0")}, Vel: rv(0, -1)}, {ID: "P2", Site: "B[2,2]", Pos: VecQ2{qstr("2", "1"), qstr("2", "1")}, Vel: rv(-1, 0)}}},
	1241: {Class: 1241, Raw: []string{"B[1,2] +x", "A[2,1] -y", "B[2,2] +x"}, Ps: []P{{ID: "P0", Site: "B[1,2]", Pos: VecQ2{qstr("0", "0"), qstr("2", "1")}, Vel: rv(1, 0)}, {ID: "P1", Site: "A[2,1]", Pos: VecQ2{qstr("1", "1/2"), qstr("-1", "-1/2")}, Vel: rv(0, -1)}, {ID: "P2", Site: "B[2,2]", Pos: VecQ2{qstr("2", "1"), qstr("2", "1")}, Vel: rv(1, 0)}}},
	5629: {Class: 5629, Raw: []string{"A[1,1] +y", "A[1,3] -y", "B[2,0] +x"}, Ps: []P{{ID: "P0", Site: "A[1,1]", Pos: VecQ2{qstr("-1", "-1/2"), qstr("-1", "-1/2")}, Vel: rv(0, 1)}, {ID: "P1", Site: "A[1,3]", Pos: VecQ2{qstr("-1", "-1/2"), qstr("3", "3/2")}, Vel: rv(0, -1)}, {ID: "P2", Site: "B[2,0]", Pos: VecQ2{qstr("2", "1"), qstr("-2", "-1")}, Vel: rv(1, 0)}}},
	4092: {Class: 4092, Raw: []string{"A[1,2] +x", "A[2,0] +y", "B[2,2] +x"}, Ps: []P{{ID: "P0", Site: "A[1,2]", Pos: VecQ2{qstr("-1", "-1/2"), qstr("1", "1/2")}, Vel: rv(1, 0)}, {ID: "P1", Site: "A[2,0]", Pos: VecQ2{qstr("1", "1/2"), qstr("-3", "-3/2")}, Vel: rv(0, 1)}, {ID: "P2", Site: "B[2,2]", Pos: VecQ2{qstr("2", "1"), qstr("2", "1")}, Vel: rv(1, 0)}}},
	3097: {Class: 3097, Raw: []string{"A[1,2] +y", "B[1,0] -x", "A[3,1] -x"}, Ps: []P{{ID: "P0", Site: "A[1,2]", Pos: VecQ2{qstr("-1", "-1/2"), qstr("1", "1/2")}, Vel: rv(0, 1)}, {ID: "P1", Site: "B[1,0]", Pos: VecQ2{qstr("0", "0"), qstr("-2", "-1")}, Vel: rv(-1, 0)}, {ID: "P2", Site: "A[3,1]", Pos: VecQ2{qstr("3", "3/2"), qstr("-1", "-1/2")}, Vel: rv(-1, 0)}}},
	1273: {Class: 1273, Raw: []string{"B[1,2] +x", "A[2,1] -x", "A[3,2] -x"}, Ps: []P{{ID: "P0", Site: "B[1,2]", Pos: VecQ2{qstr("0", "0"), qstr("2", "1")}, Vel: rv(1, 0)}, {ID: "P1", Site: "A[2,1]", Pos: VecQ2{qstr("1", "1/2"), qstr("-1", "-1/2")}, Vel: rv(-1, 0)}, {ID: "P2", Site: "A[3,2]", Pos: VecQ2{qstr("3", "3/2"), qstr("1", "1/2")}, Vel: rv(-1, 0)}}},
	4678: {Class: 4678, Raw: []string{"A[1,3] -y", "A[2,2] +y", "B[2,0] +y"}, Ps: []P{{ID: "P0", Site: "A[1,3]", Pos: VecQ2{qstr("-1", "-1/2"), qstr("3", "3/2")}, Vel: rv(0, -1)}, {ID: "P1", Site: "A[2,2]", Pos: VecQ2{qstr("1", "1/2"), qstr("1", "1/2")}, Vel: rv(0, 1)}, {ID: "P2", Site: "B[2,0]", Pos: VecQ2{qstr("2", "1"), qstr("-2", "-1")}, Vel: rv(0, 1)}}},
	1152: {Class: 1152, Raw: []string{"B[1,2] -y", "B[2,0] -y", "B[2,1] -x"}, Ps: []P{{ID: "P0", Site: "B[1,2]", Pos: VecQ2{qstr("0", "0"), qstr("2", "1")}, Vel: rv(0, -1)}, {ID: "P1", Site: "B[2,0]", Pos: VecQ2{qstr("2", "1"), qstr("-2", "-1")}, Vel: rv(0, -1)}, {ID: "P2", Site: "B[2,1]", Pos: VecQ2{qstr("2", "1"), qstr("0", "0")}, Vel: rv(-1, 0)}}},
}

type HalfSearchReport struct {
	Schema       string      `json:"schema"`
	EdgeLength   string      `json:"edge_length"`
	Container    string      `json:"container"`
	MaxL         int         `json:"max_L"`
	MaxStateBits int         `json:"max_state_bits"`
	Levels       []HalfLevel `json:"levels"`
}
type HalfLevel struct {
	L            int            `json:"L"`
	Bodies       int            `json:"bodies"`
	Sites        int            `json:"sites"`
	RawInitials  int            `json:"raw_initials"`
	D4Classes    int            `json:"d4_classes"`
	CleanClasses int            `json:"clean_classes"`
	StatusCounts map[string]int `json:"status_counts"`
	Top          []Trial        `json:"top_nonreturns"`
}

func main() {
	maxL := flag.Int("max-l", 3, "scan all L=2,...,max-l")
	maxBits := flag.Int("max-state-bits", 128, "exact full-state coefficient bit cap")
	keep := flag.Int("keep", 24, "retain at most this many non-return results per (L,N)")
	bodiesFlag := flag.String("bodies", "2,3", "comma-separated body counts to scan (2 and/or 3)")
	outPath := flag.String("out", "", "write JSON report, or stdout when empty")
	onlyClass := flag.Int("only-class", 0, "run just this D4 class number within each (L,N); 0 scans all")
	watchBatches := flag.Int("watch-batches", 0, "non-discarding exact observation checkpoint; 0 means no checkpoint")
	flag.Parse()
	if *maxL < 2 {
		panic("max-l must be at least 2")
	}
	report := HalfSearchReport{
		Schema:     "half-edge-hard-octagon-atlas-search/v2",
		EdgeLength: "1/2",
		Container:  "unit-edge 4.8.8 L-patch, moving centers fixed to octagon centers",
		MaxL:       *maxL, MaxStateBits: *maxBits,
	}
	vels := []RawParticle{{VX: 1, VY: 0}, {VX: -1, VY: 0}, {VX: 0, VY: 1}, {VX: 0, VY: -1}}
	bodyCounts := []int{}
	for _, part := range strings.Split(*bodiesFlag, ",") {
		if part == "2" {
			bodyCounts = append(bodyCounts, 2)
		} else if part == "3" {
			bodyCounts = append(bodyCounts, 3)
		} else {
			panic("bodies must contain only 2 and/or 3")
		}
	}
	if len(bodyCounts) == 0 {
		panic("bodies must not be empty")
	}
	for L := 2; L <= *maxL; L++ {
		activeAtlasL = L
		sites := lSites(L)
		box := halfEdgeBox(L)
		for _, n := range bodyCounts {
			seen := map[string]struct{}{}
			level := HalfLevel{L: L, Bodies: n, Sites: len(sites), StatusCounts: map[string]int{}}
			var scan func(int, int, []int)
			scan = func(at, need int, chosen []int) {
				if need == 0 {
					ss := make([]Site, len(chosen))
					for i, ix := range chosen {
						ss[i] = sites[ix]
					}
					if !cleanPlacement(ss...) {
						return
					}
					var assign func(int, RawStart)
					assign = func(k int, raw RawStart) {
						if k == n {
							level.RawInitials++
							canon, key := canonicalRaw(raw)
							if _, ok := seen[key]; ok {
								return
							}
							seen[key] = struct{}{}
							if !cleanRawStart(canon, box) {
								return
							}
							level.CleanClasses++
							if *onlyClass != 0 && level.CleanClasses != *onlyClass {
								return
							}
							tr := searchTrial(level.CleanClasses, orbitSize(canon), canon, box, *maxBits, *watchBatches)
							fmt.Fprintf(os.Stderr, "done L=%d N=%d class=%d status=%s batches=%d bits=%d\n", L, n, tr.Class, tr.Status, tr.Batches, tr.MaxPositionBits)
							level.StatusCounts[tr.Status]++
							if tr.Status != "RETURN" {
								level.Top = append(level.Top, tr)
								if len(level.Top) > *keep {
									level.Top = level.Top[:*keep]
								}
							}
							return
						}
						for _, v := range vels {
							assign(k+1, append(raw, RawParticle{U: ss[k].U, V: ss[k].V, VX: v.VX, VY: v.VY}))
						}
					}
					assign(0, RawStart{})
					return
				}
				for i := at; i <= len(sites)-need; i++ {
					scan(i+1, need-1, append(chosen, i))
				}
			}
			scan(0, n, nil)
			level.D4Classes = len(seen)
			report.Levels = append(report.Levels, level)
			fmt.Printf("L=%d N=%d sites=%d classes=%d clean=%d", L, n, level.Sites, level.D4Classes, level.CleanClasses)
			keys := make([]string, 0, len(level.StatusCounts))
			for k := range level.StatusCounts {
				keys = append(keys, k)
			}
			sort.Strings(keys)
			for _, k := range keys {
				fmt.Printf(" %s=%d", k, level.StatusCounts[k])
			}
			fmt.Println()
		}
	}
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		panic(err)
	}
	if *outPath == "" {
		fmt.Println(string(data))
		return
	}
	if err := os.MkdirAll(filepath.Dir(*outPath), 0755); err != nil {
		panic(err)
	}
	if err := os.WriteFile(*outPath, append(data, '\n'), 0644); err != nil {
		panic(err)
	}
}
