// Package artifact defines the portable JSON layer.  All values are exact
// rational coefficient strings; this package does not serialize floats.
package artifact

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
	"sort"
	"strings"

	"latticegeometry/internal/engine"
)

type Scalar struct {
	A string `json:"a"`
	B string `json:"b"`
	C string `json:"c"`
	D string `json:"d"`
}
type Vec struct {
	X Scalar `json:"x"`
	Y Scalar `json:"y"`
}
type Body struct {
	Position Vec `json:"position"`
	Velocity Vec `json:"velocity"`
}
type Event struct {
	DT     Scalar  `json:"dt"`
	Kind   string  `json:"kind"`
	Bodies []int   `json:"bodies"`
	Face   *int    `json:"face"`
	Wall   *string `json:"wall"`
}
type MetricGroup struct {
	MaxAbsNumerator    string `json:"max_abs_numerator"`
	MaxDenominator     string `json:"max_denominator"`
	MaxNumeratorBits   int    `json:"max_numerator_bits"`
	MaxDenominatorBits int    `json:"max_denominator_bits"`
}
type Metrics struct {
	Positions      MetricGroup `json:"positions"`
	Velocities     MetricGroup `json:"velocities"`
	AllCoordinates MetricGroup `json:"all_coordinates"`
}
type EventRecord struct {
	Step          int      `json:"step"`
	ExactDT       Scalar   `json:"exact_dt"`
	ExactT        Scalar   `json:"exact_T"`
	EventClass    string   `json:"event_class"`
	Batch         []Event  `json:"batch"`
	BatchCode     string   `json:"batch_code"`
	PreStateHash  string   `json:"pre_state_hash,omitempty"`
	PostStateHash string   `json:"post_state_hash,omitempty"`
	PreState      []Body   `json:"pre_state,omitempty"`
	PostState     []Body   `json:"post_state,omitempty"`
	Metrics       *Metrics `json:"metrics,omitempty"`
}
type Outcome struct {
	Status                     string        `json:"status"`
	EventBatches               int           `json:"event_batches"`
	ExactT                     Scalar        `json:"exact_T"`
	Events                     []EventRecord `json:"events,omitempty"`
	FinalState                 []Body        `json:"final_state,omitempty"`
	FinalStateHash             string        `json:"final_state_hash"`
	DistinctStates             int           `json:"distinct_states"`
	PairFaceWord               []int         `json:"pair_face_word"`
	InitialMetrics             Metrics       `json:"initial_metrics"`
	FinalMetrics               Metrics       `json:"final_metrics"`
	MaxMetrics                 Metrics       `json:"max_metrics"`
	FirstDenominatorPromotion  *int          `json:"first_denominator_promotion"`
	FirstNumeratorHeightGrowth *int          `json:"first_numerator_height_growth"`
	ReturnPreperiod            *int          `json:"preperiod_events,omitempty"`
	ReturnPeriod               *int          `json:"period_events,omitempty"`
}
type Model struct {
	ModelID         string   `json:"model_id"`
	Polygon         string   `json:"polygon"`
	Sides           int      `json:"sides"`
	Edge            Scalar   `json:"edge"`
	Apothem         Scalar   `json:"apothem"`
	CellSide        Scalar   `json:"cell_side"`
	CardinalWidth   Scalar   `json:"cardinal_width"`
	Field           string   `json:"field"`
	Basis           []string `json:"basis"`
	FaceConvention  string   `json:"face_convention"`
	Normals         []Vec    `json:"face_normals"`
	GeometryVersion string   `json:"geometry_version"`
}
type Container struct {
	Kind         string `json:"kind"`
	CellsPerSide int    `json:"cells_per_side"`
	HalfSide     Scalar `json:"half_side"`
}
type Producer struct {
	Language string `json:"language"`
	Runtime  string `json:"runtime"`
	Module   string `json:"module"`
	Build    string `json:"build"`
}
type Dynamics struct {
	Translation        string   `json:"translation"`
	PolygonOrientation string   `json:"polygon_orientation"`
	PairLaw            string   `json:"pair_law"`
	WallLaw            string   `json:"wall_law"`
	BatchLaw           string   `json:"batch_law"`
	TerminalClasses    []string `json:"terminal_classes"`
	FloatPolicy        string   `json:"float_policy"`
}

