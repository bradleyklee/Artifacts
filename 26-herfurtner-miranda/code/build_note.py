#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "note.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCenter", parent=styles["Title"], alignment=TA_CENTER, spaceAfter=16))
styles.add(ParagraphStyle(name="H1x", parent=styles["Heading1"], spaceBefore=10, spaceAfter=7))
styles.add(ParagraphStyle(name="H2x", parent=styles["Heading2"], spaceBefore=8, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyX", parent=styles["BodyText"], leading=14, spaceAfter=7))
styles.add(ParagraphStyle(name="CodeX", parent=styles["Code"], fontName="Courier", fontSize=8.2, leading=10.2, leftIndent=12, rightIndent=8, spaceAfter=8))
styles.add(ParagraphStyle(name="SmallX", parent=styles["BodyText"], fontSize=8.2, leading=10))


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.drawString(0.65 * inch, 0.42 * inch, "Miranda-Herfurtner release v2 - 2026-08-05")
    canvas.drawRightString(7.85 * inch, 0.42 * inch, f"page {doc.page}")
    canvas.restoreState()


def P(text, style="BodyX"):
    return Paragraph(text, styles[style])


story = [
    P("Miranda-Herfurtner Plane Hamiltonian Search", "TitleCenter"),
    P("Release v2: curve models, Laurent periods, and OEIS ledger", "Heading2"),
    P(
        "This artifact treats two searches as equally important: finding useful plane curve presentations of elliptic families, and finding Laurent polynomials whose constant terms reproduce the corresponding period series. All examples are organized directly under <font name='Courier'>examples/</font>."
    ),
    P("Verified baseline", "H1x"),
    P(
        "The baseline contains 11 exact four-fiber plane models: 3 harmonic cubics and 8 quartics with two fixed nodes at infinity. All 11 have exact period data. Baseline models 1, 2, 3, 5, 7, and 9 have independent exact plane and Laurent certificates."
    ),
    Table(
        [
            [P("group", "SmallX"), P("count", "SmallX"), P("status", "SmallX")],
            ["baseline plane models", "11", "exact invariants and periods"],
            ["baseline Laurent-complete", "6", "exact certificates"],
            ["new tacnode presentations", "2", "T0 covered; T1 open"],
            ["OEIS exact matches", "1", "model 2 = A303790"],
        ],
        colWidths=[2.2 * inch, 1.1 * inch, 3.6 * inch],
        repeatRows=1,
        style=TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("LEADING", (0, 0), (-1, -1), 10.5),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    ),
    Spacer(1, 10),
    P("New curve-model stratum", "H1x"),
    P("A one-fixed-tacnode harmonic quartic family was solved:"),
    P(
        "2H = p^2+q^2+2s p^2 q+v p q^2+w q^3<br/>"
        "+ s^2 p^2 q^2+s v p q^3+c q^4.",
        "CodeX",
    ),
    P("Projection from the tacnode gives"),
    P("Y^2 = (v^2-4c)x^4 - 4w x^3 - 4x^2 + 4E.", "CodeX"),
    P(
        "Writing A=v^2-4c, the normalized invariants are c4=1+3AE and c6=1-(9A+27w^2/2)E. Generic members therefore have the already known fiber configuration III*+I1+I1+I1. The result adds plane presentations, not a new entry in the historical four-fiber list."
    ),
    PageBreak(),
    P("Two retained tacnode presentations", "H1x"),
    P("T0 - holomorphic time form", "H2x"),
    P("2H = p^2+q^2+q^3-q^4/4", "CodeX"),
    P(
        "At arithmetic scale 32, its first 31 period coefficients agree exactly with baseline model 1. The same normalized elliptic invariants and the termwise period calculation identify the periods. The stored model-1 Laurent polynomial and certificate therefore cover this new plane presentation."
    ),
    P("T1 - third-kind time form", "H2x"),
    P("2H = p^2+q^2+2p^2q+q^3+p^2q^2-q^4/4", "CodeX"),
    P("Its scale-32 period starts"),
    P("1, 76, 12084, 2361680, 509004580, 116126173296, ...", "CodeX"),
    P(
        "Fifty-one exact coefficients were computed. An order-three differential equation was checked on 48 coefficient equations. The extra factor in the normalized time form is 1/(1+x), so the Hamiltonian period is a period of a third-kind differential rather than the holomorphic elliptic differential. Its Laurent model remains open."
    ),
    P("Laurent search advanced by exact exclusions", "H1x"),
    P(
        "For baseline models 4, 8, and 10, divide the period coefficients by binomial(2n,n). The resulting reduced sequences were tested against the integer palindromic product class"
    ),
    P("F=((1+w)^2/w) G(z),  G=g0+sum_(k=1)^d gk(z^k+z^(-k)).", "CodeX"),
    Table(
        [
            ["model", "degree", "square vectors", "match b3", "match b4"],
            ["4", "5", "77,760", "4", "0"],
            ["4", "6", "3,218,040", "76", "0"],
            ["8", "5", "485,760", "2", "0"],
            ["8", "6", "32,901,120", "182", "0"],
            ["10", "5", "339,840", "42", "0"],
            ["10", "6", "15,952,920", "786", "0"],
        ],
        colWidths=[0.7 * inch, 0.75 * inch, 1.5 * inch, 1.15 * inch, 1.15 * inch],
        repeatRows=1,
        style=TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]),
    ),
    Spacer(1, 8),
    P(
        "No degree-5 or degree-6 candidate matches the fourth reduced moment. A separate exact rank-two search examined 495 centrally symmetric four-pair support sets and found no candidate matching even the third reduced moment. These are bounded exclusions, not nonexistence results."
    ),
    PageBreak(),
    P("OEIS ledger", "H1x"),
    P(
        "Baseline model 2 is exactly OEIS A303790. Exact-prefix searches located no raw match for the other stored baseline sequences or T1 on 2026-08-05. The ledger uses the phrase 'no exact-prefix match located' because this does not exclude occurrence after a shift, sign change, binomial reduction, rescaling, or another transform."
    ),
    P("Next paired search round", "H1x"),
    P("Curve models", "H2x"),
    P(
        "Classify delta-two unibranch singularities and degenerate tacnodes at infinity; check rational presentation coverage inside the two-node class; then move to quintics with prescribed singularity clusters whose total delta leaves genus one."
    ),
    P("Laurent polynomials", "H2x"),
    P(
        "Treat T1 as an order-three meromorphic-period problem and allow three-variable diagonals. For models 4, 8, and 10, move to larger rank-two supports, nonsymmetric supports, and mutation templates. Normalize models 6 and 11 before enumeration so their large arithmetic scales do not dominate coefficient solving."
    ),
    P("Files to read", "H1x"),
    P("paper/SEARCH_LEDGER.md - compact human ledger", "CodeX"),
    P("examples/data/research_ledger.json - machine-readable source of truth", "CodeX"),
    P("examples/data/tacnode_quartic_result.json - exact curve calculation", "CodeX"),
    P("examples/data/tacnode_period_result.json - T0/T1 periods and T1 equation", "CodeX"),
    P("examples/data/laurent_palindromic_search_d5_d6.json - exhaustive counts", "CodeX"),
    P("Run the audit", "H1x"),
    P("python code/run_release_checks.py", "CodeX"),
]

doc = SimpleDocTemplate(
    str(OUTPUT),
    pagesize=letter,
    rightMargin=0.65 * inch,
    leftMargin=0.65 * inch,
    topMargin=0.62 * inch,
    bottomMargin=0.65 * inch,
    title="Miranda-Herfurtner Plane Hamiltonian Search - Release v2",
    author="Research artifact",
)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote", OUTPUT)
