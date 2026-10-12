"""Build editable AASTeX and a separately typeset review PDF from manuscript.json.

The PDF is a review copy, not a claim that AASTeX compiled locally.
"""

from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

P = Path(__file__).resolve().parent
m = json.loads((P / "manuscript.json").read_text())


def tex(s):
    return "".join(
        {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }.get(c, c)
        for c in s
    )


lines = [
    r"\documentclass[twocolumn]{aastex7}",
    r"\begin{document}",
    r"\title{" + tex(m["title"]) + "}",
    r"\author"
    + ("[" + m["orcid"] + "]" if m.get("orcid") else "")
    + "{"
    + tex(m["author"])
    + "}",
]
if m["affiliation"]:
    lines.append(r"\affiliation{" + tex(m["affiliation"]) + "}")
else:
    lines.append("% Author affiliation must be supplied before submission.")
if m["email"]:
    lines.append(r"\email{" + tex(m["email"]) + "}")
else:
    lines.append("% Corresponding email must be supplied before submission.")
lines.extend([r"\begin{abstract}", tex(m["abstract"]), r"\end{abstract}"])
for s in m["sections"]:
    lines.append(r"\section{" + tex(s["heading"]) + "}")
    lines.extend(tex(p) + "\n" for p in s["paragraphs"])
lines.extend(
    [
        r"\begin{figure*}",
        r"\centering",
        r"\includegraphics[width=\textwidth]{figure1.pdf}",
        r"\caption{" + tex(m["figure_caption"].removeprefix("Figure 1. ")) + "}",
        r"\end{figure*}",
        r"\section*{References}",
    ]
)
lines.extend(tex(r) + r"\par" for r in m["references"])
lines.append(r"\end{document}")
(P / "rnaas.tex").write_text("\n".join(lines) + "\n")
text = [
    m["title"],
    m["author"],
    m.get("affiliation") or "[Affiliation pending]",
    m.get("email") or "[Corresponding email pending]",
    "ORCID: " + m["orcid"] if m.get("orcid") else "",
    m["status"],
    "ABSTRACT",
    m["abstract"],
]
for s in m["sections"]:
    text.extend([s["heading"], *s["paragraphs"]])
text.extend([m["figure_caption"], "REFERENCES", *m["references"]])
(P / "rnaas.txt").write_text("\n\n".join(text) + "\n")
styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="PaperTitle", fontName="Times-Bold", fontSize=17, leading=20, spaceAfter=10
    )
)
styles.add(
    ParagraphStyle(
        name="PaperBody",
        fontName="Times-Roman",
        fontSize=10.5,
        leading=14,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperHead",
        fontName="Times-Bold",
        fontSize=11,
        leading=14,
        spaceBefore=7,
        spaceAfter=5,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        name="PaperSmall", fontName="Times-Roman", fontSize=9, leading=12, spaceAfter=6
    )
)
flow = [
    Paragraph(escape(m["title"]), styles["PaperTitle"]),
    Paragraph(escape(m["author"]), styles["PaperBody"]),
]
if m["affiliation"]:
    flow.append(Paragraph(escape(m["affiliation"]), styles["PaperSmall"]))
if m.get("orcid"):
    flow.append(
        Paragraph(
            'ORCID: <link href="https://orcid.org/'
            + m["orcid"]
            + '">'
            + m["orcid"]
            + "</link>",
            styles["PaperSmall"],
        )
    )
if m["email"]:
    flow.append(Paragraph(escape(m["email"]), styles["PaperSmall"]))
flow.extend(
    [
        Paragraph(escape(m["status"]), styles["PaperSmall"]),
        Spacer(1, 7),
        Paragraph("Abstract", styles["PaperHead"]),
        Paragraph(escape(m["abstract"]), styles["PaperBody"]),
    ]
)
for s in m["sections"]:
    flow.append(Paragraph(escape(s["heading"]), styles["PaperHead"]))
    for p in s["paragraphs"]:
        flow.append(Paragraph(escape(p), styles["PaperBody"]))
flow.append(Paragraph("References", styles["PaperHead"]))
for r in m["references"]:
    flow.append(Paragraph(escape(r), styles["PaperSmall"]))
flow.extend(
    [
        Spacer(1, 18),
        Image(str(P / "figure1.png"), width=480, height=192),
        Spacer(1, 12),
        Paragraph(escape(m["figure_caption"]), styles["PaperBody"]),
    ]
)


def footer(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(54, 30, "PLANETHUNT | Author-review draft | 13 October 2026")
    canvas.drawRightString(558, 30, str(doc.page))


SimpleDocTemplate(
    str(P / "rnaas-review.pdf"),
    pagesize=(612, 792),
    rightMargin=54,
    leftMargin=54,
    topMargin=48,
    bottomMargin=48,
    title=m["title"],
    author=m["author"],
).build(flow, onFirstPage=footer, onLaterPages=footer)

# Count the same text that appears in the manuscript, excluding author metadata.
counted = [m["title"], m["abstract"], "References"]
for section in m["sections"]:
    counted.extend([section["heading"], *section["paragraphs"]])
counted.extend([m["figure_caption"], *m["references"]])
counts = {
    "method": "whitespace-separated words including title, headings, abstract, body, caption and references; author metadata excluded",
    "abstract": len(m["abstract"].split()),
    "total": len(" ".join(counted).split()),
    "limit_total": 1500,
    "limit_abstract": 150,
}
assert counts["total"] <= 1500 and counts["abstract"] <= 150
(P / "word-count.json").write_text(json.dumps(counts, indent=2) + "\n")
print(json.dumps(counts))
