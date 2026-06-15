#!/usr/bin/env python3
"""
metabaseis_gen.py  v6
Input:   STATE |WEIGHT> STATE   (one per line)
Outputs: transition_matrix.tex  flow_diagram.svg  flow_diagram_no_labels.svg
Usage:   python metabaseis_gen.py [file]   (default: metabaseis.txt)
"""

import re, sys, math
from collections import defaultdict, deque


# ═══ CONSTANTS ════════════════════════════════════════════════════════════════

R          = 26
AH         = 10
CURVE_OFF  = 34
AVOID_R    = R + 10
LABEL_MARGIN = R + 10    # min distance from label centre to any node centre

NODE_FILL   = "#E74C3C"
NODE_STROKE = "#2980B9"
NODE_SW     = 3
EDGE_OUT_SW = 5
EDGE_IN_SW  = 2
EDGE_COLOR  = "#333333"


# ─── 1. PARSER ───────────────────────────────────────────────────────────────

def parse_file(path):
    transitions, order, seen = [], [], set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"\s*(\w+)\s*\|(\d+(?:\.\d+)?)\>\s*(\w+)", line)
            if m:
                s, w, d = m.group(1), m.group(2), m.group(3)
                transitions.append((s, w, d))
                for x in (s, d):
                    if x not in seen:
                        order.append(x); seen.add(x)
    return transitions, order


# ─── 2. LaTeX ────────────────────────────────────────────────────────────────

def build_latex(transitions, states):
    n = len(states)
    M = {s: {t: "0" for t in states} for s in states}
    for s, w, d in transitions: M[s][d] = w
    col_hdr = " & ".join(r"\mathbf{" + s + "}" for s in states)
    lines = [r"\[", r"\begin{array}{c|" + "c"*n + "}",
             "  & " + col_hdr + r" \\", r"\hline"]
    for s in states:
        lines.append(r"  \mathbf{" + s + "} & " +
                     " & ".join(M[s][t] for t in states) + r" \\")
    lines += [r"\end{array}", r"\]"]
    return "\n".join(lines)


# ─── 3. LAYOUT ───────────────────────────────────────────────────────────────

def compute_layout(states, transitions, W=640, H=360):
    adj = defaultdict(list)
    out_deg = {s: 0 for s in states}
    for s, _, d in transitions:
        if s != d:
            adj[s].append(d); out_deg[s] += 1

    depth, remaining = {}, set(states)
    while remaining:
        root = max(remaining, key=lambda x: out_deg[x])
        q = deque([(root, 0)])
        while q:
            node, dd = q.popleft()
            if node in depth: continue
            depth[node] = dd; remaining.discard(node)
            for nb in adj[node]:
                if nb not in depth: q.append((nb, dd + 1))

    col = defaultdict(list)
    for s, d in depth.items(): col[d].append(s)
    for d in col: col[d].sort()

    max_d = max(depth.values()) if depth else 0
    mx, my = 90, 60
    pos = {}
    for d, nodes in col.items():
        x = mx + d * (W - 2*mx) / max(max_d, 1)
        n = len(nodes)
        for j, node in enumerate(nodes):
            pos[node] = (x, my + (j + 0.5)*(H - 2*my)/n)
    return pos


# ─── 4. GEOMETRY & ROUTING HELPERS ───────────────────────────────────────────

def _pt(cx, cy, angle, r=None):
    if r is None: r = R
    return cx + r*math.cos(angle), cy + r*math.sin(angle)

def _label_half_w(text):
    return max(len(str(text)) * 4.5 + 2, 8)

def _dist_pt_to_segment(px, py, ax, ay, bx, by):
    dx, dy = bx-ax, by-ay
    l2 = dx*dx + dy*dy
    if l2 < 1e-10: return math.hypot(px-ax, py-ay)
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy) / l2))
    return math.hypot(px-(ax+t*dx), py-(ay+t*dy))

def _sample_path(sx, sy, cpx, cpy, ex, ey, t):
    if cpx is None:
        return sx + t*(ex-sx), sy + t*(ey-sy)
    return ((1-t)**2*sx + 2*t*(1-t)*cpx + t**2*ex,
            (1-t)**2*sy + 2*t*(1-t)*cpy + t**2*ey)

