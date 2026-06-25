// exact-c4 is a deliberately small, Go-only Q(sqrt(2)) batch-event prototype.
// It reconstructs the C4 candidate in the README's inradius-one octagon metric:
// |x|<=1, |y|<=1, |x+y|<=sqrt(2), |x-y|<=sqrt(2).
package main

import (
	"fmt"
	"math/big"
	"sort"
)

type Q2 struct{ A, B *big.Rat }  // A + B sqrt(2)
func q(a, b int64) Q2            { return Q2{big.NewRat(a, 1), big.NewRat(b, 1)} }
func qr(a, b *big.Rat) Q2        { return Q2{new(big.Rat).Set(a), new(big.Rat).Set(b)} }
func (x Q2) add(y Q2) Q2         { return qr(new(big.Rat).Add(x.A, y.A), new(big.Rat).Add(x.B, y.B)) }
func (x Q2) sub(y Q2) Q2         { return qr(new(big.Rat).Sub(x.A, y.A), new(big.Rat).Sub(x.B, y.B)) }
func (x Q2) scale(r *big.Rat) Q2 { return qr(new(big.Rat).Mul(x.A, r), new(big.Rat).Mul(x.B, r)) }
func (x Q2) div(r *big.Rat) Q2   { return qr(new(big.Rat).Quo(x.A, r), new(big.Rat).Quo(x.B, r)) }
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
func (x Q2) str() string {
	if x.B.Sign() == 0 {
		return x.A.RatString()
	}
	if x.A.Sign() == 0 {
		return x.B.RatString() + "*sqrt2"
	}
	return x.A.RatString() + " + (" + x.B.RatString() + ")*sqrt2"
}

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
func (v RatVec) eq(w RatVec) bool { return v.X.Cmp(w.X) == 0 && v.Y.Cmp(w.Y) == 0 }

type VecQ2 struct{ X, Y Q2 }

func (v VecQ2) sub(w VecQ2) VecQ2 { return VecQ2{v.X.sub(w.X), v.Y.sub(w.Y)} }
func (v VecQ2) addVel(vel RatVec, t Q2) VecQ2 {
	return VecQ2{v.X.add(t.scale(vel.X)), v.Y.add(t.scale(vel.Y))}
}

type Face struct {
	Name    string
	NX, NY  int64
	Support Q2
}

// Unit-edge regular octagon: cardinal support r=(1+sqrt2)/2.
// For unnormalised diagonal normals (±1,±1), support is r*sqrt2=1+sqrt2/2.
var faces = []Face{
	{"E", 1, 0, Q2{big.NewRat(1, 2), big.NewRat(1, 2)}},
	{"NE", 1, 1, Q2{big.NewRat(1, 1), big.NewRat(1, 2)}},
	{"N", 0, 1, Q2{big.NewRat(1, 2), big.NewRat(1, 2)}},
	{"NW", -1, 1, Q2{big.NewRat(1, 1), big.NewRat(1, 2)}},
	{"W", -1, 0, Q2{big.NewRat(1, 2), big.NewRat(1, 2)}},
	{"SW", -1, -1, Q2{big.NewRat(1, 1), big.NewRat(1, 2)}},
	{"S", 0, -1, Q2{big.NewRat(1, 2), big.NewRat(1, 2)}},
	{"SE", 1, -1, Q2{big.NewRat(1, 1), big.NewRat(1, 2)}},
}

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
	ID  string
	Pos VecQ2
	Vel RatVec
}

func (p P) cp() P { return P{p.ID, VecQ2{p.Pos.X, p.Pos.Y}, p.Vel.cp()} }

type State struct{ Ps []P }

func (s State) cp() State {
	o := State{Ps: make([]P, len(s.Ps))}
	for i, p := range s.Ps {
		o.Ps[i] = p.cp()
	}
	return o
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
	Corner bool // disk--disk contact at a relative-exclusion vertex; never resolved
}

