// Package burner is an exact, two-body-only event runner for the retained
// dodecagon and 24-gon fixtures.  It deliberately keeps the generic engine as
// an oracle while reducing hot-loop work to a wall horizon, safe rejects, and
// an exposed-half contact-facet scan.
package burner

import (
	"fmt"
	"math/big"
	"sort"

	"latticegeometry/internal/engine"
)

// Height measures coefficient complexity without converting an exact field
// element to a float.  The maximum is taken across the fixed field basis.
type Height struct {
	MaxNumeratorBits   int `json:"max_numerator_bits"`
	MaxDenominatorBits int `json:"max_denominator_bits"`
}

// TimeComplexity records the monolithic exact collision clock as well as the
// current local increment.  Both heights are computed directly from rational
// coefficients in Q(sqrt(2),sqrt(3)).
// RationalHeight preserves the separate reduced numerator and denominator
// bit lengths of one rational coefficient.  These are telemetry only: the
// exact rational itself remains in the ledger's exact_dt/exact_T fields.
type RationalHeight struct {
	NumeratorBits   int `json:"numerator_bits"`
	DenominatorBits int `json:"denominator_bits"`
}

// FieldHeight exposes all four Q(sqrt(2),sqrt(3)) basis coefficients in a
// stable order: a + b*sqrt(2) + c*sqrt(3) + d*sqrt(6).  A dodecagon run has
// b=d=0, but they remain present so every campaign row has one schema.
type FieldHeight struct {
	A RationalHeight `json:"a"`
	B RationalHeight `json:"b"`
	C RationalHeight `json:"c"`
	D RationalHeight `json:"d"`
}

// TimeComplexity records the monolithic exact collision clock as well as the
// current local increment.  DT/T retain aggregate maxima for quick profiles;
// DTParts/TParts retain every coefficient's numerator and denominator bit
// length for growth/recurrence analysis.
type TimeComplexity struct {
	DT      Height      `json:"dt"`
	T       Height      `json:"T"`
	Running Height      `json:"running_T"`
	DTParts FieldHeight `json:"dt_parts"`
	TParts  FieldHeight `json:"T_parts"`
}

// FilterStats is proof-oriented telemetry.  A true rejection means the pair
// was ruled out exactly before the facet scan; a false value never rules out a
// possible contact.
type FilterStats struct {
	AABBRejected          bool `json:"aabb_rejected"`
	ParabolaRejected      bool `json:"parabola_rejected"`
	ConstantMiss          bool `json:"constant_distance_miss"`
	FacetsExposed         int  `json:"facets_exposed"`
	FacetsTested          int  `json:"facets_tested"`
	ValidPairCandidates   int  `json:"valid_pair_candidates"`
	QuotientsMaterialized int  `json:"quotients_materialized"`
}

// Record is a compact, exact ledger row.  State payloads are intentionally
// absent here so callers can stream millions of rows without retaining an
// in-memory trace; checkpointing belongs to the output layer.
type Record struct {
	Step     int               `json:"step"`
	DT       engine.F          `json:"-"`
	T        engine.F          `json:"-"`
	Class    engine.BatchClass `json:"event_class"`
	Batch    []engine.Event    `json:"-"`
	PreHash  string            `json:"pre_state_hash"`
	PostHash string            `json:"post_state_hash"`
	Filter   FilterStats       `json:"filter"`
	Time     TimeComplexity    `json:"time_complexity"`
	State    engine.Metrics    `json:"-"`
}

// Options controls storage rather than physics.  The hot path is exact in
// either mode.  Disable DetectReturn for long certificate burns where the
// append-only ledger/checkpoints are the product and a growing StateKey map is
// not wanted.
type Options struct {
	// InitialTime and StartStep make a checkpointed continuation a first-class
	// exact segment.  The supplied state must be the state *after* StartStep;
	// records produced by Run then begin at StartStep+1 and retain absolute T.
	// Nil InitialTime means exact time zero.
	InitialTime      *engine.F
	StartStep        int
	DetectReturn     bool
	InitialPairFaces []int
	OnRecord         func(Record) error
	CheckpointEvery  int
	OnCheckpoint     func(step int, t engine.F, bodies []engine.Body, hash string) error
}

