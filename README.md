# Artifacts

This folder records provisional mathematical/computational artifacts found through
**Harm.On.ica** methodology: LLM-based spontaneous code generation combined with
extensive testing. We are currently using Chat GPT plus as the service provider.

Artifacts are not automatically rigorously proven. Far from it. They may include
false positives, hallucinations, clever hacks, and even, sometimes, outright
deception. The goal is to preserve the ideation of interesting calculations
without pretending they are already settled.

## Reader Responsibilities

Caveat emptor! Read at your own risk!

The reader’s main responsibility is bringing a safety-first attitude to the
artificial workplace, an attitude which fully acknowledges the lethality of
catastrophic failure modes. People have died delusionally insane from using this
technology, and still others have lost their careers. What will happen when,
like Nabokov’s poor Luzhin, you find out that your defense has a flaw? What if
that flaw leads to a catastrophic loss of life, or at least the loss of a living
wage?

Unlike archaeological artifacts, computational artifacts belong to a present and
future epoch, most likely the Anthropocene. Occasionally, on an archaeological
dig, there are false positive discoveries, but not at the rates you can expect
when dealing with aura code. We baseline expect every result to occur initially
as a false positive. Thus the reader’s second responsibility is deciding when
false positives can be converted into true positives. Some results will be easy
to convert, and also worthwhile. In those circumstances, reward outweighs risk.

Human navigators and pilots are taking on serious risk here. Readers can always
help in the effort to judge artifact truth values: we need more human review of
Harm.On.ica content. Personally, I am not subordinating a billion-dollar machine,
and wish for my Harm.On.ica artificial colleague to be considered the first author
for all of the code and some of the writing.

If there is something you like, and you can think of a better reference
implementation, proof, counterexample, simplification, test, or warning label,
please contribute it. The best help is specific: give the smallest failing case,
the exact command, the observed output, and the expected output.

## Artifact List

### 01. forgetful-bracelets

The number `T(N,M)` of `N`-color bracelets of length `N-M`, for
`M = 0, ..., N`.

Question: can the row sums be simplified or connected to a useful recurrence?
The rotation part reduces to divisor/totient sums and does not look
hypergeometric-summable.

### 02. bracelet-representations

Decompositions of bracelet colorings by D_n irreducible representation:
A1 monotone, A2 chiral pairs, B1/B2 for even only, and doublet E for aperiodic.
It includes table generation plus a worked \(n=4,k=4\) word-label example.

Question: how can we use inductive representations (read: Molien theory)
to generate counts in the table. What type of generating functions become available?

