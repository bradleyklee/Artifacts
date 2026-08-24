// Package skiplist implements a deterministic 1-2 skip list in the algorithmic
// family introduced by Munro, Papadakis, and Sedgewick (SODA 1992).
//
// Horizontal type tags 1..5 encode the 1-2 gap invariant. Updates use local
// deterministic rewrites; representation changes are admitted only when they
// preserve the verified invariants or improve measured cost.
package skiplist

import (
	"errors"
	"fmt"
	"sort"
)

// OrderFunc returns positive when a precedes b, zero when they are equivalent
// for ordering, and negative when a follows b.
type OrderFunc[V any] func(a, b V) int

type link struct {
	prev int
	next int
	typ  int
}

type node[V any] struct {
	value    V
	hasValue bool
	// levels is a contiguous tower indexed by level-1. Contiguity is structural
	// rather than represented by a per-level map.
	levels []link
}

// List is a deterministic 1-2 skip list ordered by values while keys provide
// identity. Keys are unique; values need not be.
type List[K comparable, V any] struct {
	depth int
	order OrderFunc[V]

	// Internal indices are arena offsets. Index 0 is the start sentinel and
	// -1 is the separately stored stop sentinel. This keeps local rewrites in
	// integer-index form while avoiding a hash lookup and heap allocation for
	// every node.
	head  node[V]
	tail  node[V]
	nodes []node[V] // nodes[0] is unused; live nodes have hasValue=true.

	nextIndex int
	missing   []int // reusable arena indices, in release order.
	keyToIdx  map[K]int
	idxToKey  []K // valid exactly where nodes[index].hasValue is true.

	trace func(string) // verification hook; nil in normal use
}

func (s *List[K, V]) emit(event string) {
	if s.trace != nil {
		s.trace(event)
	}
}

// New constructs an empty list.
func New[K comparable, V any](order OrderFunc[V]) *List[K, V] {
	if order == nil {
		panic("skiplist: nil order function")
	}
	return &List[K, V]{
		order:     order,
		nodes:     make([]node[V], 1),
		nextIndex: 1,
		keyToIdx:  make(map[K]int),
		idxToKey:  make([]K, 1),
	}
}

func (s *List[K, V]) Depth() int  { return s.depth }
func (s *List[K, V]) Len() int    { return len(s.keyToIdx) }
func (s *List[K, V]) Empty() bool { return s.depth == 0 }

func (s *List[K, V]) n(index int) *node[V] {
	switch index {
	case 0:
		return &s.head
	case -1:
		return &s.tail
	}
	if index <= 0 || index >= len(s.nodes) || !s.nodes[index].hasValue {
		panic(fmt.Sprintf("skiplist: invariant failed: missing node %d", index))
	}
	return &s.nodes[index]
}

func (s *List[K, V]) ensureSlot(index int) {
	if index < len(s.nodes) {
		return
	}
	grow := index + 1 - len(s.nodes)
	s.nodes = append(s.nodes, make([]node[V], grow)...)
	s.idxToKey = append(s.idxToKey, make([]K, grow)...)
}

func (s *List[K, V]) hasLevel(index, level int) bool {
	return level > 0 && level <= len(s.n(index).levels)
}

func (s *List[K, V]) l(index, level int) *link {
	if !s.hasLevel(index, level) {
		panic(fmt.Sprintf("skiplist: invariant failed: missing node %d level %d", index, level))
	}
	return &s.n(index).levels[level-1]
}

func (s *List[K, V]) ensureLevel(index, level int) *link {
	if level <= 0 {
		panic(fmt.Sprintf("skiplist: invariant failed: invalid level %d", level))
	}
	n := s.n(index)
	if level > len(n.levels) {
		n.levels = append(n.levels, make([]link, level-len(n.levels))...)
	}
	return &n.levels[level-1]
}

func (s *List[K, V]) clearLevel(index, level int) {
	n := s.n(index)
	if level <= 0 || level != len(n.levels) {
		panic(fmt.Sprintf("skiplist: invariant failed: clear non-top node %d level %d height %d", index, level, len(n.levels)))
	}
	n.levels = n.levels[:level-1]
}