// Outcome is deliberately compact.  It contains enough information to bind a
// streamed ledger to an exact final state and to report collision-clock growth.
type Outcome struct {
	Status engine.BatchClass
	// EventBatches is the number of batches produced by this segment.
	EventBatches    int
	StartStep       int
	EndStep         int
	T               engine.F
	Final           []engine.Body
	FinalHash       string
	PairFaceWord    []int
	InitialState    engine.Metrics
	FinalState      engine.Metrics
	MaxState        engine.Metrics
	MaxTime         Height
	Filters         FilterTotals
	ReturnPreperiod int
	ReturnPeriod    int
}

// FilterTotals is an aggregate profile for one burn.
type FilterTotals struct {
	Steps                 int `json:"steps"`
	AABBRejects           int `json:"aabb_rejects"`
	ParabolaRejects       int `json:"parabola_rejects"`
	ConstantMisses        int `json:"constant_distance_misses"`
	FacetsExposed         int `json:"facets_exposed"`
	FacetsTested          int `json:"facets_tested"`
	ValidCandidates       int `json:"valid_pair_candidates"`
	QuotientsMaterialized int `json:"quotients_materialized"`
}

func heightOf(x engine.F) Height {
	h := Height{}
	for _, r := range x.C {
		n := new(big.Int).Abs(r.Num()).BitLen()
		d := r.Denom().BitLen()
		if n > h.MaxNumeratorBits {
			h.MaxNumeratorBits = n
		}
		if d > h.MaxDenominatorBits {
			h.MaxDenominatorBits = d
		}
	}
	return h
}

func rationalHeight(r *big.Rat) RationalHeight {
	return RationalHeight{NumeratorBits: new(big.Int).Abs(r.Num()).BitLen(), DenominatorBits: r.Denom().BitLen()}
}

func fieldHeightOf(x engine.F) FieldHeight {
	return FieldHeight{A: rationalHeight(x.C[0]), B: rationalHeight(x.C[1]), C: rationalHeight(x.C[2]), D: rationalHeight(x.C[3])}
}
func maxHeight(a, b Height) Height {
	if b.MaxNumeratorBits > a.MaxNumeratorBits {
		a.MaxNumeratorBits = b.MaxNumeratorBits
	}
	if b.MaxDenominatorBits > a.MaxDenominatorBits {
		a.MaxDenominatorBits = b.MaxDenominatorBits
	}
	return a
}

func copyBodies(bs []engine.Body) []engine.Body {
	out := make([]engine.Body, len(bs))
	for i, b := range bs {
		out[i] = b.Clone()
	}
	return out
}

// quotient denotes num/den with den strictly positive.  It supports exact
// ordering by cross multiplication, postponing field division until the
// earliest event batch has been selected.
type quotient struct{ num, den engine.F }

func (q quotient) value() engine.F { return q.num.Div(q.den) }
func cmpQ(a, b quotient) int       { return a.num.Mul(b.den).Cmp(b.num.Mul(a.den)) }

// candidate contains only the event identity and its positive exact quotient.
// Event.DT is filled once the global earliest quotient is known.
type candidate struct {
	q      quotient
	kind   string
	bodies []int
	face   int
	wall   string
}

func (c candidate) event(dt engine.F) engine.Event {
	return engine.Event{DT: dt, Kind: c.kind, Bodies: append([]int{}, c.bodies...), Face: c.face, Wall: c.wall}
}

func wallCandidates(m engine.Model, c engine.Container, bs []engine.Body, i int) []candidate {
	b := bs[i]
	out := make([]candidate, 0, 2)
	specs := []struct {
		coord, vel engine.F
		wall       string
		sign       int
	}{
		{b.Pos.X, b.Vel.X, "E", 1}, {b.Pos.X, b.Vel.X, "W", -1},
		{b.Pos.Y, b.Vel.Y, "N", 1}, {b.Pos.Y, b.Vel.Y, "S", -1},
	}
	for _, s := range specs {
		target := c.HalfSide.Sub(m.Apothem)
		if s.sign < 0 {
			target = c.HalfSide.Neg().Add(m.Apothem)
		}
		speed := s.vel
		gap := target.Sub(s.coord)
		if s.sign < 0 {
			speed = speed.Neg()
			gap = s.coord.Sub(target)
		}
		if speed.Sign() > 0 && gap.Sign() > 0 {
			out = append(out, candidate{q: quotient{gap, speed}, kind: "WALL_FACE", bodies: []int{i}, face: -1, wall: s.wall})
		}
	}
	return out
}

