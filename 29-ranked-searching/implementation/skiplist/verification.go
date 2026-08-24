package skiplist

import (
	"fmt"
	"sort"
)

// SetVerificationTrace installs an optional event hook used by the external
// verification suite to prove closure-branch coverage. Passing nil disables it.
// It is intentionally not part of skip-list semantics.
func (s *List[K, V]) SetVerificationTrace(trace func(string)) {
	s.trace = trace
}

// CloneForVerification returns a deep structural clone. It exists so the
// external verification suite can explore the transition graph without
// depending on private representation fields or replaying operation history.
func (s *List[K, V]) CloneForVerification() *List[K, V] {
	c := &List[K, V]{
		depth:     s.depth,
		order:     s.order,
		head:      node[V]{levels: append([]link(nil), s.head.levels...)},
		tail:      node[V]{levels: append([]link(nil), s.tail.levels...)},
		nodes:     make([]node[V], len(s.nodes)),
		nextIndex: s.nextIndex,
		missing:   append([]int(nil), s.missing...),
		keyToIdx:  make(map[K]int, len(s.keyToIdx)),
		idxToKey:  append([]K(nil), s.idxToKey...),
	}
	for idx := 1; idx < len(s.nodes); idx++ {
		n := s.nodes[idx]
		c.nodes[idx] = node[V]{
			value:    n.value,
			hasValue: n.hasValue,
			levels:   append([]link(nil), n.levels...),
		}
	}
	for k, v := range s.keyToIdx {
		c.keyToIdx[k] = v
	}
	return c
}

// ShapeSignature returns the structure with user nodes named only by their
// rank on the bottom level. It deliberately ignores keys, values, and allocator
// indices, so independently reached representations of the same ordered 1-2
// structure have the same signature.
func (s *List[K, V]) ShapeSignature() string {
	rank := make(map[int]int, len(s.keyToIdx))
	if s.depth > 0 {
		r := 0
		for i := s.l(0, 1).next; i != -1; i = s.l(i, 1).next {
			rank[i] = r
			r++
		}
	}
	parts := make([]string, 0, s.depth)
	name := func(i int) string {
		if i == 0 {
			return "S"
		}
		if i == -1 {
			return "T"
		}
		return fmt.Sprint(rank[i])
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

// CorruptForVerification deliberately violates one named representation
// invariant. It is used only to prove that Validate rejects known corruptions.
func (s *List[K, V]) CorruptForVerification(kind string) error {
	if s.depth == 0 {
		return fmt.Errorf("verification corruption %q needs a nonempty list", kind)
	}
	switch kind {
	case "backlink":
		first := s.l(0, 1).next
		if first == -1 {
			return fmt.Errorf("no first node")
		}
		s.l(first, 1).prev = -99
	case "type":
		s.l(0, 1).typ = 2
	case "tower":
		if s.depth < 2 {
			return fmt.Errorf("no level 2")
		}
		promoted := 0
		for i := s.l(0, 1).next; i != -1; i = s.l(i, 1).next {
			if s.hasLevel(i, 2) {
				promoted = i
				break
			}
		}
		if promoted == 0 {
			return fmt.Errorf("no promoted real node")
		}
		s.n(promoted).levels[1] = link{}
	case "orphan":
		idx := s.nextIndex
		s.ensureSlot(idx)
		var zero V
		s.nodes[idx] = node[V]{value: zero, hasValue: true, levels: make([]link, 1)}
		s.nextIndex++
	case "ordering":
		a := s.l(0, 1).next
		if a == -1 {
			return fmt.Errorf("no first node")
		}
		b := s.l(a, 1).next
		if b == -1 {
			return fmt.Errorf("need two nodes")
		}
		s.n(a).value, s.n(b).value = s.n(b).value, s.n(a).value
	default:
		return fmt.Errorf("unknown verification corruption %q", kind)
	}
	return nil
}
