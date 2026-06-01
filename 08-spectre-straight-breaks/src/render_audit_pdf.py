#!/usr/bin/env python3
from __future__ import annotations
import csv
import json
import subprocess
from collections import defaultdict
from pathlib import Path
from spectre_straight import ROOT

DATA = ROOT / 'data'; BUILD = ROOT / 'build'; DOCS = ROOT / 'docs'
BUILD.mkdir(exist_ok=True); DOCS.mkdir(exist_ok=True)
rows = list(csv.DictReader((DATA / 'straight_local_join_audit.csv').open(encoding='utf-8')))
summary = json.loads((DATA / 'straight_local_join_summary.json').read_text(encoding='utf-8'))
immediate = [row for row in rows if row['immediate'] == 'True']
groups = defaultdict(list)
for row in rows:
    groups[(row['local'], row['br'], row['post'], row['reason'])].append(row)
priority = {'image join': 0, 'left word': 1, 'right word': 2}
grouped = sorted(groups.items(), key=lambda item: (priority[item[0][0]], item[0][1], -len(item[1]), item[0][2]))

def M(text: str) -> str:
    return '$' + text + '$'

def immediate_table(chunk):
    out = [r'{\small\renewcommand{\arraystretch}{1.62}', r'\begin{tabularx}{\textwidth}{@{}>{\raggedright\arraybackslash}p{1.62in} >{\raggedright\arraybackslash}p{2.86in} X@{}}', r'\toprule', r'\textbf{Pre-image join} & \textbf{Post-image words} & \textbf{Positioned until immediate break}\\', r'\midrule']
    for row in chunk:
        out.append(M(row['pre']) + ' & ' + M(row['post']) + ' & ' + M(row['broken']) + r'\\[4pt]')
    out += [r'\bottomrule', r'\end{tabularx}}']
    return '\n'.join(out)

def group_table(chunk):
    out = [r'{\footnotesize\renewcommand{\arraystretch}{1.55}', r'\begin{tabularx}{\textwidth}{@{}p{0.25in}p{0.36in}p{0.48in}p{2.42in}p{2.35in}X@{}}', r'\toprule', r'\textbf{\#} & \textbf{N} & \textbf{Break} & \textbf{Post-image pattern} & \textbf{Required / available} & \textbf{Representative pre-images}\\', r'\midrule']
    for number, ((location, br, post, reason), members) in chunk:
        tag = {'image join': 'J', 'left word': 'L', 'right word': 'R'}[location]
        examples = '; '.join(M(row['pre']) for row in members[:2])
        out.append(f"{number} & {len(members)}{tag} & {M(br)} & {M(post)} & {M(reason)} & {examples}" + r'\\[3pt]')
    out += [r'\bottomrule', r'\end{tabularx}}']
    return '\n'.join(out)

numbered = list(enumerate(grouped, start=1))
tex = r'''\documentclass[10pt]{article}
\usepackage[letterpaper,landscape,margin=0.33in]{geometry}
\usepackage{amsmath,amssymb,booktabs,tabularx,array,xcolor}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype}
\setlength{\parindent}{0pt}
\setlength{\tabcolsep}{3pt}
\pagestyle{plain}
\begin{document}
\begin{center}
{\Large\bfseries Spectre Figure 5.1: Straight Positioned Join Audit}\\[-1pt]
{\normalsize Immediate breakers first; compressed complete classification after}\\[5pt]
\end{center}
{\small Straight-only catalogue: $76$ positioned path records; $288$ valid pre-image joins; $0$ non-breaking inflated joins. There are $25$ immediate breaks. Every immediate break has the same condition:
\[
\text{need }(\varepsilon^{-},\,1:\varepsilon^{+})\qquad
\text{available straight record: }\Phi_{4,3}.
\]}
\vspace{-5pt}
\section*{Immediate breakers (1 of 2)}
''' + immediate_table(immediate[:12]) + r'''
\newpage
\section*{Immediate breakers (2 of 2)}
''' + immediate_table(immediate[12:]) + r'''
\vfill
{\footnotesize\textbf{Key for pages 3-5.} J = break at the join between the parenthesized image words; L = break inside the left image word; R = break inside the right image word. The grouped tables cover all $288$ rows; $N$ gives the number of pre-image joins represented by each row.}
\newpage
\section*{Complete grouped classification (1 of 3)}
''' + group_table(numbered[:16]) + r'''
\newpage
\section*{Complete grouped classification (2 of 3)}
''' + group_table(numbered[16:32]) + r'''
\newpage
\section*{Complete grouped classification (3 of 3)}
''' + group_table(numbered[32:]) + r'''
\end{document}
'''
tex_path = BUILD / 'spectre_straight_join_audit_5page.tex'; tex_path.write_text(tex, encoding='utf-8')
subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-output-directory', str(BUILD), str(tex_path)], check=True, stdout=subprocess.DEVNULL)
(BUILD / 'spectre_straight_join_audit_5page.pdf').replace(DOCS / 'spectre_straight_join_audit_5page.pdf')
print('wrote', DOCS / 'spectre_straight_join_audit_5page.pdf')

# Keep the packaged build directory free of LaTeX intermediates.
for suffix in ['.aux', '.log']:
    artifact = BUILD / (tex_path.stem + suffix)
    if artifact.exists():
        artifact.unlink()
