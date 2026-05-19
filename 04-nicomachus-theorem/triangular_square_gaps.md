Start with the square itself: \((x+h)^2-x^2=2xh+h^2\). In calculus we divide by \(h\) and send \(h\to0\), so the correction term disappears and we recover \(\partial_x(x^2)=2x\). More generally, \(K[\partial_x,x]\) is graded by total term weight: \(\partial_x\) lowers degree, \(x\) raises degree, and for bounded exponents the grade layers close through bounded zero sums. But in the discrete square-gap case the step is fixed at \(h=1\), so the correction term remains: \((x+1)^2-x^2=2x+1\). This is completing the square in reverse. Asking when the gap is an odd square, \(2x+1=(2n+1)^2\), gives \(x=2n^2+2n=4T_n\), hence

\[
(2n+1)^2+(4T_n)^2=(4T_n+1)^2.
\]

Rather than shifting the function value, it is more natural here to shift the index value. For triangular numbers,

\[
T_{n+1}-T_n=n+1=\partial_nT_n+\frac12.
\]

Meanwhile every square is the sum of two consecutive triangular numbers:

\[
T_{n+1}+T_n=(n+1)^2=(T_{n+1}-T_n)^2.
\]

Therefore

\[
T_{n+1}^2-T_n^2
=(T_{n+1}-T_n)(T_{n+1}+T_n)
=(T_{n+1}-T_n)^3
=\left(\partial_nT_n+\frac12\right)^3.
\]

So consecutive triangular squares differ by consecutive cubes. This is the finite-difference form of Nicomachus's theorem.