func earliest(cs []candidate) (candidate, []candidate, bool) {
	if len(cs) == 0 {
		return candidate{}, nil, false
	}
	best := cs[0]
	for _, c := range cs[1:] {
		if cmpQ(c.q, best.q) < 0 {
			best = c
		}
	}
	batch := make([]candidate, 0, len(cs))
	for _, c := range cs {
		if cmpQ(c.q, best.q) == 0 {
			batch = append(batch, c)
		}
	}
	return best, batch, true
}

func contactThreshold(m engine.Model) engine.F { return m.Apothem.ScaleRat(2, 1) }

// facetSegmentCheck uses the two adjacent supporting inequalities.  On the
// supporting line of one facet of a strictly convex polygon, those two
// neighbors alone bound exactly that finite facet segment; all other halfspace
// tests are redundant.  This is the exact tangent-span check described in the
// burner design, not an approximation.
func facetSegmentCheck(m engine.Model, face int, r0, u engine.Vec, q quotient) (ok bool, activeFaces int) {
	h := contactThreshold(m)
	activeFaces = 1 // the candidate's own supporting equality
	for _, neighbor := range []int{(face - 1 + m.Sides) % m.Sides, (face + 1) % m.Sides} {
		n := m.Normals[neighbor]
		v := engine.Dot(n, r0).Sub(h).Mul(q.den).Add(engine.Dot(n, u).Mul(q.num))
		if v.Sign() > 0 {
			return false, 0
		}
		if v.Sign() == 0 {
			activeFaces++
		}
	}
	return true, activeFaces
}

// axisAABBReject exactly proves that the two swept physical body AABBs are
// disjoint over [0,T].  In the retained orientations face normals are cardinal,
// so the exact x/y body reach is the apothem.
func axisAABBReject(m engine.Model, a, b engine.Body, T engine.F) bool {
	bounds := func(pos, vel engine.F) (engine.F, engine.F) {
		end := pos.Add(vel.Mul(T))
		lo, hi := pos, end
		if lo.Cmp(hi) > 0 {
			lo, hi = hi, lo
		}
		return lo.Sub(m.Apothem), hi.Add(m.Apothem)
	}
	ax0, ax1 := bounds(a.Pos.X, a.Vel.X)
	ay0, ay1 := bounds(a.Pos.Y, a.Vel.Y)
	bx0, bx1 := bounds(b.Pos.X, b.Vel.X)
	by0, by1 := bounds(b.Pos.Y, b.Vel.Y)
	return ax1.Cmp(bx0) < 0 || bx1.Cmp(ax0) < 0 || ay1.Cmp(by0) < 0 || by1.Cmp(ay0) < 0
}

// circumradiusSquared returns R^2 without introducing a square root outside
// the state field.  R^2=A^2/cos(pi/n)^2 lies in the retained field for both
// models even though R itself need not.
func circumradiusSquared(m engine.Model) engine.F {
	switch m.ID {
	case "dodecagon":
		cosHalfSq := engine.Q(2).Add(engine.Sqrt3()).ScaleRat(1, 4) // cos(15°)^2
		return m.Apothem.Mul(m.Apothem).Div(cosHalfSq)
	case "24gon":
		// cos(7.5°)^2 = (4 + sqrt(2) + sqrt(6))/8.
		cosHalfSq := engine.Q(4).Add(engine.Sqrt2()).Add(engine.Sqrt2().Mul(engine.Sqrt3())).ScaleRat(1, 8)
		return m.Apothem.Mul(m.Apothem).Div(cosHalfSq)
	default:
		panic("burner only supports dodecagon and 24gon")
	}
}