// insertPosition returns the internal neighbors around the insertion point.
// It is kept internal because sentinel neighbors have no user key.
func (s *List[K, V]) insertPosition(value V) (left, right int) {
	cursor := 0
	for level := s.depth; level > 0; {
		next := s.l(cursor, level).next
		if next == -1 || s.order(value, s.n(next).value) == 1 {
			level--
		} else {
			cursor = next
		}
	}
	if s.depth == 0 {
		return 0, -1
	}
	return cursor, s.l(cursor, 1).next
}

func (s *List[K, V]) allocIndex() int {
	if len(s.missing) != 0 {
		i := s.missing[0]
		s.missing = s.missing[1:]
		return i
	}
	i := s.nextIndex
	s.nextIndex++
	return i
}

// Insert inserts or replaces key. It returns true for a new key and false when
// an existing key was deleted and reinserted.
func (s *List[K, V]) Insert(key K, value V) bool {
	fresh := true
	if _, ok := s.keyToIdx[key]; ok {
		_ = s.Delete(key)
		fresh = false
	}

	index := s.allocIndex()
	s.ensureSlot(index)
	s.nodes[index] = node[V]{value: value, hasValue: true, levels: make([]link, 1)}
	s.keyToIdx[key] = index
	s.idxToKey[index] = key

	if s.depth == 0 {
		s.depth = 1
		*s.ensureLevel(0, 1) = link{next: index, typ: 1}
		*s.ensureLevel(-1, 1) = link{prev: index}
		*s.ensureLevel(index, 1) = link{prev: 0, next: -1, typ: 2}
		return fresh
	}

	left, right := s.insertPosition(value)
	s.insertAt(index, left, right, 1)
	return fresh
}

func (s *List[K, V]) insertAt(index, left, right, level int) {
	s.ensureLevel(index, level)
	s.l(left, level).next = index
	s.l(right, level).prev = index
	x := s.l(index, level)
	x.next, x.prev = right, left

	lt, rt := s.l(left, level).typ, s.l(right, level).typ
	var reassign []int
	var nextTypes []int

	switch {
	case lt == 1 && rt == 2:
		reassign = []int{left, index, right}
		nextTypes = []int{3, 4, 5}
	case lt == 2:
		left2 := s.l(left, level).prev
		reassign = []int{left2, left, index}
		nextTypes = []int{3, 4, 5}
	case lt == 3 && rt == 4:
		right2 := s.l(right, level).next
		reassign = []int{left, index, right, right2}
		nextTypes = []int{1, 2, 1, 2}
	case lt == 4 && rt == 5:
		left2 := s.l(left, level).prev
		reassign = []int{left2, left, index, right}
		nextTypes = []int{1, 2, 1, 2}
	case lt == 5:
		left2 := s.l(left, level).prev
		left3 := s.l(left2, level).prev
		reassign = []int{left3, left2, left, index}
		nextTypes = []int{1, 2, 1, 2}
	default:
		panic(fmt.Sprintf("skiplist: invariant failed: unhandled insert types {%d,%d} at level %d", lt, rt, level))
	}

	for i, idx := range reassign {
		s.l(idx, level).typ = nextTypes[i]
	}

	if len(nextTypes) != 4 {
		return
	}

	promoted := reassign[2]
	if s.depth == level {
		s.depth = level + 1
		end := s.l(reassign[3], level).next
		*s.ensureLevel(0, level+1) = link{next: promoted, typ: 1}
		*s.ensureLevel(promoted, level+1) = link{prev: 0, next: end, typ: 2}
		s.ensureLevel(end, level+1).prev = promoted
		return
	}

	s.ensureLevel(promoted, level+1)
	upperLeft := reassign[0]
	upperRight := s.l(upperLeft, level+1).next
	s.insertAt(promoted, upperLeft, upperRight, level+1)
}

