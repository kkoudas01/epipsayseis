#!/usr/bin/env python3
"""
wljs_to_static_v4.py  —  WLJS → Standalone Static HTML Converter
═════════════════════════════════════════════════════════════════════

ΣΚΟΠΟΣ / PURPOSE
─────────────────
Μετατρέπει ένα WLJS static HTML notebook σε πλήρως αυτόνομο στατικό HTML αρχείο.
Το αποτέλεσμα δεν χρειάζεται JavaScript runtime, external assets, ή server:
ανοίγει in a browser ως single self-contained file.

ΑΡΧΙΤΕΚΤΟΝΙΚΗ PIPELINE
────────────────────────
1. JSON parse     : Εξάγει cells-data + json-objects από το WLJS HTML
2. gmap build     : Αποκωδικοποιεί/αποσυμπιέζει WL expression trees από json-objects
3. gmap resolve   : Λύνει VB indirection chains ((*VB[*)(FrontEndRef["uuid"])...)
4. Cell rendering : Κάθε cell → HTML block ανάλογα με type:
     Input/codemirror  → <pre> code block (collapsible αν Fade=True)
     Output/markdown   → rendered HTML (via python-markdown)
     Output/math       → LaTeX/MathJax (wljs_to_latex: box notation decoding)
     Output/Graphics   → inline SVG (graphics_to_svg)
     Output/Graphics3D → PNG base64 (g3d_to_b64_matplotlib)
     Output/Image      → PNG base64 (image_to_b64)
5. TOC build      : Floating sidebar με headings + active tracking
6. HTML output    : Ενιαίο αρχείο με embedded CSS + MathJax CDN

ΤΥΠΟΙ OUTPUT CELLS (WL → HTML)
────────────────────────────────
• Plain math:   (*FB[*), (*SpB[*), (*SqB[*) box notation → LaTeX via wljs_to_latex
• Series:       (*VB[*)(SeriesData[...]) → LaTeX power series
• Graphics:     (*VB[*)(FrontEndRef["uuid"]) → SVG μέσω graphics_to_svg
• Graphics3D:   (*VB[*)(FrontEndRef["uuid"]) → PNG μέσω matplotlib
• Legended:     (*VB[*)(Legended[FrontEndRef["uuid"], BarLegend[...]]) →
                  Plot SVG/PNG + vertical colorbar (bar_graphics_to_svg)
• StreamPlot:   Γεωμετρικά primitives (Arrow/BezierCurve + color directives)
• VectorPlot3D: Arrow[Tube[...]] 3D arrows → ax.quiver με LABColor χρωματισμό
• LineLegend:   Legended output → SVG (linelegend_to_svg) + scrollable labels
• BarLegend:    Legended output → bar_graphics_to_svg με min/max labels

ΓΝΩΣΤΑ BUGS ΠΟΥ ΔΙΟΡΘΩΘΗΚΑΝ (κατά σειρά ανακάλυψης)
──────────────────────────────────────────────────────
01. DensityPlot colorbar: densityplot_to_b64 + bar_graphics_to_svg
02. Abs[x] LaTeX: |x| αντί AbsoluteValue[x]
03. Named chars: [Pi] → pi, [Alpha] → alpha κτλ.
04. Admonitions: ::: warning/note → colored div blocks
05. Multi-primitive color: Directive state inheritance σε nested primitives
06-10. Διάφορες διορθώσεις SVG rendering (Arrow, Disk, BSplineCurve...)
11. Rational[a,b] coords: _wl_num() evaluator για WL αριθμητικές εκφράσεις
12. Scatter ColorFunction: densityplot_to_b64 για Point-based scatter plots
13. PointSize[v]: DS.pt_size από PointSize/AbsolutePointSize directives
14. (*VB[*) extraction: αντί για [⋯] εξάγει εσωτερικό WL expression
15. SeriesData → LaTeX: _seriesdata_to_latex converter
16. HoldForm in legends: strip_holdform στο to_text() της parse_linelegend
17. Legend overflow: linelegend_to_svg → HTML div με overflow-x:auto + MathJax
18. collect_xy NameError: xs,ys=[] τοπική αρχικοποίηση (StreamPlot crash fix)
19. tp() pw/ph undefined: pw=W-2*pad τοπικά αντί ως global
20. render_2d out=[]: λείπουσα αρχικοποίηση της λίστας SVG output
21. nice_ticks span undefined: span=v1-v0 στην αρχή της συνάρτησης
22. render_md ph/ctr undefined: ph={}, ctr=[0] τοπικές μεταβλητές
23. FrontEndRef uuids: uuids=re.findall(...) πριν το for loop
24. ParametricPlot3D: g3d handles Line → ax.plot3D curves
25. VectorPlot3D: g3d handles Arrow[Tube[...]] → ax.quiver με LABColor
26. StreamPlot+BarLegend: Legended VB cells resolved via alias chain
27. MatrixForm output: decode_gb handles outer () wrapper around GB box
28. Print[] output: display='print' cells rendered as monospace block
29. LaTeX output: display='latex' cells now rendered via MathJax (were silently skipped)

ΕΞΑΡΤΗΣΕΙΣ
───────────
Απαιτούνται: (pip install ...)
  beautifulsoup4  — HTML parsing
  lxml            — fast HTML parser backend (optional αλλά συνιστάται)
Προαιρετικές:
  matplotlib      — 3D graphics rendering (Graphics3D → PNG)
  numpy           — αριθμητικές πράξεις (για matplotlib + densityplot)
  Pillow (PIL)    — Image cell rendering
  markdown        — markdown → HTML (render_md)

ΧΡΗΣΗ / USAGE
──────────────
  python wljs_to_static_v4.py input.html output.html


ΤΕΧΝΙΚΟ ΥΠΟΒΑΘΡΟ
─────────────────
Τα WLJS notebook αρχεία (.html) εξάγονται από το Mathematica/WLJS Workbench
και περιέχουν:
  • JSON blob #cells-data : λίστα κελιών (Input/Output) με raw WL notation
  • JSON blob #json-objects: αντιστοίχιση UUID → Graphics/Graphics3D/Image/...
    (αυτά είναι τα rendered αντικείμενα, συχνά zlib-compressed)

Ο κώδικας αυτός:
  1. Διαβάζει τα δύο JSON blobs
  2. Αποσυμπιέζει τα compressed αντικείμενα (zlib+base64)
  3. Μετατρέπει κάθε κελί σε HTML:
       - markdown cells  → HTML μέσω python-markdown
       - code cells       → <pre><code> (με syntax highlight styling)
       - math output      → LaTeX μέσω MathJax (wljs_to_latex)
       - 2D graphics      → inline SVG (graphics_to_svg)
       - 3D graphics      → PNG base64 (matplotlib)
       - raster/image     → PNG base64 (pillow)
       - scatter/density  → rasterized PNG (numpy)
  4. Παράγει ένα αυτόνομο HTML με:
       - MathJax για LaTeX rendering
       - Floating TOC sidebar
       - Collapsible code cells (Fade=True → κλικ για ανάπτυξη)
       - Color scheme από το WLJS CSS

ΙΣΤΟΡΙΚΟ BUGS ΠΟΥ ΔΙΟΡΘΩΘΗΚΑΝ
───────────────────────────────
  v4 session (όλες οι διορθώσεις σε αυτό το αρχείο):
  #01  DensityPlot: λευκό (GraphicsComplex+Polygon renderer)
  #02  Abs[x] → |x| (LaTeX pipes)
  #03  Named chars (n π) → LaTeX greek
  #04  Markdown admonitions (:::warning) → colored box
  #05  Multi-primitive color inheritance
  #06  Rational coordinates → float (Rational[a,b] → a/b)
  #07  Scatter ColorFunction rasterization (bifurcation diagram)
  #08  PointSize[v] rendering (small r=1.3px αντί fixed r=3px)
  #09  VB tag: εξαγωγή WL_EXPR αντί placeholder [⋯]
  #10  SeriesData → LaTeX power series (Taylor/Fourier output)
  #11  HoldForm[x] σε legend labels → ξεγίνεται, εμφανίζεται x
  #12  Legend overflow → HTML div με overflow-x:auto + MathJax labels
  #13  3D plots (ParametricPlot3D, VectorPlot3D) → matplotlib PNG
  #14  StreamPlot BarLegend → colorbar SVG δίπλα στο plot

ΕΓΚΑΤΑΣΤΑΣΗ (μόνο μια φορά):
    pip install beautifulsoup4 markdown pillow numpy matplotlib

ΧΡΗΣΗ:
    python3 wljs_to_static_v4.py input.html output.html
"""

import sys, re, json, math, base64, zlib, io
from pathlib import Path

# ── Εξαρτήσεις ────────────────────────────────────────────────────────────────
# Αυστηρά απαιτούμενες (αποτυχία αν λείπουν):
try:    from bs4 import BeautifulSoup
except ImportError: sys.exit("pip install beautifulsoup4")
try:    import markdown as md_lib
except ImportError: sys.exit("pip install markdown")

# Προαιρετικές (WARN αν λείπουν, αλλά ο κώδικας συνεχίζει):
try:
    from PIL import Image as PILImage, ImageDraw
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("WARN: pip install pillow  (χρειάζεται για rasterized images)")

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False
    print("WARN: pip install numpy  (χρειάζεται για 3D rendering)")

try:
    # matplotlib.use('Agg') = non-interactive backend, παράγει PNG χωρίς X11/GUI
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    HAS_MPL = True
except ImportError:
    HAS_MPL = False
    print("WARN: pip install matplotlib  (χρειάζεται για 3D rendering)")

# Χρυσός αριθμός: χρησιμοποιείται ως fallback aspect ratio για SVG/3D plots
GOLDEN = (1 + math.sqrt(5)) / 2


# ══════════════════════════════════════════════════════════════════════════════
# ΑΠΟΣΥΜΠΙΕΣΗ
# ══════════════════════════════════════════════════════════════════════════════
# Τα Graphics/Graphics3D αντικείμενα στο #json-objects blob αποθηκεύονται
# ως zlib-compressed JSON, base64-encoded. Η decompress() τα επαναφέρει
# σε Python list structure (WL expression tree).

def decompress(s):
    """Αποσυμπιέζει WL αντικείμενο από base64(zlib(JSON)).
    Επιστρέφει Python list (WL expression tree), π.χ. ['Graphics3D', [...], ...].
    Το `s` μπορεί να έχει leading/trailing quote chars από το JSON storage.

    Το WLJS αποθηκεύει τα μεγάλα γραφήματα (Graphics, Graphics3D) συμπιεσμένα
    για να μειώσει το μέγεθος του HTML αρχείου. Τα compressed αντικείμενα
    αναγνωρίζονται από τον τύπο 'Compressed' στο expression tree.
    Αποσυμπίεση: base64 → bytes → zlib.decompress → JSON → Python list."""
    return json.loads(zlib.decompress(base64.b64decode(s.strip("'"))))


# ══════════════════════════════════════════════════════════════════════════════
# WLJS / WL OUTPUT → LaTeX
# ══════════════════════════════════════════════════════════════════════════════
# Το Mathematica/WLJS αποθηκεύει τα Output κελιά σε ειδική notation που
# αναμιγνύει plain WL (π.χ. "x^2 + 5") με "box" markers:
#   (*SqB[*) ... (*]SqB*)  = Square root box   → \sqrt{...}
#   (*SpB[*) ... (*]SpB*)  = Superscript box    → ...^{...}
#   (*FB[*)  ... (*]FB*)   = Fraction box       → \frac{...}{...}
#   (*BB[*)  ... (*]BB*)   = Generic box (hint) → extract inner WL
#   (*VB[*)  ... (*]VB*)   = Visual box (binary display data) → extract WL expr
#   (*TB[*)  ... (*]TB*)   = Template box (Piecewise, ConditionalExpression)
#   (*GB[*)  ... (*]GB*)   = Grid box (matrix)
#   (*|*)                  = argument separator inside boxes
#   (*,*)                  = segment separator (WL expr | display data)
# H wljs_to_latex() μετατρέπει όλα αυτά σε έγκυρο LaTeX για MathJax.

# Πίνακας αντιστοίχισης WL named chars (\[Pi] κτλ.) → LaTeX (\pi κτλ.)
# Διατηρείται ordered: τα πιο specific πρώτα (CurlyPhi πριν το Phi) για
# να μην γίνει partial match.
# Bug #03: τα \[Pi], \[Alpha] κτλ. εμφανίζονταν verbatim αντί για LaTeX.
# Η σειρά CurlyPhi → Phi είναι κρίσιμη: αν ψάξουμε 'Phi' πρώτα, το
# 'CurlyPhi' θα αντικατασταθεί ως 'Curly\phi ' (λάθος).
_GREEK = [
    # Lowercase
    ('CurlyPhi','\\varphi'), ('CurlyEpsilon','\\varepsilon'), ('CurlyTheta','\\vartheta'),
    # Formal variables (\[FormalN] etc.) → plain letters
    ('FormalA','a'), ('FormalB','b'), ('FormalC','c'), ('FormalD','d'), ('FormalE','e'),
    ('FormalF','f'), ('FormalG','g'), ('FormalH','h'), ('FormalI','i'), ('FormalJ','j'),
    ('FormalK','k'), ('FormalL','l'), ('FormalM','m'), ('FormalN','n'), ('FormalO','o'),
    ('FormalP','p'), ('FormalQ','q'), ('FormalR','r'), ('FormalS','s'), ('FormalT','t'),
    ('FormalU','u'), ('FormalV','v'), ('FormalW','w'), ('FormalX','x'), ('FormalY','y'), ('FormalZ','z'),
    # Logic/set operators
    ('Element','\\in '), ('NotElement','\\notin '), ('Subset','\\subset '), ('SupersetEqual','\\supseteq '),
    ('CurlyRho','\\varrho'), ('CurlyKappa','\\varkappa'), ('CurlyPi','\\varpi'),
    ('Pi','\\pi'), ('Infinity','\\infty'), ('Alpha','\\alpha'), ('Beta','\\beta'),
    ('Gamma','\\gamma'), ('Delta','\\delta'), ('Epsilon','\\epsilon'),
    ('Theta','\\theta'), ('Lambda','\\lambda'), ('Mu','\\mu'), ('Nu','\\nu'),
    ('Xi','\\xi'), ('Sigma','\\sigma'), ('Tau','\\tau'), ('Phi','\\phi'),
    ('Chi','\\chi'), ('Psi','\\psi'), ('Omega','\\omega'),
    ('Eta','\\eta'), ('Zeta','\\zeta'), ('Kappa','\\kappa'), ('Rho','\\rho'),
    # Uppercase Greek (must come before lowercase to avoid partial matches)
    ('CapitalAlpha','A'), ('CapitalBeta','B'), ('CapitalGamma','\\Gamma'),
    ('CapitalDelta','\\Delta'), ('CapitalEpsilon','E'), ('CapitalZeta','Z'),
    ('CapitalEta','H'), ('CapitalTheta','\\Theta'), ('CapitalIota','I'),
    ('CapitalKappa','K'), ('CapitalLambda','\\Lambda'), ('CapitalMu','M'),
    ('CapitalNu','N'), ('CapitalXi','\\Xi'), ('CapitalOmicron','O'),
    ('CapitalPi','\\Pi'), ('CapitalRho','P'), ('CapitalSigma','\\Sigma'),
    ('CapitalTau','T'), ('CapitalUpsilon','\\Upsilon'), ('CapitalPhi','\\Phi'),
    ('CapitalChi','X'), ('CapitalPsi','\\Psi'), ('CapitalOmega','\\Omega'),
]
# Πίνακας αντιστοίχισης WL functions → LaTeX equivalents.
# Χρησιμοποιείται στο wljs_to_latex: Sin[x] → \sin(x) κτλ.
# Μόνο "standard" math functions. Η f[x] → f(x) γενική αντικατάσταση
# γίνεται στο βήμα 7 του wljs_to_latex για πεζά ονόματα.
_WL_FNS = [
    ('Sin','\\sin'), ('Cos','\\cos'), ('Tan','\\tan'), ('Sec','\\sec'),
    ('Csc','\\csc'), ('Cot','\\cot'), ('Sinh','\\sinh'), ('Cosh','\\cosh'),
    ('Tanh','\\tanh'), ('ArcSin','\\arcsin'), ('ArcCos','\\arccos'),
    ('ArcTan','\\arctan'), ('Exp','\\exp'), ('Log','\\ln'),
]