// parabolaMiss is the mandatory exact circumscribed-disk rejection.  It tests
// the minimum of |r0+u t|^2 on [0,T] using endpoint/vertex cases.  The vertex
// case is compared after clearing 4a, avoiding roots and avoiding division.
func parabolaMiss(m engine.Model, r0, u engine.Vec, T engine.F) (miss, constant bool) {
	dmax2 := circumradiusSquared(m).ScaleRat(4, 1)
	a := engine.Dot(u, u)
	c := engine.Dot(r0, r0)
	if a.IsZero() {
		return c.Cmp(dmax2) > 0, true
	}
	b := engine.Dot(r0, u).ScaleRat(2, 1)
	// Vertex lies at or left of t=0: min is c.
	if b.Sign() >= 0 {
		return c.Cmp(dmax2) > 0, false
	}
	rightDerivative := b.Add(a.Mul(T).ScaleRat(2, 1))
	// Vertex lies at or right of the horizon: min is the right endpoint.
	if rightDerivative.Sign() <= 0 {
		rT := r0.Add(u.Scale(T))
		return engine.Dot(rT, rT).Cmp(dmax2) > 0, false
	}
	// Interior vertex.  Since a>0, min>dmax2 iff
	// 4a(c-dmax2)-b^2 > 0.
	cleared := a.Mul(c.Sub(dmax2)).ScaleRat(4, 1).Sub(b.Mul(b))
	return cleared.Sign() > 0, false
}

func pairCandidate(m engine.Model, bs []engine.Body, horizon quotient, haveHorizon bool, T engine.F, stats *FilterStats) *candidate {
	r0 := bs[1].Pos.Sub(bs[0].Pos)
	u := bs[1].Vel.Sub(bs[0].Vel)
	if haveHorizon {
		if axisAABBReject(m, bs[0], bs[1], T) {
			stats.AABBRejected = true
			return nil
		}
		if miss, constant := parabolaMiss(m, r0, u, T); miss {
			stats.ParabolaRejected = true
			stats.ConstantMiss = constant
			return nil
		}
	}
	h := contactThreshold(m)
	retained := make([]candidate, 0, m.Sides/2)
	for face, n := range m.Normals {
		derivative := engine.Dot(n, u)
		gap := engine.Dot(n, r0).Sub(h)
		if derivative.Sign() >= 0 || gap.Sign() <= 0 {
			continue
		}
		stats.FacetsExposed++
		q := quotient{num: gap, den: derivative.Neg()}
		if haveHorizon && cmpQ(q, horizon) > 0 {
			continue
		}
		stats.FacetsTested += 2
		ok, _ := facetSegmentCheck(m, face, r0, u, q)
		if !ok {
			continue
		}
		retained = append(retained, candidate{q: q, kind: "PAIR_FACE", bodies: []int{0, 1}, face: face, wall: ""})
		stats.ValidPairCandidates++
	}
	best, _, ok := earliest(retained)
	if !ok {
		return nil
	}
	_, active := facetSegmentCheck(m, best.face, r0, u, best.q)
	if active != 1 {
		best.kind = "PAIR_CORNER"
	}
	return &best
}

func classify(batch []engine.Event) engine.BatchClass {
	for _, e := range batch {
		if e.Kind == "PAIR_CORNER" {
			return engine.PairCorner
		}
	}
	wallSeen := map[int]bool{}
	for _, e := range batch {
		if e.Kind == "WALL_FACE" {
			i := e.Bodies[0]
			if wallSeen[i] {
				return engine.WallCorner
			}
			wallSeen[i] = true
		}
	}
	if len(batch) == 1 {
		return engine.Regular
	}
	involved := map[int]bool{}
	arity := 0
	allWall := true
	for _, e := range batch {
		if e.Kind != "WALL_FACE" {
			allWall = false
		}
		for _, i := range e.Bodies {
			involved[i] = true
			arity++
		}
	}
	if len(involved) == arity {
		if allWall {
			return engine.IndependentWallBatch
		}
		return engine.IndependentBatch
	}
	return engine.CoupledSimultaneous
}