// Delete removes key and reports whether it existed.
func (s *List[K, V]) Delete(key K) bool {
	index, ok := s.keyToIdx[key]
	if !ok {
		return false
	}
	s.deleteAt(index, 1)
	delete(s.keyToIdx, key)
	var zeroK K
	s.idxToKey[index] = zeroK
	s.nodes[index] = node[V]{}
	s.missing = append(s.missing, index)
	return true
}

func (s *List[K, V]) deleteAt(index, level int) {
	x := s.l(index, level)
	typ, left, right := x.typ, x.prev, x.next
	s.l(left, level).next = right
	s.l(right, level).prev = left

	// Keep the detached level in the node until closure has moved or removed
	// every promoted level above it. This preserves contiguous tower storage
	// throughout the mutation without changing any horizontal rewrite.
	s.deleteType(typ, index, level, left, right)
	s.clearLevel(index, level)
}

func (s *List[K, V]) shiftVertical(shiftFrom, shiftTo, level int) {
	from := s.n(shiftFrom)
	height := len(from.levels)
	for nextLevel := level + 1; nextLevel <= height; nextLevel++ {
		levelData := from.levels[nextLevel-1]
		*s.ensureLevel(shiftTo, nextLevel) = levelData
		s.l(levelData.next, nextLevel).prev = shiftTo
		s.l(levelData.prev, nextLevel).next = shiftTo
	}
	if height > level {
		from.levels = from.levels[:level]
	}
}

func (s *List[K, V]) setTypes(level int, indices, types []int) {
	if len(indices) != len(types) {
		panic("skiplist: invariant failed: setTypes length mismatch")
	}
	for i, idx := range indices {
		s.l(idx, level).typ = types[i]
	}
}

func (s *List[K, V]) deleteType2(index, level, left, right int) {
	left2 := s.l(left, level).prev
	switch {
	case left == 0 && right == -1:
		s.emit("D2_TOP")
		s.clearLevel(left, level)
		s.clearLevel(right, level)
		s.depth--

	case s.l(right, level).typ == 3:
		s.emit("D2_MERGE_RIGHT")
		right2 := s.l(right, level).next
		right3 := s.l(right2, level).next
		s.setTypes(level, []int{right, right2, right3}, []int{2, 1, 2})
		s.shiftVertical(right, right2, level)

	case s.l(left2, level).typ == 5:
		s.emit("D2_MERGE_LEFT")
		left3 := s.l(left2, level).prev
		left4 := s.l(left3, level).prev
		s.setTypes(level, []int{left4, left3, left2, left}, []int{1, 2, 1, 2})
		s.shiftVertical(left, left2, level)

	case right != -1:
		s.emit("D2_RECURSE_RIGHT")
		right2 := s.l(right, level).next
		s.setTypes(level, []int{left, right, right2}, []int{3, 4, 5})
		if level != s.depth {
			s.deleteAt(right, level+1)
		}

	default:
		s.emit("D2_RECURSE_LEFT")
		left3 := s.l(left2, level).prev
		s.setTypes(level, []int{left3, left2, left}, []int{3, 4, 5})
		if level != s.depth {
			s.deleteAt(left, level+1)
		}
	}
}

func (s *List[K, V]) deleteType(typ, index, level, left, right int) {
	switch typ {
	case 1:
		left2 := s.l(left, level).prev
		if s.l(left, level).typ == 2 {
			s.emit("D1_RECURSE")
			s.setTypes(level, []int{left2, left, right}, []int{3, 4, 5})
			if level != s.depth {
				s.deleteAt(index, level+1)
			}
		} else {
			s.emit("D1_MERGE")
			left3 := s.l(left2, level).prev
			s.setTypes(level, []int{left3, left2, left}, []int{1, 2, 1})
			s.shiftVertical(index, left, level)
		}

	case 2:
		s.deleteType2(index, level, left, right)

	case 3:
		s.emit("D3_SHIFT_RIGHT")
		rightRight := s.l(right, level).next
		s.l(right, level).typ = 1
		s.l(rightRight, level).typ = 2
		s.shiftVertical(index, right, level)

	case 4:
		s.emit("D4_LOCAL")
		s.l(left, level).typ = 1
		s.l(right, level).typ = 2

	case 5:
		s.emit("D5_LOCAL")
		leftLeft := s.l(left, level).prev
		s.l(leftLeft, level).typ = 1
		s.l(left, level).typ = 2

	default:
		panic(fmt.Sprintf("skiplist: invariant failed: deletion type %d", typ))
	}
}

