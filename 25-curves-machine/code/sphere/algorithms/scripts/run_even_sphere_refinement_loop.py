#!/usr/bin/env python3
"""Exact overlap sweep plus structural statistics for even sphere quartics."""
from __future__ import annotations
import os

import json, pathlib, sys, time
import sympy as sp

ROOT=pathlib.Path(__file__).resolve().parents[2]
DATA_ROOT=pathlib.Path(os.environ.get('CURVES_MACHINE_DATA_ROOT', str(ROOT/'data')))
sys.path.insert(0,str(ROOT/"algorithms/src/core"))
import dihedral_ode_sphere as d
import even_sphere_quartic_factory as q


LINEAR_FAMILY=[(1,2,5),(0,1,3),(1,3,7),(-2,2,9)]


def operator_from_relation(z,degree=3,order=2):
    width=degree+1
    return [sp.factor(sum(z[width*k+j]*q.alpha**j for j in range(width)))
            for k in range(order+1)]


def exact_dihedral_linear(abc):
    a,b,c=abc; model=d.asymmetric_top(a,b,c)
    sa,sb,sc=sp.symbols("a b c")
    op=[-4*x.subs({sa:a,sb:b,sc:c})
        for x in q.dissertation_asymmetric_operator()]
    R=1/(d.lam**3*(d.alpha-c))
    residual=sp.factor(sum(a*x for a,x in zip(op,d.density_tower(model,2)))
        -d.time_derivative_over_lambda_dot(model,R))
    assert residual==0
    M,_,_=d.bounded_certificate_matrix(model,2,3,0,3)
    return {"status":"closed","operator":op,"R":R,
            "matrix_shape":list(M.shape),
            "G_shape":list(d.dissertation_kernel(model)["G"].shape)}


def linear_case(abc,zd):
    a,b,c=abc
    F=q.general_quartic([0,a,b,c,0,0,0,0,0,0],name=str(abc)).action_fiber()
    checkpoints=[]; closing=None
    for degree in (5,6):
        tick=time.monotonic()
        M,U,Xi=q.bounded_certificate_matrix(F,2,3,0,degree,3)
        null=M.nullspace()
        rel=[z for z in null if any(z[i] for i in range(12))]
        checkpoints.append({"v_degree":degree,"matrix_shape":list(M.shape),
            "rank":M.rank(),"nullity":len(null),"operator_relations":len(rel),
            "nonzeros":sum(bool(x) for x in M),
            "density":float(sum(bool(x) for x in M)/(M.rows*M.cols)),
            "seconds":time.monotonic()-tick})
        if rel:
            z=rel[0]; sub=dict(zip(U,list(z)))
            op=operator_from_relation(z)
            XiG=sp.factor(Xi.subs(sub))
            assert q.verify_operator_exact(F,op,XiG)==0
            closing=(op,XiG)
            break
    assert closing is not None and checkpoints[0]["operator_relations"]==0
    assert zd["status"]=="closed"
    opG,XiG=closing; opD=zd["operator"]
    ratios=[sp.cancel(x/y) for x,y in zip(opD,opG)]
    assert ratios[0]==ratios[1]==ratios[2]
    # lambda_dot=2*F_v*y/lambda; the resulting expression is even in lambda.
    XiD=sp.cancel((2*sp.diff(F,q.v)*q.y/d.lam*zd["R"]).subs(
        d.lam,sp.sqrt(q.u)))
    primitive_difference=q.reduce_on_curve(XiD-ratios[0]*XiG,F)
    assert primitive_difference==0
    return {"parameters":{"a":a,"b":b,"c":c},
        "general_checkpoints":checkpoints,
        "general_closing_v_degree":6,
        "dihedral_closing_lambda_degree":0,
        "dihedral_matrix_shape":zd["matrix_shape"],
        "dihedral_G_shape":zd["G_shape"],
        "operator_scale_dihedral_over_general":str(ratios[0]),
        "primitive_difference_mod_curve":str(primitive_difference),
        "operator_general":[str(x) for x in opG]}


def structural_case(rec):
    model=q.general_quartic([sp.Integer(x) for x in rec["coefficients"]],rec["name"])
    F=model.action_fiber(); p=sp.Poly(F,q.u)
    du=int(p.degree()); dv=int(sp.degree(F,q.v))
    disc=sp.factor(sp.discriminant(F,q.u)) if du>1 else sp.S.One
    reflection=sp.expand(F.subs(q.v,1-q.v)-F)==0
    lead=sp.factor(p.LC())
    return {"name":rec["name"],"stratum":rec["stratum"],
        "degree_u_F":du,"proven_quotient_u_max_degree":du-1,
        "degree_v_F":dv,"reflection_v_to_1_minus_v":reflection,
        "leading_u_coefficient":str(lead),
        "degree_v_discriminant_u":int(sp.degree(disc,q.v)) if disc!=0 else None,
        "discriminant_u":str(disc)}


def main():
    # Build the parallel reductions in separate phases.  Besides reducing peak
    # expression pressure, this makes accidental cross-method symbol aliasing
    # a tested failure rather than an invisible change in rank.
    dihedral={x:exact_dihedral_linear(x) for x in LINEAR_FAMILY}
    assert all(z["status"]=="closed" for z in dihedral.values())
    linear=[linear_case(x,dihedral[x]) for x in LINEAR_FAMILY]
    catalog=json.loads((DATA_ROOT/"examples/sphere_curves/even_quartic_catalog.json").read_text())
    structural=[structural_case(x) for x in catalog["models"]]
    out={"scope":"even powers of Jx,Jy,Jz only",
         "odd_power_symmetry_breaking":"deferred",
         "linear_exact_family":linear,"quartic_structural_catalog":structural,
         "empirical_bound_summary":{
             "linear_general_minimal_v_degree_observed":6,
             "linear_dihedral_minimal_lambda_degree_observed":0,
             "linear_samples":len(linear),
             "quartic_structural_samples":len(structural),
             "proven_u_bound":"deg_u(P)<deg_u(F)",
             "angular_support_bound_status":"empirical only; no theorem yet"}}
    path=DATA_ROOT/"examples/sphere_curves/even_sphere_refinement_stats.json"
    path.write_text(json.dumps(out,indent=2)+"\n")
    print("EVEN_SPHERE_REFINEMENT_PASS")
    print(f"linear_exact={len(linear)} structural_quartics={len(structural)}")
    print("linear_closure general_v=6 dihedral_lambda=0 all_cases")
    print(path)


if __name__=="__main__": main()