def wljs_to_latex(raw: str) -> str:
    """
    Μετατρέπει WLJS/WL output notation σε LaTeX string.

    Χειρίζεται:
      (*BB[*)(WL_EXPR)(*,*)(*"data"*)(*]BB*) → WL_EXPR (box display hint)
      (*SqB[*)Sqrt[X](*]SqB*)               → \\sqrt{X}
      (*SpB[*)Power[b(*|*),(*|*)e(*]SpB*)   → b^{e}
      (*FB[*)num(*,*)/(*,*)den(*]FB*)        → \\frac{num}{den}
      Derivative[n,m][f][args]               → \\frac{\\partial^n f}{...}(args)
      Sin[x], Cos[x], …                      → \\sin(x), \\cos(x), …
      \\[Pi], \\[Alpha], …                   → \\pi, \\alpha, …
      f[args]                                → f(args)
      ->                                     → \\to
      ==                                     → =
    """
    s = raw.strip("'").strip()
    # Cell data stores '\\\\X' (2 backslashes) for LaTeX '\\X' (1 backslash).
    # Simple replace: \\[ → \[ for all \\[Letter sequences (greek etc.)
    import re as _re
    s = _re.sub(r'(?<=\\)\\(?=[A-Za-z\[])', '', s)


    # ── helpers ───────────────────────────────────────────────────────────────
    def _strip_parens(s):
        """
        1) Εξισορροπεί unbalanced παρενθέσεις (αφαιρεί την πλεονάζουσα
           αριστερά ή δεξιά), 2) αφαιρεί ΟΛΑ τα εξωτερικά balanced ζεύγη.
        Π.χ.: '((1)' → '1',  '(25))' → '25',  '((x+1))' → 'x+1'
        """
        s = s.strip()
        opens, closes = s.count('('), s.count(')')
        for _ in range(opens - closes):
            i = s.find('(');
            if i >= 0: s = s[:i] + s[i+1:]
        for _ in range(closes - opens):
            i = s.rfind(')');
            if i >= 0: s = s[:i] + s[i+1:]
        s = s.strip()
        while s.startswith('(') and s.endswith(')'):
            depth = 0; matched = False
            for i, c in enumerate(s):
                if c == '(': depth += 1
                elif c == ')':
                    depth -= 1
                    if depth == 0:
                        matched = (i == len(s) - 1)
                        break
            if matched: s = s[1:-1].strip()
            else: break
        return s

    def _sqb(m):
        inner = m.group(1).strip()
        mm = re.match(r'Sqrt\[(.*)\]$', inner, re.DOTALL)
        return '\\sqrt{' + (mm.group(1) if mm else inner) + '}'

    def _spb(m):
        b_raw, e_raw = m.group(1).strip(), m.group(2).strip()
        combined = b_raw + ',' + e_raw
        b, e = b_raw, e_raw
        if combined.startswith('Power['):
            # Bracket-depth-aware split: comma at depth 1 inside Power[...]
            # Correctly handles nested (*,*) or other commas inside base
            depth = 0
            for j, c in enumerate(combined):
                if c in '([': depth += 1
                elif c in ')]': depth -= 1
                elif c == ',' and depth == 1:
                    b = combined[6:j].strip()   # after 'Power['
                    e = combined[j+1:-1].strip() # before final ']' of Power
                    break
        if len(b) > 1 and not b.startswith('{'): b = '{' + b + '}'
        return b + '^{' + e + '}'

    def _fb(m):
        n = _strip_parens(m.group(1).strip())
        d = _strip_parens(m.group(2).strip())
        return '\\frac{' + n + '}{' + d + '}'

    def _bb(m):
        """BB box: strip outer parens from WL expression, discard display hint."""
        return m.group(1).strip().strip('(').rstrip(')')

    # ── 1. BB boxes (display hints) ───────────────────────────────────────────
    # Format: (*BB[*)(WL_EXPR)(*,*)(*"base64data"*)(*]BB*)
    # Note: closing of the data comment is "*) i.e. quote-asterisk-paren
    s = re.sub(
        r'\(\*BB\[\*\)(.*?)\(\*,\*\)\(\*"[^"]*"\*\)\(\*\]BB\*\)',
        _bb, s, flags=re.DOTALL)
    # Resolve (Derivative[n,m][f])[args] → Derivative[n,m][f][args]
    s = re.sub(
        r'\(Derivative\[([^\]]+)\]\[([^\]]+)\]\)\[([^\]]*)\]',
        lambda m: f'Derivative[{m.group(1)}][{m.group(2)}][{m.group(3)}]', s)

    # ── 1a. VB (Visual Box with binary data) — Bug #09 ──────────────────────
    # Format: (*VB[*)(WL_EXPR)(*,*)(*"display_data"*)(*]VB*)
    # Πριν τη διόρθωση: ολόκληρο το VB αντικαθίσταται με '[⋯]'.
    # Αποτέλεσμα: τα SeriesData outputs (Taylor/Fourier series) δεν εμφανίζονταν.
    # Μετά τη διόρθωση: εξάγεται η WL_EXPR και μεταφράζεται σε LaTeX.
    # ΕΞΑΙΡΕΣΗ: FrontEndRef/Legended/ToExpression → '[⋯]' γιατί αυτά
    #   χειρίζονται αλλού (ως Graphics UUID references στο cell render loop).
    # Bug #26: Τα Legended[FrontEndRef["uuid"], BarLegend[...]] cells
    #   ΠΡΕΠΕΙ να φτάνουν ακέραια στο render loop (δεν καταναλώνονται εδώ)
    #   ώστε να αποδοθεί το γράφημα + η colorbar μαζί.
    def _extract_vb(m):
        inner = m.group(1).strip('()')
        # Skip graphics wrappers handled elsewhere
        if re.match(r'(?:FrontEndRef|Legended|ToExpression)\b', inner): return '[\u22ef]'
        return inner
    s = re.sub(r'\(\*VB\[\*\)(.*?)\(\*,\*\).*?\(\*\]VB\*\)', _extract_vb, s, flags=re.DOTALL)


    # ── 1a2. SeriesData → LaTeX power series — Bug #10 ───────────────────────
    # SeriesData[var, center, {c0,c1,...,ck}, nmin, nmax, den]
    # Αναπαριστά: Σ_{j=0}^{k} c_j * (var-center)^((nmin+j)/den) + O((var-center)^(nmax/den))
    # Παράδειγμα: SeriesData[x, Pi, {Pi^2, -5+2Pi, 1, 5/6}, 0, 11, 1]
    #   → π² + (-5+2π)(x-π) + (x-π)² + (5/6)(x-π)³ + O((x-π)^11)
    # Χρησιμοποιείται για Taylor/Fourier series output από Series[] στο Mathematica.
    def _seriesdata_to_latex(m):
        inner = m.group(0)
        # Parse: SeriesData[var, center, {c0,c1,...}, nmin, nmax, den]
        sm = re.match(r'SeriesData\s*\[\s*(\w+)\s*,\s*([^,]+)\s*,\s*\{([^}]*)\}\s*,\s*([-\d]+)\s*,\s*([-\d]+)\s*,\s*(\d+)\s*\]', inner)
        if not sm: return inner
        var, center, coefs_str, nmin_s, nmax_s, den_s = sm.groups()
        nmin, nmax, den = int(nmin_s), int(nmax_s), int(den_s)
        # Parse coefficients (split by top-level commas)
        coefs_raw = []; depth2=0; cur2=''
        for ch in coefs_str:
            if ch in '([{': depth2+=1
            elif ch in ')]}': depth2-=1
            if ch==',' and depth2==0: coefs_raw.append(cur2.strip()); cur2=''
            else: cur2+=ch
        if cur2.strip(): coefs_raw.append(cur2.strip())
        # Build LaTeX terms
        def _coef_latex(c):
            c=c.strip()
            c=re.sub(r'Pi\^(\d+)', r'\\pi^{\1}', c)
            c=c.replace('Pi','\\pi').replace('Sqrt[3]','\\sqrt{3}').replace('Sqrt[2]','\\sqrt{2}')
            return c
        def _var_term(exp_num, den_v, var_v, center_v):
            if den_v==1: exp=exp_num
            else: exp=f'{exp_num}/{den_v}'
            if center_v.strip() in ('0','0.','0.0'):
                base=var_v
            else:
                base=f'({var_v}-{_coef_latex(center_v)})'
            if exp==0 or exp=='0': return ''
            if exp==1 or exp=='1': return base
            return f'{base}^{{{exp}}}'
        terms=[]
        for j, coef in enumerate(coefs_raw):
            exp_num = nmin + j
            c=coef.strip()
            if c in ('0','0.'): continue
            c_lat = _coef_latex(c)
            vt = _var_term(exp_num, den, var, center)
            if vt:
                if c in ('1','1.'): terms.append(vt)
                elif c in ('-1','-1.'): terms.append(f'-{vt}')
                else: terms.append(f'({c_lat}){vt}' if len(c_lat)>2 else f'{c_lat} {vt}')
            else:
                terms.append(c_lat)
        # O() remainder
        o_exp = _var_term(nmax, den, var, center)
        o_term = f'+O({o_exp})' if o_exp else ''
        if not terms: return f'O({o_exp})'
        result_parts=[terms[0]]
        for t in terms[1:]:
            if t.startswith('-'): result_parts.append(t)
            else: result_parts.append(f'+{t}')
        return ''.join(result_parts) + o_term
    s = re.sub(r'SeriesData\s*\[.*?\]', _seriesdata_to_latex, s, flags=re.DOTALL)

    # ── 1b. TB (Template Box) — ConditionalExpression, Piecewise etc. ──────────
    _TB_PIPE = '\x01PIPE\x01'
    def _decode_tb(m):
        inner = m.group(1)
        inner = re.sub(r'\(\*1:[A-Za-z0-9+/=]*\*\)', '', inner)
        # Check if this is Piecewise[{{val,cond},...}] → \begin{cases}
        if re.match(r'\s*Piecewise\[', inner, re.DOTALL):
            # Protect (*|*) inside nested SpB/FB/SqB/BB boxes before splitting
            _OPEN_BOXES  = ['(*SpB[*)', '(*FB[*)', '(*SqB[*)', '(*BB[*)', '(*GB[*)', '(*SbB[*)']
            _CLOSE_BOXES = ['(*]SpB*)', '(*]FB*)', '(*]SqB*)', '(*]BB*)', '(*]GB*)', '(*]SbB*)']
            _PIPE_PH = '\x01P\x01'
            def _protect_pipe(s):
                buf=[]; idx=0; depth=0
                while idx < len(s):
                    found = False
                    for tag in _OPEN_BOXES:
                        if s[idx:idx+len(tag)] == tag:
                            depth += 1; buf.append(tag); idx += len(tag); found=True; break
                    if found: continue
                    for tag in _CLOSE_BOXES:
                        if s[idx:idx+len(tag)] == tag:
                            depth = max(0,depth-1); buf.append(tag); idx += len(tag); found=True; break
                    if found: continue
                    if s[idx:idx+5] == '(*|*)':
                        buf.append(_PIPE_PH if depth > 0 else '(*|*)'); idx += 5
                    else:
                        buf.append(s[idx]); idx += 1
                return ''.join(buf)
            protected = _protect_pipe(inner)
            pairs = re.findall(
                r'\{\(\*\|\*\)(.*?)\(\*\|\*\),\(\*\|\*\)(.*?)\(\*\|\*\)\}',
                protected, re.DOTALL)
            if pairs:
                rows = []
                for val_prot, cond_prot in pairs:
                    val_raw  = val_prot.replace(_PIPE_PH, '(*|*)')
                    cond_raw = cond_prot.replace(_PIPE_PH, '(*|*)')
                    val  = re.sub(r'\(\*TB\[\*\)(.*?)\(\*\]TB\*\)', _decode_tb, val_raw, flags=re.DOTALL)
                    cond = re.sub(r'\(\*TB\[\*\)(.*?)\(\*\]TB\*\)', _decode_tb, cond_raw, flags=re.DOTALL)
                    val_tex  = wljs_to_latex(val)  if val.strip()  else val
                    cond_tex = wljs_to_latex(cond) if cond.strip() else cond
                    cond_tex = cond_tex.replace('&&','\\mathbin{\\&\\&}').replace('||','\\mathbin{|}')
                    cond_tex = cond_tex.replace('==','=')
                    rows.append(f'{val_tex} & {cond_tex}')
                return '\\begin{cases}' + ' \\\\ '.join(rows) + '\\end{cases}'
        # Default: strip TB wrapper, protect (*|*) inside nested boxes
        def _prot(mm): return mm.group(0).replace('(*|*)', _TB_PIPE)
        inner = re.sub(r'\(\*(?:SpB|FB|SqB|BB)\[\*\).*?\(\*\](?:SpB|FB|SqB|BB)\*\)',
                       _prot, inner, flags=re.DOTALL)
        inner = inner.replace('(*|*)', '')
        inner = inner.replace(_TB_PIPE, '(*|*)')
        return inner.strip()
    for _ in range(6):
        s = re.sub(r'\(\*TB\[\*\)(.*?)\(\*\]TB\*\)', _decode_tb, s, flags=re.DOTALL)

    # ── 2. SqB / SpB / FB / SbB (innermost-first loop) ────────────────────────
    def _sbb(m):
        """SbB (SubscriptBox): Subscript[base(*|*),(*|*)sub] → base_{sub}"""
        inner = m.group(1).strip()
        # Parse Subscript[base, sub] splitting on (*|*),(*|*)
        sub_m = re.match(r'Subscript\[(.*?)\(\*\|\*\),\(\*\|\*\)(.*?)\]$', inner, re.DOTALL)
        if sub_m:
            base = sub_m.group(1).strip()
            sub  = sub_m.group(2).strip()
            return base + '_{' + sub + '}'
        return inner

    prev = None
    while s != prev:
        prev = s
        s = re.sub(
            r'\(\*SqB\[\*\)((?:(?!\(\*SqB\[\*\)).)*?)\(\*\]SqB\*\)',
            _sqb, s, flags=re.DOTALL)
        s = re.sub(
            r'\(\*SpB\[\*\)((?:(?!\(\*SpB\[\*\)).)*?)\(\*\|\*\),\(\*\|\*\)'            r'((?:(?!\(\*SpB\[\*\)).)*?)\(\*\]SpB\*\)',
            _spb, s, flags=re.DOTALL)
        s = re.sub(
            r'\(\*FB\[\*\)((?:(?!\(\*FB\[\*\)).)*?)\(\*,\*\)/\(\*,\*\)'            r'((?:(?!\(\*FB\[\*\)).)*?)\(\*\]FB\*\)',
            _fb, s, flags=re.DOTALL)
        s = re.sub(
            r'\(\*SbB\[\*\)((?:(?!\(\*SbB\[\*\)).)*?)\(\*\]SbB\*\)',
            _sbb, s, flags=re.DOTALL)

    # ── 3. Greek / special symbols  \\[Name] ─────────────────────────────────
    for name, latex in _GREEK:
        s = s.replace('\\[' + name + ']', latex + ' ')

    # ── 4. Derivative[n,m][f][args] → LaTeX ──────────────────────────────────
    # Use superscript notation f^{(n,m)}(args) — safe even when args are
    # evaluated values (e.g. [0,t] instead of [t,x]).
    def _deriv(m):
        orders   = m.group(1)   # e.g. "1,0"
        func     = m.group(2)   # e.g. "u"
        args     = m.group(3)   # e.g. "t,x" or "0,t"
        order_list = [int(x.strip()) for x in orders.split(',')]
        total    = sum(order_list)
        if total == 0:
            return func + '(' + args + ')'
        return func + '^{(' + orders + ')}(' + args + ')'
    s = re.sub(r'Derivative\[([^\]]+)\]\[([^\]]+)\]\[([^\]]*)\]', _deriv, s)

    # ── 4b. ConditionalExpression → LaTeX ─────────────────────────────────────
    # Bracket-depth-aware: find full ConditionalExpression[...] extent
    ci = 0
    while True:
        ci = s.find('ConditionalExpression[', ci)
        if ci < 0: break
        start = ci + len('ConditionalExpression[')
        depth = 1; j2 = start
        while j2 < len(s) and depth > 0:
            if s[j2] in '([{': depth += 1
            elif s[j2] in ')]}': depth -= 1
            j2 += 1
        inner = s[start:j2-1]
        # Split inner on first comma at depth 0
        dep2 = 0; split_at = -1
        for ki, kc in enumerate(inner):
            if kc in '([{': dep2 += 1
            elif kc in ')]}': dep2 -= 1
            elif kc == ',' and dep2 == 0:
                split_at = ki; break
        if split_at >= 0:
            el = wljs_to_latex("'" + inner[:split_at].strip() + "'")
            cl = wljs_to_latex("'" + inner[split_at+1:].strip() + "'")
            repl = el + r'\,\text{ if }\,' + cl
        else:
            repl = wljs_to_latex("'" + inner + "'")
        s = s[:ci] + repl + s[j2:]
        ci += len(repl)

    # ── 5. Residual WL constructs ─────────────────────────────────────────────
    s = re.sub(r'Sqrt\[([^\[\]]+)\]',
               lambda m: '\\sqrt{' + m.group(1) + '}', s)
    s = re.sub(r'Power\[([^,\[\]]+),([^\[\]]+)\]',
               lambda m: '{' + m.group(1).strip() + '}^{' + m.group(2).strip() + '}', s)

    # ── 5b. Integrate[f, {var, lo, hi}] → \int_{lo}^{hi} f \,d{var} ─────────
    def _integrate_to_latex(s_in):
        """Recursively convert Integrate[...] to LaTeX integral notation."""
        # Match outermost Integrate[expr, {var, lo, hi}]
        # Use depth-aware bracket matching
        result = []
        i = 0
        while i < len(s_in):
            if s_in[i:i+10] == 'Integrate[':
                # Find matching closing bracket
                depth = 0
                j = i + 9  # start at '['
                while j < len(s_in):
                    if s_in[j] in '[{(': depth += 1
                    elif s_in[j] in ']}(':
                        depth -= 1
                        if depth == 0: break
                    j += 1
                # s_in[i+10:j] is the content inside Integrate[...]
                content = s_in[i+10:j]
                # Split into arguments at top-level commas
                args = []
                cur = []; d = 0
                for ch in content:
                    if ch in '[{(': d += 1; cur.append(ch)
                    elif ch in ']}': d -= 1; cur.append(ch)
                    elif ch == ',' and d == 0: args.append(''.join(cur).strip()); cur = []
                    else: cur.append(ch)
                if cur: args.append(''.join(cur).strip())
                # args[0]=expr, args[1]={var, args[2]=lo, args[3]=hi}
                if len(args) >= 2:
                    expr_part = args[0]
                    limits_str = ','.join(args[1:])
                    # Extract {var, lo, hi} from limits_str
                    lm = re.match(r'\{([^,}]+),([^,}]+),([^,}]+)\}', limits_str.strip())
                    if lm:
                        var = lm.group(1).strip()
                        lo  = lm.group(2).strip()
                        hi  = lm.group(3).strip()
                        inner_expr = _integrate_to_latex(expr_part)
                        result.append(f'\\int_{{{lo}}}^{{{hi}}} {inner_expr} \\,d{var}')
                    else:
                        result.append('\\int ' + _integrate_to_latex(expr_part))
                else:
                    result.append('Integrate(' + content + ')')
                i = j + 1
            else:
                result.append(s_in[i])
                i += 1
        return ''.join(result)
    s = _integrate_to_latex(s)

    # ── 5b2. Abs[expr] → \left|expr\right| ──────────────────────────────────
    def _replace_abs(s_in):
        result = []
        i = 0
        while i < len(s_in):
            if s_in[i:i+4] == 'Abs[':
                # Find balanced closing bracket
                depth = 0
                j = i + 3  # at '['
                while j < len(s_in):
                    if s_in[j] in '[{(': depth += 1
                    elif s_in[j] in ']}':
                        depth -= 1
                        if depth == 0: break
                    j += 1
                inner = _replace_abs(s_in[i+4:j])
                result.append(r'\left|' + inner + r'\right|')
                i = j + 1
            else:
                result.append(s_in[i]); i += 1
        return ''.join(result)
    s = _replace_abs(s)

    # ── 5c. TemplateBox[{}, Domain] → Domain name ──────────────────────────────
    s = re.sub(r'TemplateBox\[\{[^}]*\},\s*(\w+)\]', lambda m: m.group(1), s)

    # ── 6. Named math functions Sin[x] → \sin(x) ─────────────────────────────
    for wl, lt in _WL_FNS:
        s = re.sub(r'\b' + wl + r'\b', lambda m, lt=lt: lt, s)
    # After substitution, Sin[x] → \sin[x] — fix remaining brackets
    s = re.sub(r'(\\[a-z]+)\[([^\[\]]*)\]', r'\1(\2)', s)

    # ── 7. Lowercase f[args] → f(args)  (skip uppercase = WL symbols) ────────
    s = re.sub(r'\b([a-z][a-zA-Z0-9]*)\[([^\[\]]*)\]',
               lambda m: m.group(1) + '(' + m.group(2) + ')', s)

    # ── 8. Operators ──────────────────────────────────────────────────────────
    s = s.replace('->', '\\to ')
    s = s.replace('==', '=')
    s = s.rstrip("'").strip()
    return s



def decode_gb(raw: str) -> list | None:
    """
    Αποκωδικοποιεί (*GB[*) GRID (*]GB*) σε λίστα γραμμών x λίστα κελιών.
    Χρησιμοποιεί depth-aware split ώστε τα (*|*) μέσα σε SpB/FB να μη
    μπερδεύονται με τους διαχωριστές κελιών/γραμμών του GB.

    Bug #27 (MatrixForm output): το WLJS τυλίγει το GB box σε εξωτερικές
    παρενθέσεις: ((*GB[*){{...}}(*]GB*))  αντί  (*GB[*){{...}}(*]GB*)
    Το αρχικό regex ^(*GB[*) απέτυχε → decode_gb επέστρεφε None →
    format_gb_matrix επέστρεφε '' → κανένα output cell δεν εμφανιζόταν.
    Fix: αφαιρούμε πρώτα τυχόν εξωτερικό ( ) wrapper πριν το match.
    """
    s = raw.strip("'").strip()
    # Bug #27 fix: strip outer ( ) that WLJS wraps around the GB expression
    s = re.sub(r'^\((\(\*GB\[\*\).*\(\*\]GB\*\))\)$', r'\1', s, flags=re.DOTALL)
    m = re.match(r'^\(\*GB\[\*\)(.*)\(\*\]GB\*\)$', s, re.DOTALL)
    if not m:
        return None
    inner = m.group(1)
    # Αφαίρεση compressed display hint: (*1:BASE64*)
    inner = re.sub(r'\(\*1:[A-Za-z0-9+/=]*\*\)', '', inner).strip().rstrip(',').strip()
    # Πρώτα αφαιρούμε τυχόν trailing (*||*) που απομένει μετά τα }}
    inner = re.sub(r'\(\*\|\|\*\)\s*$', '', inner).strip()
    # Outer {{ and }} wrapping
    if inner.startswith('{{'):  inner = inner[2:]
    elif inner.startswith('{'): inner = inner[1:]
    if inner.endswith('}}'):    inner = inner[:-2]
    elif inner.endswith('}'):   inner = inner[:-1]
    inner = inner.strip()

    def split_depth(s, sep_pattern, open_tags, close_tags):
        """Split string by sep_pattern only when not inside nested boxes."""
        depth = 0
        result = []
        current = []
        i = 0
        while i < len(s):
            # Open tag?
            om = None
            for tag in open_tags:
                tm = re.match(re.escape(tag), s[i:])
                if tm: om = tm; break
            if om:
                depth += 1
                current.append(om.group())
                i += len(om.group())
                continue
            # Close tag?
            cm = None
            for tag in close_tags:
                tm = re.match(re.escape(tag), s[i:])
                if tm: cm = tm; break
            if cm:
                depth = max(0, depth - 1)
                current.append(cm.group())
                i += len(cm.group())
                continue
            # Separator at depth 0?
            sm = re.match(sep_pattern, s[i:])
            if sm and depth == 0:
                result.append(''.join(current).strip())
                current = []
                i += len(sm.group())
                continue
            current.append(s[i])
            i += 1
        if current:
            result.append(''.join(current).strip())
        return result

    OPEN_TAGS  = ['(*SpB[*)', '(*FB[*)', '(*SqB[*)', '(*BB[*)', '(*GB[*)']
    CLOSE_TAGS = ['(*]SpB*)', '(*]FB*)', '(*]SqB*)', '(*]BB*)', '(*]GB*)']
    ROW_SEP    = r'\(\*\|\|\*\)\s*,\s*\(\*\|\|\*\)'
    CELL_SEP   = r'\(\*\|\*\)\s*,\s*\(\*\|\*\)'

    rows_raw = split_depth(inner, ROW_SEP, OPEN_TAGS, CLOSE_TAGS)
    rows = []
    for row_str in rows_raw:
        row_str = row_str.strip()
        if row_str.startswith('{'):  row_str = row_str[1:]
        if row_str.endswith('}'):    row_str = row_str[:-1]
        row_str = row_str.strip()
        if not row_str:
            continue
        cells = split_depth(row_str, CELL_SEP, OPEN_TAGS, CLOSE_TAGS)
        rows.append([c.strip() for c in cells])
    return rows if rows else None


def format_gb_matrix(raw: str) -> str:
    """Μετατρέπει GB matrix σε HTML table με LaTeX σε κάθε κελί."""
    rows = decode_gb(raw)
    if not rows:
        return ''
    # Βρίσκουμε αν είναι column vector (1 στήλη) ή πίνακας
    n_cols = max(len(r) for r in rows)
    # Κατασκευή LaTeX pmatrix
    latex_rows = []
    for row in rows:
        cells_latex = [wljs_to_latex("'" + cell + "'") for cell in row]
        latex_rows.append(' & '.join(cells_latex))
    latex = '\\begin{pmatrix} ' + ' \\\\ '.join(latex_rows) + ' \\end{pmatrix}'
    return (f'<div class="math-output">'
            f'<div class="math-display">\\[{latex}\\]</div></div>')


def is_wl_output(data: str) -> bool:
    """
    True αν το data περιέχει WLJS box tags, Derivative, WL functions,
    ή WL square-bracket notation — δηλ. χρειάζεται μετατροπή σε LaTeX.
    """
    if any(tok in data for tok in
           ('(*SqB[*)', '(*SpB[*)', '(*FB[*)', '(*BB[*)', '(*GB[*)', '(*TB[*)',
            '(*SbB[*)', '(*VB[*)')):
        return True
    s = data.strip("'").strip()
    # WL named character escape: \\[Name] e.g. \\[Pi], \\[Alpha]
    if '\\[' in s:
        return True
    # WL function call  f[...] ή Derivative ή ==
    if re.search(r'\b[A-Za-z][A-Za-z0-9]*\[', s):
        return True
    if '==' in s or '->' in s:
        return True
    return False


def format_wl_output(data: str) -> str:
    """Μετατρέπει WL/WLJS output σε HTML με LaTeX μέσω MathJax."""
    # GB matrix: ειδική αντιμετώπιση
    if '(*GB[*)' in data:
        return format_gb_matrix(data)
    latex = wljs_to_latex(data)
    if not latex:
        return ''
    # Display mode: λύσεις ({...→...}) ή εξισώσεις με =
    is_display = (latex.startswith('{{') or latex.startswith('\\{')
                  or ('=' in latex and len(latex) > 6)
                  or '\\frac' in latex or '\\begin' in latex
                  or len(latex) > 60)
    if is_display:
        return (f'<div class="math-output">'
                f'<div class="math-display">\\[{latex}\\]</div></div>')
    else:
        return (f'<div class="math-output">'
                f'<span class="math-inline">\\({latex}\\)</span></div>')


def format_plain_output(data: str) -> str:
    """Απλό output χωρίς WL notation — εμφανίζεται ως monospace."""
    s = data.strip("'").strip()
    if not s or s == '{}':
        return ''
    esc = s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    return f'<div class="math-output"><code class="plain-out">{esc}</code></div>'


# ══════════════════════════════════════════════════════════════════════════════
# RASTERIZED IMAGE → base64 PNG
# ══════════════════════════════════════════════════════════════════════════════