type LatticeStart struct {
	Sites        []int    `json:"sites"`
	Velocities   []string `json:"velocities"`
	InitialState []Body   `json:"initial_state"`
}
type CenteredStart struct {
	Face              int         `json:"face"`
	FaceClassMod3     int         `json:"face_class_mod_3"`
	Incoming          []string    `json:"incoming"`
	PreTimeZeroState  []Body      `json:"pre_time_zero_state"`
	TimeZeroEvent     EventRecord `json:"time_zero_event"`
	PostTimeZeroState []Body      `json:"post_time_zero_state"`
}

type Certificate struct {
	Schema        string         `json:"schema"`
	CertificateID string         `json:"certificate_id"`
	Producer      Producer       `json:"producer"`
	Model         Model          `json:"model"`
	Container     Container      `json:"container"`
	Dynamics      Dynamics       `json:"dynamics"`
	Instance      any            `json:"instance"`
	StoppingRule  map[string]any `json:"stopping_rule"`
	Evolution     struct {
		RecordEncoding string        `json:"record_encoding"`
		Events         []EventRecord `json:"events"`
	} `json:"evolution"`
	Result                   Outcome        `json:"result"`
	IndependentCheckContract map[string]any `json:"independent_check_contract"`
}

type AtlasCase struct {
	CaseID     string  `json:"case_id"`
	RawStartID int     `json:"raw_start_id"`
	Start      any     `json:"start"`
	Outcome    Outcome `json:"outcome"`
}
type Atlas struct {
	Schema       string            `json:"schema"`
	ExperimentID string            `json:"experiment_id"`
	Producer     Producer          `json:"producer"`
	Model        Model             `json:"model"`
	Container    Container         `json:"container"`
	Dynamics     Dynamics          `json:"dynamics"`
	Scan         map[string]any    `json:"scan"`
	EventCap     int               `json:"event_cap"`
	RawStarts    int               `json:"raw_starts"`
	Counts       map[string]int    `json:"counts"`
	Earliest     map[string]string `json:"earliest"`
	Results      []AtlasCase       `json:"results"`
}

