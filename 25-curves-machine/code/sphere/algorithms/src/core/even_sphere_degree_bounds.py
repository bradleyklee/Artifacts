#!/usr/bin/env python3
"""Genus and Picard-Fuchs order bounds for coordinatewise-even sphere curves."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class EvenSphereDegreeBound:
    degree_squared_variables: int

    @property
    def degree_in_J(self): return 2*self.degree_squared_variables

    @property
    def base_genus(self):
        d=self.degree_squared_variables
        return (d-1)*(d-2)//2

    @property
    def generic_branch_points(self): return 4*self.degree_squared_variables

    @property
    def quotient_genus(self):
        d=self.degree_squared_variables
        return d*d-d+1

    @property
    def gauss_manin_rank(self): return 2*self.quotient_genus

    @property
    def generic_period_ode_order_ceiling(self): return self.gauss_manin_rank

    def record(self):
        return {"degree_in_squared_variables":self.degree_squared_variables,
                "degree_in_J":self.degree_in_J,
                "base_plane_curve_genus":self.base_genus,
                "generic_simple_branch_points":self.generic_branch_points,
                "even_quotient_curve_genus":self.quotient_genus,
                "gauss_manin_rank":self.gauss_manin_rank,
                "generic_period_ode_order_ceiling":self.generic_period_ode_order_ceiling}


def assumptions():
    return ["H restricted to X+Y+Z=L2 is a smooth degree-d plane curve",
            "intersections with X=0,Y=0,Z=0 and infinity are transverse",
            "period differential represents a second-kind/compact de Rham class",
            "special symmetry or singularity may lower, never raise, the generic rank"]


def self_check():
    expected={1:(1,2),2:(3,6),3:(7,14),4:(13,26)}
    for d,(g,r) in expected.items():
        b=EvenSphereDegreeBound(d)
        assert (b.quotient_genus,b.gauss_manin_rank)==(g,r)
    print("EVEN_SPHERE_DEGREE_BOUNDS_PASS",expected)


if __name__=="__main__": self_check()
