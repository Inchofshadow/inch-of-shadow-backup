"""Builds layout options for the bottom (terms) block of rate-card.html.
Writes options/opt<N>.html, renders each to PDF + PNG. Same facts in every option.
Run: python3 build_options.py
"""
import os
import re
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "options")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

src = open(os.path.join(HERE, "rate-card.html"), encoding="utf-8").read()
# fonts are referenced relative to plans/studio-service; options live one level deeper
src = src.replace('url("../../docs/', 'url("../../../docs/')
TERMS = re.search(r'  <div class="terms">.*?\n  </div>\n', src, re.S).group(0)

OPTIONS = {
    1: ("Spec sheet: label left, text right, one row each", """
  .o1 { display: grid; grid-template-columns: 30mm 1fr; row-gap: 3.2mm; column-gap: 8mm; }
  .o1 dt { font-weight: 400; font-size: 7.5pt; letter-spacing: 0.3em; text-transform: uppercase; color: var(--soft); padding-top: 1mm; }
  .o1 dd { margin: 0; font-size: 10pt; }
""", """  <dl class="o1">
    <dt>Revisions</dt><dd>2 rounds included</dd>
    <dt>Delivery</dt><dd>Within 10 days after the files and the first payment arrive, usually faster</dd>
    <dt>Express</dt><dd>&euro;100 for delivery within 48 hours, up to 4 tracks, when available</dd>
    <dt>Payment</dt><dd>50% before the work starts, 50% before the final files are delivered</dd>
    <dt>Discounts</dt><dd>Possible for EPs and albums, by custom quote</dd>
    <dt>Files</dt><dd>WAV, 24-bit or higher, at the session's sample rate. Stems and setup once the price is agreed</dd>
  </dl>
"""),
    2: ("How it works: 4 numbered steps in the client's order", """
  .o2h { font-weight: 400; font-size: 7.5pt; letter-spacing: 0.32em; text-transform: uppercase; color: var(--soft); margin: 0 0 5mm; }
  .o2 { display: grid; grid-template-columns: repeat(4, 1fr); column-gap: 7mm; }
  .o2 .n { font-family: "Marcellus", serif; font-size: 30pt; line-height: 1; color: var(--flash); margin-bottom: 3mm; }
  .o2 h3 { font-family: "Marcellus", serif; font-weight: 400; font-size: 12pt; color: var(--flash); margin: 0 0 1.5mm; }
  .o2 p { margin: 0; font-size: 9pt; line-height: 1.5; }
  .o2note { margin: 7mm 0 0; font-size: 9pt; color: var(--soft); }
""", """  <p class="o2h">How it works</p>
  <div class="o2">
    <div><div class="n">1</div><h3>Send files</h3><p>WAV, 24-bit or higher, at the session's sample rate.</p></div>
    <div><div class="n">2</div><h3>Pay 50%</h3><p>The work starts once the first half arrives.</p></div>
    <div><div class="n">3</div><h3>10 days</h3><p>Delivery within 10 days, usually faster. 2 revision rounds included.</p></div>
    <div><div class="n">4</div><h3>Pay 50%</h3><p>The second half, then you get the final files.</p></div>
  </div>
  <p class="o2note">Express: &euro;100 for 48 hours, up to 4 tracks, when available. Discounts for EPs and albums by custom quote.</p>
"""),
    3: ("Big numbers: the 4 key facts large, the rest as one small line", """
  .o3 { display: grid; grid-template-columns: 0.8fr 0.8fr 1.3fr 1fr; column-gap: 7mm; }
  .o3 .big { font-family: "Marcellus", serif; font-size: 30pt; line-height: 1; color: var(--flash); letter-spacing: 0.01em; }
  .o3 .cap { margin-top: 3mm; font-weight: 400; font-size: 7.5pt; letter-spacing: 0.26em; text-transform: uppercase; color: var(--soft); }
  .o3 p { margin: 2mm 0 0; font-size: 9pt; line-height: 1.45; }
  .o3note { margin: 9mm 0 0; font-size: 9pt; color: var(--soft); line-height: 1.6; }
""", """  <div class="o3">
    <div><div class="big">2</div><div class="cap">Revision rounds</div><p>Included in every price.</p></div>
    <div><div class="big">10</div><div class="cap">Days</div><p>Delivery after files and first payment, usually faster.</p></div>
    <div><div class="big">50/50</div><div class="cap">Payment</div><p>Half before the work, half before the final files.</p></div>
    <div><div class="big">48h</div><div class="cap">Express</div><p>&euro;100, up to 4 tracks, when available.</p></div>
  </div>
  <p class="o3note">Files: WAV, 24-bit or higher, at the session's sample rate. Discounts for EPs and albums by custom quote.</p>
"""),
    4: ("Two groups: what is included / good to know", """
  .o4 { display: grid; grid-template-columns: 1fr 1fr; column-gap: 14mm; }
  .o4 h3 { font-family: "Marcellus", serif; font-weight: 400; font-size: 15pt; color: var(--flash); margin: 0 0 4mm; }
  .o4 ul { list-style: none; margin: 0; padding: 0; }
  .o4 li { font-size: 9.5pt; line-height: 1.5; margin: 0 0 3mm; }
  .o4 li b { font-weight: 400; color: var(--flash); }
""", """  <div class="o4">
    <div><h3>Included</h3><ul>
      <li><b>2 revision rounds</b> per track</li>
      <li><b>Delivery in 10 days</b> after the files and the first payment arrive, usually faster</li>
      <li><b>Vinyl master</b> comes with the digital version</li>
    </ul></div>
    <div><h3>Good to know</h3><ul>
      <li><b>Payment:</b> 50% before the work starts, 50% before the final files</li>
      <li><b>Express:</b> &euro;100 for 48 hours, up to 4 tracks, when available</li>
      <li><b>Discounts:</b> for EPs and albums, by custom quote</li>
      <li><b>Files:</b> WAV, 24-bit or higher, at the session's sample rate</li>
    </ul></div>
  </div>
"""),
}

os.makedirs(OUT, exist_ok=True)
for n, (title, css, html) in OPTIONS.items():
    page = src.replace("</style>", css + "</style>").replace(TERMS, html)
    hp = os.path.join(OUT, f"opt{n}.html")
    open(hp, "w", encoding="utf-8").write(page)
    pdf = os.path.join(OUT, f"opt{n}.pdf")
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={prof}",
                        "--no-pdf-header-footer", "--allow-file-access-from-files", f"--print-to-pdf={pdf}",
                        "file://" + hp], capture_output=True)
    subprocess.run(["sips", "-s", "format", "png", "-Z", "1400", pdf, "--out", os.path.join(OUT, f"opt{n}.png")],
                   capture_output=True)
    pages = open(pdf, "rb").read().count(b"/Type /Page\n") or open(pdf, "rb").read().count(b"/Type/Page")
    print(n, title, "pdf ok" if os.path.exists(pdf) else "FAILED")