def _dist_pt_to_path(px, py, sx, sy, cpx, cpy, ex, ey, n=40):
    if cpx is None:
        return _dist_pt_to_segment(px, py, sx, sy, ex, ey)
    best = float('inf')
    for i in range(n+1):
        t = i/n
        qx, qy = _sample_path(sx, sy, cpx, cpy, ex, ey, t)
        d = (px-qx)**2 + (py-qy)**2
        if d < best: best = d
    return math.sqrt(best)

def _bq_min_dist(sx, sy, cpx, cpy, ex, ey, px, py, n=60):
    best = float('inf')
    for i in range(n+1):
        t = i/n
        qx = (1-t)**2*sx + 2*t*(1-t)*cpx + t**2*ex
        qy = (1-t)**2*sy + 2*t*(1-t)*cpy + t**2*ey
        d = (qx-px)**2 + (qy-py)**2
        if d < best: best = d
    return math.sqrt(best)

def _seg_hits_circle(ax, ay, bx, by, cx, cy, r):
    dx, dy = bx-ax, by-ay
    fx, fy = ax-cx, ay-cy
    a = dx*dx + dy*dy
    if a < 1e-10: return False
    b = 2*(fx*dx + fy*dy)
    c = fx*fx + fy*fy - r*r
    disc = b*b - 4*a*c
    if disc < 0: return False
    sq = math.sqrt(disc)
    t1 = (-b-sq)/(2*a); t2 = (-b+sq)/(2*a)
    return (0.05 < t1 < 0.95) or (0.05 < t2 < 0.95)

def _blocked(sx, sy, cpx, cpy, ex, ey, pos, states, src, dst):
    out = []
    for st in states:
        if st in (src, dst): continue
        cx, cy = pos[st]
        if cpx is None:
            if _seg_hits_circle(sx, sy, ex, ey, cx, cy, AVOID_R): out.append(st)
        else:
            if _bq_min_dist(sx, sy, cpx, cpy, ex, ey, cx, cy) < AVOID_R: out.append(st)
    return out

def _route_straight(sx, sy, ex, ey, pos, states, src, dst):
    if not _blocked(sx, sy, None, None, ex, ey, pos, states, src, dst):
        return None
    mx, my = (sx+ex)/2, (sy+ey)/2
    dx, dy = ex-sx, ey-sy
    length = math.sqrt(dx*dx + dy*dy)
    if length < 1e-10: return None
    perp_x, perp_y = -dy/length, dx/length
    for sign in (1, -1):
        for mult in (1.5, 2.5, 3.5, 5.0, 7.0, 10.0):
            cpx = mx + sign*mult*AVOID_R*perp_x
            cpy = my + sign*mult*AVOID_R*perp_y
            if not _blocked(sx, sy, cpx, cpy, ex, ey, pos, states, src, dst):
                return (cpx, cpy)
    return (mx + 3*AVOID_R*perp_x, my + 3*AVOID_R*perp_y)

def _route_bidir(sx, sy, cpx, cpy, ex, ey, pos, states, src, dst):
    if not _blocked(sx, sy, cpx, cpy, ex, ey, pos, states, src, dst):
        return cpx, cpy
    mx, my = (sx+ex)/2, (sy+ey)/2
    dx_cp, dy_cp = cpx-mx, cpy-my
    base = math.sqrt(dx_cp**2 + dy_cp**2)
    if base < 1e-10: return cpx, cpy
    ux, uy = dx_cp/base, dy_cp/base
    for mult in (2.0, 3.0, 4.5, 6.0, 8.0):
        ncpx = mx + mult*base*ux
        ncpy = my + mult*base*uy
        if not _blocked(sx, sy, ncpx, ncpy, ex, ey, pos, states, src, dst):
            return ncpx, ncpy
    return cpx, cpy


# ─── 5. SELF-LOOP WITH DIRECTION SELECTION ───────────────────────────────────

