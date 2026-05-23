import Mathlib

/-!
# Gap dominance proof for interval sums

This file proves the structural, non-Catalan-specific part of the argument.

It does not try to prove the Catalan growth estimates.  Instead it assumes
the four gap estimates that follow from positivity plus strong exponential
decay of the reciprocal sequence.

For Catalan reciprocals, the intended `b` is

  b n = 1 / C_n.

Then the hard arithmetic work is to prove `GapHyp b`.
Once that is available, the theorem below proves that ordinary interval
sums are injective in `(j,k)`.
-/

open scoped BigOperators

namespace GapDominance

noncomputable section

/-- Finite interval sum of a sequence `b`. -/
def intervalSum (b : ℕ → ℝ) (j k : ℕ) : ℝ :=
  ∑ i ∈ Finset.Icc j k, b i

/--
Lean-friendly assumptions for the four-endpoint gap proof.

`first_le` says an interval contains at least its first term.

`later_le_tail` says an interval beginning later than `j` is contained in
the finite tail after `j`.

`tail_lt` is the real "strong exponential growth" hypothesis:
the tail after `j` is smaller than the term at `j`.

`strict_right` says extending the right endpoint strictly increases the sum.
-/
structure GapHyp (b : ℕ → ℝ) : Prop where
  first_le :
    ∀ j k : ℕ, 2 ≤ j → j ≤ k →
      b j ≤ intervalSum b j k
  later_le_tail :
    ∀ j₁ j₂ k₂ : ℕ, 2 ≤ j₁ → j₁ < j₂ →
      intervalSum b j₂ k₂ ≤ intervalSum b (j₁ + 1) k₂
  tail_lt :
    ∀ j k : ℕ, 2 ≤ j → j < k →
      intervalSum b (j + 1) k < b j
  strict_right :
    ∀ j k₁ k₂ : ℕ, 2 ≤ j → j ≤ k₁ → k₁ < k₂ →
      intervalSum b j k₁ < intervalSum b j k₂

variable {b : ℕ → ℝ}

/--
If the starting indices are different, the interval sums are different.

This is the `a < b ≤ c < d` / gap-dominance comparison:
the later-starting interval lies inside the tail after the earlier start,
while the earlier-starting interval contains its first term.
-/
lemma start_ne_interval_ne
    (H : GapHyp b)
    {j₁ k₁ j₂ k₂ : ℕ}
    (hj₁ : 2 ≤ j₁) (hjk₁ : j₁ ≤ k₁)
    (hj₂ : 2 ≤ j₂) (hjk₂ : j₂ ≤ k₂)
    (hstart : j₁ ≠ j₂) :
    intervalSum b j₁ k₁ ≠ intervalSum b j₂ k₂ := by
  intro h_eq
  rcases lt_or_gt_of_ne hstart with hlt | hgt
  · -- Case `j₁ < j₂`.
    have lower :
        b j₁ ≤ intervalSum b j₁ k₁ :=
      H.first_le j₁ k₁ hj₁ hjk₁
    have upper_le :
        intervalSum b j₂ k₂ ≤ intervalSum b (j₁ + 1) k₂ :=
      H.later_le_tail j₁ j₂ k₂ hj₁ hlt
    have j₁_lt_k₂ : j₁ < k₂ :=
      lt_of_lt_of_le hlt hjk₂
    have upper_lt :
        intervalSum b j₂ k₂ < b j₁ :=
      lt_of_le_of_lt upper_le (H.tail_lt j₁ k₂ hj₁ j₁_lt_k₂)
    linarith
  · -- Case `j₂ < j₁`, symmetric.
    have lower :
        b j₂ ≤ intervalSum b j₂ k₂ :=
      H.first_le j₂ k₂ hj₂ hjk₂
    have upper_le :
        intervalSum b j₁ k₁ ≤ intervalSum b (j₂ + 1) k₁ :=
      H.later_le_tail j₂ j₁ k₁ hj₂ hgt
    have j₂_lt_k₁ : j₂ < k₁ :=
      lt_of_lt_of_le hgt hjk₁
    have upper_lt :
        intervalSum b j₁ k₁ < b j₂ :=
      lt_of_le_of_lt upper_le (H.tail_lt j₂ k₁ hj₂ j₂_lt_k₁)
    linarith

/--
Main structural theorem.

Under the gap-dominance hypotheses, ordinary interval sums are injective:
if

  ∑_{i=j₁}^{k₁} b i = ∑_{i=j₂}^{k₂} b i

and `2 ≤ j₁ ≤ k₁`, `2 ≤ j₂ ≤ k₂`, then `(j₁,k₁) = (j₂,k₂)`.
-/
theorem intervalSum_injective
    (H : GapHyp b)
    {j₁ k₁ j₂ k₂ : ℕ}
    (hj₁ : 2 ≤ j₁) (hjk₁ : j₁ ≤ k₁)
    (hj₂ : 2 ≤ j₂) (hjk₂ : j₂ ≤ k₂)
    (h_eq : intervalSum b j₁ k₁ = intervalSum b j₂ k₂) :
    j₁ = j₂ ∧ k₁ = k₂ := by
  have hj_eq : j₁ = j₂ := by
    by_contra hne
    exact start_ne_interval_ne H hj₁ hjk₁ hj₂ hjk₂ hne h_eq
  subst hj_eq

  have hk_eq : k₁ = k₂ := by
    rcases lt_trichotomy k₁ k₂ with hlt | heq | hgt
    · have hlt_sum :
          intervalSum b j₁ k₁ < intervalSum b j₁ k₂ :=
        H.strict_right j₁ k₁ k₂ hj₁ hjk₁ hlt
      linarith
    · exact heq
    · have hlt_sum :
          intervalSum b j₁ k₂ < intervalSum b j₁ k₁ :=
        H.strict_right j₁ k₂ k₁ hj₁ hjk₂ hgt
      linarith

  exact ⟨rfl, hk_eq⟩

end

end GapDominance
