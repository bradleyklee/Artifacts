// Generated comparison input for elliptic_must_have.
// Pierre Lairez attribution: Periods/Rham-Koszul/Picard-Fuchs machinery,
// https://github.com/lairez/periods ; Math. Comp. 85 (2016), 1719-1752.
// Research case and action-period normalization: Bradley Klee.

spec := GetEnv("PERIODS_SPEC");
require #spec gt 0: "Set PERIODS_SPEC to periods/src/PF.spec";
AttachSpec(spec);
SetVerbose("User2", true);
SetAssertions(2);

A<alpha,p,q> := FunctionField(Rationals(), 3);
E := p^2 + q^2 + (q^3 - 3*p^2*q) + (q^2 - 3*p^2)^2/4;

// Poincare-residue bridge:
// rho=(2H)_p=2H_p; Res_{2H=alpha} 2 dp dq/(2H-alpha)
// equals 2 dq/rho = dq/H_p.
f := 2/(E-alpha);

printf "CASE elliptic_must_have KNOWN_ORDER UNKNOWN\n";
for r in [1..4] do
    printf "TRY_R %o\n", r;
    time L := Periods(f : r := r);
    printf "RESULT_R %o OPERATOR %o\n", r, L;
    printf "RESULT_R %o ORDER %o\n", r, Degree(L);
end for;

// The public interface accepts "cert", but currently returns only L.
// This run is retained because it exercises the certificate-carrying reducer.
time Lcertpath := Periods(f : r := 2, variant := {"cert"});
printf "CERT_PATH_OPERATOR %o\n", Lcertpath;