def _make_selfloop(x1, y1, pos, states, node_name, scale=3.8):
    """
    Try 8 axis directions for the self-loop arc and choose the one that
    maximises clearance from every other node.
    """
    # Candidates: up first (preferred default), then alternatives
    axes = [
        -math.pi/2,          # up
         math.pi/2,          # down
         0,                  # right
         math.pi,            # left
        -math.pi/4,          # upper-right
        -3*math.pi/4,        # upper-left
         math.pi/4,          # lower-right
         3*math.pi/4,        # lower-left
    ]

    best_params   = None
    best_clearance = -1.0

    for axis in axes:
        sa  = axis - math.pi/6
        ea  = axis + math.pi/6
        bx,  by    = _pt(x1, y1, sa)
        ex_r, ey_r = _pt(x1, y1, ea)
        cpx = x1 + R*scale*math.cos(axis)
        cpy = y1 + R*scale*math.sin(axis)
        tang = math.atan2(ey_r - cpy, ex_r - cpx)
        ex_p = ex_r - AH*math.cos(tang)
        ey_p = ey_r - AH*math.sin(tang)

        # Min distance of bezier arc from any other node
        other_nodes = [st for st in states if st != node_name]
        if other_nodes:
            min_d = min(
                _bq_min_dist(bx, by, cpx, cpy, ex_p, ey_p,
                             pos[st][0], pos[st][1])
                for st in other_nodes
            )
        else:
            min_d = float('inf')

        if min_d > best_clearance:
            best_clearance = min_d
            best_params = (bx, by, cpx, cpy, ex_p, ey_p)

        if min_d > AVOID_R:
            break   # good enough — stop at first clear direction

    bx, by, cpx, cpy, ex_p, ey_p = best_params
    path = (f"M {bx:.1f},{by:.1f} "
            f"Q {cpx:.1f},{cpy:.1f} {ex_p:.1f},{ey_p:.1f}")
    lx = (bx + 2*cpx + ex_p) / 4
    ly = (by + 2*cpy + ey_p) / 4
    return path, lx, ly, bx, by, cpx, cpy, ex_p, ey_p


# ─── 6. LABEL POSITION OPTIMISER ─────────────────────────────────────────────

def _optimise_label_positions(records, pos, states, n_samples=30):
    """
    For each non-self-loop edge, find the t ∈ [0.10, 0.90] that:
      (a) is at least LABEL_MARGIN away from every node, AND
      (b) maximises the minimum distance to all other edges.

    If no on-path position satisfies (a) (very short edge), the label is
    placed perpendicular to the edge midpoint at a safe offset.
    """
    non_loops = [r for r in records if not r['self_loop']]

    for rec in non_loops:
        others = [o for o in non_loops if o is not rec]
        best_t      = 0.5
        best_score  = -float('inf')
        found_valid = False

        for i in range(n_samples + 1):
            t = 0.10 + 0.80 * i / n_samples
            px, py = _sample_path(rec['gsx'], rec['gsy'],
                                  rec['gcpx'], rec['gcpy'],
                                  rec['gex'], rec['gey'], t)

            # Constraint: must be sufficiently clear of every node
            node_min = min(
                math.hypot(px - pos[st][0], py - pos[st][1])
                for st in states
            )
            if node_min < LABEL_MARGIN:
                continue

            # Score: min distance to any other edge
            # (for a single edge, use node clearance as score so we prefer the centre)
            if others:
                score = min(
                    _dist_pt_to_path(px, py,
                                     o['gsx'], o['gsy'],
                                     o['gcpx'], o['gcpy'],
                                     o['gex'], o['gey'])
                    for o in others
                )
            else:
                score = node_min

            if score > best_score:
                best_score = score
                best_t     = t
                found_valid = True

        if found_valid:
            rec['lx'], rec['ly'] = _sample_path(
                rec['gsx'], rec['gsy'],
                rec['gcpx'], rec['gcpy'],
                rec['gex'], rec['gey'], best_t
            )
        else:
            # Very short edge: no on-path position clears all nodes.
            # Offset the label PERPENDICULARLY from the edge midpoint.
            px, py = _sample_path(rec['gsx'], rec['gsy'],
                                  rec['gcpx'], rec['gcpy'],
                                  rec['gex'], rec['gey'], 0.5)
            dx = rec['gex'] - rec['gsx']
            dy = rec['gey'] - rec['gsy']
            length = math.hypot(dx, dy)
            placed = False
            if length > 1e-10:
                perp_x, perp_y = -dy/length, dx/length
                for sign in (1, -1):
                    for offset in (R+16, R+30, R+48):
                        nlx = px + sign*offset*perp_x
                        nly = py + sign*offset*perp_y
                        if all(math.hypot(nlx-pos[st][0], nly-pos[st][1]) >= R+6
                               for st in states):
                            rec['lx'], rec['ly'] = nlx, nly
                            placed = True
                            break
                    if placed: break
            if not placed:
                rec['lx'], rec['ly'] = px, py   # absolute last resort


# ─── 7. LABEL OVERLAP RESOLUTION ─────────────────────────────────────────────

