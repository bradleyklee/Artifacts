// mask_evolve.go reads one exact seed and writes a raw exact event ledger.
// Run: go run mask_evolve.go main_nomai.go --seed ../initial/.../mask_019.json --out ../runs/mask_019.evolve.json
package main

import (
	"encoding/json"
	"errors"
	"flag"
	"fmt"
	"math/big"
	"os"
)

type MQ2W struct {
	A string `json:"a"`
	B string `json:"b"`
}
type MPosW struct {
	X MQ2W `json:"x"`
	Y MQ2W `json:"y"`
}
type MVelW struct {
	VX string `json:"vx"`
	VY string `json:"vy"`
}
type MBodyW struct {
	ID       string `json:"id"`
	Position MPosW  `json:"position"`
	Velocity MVelW  `json:"velocity"`
}
type MSeed struct {
	MaskBits  int    `json:"mask_bits"`
	MaskText  string `json:"mask_text"`
	Weight    int    `json:"weight"`
	Container struct {
		HalfBox MQ2W `json:"half_box"`
	} `json:"container"`
	State []MBodyW `json:"state"`
}
type MStateW struct {
	ID       string `json:"id"`
	Position MPosW  `json:"position"`
	Velocity MVelW  `json:"velocity"`
}
type MLedgerRow struct {
	Index     int       `json:"index"`
	Time      Q2Wire    `json:"time"`
	Events    []string  `json:"events"`
	Pre       []MStateW `json:"pre"`
	Post      []MStateW `json:"post"`
	StateHash string    `json:"state_hash"`
}
type MRun struct {
	Schema           string       `json:"schema"`
	ComplexityCutoffBits int    `json:"complexity_cutoff_bits,omitempty"`
	MaxComplexityBits int       `json:"max_complexity_bits_observed,omitempty"`
	NextComplexityBits int      `json:"next_complexity_bits,omitempty"`
	Seed             string       `json:"seed"`
	MaskBits         int          `json:"mask_bits"`
	MaskText         string       `json:"mask_text"`
	Weight           int          `json:"weight"`
	HalfBox          Q2Wire       `json:"half_box"`
	RequestedBatches int          `json:"requested_batches"`
	CompletedBatches int          `json:"completed_batches"`
	StopClass        string       `json:"stop_class"`
	StopDetail       string       `json:"stop_detail,omitempty"`
	ReturnIndex      int          `json:"return_index,omitempty"`
	Ledger           []MLedgerRow `json:"ledger"`
}

func mr(s string) *big.Rat {
	x := new(big.Rat)
	if _, ok := x.SetString(s); !ok {
		panic("bad rational " + s)
	}
	return x
}
func mq(w MQ2W) Q2 { return Q2{mr(w.A), mr(w.B)} }
func ms(s State) []MStateW {
	out := make([]MStateW, len(s.Ps))
	for i, p := range s.Ps {
		out[i] = MStateW{
			ID: p.ID,
			Position: MPosW{
				X: MQ2W{A: p.Pos.X.A.RatString(), B: p.Pos.X.B.RatString()},
				Y: MQ2W{A: p.Pos.Y.A.RatString(), B: p.Pos.Y.B.RatString()},
			},
			Velocity: MVelW{VX: p.Vel.X.RatString(), VY: p.Vel.Y.RatString()},
		}
	}
	return out
}
func hashState(s State) string { b, _ := json.Marshal(ms(s)); return string(b) }
func classErr(err error) string {
	var u *UnknownEventError
	if errors.As(err, &u) {
		return "unknown_" + u.Class
	}
	msg := err.Error()
	if len(msg) >= 17 && msg[:17] == "shared-body batch" {
		return "shared_body_batch"
	}
	if len(msg) >= 11 && msg[:11] == "three-wall " {
		return "three_wall_batch"
	}
	if len(msg) >= 17 && msg[:17] == "nonperpendicular" {
		return "nonperpendicular_double_wall"
	}
	return "evolver_error"
}

