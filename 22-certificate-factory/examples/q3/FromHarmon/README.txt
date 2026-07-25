A120590 TERNATREES

Primary paper

A120590_Ternatrees.pdf
    A thirteen-page mathematical account of the ordered ternatree model,
    coefficient integrals, the summed integral definition of A(x), the
    algebraic generating function, a one-page shift reduction and recurrence,
    direct differential reduction, differential equation, pseudocode, and exact
    SymPy implementation. The algebraic equation is derived from the integral
    definition using the local inverse of rho. The paper compares the fixed
    reduction matrix G with G_x = G - x*diag(I_3,0).

Executable data

ternatree_q3.py
    Exact q=3 implementation. Run:

        python3 ternatree_q3.py 30

    The program derives the recurrence and differential equation, generates
    a(0) through a(30), and checks the kernel identity, integer recurrence
    divisions, cubic equation, and differential equation.

ternatree_one_page_crank.txt
    One-page pseudocode specification.

ternatree_reduction_matrices.txt
    The matrices G, U, V, J, the deformation G_x, and the common one-step
    lowering identity.

ternatree_pseudocode_mysteries.png
ternatree_sympy_resolutions.png
    Publication graphics. The first tree displays the fifteen algebraic
    operations named but not defined by the pseudocode. The second occupies
    the same rows with their exact Python or SymPy realizations.

ternatree_a3_menagerie.txt
    ASCII list of all 19 ternatrees with three true leaves.

ternatree_poetry_digest.pdf
    The initial kanshi and the Kimi and Claude responses, with notes on the
    matrix imagery.

proposed_oeis_update.txt
    Draft text for OEIS A120590.

Supporting evidence

The hidden .support directory contains the LaTeX sources, deterministic graph
renderer, raw matrix files, frozen q=3 factory case, certificates, independent
translations, exact checks, and checksums.