// nextBatch is a two-body replacement for engine.NextBatch.  It has identical
// event semantics on regular cases but applies the safe filters before the
// exposed-half scan and materializes only the winner's exact quotient.
func nextBatch(m engine.Model, c engine.Container, bs []engine.Body) ([]engine.Event, engine.BatchClass, FilterStats) {
	stats := FilterStats{}
	walls := append(wallCandidates(m, c, bs, 0), wallCandidates(m, c, bs, 1)...)
	wallBest, wallBatch, haveWall := earliest(walls)
	var T engine.F
	if haveWall {
		T = wallBest.q.value()
		stats.QuotientsMaterialized++
	}
	pair := pairCandidate(m, bs, wallBest.q, haveWall, T, &stats)
	if !haveWall && pair == nil {
		return nil, engine.NoEvent, stats
	}

	var chosenQ quotient
	chosen := []candidate{}
	switch {
	case !haveWall:
		chosenQ, chosen = pair.q, []candidate{*pair}
	case pair == nil:
		chosenQ, chosen = wallBest.q, wallBatch
	default:
		rel := cmpQ(pair.q, wallBest.q)
		if rel < 0 {
			chosenQ, chosen = pair.q, []candidate{*pair}
		} else if rel > 0 {
			chosenQ, chosen = wallBest.q, wallBatch
		} else {
			chosenQ = wallBest.q
			chosen = append(append([]candidate{}, wallBatch...), *pair)
		}
	}
	dt := chosenQ.value()
	stats.QuotientsMaterialized++
	batch := make([]engine.Event, len(chosen))
	for i, q := range chosen {
		batch[i] = q.event(dt)
	}
	return batch, classify(batch), stats
}

func accumulate(t *FilterTotals, s FilterStats) {
	t.Steps++
	if s.AABBRejected {
		t.AABBRejects++
	}
	if s.ParabolaRejected {
		t.ParabolaRejects++
	}
	if s.ConstantMiss {
		t.ConstantMisses++
	}
	t.FacetsExposed += s.FacetsExposed
	t.FacetsTested += s.FacetsTested
	t.ValidCandidates += s.ValidPairCandidates
	t.QuotientsMaterialized += s.QuotientsMaterialized
}