func (s *List[K, V]) Lookup(key K) (V, bool) {
	idx, ok := s.keyToIdx[key]
	if !ok {
		var zero V
		return zero, false
	}
	return s.n(idx).value, true
}

func (s *List[K, V]) First() (V, bool) {
	if s.depth == 0 {
		var zero V
		return zero, false
	}
	i := s.l(0, 1).next
	return s.n(i).value, true
}

func (s *List[K, V]) Last() (V, bool) {
	if s.depth == 0 {
		var zero V
		return zero, false
	}
	i := s.l(-1, 1).prev
	return s.n(i).value, true
}

func (s *List[K, V]) PopFirst() (V, bool) {
	if s.depth == 0 {
		var zero V
		return zero, false
	}
	idx := s.l(0, 1).next
	v := s.n(idx).value
	s.Delete(s.idxToKey[idx])
	return v, true
}

func (s *List[K, V]) PopLast() (V, bool) {
	if s.depth == 0 {
		var zero V
		return zero, false
	}
	idx := s.l(-1, 1).prev
	v := s.n(idx).value
	s.Delete(s.idxToKey[idx])
	return v, true
}

func (s *List[K, V]) Values() []V {
	if s.depth == 0 {
		return nil
	}
	out := make([]V, 0, len(s.keyToIdx))
	for i := s.l(0, 1).next; i != -1; i = s.l(i, 1).next {
		out = append(out, s.n(i).value)
	}
	return out
}

// Entry is one ordered key/value pair.
type Entry[K comparable, V any] struct {
	Key   K
	Value V
}

// EntriesAt returns entries at a specific level in skip-list order.
func (s *List[K, V]) EntriesAt(level int) []Entry[K, V] {
	if level <= 0 || level > s.depth {
		return nil
	}
	out := make([]Entry[K, V], 0)
	for i := s.l(0, level).next; i != -1; i = s.l(i, level).next {
		out = append(out, Entry[K, V]{Key: s.idxToKey[i], Value: s.n(i).value})
	}
	return out
}

// InsertPosition reports the user keys adjacent to the insertion position.
// A false boolean means that side is the start/stop sentinel.
func (s *List[K, V]) InsertPosition(value V) (left K, leftOK bool, right K, rightOK bool) {
	li, ri := s.insertPosition(value)
	if li != 0 {
		left, leftOK = s.idxToKey[li], true
	}
	if ri != -1 {
		right, rightOK = s.idxToKey[ri], true
	}
	return
}

// GarbageCollect compacts allocator bookkeeping by dropping free indices
// above the current maximum live index and moves nextIndex down accordingly.
// Live nodes are never renumbered.
func (s *List[K, V]) GarbageCollect() bool {
	maxIndex := 0
	limit := s.nextIndex
	if limit > len(s.nodes) {
		limit = len(s.nodes)
	}
	for idx := 1; idx < limit; idx++ {
		if s.nodes[idx].hasValue {
			maxIndex = idx
		}
	}
	changed := s.nextIndex != maxIndex+1
	kept := s.missing[:0]
	for _, idx := range s.missing {
		if idx <= maxIndex {
			kept = append(kept, idx)
		} else {
			changed = true
		}
	}
	s.missing = kept
	s.nextIndex = maxIndex + 1
	return changed
}

