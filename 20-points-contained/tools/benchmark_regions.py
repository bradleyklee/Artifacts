#!/usr/bin/env python3
import os
import statistics
import subprocess

RADII=(1,2,4,8,16,32,47,100,200,300)

def timed(command,threads=None):
    env=os.environ.copy()
    if threads is not None: env["OMP_NUM_THREADS"]=str(threads)
    fields=subprocess.check_output(command,text=True,env=env).split()
    return int(fields[1]),float(fields[-1])

def median(command,threads,n):
    repeats=15 if n<=47 else (5 if n<=100 else 3)
    runs=[timed(command,threads) for _ in range(repeats)]
    return runs[0][0],statistics.median(t for _,t in runs)

print("n,row_s,regions_1t_s,regions_4t_s,sweep_s,row_over_sweep")
for n in RADII:
    rc,rt=median(["./a295344","row",str(n),str(n)],None,n)
    sc,st=median(["./a295344_regions_serial",str(n),str(n)],None,n)
    pc,pt=median(["./a295344_regions_omp",str(n),str(n)],4,n)
    wc,wt=median(["./a295344_sweep",str(n),str(n)],None,n)
    if n<=47: assert rc==sc==pc==wc
    print(f"{n},{rt:.9f},{st:.9f},{pt:.9f},{wt:.9f},{rt/wt:.3f}")
