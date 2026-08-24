package verification

import "testing"

// count23ByLeaves counts ordered height-balanced 2-3 tree shapes with exactly
// leaves leaves. Munro-Papadakis-Sedgewick give a one-to-one correspondence
// between these trees and 1-2 deterministic skip-list structures; n skip-list
// keys correspond to n+1 leaves because of the boundary/sentinel intervals.
func count23ByLeaves(leaves int) uint64 {
	if leaves < 1 {
		return 0
	}
	// dp[h][n] = ordered 2-3 trees of exact height h with n leaves.
	// Height zero is one leaf. At positive height the root has 2 or 3
	// ordered children, all of exact height h-1.
	dp := make([][]uint64, 1)
	dp[0] = make([]uint64, leaves+1)
	dp[0][1] = 1
	total := uint64(0)
	for h := 0; ; h++ {
		if h >= len(dp) {
			break
		}
		if dp[h][leaves] != 0 {
			total += dp[h][leaves]
		}
		// A height-h tree has at least 2^h leaves, so once the minimum next
		// height exceeds leaves, no further terms can occur.
		if (1 << uint(h+1)) > leaves {
			break
		}
		prev := dp[h]
		next := make([]uint64, leaves+1)
		for n := 2; n <= leaves; n++ {
			var c uint64
			for a := 1; a < n; a++ {
				c += prev[a] * prev[n-a]
			}
			for a := 1; a < n-1; a++ {
				for b := 1; b < n-a; b++ {
					c += prev[a] * prev[b] * prev[n-a-b]
				}
			}
			next[n] = c
		}
		dp = append(dp, next)
	}
	return total
}

func TestKnownReachableCountsMatch23TreeEnumeration(t *testing.T) {
	// Independently obtained from exhaustive deterministic transition-graph runs.
	got := []uint64{
		1, 1, 1, 1, 2, 2, 3, 4, 5, 8, 14, 23, 32, 43, 63, 97, 149, 224, 332, 489,
		727, 1116, 1776, 2897, 4782, 7895, 12909,
	}
	for n, want := range got {
		all := count23ByLeaves(n + 1)
		if all != want {
			t.Fatalf("n=%d reachable=%d all 2-3 shapes=%d", n, want, all)
		}
	}
}
