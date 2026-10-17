#!/usr/bin/env python3
"""Build ROADMAP.pdf from ROADMAP.md (minimal Markdown subset) with reportlab."""
import os, re
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
                                Preformatted, KeepTogether)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping

D = "/usr/share/fonts/truetype/dejavu/"
for n, f in [("DV", "DejaVuSans.ttf"), ("DV-B", "DejaVuSans-Bold.ttf"), ("DVM", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(n, D + f))
addMapping("DV", 0, 0, "DV"); addMapping("DV", 1, 0, "DV-B"); addMapping("DV", 0, 1, "DV"); addMapping("DV", 1, 1, "DV-B")  # no DejaVu italic installed: render upright

HERE = "/workspace/querp-multinode-sim"
body = ParagraphStyle("b", fontName="DV", fontSize=8.9, leading=11.6, spaceAfter=3.5)
cap = ParagraphStyle("c", parent=body, fontSize=8.2, leading=10.5, textColor=colors.HexColor("#333333"))
h1 = ParagraphStyle("h1", fontName="DV-B", fontSize=16, leading=20, spaceAfter=4, textColor=colors.HexColor("#1b3a5c"))
h2 = ParagraphStyle("h2", fontName="DV-B", fontSize=11.5, leading=14.5, spaceBefore=8, spaceAfter=4,
                    textColor=colors.HexColor("#1b3a5c"))
h3 = ParagraphStyle("h3", fontName="DV-B", fontSize=10, leading=13, spaceBefore=5, spaceAfter=3,
                    textColor=colors.HexColor("#2b4a6b"))
bul = ParagraphStyle("li", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=2)
code = ParagraphStyle("code", fontName="DVM", fontSize=9.5, leading=12, leftIndent=18, spaceBefore=2, spaceAfter=6,
                      backColor=colors.HexColor("#f2f4f7"), borderPadding=4)
tcell = ParagraphStyle("tc", parent=body, fontSize=8.4, leading=10.4, spaceAfter=0)

def inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"`([^`]+)`", r'<font name="DVM" size="8.5">\1</font>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r'<font color="#2b4a6b">\1</font>', s)
    return s

def footer(c, doc):
    c.saveState(); c.setFont("DV", 7.5); c.setFillColor(colors.grey)
    c.drawString(0.8 * inch, 0.5 * inch, "Waurika Magnetic Laboratory · QuERP build-and-test roadmap")
    c.drawRightString(letter[0] - 0.8 * inch, 0.5 * inch, "page %d" % doc.page); c.restoreState()

lines = [l[2:] if l.startswith("> ") else l for l in open(os.path.join(HERE, "ROADMAP.md"), encoding="utf-8").read().splitlines()]
story, i, W = [], 0, letter[0] - 1.6 * inch
while i < len(lines):
    L = lines[i]
    if not L.strip(): i += 1; continue
    if L.startswith("# "): story.append(Paragraph(inline(L[2:]), h1)); i += 1; continue
    if L.startswith("### "): story.append(Paragraph(inline(L[4:]), h3)); i += 1; continue
    if L.startswith("## "): story.append(Paragraph(inline(L[3:]), h2)); i += 1; continue
    if L.startswith("    "):
        blk = []
        while i < len(lines) and lines[i].startswith("    "): blk.append(lines[i][4:]); i += 1
        story.append(Preformatted("\n".join(blk), code)); continue
    m = re.match(r"!\[.*\]\((.+)\)", L)
    if m:
        p = os.path.join(HERE, m.group(1)); img = Image(p); r = img.imageHeight / img.imageWidth
        ww = W * (0.62 if r > 0.6 else 0.92); img.drawWidth, img.drawHeight = ww, ww * r
        i += 1
        while i < len(lines) and not lines[i].strip(): i += 1
        capt = Paragraph(inline(lines[i].strip("*")), cap) if i < len(lines) and lines[i].startswith("*Figure") else None
        if capt: i += 1
        story.append(KeepTogether([img] + ([capt] if capt else []))); continue
    if L.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-+:?", c) for c in cells): rows.append(cells)
            i += 1
        data = [[Paragraph(("<b>%s</b>" % inline(c)) if r == 0 else inline(c), tcell) for c in row]
                for r, row in enumerate(rows)]
        nc = len(rows[0])
        ln = [max(8, min(60, max(len(r[k]) for r in rows))) ** 0.8 for k in range(nc)]
        cw = [W * x / sum(ln) for x in ln]
        t = Table(data, colWidths=cw, hAlign="LEFT")
        t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dde5ee")),
                               ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#9aa8b8")),
                               ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                               ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        story += [t, Spacer(1, 6)]; continue
    m = re.match(r"(\d+)\.\s+(.*)", L)
    if L.startswith("- ") or m:
        while i < len(lines) and (lines[i].startswith("- ") or re.match(r"\d+\.\s", lines[i])):
            mm = re.match(r"(\d+)\.\s+(.*)", lines[i])
            txt, b = (mm.group(2), mm.group(1) + ".") if mm else (lines[i][2:], "•")
            story.append(Paragraph(inline(txt), bul, bulletText=b)); i += 1
        story.append(Spacer(1, 3)); continue
    para = [L]; i += 1
    while i < len(lines) and lines[i].strip() and not re.match(r"(#|\||!\[|- |\d+\.\s|    )", lines[i]):
        para.append(lines[i]); i += 1
    story.append(Paragraph(inline(" ".join(para)), body))

doc = SimpleDocTemplate(os.path.join(HERE, "ROADMAP.pdf"), pagesize=letter,
                        leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.75 * inch,
                        title="QuERP Build-and-Test Roadmap", author="Waurika Magnetic Laboratory")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print("wrote ROADMAP.pdf")
