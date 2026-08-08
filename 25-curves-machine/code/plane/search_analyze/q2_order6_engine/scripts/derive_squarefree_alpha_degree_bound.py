#!/usr/bin/env python3
"""Safe alpha-degree bounds for the gauge-fixed squarefree quartic relation matrix.

Assumptions:
- quartic E is monic up to a nonzero rational constant in p;
- source support B_r=6r-3;
- p-reduced primitive basis has p-degree 0..3 and p+q<=B_r;
- the constant primitive kernel is gauged out;
- at the first relation the gauge-fixed combined matrix has nullity one.

The exact-image columns have alpha-degree <=2.  The derivative column j has
alpha-degree <= floor((6r-4j)/4)=floor(3r/2)-j.  A polynomial null vector is
formed from signed maximal minors; its coordinate degree is bounded by the sum
of the degrees of the columns retained in the corresponding minor.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def record(r:int):
    B=6*r-3
    source_columns=4*(B+1)-6          # 24r-14, including constant kernel
    gauge_source=source_columns-1     # 24r-15
    wd=[(3*r)//2-j for j in range(r+1)]
    S=sum(wd)
    primitive_coord=2*(gauge_source-1)+S
    operator_coords=[2*gauge_source+S-d for d in wd]
    uniform=max([primitive_coord]+operator_coords)
    return {
        'order':r,
        'support_bound':B,
        'source_columns_including_kernel':source_columns,
        'gauge_fixed_source_columns':gauge_source,
        'derivative_column_alpha_degree_bounds':wd,
        'sum_derivative_column_degree_bounds':S,
        'primitive_coordinate_degree_bound':primitive_coord,
        'operator_coordinate_degree_bounds':operator_coords,
        'uniform_kernel_coordinate_degree_bound':uniform,
        'safe_projective_interpolation_samples':2*uniform+1,
    }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--max-order',type=int,default=9);ap.add_argument('--output',type=Path)
    ns=ap.parse_args();data={'status':'SAFE_DEGREE_BOUND','scope':'squarefree quartic branch under the stated rank/nullity assumptions','records':[record(r) for r in range(1,ns.max_order+1)]}
    text=json.dumps(data,indent=2)+'\n'
    if ns.output:ns.output.write_text(text)
    print(text,end='')
if __name__=='__main__':main()
