package goldenhex

import "fmt"

// OnCells builds the finite level patch and returns its ON cells.
func OnCells(level int) (map[Hex]bool, error) {
	if level < 0 {
		return nil, fmt.Errorf("negative level %d", level)
	}

	patch := []Tile{{Kind: FalseCenter, Ori: 0}}
	var err error
	for n := 0; n < level; n++ {
		patch, err = Inflate(patch)
		if err != nil {
			return nil, err
		}
	}

	on := make(map[Hex]bool)
	for _, tile := range patch {
		cell := anchor(tile.Address)
		switch tile.Kind {
		case FalseCenter:
			on[cell] = true
		case Dimer:
			on[cell] = true
			on[cell.Add(dir(tile.Ori))] = true
		case Branch:
			if !tile.AxisCap {
				on[cell] = true
			}
		}
	}
	return on, nil
}

type ray struct {
	Cell    Hex
	Heading int
}

// ArrivalTimes replays directed growth on the ON-cell set.
func ArrivalTimes(on map[Hex]bool) (map[Hex]int, error) {
	times := map[Hex]int{{}: 0}
	seen := make(map[ray]bool)
	front := make([]ray, 0, 6)

	for heading, step := range Directions {
		nb := (Hex{}).Add(step)
		if on[nb] {
			front = append(front, ray{Cell: nb, Heading: heading})
			seen[ray{Cell: nb, Heading: heading}] = true
			if _, ok := times[nb]; !ok {
				times[nb] = 1
			}
		}
	}

	for t := 1; len(front) > 0; t++ {
		next := make([]ray, 0, len(front))
		for _, current := range front {
			targets := []ray{{
				Cell:    current.Cell.Add(dir(current.Heading)),
				Heading: current.Heading,
			}}

			for _, turn := range []int{-1, 1} {
				h1 := mod6(current.Heading + turn)
				h2 := mod6(current.Heading + 2*turn)
				c1 := current.Cell.Add(dir(h1))
				c2 := current.Cell.Add(dir(h2))
				if on[c1] && on[c2] {
					targets = append(targets, ray{Cell: c1, Heading: h1})
					targets = append(targets, ray{Cell: c2, Heading: h2})
				}
			}

			for _, target := range targets {
				if !on[target.Cell] || seen[target] {
					continue
				}
				seen[target] = true
				next = append(next, target)
				if _, ok := times[target.Cell]; !ok {
					times[target.Cell] = t + 1
				}
			}
		}
		front = next
	}

	if len(times) != len(on) {
		return nil, fmt.Errorf("replay reached %d ON cells, expected %d", len(times), len(on))
	}
	return times, nil
}

// ReplaySequence returns a_t=(N_t-1)/6 for a finite substituted patch.
func ReplaySequence(level int) ([]int, error) {
	on, err := OnCells(level)
	if err != nil {
		return nil, err
	}
	times, err := ArrivalTimes(on)
	if err != nil {
		return nil, err
	}

	maxTime := 0
	for _, t := range times {
		if t > maxTime {
			maxTime = t
		}
	}

	births := make([]int, maxTime+1)
	for _, t := range times {
		births[t]++
	}

	seq := make([]int, 0, len(births))
	total := 0
	for _, birth := range births {
		total += birth
		if (total-1)%6 != 0 {
			return nil, fmt.Errorf("normalization failed at total %d", total)
		}
		seq = append(seq, (total-1)/6)
	}
	return seq, nil
}

func FirstDifferences(seq []int) []int {
	if len(seq) == 0 {
		return nil
	}
	diffs := make([]int, len(seq))
	diffs[0] = 0
	for i := 1; i < len(seq); i++ {
		diffs[i] = seq[i] - seq[i-1]
	}
	return diffs
}
