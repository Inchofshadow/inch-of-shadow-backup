"""Builds colour versions of rate-card.html from the brand colour moods (docs/brand/frame.md).
Writes options/col<N>.html/.pdf/.png/.jpg. Text and layout stay the same; only colour changes.
Run: python3 build_colours.py
"""
import os
import subprocess
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "options")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

src = open(os.path.join(HERE, "rate-card.html"), encoding="utf-8").read()
src = src.replace('url("../../docs/', 'url("../../../docs/')


src = src.replace("Mixing &amp;<br>", '<span class="w1">Mixing</span> <span class="amp">&amp;</span><br>')


def vibe(ground, glow, title_a, title_b, amp, accent, ink, price):
    """ground page, soft glow blobs, gradient title, coloured & / labels / prices."""
    return f"""
  :root {{ --ground: {ground}; --flash: {ink}; --ink: {ink}; --soft: {accent}; --faint: transparent; }}
  .page {{ background: {glow}, {ground}; }}
  h1 {{ background: linear-gradient(100deg, {title_a} 0%, {title_b} 85%); -webkit-background-clip: text; background-clip: text;
        color: transparent; -webkit-text-fill-color: transparent; padding-bottom: 2mm; }}
  h1 .amp {{ -webkit-text-fill-color: {amp}; color: {amp}; font-style: italic; }}
  .name {{ color: {title_a}; }}
  .kicker, .label, .o1 dt, footer span {{ color: {accent}; font-weight: 500; }}
  .rates .price {{ color: {price}; font-weight: 400; }}
  .vat {{ color: {title_a}; }}
  .rates .what small {{ color: {accent}; }}
"""


COLOURS = {
    1: ("Dusk: midnight to violet title, rose glow",
        vibe("#F7F3EF",
             "radial-gradient(circle at 92% 6%, rgba(201,162,214,0.55), transparent 42%), "
             "radial-gradient(circle at 8% 98%, rgba(232,190,200,0.55), transparent 40%)",
             "#2B2147", "#7A5FA8", "#C46F8E", "#8A6BAE", "#2B2147", "#6A4C93")),
    2: ("Warm studio: oxblood to amber title, golden glow",
        vibe("#FAF4EA",
             "radial-gradient(circle at 90% 4%, rgba(232,190,120,0.55), transparent 44%), "
             "radial-gradient(circle at 6% 96%, rgba(214,150,120,0.40), transparent 40%)",
             "#5C1F26", "#B5652E", "#C8923A", "#B0784A", "#2E1A14", "#7A2B2F")),
    3: ("Forest: deep green to moss title, sage glow",
        vibe("#F3F4EE",
             "radial-gradient(circle at 92% 6%, rgba(170,196,160,0.60), transparent 44%), "
             "radial-gradient(circle at 6% 96%, rgba(214,206,150,0.45), transparent 40%)",
             "#1F3A2B", "#5E7F3E", "#B08A3A", "#5C7A55", "#16241C", "#2F5A3B")),
    4: ("Night and coral: navy to blue title, coral accents",
        vibe("#F6F2EE",
             "radial-gradient(circle at 92% 5%, rgba(150,175,220,0.55), transparent 44%), "
             "radial-gradient(circle at 6% 97%, rgba(240,160,135,0.45), transparent 40%)",
             "#1C2747", "#3F63A8", "#E0785E", "#D06A50", "#1C2233", "#1C2747")),
}

os.makedirs(OUT, exist_ok=True)
for n, (title, css) in COLOURS.items():
    page = src.replace("</style>", css + "</style>")
    hp = os.path.join(OUT, f"col{n}.html")
    open(hp, "w", encoding="utf-8").write(page)
    pdf = os.path.join(OUT, f"col{n}.pdf")
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={prof}",
                        "--no-pdf-header-footer", "--allow-file-access-from-files", f"--print-to-pdf={pdf}",
                        "file://" + hp], capture_output=True)
    subprocess.run(["sips", "-s", "format", "jpeg", "-s", "formatOptions", "82", "-Z", "1100", pdf,
                    "--out", os.path.join(OUT, f"col{n}.jpg")], capture_output=True)
    print(n, title)
