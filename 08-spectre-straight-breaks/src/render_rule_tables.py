#!/usr/bin/env python3
from __future__ import annotations
import csv
import subprocess
from collections import defaultdict
from pathlib import Path
from spectre_straight import ROOT, NAMES, TEX_SYMBOL, EDGE_TEX, parse_mark_ascii

DATA = ROOT / 'data'
BUILD = ROOT / 'build'
DOCS = ROOT / 'docs'
BUILD.mkdir(exist_ok=True); DOCS.mkdir(exist_ok=True)

def edge_tex(text: str) -> str:
    edge, sign = parse_mark_ascii(text)
    base = EDGE_TEX[edge]
    return base if sign == '1' else rf'{base}^{{{sign}}}'

def state_tex(tile: str, n: str, m: str | None = None) -> str:
    sub = n if m is None else f'{n},{m}'
    return rf'{TEX_SYMBOL[tile]}_{{{sub}}}'

def word_tex(word: str) -> str:
    terms = []
    for token in word.split():
        tile, n = token.rsplit('_', 1)
        terms.append(state_tex(tile, n))
    return r'\;'.join(terms)

edge_rows = defaultdict(list)
with (DATA / 'figure_4_2_edge_dictionary.csv').open(encoding='utf-8') as handle:
    for row in csv.DictReader(handle):
        edge_rows[row['tile']].append(row)
records = defaultdict(list)
with (DATA / 'straight_path_records.csv').open(encoding='utf-8') as handle:
    import json
    for row in csv.DictReader(handle):
        word = ' '.join(f'{tile}_{n}' for tile, n in json.loads(row['word_json']))
        row['word'] = word
        records[row['parent']].append(row)

def dictionary_table() -> str:
    out = [r'{\small\renewcommand{\arraystretch}{1.15}', r'\begin{tabularx}{\linewidth}{@{}c X@{}}', r'\toprule', r'\textbf{tile} & \textbf{cyclic signed-edge word}\\', r'\midrule']
    for tile in NAMES:
        word = r'\;'.join(edge_tex(row['edge'] + ('' if row['sign'] == '1' else row['sign'])) for row in edge_rows[tile])
        out.append(f'${TEX_SYMBOL[tile]}$ & ${word}$' + r'\\')
    out += [r'\bottomrule', r'\end{tabularx}}']
    return '\n'.join(out)

def rule_table(tile: str) -> str:
    out = [rf'\subsection*{{Supertile ${TEX_SYMBOL[tile]}$ \hfill \normalfont\small {len(records[tile])} records}}', r'\vspace{-5pt}', r'{\footnotesize\renewcommand{\arraystretch}{1.08}', r'\begin{tabularx}{\textwidth}{@{}p{0.84in}p{0.82in}p{0.82in}X p{0.82in}p{0.82in}@{}}', r'\toprule', r'\textbf{state} & \textbf{entry super} & \textbf{entry} & \textbf{word} & \textbf{exit super} & \textbf{exit}\\', r'\midrule']
    for row in records[tile]:
        out.append(f"${state_tex(tile,row['n'],row['m'])}$ & ${edge_tex(row['entry_super'])}$ & ${row['m']}:{edge_tex(row['entry'])}$ & ${word_tex(row['word'])}$ & ${edge_tex(row['exit_super'])}$ & ${row['exit_m']}:{edge_tex(row['exit'])}$" + r'\\')
    out += [r'\bottomrule', r'\end{tabularx}}', r'\vspace{4pt}']
    return '\n'.join(out)

inventory = []
for trio in [NAMES[:3], NAMES[3:6], NAMES[6:9]]:
    cells = []
    for tile in trio:
        cells.extend([f'${TEX_SYMBOL[tile]}$', str(len(records[tile]))])
    inventory.append(' & '.join(cells) + r'\\')

tex = r'''\documentclass[10pt]{article}
\usepackage[letterpaper,landscape,margin=0.39in]{geometry}
\usepackage{amsmath,amssymb,booktabs,tabularx,array,xcolor}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype}
\setlength{\parindent}{0pt}
\setlength{\tabcolsep}{4pt}
\pagestyle{plain}
\begin{document}
\begin{center}
{\LARGE\bfseries Spectre Figure 4.2 / 5.1 Straight-Path Rule Data}\\[4pt]
{\large Positioned entry-to-exit records for the nine supertiles}\\[7pt]
\end{center}
\textbf{Scope.} This packet is the extracted \emph{straight-line baseline}: paths crossing each Figure 5.1 supertile between opposing super-edges without internal bends. Bent paths are intentionally excluded and may be added as a later rule-data layer.

\vspace{6pt}
\textbf{Positioned-state convention.} A state $X_{n,m}$ enters supertile $X$ on directional super-edge $n$ through its $m$-th ordinary edge segment, counted $1$-based along the oriented super-edge. Across a glued super-edge of length $|E|$, positions match by $m' = |E| - m + 1$.

\vspace{8pt}
\begin{minipage}[t]{0.58\textwidth}
\section*{Figure 4.2 signed-edge dictionary}
Each row is the cyclic signed-edge word for one parent hexagon in the extracted local order.\vspace{4pt}
''' + dictionary_table() + r'''
\end{minipage}\hfill
\begin{minipage}[t]{0.37\textwidth}
\section*{Figure 5.1 straight-path inventory}
{\small\begin{tabular}{@{}c r@{\qquad}c r@{\qquad}c r@{}}
\toprule
\textbf{tile} & \textbf{N} & \textbf{tile} & \textbf{N} & \textbf{tile} & \textbf{N}\\
\midrule
''' + '\n'.join(inventory) + r'''
\bottomrule
\end{tabular}}
\vspace{10pt}

Total: $76$ positioned straight-path records.

\vspace{12pt}
\textbf{Source excerpts.} The build reads only the bundled Figure 4.2 tile-edge macro excerpt and Figure 5.1 supertile excerpt, not the full paper.
\end{minipage}
\newpage
''' + '\n'.join(rule_table(tile) for tile in NAMES[:3]) + r'''
\newpage
''' + '\n'.join(rule_table(tile) for tile in NAMES[3:6]) + r'''
\newpage
''' + '\n'.join(rule_table(tile) for tile in NAMES[6:9]) + r'''
\end{document}
'''
tex_path = BUILD / 'spectre_straight_path_rule_tables.tex'
pdf_path = DOCS / 'spectre_straight_path_rule_tables.pdf'
tex_path.write_text(tex, encoding='utf-8')
subprocess.run(['pdflatex', '-interaction=nonstopmode', '-halt-on-error', '-output-directory', str(BUILD), str(tex_path)], check=True, stdout=subprocess.DEVNULL)
(BUILD / 'spectre_straight_path_rule_tables.pdf').replace(pdf_path)
print(f'wrote {pdf_path}')

# Keep the packaged build directory free of LaTeX intermediates.
for suffix in ['.aux', '.log']:
    artifact = BUILD / (tex_path.stem + suffix)
    if artifact.exists():
        artifact.unlink()