// Validate checks the complete representation invariant. It verifies horizontal
// reciprocity, ordering, exact vertical
// promotion correspondence, contiguous towers, sentinel coverage, key/index
// bijection, and the type grammar encoding the 1-2 gap rule.
func (s *List[K, V]) Validate() error {
	if s.order == nil {
		return errors.New("nil order function")
	}
	if s.nextIndex < 1 {
		return fmt.Errorf("invalid nextIndex %d", s.nextIndex)
	}
	if s.nextIndex > len(s.nodes) {
		return fmt.Errorf("nextIndex %d exceeds arena length %d", s.nextIndex, len(s.nodes))
	}
	if len(s.idxToKey) != len(s.nodes) {
		return fmt.Errorf("key arena length mismatch: keys=%d nodes=%d", len(s.idxToKey), len(s.nodes))
	}

	for k, idx := range s.keyToIdx {
		if idx <= 0 || idx >= s.nextIndex || idx >= len(s.nodes) || !s.nodes[idx].hasValue {
			return fmt.Errorf("key points to absent/non-value node %d", idx)
		}
		if s.idxToKey[idx] != k {
			return fmt.Errorf("key/index maps not inverse at index %d", idx)
		}
	}

	missing := make(map[int]bool, len(s.missing))
	for _, idx := range s.missing {
		if idx <= 0 || idx >= s.nextIndex {
			return fmt.Errorf("invalid missing index %d with nextIndex %d", idx, s.nextIndex)
		}
		if missing[idx] {
			return fmt.Errorf("duplicate missing index %d", idx)
		}
		missing[idx] = true
		if s.nodes[idx].hasValue {
			return fmt.Errorf("missing index %d is still live", idx)
		}
	}

	realNodes := 0
	for idx := 1; idx < s.nextIndex; idx++ {
		n := &s.nodes[idx]
		if !n.hasValue {
			if !missing[idx] {
				return fmt.Errorf("unaccounted free index %d", idx)
			}
			continue
		}
		realNodes++
		k := s.idxToKey[idx]
		if idx2, ok := s.keyToIdx[k]; !ok || idx2 != idx {
			return fmt.Errorf("orphan real node %d", idx)
		}
		if len(n.levels) == 0 {
			return fmt.Errorf("real node %d has empty tower", idx)
		}
		if len(n.levels) > s.depth {
			return fmt.Errorf("node %d exceeds depth: %d > %d", idx, len(n.levels), s.depth)
		}
	}
	for idx := s.nextIndex; idx < len(s.nodes); idx++ {
		if s.nodes[idx].hasValue {
			return fmt.Errorf("live node %d above nextIndex %d", idx, s.nextIndex)
		}
	}
	if realNodes != len(s.keyToIdx) {
		return fmt.Errorf("arena/key count mismatch: %d != %d", realNodes, len(s.keyToIdx))
	}
	if realNodes+len(s.missing) != s.nextIndex-1 {
		return fmt.Errorf("allocator coverage mismatch: live=%d missing=%d nextIndex=%d", realNodes, len(s.missing), s.nextIndex)
	}

	if s.depth == 0 {
		if len(s.keyToIdx) != 0 {
			return errors.New("depth zero with real nodes")
		}
		if len(s.head.levels) != 0 || len(s.tail.levels) != 0 {
			return errors.New("depth zero with sentinel levels")
		}
		return nil
	}
	if len(s.head.levels) != s.depth || len(s.tail.levels) != s.depth {
		return fmt.Errorf("sentinel depth mismatch: head=%d tail=%d depth=%d", len(s.head.levels), len(s.tail.levels), s.depth)
	}

	seenLevel1 := map[int]bool{}
	for level := 1; level <= s.depth; level++ {
		seen := map[int]bool{0: true}
		cur := 0
		var prevValue V
		havePrevValue := false
		for {
			cl := s.l(cur, level)
			next := cl.next
			if next == 0 {
				return fmt.Errorf("level %d loops to start", level)
			}
			if next != -1 {
				if next <= 0 || next >= s.nextIndex || !s.nodes[next].hasValue {
					return fmt.Errorf("level %d links to absent node %d", level, next)
				}
				if seen[next] {
					return fmt.Errorf("level %d cycle at node %d", level, next)
				}
				seen[next] = true
			}
			nl := s.l(next, level)
			if nl.prev != cur {
				return fmt.Errorf("level %d reciprocal link failure %d -> %d but prev=%d", level, cur, next, nl.prev)
			}

			t := cl.typ
			if t < 1 || t > 5 {
				return fmt.Errorf("level %d node %d invalid type %d", level, cur, t)
			}
			nextType := 0
			if next != -1 {
				nextType = nl.typ
			}
			switch t {
			case 1:
				if next == -1 || nextType != 2 {
					return fmt.Errorf("level %d type1 at %d not followed by type2", level, cur)
				}
			case 2:
				if next != -1 && nextType != 1 && nextType != 3 {
					return fmt.Errorf("level %d type2 at %d followed by type%d", level, cur, nextType)
				}
			case 3:
				if next == -1 || nextType != 4 {
					return fmt.Errorf("level %d type3 at %d not followed by type4", level, cur)
				}
			case 4:
				if next == -1 || nextType != 5 {
					return fmt.Errorf("level %d type4 at %d not followed by type5", level, cur)
				}
			case 5:
				if next != -1 && nextType != 1 && nextType != 3 {
					return fmt.Errorf("level %d type5 at %d followed by type%d", level, cur, nextType)
				}
			}

			if level < s.depth {
				above := s.hasLevel(cur, level+1)
				wantAbove := t == 1 || t == 3
				if above != wantAbove {
					return fmt.Errorf("level %d node %d promotion mismatch: type=%d above=%v", level, cur, t, above)
				}
			}

			if next == -1 {
				seen[-1] = true
				break
			}
			if level == 1 {
				seenLevel1[next] = true
			}
			nv := s.n(next).value
			if havePrevValue && s.order(prevValue, nv) < 0 {
				return fmt.Errorf("level %d ordering violation before node %d", level, next)
			}
			prevValue, havePrevValue = nv, true
			cur = next
		}

		if seen[-1] != true {
			return fmt.Errorf("level %d does not reach stop sentinel", level)
		}
		if has := s.hasLevel(0, level); has != seen[0] {
			return fmt.Errorf("level %d start sentinel presence mismatch", level)
		}
		if has := s.hasLevel(-1, level); has != seen[-1] {
			return fmt.Errorf("level %d stop sentinel presence mismatch", level)
		}
		for idx := 1; idx < s.nextIndex; idx++ {
			has := s.nodes[idx].hasValue && level <= len(s.nodes[idx].levels)
			if has != seen[idx] {
				return fmt.Errorf("level %d reachability/presence mismatch at node %d: present=%v reachable=%v", level, idx, has, seen[idx])
			}
		}
	}

	if len(seenLevel1) != len(s.keyToIdx) {
		return fmt.Errorf("level1 reachability mismatch: %d != %d", len(seenLevel1), len(s.keyToIdx))
	}
	for idx := 1; idx < s.nextIndex; idx++ {
		if s.nodes[idx].hasValue && !seenLevel1[idx] {
			return fmt.Errorf("node %d unreachable at level1", idx)
		}
	}
	return nil
}

// DebugSignature returns a structural signature by user key, not allocator
// index. It exists for exhaustive state-space testing and diagnostics.
func (s *List[K, V]) DebugSignature(keyString func(K) string) string {
	parts := make([]string, 0, s.depth)
	name := func(i int) string {
		if i == 0 {
			return "S"
		}
		if i == -1 {
			return "T"
		}
		return keyString(s.idxToKey[i])
	}
	for level := 1; level <= s.depth; level++ {
		line := fmt.Sprintf("L%d:", level)
		for i := 0; ; i = s.l(i, level).next {
			l := s.l(i, level)
			line += fmt.Sprintf("%s/%d", name(i), l.typ)
			if l.next == -1 {
				line += ">T"
				break
			}
			line += ">"
		}
		parts = append(parts, line)
	}
	sort.Strings(parts)
	return fmt.Sprintf("D%d|%v", s.depth, parts)
}
