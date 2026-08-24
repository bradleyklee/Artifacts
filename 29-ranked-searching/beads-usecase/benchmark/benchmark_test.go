package benchmark

import (
	"testing"
	"verifiedskiplist/beads-usecase/model"
)

func TestValidateTasksRejectsPriorLeak(t *testing.T) {
	x := []Task{{ID: "x", Prompt: "run bd secret", Search: "foo", Checkpoints: []Checkpoint{{ID: "c", EvidenceAny: []string{"bd secret"}}}}}
	if ValidateTasks(x) == nil {
		t.Fatal("expected leak rejection")
	}
}

func TestFlatTrajectoryResolvesOnlyAfterRecall(t *testing.T) {
	tasks := []Task{{ID: "x", Prompt: "repair it", Search: "repair", Checkpoints: []Checkpoint{{ID: "c1", EvidenceAny: []string{"secret command"}}}}}
	if err := ValidateTasks(tasks); err != nil {
		t.Fatal(err)
	}
	mem := []model.Memory{{ID: "a", Title: "A repair overview", Body: "nothing yet"}, {ID: "b", Title: "Z repair command", Body: "use secret command"}}
	tr := Run(tasks[0], mem, "alphabetical", "flat")
	if !tr.Success || tr.BodiesRecalled != 2 {
		t.Fatalf("got %+v", tr)
	}
	if tr.Events[1].KnowledgePct != 0 {
		t.Fatalf("first recall should stay 0, got %v", tr.Events[1].KnowledgePct)
	}
}

func TestGuidedRefOrderingDoesNotReadBody(t *testing.T) {
	task := Task{ID: "x", Prompt: "find sync repair", Search: "sync", Checkpoints: []Checkpoint{{ID: "c", EvidenceAny: []string{"magic answer"}}}}
	mem := []model.Memory{
		{ID: "seed", Title: "sync hub", Body: "hub", References: []model.Reference{{TargetID: "noise"}, {TargetID: "good"}}},
		{ID: "noise", Title: "unrelated", Body: "magic answer"},
		{ID: "good", Title: "sync repair", Body: "also magic answer"},
	}
	tr := Run(task, mem, "outdegree", "guided-dfs")
	if !tr.Success {
		t.Fatal("expected success")
	}
	if len(tr.Events) < 3 || tr.Events[2].ToID != "good" {
		t.Fatalf("guided edge order wrong: %+v", tr.Events)
	}
}