// Run executes exactly two labelled bodies.  It never uses floating-point
// arithmetic to select, reject, order, classify, or resolve events.
func Run(m engine.Model, c engine.Container, start []engine.Body, cap int, opt Options) (Outcome, error) {
	if len(start) != 2 {
		return Outcome{}, fmt.Errorf("burner requires exactly two bodies, got %d", len(start))
	}
	if m.ID != "dodecagon" && m.ID != "24gon" {
		return Outcome{}, fmt.Errorf("burner supports only dodecagon and 24gon, got %s", m.ID)
	}
	bs := copyBodies(start)
	t := engine.Zero()
	if opt.InitialTime != nil {
		t = opt.InitialTime.Clone()
	}
	if opt.StartStep < 0 {
		return Outcome{}, fmt.Errorf("negative StartStep %d", opt.StartStep)
	}
	initialMetrics := engine.StateMetrics(bs)
	maxState := initialMetrics
	maxTime := heightOf(t)
	pairWord := append([]int{}, opt.InitialPairFaces...)
	seen := map[string]int(nil)
	if opt.DetectReturn {
		seen = map[string]int{engine.StateKey(bs): opt.StartStep}
	}
	totals := FilterTotals{}
	if opt.CheckpointEvery > 0 && opt.OnCheckpoint != nil {
		if err := opt.OnCheckpoint(opt.StartStep, t, copyBodies(bs), engine.StateHash(bs)); err != nil {
			return Outcome{}, err
		}
	}

	// checkpointFinal anchors every completed segment at its actual absolute
	// endpoint, even when StartStep+steps is not a multiple of the regular
	// checkpoint cadence.  This is required for lossless continuation chains.
	checkpointFinal := func(steps int) error {
		if opt.CheckpointEvery <= 0 || opt.OnCheckpoint == nil {
			return nil
		}
		step := opt.StartStep + steps
		if step%opt.CheckpointEvery == 0 {
			return nil // the cadence checkpoint already wrote this state.
		}
		return opt.OnCheckpoint(step, t, copyBodies(bs), engine.StateHash(bs))
	}

	finish := func(status engine.BatchClass, steps int) Outcome {
		return Outcome{Status: status, EventBatches: steps, StartStep: opt.StartStep, EndStep: opt.StartStep + steps, T: t, Final: copyBodies(bs), FinalHash: engine.StateHash(bs), PairFaceWord: append([]int{}, pairWord...), InitialState: initialMetrics, FinalState: engine.StateMetrics(bs), MaxState: maxState, MaxTime: maxTime, Filters: totals}
	}

	for localStep := 1; localStep <= cap; localStep++ {
		step := opt.StartStep + localStep
		batch, class, stats := nextBatch(m, c, bs)
		accumulate(&totals, stats)
		if class == engine.NoEvent {
			if err := checkpointFinal(localStep - 1); err != nil {
				return Outcome{}, err
			}
			return finish(engine.NoEvent, localStep-1), nil
		}
		dt := batch[0].DT
		preHash := engine.StateHash(bs)
		engine.Advance(bs, dt)
		t = t.Add(dt)
		if !class.Resolvable() {
			rec := Record{Step: step, DT: dt, T: t, Class: class, Batch: batch, PreHash: preHash, PostHash: "", Filter: stats, Time: TimeComplexity{DT: heightOf(dt), T: heightOf(t), Running: maxTime, DTParts: fieldHeightOf(dt), TParts: fieldHeightOf(t)}, State: engine.StateMetrics(bs)}
			maxTime = maxHeight(maxTime, rec.Time.T)
			rec.Time.Running = maxTime
			if opt.OnRecord != nil {
				if err := opt.OnRecord(rec); err != nil {
					return Outcome{}, err
				}
			}
			if opt.CheckpointEvery > 0 && opt.OnCheckpoint != nil && step%opt.CheckpointEvery == 0 {
				if err := opt.OnCheckpoint(step, t, copyBodies(bs), engine.StateHash(bs)); err != nil {
					return Outcome{}, err
				}
			}
			if err := checkpointFinal(localStep); err != nil {
				return Outcome{}, err
			}
			return finish(class, localStep), nil
		}
		for _, e := range batch {
			engine.Resolve(m, bs, e)
			if e.Kind == "PAIR_FACE" && e.Face >= 0 {
				pairWord = append(pairWord, e.Face)
			}
		}
		state := engine.StateMetrics(bs)
		maxState = engine.MaxMetrics(maxState, state)
		hT := heightOf(t)
		maxTime = maxHeight(maxTime, hT)
		rec := Record{Step: step, DT: dt, T: t, Class: class, Batch: batch, PreHash: preHash, PostHash: engine.StateHash(bs), Filter: stats, Time: TimeComplexity{DT: heightOf(dt), T: hT, Running: maxTime, DTParts: fieldHeightOf(dt), TParts: fieldHeightOf(t)}, State: state}
		if opt.OnRecord != nil {
			if err := opt.OnRecord(rec); err != nil {
				return Outcome{}, err
			}
		}
		if opt.CheckpointEvery > 0 && opt.OnCheckpoint != nil && step%opt.CheckpointEvery == 0 {
			if err := opt.OnCheckpoint(step, t, copyBodies(bs), engine.StateHash(bs)); err != nil {
				return Outcome{}, err
			}
		}
		if opt.DetectReturn {
			key := engine.StateKey(bs)
			if prior, ok := seen[key]; ok {
				if err := checkpointFinal(localStep); err != nil {
					return Outcome{}, err
				}
				out := finish("RETURN", localStep)
				out.ReturnPreperiod, out.ReturnPeriod = prior, step-prior
				return out, nil
			}
			seen[key] = step
		}
	}
	if err := checkpointFinal(cap); err != nil {
		return Outcome{}, err
	}
	return finish("CAP", cap), nil
}

// CanonicalBatchString mirrors the engine's compact external labels without
// exposing the candidate representation.
func CanonicalBatchString(batch []engine.Event) string { return engine.CanonicalBatchString(batch) }

// SortedPairFaceWord is convenient for testing only; evolution keeps the
// original chronological word and never calls this helper.
func SortedPairFaceWord(word []int) []int {
	out := append([]int{}, word...)
	sort.Ints(out)
	return out
}