def image_to_b64(img_data):
    if not HAS_PIL: return None
    rows = img_data[1][1][1:]
    h = len(rows); w = len(rows[0]) - 1
    pixels = []
    for row in rows:
        for px in row[1:]:
            if isinstance(px, list): pixels.append((int(px[1]), int(px[2]), int(px[3])))
            else: pixels.append((0,0,0))
    img = PILImage.new('RGB', (w,h)); img.putdata(pixels)
    buf = io.BytesIO(); img.save(buf,'PNG',optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()



def densityplot_to_b64(gexpr):
    """
    Converts a Graphics[GraphicsComplex[coords, primitives, Rule[VertexColors,...]]]
    (DensityPlot, ContourPlot etc.) to a base64 PNG via triangle rasterization.
    Returns (b64_png_data_uri, xmin, xmax, ymin, ymax) or None.
    """
    if not HAS_PIL: return None
    try:
        import numpy as np
    except ImportError:
        return None

    def _lab2rgb(L, a, b):
        """Pure-numpy CIE L*a*b* → sRGB (D65). No external deps."""
        # L*a*b* (Mathematica normalised: L∈[0,1], a/b∈[-1,1]) → CIE scale
        L_cie = L * 100.0
        a_cie = a * 128.0
        b_cie = b * 128.0
        # Lab → XYZ (D65 white point)
        fy = (L_cie + 16.0) / 116.0
        fx = a_cie / 500.0 + fy
        fz = fy - b_cie / 200.0
        def f_inv(t):
            return np.where(t > 0.20689303442, t ** 3, (t - 16.0 / 116.0) / 7.787)
        X = f_inv(fx) * 0.95047
        Y = f_inv(fy) * 1.00000
        Z = f_inv(fz) * 1.08883
        # XYZ → linear RGB (sRGB primaries)
        R =  3.2406 * X - 1.5372 * Y - 0.4986 * Z
        G = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
        B =  0.0557 * X - 0.2040 * Y + 1.0570 * Z
        # Gamma correction (linear → sRGB)
        def gamma(c):
            return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(np.clip(c, 0, None), 1/2.4) - 0.055)
        return np.clip(np.stack([gamma(R), gamma(G), gamma(B)], axis=-1), 0.0, 1.0)

    if not isinstance(gexpr, list) or gexpr[0] != 'Graphics': return None
    prim_outer = gexpr[1] if len(gexpr) > 1 else None
    if not isinstance(prim_outer, list) or prim_outer[0] != 'List': return None

    # Find GraphicsComplex in the primitive list
    gc = None
    for item in prim_outer[1:]:
        if isinstance(item, list) and item[0] == 'GraphicsComplex':
            gc = item; break
    if gc is None: return None

    # Must have VertexColors rule
    vc_rule = None
    for item in gc:
        if isinstance(item, list) and item[0] == 'Rule' and 'VertexColors' in str(item[1]):
            vc_rule = item; break
    if vc_rule is None: return None

    # Extract coords
    coords_raw = gc[1][1:]  # List items ['List', x, y]
    if not coords_raw: return None
    coords = np.array([[float(c[1]), float(c[2])] for c in coords_raw])
    xmin, xmax = coords[:,0].min(), coords[:,0].max()
    ymin, ymax = coords[:,1].min(), coords[:,1].max()
    if xmax == xmin or ymax == ymin: return None

    # Extract triangles: find Polygon inside GraphicsComplex primitives
    tris = []
    def find_polygons(obj):
        if not isinstance(obj, list): return
        if obj and obj[0] == 'Polygon' and len(obj) > 1:
            poly_data = obj[1]
            if isinstance(poly_data, list) and poly_data[0] == 'List':
                for tri in poly_data[1:]:
                    if isinstance(tri, list) and tri[0] == 'List' and len(tri) == 4:
                        tris.append((int(tri[1])-1, int(tri[2])-1, int(tri[3])-1))
        else:
            for item in obj[1:]:
                find_polygons(item)
    find_polygons(gc[2])
    if not tris:
        # ── Fallback: try Point-based scatter (ListPlot with ColorFunction) ──
        # Bug #12 (scatter): Τα bifurcation diagram και scatter plots με
        # ColorFunction αποθηκεύουν τις τιμές ως Points με VertexColors,
        # χωρίς τρίγωνα. Χρησιμοποιούμε pixel-level rasterization αντί
        # triangle fill. Κάθε σημείο = 1 pixel στο τελικό PNG.
        pt_indices = []
        def find_points(obj):
            if not isinstance(obj, list): return
            if obj and obj[0] == 'Point' and len(obj) > 1:
                pd = obj[1]
                if isinstance(pd, list) and pd[0] == 'List':
                    for idx in pd[1:]:
                        if isinstance(idx, (int, float)):
                            pt_indices.append(int(idx)-1)
                return
            for item in obj[1:]: find_points(item)
        find_points(gc[2])
        if not pt_indices: return None

        # Convert VertexColors
        vc_list = vc_rule[2][1:]
        def lab_to_rgb_arr2(c):
            if not isinstance(c, list): return np.array([0.5,0.5,0.5])
            h = c[0]
            if h == 'LABColor': return _lab2rgb(float(c[1]), float(c[2]), float(c[3]))
            elif h in ('RGBColor', 'List') and len(c) >= 4:
                return np.clip([float(c[1]),float(c[2]),float(c[3])], 0, 1)
            elif h == 'GrayLevel': v=float(c[1]); return np.array([v,v,v])
            return np.array([0.5,0.5,0.5])

        vc = np.array([lab_to_rgb_arr2(c) for c in vc_list])

        # Rasterize: 1-pixel dots
        IMG_W, IMG_H = 600, 400
        from PIL import Image
        bg_arr = np.zeros((IMG_H, IMG_W, 3), dtype=np.uint8)
        # Background from Graphics option (default black for bifurcation)
        # Use coord bounding box (coords is Nx2 numpy array)
        pt_idx_arr = np.array([i for i in pt_indices if i < len(coords)], dtype=np.int32)
        if len(pt_idx_arr) == 0: return None
        xs_arr = coords[pt_idx_arr, 0]
        ys_arr = coords[pt_idx_arr, 1]
        xmin2, xmax2 = float(xs_arr.min()), float(xs_arr.max())
        ymin2, ymax2 = float(ys_arr.min()), float(ys_arr.max())
        if xmax2==xmin2: xmax2=xmin2+1
        if ymax2==ymin2: ymax2=ymin2+1

        img = Image.new('RGB', (IMG_W, IMG_H), (0, 0, 0))
        img_arr = np.array(img)
        for idx_v in pt_idx_arr:
            if idx_v >= len(vc): continue
            cx, cy = float(coords[idx_v, 0]), float(coords[idx_v, 1])
            px = int((cx - xmin2) / (xmax2 - xmin2) * (IMG_W-1))
            py = IMG_H - 1 - int((cy - ymin2) / (ymax2 - ymin2) * (IMG_H-1))
            if 0 <= px < IMG_W and 0 <= py < IMG_H:
                img_arr[py, px] = (vc[idx_v]*255).astype(np.uint8)

        img2 = Image.fromarray(img_arr)
        import io as _io2, base64 as _b64_2
        buf2 = _io2.BytesIO(); img2.save(buf2, 'PNG')
        b64 = 'data:image/png;base64,' + _b64_2.b64encode(buf2.getvalue()).decode()
        return b64, xmin2, xmax2, ymin2, ymax2

    # Convert VertexColors to RGB
    vc_list = vc_rule[2][1:]  # remove 'List' head
    def lab_to_rgb_arr(lab_color):
        h = lab_color[0] if isinstance(lab_color, list) else ''
        if h == 'LABColor':
            L, a, b = float(lab_color[1]), float(lab_color[2]), float(lab_color[3])
            return _lab2rgb(np.float64(L), np.float64(a), np.float64(b))
        elif h == 'RGBColor' and len(lab_color) >= 4:
            return np.clip([float(lab_color[1]), float(lab_color[2]), float(lab_color[3])], 0, 1)
        elif h == 'GrayLevel':
            v = float(lab_color[1]); return np.array([v, v, v])
        elif h == 'List' and len(lab_color) >= 4:
            # Raw RGB triple: List[r, g, b] (used by ColorFunction-based plots)
            return np.clip([float(lab_color[1]), float(lab_color[2]), float(lab_color[3])], 0, 1)
        return np.array([0.5, 0.5, 0.5])

    vc = np.array([lab_to_rgb_arr(c) for c in vc_list])

    # Rasterize: render triangles with average vertex color
    IMG_W, IMG_H = 400, 400
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new('RGB', (IMG_W, IMG_H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    def to_px(x, y):
        px = int((x - xmin) / (xmax - xmin) * (IMG_W - 1))
        py = int((1.0 - (y - ymin) / (ymax - ymin)) * (IMG_H - 1))
        return (max(0, min(IMG_W-1, px)), max(0, min(IMG_H-1, py)))

    tris_np = np.array(tris, dtype=np.int32)
    n_coords = len(coords)
    for tri in tris_np:
        i, j, k = int(tri[0]), int(tri[1]), int(tri[2])
        if i >= n_coords or j >= n_coords or k >= n_coords: continue
        p1 = to_px(coords[i,0], coords[i,1])
        p2 = to_px(coords[j,0], coords[j,1])
        p3 = to_px(coords[k,0], coords[k,1])
        avg_color = (vc[i] + vc[j] + vc[k]) / 3
        c = tuple(int(v*255) for v in avg_color[:3])
        draw.polygon([p1, p2, p3], fill=c)

    import io, base64
    buf = io.BytesIO()
    img.save(buf, 'PNG')
    b64 = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    return b64, xmin, xmax, ymin, ymax


def raster_to_b64(gexpr):
    """Converts a Graphics[Raster[...]] to a base64 PNG.

    Η WL Raster[] primitive περιέχει έναν 2D πίνακα RGB τιμών (0-1).
    Χρησιμοποιείται από το MatrixPlot, ArrayPlot και άλλα raster outputs.
    Σημαντικό quirk: τα Raster rows είναι bottom-to-top (WL y-convention),
    οπότε γίνεται flip για σωστό orientation.
    Τα μικρά rasters (π.χ. 5x5 από MatrixPlot) scale-up x10-80 για ορατότητα."""
    if not HAS_PIL: return None
    if not isinstance(gexpr, list) or gexpr[0] != 'Graphics': return None
    prim = gexpr[1] if len(gexpr) > 1 else None
    if not isinstance(prim, list) or prim[0] != 'Raster': return None
    pixel_data = prim[1]  # List of rows
    if not isinstance(pixel_data, list) or pixel_data[0] != 'List': return None
    rows = pixel_data[1:]
    if not rows: return None
    h = len(rows)
    first_row = rows[0]
    cols = first_row[1:] if isinstance(first_row, list) and first_row[0] == 'List' else []
    w = len(cols)
    if w == 0: return None
    pixels = []
    # Raster rows are bottom-to-top, flip for correct orientation
    for row in reversed(rows):
        row_pixels = row[1:] if isinstance(row, list) and row[0] == 'List' else []
        for px in row_pixels:
            if isinstance(px, list) and len(px) >= 4:
                r, g, b = int(px[1]*255), int(px[2]*255), int(px[3]*255)
            elif isinstance(px, list) and len(px) == 3:
                r, g, b = int(px[0]*255), int(px[1]*255), int(px[2]*255)
            elif isinstance(px, (int, float)):
                v = int(px*255); r, g, b = v, v, v
            else: r, g, b = 0, 0, 0
            pixels.append((r, g, b))
    if len(pixels) != w * h: return None
    img = PILImage.new('RGB', (w, h))
    img.putdata(pixels)
    # Scale up for visibility - ensure minimum 400px for readability
    target = 400
    scale = max(1, min(80, target // max(w, h)))
    if scale > 1:
        img = img.resize((w*scale, h*scale), PILImage.NEAREST)
    buf = io.BytesIO(); img.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


# ══════════════════════════════════════════════════════════════════════════════
# GRAPHICS3D → matplotlib PNG  (Bugs #13, #24, #25)
# ══════════════════════════════════════════════════════════════════════════════
# Τα 3D γραφήματα (Plot3D, ParametricPlot3D, VectorPlot3D) αποθηκεύονται
# στο WLJS ως Graphics3D expression trees. Δεν μπορούν να αποδοθούν σε SVG
# (SVG είναι 2D). Χρησιμοποιούμε matplotlib/mpl_toolkits.mplot3d για rendering
# σε PNG, base64-encoded.
#
# Bug #13 (αρχικό): Τα VB-wrapped cells (FrontEndRef["uuid"]) δεν αναλύονταν
# σωστά στο gmap resolve pass, με αποτέλεσμα το g3d_to_b64_matplotlib() να
# μην καλείται ποτέ. Μετά τη διόρθωση του VB handler και του gmap UUID
# resolution (2-level alias chain), τα Graphics3D αντικείμενα φτάνουν σωστά.
#
# Bug #24 (ParametricPlot3D): Η g3d_to_b64_matplotlib() χειριζόταν μόνο
# Polygon/GraphicsComplex (3D επιφάνειες). Τα ParametricPlot3D curves
# αποθηκεύονται ως Line[{pt1,pt2,...}] → προστέθηκε ax.plot3D() branch.
#
# Bug #25 (VectorPlot3D): Τα 3D διανυσματικά πεδία αποθηκεύονται ως
# Arrow[Tube[{p1,p2}, r]] με LABColor χρωματισμό ανά βέλος.
# Προστέθηκε ax.quiver() branch με LABColor→RGB μετατροπή.
#
# Τρεις τύποι Graphics3D περιεχομένου:
#   1. Polygon/GraphicsComplex  → 3D επιφάνεια (Plot3D, ParametricPlot3D surface)
#   2. Line                     → 3D καμπύλη   (ParametricPlot3D curve: x(t),y(t),z(t))
#   3. Arrow[Tube[{p1,p2},r]]  → 3D διάνυσμα  (VectorPlot3D)

def g3d_to_b64_matplotlib(g3d_expr):
    """Αποδίδει Graphics3D expression σε PNG base64 string μέσω matplotlib.
    
    ΙΣΤΟΡΙΚΟ: Αρχικά χειριζόταν μόνο Polygon (Plot3D, ContourPlot3D).
    Μετά από bug reports επεκτάθηκε για τρεις τύπους:
    
    1. Polygon/GraphicsComplex  → 3D surface (τρίγωνα με φωτισμό)
       Χρήση: Plot3D, ContourPlot3D, ParametricPlot3D (surface version)
       Παράμετροι: VertexColors για ColorFunction gradients
    
    2. Line[{pt1,pt2,...}]      → 3D καμπύλη (ax.plot3D)
       Χρήση: ParametricPlot3D curve, e.g. {Sin[t], Cos[t], t}
       Bug fix #24: πριν επέστρεφε None → "[3D — pip install matplotlib]"
    
    3. Arrow[Tube[{p1,p2},r]]   → 3D διανυσματικό βέλος (ax.quiver)
       Χρήση: VectorPlot3D — χρωματισμός από LABColor directive
       Bug fix #25: πριν επέστρεφε None → "[3D — pip install matplotlib]"
    
    Επιστρέφει: 'data:image/png;base64,...' string ή None αν αποτύχει.
    Απαιτεί: matplotlib, numpy (HAS_MPL, HAS_NP flags).
    """
    # Handles THREE types of Graphics3D content (Bug fix: was only handling surfaces):
    #    1. Polygon/GraphicsComplex  → 3D surfaces (Plot3D, ParametricPlot3D surface)
    #    2. Line                     → 3D curves   (ParametricPlot3D curve, e.g. x(t),y(t),z(t))
    #    3. Arrow[Tube[{p1,p2},r]]  → 3D vector field arrows (VectorPlot3D)
    # Before this fix only Polygon was handled; Line/Arrow returned None →
    # "[3D — pip install matplotlib numpy]" was shown for ParametricPlot3D and VectorPlot3D.
    if not HAS_MPL or not HAS_NP: return None
    if not isinstance(g3d_expr, list) or g3d_expr[0] != 'Graphics3D': return None

    # ── Accumulators for the three primitive types ──────────────────────────
    face_color    = [0.880722, 0.611041, 0.142051]  # Mathematica default orange-gold
    all_verts     = []   # 3D vertex list for Polygon (surface) rendering
    all_tris      = []   # triangle index list for surface rendering
    vertex_colors = []   # per-vertex colors for ColorFunction surfaces
    lines_3d      = []   # list of (pts_array, color) for Line rendering
    arrows_3d     = []   # list of (tail, head, color) for Arrow rendering
    cur_color     = [0.24, 0.60, 0.80]  # default blue (matches Mathematica's default)

    # ── Helper: find first RGBColor recursively ─────────────────────────────
    def find_rgb(e):
        if not isinstance(e, list): return None
        if e[0]=='RGBColor' and len(e)>=4: return [float(e[1]),float(e[2]),float(e[3])]
        for s in e[1:]:
            c = find_rgb(s)
            if c: return c
        return None

    # ── Helper: find first LABColor recursively (VectorPlot3D uses LABColor) ─
    def find_lab(e):
        # LABColor[L,a,b] → convert to approximate RGB for matplotlib
        if not isinstance(e, list): return None
        if e[0]=='LABColor' and len(e)>=4:
            # Rough CIE Lab→RGB conversion via XYZ
            L, a, b = float(e[1])*100, float(e[2])*100, float(e[3])*100
            fy = (L+16)/116; fx = a/500+fy; fz = fy-b/200
            x = 0.95047*(fx**3 if fx>0.2069 else (fx-16/116)/7.787)
            y = 1.00000*(fy**3 if fy>0.2069 else (fy-16/116)/7.787)
            z = 1.08883*(fz**3 if fz>0.2069 else (fz-16/116)/7.787)
            r = min(1,max(0, 3.2406*x - 1.5372*y - 0.4986*z))
            g = min(1,max(0,-0.9689*x + 1.8758*y + 0.0415*z))
            bv= min(1,max(0, 0.0557*x - 0.2040*y + 1.0570*z))
            # Gamma correction
            def gc(c): return 1.055*c**(1/2.4)-0.055 if c>0.0031308 else 12.92*c
            return [gc(r), gc(g), gc(bv)]
        for s in e[1:]:
            c = find_lab(s)
            if c: return c
        return None

    def find_any_color(e):
        return find_rgb(e) or find_lab(e)

    # ── Helper: extract 3D point from List[x,y,z] ──────────────────────────
    def get_pt3(e):
        if isinstance(e, list) and e[0]=='List' and len(e)==4:
            return [float(e[1]), float(e[2]), float(e[3])]
        return None

    # ── Recursive collect: traverses the primitives tree ────────────────────
    def collect(e):
        nonlocal face_color, cur_color
        if not isinstance(e,list) or not e: return
        h = e[0]

        # Surface primitive via GraphicsComplex (Plot3D, ContourPlot3D, etc.)
        if h=='GraphicsComplex':
            base = len(all_verts)
            pts = e[1][1:]
            for v in pts:
                if isinstance(v,list) and v[0]=='List':
                    all_verts.append([float(v[1]),float(v[2]),float(v[3])])
            # VertexColors from ColorFunction
            for elem in e[3:]:
                if (isinstance(elem,list) and elem[0]=='Rule' and
                        elem[1]=='VertexColors' and isinstance(elem[2],list)
                        and elem[2][0]=='List'):
                    for vc in elem[2][1:]:
                        if isinstance(vc,list) and len(vc)>=4:
                            vertex_colors.append([float(vc[1]),float(vc[2]),float(vc[3])])
                        else:
                            vertex_colors.append(None)
            collect_idx(e[2], base)

        # Line: 3D parametric curve (ParametricPlot3D) — Bug fix: was missing!
        elif h=='Line':
            pts_raw = e[1]  # List[List[x,y,z], ...]
            pts = []
            for p in pts_raw[1:]:
                pt = get_pt3(p)
                if pt: pts.append(pt)
            if pts:
                lines_3d.append((np.array(pts), list(cur_color)))

        # Arrow[Tube[{pt1,pt2}, radius]] — VectorPlot3D arrows — Bug fix: was missing!
        elif h=='Arrow':
            inner = e[1] if len(e)>1 else None
            if isinstance(inner,list) and inner[0]=='Tube':
                seg = inner[1]  # List[List[x1,y1,z1], List[x2,y2,z2]]
                if isinstance(seg,list) and seg[0]=='List' and len(seg)>=3:
                    p1 = get_pt3(seg[1])
                    p2 = get_pt3(seg[2])
                    if p1 and p2:
                        arrows_3d.append((p1, p2, list(cur_color)))

        # Directive: update current color before processing children
        elif h=='Directive':
            c = find_any_color(e)
            if c: cur_color = c; face_color = c
            for s in e[1:]: collect(s)

        # LABColor / RGBColor: update current color (VectorPlot3D sets color per-arrow)
        elif h in ('LABColor','RGBColor','Hue'):
            c = find_any_color(e) or find_rgb(e)
            if c: cur_color = c

        else:
            for s in e[1:]:
                if isinstance(s,list): collect(s)

    def collect_idx(e, base):
        if not isinstance(e,list) or not e: return
        if e[0]=='Polygon':
            for face in e[1][1:]:
                if isinstance(face,list) and face[0]=='List':
                    idxs=[int(face[k])-1+base for k in range(1,len(face))]
                    for k in range(1,len(idxs)-1): all_tris.append([idxs[0],idxs[k],idxs[k+1]])
        else:
            for s in e[1:]:
                if isinstance(s,list): collect_idx(s,base)

    collect(g3d_expr[1] if len(g3d_expr)>1 else ['List'])

    # ── Nothing to render ───────────────────────────────────────────────────
    has_surface = bool(all_verts and all_tris)
    has_lines   = bool(lines_3d)
    has_arrows  = bool(arrows_3d)
    if not has_surface and not has_lines and not has_arrows: return None

    # ── Set up figure ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(7, 5.2), dpi=130, facecolor='white')
    ax  = fig.add_subplot(111, projection='3d')
    ax.set_facecolor((0.97, 0.97, 0.98))

    all_xs, all_ys, all_zs = [], [], []  # for auto-setting axis limits

    # ── Render 3D surface (Polygon/GraphicsComplex) ──────────────────────────
    if has_surface:
        verts = np.array(all_verts, dtype=float)
        tris  = np.array(all_tris,  dtype=int)
        n = len(verts)
        tris = tris[np.all((tris>=0) & (tris<n), axis=1)]
        if len(tris) > 0:
            polys = verts[tris]
            v0,v1,v2 = polys[:,0], polys[:,1], polys[:,2]
            normals = np.cross(v1-v0, v2-v0)
            nl = np.linalg.norm(normals, axis=1, keepdims=True)
            normals = normals / np.where(nl==0, 1, nl)
            light = np.array([0.5, -0.8, 1.2]); light /= np.linalg.norm(light)
            intensity = np.clip(0.3 + 0.7 * np.clip(normals @ light, 0, 1), 0, 1)
            has_vc = (len(vertex_colors)==len(all_verts) and
                      all(c is not None for c in vertex_colors))
            if has_vc:
                vc_arr = np.array(vertex_colors, dtype=float)
                face_rgb = vc_arr[tris].mean(axis=1)
                fcolors = np.column_stack([np.clip(face_rgb*intensity[:,None],0,1), np.ones(len(tris))])
            else:
                r,g,b = face_color
                fcolors = np.column_stack([r*intensity,g*intensity,b*intensity,np.ones(len(tris))])
            coll = Poly3DCollection(polys, facecolors=fcolors, edgecolors='none', linewidth=0, zsort='average')
            ax.add_collection3d(coll)
            all_xs.extend([verts[:,0].min(), verts[:,0].max()])
            all_ys.extend([verts[:,1].min(), verts[:,1].max()])
            all_zs.extend([verts[:,2].min(), verts[:,2].max()])

    # ── Render 3D parametric curves (Line) ──────────────────────────────────
    if has_lines:
        for pts, col in lines_3d:
            ax.plot(pts[:,0], pts[:,1], pts[:,2],
                    color=col, linewidth=1.5, alpha=0.9)
            all_xs.extend([pts[:,0].min(), pts[:,0].max()])
            all_ys.extend([pts[:,1].min(), pts[:,1].max()])
            all_zs.extend([pts[:,2].min(), pts[:,2].max()])

    # ── Render 3D vector field arrows (VectorPlot3D) ─────────────────────────
    if has_arrows:
        # Use ax.quiver: tail=(x,y,z), direction=(dx,dy,dz), color per-arrow
        tails = np.array([a[0] for a in arrows_3d], dtype=float)
        heads = np.array([a[1] for a in arrows_3d], dtype=float)
        dirs  = heads - tails
        colors= [a[2] for a in arrows_3d]
        # Subsample if too many arrows (performance + clarity)
        max_arrows = 800
        if len(tails) > max_arrows:
            idx_s = np.linspace(0, len(tails)-1, max_arrows, dtype=int)
            tails = tails[idx_s]; dirs = dirs[idx_s]; colors = [colors[i] for i in idx_s]
        # Length normalization so arrows have uniform visual size
        lengths = np.linalg.norm(dirs, axis=1, keepdims=True)
        scale = np.percentile(lengths[lengths>0], 75) if (lengths>0).any() else 1.0
        dirs_norm = dirs / np.where(lengths==0, 1, lengths) * (scale * 0.7)
        ax.quiver(tails[:,0], tails[:,1], tails[:,2],
                  dirs_norm[:,0], dirs_norm[:,1], dirs_norm[:,2],
                  colors=colors, arrow_length_ratio=0.35,
                  linewidth=0.8, alpha=0.85)
        all_xs.extend([tails[:,0].min(), tails[:,0].max()])
        all_ys.extend([tails[:,1].min(), tails[:,1].max()])
        all_zs.extend([tails[:,2].min(), tails[:,2].max()])

    # ── Axis limits ──────────────────────────────────────────────────────────
    if all_xs:
        ax.set_xlim(min(all_xs), max(all_xs))
        ax.set_ylim(min(all_ys), max(all_ys))
        ax.set_zlim(min(all_zs), max(all_zs))

    # ── Mathematica-style appearance ─────────────────────────────────────────
    ax.view_init(elev=25, azim=-60)
    ax.tick_params(labelsize=8)
    ax.xaxis.pane.fill = True;  ax.xaxis.pane.set_facecolor((0.93,0.93,0.95,0.5))
    ax.yaxis.pane.fill = True;  ax.yaxis.pane.set_facecolor((0.93,0.93,0.95,0.5))
    ax.zaxis.pane.fill = True;  ax.zaxis.pane.set_facecolor((0.90,0.90,0.93,0.5))
    ax.grid(True, linewidth=0.4, color='gray', alpha=0.4)
    plt.tight_layout(pad=0.5)

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='white')
    plt.close(fig)

    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


# ══════════════════════════════════════════════════════════════════════════════
# 2D GRAPHICS → SVG
# ══════════════════════════════════════════════════════════════════════════════

def _wl_num(v):
    """Μετατρέπει WL numeric expression tree σε Python float. (Bug #11 Rational coords)
    Χρειάστηκε γιατί τα cobweb Epilog lines είχαν Rational[251,954] coordinates
    που δεν μπορούσε να αξιολογήσει το float() απευθείας.

    Παραδείγματα WL numeric expressions:
      Rational[1,3]       → 0.333...
      Times[2, Pi]        → 6.283...  (αλλά το Pi δεν αναλύεται εδώ, απλά αποτυγχάνει)
      Plus[1, Rational[1,2]] → 1.5
      Power[2, -1]        → 0.5

    Υποστηρίζει: Rational[a,b], Real[x], Integer[x], Times[...], Plus[...], Power[b,e]."""
    if isinstance(v, (int, float)): return float(v)
    if isinstance(v, list) and v:
        h = v[0]
        if h == 'Rational' and len(v) >= 3: return float(v[1]) / float(v[2])
        if h == 'Real'    and len(v) >= 2: return float(v[1])
        if h == 'Integer' and len(v) >= 2: return float(v[1])
        if h == 'Times'   and len(v) >= 2:
            r = 1.0
            for x in v[1:]: r *= _wl_num(x)
            return r
        if h == 'Plus'    and len(v) >= 2:
            return sum(_wl_num(x) for x in v[1:])
        if h == 'Power'   and len(v) == 3:
            return _wl_num(v[1]) ** _wl_num(v[2])
    raise ValueError(f'Cannot evaluate: {v!r}')

def unwrap_pt(pt):
    """Εξάγει (x, y) float tuple από WL point representation.
    Αποδέχεται: List[x,y], List[Rational[a,b], ...], ή [x, y] list.
    Χρησιμοποιεί _wl_num() για να χειριστεί non-literal coords (Bug #06)."""
    if isinstance(pt,list):
        if len(pt)>=3 and pt[0]=='List':
            return _wl_num(pt[1]), _wl_num(pt[2])
        if len(pt)==2:
            return _wl_num(pt[0]), _wl_num(pt[1])
    raise ValueError(f'Bad point: {pt!r}')

def rgb_hex(r,g,b,a=1.0):
    """WL color floats [0,1] → CSS hex (#rrggbb) ή rgba(r,g,b,a) αν a<1."""
    ri,gi,bi=int(r*255),int(g*255),int(b*255)
    return f'rgba({ri},{gi},{bi},{a:.2f})' if a<1 else f'#{ri:02x}{gi:02x}{bi:02x}'

class DS:
    """Drawing State — η τρέχουσα κατάσταση χρώματος/πάχους κατά το render.
    
    Λειτουργεί σαν "current graphics state" του SVG renderer. Κάθε Directive
    ή color primitive (RGBColor, Opacity, Thickness, PointSize κτλ.) ενημερώνει
    το DS μέσω apply(). Οι primitives (Line, Point, Polygon) διαβάζουν από αυτό.
    
    Το copy() δημιουργεί snapshot για nested Directives (π.χ. Legended graphics).
    
    Bug #08: Προστέθηκε pt_size για PointSize/AbsolutePointSize rendering
              (πριν ήταν hardcoded r=3, τώρα r=pt_size).
    Bug #05: Το stroke field χρησιμοποιείται για EdgeForm (border χρώμα).
    """
    def __init__(self): self.color='#3d99cc'; self.fill='#3d99cc'; self.opacity=1.0; self.thick=1.5; self.stroke=None; self.pt_size=2.5
    def copy(self):
        s=DS(); s.color=self.color; s.fill=self.fill; s.opacity=self.opacity; s.thick=self.thick; s.stroke=self.stroke; s.pt_size=self.pt_size; return s
    def apply(self,e):
        # Ενημερώνει το DS από ένα WL color/thickness/pointsize directive.
        # Κάθε primitive (Line, Point, Polygon) διαβάζει ΑΜΕΣΩΣ μετά το apply().
        # Η κληρονόμηση χρώματος λειτουργεί ως: Directive > explicit color > DS default.
        # Bug #05 (multi-primitive): χωρίς σωστό state inheritance, όλα τα primitives
        # μετά από ένα Directive έπαιρναν το ίδιο χρώμα ακόμα και αν δεν έπρεπε.
        h=e[0]
        if h=='RGBColor': c=rgb_hex(e[1],e[2],e[3],e[4] if len(e)>4 else 1.0); self.color=c; self.fill=c
        elif h=='GrayLevel': v=e[1]; a=e[2] if len(e)>2 else 1.0; c=rgb_hex(v,v,v,a); self.color=c; self.fill=c
        elif h=='CMYKColor': r=(1-e[1])*(1-e[4]); g=(1-e[2])*(1-e[4]); b=(1-e[3])*(1-e[4]); c=rgb_hex(r,g,b); self.color=c; self.fill=c
        elif h=='Hue':
            import colorsys as _cs
            r2,g2,b2=_cs.hsv_to_rgb(float(e[1])%1, float(e[2]) if len(e)>2 else 1.0, float(e[3]) if len(e)>3 else 1.0)
            c=rgb_hex(r2,g2,b2); self.color=c; self.fill=c
        elif h=='LABColor':
            # LAB (Mathematica normalized 0-1) → RGB
            Lv,av,bv=float(e[1])*100,float(e[2])*100,float(e[3])*100
            fy=(Lv+16)/116; fx=av/500+fy; fz=fy-bv/200
            def _fi(t): return t**3 if t>0.206897 else 3*(0.206897**2)*(t-4/29)
            Xv,Yv,Zv=0.95047*_fi(fx),_fi(fy),1.08883*_fi(fz)
            rl=3.2406*Xv-1.5372*Yv-0.4986*Zv; gl=-0.9689*Xv+1.8758*Yv+0.0415*Zv; bl=0.0557*Xv-0.2040*Yv+1.0570*Zv
            def _gm(c2): return max(0,min(1,(1.055*(max(0,c2)**0.41667)-0.055) if c2>0.0031308 else 12.92*c2))
            c=rgb_hex(_gm(rl),_gm(gl),_gm(bl)); self.color=c; self.fill=c
        elif h=='Opacity' and len(e)>1: self.opacity=float(e[1])
        elif h in ('AbsoluteThickness','Thickness') and isinstance(e[1],(int,float)): self.thick=float(e[1])
        elif h == 'PointSize' and isinstance(e[1],(int,float)): self.pt_size=max(0.5, float(e[1])*460*0.5)
        elif h == 'AbsolutePointSize' and isinstance(e[1],(int,float)): self.pt_size=max(0.5, float(e[1])*0.5)
        elif h=='EdgeForm':
            # EdgeForm[color_directive] → sets stroke color for filled shapes
            ef_st = DS()
            for arg in e[1:]:
                if isinstance(arg,list): ef_st.apply(arg)
            self.stroke = ef_st.color
        elif h=='Directive':
            for s in e[1:]:
                if isinstance(s,list): self.apply(s)

def tp(x,y,xmn,xmx,ymn,ymx,W,H,pad):
    """Μετατρέπει WL (x,y) plot coordinates σε SVG pixel coords.
    Το WL plot space (xmn..xmx, ymn..ymx) → SVG canvas (pad..W-pad, pad..H-pad).
    Η y-axis αντιστρέφεται: WL y↑ = SVG y↓.

    Bug #19 (pw/ph undefined): πρώην χρησιμοποιούσε globals pw,ph που δεν ορίζονταν
    όταν η tp() κλήθηκε πριν τεθούν τα pw,ph στο graphics_to_svg (π.χ. από
    collect_xy). Τώρα υπολογίζονται τοπικά από W,H,pad σε κάθε κλήση."""
    pw = W - 2*pad   # plot width in pixels
    ph = H - 2*pad   # plot height in pixels
    return pad+(x-xmn)/(xmx-xmn)*pw, pad+(1-(y-ymn)/(ymx-ymn))*ph

def collect_xy(e):
    """Συλλέγει όλα τα (x,y) σημεία από ένα WL primitive ή expression tree.
    Χρησιμοποιείται για auto-range detection (PlotRange auto-detect).
    ΣΗΜΑΝΤΙΚΟ: πρέπει να αρχικοποιεί xs,ys=[] τοπικά — η έλλειψή του
    προκαλούσε NameError όταν το input ήταν κενή λίστα [] (bug fix).
    Αποδέχεται: Line, Point, Disk, BezierCurve, Arrow, Text, Rectangle."""
    xs, ys = [], []   # ← Κρίσιμο: τοπική αρχικοποίηση (πρώην crash site)
    if not isinstance(e,list) or not e: return xs, ys
    h=e[0]
    if h=='Line':
        if isinstance(e[1],list) and e[1][0]=='List':
            for pt in e[1][1:]:
                try: x,y=unwrap_pt(pt); xs.append(x); ys.append(y)
                except: pass
    elif h=='Rectangle':
        for c in e[1:3]:
            try: x,y=unwrap_pt(c); xs.append(x); ys.append(y)
            except: pass
    elif h=='Point':
        pts=e[1]; pl=pts[1:] if (isinstance(pts,list) and pts[0]=='List') else [pts]
        for pt in pl:
            try: x,y=unwrap_pt(pt); xs.append(x); ys.append(y)
            except: pass
    elif h=='Disk':
        # Disk[{cx,cy}, {rx,ry}] or Disk[{cx,cy}, r]
        try: x,y=unwrap_pt(e[1]); xs.append(x); ys.append(y)
        except: pass
    elif h=='BezierCurve':
        pts_list = e[1] if len(e)>1 and isinstance(e[1],list) and e[1][0]=='List' else None
        if pts_list:
            for pt in pts_list[1:]:
                try: x,y=unwrap_pt(pt); xs.append(x); ys.append(y)
                except: pass
    elif h=='Arrow':
        # Arrow[BezierCurve[...]] or Arrow[{pts}] — ο κόμβος της streamplot
        inner = e[1] if len(e)>1 else None
        if isinstance(inner,list):
            a,b=collect_xy(inner); xs.extend(a); ys.extend(b)
    elif h=='Text':
        if len(e)>2:
            try: x,y=unwrap_pt(e[2]); xs.append(x); ys.append(y)
            except: pass
    else:
        for s in e[1:]:
            if isinstance(s, list):   # ← guard: αποφυγή crash σε non-list items
                a,b=collect_xy(s); xs.extend(a); ys.extend(b)
    return xs, ys

_WRAPPERS={'Tooltip','StatusArea','Style','Mouseover','EventHandler',
           'Legended','Labeled','Inset','GraphicsGroup','Annotation'}

def render_2d(prim,xmn,xmx,ymn,ymx,W,H,pad):
    """Μετατρέπει WL 2D primitive (Line/Point/Polygon/Arrow/Disk/Text/Arrowheads...)
    σε λίστα SVG element strings.
    
    Παράμετροι:
      prim          : WL expression (list) — το primitive ή Directive
      xmn,xmx,ymn,ymx : plot range (WL coordinates)
      W,H           : SVG canvas διαστάσεις (pixels)
      pad           : padding (pixels) γύρω από το plot area
    
    Επιστρέφει λίστα SVG strings (π.χ. ['<polyline .../>', '<circle .../>'])
    τα οποία ενσωματώνονται στο τελικό SVG.
    
    Γνωστά quirks:
    - Arrow: χρησιμοποιεί SVG <marker> για arrowhead. Μόνο ένας marker ορισμός
      ανά SVG αλλά παράγεται redundant αν υπάρχουν πολλά Arrows (OK για browsers).
    - Point: μέγεθος ελέγχεται από DS.pt_size (Bug #08)."""
    out = []   # Λίστα SVG στοιχείων — τροφοδοτείται από τη r() μέσω closure
    def r(e,st):
        if not isinstance(e,list) or not e: return
        h=e[0]
        if h=='List':
            _COLOR_HEADS = ('Directive','RGBColor','GrayLevel','CMYKColor','Hue',
                            'LABColor','Opacity','AbsoluteThickness','Thickness',
                            'PointSize','EdgeForm','AbsolutePointSize')
            # Bug #05 (multi-primitive color inheritance):
            # Η WL primitives list δομή είναι: [Dir1, Prim1, Dir2, Prim2, ...]
            # Πρόβλημα: αν έχουμε [Dir1, Prim1, Prim2], το Prim2 πρέπει να
            # κληρονομεί Dir1 (όχι να παίρνει fresh DS). Αν έχουμε [Dir1, Prim1, Dir2, Prim2],
            # το Prim2 πρέπει να παίρνει Dir2 (reset μετά το render).
            # Λύση: reset loc ΜΟΝΟ αν έχει ήδη γίνει render (has_rendered flag).
            # Walk sequentially: accumulate directives into loc, render each primitive.
            # Only reset loc when a new Directive/Color head is encountered AFTER a
            # primitive has been rendered. This correctly handles both:
            #   [D1, P1, D2, P2]  → P1 gets c1, P2 gets c2
            #   [D1, P1, P2]      → both P1 and P2 get c1
            loc=st.copy(); i=1; has_rendered=False
            while i<len(e):
                it=e[i]
                if isinstance(it,list) and it[0] in _COLOR_HEADS:
                    if has_rendered:
                        loc=st.copy(); has_rendered=False
                    loc.apply(it); i+=1
                elif isinstance(it,list) and it[0]=='List':
                    r(it,loc); i+=1; has_rendered=True
                else:
                    r(it,loc); i+=1; has_rendered=True
        elif h=='Style':
            # Style[expr, directives...] — apply extra args as directives
            loc = st.copy()
            for d in e[2:]:
                if isinstance(d,list): loc.apply(d)
            if len(e)>1 and isinstance(e[1],list): r(e[1],loc)
        elif h in _WRAPPERS or (isinstance(h,str) and 'Charting' in h):
            if len(e)>1 and isinstance(e[1],list): r(e[1],st)
        elif h in ('Directive','LABColor','RGBColor','GrayLevel','Hue','CMYKColor'): st.apply(e)
        elif h=='Line':
            if isinstance(e[1],list) and e[1][0]=='List':
                coords=[]
                for pt in e[1][1:]:
                    try: x,y=unwrap_pt(pt); sx,sy=tp(x,y,xmn,xmx,ymn,ymx,W,H,pad); coords.append(f'{sx:.2f},{sy:.2f}')
                    except: pass
                if coords:
                    out.append(f'<path d="M {" L ".join(coords)}" stroke="{st.color}" stroke-opacity="{st.opacity:.2f}" stroke-width="{st.thick:.1f}" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
        elif h=='Rectangle':
            if len(e)>=3:
                try:
                    x0,y0=unwrap_pt(e[1]); x1,y1=unwrap_pt(e[2])
                    sx0,sy1=tp(x0,y0,xmn,xmx,ymn,ymx,W,H,pad); sx1,sy0=tp(x1,y1,xmn,xmx,ymn,ymx,W,H,pad)
                    rw,rh=abs(sx1-sx0),abs(sy1-sy0)
                    out.append(f'<rect x="{min(sx0,sx1):.2f}" y="{min(sy0,sy1):.2f}" width="{rw:.2f}" height="{rh:.2f}" fill="{st.fill}" fill-opacity="{st.opacity:.2f}" stroke="{st.color}" stroke-width="0.5"/>')
                except: pass
        elif h=='Polygon':
            pts=e[1]; pl=pts[1:] if (isinstance(pts,list) and pts[0]=='List') else [pts]
            coords=[]
            for pt in pl:
                try: x,y=unwrap_pt(pt); sx,sy=tp(x,y,xmn,xmx,ymn,ymx,W,H,pad); coords.append(f'{sx:.2f},{sy:.2f}')
                except: pass
            if coords:
                out.append(f'<polygon points="{" ".join(coords)}" fill="{st.fill}" fill-opacity="{st.opacity:.2f}" stroke="{st.color}" stroke-width="0.5"/>')
        elif h=='Point':
            pts=e[1]; pl=pts[1:] if (isinstance(pts,list) and pts[0]=='List') else [pts]
            for pt in pl:
                try:
                    x,y=unwrap_pt(pt); sx,sy=tp(x,y,xmn,xmx,ymn,ymx,W,H,pad)
                    out.append(f'<circle cx="{sx:.2f}" cy="{sy:.2f}" r="{st.pt_size:.1f}" fill="{st.color}" fill-opacity="{st.opacity:.2f}"/>')
                except: pass
        elif h=='Arrow':
            import math as _m
            pts_arg = e[1] if len(e)>1 else None
            def _arrow_path_and_head(svgd, end_x, end_y, prev_x, prev_y, color, opacity, thick):
                ang=_m.atan2(end_y-prev_y,end_x-prev_x); hs=max(5,thick*3)
                ax1=end_x-hs*_m.cos(ang-0.4); ay1=end_y-hs*_m.sin(ang-0.4)
                ax2=end_x-hs*_m.cos(ang+0.4); ay2=end_y-hs*_m.sin(ang+0.4)
                out.append(f'<path d="{svgd}" stroke="{color}" stroke-opacity="{opacity:.2f}" stroke-width="{thick:.1f}" fill="none" stroke-linecap="round"/>')
                out.append(f'<polygon points="{end_x:.2f},{end_y:.2f} {ax1:.2f},{ay1:.2f} {ax2:.2f},{ay2:.2f}" fill="{color}" fill-opacity="{opacity:.2f}"/>')
            if isinstance(pts_arg,list):
                if pts_arg[0]=='BezierCurve':
                    pts_e = pts_arg[1] if len(pts_arg)>1 and isinstance(pts_arg[1],list) and pts_arg[1][0]=='List' else None
                    if pts_e:
                        pts=[]
                        for p in pts_e[1:]:
                            try: xp,yp=unwrap_pt(p); pts.append(tp(xp,yp,xmn,xmx,ymn,ymx,W,H,pad))
                            except: pass
                        if len(pts)>=2:
                            sx,sy=pts[0]; d=f'M {sx:.2f},{sy:.2f}'
                            i2=1
                            while i2<len(pts):
                                if i2+2<len(pts):
                                    c1x,c1y=pts[i2]; c2x,c2y=pts[i2+1]; ex,ey=pts[i2+2]
                                    d+=f' C {c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f} {ex:.2f},{ey:.2f}'; i2+=3
                                elif i2+1<len(pts):
                                    c1x,c1y=pts[i2]; ex,ey=pts[i2+1]
                                    d+=f' Q {c1x:.2f},{c1y:.2f} {ex:.2f},{ey:.2f}'; i2+=2
                                else:
                                    ex,ey=pts[i2]; d+=f' L {ex:.2f},{ey:.2f}'; i2+=1
                            # Use second-to-last and last as direction for arrowhead
                            prev = pts[-2] if len(pts)>=2 else pts[0]
                            _arrow_path_and_head(d, pts[-1][0], pts[-1][1], prev[0], prev[1], st.color, st.opacity, st.thick)
                elif pts_arg[0]=='List':
                    coords=[]
                    for pt in pts_arg[1:]:
                        try: xp,yp=unwrap_pt(pt); sx,sy=tp(xp,yp,xmn,xmx,ymn,ymx,W,H,pad); coords.append((sx,sy))
                        except: pass
                    if len(coords)>=2:
                        dpath=' '.join([f'M {coords[0][0]:.2f},{coords[0][1]:.2f}']+[f'L {p[0]:.2f},{p[1]:.2f}' for p in coords[1:]])
                        _arrow_path_and_head(dpath, coords[-1][0], coords[-1][1], coords[-2][0], coords[-2][1], st.color, st.opacity, st.thick)
        elif h=='Arrowheads': pass
        elif h=='BezierCurve':
            # BezierCurve[{ctrl_pts...}] — render as cubic SVG path
            pts_e = e[1] if len(e)>1 and isinstance(e[1],list) and e[1][0]=='List' else None
            if pts_e and len(pts_e)>2:
                pts=[]; 
                for p in pts_e[1:]:
                    try: x,y=unwrap_pt(p); pts.append(tp(x,y,xmn,xmx,ymn,ymx,W,H,pad)); 
                    except: pass
                if len(pts)>=2:
                    sx,sy=pts[0]
                    d=f'M {sx:.2f},{sy:.2f}'
                    # Convert control points to cubic bezier segments
                    # Cubic bezier: every 3 points = 1 segment (C command)
                    i=1
                    while i<len(pts):
                        if i+2<len(pts):
                            c1x,c1y=pts[i]; c2x,c2y=pts[i+1]; ex,ey=pts[i+2]
                            d+=f' C {c1x:.2f},{c1y:.2f} {c2x:.2f},{c2y:.2f} {ex:.2f},{ey:.2f}'; i+=3
                        elif i+1<len(pts):
                            c1x,c1y=pts[i]; ex,ey=pts[i+1]
                            d+=f' Q {c1x:.2f},{c1y:.2f} {ex:.2f},{ey:.2f}'; i+=2
                        else:
                            ex,ey=pts[i]; d+=f' L {ex:.2f},{ey:.2f}'; i+=1
                    out.append(f'<path d="{d}" stroke="{st.color}" stroke-opacity="{st.opacity:.2f}" stroke-width="{st.thick:.1f}" fill="none"/>')
        elif h=='Disk':
            # Disk[{cx,cy}] or Disk[{cx,cy},{rx,ry}] or Disk[{cx,cy},r]
            try:
                cx,cy=unwrap_pt(e[1])
                sx,sy=tp(cx,cy,xmn,xmx,ymn,ymx,W,H,pad)
                # Radius in data coords
                if len(e)>2 and isinstance(e[2],list) and e[2][0]=='List':
                    rx_d=float(e[2][1]); ry_d=float(e[2][2])
                elif len(e)>2 and isinstance(e[2],(int,float)):
                    rx_d=ry_d=float(e[2])
                else:
                    rx_d=ry_d=(xmx-xmn)*0.05
                # Convert radius to pixel coords
                rx_px=abs(tp(cx+rx_d,cy,xmn,xmx,ymn,ymx,W,H,pad)[0]-sx)
                ry_px=abs(tp(cx,cy+ry_d,xmn,xmx,ymn,ymx,W,H,pad)[1]-sy)
                fill_c = st.fill if st.fill!='none' else st.color
                stroke_c = st.stroke if st.stroke else st.color
                out.append(f'<ellipse cx="{sx:.2f}" cy="{sy:.2f}" rx="{rx_px:.2f}" ry="{ry_px:.2f}" fill="{fill_c}" stroke="{stroke_c}" stroke-width="1"/>')
            except: pass
        elif h=='FilledCurve':
            # FilledCurve = bezier-drawn shape (often circular nodes in Graph)
            # Compute bounding box of all coordinate pairs
            try:
                import re as _re
                all_pts_str = str(e)
                coord_pairs = _re.findall(r'\[List,\s*([-\d.eE+]+),\s*([-\d.eE+]+)\]', all_pts_str.replace("'",""))
                if coord_pairs:
                    fxs = [float(x) for x,y in coord_pairs]
                    fys = [float(y) for x,y in coord_pairs]
                    cx = (min(fxs)+max(fxs))/2
                    cy = (min(fys)+max(fys))/2
                    rx_d = (max(fxs)-min(fxs))/2
                    ry_d = (max(fys)-min(fys))/2
                    if rx_d < 1e-9: rx_d = ry_d = (xmx-xmn)*0.05
                    sx,sy = tp(cx,cy,xmn,xmx,ymn,ymx,W,H,pad)
                    rx_px = abs(tp(cx+rx_d,cy,xmn,xmx,ymn,ymx,W,H,pad)[0]-sx)
                    ry_px = abs(tp(cx,cy+ry_d,xmn,xmx,ymn,ymx,W,H,pad)[1]-sy)
                    fill_c = st.fill if st.fill!='none' else st.color
                    stroke_c = st.stroke if st.stroke else st.color
                    out.append(f'<ellipse cx="{sx:.2f}" cy="{sy:.2f}" rx="{rx_px:.2f}" ry="{ry_px:.2f}" fill="{fill_c}" stroke="{stroke_c}" stroke-width="1"/>')
            except: pass
        elif h=='Text':
            # Text['label', {x,y}]
            try:
                lbl = e[1].strip("'\"") if isinstance(e[1],str) else str(e[1])
                tx,ty=unwrap_pt(e[2])
                sx,sy=tp(tx,ty,xmn,xmx,ymn,ymx,W,H,pad)
                out.append(f'<text x="{sx:.1f}" y="{sy+4:.1f}" text-anchor="middle" font-size="11" font-weight="bold" fill="{st.color}">{lbl}</text>')
            except: pass
        else:
            if isinstance(h,str) and h not in ('Rule','RuleDelayed','Association'):
                for s in e[1:]:
                    if isinstance(s,list): r(s,st)
    r(prim,DS()); return out

def nice_ticks(v0,v1,n=5):
    """Παράγει "nice" tick values για έναν άξονα [v0,v1].
    Χρησιμοποιεί στρογγύλεμα σε round numbers (1,2,5 × 10^k) για n~5 ticks.

    Bug #21 (span undefined): η μεταβλητή `span` δεν ορίζεται αν το v1<=v0.
    Τώρα ορίζεται ΠΡΩΤΑ και επιστρέφει [v0] αν span<=0."""
    span = v1 - v0   # ← bug fix: span δεν ορίζεται αλλιώς
    if span<=0: return [v0]
    rough=span/(n-1); mag=10**math.floor(math.log10(rough))
    for ns in [0.1,0.2,0.25,0.5,1,2,2.5,5,10]:
        if ns*mag>=rough: step=ns*mag; break
    else: step=mag
    start=math.ceil(v0/step)*step; ticks=[]; v=start
    while v<=v1+1e-10: ticks.append(round(v,10)); v+=step; v=round(v,10)
    return ticks

def fmt(v):
    """Μορφοποιεί tick value: 0 → '0', integers → '1', floats → '1.5' ή '1.23e-5'."""
    if abs(v)>=1000 or (abs(v)<0.01 and v!=0): return f'{v:.2e}'
    return str(int(v)) if v==int(v) else f'{v:.2g}'

def _expand_graphics_complex(prims):
    """Expands GraphicsComplex[points, primitives] by substituting
    integer index references with actual [x,y] coordinate pairs.

    Το WL GraphicsComplex αποθηκεύει τις συντεταγμένες σε ξεχωριστή λίστα
    και στα primitives χρησιμοποιεί ακέραιους δείκτες αντί για συντεταγμένες.
    Π.χ.: GraphicsComplex[{p1,p2,p3}, Polygon[{{1,2,3}}]]
          → Polygon[{p1,p2,p3}]  (coordinates inline)

    Χρησιμοποιείται για Graph[] outputs (nodes+edges με δείκτες αντί για coords).
    Η _expand_graphics_complex() καλείται ΠΡΙΝ το render_2d() για να μετατρέψει
    τους δείκτες σε πραγματικές συντεταγμένες."""
    if not isinstance(prims, list): return prims
    if prims[0] == 'GraphicsComplex':
        pts = prims[1]  # List[List[x1,y1], List[x2,y2], ...]
        point_list = pts[1:] if (isinstance(pts,list) and pts[0]=='List') else []
        rest = prims[2:]  # rendering primitives with index refs
        def resolve(e):
            if not isinstance(e, list): return e
            if e[0] == 'List' and all(isinstance(x,(int,float)) for x in e[1:]):
                # List of integer indices → list of coordinate pairs
                return ['List'] + [point_list[int(x)-1] if 1<=int(x)<=len(point_list)
                                   else e for x in e[1:]]
            return [e[0]] + [resolve(s) for s in e[1:]]
        expanded = [resolve(r) for r in rest]
        return ['List'] + expanded
    elif prims[0] == 'List':
        return ['List'] + [_expand_graphics_complex(s) for s in prims[1:]]
    else:
        return [prims[0]] + [_expand_graphics_complex(s) if isinstance(s,list) else s
                             for s in prims[1:]]


def bar_graphics_to_svg(bar_g, vmin, vmax, H=300, grad_id='cbgrad'):
    """Παράγει SVG colorbar (κατακόρυφη μπάρα έντασης) από pre-rendered bar Graphics.

    Χρησιμοποιείται για StreamPlot/VectorPlot/DensityPlot με PlotLegends->Automatic.
    Τα bar Graphics αντικείμενα αποθηκεύονται στο gmap με ειδικά κλειδιά
    (key_hash + 'bar') και περιέχουν Rectangle primitives με LABColor/RGBColor.

    Bug #14 / Bug #26: Η colorbar εμφανίζεται δίπλα στο StreamPlot ή VectorPlot3D.
    Η αντιστοίχιση bar_g ↔ plot γίνεται με proximity matching του y-span
    των Rectangles με το declared range {vmin, vmax} από το BarLegend[].
    Το WLJS αποθηκεύει 2 bar objects ανά notebook (ένα για κάθε Legended plot)·
    το proximity matching επιλέγει το σωστό (αυτό με το πιο κοντινό y-span).

    Τεχνική λεπτομέρεια: Η y-axis στα bar Graphics είναι σε arbitrary WL units
    (π.χ. -1.27 έως 26.6), ΟΧΙ στα πραγματικά vmin/vmax. Το matching γίνεται
    συγκρίνοντας το ΕΚΤΕΤΑΜΕΝΟ εύρος (max_y - min_y) με (vmax - vmin).

    Παράγει <svg> με linearGradient από τα Rectangle colors + αριθμητικές ετικέτες."""
    if not isinstance(bar_g, list) or bar_g[0] != 'Graphics': return None
    prims = bar_g[1]
    if not isinstance(prims, list) or prims[0] != 'List': return None

    def lab_to_hex(Ln, an, bn):
        L=Ln*100; a=an*100; b=bn*100
        fy=(L+16)/116; fx=a/500+fy; fz=fy-b/200
        def fi(t): return t**3 if t>6/29 else 3*(6/29)**2*(t-4/29)
        X=0.95047*fi(fx); Y=fi(fy); Z=1.08883*fi(fz)
        rl=3.2406*X-1.5372*Y-0.4986*Z; gl=-0.9689*X+1.8758*Y+0.0415*Z; bl=0.0557*X-0.2040*Y+1.0570*Z
        def gam(c): return 1.055*max(0,c)**0.41667-0.055 if c>0.0031308 else 12.92*c
        r2,g2,b2=max(0,min(1,gam(rl))),max(0,min(1,gam(gl))),max(0,min(1,gam(bl)))
        return f'#{int(r2*255):02x}{int(g2*255):02x}{int(b2*255):02x}'

    def rgb_to_hex(r,g,b):
        return f'#{int(max(0,min(1,r))*255):02x}{int(max(0,min(1,g))*255):02x}{int(max(0,min(1,b))*255):02x}'

    # Collect (y_min, y_max, hex_color) stops — handles LABColor and RGBColor
    raw_stops = []
    for elem in prims[1:]:
        if not isinstance(elem, list) or elem[0] != 'List': continue
        col_el = next((s for s in elem[1:] if isinstance(s,list)
                       and s[0] in ('LABColor','RGBColor','GrayLevel')), None)
        rect = next((s for s in elem[1:] if isinstance(s,list) and s[0]=='Rectangle'), None)
        if col_el and rect:
            try:
                if col_el[0] == 'LABColor':
                    hx = lab_to_hex(float(col_el[1]),float(col_el[2]),float(col_el[3]))
                elif col_el[0] == 'RGBColor':
                    hx = rgb_to_hex(float(col_el[1]),float(col_el[2]),float(col_el[3]))
                elif col_el[0] == 'GrayLevel':
                    v=float(col_el[1]); hx=rgb_to_hex(v,v,v)
                else: continue
                y0 = float(rect[1][2]) if isinstance(rect[1],list) and len(rect[1])>=3 else 0
                y1 = float(rect[2][2]) if isinstance(rect[2],list) and len(rect[2])>=3 else 0
                raw_stops.append((min(y0,y1), max(y0,y1), hx))
            except: pass
    if not raw_stops: return None
    raw_stops.sort()

    # Normalise y to [0,1]
    y_lo = raw_stops[0][0]; y_hi = raw_stops[-1][1]; span = y_hi - y_lo or 1
    # Build SVG gradient
    W_bar=22; pad_l=4; pad_r=52; pad_t=8; pad_b=8
    W_svg = pad_l + W_bar + pad_r
    H_svg = H + pad_t + pad_b

    # Build stops: map raw_stops (bottom→top in Mathematica y) to SVG offsets 0→1 (top→bottom)
    # t = 1 - (y - y_lo)/span  inverts the axis: high y → low SVG offset → top of bar
    stop_pairs = []
    for i, (ya, yb, hx) in enumerate(raw_stops):
        t_bottom = 1.0 - (ya - y_lo) / span   # ya (low y) = low value = bottom = offset near 1
        t_top    = 1.0 - (yb - y_lo) / span   # yb (high y) = high value = top = offset near 0
        if i == 0:
            stop_pairs.append((t_bottom, hx))  # anchor at very bottom
        stop_pairs.append((t_top, hx))
    # Sort ascending by offset (SVG spec requirement for correct rendering in all browsers)
    stop_pairs.sort(key=lambda x: x[0])
    grad_stops = [f'<stop offset="{t:.4f}" stop-color="{c}"/>' for t, c in stop_pairs]
    
    # Tick labels — choose nice round numbers
    import math as _m
    val_range = vmax - vmin
    if val_range == 0: val_range = 1
    mag = _m.floor(_m.log10(val_range))
    raw_step = val_range / 6
    step_mag = 10 ** _m.floor(_m.log10(raw_step)) if raw_step > 0 else 1
    # Target ~10 ticks maximum; try smaller steps first for smoother scale
    nice_step = raw_step
    for divisor in [10, 5, 4, 2, 1]:
        candidate = step_mag / divisor
        if candidate <= 0: continue
        n = val_range / candidate
        if 4 <= n <= 14:
            nice_step = candidate; break
    else:
        for mult in [1, 2, 2.5, 5, 10]:
            candidate = step_mag * mult
            if val_range / candidate <= 14:
                nice_step = candidate; break
    first_tick = _m.ceil(vmin / nice_step - 1e-9) * nice_step
    tick_vals = []
    v = first_tick
    while v <= vmax + nice_step * 0.01:
        if v >= vmin - nice_step * 0.01:
            tick_vals.append(round(v, 10))
        v += nice_step
    # Format: integer if large, else 2 decimal places
    def fmt(v):
        if abs(vmax) > 100: return f'{v:.0f}'
        elif nice_step >= 0.1: return f'{v:.2f}'.rstrip('0').rstrip('.') or '0'
        else: return f'{v:.3g}'
    ticks = []
    for val in tick_vals:
        frac = (val - vmin) / val_range
        y_px = pad_t + (1.0 - frac) * H
        if y_px < pad_t - 5 or y_px > pad_t + H + 5: continue
        label = fmt(val)
        ticks.append(f'<line x1="{pad_l+W_bar}" y1="{y_px:.1f}" x2="{pad_l+W_bar+4}" y2="{y_px:.1f}" stroke="#555" stroke-width="1"/>')
        ticks.append(f'<text x="{pad_l+W_bar+7}" y="{y_px+4:.1f}" font-size="10" fill="#333">{label}</text>')

    # grad_id passed as parameter
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W_svg}" height="{H_svg}" style="flex-shrink:0">
  <defs>
    <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
      {chr(10).join(grad_stops)}
    </linearGradient>
  </defs>
  <rect x="{pad_l}" y="{pad_t}" width="{W_bar}" height="{H}" fill="url(#{grad_id})" stroke="#888" stroke-width="0.5"/>
  {chr(10).join(ticks)}
</svg>'''
    return svg


def wl_to_label(e):
    """Convert a WL expression to an SVG-safe text string (may contain <tspan>)."""
    if e is None or e == 'None': return ''
    if isinstance(e, str):
        s = e.strip("'\"")
        return '' if s in ('None','') else s
    if isinstance(e, (int, float)): return str(e)
    if not isinstance(e, list) or not e: return ''
    h = e[0]
    if h in ('HoldForm','Defer','TraditionalForm','InputForm','StandardForm','DisplayForm'):
        return wl_to_label(e[1]) if len(e)>1 else ''
    if h == 'Subscript':
        base = wl_to_label(e[1]) if len(e)>1 else ''
        sub  = wl_to_label(e[2]) if len(e)>2 else ''
        return f'{base}<tspan dy="3" font-size="0.75em">{sub}</tspan><tspan dy="-3"></tspan>'
    if h == 'Superscript':
        base = wl_to_label(e[1]) if len(e)>1 else ''
        sup  = wl_to_label(e[2]) if len(e)>2 else ''
        return f'{base}<tspan dy="-4" font-size="0.75em">{sup}</tspan><tspan dy="4"></tspan>'
    if h in ('Style','Annotation','Tooltip','StatusArea','Framed'):
        return wl_to_label(e[1]) if len(e)>1 else ''
    if h == 'Row':
        items = e[1][1:] if (len(e)>1 and isinstance(e[1],list) and e[1][0]=='List') else e[1:]
        return ''.join(wl_to_label(i) for i in items)
    if h == 'List':
        return ''.join(wl_to_label(i) for i in e[1:])
    if isinstance(h, str): return h.strip("'\"")
    return ''

def graphics_to_svg(gexpr, W=460):
    """Μετατρέπει WL Graphics[] expression σε inline SVG string.
    
    Αλυσίδα επεξεργασίας:
    1. Αν υπάρχει GraphicsComplex + VertexColors → densityplot_to_b64() (raster PNG)
    2. Αλλιώς: SVG renderer από primitives (Line, Arrow, Point, Polygon, Text κτλ.)
    
    Διαχειρίζεται:
    - Εύρεση PlotRange (explicit ή auto από τα σημεία)
    - Axis labels, tick marks
    - GraphicsComplex expansion (δείκτες → συντεταγμένες)
    - VertexColors → per-triangle rasterization για DensityPlot
    - StreamPlot arrows (Arrowheads + Arrow)
    
    Επιστρέφει HTML string (SVG element) ή None αν αποτύχει."""
    # ── DensityPlot / ContourPlot (GraphicsComplex + VertexColors) ──────────
    # Αν το γράφημα έχει GraphicsComplex + VertexColors (χρωματισμός ανά κορυφή),
    # το αποδίδουμε ως rasterized PNG μέσω densityplot_to_b64() (triangle fill).
    # Αυτή η διαδρομή καλύπτει: DensityPlot, ContourPlot, VectorDensityPlot.
    # Το αποτέλεσμα ενσωματώνεται ως <image> μέσα σε SVG wrapper με axis ticks.
    dp = densityplot_to_b64(gexpr)
    if dp is not None:
        b64, xmin, xmax, ymin, ymax = dp
        # Build a nice framed SVG with the raster image + tick labels
        PAD_L, PAD_R, PAD_T, PAD_B = 50, 15, 15, 35
        IW, IH = 300, 300
        TW = PAD_L + IW + PAD_R
        TH = PAD_T + IH + PAD_B
        # Compute ~5 ticks for each axis
        xticks = nice_ticks(xmin, xmax)
        yticks = nice_ticks(ymin, ymax)
        svg_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{TW}" height="{TH}" '
            f'style="max-width:100%;height:auto;display:block;margin:auto">',
            # Image
            f'<image x="{PAD_L}" y="{PAD_T}" width="{IW}" height="{IH}" '
            f'href="{b64}" preserveAspectRatio="none"/>',
            # Frame border
            f'<rect x="{PAD_L}" y="{PAD_T}" width="{IW}" height="{IH}" '
            f'fill="none" stroke="#555" stroke-width="1"/>',
        ]
        # X axis ticks
        for v in xticks:
            px = PAD_L + (v - xmin) / (xmax - xmin) * IW
            lbl = f'{v:.1f}' if v != int(v) else str(int(v))
            svg_parts.append(f'<line x1="{px:.1f}" y1="{PAD_T+IH}" x2="{px:.1f}" y2="{PAD_T+IH+4}" stroke="#555" stroke-width="1"/>')
            svg_parts.append(f'<text x="{px:.1f}" y="{PAD_T+IH+16}" text-anchor="middle" font-size="10" fill="#333">{lbl}</text>')
        # Y axis ticks
        for v in yticks:
            py = PAD_T + IH - (v - ymin) / (ymax - ymin) * IH
            lbl = f'{v:.1f}' if v != int(v) else str(int(v))
            svg_parts.append(f'<line x1="{PAD_L-4}" y1="{py:.1f}" x2="{PAD_L}" y2="{py:.1f}" stroke="#555" stroke-width="1"/>')
            svg_parts.append(f'<text x="{PAD_L-6}" y="{py+4:.1f}" text-anchor="end" font-size="10" fill="#333">{lbl}</text>')
        svg_parts.append('</svg>')
        return '\n'.join(svg_parts)
    prims=gexpr[1] if len(gexpr)>1 else ['List']
    # Expand GraphicsComplex indexed references into actual coordinates
    prims = _expand_graphics_complex(prims)
    opts =gexpr[2][1:] if len(gexpr)>2 and isinstance(gexpr[2],list) else []
    def opt(k):
        k2 = k.strip("'\"")
        for o in opts:
            if isinstance(o,list) and o[0] in ('Rule','RuleDelayed'):
                ok = o[1] if isinstance(o[1],str) else ''
                if ok == k or ok.strip("'\"") == k2: return o[2]
    all_xs,all_ys=collect_xy(prims)
    def parse_axis(spec,coords):
        if isinstance(spec,list) and len(spec)==3 and spec[0]=='List':
            try: return float(spec[1]),float(spec[2])
            except: pass
        if coords:
            p5=(max(coords)-min(coords))*0.05 or 0.1
            return min(coords)-p5, max(coords)+p5
        return 0.0,1.0
    pr=opt('PlotRange')
    if isinstance(pr,list) and len(pr)==3: xmn,xmx=parse_axis(pr[1],all_xs); ymn,ymx=parse_axis(pr[2],all_ys)
    else: xmn,xmx=parse_axis(None,all_xs); ymn,ymx=parse_axis(None,all_ys)
    if xmx==xmn: xmx=xmn+1
    if ymx==ymn: ymx=ymn+1
    ar_raw=opt('AspectRatio')
    if isinstance(ar_raw,list) and ar_raw[0]=='Power':
        base=GOLDEN if ar_raw[1]=='GoldenRatio' else ar_raw[1]
        try: ar=float(base)**float(ar_raw[2])
        except: ar=1/GOLDEN
    elif isinstance(ar_raw,(int,float)): ar=float(ar_raw)
    else: ar=1/GOLDEN
    H=int(W*ar); pad=45; pw,ph=W-2*pad,H-2*pad
    parts=render_2d(prims,xmn,xmx,ymn,ymx,W,H,pad)
    # ── Detect "network graph" mode (Graph[...] output) ─────────────────────
    # Τα Graph[] outputs περιέχουν Disk (κόμβοι) + BezierCurve (ακμές).
    # Σε αυτή τη λειτουργία: δεν σχεδιάζουμε grid lines και axis ticks,
    # χρησιμοποιούμε rounded border στο container SVG.
    # Ο εντοπισμός γίνεται heuristically από την παρουσία και των δύο.
    _prims_str = str(prims)
    _is_graph = 'Disk' in _prims_str and 'BezierCurve' in _prims_str
    # ── Epilog: rendered ON TOP of main content ──────────────────────────────
    epilog_raw = opt('Epilog')
    epilog_parts = render_2d(epilog_raw,xmn,xmx,ymn,ymx,W,H,pad) if epilog_raw else []
    # ── Background color ─────────────────────────────────────────────────────
    bg_opt = opt('Background')
    def _chex(c):
        if not isinstance(c,list): return None
        if c[0]=='RGBColor' and len(c)>=4:
            return '#{:02x}{:02x}{:02x}'.format(int(max(0,min(1,float(c[1])))*255),
                int(max(0,min(1,float(c[2])))*255),int(max(0,min(1,float(c[3])))*255))
        if c[0]=='GrayLevel' and len(c)>=2:
            v=int(max(0,min(1,float(c[1])))*255); return f'#{v:02x}{v:02x}{v:02x}'
        return None
    bg_hex  = _chex(bg_opt) if bg_opt else None
    plot_fill  = bg_hex if bg_hex else '#fafafa'
    outer_fill = bg_hex if bg_hex else 'white'
    uid=abs(id(gexpr))%100000
    xt=nice_ticks(xmn,xmx); yt=nice_ticks(ymn,ymx)
    L=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="max-width:100%;height:auto;display:block;margin:auto">',
       f'<rect width="{W}" height="{H}" fill="{outer_fill}"{"  rx=\"6\"" if _is_graph else ""}/>',
       f'<clipPath id="cp{uid}"><rect x="{pad}" y="{pad}" width="{pw}" height="{ph}"/></clipPath>',
       f'<rect x="{pad}" y="{pad}" width="{pw}" height="{ph}" fill="{plot_fill}"{"" if _is_graph else " stroke=\"#ccc\" stroke-width=\"1\""}/>' ]
    if not _is_graph:
        L.append('<g stroke="#e8e8e8" stroke-width="0.5">')
        for v in xt:
            if xmn<=v<=xmx:
                sx,_=tp(v,ymn,xmn,xmx,ymn,ymx,W,H,pad); L.append(f'<line x1="{sx:.1f}" y1="{pad}" x2="{sx:.1f}" y2="{pad+ph}"/>')
        for v in yt:
            if ymn<=v<=ymx:
                _,sy=tp(xmn,v,xmn,xmx,ymn,ymx,W,H,pad); L.append(f'<line x1="{pad}" y1="{sy:.1f}" x2="{pad+pw}" y2="{sy:.1f}"/>')
        L.append('</g>')
    L.append(f'<g clip-path="url(#cp{uid})">'); L.extend(parts); L.append('</g>')
    if epilog_parts:
        L.append(f'<g clip-path="url(#cp{uid})">'); L.extend(epilog_parts); L.append('</g>')
    if not _is_graph:
        _,ay=tp(xmn,max(ymn,min(0,ymx)),xmn,xmx,ymn,ymx,W,H,pad); ay=max(pad,min(pad+ph,ay))
        ax,_=tp(max(xmn,min(0,xmx)),ymn,xmn,xmx,ymn,ymx,W,H,pad); ax=max(pad,min(pad+pw,ax))
        L.append(f'<line x1="{pad}" y1="{ay:.1f}" x2="{pad+pw:.1f}" y2="{ay:.1f}" stroke="#555" stroke-width="1"/>')
        L.append(f'<line x1="{ax:.1f}" y1="{pad}" x2="{ax:.1f}" y2="{pad+ph:.1f}" stroke="#555" stroke-width="1"/>')
        for v in xt:
            if xmn<=v<=xmx:
                sx,_=tp(v,ymn,xmn,xmx,ymn,ymx,W,H,pad)
                L.append(f'<line x1="{sx:.1f}" y1="{ay:.1f}" x2="{sx:.1f}" y2="{ay+5:.1f}" stroke="#555" stroke-width="1"/>')
                L.append(f'<text x="{sx:.1f}" y="{ay+16:.1f}" text-anchor="middle" font-size="10" fill="#555">{fmt(v)}</text>')
        for v in yt:
            if ymn<=v<=ymx:
                _,sy=tp(xmn,v,xmn,xmx,ymn,ymx,W,H,pad)
                L.append(f'<line x1="{ax-5:.1f}" y1="{sy:.1f}" x2="{ax:.1f}" y2="{sy:.1f}" stroke="#555" stroke-width="1"/>')
                L.append(f'<text x="{ax-8:.1f}" y="{sy+4:.1f}" text-anchor="end" font-size="10" fill="#555">{fmt(v)}</text>')
    # ── Axis labels + PlotLabel (only for non-graph plots) ─────────────────
    if not _is_graph:
        al = opt('AxesLabel')
        x_label_raw = al[1] if (isinstance(al,list) and len(al)>1 and al[0]=='List') else None
        y_label_raw = al[2] if (isinstance(al,list) and len(al)>2) else None
        x_label = wl_to_label(x_label_raw) if x_label_raw else ''
        y_label = wl_to_label(y_label_raw) if y_label_raw else ''
        plot_label = wl_to_label(opt('PlotLabel'))
        if x_label:
            lx = pad + pw // 2; ly = H - 6
            L.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="12" fill="#444">{x_label}</text>')
        if y_label:
            lx = 12; ly = pad + ph // 2
            L.append(f'<text transform="rotate(-90,{lx},{ly})" x="{lx}" y="{ly}" text-anchor="middle" font-size="12" fill="#444">{y_label}</text>')
        if plot_label:
            lx = pad + pw // 2; ly = pad - 8
            L.append(f'<text x="{lx}" y="{ly}" text-anchor="middle" font-size="13" font-weight="500" fill="#333">{plot_label}</text>')
    L.append('</svg>'); return '\n'.join(L)


# ══════════════════════════════════════════════════════════════════════════════
# MARKDOWN → HTML
# ══════════════════════════════════════════════════════════════════════════════

def render_md(text):
    """Μετατρέπει WLJS markdown κείμενο σε HTML.
    
    Εκτός από το standard markdown (python-markdown), χειρίζεται:
    - ::: admonitions (:::warning, :::note, :::info, :::danger)
      → Colored div με εικονίδιο (🔔 ⚠️ 💡 ❗)
      Αυτά ήταν Bug #04: πριν εμφανίζονταν ως plain text "::: warning"
    - Inline math ($...$ και $$...$$) → προστατεύεται από markdown escaping
    - Τα headings (h1-h4) συλλέγονται για το TOC"""
    # ── Pre-process ::: admonitions (callout blocks) ──────────────────────────
    _ADM_ICONS = {'warning':'⚠️','warn':'⚠️','note':'ℹ️','info':'ℹ️',
                  'tip':'💡','hint':'💡','danger':'🚨',
                  'caution':'🚨','error':'🚨','success':'✅','check':'✅'}
    def _adm(m):
        typ=m.group(1).strip().lower(); body=m.group(2).strip()
        icon=_ADM_ICONS.get(typ,'📌'); label=typ.capitalize()
        esc=body.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
        return (f'<div class="admonition adm-{typ}">'
                f'<div class="adm-title">{icon} {label}</div>'
                f'<div class="adm-body">{esc}</div></div>')
    text=re.sub(r'^:::(\w+)[ \t]*\n(.*?)\n:::',_adm,text,flags=re.DOTALL|re.MULTILINE)
    ph = {}    # placeholder dict: math spans → kept verbatim through markdown
    # Bug #22 (render_md ph/ctr undefined): πρώην ph και ctr ορίζονταν μέσα
    # στο sub() closure χωρίς να υπάρχουν ως outer variables → NameError.
    # Τώρα ορίζονται ρητά πριν την κλήση του re.sub().
    ctr = [0]  # mutable counter (list ώστε να τροποποιείται μέσα στο closure)
    def sub(m):
        # Unescape double-backslash inside math: \\cmd → \cmd
        content = m.group(0).replace('\\\\', '\\')
        k=f'MPHX{ctr[0]}X'; ph[k]=content; ctr[0]+=1; return k
    text=re.sub(r'\$\$(.+?)\$\$',sub,text,flags=re.DOTALL)
    text=re.sub(r'(?<!\$)\$(?!\$)(.+?)(?<!\$)\$(?!\$)',sub,text,flags=re.DOTALL)
    html=md_lib.markdown(text,extensions=['tables','fenced_code','nl2br'])
    for k,v in ph.items(): html=html.replace(k,v)
    # Wrap display math
    html=re.sub(r'\$\$(.+?)\$\$',r'<div class="math-display">\\[\1\\]</div>',html,flags=re.DOTALL)
    return html


# ══════════════════════════════════════════════════════════════════════════════
# CSS ΧΡΩΜΑΤΑ
# ══════════════════════════════════════════════════════════════════════════════

def parse_colors(css):
    """Εξάγει τα background colors cin/cout από το WLJS custom CSS.
    Το WLJS notebook αποθηκεύει custom theme colors στο <style> tag.
    Αναζητούμε: .cell-input .bg-* { background: ... } (cin)
                .cell-output .bg-* { background: ... } (cout)
    Αυτά χρησιμοποιούνται για το color scheme του εξαγόμενου HTML."""
    def bg(sel):
        m=re.search(re.escape(sel)+r'\s*\{[^}]*?background\s*:\s*([^;!\}]+)',css,re.DOTALL)
        return m.group(1).strip() if m else None
    return {
        'body':    (bg('body') or '#3c3a3d').replace('!important','').strip(),
        'cin':     bg('.cin')               or '#e1e5ea',
        'cout':    bg('.cout')              or '#c0d5eb',
        'cin_md':  bg('.cin .clang-markdown') or '#f29083',
        'cout_md': bg('.cout.markdown')     or '#fffdd0',
    }


# ══════════════════════════════════════════════════════════════════════════════
# ΠΙΝΑΚΑΣ ΠΕΡΙΕΧΟΜΕΝΩΝ
# ══════════════════════════════════════════════════════════════════════════════

def slugify(text):
    s=re.sub(r'[^\w\s-]','',text.lower())
    return re.sub(r'\s+','-',s).strip('-') or 'section'

def inject_ids(html, headings):
    for level,text,slug in headings:
        pat=re.compile(r'(<h'+str(level)+r'(?![^>]*\bid\s*=)[^>]*>)',re.IGNORECASE)
        def make_repl(s):
            def repl(m): return m.group(1)[:-1]+f' id="{s}">'
            return repl
        html=pat.sub(make_repl(slug),html,count=1)
    return html

def build_toc(headings):
    if not headings: return ''
    items=[]
    for level,text,slug in headings:
        ind=(level-1)*14
        items.append(f'<a href="#{slug}" class="toc-item toc-h{level}" style="padding-left:{8+ind}px">{text}</a>')
    return '<nav id="toc"><div id="toc-meta">{toc_meta_placeholder}</div><div id="toc-title">Περιεχόμενα</div>\n'+'\n'.join(items)+'\n</nav>'


# ══════════════════════════════════════════════════════════════════════════════
# ΚΥΡΙΟΣ ΜΕΤΑΤΡΟΠΕΑΣ
# ══════════════════════════════════════════════════════════════════════════════

def parse_linelegend(data_str):
    """Parse LineLegend από cell data string → λίστα (hex_color, label_str).
    
    Χρησιμοποιείται για Plot με PlotLegends->"Expressions" ή PlotLegends->functList.
    Το LineLegend[{colors}, {labels}] αποθηκεύεται στο cell data string (VB notation).
    
    Bug #11: Οι labels περιείχαν HoldForm[x] (π.χ. "5*HoldForm[x]+HoldForm[x]^2").
             Η to_text() εσωτερικά αφαιρεί HoldForm[] και μετατρέπει Pi->\\pi, Sqrt[]->\\sqrt{}.
    Bug #12: Τα labels μπορεί να είναι πολύ μακριά (Fourier series).
             linelegend_to_svg() τα αποδίδει σε HTML div με overflow-x:auto."""
    if 'LineLegend' not in data_str: return None
    colors = re.findall(r'RGBColor\[([\.\d]+),\s*([\.\d]+),\s*([\.\d]+)\]', data_str)
    if not colors: return None
    hex_colors = ['#{:02x}{:02x}{:02x}'.format(
        int(float(r)*255), int(float(g)*255), int(float(b)*255))
        for r,g,b in colors]
    # Extract second {}-group (labels) from LineLegend[{...},{...},...]
    ll = re.search(r'LineLegend\[\{.*?\},\s*(\{.*?\})', data_str, re.DOTALL)
    labels_str = ll.group(1) if ll else '{}'
    # Split by top-level commas
    parts, depth, cur = [], 0, ''
    for ch in labels_str.strip('{}'):
        if ch in '([{': depth += 1
        elif ch in ')]}': depth -= 1
        if ch == ',' and depth == 0: parts.append(cur.strip()); cur = ''
        else: cur += ch
    if cur.strip(): parts.append(cur.strip())
    def to_text(lbl):
        m = re.match(r'HoldForm\[(\w[\w\d]*)\[HoldForm\[(\w+)\]\]\]', lbl)
        if m: return f'{m.group(1)}[{m.group(2)}]'
        m = re.match(r'HoldForm\[Subscript\[(\w+),\s*(\w+)\]\]', lbl)
        if m: return f'{m.group(1)}₂{m.group(2)}'
        m = re.match(r'HoldForm\[Placeholder\[.*?(\d+).*?\]\]', lbl)
        if m: return f'Series {m.group(1)}'
        # Strip all HoldForm[] wrappers anywhere in the expression
        def _strip_hf(s):
            prev = None
            while prev != s:
                prev = s
                s = re.sub(r'HoldForm\[([^\[\]]*)\]', r'\1', s)
            return s
        lbl_clean = _strip_hf(lbl)
        # Also convert basic WL math: Pi→\pi, Sqrt[n]→\sqrt{n}, *→·
        lbl_clean = re.sub(r'Sqrt\[(\d+)\]', r'\\sqrt{\1}', lbl_clean)
        lbl_clean = re.sub(r'Pi\^(\d+)', r'\\pi^{\1}', lbl_clean)
        lbl_clean = lbl_clean.replace('Pi', '\\pi ')
        lbl_clean = re.sub(r'\*', ' ', lbl_clean)
        return lbl_clean.strip("'\" ")
    labels = [to_text(p) for p in parts]
    n = min(len(hex_colors), len(labels))
    return list(zip(hex_colors[:n], labels[:n])) if n else None


def linelegend_to_svg(entries, svg_height=370):
    """Παράγει scrollable HTML legend panel από (color, label) pairs. (Bug #12)

    Αλλαγή από SVG <text> σε HTML <div> με MathJax labels:
    - Bug #12: Τα Fourier series labels ήταν πολύ μακριά → ξεχείλιζαν.
      Τώρα: max-width:320px + overflow-x:auto scroll στη legend μπάρα.
    - Τα labels που περιέχουν math (^, \\, /) τυλίγονται σε \\(...\\) για MathJax.
    - Bug #11: HoldForm[x] έχει αφαιρεθεί πριν φτάσουν εδώ (parse_linelegend).
    Επιστρέφει HTML string (div element), ΟΧΙ SVG."""
    if not entries: return ''
    rows = []
    for color, label in entries:
        # Escape HTML special chars in label
        lbl_esc = label.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Detect if label contains math operators → wrap in \(...\) for MathJax
        has_math = any(c in label for c in ('^', '_', '\\', '/')) or any(
            kw in label for kw in ('\\pi', '\\sqrt', 'Cos', 'Sin', 'cos', 'sin'))
        lbl_html = f'\\({lbl_esc}\\)' if has_math else lbl_esc
        swatch = (f'<span style="display:inline-block;width:22px;height:2px;'
                  f'background:{color};vertical-align:middle;margin-right:5px;'
                  f'border-radius:1px;flex-shrink:0"></span>')
        rows.append(
            f'<div style="display:flex;align-items:center;padding:2px 0;min-width:0">'
            f'{swatch}'
            f'<span style="font-size:12px;color:#333;white-space:nowrap">{lbl_html}</span>'
            f'</div>'
        )
    inner = '\n'.join(rows)
    return (
        f'<div style="background:white;border:1px solid #ddd;border-radius:4px;'
        f'padding:8px 10px;align-self:flex-start;max-width:320px;'
        f'overflow-x:auto;flex-shrink:0">'
        f'{inner}</div>'
    )


def convert(inp: str, out: str):
    """Κύρια συνάρτηση μετατροπής: WLJS notebook → αυτόνομο στατικό HTML.
    
    ΦΑΣΗ 1 — Ανάγνωση και parsing:
      - Διαβάζει το WLJS HTML
      - Εξάγει custom CSS colors (cin/cout theme)
      - Αναλύει #cells-data (λίστα κελιών)
      - Αναλύει #json-objects (UUID → WL expression) και αποσυμπιέζει
      - Επιλύει VB indirection: uuid1 → VB("uuid2") → gmap[uuid2]
    
    ΦΑΣΗ 2 — Μετατροπή κελιών:
      Για κάθε κελί (Association με Type/Display/Data):
        Input codemirror   → <pre><code> (syntax colored)
        Input markdown     → skip (αντικαθίσταται από Output)
        Output markdown    → rendered HTML (render_md)
        Output codemirror → γραφήματα, math, plain text:
            FrontEndRef[uuid] → lookup gmap → render Graphics/Graphics3D/Image
            is_wl_output      → LaTeX via wljs_to_latex (MathJax)
            else              → plain text / formatted output
    
    ΦΑΣΗ 3 — Παραγωγή HTML:
      - Ενσωμάτωση CSS (inline)
      - MathJax CDN script
      - TOC sidebar (floating, active-tracking JS)
      - Collapsible code cells (Fade=True)
      - Σύνοψη στατιστικών (κελιά, συμπίεση)
    """
    print(f'Διαβάζω: {inp}')
    raw = open(inp, encoding='utf-8').read()
    orig = len(raw)
    print(f'Αρχικό μέγεθος: {orig/1024/1024:.2f} MB')

    soup = BeautifulSoup(raw, 'html.parser')

    # ── ΦΑΣΗ 1a: Εξαγωγή custom CSS colors (cin/cout background) ─────────────
    custom_css = ''.join(
        (s.string or '') for s in soup.head.find_all('style')
        if 'tailwindcss' not in (s.string or '')
    )
    C = parse_colors(custom_css)

    # ── ΦΑΣΗ 1b: Parsing των cells (Input/Output) ─────────────────────────────
    # Δομή: cells_json['storage'][1][2] = λίστα Association objects
    # Κάθε Association έχει: 'Type', 'Display', 'Data', 'Invisible', κτλ.
    cells_json = json.loads(soup.find(id='cells-data').string)
    cells_list = cells_json['storage'][1][2]

    # ── ΦΑΣΗ 1c: Parsing των graphics objects ────────────────────────────────
    # Δομή: obj_json['storage'] = [head, Rule[uuid1, Hold[Graphics[...]]], ...]
    # Κάθε Hold[] μπορεί να περιέχει:
    #   - Compressed["base64zlib"] → αποσυμπιέζεται σε list
    #   - Άμεσο Graphics/Graphics3D/Image list
    #   - String (VB notation με FrontEndRef → δεύτερο επίπεδο indirection)
    # Ειδικές περιπτώσεις:
    #   - Κλειδιά που τελειώνουν σε 'bar' → pre-rendered colorbar Graphics
    #     (χρησιμοποιούνται για StreamPlot/VectorPlot PlotLegends->Automatic)
    #   - Κλειδιά UUID → ακριβής αντιστοίχιση με FrontEndRef["uuid"] στα cells
    obj_json = json.loads(soup.find(id='json-objects').string)
    gmap = {}
    for r in obj_json['storage'][1:]:
        if r[0]!='Rule': continue
        key=r[1].strip("'")
        val=r[2]
        if not isinstance(val,list) or val[0]!='Hold': continue
        g=val[1]
        if isinstance(g,list) and 'Compressed' in g[0]:
            try: g=decompress(g[1])
            except: continue
        gmap[key]=g
    # Επίλυση VB indirection: (*VB[*)(FrontEndRef["uuid2"])...) → gmap[uuid2]
    # Ορισμένα γραφήματα αποθηκεύονται με 2-επίπεδη αναφορά:
    # cell_data → FrontEndRef[uuid1] → gmap[uuid1] = VB string with FrontEndRef[uuid2]
    # → gmap[uuid2] = actual Graphics/Graphics3D
    #
    # Bug #26 (Legended StreamPlot/VectorPlot3D): τα cells με Legended wrapper
    # έχουν τη δομή: (*VB[*)(Legended[ToExpression[FrontEndRef["uuid1"]], BarLegend[...]])
    # Το uuid1 στο gmap αποθηκεύει άλλο (*VB[*)(FrontEndRef["uuid2"]) string.
    # Μετά το resolve: gmap[uuid1] → gmap[uuid2] = actual Graphics/Graphics3D.
    # Το cell data_str ΔΕΝ αλλάζει, άρα η BarLegend info παραμένει διαθέσιμη
    # για εξαγωγή του {vmin, vmax} range κατά τη render φάση.
    for key in list(gmap.keys()):
        g = gmap[key]
        if isinstance(g, str) and '(*VB[*)' in g:
            inner_uuids = re.findall(r'FrontEndRef\[.{0,5}([0-9a-f-]{36})', g)
            for iuuid in inner_uuids:
                if iuuid in gmap and isinstance(gmap[iuuid], list):
                    gmap[key] = gmap[iuuid]
                    break

    # ── Temporal queue (για Graph[] widgets χωρίς UUID) ───────────────────────
    # Ορισμένα dynamic widgets (Graph[], GameBoard κτλ.) δεν έχουν UUID reference
    # στο cell data (έχουν "temporal$..." string). Τα Arrowheads-containing
    # Graphics που δεν έχουν reference αποθηκεύονται σε queue και
    # αποδίδονται FIFO.
    # Σημείωση: Αυτό είναι heuristic. Λειτουργεί αξιόπιστα μόνο όταν τα
    # temporal cells εμφανίζονται με την ίδια σειρά που αποθηκεύτηκαν.
    # Αν υπάρχουν πολλαπλά Graph[] outputs, η αντιστοίχιση γίνεται positionally.
    _referenced_uuids = set()
    for _cell in cells_list[1:]:
        if not isinstance(_cell, list) or _cell[0]!='Association': continue
        for _r in _cell[1:]:
            if isinstance(_r,list) and _r[0]=='Rule' and _r[1]=="'Data'":
                _d=_r[2]
                if isinstance(_d,list) and _d[0]=='Association':
                    for _dr in _d[1:]:
                        if isinstance(_dr,list) and _dr[0]=='Rule' and _dr[1]=="'Data'":
                            for _u in re.findall(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', str(_dr[2])):
                                _referenced_uuids.add(_u)
    _temporal_queue = [v for k,v in gmap.items()
                       if k not in _referenced_uuids and isinstance(v,list) and v[0]=='Graphics'
                       and 'Arrowheads' in str(v)[:600]]

    blocks=[]
    headings=[]
    slug_cnt={}
    stats={k:0 for k in ('md','code','fade','math_out','plain_out','svg','img','3d','unk')}


    # ── ΦΑΣΗ 2: Μετατροπή κελιών ─────────────────────────────────────────────
    # Κάθε cell στο WLJS είναι Association με πεδία:
    #   'Data'    : το περιεχόμενο (string με WL/markdown/UUID reference)
    #   'Display' : 'codemirror' | 'markdown'
    #   'Type'    : 'Input' | 'Output'
    #   'Props'   : Association με Hidden:True/False, Fade:True/False
    # Τα Input cells με display='markdown' αντικαθίστανται από Output κελιά
    # (το WLJS αποδίδει markdown output από input). Τα Input codemirror με
    # Hidden:True επίσης παραλείπονται.
    for cell in cells_list[1:]:
        if not isinstance(cell,list) or cell[0]!='Association': continue
        drules={}
        for r in cell[1:]:
            if r[0]=='Rule' and r[1]=="'Data'":
                d=r[2]
                if isinstance(d,list) and d[0]=='Association':
                    for dr in d[1:]:
                        if dr[0]=='Rule': drules[dr[1]]=dr[2]

        data    = drules.get("'Data'",'')
        display = drules.get("'Display'",'').strip("'")
        ctype   = drules.get("'Type'", "''").strip("'")
        props   = drules.get("'Props'",[])

        if not isinstance(data,str): continue

        # Props: Hidden, Fade
        is_hidden=False; is_fade=False
        if isinstance(props,list) and props[0]=='Association':
            for pr in props[1:]:
                if pr[0]=='Rule':
                    if pr[1]=="'Hidden'": is_hidden=pr[2]
                    if pr[1]=="'Fade'":   is_fade=pr[2]

        # CSS class
        is_md_content = (display=='markdown' or data.startswith("'.md"))
        is_cin  = ctype=='Input'  and display!='markdown'
        is_cout = ctype=='Output'

        if is_cout:   wcls='cout'+(' cout-md' if is_md_content else '')
        elif is_cin:  wcls='cin' +(' cin-md'  if is_md_content else '')
        else:         wcls='other'

        # ── SKIP: Input codemirror hidden=True (source, replaced by Output markdown) ──
        if ctype=='Input' and display=='codemirror' and is_hidden:
            continue

        # ── Output markdown → rendered markdown ──────────────────────────────
        if display=='markdown':
            md_text = data.strip().strip("'")
            html_block = render_md(md_text)
            for m in re.finditer(r'<(h[1-4])[^>]*>(.*?)</h[1-4]>',html_block,re.DOTALL):
                lvl=int(m.group(1)[1])
                text=re.sub(r'<[^>]+>','',m.group(2)).strip()
                base=slugify(text)
                slug_cnt[base]=slug_cnt.get(base,0)+1
                slug=base if slug_cnt[base]==1 else f'{base}-{slug_cnt[base]}'
                headings.append((lvl,text,slug))
            blocks.append(f'<div class="cell {wcls}">{html_block}</div>')
            stats['md']+=1

        # ── Output latex: rendered LaTeX block (display='latex') — Bug #29 ────
        # Τα κελιά με display='latex' παράγονται από .latex input cells στο WLJS.
        # Περιέχουν έτοιμο LaTeX (π.χ. \begin{align*}...\end{align*}) ΌΧΙ WL
        # notation — δεν χρειάζονται wljs_to_latex() μετατροπή.
        # Εντελώς αγνοούνταν πριν τη διόρθωση: κανένα elif δεν τα έπιανε,
        # οπότε δεν παραγόταν κανένα HTML block για αυτά.
        elif display=='latex' and ctype=='Output':
            tex = data.strip("'").strip()
            if tex:
                html_out = (f'<div class="math-output">'
                            f'<div class="math-display">\\[{tex}\\]</div></div>')
                blocks.append(f'<div class="cell {wcls}">{html_out}</div>')
                stats['math_out'] += 1

        # ── Output print: Print["..."] output — Bug #28 ─────────────────────
        # Το display='print' είναι ο τύπος των Output cells που παράγονται από
        # Print["string"] στο Mathematica. Εντελώς αγνοούνταν πριν τη διόρθωση.
        # Το data περιέχει plain string (με outer quotes): '"(x,y)=(SX, SY)"'
        # Αποδίδεται ως monospace block (ίδιο με format_plain_output).
        elif display=='print' and ctype=='Output':
            txt = data.strip("'").strip('"').strip()
            if txt:
                esc = txt.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
                blocks.append(f'<div class="cell {wcls}"><code class="plain-out">{esc}</code></div>')
                stats['plain_out']+=1

        # ── Output codemirror: graphic, math, or plain ────────────────────────
        # Εδώ γίνεται το κύριο rendering των Output cells.
        # Το Output cell data μπορεί να είναι:
        #   - "temporal$..." : dynamic widget (Graph[], Board κτλ.) χωρίς UUID
        #   - "(*VB[*)(FrontEndRef["uuid"]...": graphics reference (UUID lookup)
        #   - "(*FB[*)..., (*SpB[*)..." : math με WL box notation → LaTeX
        #   - plain string: αριθμός, σύμβολο, αποτέλεσμα χωρίς formatting
        elif display=='codemirror' and ctype=='Output':
            # Temporal$ cells (dynamic widgets like Graph[]) → use _temporal_queue
            if 'temporal$' in str(data) and not re.search(r'[0-9a-f]{8}-[0-9a-f]{4}', str(data)):
                g_obj = _temporal_queue.pop(0) if _temporal_queue else None
                if g_obj is not None:
                    svg = graphics_to_svg(g_obj)
                    if svg:
                        blocks.append(f'<div class="cell {wcls} graphic">{svg}</div>')
                        stats['svg']+=1
                    else: stats['unk']+=1
                # else: skip silently (no matching object)
            elif 'FrontEndRef' in data:
                # FrontEndRef["uuid"] → lookup gmap → render as appropriate type.
                # Πιθανοί τύποι αντικειμένων: Graphics, Graphics3D, Image, Raster.
                # Μετά το render ελέγχεται αν υπάρχει legend:
                #   - LineLegend (Plot με PlotLegends->"Expressions") → parse_linelegend + linelegend_to_svg
                #   - BarLegend (StreamPlot, VectorPlot με PlotLegends->Automatic)
                #       → εξαγωγή {vmin,vmax} από cell data_str + proximity matching bar object
                #       → bar_graphics_to_svg (SVG colorbar)
                # Και τα δύο (γράφημα + legend) τυλίγονται σε flex div side-by-side.
                #
                # Σημαντικό για BarLegend range extraction (Bug #26):
                # Το WL αποθηκεύει scientific notation ως 3.05*^-6 (όχι 3.05e-6).
                # Το regex \{([0-9.e+\-*^]+),...\}\}\s*,\s*LabelStyle βρίσκει
                # το τελευταίο {num, num} ζεύγος πριν το LabelStyle (το πραγματικό range),
                # ΟΧΙ τα ενδιάμεσα {0, 1} ζεύγη από το ColorDataFunction domain.
                uuids=re.findall(r'FrontEndRef\[.{0,5}([0-9a-f-]{36})',data)
                # Bug #23 (uuids undefined): πρώην το re.findall() κλήθηκε
                # μέσα στο for loop → NameError αν το loop δεν εκτελέστηκε.
                # Τώρα ορίζεται πριν το for, ο κώδικας δεν διακόπτεται.
                for uuid in uuids:
                    g=gmap.get(uuid)
                    # Resolve one more level of VB indirection if needed.
                    # Αφορά κυρίως τα Legended[FrontEndRef["alias"]] cells:
                    # gmap["alias"] = (*VB[*)(FrontEndRef["real-uuid"]...)
                    # → gmap["real-uuid"] = actual Graphics/Graphics3D
                    # Το ΦΑΣΗ 1c pass κανονικά τα έχει ήδη λύσει, αλλά
                    # αυτό είναι safety net για τυχόν missed cases.
                    if isinstance(g,str) and '(*VB[*)' in g:
                        for u2 in re.findall(r'FrontEndRef\[.{0,5}([0-9a-f-]{36})',g):
                            if u2 in gmap and isinstance(gmap[u2],list): g=gmap[u2]; break
                    if not isinstance(g,list): continue
                    gtype=g[0]
                    if gtype=='Image':
                        b64=image_to_b64(g)
                        if b64:
                            blocks.append(f'<div class="cell {wcls} graphic"><img src="{b64}" alt="Plot" style="max-width:100%;min-width:min(100%,300px);height:auto;display:block;margin:auto;border-radius:4px"/></div>')
                            stats['img']+=1
                        else:
                            blocks.append(f'<div class="cell {wcls} graphic unk"><em>[εικόνα — pip install pillow]</em></div>')
                            stats['unk']+=1
                    elif gtype=='Graphics' and len(g)>1 and isinstance(g[1],list) and g[1][0]=='Raster':
                        # Raster image (e.g. MatrixPlot, DensityPlot)
                        b64=raster_to_b64(g)
                        if b64:
                            blocks.append(f'<div class="cell {wcls} graphic"><img src="{b64}" alt="Raster Plot" style="max-width:100%;height:auto;display:block;margin:auto;border-radius:4px"/></div>')
                            stats['img']+=1
                        else:
                            blocks.append(f'<div class="cell {wcls} graphic unk"><em>[Raster — pip install pillow]</em></div>')
                            stats['unk']+=1
                    elif gtype=='Graphics':
                        svg=graphics_to_svg(g)
                        if svg:
                            # Check if the cell also has a BarLegend → append colorbar
                            bar_html = ''
                            data_str = str(data)
                            # ── LineLegend (PlotLegends -> "Expressions" etc.) ──────────
                            if 'LineLegend' in data_str:
                                ll_entries = parse_linelegend(data_str)
                                if ll_entries:
                                    bar_html = linelegend_to_svg(
                                        ll_entries,
                                        svg_height=int(svg.split('height="')[1].split('"')[0]) if 'height="' in svg else 370)
                            if not bar_html and 'BarLegend' in data_str:
                                # Extract value range
                                # Bug fix: WL uses *^-6 for scientific notation; also match }} before LabelStyle
                                m_rng = re.search(r'\{([0-9.e+\-*^]+),\s*([0-9.e+\-*^]+)\}\s*\}\s*,\s*LabelStyle', data_str)
                                if m_rng:
                                    # Convert WL scientific notation (*^N) to Python float (eN)
                                    def _wl_float(s): return float(s.replace('*^','e'))
                                    vmin2, vmax2 = _wl_float(m_rng.group(1)), _wl_float(m_rng.group(2))
                                    # Match bar by closest y-span to (vmax2 - vmin2)
                                    val_span = vmax2 - vmin2
                                    best_bar = None; best_dist = float('inf')
                                    for bk, bv in gmap.items():
                                        if not bk.endswith('bar') or not isinstance(bv,list) or bv[0]!='Graphics': continue
                                        bp = bv[1]
                                        ys = []
                                        for be in bp[1:]:
                                            if not isinstance(be,list) or be[0]!='List': continue
                                            for bs in be[1:]:
                                                if isinstance(bs,list) and bs[0]=='Rectangle' and len(bs)>=3:
                                                    if isinstance(bs[1],list) and len(bs[1])>=3:
                                                        try: ys.append(float(bs[1][2]))
                                                        except: pass
                                                    if isinstance(bs[2],list) and len(bs[2])>=3:
                                                        try: ys.append(float(bs[2][2]))
                                                        except: pass
                                        if not ys: continue
                                        bar_span = max(ys) - min(ys)
                                        dist = abs(bar_span - val_span) / (val_span + 1e-10)
                                        if dist < best_dist: best_dist = dist; best_bar = bv
                                    bar_g = best_bar
                                    if bar_g:
                                        _bar_h = int(svg.split('height="')[1].split('"')[0]) if 'height="' in svg else 300
                                        _bar_id = f'cbgrad_{id(bar_g) & 0xFFFFFF}'
                                        bar_svg = bar_graphics_to_svg(bar_g, vmin2, vmax2, H=_bar_h, grad_id=_bar_id)
                                        if bar_svg:
                                            bar_html = bar_svg
                            if bar_html:
                                blocks.append(f'<div class="cell {wcls} graphic" style="display:flex;align-items:flex-start;gap:12px;overflow:visible"><div style="flex:0 0 auto">{svg}</div>{bar_html}</div>')
                            else:
                                blocks.append(f'<div class="cell {wcls} graphic">{svg}</div>')
                            stats['svg']+=1
                        else: stats['unk']+=1
                    elif gtype=='Graphics3D':
                        b64=g3d_to_b64_matplotlib(g)
                        if b64:
                            # Check for BarLegend in cell data (VectorPlot3D with PlotLegends->Automatic)
                            bar3d_html = ''
                            data_str_3d = str(data)
                            if 'BarLegend' in data_str_3d:
                                m3d = re.search(r'\{([0-9.e+\-*^]+),\s*([0-9.e+\-*^]+)\}\s*\}\s*,\s*LabelStyle', data_str_3d)
                                if m3d:
                                    def _wf(s): return float(s.replace('*^','e'))
                                    v3min, v3max = _wf(m3d.group(1)), _wf(m3d.group(2))
                                    # Find the matching pre-rendered bar in gmap
                                    best3=None; best3d=float('inf')
                                    for bk,bv in gmap.items():
                                        if not bk.endswith('bar') or not isinstance(bv,list) or bv[0]!='Graphics': continue
                                        bys=[]
                                        for be in bv[1][1:]:
                                            if not isinstance(be,list) or be[0]!='List': continue
                                            for bs in be[1:]:
                                                if isinstance(bs,list) and bs[0]=='Rectangle' and len(bs)>=3:
                                                    for ep in [bs[1],bs[2]]:
                                                        if isinstance(ep,list) and len(ep)>=3:
                                                            try: bys.append(float(ep[2]))
                                                            except: pass
                                        if not bys: continue
                                        d3 = abs((max(bys)-min(bys))-(v3max-v3min))/(abs(v3max-v3min)+1e-10)
                                        if d3 < best3d: best3d=d3; best3=bv
                                    if best3:
                                        _bid3 = f'cbgrad3d_{id(best3)&0xFFFFFF}'
                                        bar3d_html = bar_graphics_to_svg(best3, v3min, v3max, H=380, grad_id=_bid3)
                            if bar3d_html:
                                blocks.append(f'<div class="cell {wcls} graphic" style="display:flex;align-items:flex-start;gap:12px;overflow:visible"><img src="{b64}" alt="3D Plot" style="max-width:100%;height:auto;border-radius:4px"/>{bar3d_html}</div>')
                            else:
                                blocks.append(f'<div class="cell {wcls} graphic"><img src="{b64}" alt="3D Plot" style="max-width:100%;height:auto;display:block;margin:auto;border-radius:4px"/></div>')
                            stats['3d']+=1
                        else:
                            blocks.append(f'<div class="cell {wcls} graphic unk"><em>[3D — pip install matplotlib numpy]</em></div>')
                            stats['unk']+=1
            elif is_wl_output(data):
                html_out = format_wl_output(data)
                if html_out:
                    blocks.append(f'<div class="cell {wcls}">{html_out}</div>')
                    stats['math_out']+=1
            else:
                # Plain text with no WL notation
                plain_html = format_plain_output(data)
                if plain_html:
                    blocks.append(f'<div class="cell {wcls}">{plain_html}</div>')
                    stats['plain_out']+=1

        # ── Input codemirror hidden=False: Wolfram code ───────────────────────
        elif ctype=='Input' and display=='codemirror' and not is_hidden:
            code=data.strip("'")
            if not code.strip(): continue
            esc=code.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

            if is_fade:
                # Collapsible (Fade=True): ο χρήστης έχει επιλέξει "Fade input"
                # στο WLJS notebook. Εμφανίζεται μόνο μια λεπτή μπάρα (6px) —
                # κλικ πάνω της αναπτύσσει τον κώδικα με CSS transition.
                # Χρησιμοποιείται για να κρύψουμε βοηθητικό κώδικα που ο
                # αναγνώστης δεν χρειάζεται να δει κανονικά.
                blocks.append(
                    f'<div class="cell {wcls} code-fade">'
                    f'<div class="fade-bar" onclick="this.parentElement.classList.toggle(\'expanded\')" '
                    f'title="Κλικ για εμφάνιση/απόκρυψη κώδικα"></div>'
                    f'<pre class="fade-code"><code>{esc}</code></pre>'
                    f'</div>'
                )
                stats['fade']+=1
            else:
                # Normal visible code
                blocks.append(f'<div class="cell {wcls} code"><pre><code>{esc}</code></pre></div>')
                stats['code']+=1

    # ── Inject heading IDs & TOC ─────────────────────────────────────────────
    nb_html = '\n'.join(blocks)
    nb_html = inject_ids(nb_html, headings)
    toc_html = build_toc(headings)
    # Inject Title + Author above TOC
    title_text = next((text for lvl,text,_ in headings if lvl==1), 'Notebook')
    meta_html = (f'<a href="index.html" id="back-btn">&#8592; Αρχική</a>'
                 f'<div id="doc-title">{title_text}</div>'
                 f'<div id="doc-author">Κώστας Κούδας</div>')
    toc_html = toc_html.replace('{toc_meta_placeholder}', meta_html)

    title='ἐπιψαύσεις'

    # ── CSS ──────────────────────────────────────────────────────────────────
    TOC_W=240
    css=f"""
*,::before,::after{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:{C['body']};font-family:ui-sans-serif,system-ui,-apple-system,sans-serif;font-size:16px;line-height:1.7;color:#1a1a1a}}

/* ── TOC ── */
#toc{{position:fixed;top:0;left:0;width:{TOC_W}px;height:100vh;overflow-y:auto;
  background:rgba(30,28,32,0.97);padding:0 0 2rem;z-index:100;
  scrollbar-width:thin;scrollbar-color:#555 transparent}}
#toc::-webkit-scrollbar{{width:5px}}
#toc::-webkit-scrollbar-thumb{{background:#555;border-radius:3px}}
#toc-meta{{padding:.9rem 1rem .6rem;border-bottom:1px solid rgba(255,255,255,.12);margin-bottom:.3rem}}
#back-btn{{display:block;font-size:.75rem;color:rgba(255,255,255,.45);text-decoration:none;padding:.5rem 1rem .1rem;letter-spacing:.03em;transition:color .2s}}
#back-btn:hover{{color:rgba(255,255,255,.8)}}
#doc-title{{font-size:.78rem;font-weight:700;color:#7ab8f5;line-height:1.35;margin-bottom:.3rem;word-break:break-word}}
#doc-author{{font-size:.72rem;color:rgba(255,255,255,.5)}}
#toc-title{{color:#aaa;font-size:.72rem;font-weight:600;letter-spacing:.1em;
  text-transform:uppercase;padding:0 14px .6rem;
  border-bottom:1px solid rgba(255,255,255,.08);margin-bottom:.5rem}}
a.toc-item{{display:block;color:#c8c8d0;text-decoration:none;font-size:.82rem;
  line-height:1.4;padding:3px 14px 3px 8px;border-left:2px solid transparent;
  transition:color .15s,border-color .15s,background .15s;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
a.toc-item:hover{{color:#fff;background:rgba(255,255,255,.06);border-left-color:#6ab}}
a.toc-item.active{{color:#fff;border-left-color:#5af;background:rgba(90,160,255,.1)}}
a.toc-h1{{font-weight:600;font-size:.85rem;color:#e0e0e8}}
a.toc-h2{{font-weight:500}}
a.toc-h3,.toc-h4{{color:#aaa}}

/* ── Notebook ── */
#notebook{{margin-left:{TOC_W}px;max-width:820px;padding:1.5rem 1.5rem 5rem}}

/* ── Cells ── */
.cell{{margin:.25rem 0;padding:.5em .75em;border-radius:6px}}
.cin{{background:{C['cin']}}}.cout{{background:{C['cout']};overflow-x:auto}}
.cin.cin-md{{background:{C['cin_md']}}}.cout.cout-md{{background:{C['cout_md']}}}
.other{{background:transparent}}

/* ── Normal code ── */
.cell.code pre{{margin:0;background:transparent;font-family:ui-monospace,'Fira Code',monospace;font-size:.88em;white-space:pre-wrap;word-break:break-word}}
.cell.code code{{background:none;padding:0;color:inherit}}

/* ── Fade/collapsible code ── */
.cell.code-fade{{padding:0;overflow:hidden;border-radius:6px;
  transition:background .2s}}
.cell.code-fade .fade-bar{{
  height:6px;
  background:linear-gradient(to right,rgba(100,140,180,.35),rgba(100,140,180,.15));
  cursor:pointer;
  border-radius:6px 6px 0 0;
  transition:background .15s;
}}
.cell.code-fade .fade-bar:hover{{background:linear-gradient(to right,rgba(100,180,255,.6),rgba(100,180,255,.25))}}
.cell.code-fade .fade-code{{
  max-height:0;
  overflow:hidden;
  margin:0;
  padding:0;
  transition:max-height .3s ease, padding .3s ease;
  font-family:ui-monospace,'Fira Code',monospace;
  font-size:.88em;
  white-space:pre-wrap;
  word-break:break-word;
  background:rgba(0,0,0,.04);
}}
.cell.code-fade.expanded .fade-code{{
  max-height:2000px;
  padding:.5em .75em;
}}
.cell.code-fade code{{background:none;color:inherit}}

/* ── Math output ── */
.math-output{{padding:.2em .4em;overflow-x:auto;max-width:100%}}
.math-output .math-display{{margin:.6rem 0;overflow-x:auto;text-align:center;font-size:1.05em}}
.math-output .math-inline{{font-size:1.05em}}
.math-output code.plain-out{{background:rgba(0,0,0,.06);padding:.2em .5em;border-radius:4px;font-size:.9em;font-family:ui-monospace,monospace}}
/* ── Admonitions (:::warning etc.) ── */
.admonition{{margin:.6rem 0;border-radius:6px;overflow:hidden;border-left:4px solid #aaa}}
.adm-title{{padding:.35em .75em;font-weight:600;font-size:.92em}}
.adm-body{{padding:.4em .75em;font-size:.95em}}
.adm-warning,.adm-warn{{border-color:#e6ac00;background:#fff8e0}}.adm-warning .adm-title,.adm-warn .adm-title{{background:#ffd700;color:#6b4c00}}
.adm-note,.adm-info{{border-color:#3b9de8;background:#e8f4ff}}.adm-note .adm-title,.adm-info .adm-title{{background:#3b9de8;color:#fff}}
.adm-tip,.adm-hint{{border-color:#26a65b;background:#e8f9ee}}.adm-tip .adm-title,.adm-hint .adm-title{{background:#26a65b;color:#fff}}
.adm-danger,.adm-caution,.adm-error{{border-color:#d63031;background:#ffeaea}}.adm-danger .adm-title,.adm-caution .adm-title,.adm-error .adm-title{{background:#d63031;color:#fff}}
.adm-success,.adm-check{{border-color:#27ae60;background:#eafaf1}}.adm-success .adm-title,.adm-check .adm-title{{background:#27ae60;color:#fff}}

/* ── Markdown typography ── */
.cell h1{{font-size:2rem;font-weight:700;margin:1.4rem 0 .4rem;color:#111}}
.cell h2{{font-size:1.5rem;font-weight:650;margin:1.1rem 0 .35rem;color:#111;border-bottom:1px solid rgba(0,0,0,.12);padding-bottom:.15rem}}
.cell h3{{font-size:1.2rem;font-weight:600;margin:.9rem 0 .3rem;color:#222}}
.cell h4{{font-size:1.05rem;font-weight:600;margin:.75rem 0 .25rem}}
.cell p{{margin:.35rem 0 .55rem}}
.cell ul,.cell ol{{margin:.25rem 0 .5rem 1.5rem}}
.cell li{{margin:.12rem 0}}
.cell strong{{font-weight:700}}.cell em{{font-style:italic}}
.cell code{{background:rgba(0,0,0,.07);padding:.1em .3em;border-radius:3px;font-family:ui-monospace,monospace;font-size:.87em;color:#c0392b}}
.cell pre code{{background:none;color:inherit}}
.cell blockquote{{border-left:3px solid rgba(0,0,0,.15);margin:.7rem 0;padding:.15rem 0 .15rem 1rem;color:#555}}
.cell table{{border-collapse:collapse;width:100%;margin:.7rem 0}}
.cell th,.cell td{{border:1px solid rgba(0,0,0,.15);padding:.35rem .6rem}}
.cell th{{background:rgba(0,0,0,.06);font-weight:600}}
.cell a{{color:#2563eb;text-decoration:underline}}
.cell div.math-display{{margin:1rem 0;overflow-x:auto;text-align:center}}

/* ── Graphics ── */
.cell.graphic{{text-align:center;padding:.5em}}
.cell.graphic img{{border-radius:4px;box-shadow:0 1px 4px rgba(0,0,0,.15)}}
.cell.unk{{color:#888;font-style:italic;font-size:.9em}}

/* ── Mobile ── */
@media(max-width:700px){{
  /* TOC: κρυμμένο by default, εμφανίζεται ως overlay από πάνω */
  #toc{{
    position:fixed;
    top:0;left:0;right:0;
    width:100%;
    max-height:65vh;
    height:auto;
    transform:translateY(-110%);
    transition:transform .3s cubic-bezier(.4,0,.2,1);
    z-index:200;
    border-radius:0 0 12px 12px;
    box-shadow:0 8px 32px rgba(0,0,0,.45);
  }}
#toc-meta{{padding:.9rem 1rem .6rem;border-bottom:1px solid rgba(255,255,255,.12);margin-bottom:.3rem}}
#doc-title{{font-size:.78rem;font-weight:700;color:#7ab8f5;line-height:1.35;margin-bottom:.3rem;word-break:break-word}}
#doc-author{{font-size:.72rem;color:rgba(255,255,255,.5)}}
  #toc.mob-open{{
    transform:translateY(0);
  }}
  /* Κουμπί TOC (hamburger) — Απαίτηση: πάντα ορατό σε κινητά
     Πρόβλημα: position:fixed + right:X τοποθετεί το button σε σχέση με
     την άκρη του VIEWPORT, όχι του document. Όταν υπάρχουν πλατιά
     γραφήματα που προκαλούν horizontal scroll, ο χρήστης μπορεί να
     βλέπει τη μεριά της σελίδας χωρίς το button (που έχει ξεφύγει δεξιά).
     Λύση: αγκυρώνουμε στο bottom-LEFT (left:1rem) ώστε το button να
     παραμένει πάντα ορατό ανεξαρτήτως horizontal scroll. */
  #toc-btn{{
    display:flex;
    position:fixed;
    bottom:1.2rem;
    left:1rem;
    z-index:300;
    width:48px;height:48px;
    border-radius:50%;
    background:rgba(30,28,32,0.92);
    border:1px solid rgba(255,255,255,.15);
    box-shadow:0 4px 16px rgba(0,0,0,.4);
    cursor:pointer;
    align-items:center;justify-content:center;
    transition:background .15s,transform .15s;
    -webkit-tap-highlight-color:transparent;
  }}
  #toc-btn:active{{transform:scale(.92)}}
  #toc-btn svg{{width:22px;height:22px;fill:none;stroke:#c8c8d0;stroke-width:2;stroke-linecap:round}}
  /* Overlay για κλείσιμο */
  #toc-overlay{{
    display:none;
    position:fixed;inset:0;
    z-index:190;
    background:rgba(0,0,0,.35);
    -webkit-backdrop-filter:blur(2px);
    backdrop-filter:blur(2px);
  }}
  #toc-overlay.mob-open{{display:block}}
  /* Notebook full width */
  #notebook{{margin-left:0;padding:1rem .7rem 5rem}}
}}
@media(min-width:701px){{
  #toc-btn{{display:none}}
  #toc-overlay{{display:none}}
}}
@media print{{#toc{{display:none}}#toc-btn{{display:none}}#notebook{{margin-left:0;max-width:none}}body{{background:#fff}}.cin{{background:#f0f0f0!important}}.cout{{background:#e8f0f8!important}}}}
"""

    mathjax_cfg = """window.MathJax={tex:{inlineMath:[['$','$'],['\\\\(','\\\\)']],displayMath:[['$$','$$'],['\\\\[','\\\\]']],processEscapes:true},options:{skipHtmlTags:['script','noscript','style','textarea','pre']}};"""
    # MathJax 3.x config: υποστηρίζει \(...\) inline και \[...\] display math.
    # processEscapes:true → \$ ερμηνεύεται σωστά μέσα σε math.
    # skipHtmlTags: αποφυγή επεξεργασίας math μέσα σε code/script blocks.

    toc_js="""
(function(){
  /* ── Active link tracking ──
     Ανιχνεύει ποιο heading είναι ορατό (πάνω από τα 80px viewport top)
     και επισημαίνει τον αντίστοιχο TOC σύνδεσμο με class 'active'.
     Τρέχει στο scroll event με passive:true για performance. */
  const items=document.querySelectorAll('a.toc-item');
  const ids=Array.from(items).map(a=>a.getAttribute('href').slice(1));
  function updateActive(){
    let active=ids[0];
    for(const id of ids){const el=document.getElementById(id);if(el&&el.getBoundingClientRect().top<=80)active=id;}
    items.forEach(a=>a.classList.toggle('active',a.getAttribute('href')==='#'+active));
  }
  window.addEventListener('scroll',updateActive,{passive:true});
  updateActive();

  /* ── Mobile TOC toggle ── */
  const btn=document.getElementById('toc-btn');
  const toc=document.getElementById('toc');
  const overlay=document.getElementById('toc-overlay');
  if(!btn||!toc) return;

  function openToc(){
    toc.classList.add('mob-open');
    overlay.classList.add('mob-open');
    btn.setAttribute('aria-expanded','true');
    /* Scroll TOC to show active item */
    const active=toc.querySelector('a.toc-item.active');
    if(active) active.scrollIntoView({block:'nearest'});
  }
  function closeToc(){
    toc.classList.remove('mob-open');
    overlay.classList.remove('mob-open');
    btn.setAttribute('aria-expanded','false');
  }
  function toggleToc(){
    toc.classList.contains('mob-open') ? closeToc() : openToc();
  }

  btn.addEventListener('click',toggleToc);
  overlay.addEventListener('click',closeToc);

  /* Κλείσιμο όταν πατηθεί σύνδεσμος στο TOC */
  items.forEach(a=>a.addEventListener('click',()=>setTimeout(closeToc,120)));
})();"""

    # Mobile TOC button (☰ / ✕ icon που αλλάζει)
    toc_btn_html = """<div id="toc-overlay"></div>
<button id="toc-btn" aria-label="Πίνακας περιεχομένων" aria-expanded="false">
  <svg viewBox="0 0 24 24"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
</button>"""

    html_out=f"""<!DOCTYPE html>
<html lang="el">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width,initial-scale=1.0"/>
<title>{title}</title>
<style>{css}</style>
<script>{mathjax_cfg}</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" async></script>
</head>
<body>
{toc_html}
{toc_btn_html}
<div id="notebook">
{nb_html}
</div>
<script>{toc_js}</script>
</body>
</html>"""

    open(out,'w',encoding='utf-8').write(html_out)
    sz=len(html_out)
    print(f'Τελικό μέγεθος  : {sz/1024:.1f} KB  (συμπίεση {(1-sz/orig)*100:.1f}%)')
    print(f'Κελιά           : md={stats["md"]} code={stats["code"]} fade={stats["fade"]} '
          f'math={stats["math_out"]} plain={stats["plain_out"]} '
          f'svg={stats["svg"]} img={stats["img"]} 3d={stats["3d"]} unk={stats["unk"]}')
    print(f'TOC headings    : {len(headings)}')
    print(f'✓ {out}')


def run_gui():
    """
    Γραφικό μενού επιλογής αρχείων με tkinter.
    - Διπλό κλικ σε φάκελο -> πλοήγηση μέσα
    - Ctrl+κλικ / Shift+κλικ -> πολλαπλή επιλογή .html αρχείων
    - Αποθήκευση ως <όνομα>_COMPRESSED.html στον ίδιο φάκελο

    Το GUI είναι εναλλακτικό της command line χρήσης (sys.argv).
    Εμφανίζεται όταν ο χρήστης εκτελεί το script χωρίς arguments.
    Χρησιμοποιεί tkinter (stdlib) — δεν απαιτεί pip install.
    Dark theme με custom χρώματα (BG, FG, ACCENT κτλ.).
    Η μετατροπή τρέχει σύγχρονα (blocking) και το αποτέλεσμα
    εμφανίζεται στο log Text widget κάτω από τη λίστα αρχείων.
    """
    import tkinter as tk
    from tkinter import messagebox

    BG     = '#1e1c20'
    BG2    = '#2a282d'
    BG3    = '#343238'
    FG     = '#e0dfe4'
    FG2    = '#9a99a0'
    ACCENT = '#5a9ff5'
    FGDIR  = '#8ab4e8'
    SEL    = '#3a3050'
    BTN    = '#3d3a42'
    BTNACT = '#4d4a52'
    GREEN  = '#2a5a2a'
    GREENA = '#3a7a3a'
    FONT   = ('Segoe UI', 10)
    FONTB  = ('Segoe UI', 10, 'bold')
    FONTS  = ('Segoe UI', 9)
    FONTM  = ('Consolas', 9)

    # Emoji prefix: each emoji = 1 char, followed by 2 spaces = 3 chars total
    PFX_DIR  = '\U0001f4c1  '
    PFX_HTML = '\U0001f310  '
    PFX_LEN  = 3  # len(emoji) + len('  ') = 1 + 2

    root = tk.Tk()
    root.title('WLJS \u2192 Static HTML')
    root.configure(bg=BG)
    root.resizable(True, True)
    W, H = 800, 580
    root.update_idletasks()
    sx = (root.winfo_screenwidth()  - W) // 2
    sy = (root.winfo_screenheight() - H) // 2
    root.geometry(f'{W}x{H}+{sx}+{sy}')
    root.minsize(560, 420)

    cwd     = [str(Path.home())]
    entries = []            # list of (kind, Path): 'up'|'dir'|'html'
    sel_files = []          # selected html Paths

    def get_entries(path_str):
        p = Path(path_str)
        result = []
        if str(p.parent) != path_str:
            result.append(('up', p.parent))
        try:
            children = list(p.iterdir())
        except PermissionError:
            return result
        dirs  = sorted([e for e in children if e.is_dir() and not e.name.startswith('.')],
                       key=lambda e: e.name.lower())
        htmls = sorted([e for e in children
                        if e.is_file() and e.suffix.lower() == '.html'
                        and not e.stem.endswith('_COMPRESSED')],
                       key=lambda e: e.name.lower())
        for d in dirs:  result.append(('dir',  d))
        for h in htmls: result.append(('html', h))
        return result

    def refresh(new_path=None):
        nonlocal entries, sel_files
        if new_path is not None:
            cwd[0] = str(new_path)
        path_var.set(cwd[0])
        entries   = get_entries(cwd[0])
        sel_files = []
        lb.delete(0, tk.END)
        for kind, p in entries:
            if kind in ('up', 'dir'):
                label = PFX_DIR + ('..' if kind == 'up' else p.name)
                lb.insert(tk.END, label)
                lb.itemconfig(tk.END, fg=FGDIR, selectforeground=FGDIR)
            else:
                sz = p.stat().st_size
                lb.insert(tk.END, f'{PFX_HTML}{p.name}   ({sz/1024:.0f} KB)')
                lb.itemconfig(tk.END, fg=FG)
        update_status()

    def on_double_click(event):
        sel = lb.curselection()
        if not sel:
            return
        kind, p = entries[sel[0]]
        if kind in ('up', 'dir'):
            refresh(p)

    def on_select(event):
        nonlocal sel_files
        sel_files = [entries[i][1] for i in lb.curselection()
                     if entries[i][0] == 'html']
        update_status()

    def update_status():
        if sel_files:
            names = ', '.join(f.name for f in sel_files[:3])
            if len(sel_files) > 3:
                names += f'  (+{len(sel_files)-3})'
            lbl_sel.config(text=f'\u0395\u03c0\u03b9\u03bb\u03b5\u03b3\u03bc\u03ad\u03bd\u03b1: {names}', fg=ACCENT)
            btn_go.config(state=tk.NORMAL)
        else:
            lbl_sel.config(text='\u039a\u03b1\u03bc\u03af\u03b1 \u03b5\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae', fg=FG2)
            btn_go.config(state=tk.DISABLED)

    def do_convert():
        if not sel_files:
            return
        btn_go.config(state=tk.DISABLED, text='\u039c\u03b5\u03c4\u03b1\u03c4\u03c1\u03bf\u03c0\u03ae\u2026')
        log.config(state=tk.NORMAL)
        log.delete('1.0', tk.END)
        root.update()
        errors = []
        for src in sel_files:
            out = src.parent / (src.stem + '_COMPRESSED.html')
            log.insert(tk.END, f'\u25ba {src.name}\n')
            log.see(tk.END); root.update()
            try:
                convert(str(src), str(out))
                sz = out.stat().st_size
                log.insert(tk.END, f'  \u2713 \u2192 {out.name}  ({sz/1024:.0f} KB)\n\n')
            except Exception as e:
                log.insert(tk.END, f'  \u2717 \u03a3\u03c6\u03ac\u03bb\u03bc\u03b1: {e}\n\n')
                errors.append(src.name)
            log.see(tk.END); root.update()
        log.config(state=tk.DISABLED)
        btn_go.config(text='\u039c\u03b5\u03c4\u03b1\u03c4\u03c1\u03bf\u03c0\u03ae \u03b5\u03c0\u03b9\u03bb\u03b5\u03b3\u03bc\u03ad\u03bd\u03c9\u03bd')
        n_done = len(sel_files) - len(errors)
        refresh()
        if errors:
            messagebox.showwarning('\u03a0\u03c1\u03bf\u03b5\u03b9\u03b4\u03bf\u03c0\u03bf\u03af\u03b7\u03c3\u03b7',
                f'\u0391\u03c0\u03bf\u03c4\u03c5\u03c7\u03af\u03b1 \u03c3\u03b5 {len(errors)} \u03b1\u03c1\u03c7\u03b5\u03af\u03bf(-\u03b1):\n' + '\n'.join(errors))
        else:
            messagebox.showinfo('\u039f\u03bb\u03bf\u03ba\u03bb\u03ae\u03c1\u03c9\u03c3\u03b7',
                f'\u0395\u03c0\u03b9\u03c4\u03c5\u03c7\u03ae\u03c2 \u03bc\u03b5\u03c4\u03b1\u03c4\u03c1\u03bf\u03c0\u03ae {n_done} \u03b1\u03c1\u03c7\u03b5\u03af\u03bf\u03c5(-\u03c9\u03bd)!')

    def go_path(event=None):
        p = path_var.get().strip()
        if Path(p).is_dir():
            refresh(p)
        else:
            path_var.set(cwd[0])

    # UI
    tk.Label(root, text='WLJS \u2192 Static HTML', font=('Segoe UI', 13, 'bold'),
             bg=BG, fg=ACCENT).pack(pady=(14, 2))
    tk.Label(root, text='\u0395\u03c0\u03b9\u03bb\u03ad\u03be\u03c4\u03b5 .html \u2014 \u03b4\u03b9\u03c0\u03bb\u03cc \u03ba\u03bb\u03b9\u03ba \u03c3\u03b5 \u03c6\u03ac\u03ba\u03b5\u03bb\u03bf \u03b3\u03b9\u03b1 \u03c0\u03bb\u03bf\u03ae\u03b3\u03b7\u03c3\u03b7, Ctrl+\u03ba\u03bb\u03b9\u03ba \u03b3\u03b9\u03b1 \u03c0\u03bf\u03bb\u03bb\u03b1\u03c0\u03bb\u03ae \u03b5\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae',
             font=FONTS, bg=BG, fg=FG2).pack(pady=(0, 8))

    nav = tk.Frame(root, bg=BG)
    nav.pack(fill=tk.X, padx=14, pady=(0, 4))
    tk.Label(nav, text='\u03a6\u03ac\u03ba\u03b5\u03bb\u03bf\u03c2:', font=FONTS, bg=BG, fg=FG2).pack(side=tk.LEFT)
    path_var = tk.StringVar()
    pe = tk.Entry(nav, textvariable=path_var, font=FONTS,
                  bg=BG3, fg=FG, insertbackground=FG, relief=tk.FLAT, bd=5)
    pe.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(6, 6))
    pe.bind('<Return>', go_path)
    tk.Button(nav, text='\u039c\u03b5\u03c4\u03ac\u03b2\u03b1\u03c3\u03b7', font=FONTS,
              bg=BTN, fg=FG, activebackground=BTNACT, activeforeground=FG,
              relief=tk.FLAT, padx=8, command=go_path).pack(side=tk.LEFT)

    lf = tk.Frame(root, bg=BG2)
    lf.pack(fill=tk.BOTH, expand=True, padx=14, pady=(0, 4))
    sb = tk.Scrollbar(lf, bg=BG3, troughcolor=BG2, activebackground=ACCENT, relief=tk.FLAT)
    sb.pack(side=tk.RIGHT, fill=tk.Y)
    lb = tk.Listbox(lf, font=FONT, bg=BG2, fg=FG,
                    selectbackground=SEL, selectforeground='#ffffff',
                    activestyle='none', selectmode=tk.EXTENDED,
                    relief=tk.FLAT, bd=0, yscrollcommand=sb.set,
                    highlightthickness=0)
    lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sb.config(command=lb.yview)
    lb.bind('<Double-Button-1>', on_double_click)
    lb.bind('<<ListboxSelect>>', on_select)

    bf = tk.Frame(root, bg=BG)
    bf.pack(fill=tk.X, padx=14, pady=(0, 4))
    lbl_sel = tk.Label(bf, text='\u039a\u03b1\u03bc\u03af\u03b1 \u03b5\u03c0\u03b9\u03bb\u03bf\u03b3\u03ae',
                       font=FONTS, bg=BG, fg=FG2, anchor='w')
    lbl_sel.pack(side=tk.LEFT, fill=tk.X, expand=True)
    btn_go = tk.Button(bf, text='\u039c\u03b5\u03c4\u03b1\u03c4\u03c1\u03bf\u03c0\u03ae \u03b5\u03c0\u03b9\u03bb\u03b5\u03b3\u03bc\u03ad\u03bd\u03c9\u03bd',
                       font=FONTB, bg=GREEN, fg='#ccffcc',
                       activebackground=GREENA, activeforeground='#ffffff',
                       relief=tk.FLAT, padx=14, pady=5,
                       state=tk.DISABLED, command=do_convert)
    btn_go.pack(side=tk.RIGHT)

    lf2 = tk.Frame(root, bg=BG)
    lf2.pack(fill=tk.X, padx=14, pady=(0, 12))
    log = tk.Text(lf2, font=FONTM, bg=BG2, fg='#88cc88',
                  height=5, relief=tk.FLAT, bd=4,
                  state=tk.DISABLED, wrap=tk.WORD, highlightthickness=0)
    log.pack(fill=tk.X)

    refresh()
    root.mainloop()


if __name__ == '__main__':
    # Εκτέλεση:
    #   python3 wljs_to_static_v4.py input.html output.html  → CLI mode
    #   python3 wljs_to_static_v4.py                          → GUI mode (tkinter)
    if len(sys.argv) >= 3:
        convert(sys.argv[1], sys.argv[2])
    else:
        run_gui()