func ScalarOf(x engine.F) Scalar {
	return Scalar{x.C[0].RatString(), x.C[1].RatString(), x.C[2].RatString(), x.C[3].RatString()}
}
func VecOf(x engine.Vec) Vec { return Vec{ScalarOf(x.X), ScalarOf(x.Y)} }
func BodiesOf(bs []engine.Body) []Body {
	out := make([]Body, len(bs))
	for i, b := range bs {
		out[i] = Body{VecOf(b.Pos), VecOf(b.Vel)}
	}
	return out
}
func EventOf(e engine.Event) Event {
	var face *int
	var wall *string
	if e.Face >= 0 {
		x := e.Face
		face = &x
	}
	if e.Wall != "" {
		x := e.Wall
		wall = &x
	}
	return Event{ScalarOf(e.DT), e.Kind, append([]int{}, e.Bodies...), face, wall}
}
func GroupOf(g engine.MetricGroup) MetricGroup {
	return MetricGroup{g.MaxAbsNumerator.String(), g.MaxDenominator.String(), g.MaxNumeratorBits, g.MaxDenominatorBits}
}
func MetricsOf(m engine.Metrics) Metrics {
	return Metrics{GroupOf(m.Positions), GroupOf(m.Velocities), GroupOf(m.All)}
}
func EventRecordOf(r engine.EventRecord, full bool) EventRecord {
	batch := make([]Event, len(r.Batch))
	for i, e := range r.Batch {
		batch[i] = EventOf(e)
	}
	out := EventRecord{Step: r.Step, ExactDT: ScalarOf(r.DT), ExactT: ScalarOf(r.T), EventClass: string(r.Class), Batch: batch, BatchCode: engine.CanonicalBatchString(r.Batch), PreStateHash: r.PreHash, PostStateHash: r.PostHash}
	if full {
		out.PreState = BodiesOf(r.Pre)
		out.PostState = BodiesOf(r.Post)
		out.Metrics = new(Metrics)
		*out.Metrics = MetricsOf(r.Metrics)
	}
	return out
}
func OutcomeOf(o engine.Outcome, full bool) Outcome {
	ev := make([]EventRecord, len(o.Events))
	for i, r := range o.Events {
		ev[i] = EventRecordOf(r, full)
	}
	out := Outcome{Status: string(o.Status), EventBatches: o.EventBatches, ExactT: ScalarOf(o.T), Events: ev, FinalStateHash: o.FinalHash, DistinctStates: o.DistinctStates, PairFaceWord: append([]int{}, o.PairFaceWord...), InitialMetrics: MetricsOf(o.InitialMetrics), FinalMetrics: MetricsOf(o.FinalMetrics), MaxMetrics: MetricsOf(o.MaxMetrics)}
	if full {
		out.FinalState = BodiesOf(o.Final)
	}
	if o.FirstDenominatorPromotion != 0 {
		v := o.FirstDenominatorPromotion
		out.FirstDenominatorPromotion = &v
	}
	if o.FirstNumeratorHeightGrowth != 0 {
		v := o.FirstNumeratorHeightGrowth
		out.FirstNumeratorHeightGrowth = &v
	}
	if o.Status == "RETURN" {
		a, b := o.ReturnPreperiod, o.ReturnPeriod
		out.ReturnPreperiod = &a
		out.ReturnPeriod = &b
	}
	return out
}
func ModelOf(m engine.Model) Model {
	ns := make([]Vec, len(m.Normals))
	for i, n := range m.Normals {
		ns[i] = VecOf(n)
	}
	return Model{m.ID, fmt.Sprintf("regular %d-gon", m.Sides), m.Sides, ScalarOf(m.Edge), ScalarOf(m.Apothem), ScalarOf(m.CellSide()), ScalarOf(m.Apothem.ScaleRat(2, 1)), m.Field, []string{"1", "sqrt(2)", "sqrt(3)", "sqrt(6)"}, "face k has outward normal angle 360*k/sides degrees", ns, "artifact16-go-v1"}
}
func ContainerOf(c engine.Container) Container {
	return Container{"axis_aligned_square", c.Cells, ScalarOf(c.HalfSide)}
}
func ProducerOf() Producer {
	return Producer{"Go", runtime.Version(), "latticegeometry", "go run ./cmd/lattice"}
}
func DynamicsContract() Dynamics {
	return Dynamics{
		Translation:        "Rigid fixed-orientation translation only; no angular degrees of freedom.",
		PolygonOrientation: "Face 0 has outward normal +x; face labels increase counterclockwise.",
		PairLaw:            "Equal-mass elastic reflection of relative velocity in the active outward face normal.",
		WallLaw:            "Axis-aligned specular reflection at the support offset of the fixed square container.",
		BatchLaw:           "Resolve only regular singleton batches and disjoint same-time batches. Distinct-body same-time contacts commute. Do not serialize shared-body contacts.",
		TerminalClasses:    []string{"PAIR_CORNER", "WALL_CORNER", "COUPLED_SIMULTANEOUS", "NO_EVENT"},
		FloatPolicy:        "No floating-point value is used to create, order, classify, or resolve an event. Coordinates are exact Q(sqrt(2),sqrt(3)) coefficients.",
	}
}
func WriteJSON(path string, value any) error {
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		return err
	}
	raw, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(raw, '\n'), 0644)
}
func SortCounts(counts map[string]int) map[string]int { // makes construction intent explicit; encoding/json sorts map keys.
	keys := make([]string, 0, len(counts))
	for k := range counts {
		keys = append(keys, k)
	}
	sort.Strings(keys)
	out := map[string]int{}
	for _, k := range keys {
		out[k] = counts[k]
	}
	return out
}
func CleanID(s string) string { return strings.NewReplacer("/", "_", " ", "_", ",", "_").Replace(s) }
