Start with the square itself, inside the ordinary polynomial ring $K[x]$:
$(x+\delta)^2-x^2=2x\delta+\delta^2$. In calculus we divide by
$\delta$ and send $\delta\to0$. The scalar term disappears and we
recover $\partial_x(x^2)=2x$. But in the discrete case the step is fixed
at $\delta=1$, so the scalar term remains: $(x+1)^2-x^2=2x+1$. This is
completing the square in reverse. Asking when the gap is an odd square,
$2x+1=(2n+1)^2$, gives $x=2n^2+2n=4T_n$, hence

$$
(2n+1)^2+(4T_n)^2=(4T_n+1)^2.
$$

Now pass from $K[x]$ to the differential ring $K[\partial_n,T_n]$.
Equivalently, $K[\partial_n,T_n]=K[\partial_n,n]$, since
$[\partial_n,T_n]=\partial_nT_n=n+\frac12$. Here
$T_{n+1}-T_n=n+1=\partial_nT_n+\frac12$. Meanwhile every square is the
sum of two consecutive triangular numbers:
$T_{n+1}+T_n=(n+1)^2=(T_{n+1}-T_n)^2$. Therefore

$$
T_{n+1}^2-T_n^2
=(T_{n+1}-T_n)(T_{n+1}+T_n)
=(T_{n+1}-T_n)^3
=\left(\partial_nT_n+\frac12\right)^3.
$$

So consecutive triangular squares differ by consecutive cubes. This is
the finite-difference form of Nicomachus's theorem.