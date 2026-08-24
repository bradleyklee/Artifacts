package model

// Task is deliberately declarative. RequiredAll is hidden from the ranker and
// is used only by the evaluator as a deterministic sufficiency certificate.
// Search is the literal binary discovery predicate for the deterministic tier;
// zero-prior agent trials choose their own search strings separately.
type Task struct {
	ID          string   `json:"id"`
	Difficulty  string   `json:"difficulty"`
	Prompt      string   `json:"prompt"`
	Search      string   `json:"search,omitempty"`
	RequiredAll []string `json:"required_all"`
}

type TrialResult struct {
	TaskID             string   `json:"task_id"`
	Ordering           string   `json:"ordering"`
	PageSize           int      `json:"page_size"`
	SuccessAtMatch     int      `json:"success_at_match"`
	SuccessPage        int      `json:"success_page"`
	FirstEssential     int      `json:"first_essential_match"`
	EssentialMatchRank []int    `json:"essential_match_ranks"`
	RecordsScanned     int      `json:"records_scanned"`
	MatchesReturned    int      `json:"matches_returned"`
	BytesBeforeDone    int      `json:"summary_bytes_before_success"`
	MatchedIDs         []string `json:"matched_ids,omitempty"`
}
