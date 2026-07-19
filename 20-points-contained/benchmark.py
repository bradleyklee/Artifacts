#!/usr/bin/env python3
import subprocess
import statistics

RADII=(1,2,3,4,5,8,12,16,24,32,48,64,96)

def run(method,n):
    fields=subprocess.check_output(
        ["./a295344",method,str(n),str(n)],text=True).split()
    return int(fields[1]),float(fields[4])

def median_run(method,n):
    repeats=15 if n<=16 else (5 if n<=64 else 3)
    runs=[run(method,n) for _ in range(repeats)]
    assert len({count for count,_ in runs})==1
    return runs[0][0],statistics.median(t for _,t in runs)

print("n,row_count,row_seconds,flood_count,flood_seconds,ratio_flood_over_row")
for n in RADII:
    rc,rt=median_run("row",n)
    fc,ft=median_run("flood",n)
    assert rc==fc
    print(f"{n},{rc},{rt:.9f},{fc},{ft:.9f},{ft/rt:.3f}")
