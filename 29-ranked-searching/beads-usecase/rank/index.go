package rank

import (
	"fmt"
	"math"

	"verifiedskiplist/implementation/skiplist"
)

type rankedKey struct {
	Score float64
	ID    string
}

// Index exercises the actual optimized deterministic skip list as a maintained
// ranked secondary index. Higher scores sort first; ID is a stable tie-break.
type Index struct {
	list *skiplist.List[string, rankedKey]
	byID map[string]rankedKey
}

func NewIndex() *Index {
	order := func(a, b rankedKey) int {
		if a.Score > b.Score {
			return 1
		}
		if a.Score < b.Score {
			return -1
		}
		if a.ID < b.ID {
			return 1
		}
		if a.ID > b.ID {
			return -1
		}
		return 0
	}
	return &Index{list: skiplist.New[string, rankedKey](order), byID: map[string]rankedKey{}}
}

func (x *Index) Upsert(id string, score float64) {
	if math.IsNaN(score) {
		panic("rank: NaN score")
	}
	k := rankedKey{Score: score, ID: id}
	x.list.Insert(id, k)
	x.byID[id] = k
}

func (x *Index) Delete(id string) bool {
	if _, ok := x.byID[id]; !ok {
		return false
	}
	delete(x.byID, id)
	return x.list.Delete(id)
}

func (x *Index) Validate() error {
	if err := x.list.Validate(); err != nil {
		return fmt.Errorf("rank index: %w", err)
	}
	return nil
}

func (x *Index) IDs() []string {
	vals := x.list.Values()
	out := make([]string, len(vals))
	for i, v := range vals {
		out[i] = v.ID
	}
	return out
}
