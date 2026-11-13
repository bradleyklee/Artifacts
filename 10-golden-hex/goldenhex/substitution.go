package goldenhex

import (
	"fmt"
	"sort"
	"strings"
)

// Address symbols are the letters used by the address inflation Phi.
type AddressSymbol byte

const (
	SymD AddressSymbol = 'D'
	SymK AddressSymbol = 'K'
	SymH AddressSymbol = 'H'
	SymA AddressSymbol = 'a'
	SymB AddressSymbol = 'b'
	SymG AddressSymbol = 'g'
	Symh AddressSymbol = 'h'
)

// Step is one address token, such as D_3 or a_1.
type Step struct {
	Symbol AddressSymbol
	Dir    int
}

// Word is an address path from the false center to a tile anchor.
type Word []Step

// TileKind is the inflated object classification used for replay.
type TileKind byte

const (
	FalseCenter TileKind = 'F'
	Dimer       TileKind = 'D'
	Branch      TileKind = 'B'
	Leaf        TileKind = 'G'
)

// Tile is one substituted object.
//
// A Dimer covers Anchor and Anchor+Directions[Ori].  A Branch normally
// contributes one ON cell, but AxisCap marks the branch as a cap and therefore
// OFF in the binary replay.
type Tile struct {
	Kind    TileKind
	Ori     int
	Address Word
	AxisCap bool
}

func inflateStep(step Step) Word {
	i := mod6(step.Dir)
	switch step.Symbol {
	case SymD:
		return Word{{SymD, i}, {SymK, i}}
	case SymK, SymH:
		return Word{{SymD, i}, {SymK, i}, {SymH, i}}
	case SymA:
		return Word{{SymD, mod6(i - 2)}, {SymA, i}, {SymH, i}}
	case SymB:
		return Word{{SymD, mod6(i - 1)}, {SymB, i}, {SymH, i}}
	case SymG, Symh:
		return Word{{step.Symbol, i}, {SymH, i}}
	default:
		panic(fmt.Sprintf("unknown address symbol %q", step.Symbol))
	}
}

func inflateWord(word Word) Word {
	out := make(Word, 0, 3*len(word))
	for _, step := range word {
		out = append(out, inflateStep(step)...)
	}
	return out
}

func newChild(root Word, kind TileKind, ori int, suffix Word, axisCap bool) Tile {
	address := make(Word, 0, len(root)+len(suffix))
	address = append(address, root...)
	for _, step := range suffix {
		address = append(address, Step{Symbol: step.Symbol, Dir: mod6(step.Dir)})
	}
	return Tile{Kind: kind, Ori: mod6(ori), Address: address, AxisCap: axisCap}
}

func InflateTile(tile Tile) []Tile {
	i := mod6(tile.Ori)
	root := inflateWord(tile.Address)

	if tile.Kind == FalseCenter {
		out := []Tile{{Kind: FalseCenter, Ori: 0, Address: root}}
		for j := 0; j < 6; j++ {
			out = append(out, newChild(root, Branch, j, Word{{SymG, j}}, false))
		}
		return out
	}

	if tile.Kind == Dimer {
		return []Tile{
			newChild(root, Dimer, i, nil, false),
			newChild(root, Dimer, i, Word{{SymD, i}, {SymK, i}}, false),
			newChild(root, Branch, i, Word{{SymD, i}, {SymK, i}, {SymD, i}, {SymK, i}}, false),
			newChild(root, Leaf, i+2, Word{{SymD, i}, {SymA, i + 2}}, false),
			newChild(root, Leaf, i+1, Word{{SymD, i}, {SymB, i + 1}}, false),
			newChild(root, Branch, i+2, Word{{SymD, i}, {SymK, i}, {SymD, i}, {SymA, i + 2}}, false),
			newChild(root, Branch, i+1, Word{{SymD, i}, {SymK, i}, {SymD, i}, {SymB, i + 1}}, false),
			newChild(root, Branch, i-1, Word{{SymG, i - 1}}, false),
			newChild(root, Branch, i-2, Word{{Symh, i - 2}}, false),
			newChild(root, Leaf, i-1, Word{{SymD, i}, {SymK, i}, {SymG, i - 1}}, false),
			newChild(root, Leaf, i-2, Word{{SymD, i}, {SymK, i}, {Symh, i - 2}}, false),
		}
	}

	// Branch is a through-branch carrier; Leaf is a terminal leaf.  The axial
	// child is an OFF cap precisely when it comes from a Leaf parent or from an
	// existing cap.
	axisCap := tile.Kind == Leaf || tile.AxisCap
	return []Tile{
		newChild(root, Dimer, i, nil, false),
		newChild(root, Branch, i, Word{{SymD, i}, {SymK, i}}, axisCap),
		newChild(root, Leaf, i+2, Word{{SymD, i}, {SymA, i + 2}}, false),
		newChild(root, Leaf, i+1, Word{{SymD, i}, {SymB, i + 1}}, false),
		newChild(root, Leaf, i-1, Word{{SymG, i - 1}}, false),
		newChild(root, Leaf, i-2, Word{{Symh, i - 2}}, false),
	}
}

// Inflate applies one substitution step and merges duplicate objects.
func Inflate(patch []Tile) ([]Tile, error) {
	seen := make(map[string]Tile)
	for _, tile := range patch {
		for _, child := range InflateTile(tile) {
			key := tileKey(child)
			old, ok := seen[key]
			if ok && old.AxisCap != child.AxisCap {
				return nil, fmt.Errorf("cap conflict at %s", key)
			}
			if !ok {
				seen[key] = child
			}
		}
	}

	keys := make([]string, 0, len(seen))
	for key := range seen {
		keys = append(keys, key)
	}
	sort.Strings(keys)

	out := make([]Tile, 0, len(seen))
	for _, key := range keys {
		out = append(out, seen[key])
	}
	return out, nil
}

func tileKey(tile Tile) string {
	return fmt.Sprintf("%c%d:%s", tile.Kind, mod6(tile.Ori), wordKey(tile.Address))
}

func wordKey(word Word) string {
	var b strings.Builder
	for _, step := range word {
		b.WriteByte(byte(step.Symbol))
		b.WriteByte(byte('0' + mod6(step.Dir)))
	}
	return b.String()
}

func anchor(word Word) Hex {
	cell := Hex{}
	for _, step := range word {
		cell = cell.Add(dir(step.Dir))
	}
	return cell
}
