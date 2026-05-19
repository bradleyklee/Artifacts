Start with the square itself: $(x+\delta)^2-x^2=2x\delta+\delta^2$.
In calculus we divide by $\delta$ and send $\delta\to0$. The scalar
term disappears and we recover $\partial_x(x^2)=2x$. More generally,
the differential ring $K[\partial_x,x]$ is graded by total term weight:
$\partial_x$ lowers degree, $x$ raises degree, and for bounded exponents
grade layers close through bounded zero sums. This is the setting for
differential calculus on polynomials, which is useful to the sciences.

In the discrete case the step is fixed at $\delta=1$, so the scalar term
remains: $(x+1)^2-x^2=2x+1$. We are confined to a sub-ring $K[x]$, with
easier grading. The identity is essentially just completing the square
in reverse. Asking when the gap is an odd square, $2x+1=(2n+1)^2$, gives
$x=2n^2+2n=4T_n$, hence

$$
(2n+1)^2+(4T_n)^2=(4T_n+1)^2.
$$

Rather than shifting the function value, it is more natural here to shift
the index value. For triangular numbers,

$$
T_{n+1}-T_n=n+1=\partial_nT_n+\frac12.
$$

Meanwhile every square is the sum of two consecutive triangular numbers:

$$
T_{n+1}+T_n=(n+1)^2=(T_{n+1}-T_n)^2.
$$

Therefore

$$
T_{n+1}^2-T_n^2
=(T_{n+1}-T_n)(T_{n+1}+T_n)
=(T_{n+1}-T_n)^3
=\left(\partial_nT_n+\frac12\right)^3.
$$

So consecutive triangular squares differ by consecutive cubes. This is the
finite-difference form of Nicomachus's theorem.