def _resolve_overlaps(labels, iterations=40):
    PAD = 4
    for _ in range(iterations):
        moved = False
        for i in range(len(labels)):
            for j in range(i+1, len(labels)):
                xi, yi, wi, hi = labels[i]
                xj, yj, wj, hj = labels[j]
                ox = (wi+wj+PAD) - abs(xj-xi)
                oy = (hi+hj+PAD) - abs(yj-yi)
                if ox > 0 and oy > 0:
                    moved = True
                    if ox <= oy:
                        push = ox/2+1; sign = 1 if xj >= xi else -1
                        labels[i][0] -= sign*push; labels[j][0] += sign*push
                    else:
                        push = oy/2+1; sign = 1 if yj >= yi else -1
                        labels[i][1] -= sign*push; labels[j][1] += sign*push
        if not moved: break
    return labels


# ─── 8. SVG ──────────────────────────────────────────────────────────────────

_DEFS = ("""  <defs>
    <marker id="ah_out" viewBox="0 0 12 12" refX="0" refY="6"
            markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12"
            orient="auto">
      <path d="M0,1.5 L10,6 L0,10.5 Z" fill="{ec}"/>
    </marker>
    <marker id="ah_in"  viewBox="0 0 12 12" refX="0" refY="6"
            markerUnits="userSpaceOnUse" markerWidth="12" markerHeight="12"
            orient="auto">
      <path d="M0,3 L9,6 L0,9 Z" fill="white"/>
    </marker>
    <filter id="glow-g" x="-70%" y="-70%" width="240%" height="240%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="3" result="blur"/>
      <feFlood flood-color="#2ECC71" flood-opacity="1" result="color"/>
      <feComposite in="color" in2="blur" operator="in" result="glow"/>
      <feMerge>
        <feMergeNode in="glow"/>
        <feMergeNode in="glow"/>
        <feMergeNode in="SourceGraphic"/>
      </feMerge>
    </filter>
  </defs>""").replace("{ec}", EDGE_COLOR)


