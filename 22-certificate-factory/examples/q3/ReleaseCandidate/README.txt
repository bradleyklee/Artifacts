A120590 TERNATREES

Primary paper

A120590_Ternatrees.pdf
    A sixteen-page mathematical account of the ordered ternatree model,
    cycle-lemma count, coefficient and contour integrals, summed integral
    definition of A(x), shift reduction and recurrence, derivative reduction
    and differential equation, algebraic ansatz verification, relations among the formulas, reference
    pseudocode, comparison graphics, ranked bibliography, and exact SymPy
    implementation.

A120590_ternatree_human.tex
    XeLaTeX source for the primary paper. The source uses portable fallbacks
    for the TeX Gyre Pagella and Heros font names.

OEIS_A120590_PDF_EXTRACTION_GUIDE.md
    Page-by-page guide to the identities worth extracting from the PDF for an
    OEIS A120590 edit, including a ready-to-paste proposal and a list of
    formulas already present on OEIS that should not be duplicated.

proposed_oeis_update.txt
    Compact ready-to-paste OEIS field text.

Executable data

ternatree_q3.py
    Exact q=3 implementation. Run:

        python3 ternatree_q3.py 30

    The program derives the recurrence and differential equation, generates
    a(0) through a(30), and checks the kernel and certificate identities, integer recurrence
    divisions, cubic equation, and differential equation.

ternatree_one_page_crank.txt
    One-page pseudocode specification.

ternatree_reduction_matrices.txt
    The matrices G, U, V, J, the deformation G_x, and the common one-step
    lowering identity.

ternatree_pseudocode_mysteries.png
ternatree_sympy_resolutions.png
    Publication graphics comparing the pseudocode operations with their exact
    Python or SymPy realizations.

ternatree_a3_menagerie.txt
    ASCII list of all 19 ternatrees with three true leaves.

ternatree_poetry_digest.pdf
    The initial kanshi and the Kimi and Claude responses, with notes on the
    matrix imagery.

Machine-readable payload

.support/payload/A120590_certificate_payload.json
    Compact UTF-8 reading payload: plain-language claims, embedded
    pseudocode, exact matrices, recurrence and ODE data, semantic checks,
    reference metadata, and links to the full frozen factory evidence.

Supporting evidence

The hidden .support directory contains synchronized LaTeX sources,
deterministic graph renderers, raw matrix files, the frozen q=3 factory case,
certificates, referee material, exact run output, PDF QA, and checksums.