// UnknownEventError marks an exact geometric event for which this model has
// deliberately chosen no collision law.  In particular, a disk--disk contact
// at a vertex of the relative exclusion octagon is NOT resolved by a velocity
// swap.  It terminates that trajectory as UNKNOWN.  This is distinct from a
// particle hitting a rectangular container corner: two simultaneous
// perpendicular wall reflections are an unambiguous total reflection.
type UnknownEventError struct {
	Class string
	A, B  string
	Time  Q2
	Faces []string
}

func (e *UnknownEventError) Error() string {
	return fmt.Sprintf("unknown %s at %s bodies %s/%s faces %v",
		e.Class, e.Time.str(), e.A, e.B, e.Faces)
}

func (e Event) key(s State) string {
	if e.K == wall {
		return "wall:" + s.Ps[e.I].ID + ":" + e.Wall
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
	// Keep a disk--disk vertex candidate through global time ordering.  It is
	// classified UNKNOWN only if it belongs to the earliest event batch; a later
	// vertex candidate must not preempt earlier ordinary collisions.
	if len(af) == 2 {
		return Event{T: *best, K: pair, I: i, J: j, F: bestF, Corner: true}, true, nil
	}
	return Event{}, false, fmt.Errorf("multi-face pair %s/%s at %s", a.ID, b.ID, best.str())
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
	radius := faces[0].Support
	negBox := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	if p.Vel.X.Sign() > 0 {
		add(faces[0], "E", box.sub(p.Pos.X).sub(radius), p.Vel.X)
	}
	if p.Vel.X.Sign() < 0 {
		add(faces[4], "W", p.Pos.X.sub(negBox).sub(radius), new(big.Rat).Neg(p.Vel.X))
	}
	if p.Vel.Y.Sign() > 0 {
		add(faces[2], "N", box.sub(p.Pos.Y).sub(radius), p.Vel.Y)
	}
	if p.Vel.Y.Sign() < 0 {
		add(faces[6], "S", p.Pos.Y.sub(negBox).sub(radius), new(big.Rat).Neg(p.Vel.Y))
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
	// A disk--disk corner is deliberately unresolved.  This check occurs only
	// after selecting the earliest exact batch, so it cannot hide an earlier
	// ordinary event.
	for _, e := range batch {
		if e.K == pair && e.Corner {
			a, b := s.Ps[e.I].ID, s.Ps[e.J].ID
			loc := s.Ps[e.J].Pos.sub(s.Ps[e.I].Pos).addVel(s.Ps[e.J].Vel.sub(s.Ps[e.I].Vel), e.T)
			af := active(loc)
			names := make([]string, len(af))
			for i, f := range af {
				names[i] = f.Name
			}
			return nil, &UnknownEventError{Class: "pair_corner", A: a, B: b, Time: e.T, Faces: names}
		}
	}
	// A body may have two walls only if they are perpendicular: total reflection.
	use := map[int][]Event{}
	for _, e := range batch {
		use[e.I] = append(use[e.I], e)
		if e.K == pair {
			use[e.J] = append(use[e.J], e)
		}
	}
	for body, hits := range use {
		pairs := 0
		walls := 0
		var wf []Face
		for _, e := range hits {
			if e.K == pair {
				pairs++
			} else {
				walls++
				wf = append(wf, e.F)
			}
		}
		if pairs > 0 && (len(hits) > 1) {
			return nil, fmt.Errorf("shared-body batch at %s body %s", min.str(), s.Ps[body].ID)
		}
		if walls > 2 {
			return nil, fmt.Errorf("three-wall batch at %s body %s", min.str(), s.Ps[body].ID)
		}
		if walls == 2 && (wf[0].NX*wf[1].NX+wf[0].NY*wf[1].NY) != 0 {
			return nil, fmt.Errorf("nonperpendicular double wall at %s body %s", min.str(), s.Ps[body].ID)
		}
	}
	return batch, nil
}
func resolvePair(s *State, e Event) {
	if e.Corner {
		panic("unresolved pair corner reached resolvePair")
	}
	a, b := &s.Ps[e.I], &s.Ps[e.J]
	n2 := e.F.NX*e.F.NX + e.F.NY*e.F.NY
	g := dotR(e.F, b.Vel.sub(a.Vel))
	aCoeff := new(big.Rat).Quo(g, big.NewRat(n2, 1))
	a.Vel.X.Add(a.Vel.X, new(big.Rat).Mul(aCoeff, big.NewRat(e.F.NX, 1)))
	a.Vel.Y.Add(a.Vel.Y, new(big.Rat).Mul(aCoeff, big.NewRat(e.F.NY, 1)))
	b.Vel.X.Sub(b.Vel.X, new(big.Rat).Mul(aCoeff, big.NewRat(e.F.NX, 1)))
	b.Vel.Y.Sub(b.Vel.Y, new(big.Rat).Mul(aCoeff, big.NewRat(e.F.NY, 1)))
}
func resolveBatch(s *State, b []Event) {
	// Pair bodies are disjoint. Wall reflections commute, including a perpendicular double wall.
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
func validPost(s State, box Q2) error {
	radius := faces[0].Support
	negBox := Q2{new(big.Rat).Neg(box.A), new(big.Rat).Neg(box.B)}
	for _, p := range s.Ps {
		if p.Pos.X.sub(radius).cmp(negBox) < 0 || p.Pos.X.add(radius).cmp(box) > 0 || p.Pos.Y.sub(radius).cmp(negBox) < 0 || p.Pos.Y.add(radius).cmp(box) > 0 {
			return fmt.Errorf("wall escape %s", p.ID)
		}
	}
	for i := range s.Ps {
		for j := i + 1; j < len(s.Ps); j++ {
			d := s.Ps[j].Pos.sub(s.Ps[i].Pos)
			if inside(d) {
				af := active(d)
				if len(af) == 0 {
					return fmt.Errorf("overlap %s/%s", s.Ps[i].ID, s.Ps[j].ID)
				} // permit one-face contact only if separating or tangential
				f := af[0]
				if dotR(f, s.Ps[j].Vel.sub(s.Ps[i].Vel)).Sign() < 0 {
					return fmt.Errorf("approaching contact %s/%s", s.Ps[i].ID, s.Ps[j].ID)
				}
			}
		}
	}
	return nil
}
func same(a, b State) bool {
	if len(a.Ps) != len(b.Ps) {
		return false
	}
	for i := range a.Ps {
		p, q := a.Ps[i], b.Ps[i]
		if p.ID != q.ID || !p.Pos.X.eq(q.Pos.X) || !p.Pos.Y.eq(q.Pos.Y) || !p.Vel.eq(q.Vel) {
			return false
		}
	}
	return true
}

type BatchWire struct {
	Index  int      `json:"index"`
	Time   Q2Wire   `json:"time"`
	Events []string `json:"events"`
}
type Out struct {
	Normalization string      `json:"normalization"`
	HalfBox       Q2Wire      `json:"half_box"`
	MaskOrbits    int         `json:"c4_mask_orbits"`
	Batches       []BatchWire `json:"batches"`
	ReturnBatch   int         `json:"return_batch"`
	ReturnTime    *Q2Wire     `json:"return_time,omitempty"`
	Error         string      `json:"error,omitempty"`
}

func c4MaskOrbits() int { // necklaces of 4 rays over per-ray alphabet {00,01,10,11}
	seen := map[[4]uint8]bool{}
	n := 0
	for x := 0; x < 256; x++ {
		var a [4]uint8
		for i := 0; i < 4; i++ {
			a[i] = uint8((x >> (2 * i)) & 3)
		}
		if seen[a] {
			continue
		}
		n++
		for r := 0; r < 4; r++ {
			var b [4]uint8
			for i := 0; i < 4; i++ {
				b[i] = a[(i+r)%4]
			}
			seen[b] = true
		}
	}
	return n
}