def build_svg(transitions, states, with_labels=True):
    W, H = 640, 360
    pos  = compute_layout(states, transitions, W, H)
    ew   = {(s, d): w for s, w, d in transitions}

    records = []

    for (s, d), w in ew.items():
        x1, y1 = pos[s]
        x2, y2 = pos[d]

        # ── Self-loop ─────────────────────────────────────────────────────
        if s == d:
            path, lx, ly, gsx, gsy, gcpx, gcpy, gex, gey = \
                _make_selfloop(x1, y1, pos, states, s)
            records.append({
                'path': path, 'lx': lx, 'ly': ly, 'label': w,
                'self_loop': True,
                'gsx': gsx, 'gsy': gsy, 'gcpx': gcpx, 'gcpy': gcpy,
                'gex': gex, 'gey': gey,
            })
            continue

        bidir = (d, s) in ew

        # ── Bidirectional: quadratic arc ───────────────────────────────────
        if bidir:
            ang  = math.atan2(y2-y1, x2-x1)
            perp = ang + math.pi/2
            cpx_ = (x1+x2)/2 + CURVE_OFF*math.cos(perp)
            cpy_ = (y1+y2)/2 + CURVE_OFF*math.sin(perp)
            a1 = math.atan2(cpy_-y1, cpx_-x1)
            a2 = math.atan2(cpy_-y2, cpx_-x2)
            sx, sy     = _pt(x1, y1, a1)
            ex_r, ey_r = _pt(x2, y2, a2)
            tang = math.atan2(ey_r-cpy_, ex_r-cpx_)
            ex_p = ex_r - AH*math.cos(tang)
            ey_p = ey_r - AH*math.sin(tang)
            cpx_, cpy_ = _route_bidir(sx, sy, cpx_, cpy_, ex_p, ey_p,
                                      pos, states, s, d)
            path = (f"M {sx:.1f},{sy:.1f} "
                    f"Q {cpx_:.1f},{cpy_:.1f} {ex_p:.1f},{ey_p:.1f}")
            lx = (sx + 2*cpx_ + ex_p)/4
            ly = (sy + 2*cpy_ + ey_p)/4
            records.append({
                'path': path, 'lx': lx, 'ly': ly, 'label': w,
                'self_loop': False,
                'gsx': sx,   'gsy': sy,
                'gcpx': cpx_, 'gcpy': cpy_,
                'gex': ex_p, 'gey': ey_p,
            })

        # ── Unidirectional: straight or detoured bezier ────────────────────
        else:
            ang = math.atan2(y2-y1, x2-x1)
            sx, sy = _pt(x1, y1, ang)
            ex_p   = x2 - (R+AH)*math.cos(ang)
            ey_p   = y2 - (R+AH)*math.sin(ang)
            cp = _route_straight(sx, sy, ex_p, ey_p, pos, states, s, d)
            if cp is None:
                cpx_, cpy_ = None, None
                path = f"M {sx:.1f},{sy:.1f} L {ex_p:.1f},{ey_p:.1f}"
            else:
                cpx_, cpy_ = cp
                path = (f"M {sx:.1f},{sy:.1f} "
                        f"Q {cpx_:.1f},{cpy_:.1f} {ex_p:.1f},{ey_p:.1f}")
            lx, ly = (sx+ex_p)/2, (sy+ey_p)/2
            records.append({
                'path': path, 'lx': lx, 'ly': ly, 'label': w,
                'self_loop': False,
                'gsx': sx,    'gsy': sy,
                'gcpx': cpx_, 'gcpy': cpy_,
                'gex': ex_p,  'gey': ey_p,
            })

    # ── Optimise label positions ───────────────────────────────────────────
    if with_labels:
        _optimise_label_positions(records, pos, states)

    # ── Resolve remaining label-box overlaps ───────────────────────────────
    if with_labels:
        movable = [r for r in records if not r['self_loop']]
        if len(movable) > 1:
            lab = [[r['lx'], r['ly'], _label_half_w(r['label']), 8]
                   for r in movable]
            _resolve_overlaps(lab)
            for i, r in enumerate(movable):
                r['lx'], r['ly'] = lab[i][0], lab[i][1]

    # ── Assemble SVG ──────────────────────────────────────────────────────
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">',
        _DEFS,
        f'  <rect width="{W}" height="{H}" fill="#EFF2F7" rx="8"/>',
    ]

    for r in records:
        svg.append(f'  <path d="{r["path"]}" fill="none" '
                   f'stroke="{EDGE_COLOR}" stroke-width="{EDGE_OUT_SW}" '
                   f'stroke-linecap="butt" marker-end="url(#ah_out)"/>')
        svg.append(f'  <path d="{r["path"]}" fill="none" '
                   f'stroke="white" stroke-width="{EDGE_IN_SW}" '
                   f'stroke-linecap="butt" marker-end="url(#ah_in)"/>')

    if with_labels:
        for r in records:
            svg.append(
                f'  <text x="{r["lx"]:.1f}" y="{r["ly"]:.1f}" '
                f'text-anchor="middle" dominant-baseline="central" '
                f'font-family="sans-serif" font-size="13" font-weight="bold" '
                f'filter="url(#glow-g)" fill="#111">{r["label"]}</text>'
            )

    for state in states:
        x, y = pos[state]
        svg += [
            f'  <circle cx="{x:.0f}" cy="{y:.0f}" r="{R}" '
            f'fill="{NODE_FILL}" stroke="{NODE_STROKE}" stroke-width="{NODE_SW}"/>',
            f'  <text x="{x:.0f}" y="{y:.0f}" text-anchor="middle" '
            f'dominant-baseline="central" font-family="sans-serif" '
            f'font-size="16" font-weight="bold" fill="white">{state}</text>',
        ]

    svg.append("</svg>")
    return "\n".join(svg)


# ─── 9. MAIN ─────────────────────────────────────────────────────────────────

def main():
    fname = sys.argv[1] if len(sys.argv) > 1 else "metabaseis.txt"
    transitions, states = parse_file(fname)
    if not transitions:
        print("Δεν βρέθηκαν έγκυρες μεταβάσεις στο αρχείο."); return

    tex = build_latex(transitions, states)
    with open("transition_matrix.tex", "w", encoding="utf-8") as f:
        f.write(f"% Transition matrix — source: {fname}\n\n{tex}\n")
    print("✓  transition_matrix.tex")

    with open("flow_diagram.svg", "w", encoding="utf-8") as f:
        f.write(build_svg(transitions, states, with_labels=True) + "\n")
    print("✓  flow_diagram.svg")

    with open("flow_diagram_no_labels.svg", "w", encoding="utf-8") as f:
        f.write(build_svg(transitions, states, with_labels=False) + "\n")
    print("✓  flow_diagram_no_labels.svg")

    print(f"\n{'─'*44}\nLaTeX:\n{'─'*44}\n{tex}\n")

if __name__ == "__main__":
    main()