func ratBits(r *big.Rat) int {
	a, b := r.Num(), r.Denom()
	an, bn := a.BitLen(), b.BitLen()
	if an > bn { return an }
	return bn
}
func q2Bits(x Q2) int {
	a, b := ratBits(x.A), ratBits(x.B)
	if a > b { return a }
	return b
}
func stateComplexityBits(s State) int {
	m := 0
	for _, p := range s.Ps {
		for _, z := range []Q2{p.Pos.X, p.Pos.Y} {
			if n:=q2Bits(z); n>m { m=n }
		}
		for _, r := range []*big.Rat{p.Vel.X,p.Vel.Y} {
			if n:=ratBits(r); n>m { m=n }
		}
	}
	return m
}

func main() {
	seedPath := flag.String("seed", "", "")
	outPath := flag.String("out", "", "")
	batches := flag.Int("batches", 512, "")
	complexityBits := flag.Int("complexity-bits", 0, "exact rational coefficient bit cutoff; 0 disables")
	flag.Parse()
	if *seedPath == "" || *outPath == "" {
		panic("--seed and --out required")
	}
	blob, err := os.ReadFile(*seedPath)
	if err != nil {
		panic(err)
	}
	var seed MSeed
	if err := json.Unmarshal(blob, &seed); err != nil {
		panic(err)
	}
	s := State{Ps: make([]P, len(seed.State))}
	for i, b := range seed.State {
		s.Ps[i] = P{b.ID, VecQ2{mq(b.Position.X), mq(b.Position.Y)}, RatVec{mr(b.Velocity.VX), mr(b.Velocity.VY)}}
	}
	box := mq(seed.Container.HalfBox)
	initial := s.cp()
	now := q(0, 0)
	run := MRun{Schema: "c4-clock-mask-evolve-ledger/v2", Seed: *seedPath, MaskBits: seed.MaskBits, MaskText: seed.MaskText, Weight: seed.Weight, HalfBox: box.wire(), RequestedBatches: *batches, ComplexityCutoffBits: *complexityBits, MaxComplexityBits: stateComplexityBits(s), ReturnIndex: -1, StopClass: "completed_budget"}
	if err := validPost(s, box); err != nil {
		run.StopClass = "invalid_initial"
		run.StopDetail = err.Error()
	} else {
		for k := 1; k <= *batches; k++ {
			pre := s.cp()
			b, err := nextBatch(s, box)
			if err != nil {
				run.StopClass = classErr(err)
				run.StopDetail = err.Error()
				break
			}
			if len(b) == 0 {
				run.StopClass = "no_future_event"
				break
			}
			dt := b[0].T
			advance(&s, dt)
			now = now.add(dt)
			resolveBatch(&s, b)
			if err := validPost(s, box); err != nil {
				run.StopClass = "post_validation_error"
				run.StopDetail = err.Error()
				break
			}
			nextBits := stateComplexityBits(s)
			if *complexityBits > 0 && nextBits > *complexityBits {
				run.StopClass = "complexity_cutoff"
				run.NextComplexityBits = nextBits
				run.StopDetail = fmt.Sprintf("next post-state complexity %d exceeds cutoff %d", nextBits, *complexityBits)
				break
			}
			ev := make([]string, len(b))
			for i, e := range b {
				ev[i] = e.key(pre)
			}
			run.Ledger = append(run.Ledger, MLedgerRow{k, now.wire(), ev, ms(pre), ms(s), hashState(s)})
			run.CompletedBatches = k
			if nextBits > run.MaxComplexityBits { run.MaxComplexityBits = nextBits }
			if same(s, initial) {
				run.StopClass = "return"
				run.ReturnIndex = k
				break
			}
		}
	}
	out, err := json.MarshalIndent(run, "", "  ")
	if err != nil {
		panic(err)
	}
	if err := os.WriteFile(*outPath, append(out, '\n'), 0644); err != nil {
		panic(err)
	}
	fmt.Println(*outPath, run.StopClass, "completed", run.CompletedBatches)
}
