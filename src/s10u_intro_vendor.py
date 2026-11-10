"""S10u · §1.3: bỏ tên sản phẩm thương mại không trích dẫn (Visa Advance
Authorization / Mastercard Decision Insights) -- rủi ro uy tín học thuật (§3.10)."""
from pathlib import Path

p = Path("report/Sections/2-Intro.tex")
s = p.read_text(encoding="utf-8")

OLD = """    \\item \\textbf{Application:} Real-time transaction authorisation for an
    issuing bank, integrated with card-network risk services such as Visa
    Advance Authorization and Mastercard Decision Insights."""

NEW = """    \\item \\textbf{Application:} Real-time transaction authorisation at the
    issuing bank, as one decision stage inside the wider card-network risk
    process. We model the decision itself --- what to score, at what cost, and
    who acts on the output --- and make no claim about any specific vendor
    product."""

if OLD not in s:
    raise SystemExit("anchor not found")

s = s.replace(OLD, NEW, 1)
p.write_text(s, encoding="utf-8")
print("[ok] 2-Intro.tex: removed uncited vendor product names")
