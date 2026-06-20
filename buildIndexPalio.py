#!/usr/bin/env python3
"""
build.py  —  Διαβάζει content.txt και παράγει index.html

Σύνταξη content.txt
────────────────────
<about>{κουμπί navbar}{τίτλος modal}</about>
...σώμα modal (παράγραφοι, [σύνδεσμοι](url), --- για <hr>)...

# Τίτλος <listmenu>        →  dropdown με ιεραρχική λίστα
  [Κείμενο](url)           →  απλό item
  ## Υπότιτλος             →  sub-dropdown (επίπεδο 2)
  ### Υπότιτλος            →  sub-dropdown (επίπεδο 3)
  #### Υπότιτλος           →  sub-dropdown (επίπεδο 4)

# Τίτλος <colmenu>         →  megamenu με στήλες
  ## Τίτλος στήλης         →  νέα στήλη
  [Κείμενο](url)           →  item στήλης

# Τίτλος <hero>            →  το hero section (πρώτη γραμμή = h2, επόμενες = <p>)
"""

import re
import sys
from pathlib import Path
from html import escape

# ── Wolfram SVG path (ακριβώς από το πρότυπο) ──────────────────────────────
SVG_PATH = (
    'M5510 5656 c-17 -22 -3 -95 31 -154 59 -104 158 -158 394 -216 55 -13 127 -34 160 -46 92 -34 98 -35 93 -19 -7 21 -120 74 -233 109 -137 43 -274 110 -328 159 -45 42 -87 114 -87 150 0 26 -15 34 -30 17z '
    'M5560 5653 c0 -10 29 -24 195 -94 28 -12 173 -60 215 -71 19 -5 51 -14 70 -19 19 -6 51 -14 70 -19 124 -30 193 -50 217 -62 41 -21 77 -42 83 -49 32 -37 268 -165 291 -157 12 4 -152 118 -170 118 -5 0 -11 3 -13 8 -4 9 -112 84 -158 109 -34 18 -68 30 -155 51 -47 12 -114 30 -170 44 -52 14 -164 48 -190 58 -188 73 -285 101 -285 83z '
    'M5765 5224 c-139 -15 -506 -35 -648 -35 -103 0 -127 -14 -56 -32 38 -10 406 -2 569 13 284 25 311 24 495 -15 266 -57 384 -74 578 -84 208 -12 231 -19 352 -117 169 -136 274 -209 451 -314 194 -115 371 -231 427 -278 40 -34 137 -131 158 -157 26 -35 111 -216 124 -265 3 -14 11 -41 16 -60 5 -19 13 -55 18 -80 5 -25 17 -85 27 -135 22 -115 26 -510 6 -625 -68 -382 -190 -684 -435 -1080 -128 -208 -376 -470 -602 -636 -376 -278 -866 -444 -1387 -470 -147 -7 -178 2 -80 24 54 13 214 63 257 82 11 4 58 23 105 41 258 99 607 333 823 552 378 384 621 864 712 1407 35 209 27 594 -15 705 -13 35 -8 42 43 57 57 17 117 78 117 119 0 71 -92 103 -156 54 -40 -30 -52 -52 -68 -114 -11 -46 -11 -46 -131 -43 -192 5 -332 43 -616 168 -192 84 -231 98 -354 128 -134 34 -324 70 -465 90 -92 13 -213 63 -230 96 -14 27 29 74 99 107 85 41 237 39 371 -4 177 -58 339 -80 472 -63 102 12 182 27 213 40 93 37 105 44 105 62 0 19 -19 24 -35 9 -6 -5 -37 -18 -69 -29 -66 -24 -84 -19 -106 25 -61 117 -144 217 -224 268 -85 53 -136 65 -337 75 -184 10 -244 20 -308 53 -43 22 -60 22 -68 0 -4 -10 -12 -23 -17 -29 -15 -14 -133 -94 -140 -94 -3 0 -35 -13 -71 -30 -36 -16 -70 -30 -76 -30 -16 0 -89 -39 -151 -81 -140 -95 -257 -136 -358 -124 -75 9 -77 23 -7 63 28 17 102 67 162 111 61 45 184 132 275 193 91 61 198 136 238 165 98 73 148 91 207 75 25 -7 71 -12 103 -12 31 0 75 -5 97 -10 22 -5 167 -10 322 -10 309 0 316 -1 406 -63 45 -30 62 -36 70 -27 15 15 -56 79 -123 113 -44 21 -54 22 -395 23 -214 1 -368 6 -395 13 -25 6 -81 11 -125 11 -70 0 -87 -4 -133 -30 -49 -27 -58 -28 -104 -20 -28 6 -112 10 -187 10 -175 0 -292 13 -362 39 -66 25 -141 87 -159 131 -15 36 -40 40 -40 6 0 -68 78 -161 170 -205 52 -25 64 -26 215 -26 88 0 206 4 263 8 56 4 102 4 102 0 0 -4 -22 -20 -48 -34 -26 -15 -124 -87 -217 -160 -94 -74 -215 -168 -270 -209 -55 -41 -112 -86 -127 -99 -36 -31 -37 -68 -3 -77 13 -3 29 -12 36 -20 10 -12 4 -14 -35 -14 -102 0 -340 -76 -496 -158 -191 -101 -408 -278 -533 -435 -77 -96 -177 -239 -177 -252 0 -5 -6 -16 -14 -24 -19 -22 -102 -218 -132 -311 -38 -123 -53 -197 -65 -340 -53 -608 311 -1259 916 -1639 125 -79 139 -87 205 -118 169 -81 251 -109 455 -159 33 -8 76 -19 96 -24 20 -6 50 -10 67 -10 17 0 43 -5 59 -11 26 -11 21 -13 -62 -24 -217 -31 -336 -37 -490 -25 -169 13 -322 36 -395 60 -79 26 -146 44 -154 42 -5 -2 -16 3 -25 11 -9 7 -29 19 -46 26 -70 31 -195 99 -216 117 -8 8 -21 14 -27 14 -7 0 -12 3 -12 8 0 4 -12 13 -27 20 -39 17 -50 -1 -16 -26 15 -12 35 -28 43 -35 8 -7 30 -19 48 -26 17 -8 32 -17 32 -21 0 -4 8 -10 18 -14 9 -3 24 -10 32 -15 8 -6 36 -19 62 -31 26 -11 50 -24 53 -30 3 -5 17 -10 30 -10 13 0 26 -4 29 -9 3 -5 22 -12 42 -16 20 -3 44 -10 53 -15 88 -49 369 -89 635 -90 171 0 218 6 489 60 21 4 117 5 213 2 215 -6 316 3 614 59 464 85 948 329 1273 638 38 36 72 67 77 69 14 5 214 243 266 317 197 277 295 520 358 885 56 329 61 575 16 830 -48 268 -68 340 -143 500 -31 67 -148 230 -165 230 -4 0 -20 13 -37 28 -47 44 -150 121 -275 207 -157 108 -244 172 -384 284 -325 263 -332 266 -641 281 -237 12 -411 33 -456 56 -14 7 -35 11 -46 8 -12 -3 -79 4 -150 15 -71 12 -133 20 -139 20 -5 -1 -63 -8 -129 -15z m230 -514 c76 -34 131 -48 280 -75 242 -43 249 -44 321 -79 57 -27 86 -51 161 -132 50 -54 89 -102 86 -108 -9 -14 -252 1 -325 19 -35 9 -106 30 -158 47 -131 42 -295 51 -397 20 -112 -35 -187 -93 -195 -155 -3 -25 -3 -25 -38 -8 -68 33 -249 81 -308 81 -49 0 -112 11 -112 19 0 4 15 12 34 19 18 7 71 41 117 75 96 72 117 85 214 127 125 54 228 123 240 159 7 22 13 21 80 -9z m-635 -415 c101 -17 163 -30 210 -44 19 -5 46 -13 60 -16 45 -12 99 -34 180 -75 438 -222 678 -674 606 -1145 -69 -450 -389 -882 -754 -1015 -436 -159 -902 65 -1028 495 -42 140 -18 390 55 579 86 223 193 342 379 422 81 34 94 37 192 37 97 1 168 -10 230 -35 25 -10 33 -14 104 -52 85 -46 174 -165 223 -301 32 -88 22 -299 -17 -376 -48 -94 -70 -125 -123 -177 -107 -102 -257 -150 -368 -118 -152 45 -234 157 -234 321 0 103 53 213 121 256 78 48 237 14 264 -55 5 -13 14 -27 19 -31 6 -3 11 -17 11 -31 0 -13 5 -24 10 -24 29 0 2 97 -39 140 -135 140 -404 49 -470 -158 -41 -127 -12 -239 89 -340 47 -48 86 -71 183 -111 59 -23 253 -9 283 22 4 4 14 7 21 7 54 0 253 199 253 252 0 8 4 18 8 23 4 6 13 26 19 45 46 142 41 306 -11 410 -9 18 -16 37 -16 42 0 20 -87 136 -134 180 -51 47 -160 108 -231 128 -22 7 -54 16 -71 21 -43 13 -204 11 -261 -2 -727 -174 -873 -1058 -248 -1504 65 -47 174 -102 228 -115 18 -5 59 -16 92 -26 96 -28 352 -25 469 5 415 108 726 407 831 801 136 505 -77 1081 -509 1372 -17 12 1 20 21 10 40 -22 118 -43 243 -66 201 -37 337 -86 491 -177 185 -110 266 -147 398 -180 149 -38 340 -40 433 -4 23 9 23 9 42 -165 20 -179 20 -268 1 -434 -49 -416 -192 -823 -397 -1131 -284 -426 -708 -768 -1168 -944 -47 -18 -94 -37 -105 -41 -36 -15 -138 -48 -246 -79 -114 -33 -166 -37 -251 -20 -170 33 -247 50 -278 59 -14 4 -45 13 -70 20 -25 7 -76 24 -115 37 -38 14 -79 28 -90 31 -26 7 -239 117 -293 150 -154 96 -330 245 -448 380 -295 336 -437 814 -379 1272 68 541 304 962 688 1228 183 127 360 198 602 242 32 6 61 13 64 15 9 10 150 4 231 -10z m2414 -424 c30 -33 -24 -98 -98 -117 -23 -5 -26 -3 -26 19 0 85 79 148 124 98z '
    'M5476 2858 c-4 -23 -15 -39 -36 -51 -28 -17 -40 -50 -22 -60 15 -10 50 13 71 46 19 31 20 38 7 67 -13 33 -13 33 -20 -2z '
    'M3820 1185 c0 -16 25 -55 36 -55 23 0 25 19 4 40 -18 18 -40 27 -40 15z'
)

# ── CSS (αντιγράφεται αυτούσιο από το πρότυπο) ────────────────────────────
CSS = """
        /* ── Reset & Base ── */
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --nav-bg:           #1a1728;
            --nav-link:         #c9bfff;
            --nav-hover:        #ffd6b0;
            --diamond-bg:       rgba(180, 130, 160, 0.85);
            --dropdown-bg:      #252235;
            --dropdown-link:    #cdc6f0;
            --dropdown-hover-bg:#3d3660;
            --dropdown-hover-fg:#f0d6ff;
            --mega-bg:          #1e1b2e;
            --mega-title:       #e08aaa;
            --mobile-bg:        #2a2545;
            --accent:           #7c6fc4;
            --page-bg:          #13111f;
            --page-text:        #d4cef5;
            --hero-sub:         #9b92cc;
            --hero-h2:          #e0d8ff;
            --font:             system-ui, 'Segoe UI', Ubuntu, sans-serif;
        }

        html { scroll-behavior: smooth; }

        body {
            background: var(--page-bg);
            color: var(--page-text);
            font-family: var(--font);
            line-height: 1.6;
        }

        a { text-decoration: none; color: inherit; }
        ul { list-style: none; }

        .demo {
            background: var(--nav-bg);
            background-image: linear-gradient(135deg, #110f1c 0%, #1a1728 60%, #221e36 100%);
        }

        .nav-container { max-width: 1200px; margin: 0 auto; padding: 0 20px; }

        .navbar {
            display: flex; align-items: center; justify-content: flex-start;
            padding: 10px 0 0; position: relative;
        }

        .navbar-toggle {
            display: none;
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.5);
            border-radius: 4px; padding: 8px 12px; cursor: pointer;
            color: #fff; font-size: 20px; line-height: 1; margin-bottom: 10px;
            transition: background 0.2s;
        }
        .navbar-toggle:hover { background: rgba(255,255,255,0.28); }

        .nav-menu { display: flex; gap: 4px; padding-bottom: 0; }

        .nav-menu > li > a {
            display: inline-block; color: var(--nav-link); font-size: 15px;
            font-weight: 700; text-transform: uppercase; letter-spacing: .04em;
            padding: 8px 16px; border-radius: 5px 5px 0 0; position: relative;
            overflow: hidden; z-index: 1; transition: color .3s; white-space: nowrap;
        }

        .nav-menu > li.dropdown > a::after {
            content: "▾"; margin-left: 6px; font-size: 13px;
            display: inline-block; transition: transform .3s;
        }
        .nav-menu > li.dropdown.on > a::after { transform: rotate(180deg); }

        .nav-menu > li > a > .nav-label::before {
            content: ''; background-color: var(--diamond-bg);
            width: 110px; height: 110px; position: absolute;
            left: 50%; top: 0;
            transform: translateX(-50%) rotate(45deg) scale(0);
            z-index: -1; transition: transform 0.3s; border-radius: 4px;
        }
        .nav-menu > li > a:hover,
        .nav-menu > li.on > a,
        .nav-menu > li.active > a { color: var(--nav-hover); text-shadow: 0 0 4px rgba(0,0,0,.5); }
        .nav-menu > li > a:hover .nav-label::before,
        .nav-menu > li.on > a .nav-label::before,
        .nav-menu > li.active > a .nav-label::before {
            transform: translateX(-50%) rotate(45deg) scale(1.9);
        }

        .dropdown-menu {
            position: absolute; top: 100%; left: 0; min-width: 220px;
            background: transparent; display: block;
            opacity: 0; visibility: hidden; pointer-events: none;
            transition: opacity .25s, visibility .25s; z-index: 9999;
        }
        .nav-menu > li.dropdown { position: relative; }
        .nav-menu > li.dropdown.on > .dropdown-menu {
            opacity: 1; visibility: visible; pointer-events: auto;
        }

        .dropdown-menu > li > a {
            display: block; padding: 10px 20px; color: var(--dropdown-link);
            background: var(--dropdown-bg); font-size: 14px; white-space: nowrap;
            opacity: 0; transform: rotateY(180deg);
            transition: opacity .3s, transform .3s, color .2s, background .2s, padding-left .2s;
        }
        .nav-menu > li.dropdown.on .dropdown-menu > li > a { opacity: 1; transform: rotateY(0); }
        .dropdown-menu > li > a:hover {
            color: var(--dropdown-hover-fg) !important;
            background: var(--dropdown-hover-bg) !important;
            font-weight: 600; box-shadow: 0 0 5px rgba(0,0,0,.35); padding-left: 26px;
        }

        .dropdown-menu li { position: relative; }
        .dropdown-menu li.dropdown > a::after { content: " ▸"; float: right; font-size: 12px; }
        .dropdown-menu .dropdown-menu { top: -10px; left: 100%; }
        .dropdown-menu li.dropdown:hover > .dropdown-menu,
        .dropdown-menu li.dropdown.on > .dropdown-menu {
            opacity: 1; visibility: visible; pointer-events: auto;
        }
        .dropdown-menu li.dropdown:hover > .dropdown-menu > li > a,
        .dropdown-menu li.dropdown.on > .dropdown-menu > li > a {
            opacity: 1; transform: rotateY(0);
        }

        .megamenu-content {
            width: 720px; left: -180px !important; background: var(--mega-bg);
            padding: 20px; border-top: 3px solid #5a4f8a;
            border-radius: 0 0 8px 8px; box-shadow: 0 8px 32px rgba(0,0,0,.55);
        }
        .megamenu-content > li { display: block; }
        .megamenu-row { display: flex; gap: 16px; flex-wrap: wrap; }
        .col-menu { flex: 1 1 22%; }
        .col-menu .title {
            color: var(--mega-title); font-size: 14px; font-weight: 700;
            padding-bottom: 8px; border-bottom: 1px solid var(--mega-title); margin-bottom: 10px;
        }
        .menu-col li a {
            display: block; padding: 5px 0 5px 8px; color: var(--hero-sub);
            font-size: 13px; border: 1px solid rgba(255,255,255,.07);
            margin-bottom: 4px; border-radius: 3px;
            opacity: 0; transform: rotateY(180deg);
            transition: opacity .3s, transform .3s, color .2s, padding-left .2s, background .2s;
        }
        .nav-menu > li.dropdown.on .megamenu-content .menu-col li a {
            opacity: 1; transform: rotateY(0);
        }
        .menu-col li a:hover {
            color: var(--dropdown-hover-fg) !important;
            background: var(--dropdown-hover-bg) !important;
            padding-left: 14px; box-shadow: 0 0 4px rgba(0,0,0,.2);
        }

        .modal-overlay {
            display: none; position: fixed; inset: 0; background: rgba(0,0,0,.55);
            z-index: 10000; align-items: center; justify-content: center;
            backdrop-filter: blur(3px);
        }
        .modal-overlay.open { display: flex; }
        .modal-box {
            background: #1e1b2e; border-radius: 12px; max-width: 680px; width: 92%;
            max-height: 85vh; overflow-y: auto; box-shadow: 0 8px 48px rgba(0,0,0,.75);
            animation: modalIn .25s ease;
        }
        @keyframes modalIn {
            from { opacity: 0; transform: translateY(-20px) scale(.97); }
            to   { opacity: 1; transform: translateY(0) scale(1); }
        }
        .modal-header {
            background: linear-gradient(135deg, #2e2850, #4a3d7a); color: #ffa0a0;
            padding: 18px 24px; border-radius: 12px 12px 0 0;
            display: flex; align-items: center; justify-content: space-between;
        }
        .modal-title { font-weight: 700; font-size: 18px; }
        .modal-close {
            background: none; border: none; color: #fff; font-size: 24px;
            cursor: pointer; line-height: 1; opacity: .8; transition: opacity .2s;
        }
        .modal-close:hover { opacity: 1; }
        .modal-body { padding: 24px; color: #cdc6f0; line-height: 1.75; }
        .modal-body p { margin-bottom: 14px; }
        .modal-body a { color: #b39dff; text-decoration: underline; }
        .modal-body hr { margin: 16px 0; border: none; border-top: 1px solid #2e2a4a; }
        .modal-body li { margin-left: 20px; margin-bottom: 6px; list-style: disc; }
        .modal-footer { padding: 16px 24px; border-top: 1px solid #2e2a4a; text-align: right; }
        .btn-close {
            background: #5a4f8a; color: #fff; border: none; padding: 8px 22px;
            border-radius: 6px; font-size: 14px; cursor: pointer; transition: background .2s;
        }
        .btn-close:hover { background: #4a4080; }

        .content-section {
            padding: 70px 20px 80px; text-align: center;
            max-width: 700px; margin: 0 auto;
        }
        .svg-icon {
            filter: drop-shadow(0 4px 14px rgba(160,140,220,.35));
            margin-bottom: 28px; transition: filter .3s;
        }
        .svg-icon:hover { filter: drop-shadow(0 6px 22px rgba(180,150,255,.6)); }
        .content-section h2 {
            font-size: 2.4rem; font-weight: 700; color: var(--hero-h2);
            letter-spacing: .02em; margin-bottom: 16px;
        }
        .content-section p { font-size: 1.1rem; color: var(--hero-sub); }
        .hero-divider {
            display: block; width: 60px; height: 3px;
            background: linear-gradient(90deg, #7c6fc4, #e08aaa);
            border-radius: 2px; margin: 18px auto 22px;
        }

        @media (max-width: 990px) {
            .navbar { flex-direction: column; align-items: flex-start; padding: 8px 0; }
            .navbar-toggle { display: block; }
            .nav-menu {
                display: none; flex-direction: column; width: 100%;
                background: var(--mobile-bg); border-top: 1px solid rgba(255,255,255,.2);
                gap: 0; max-height: 80vh; overflow-y: auto;
            }
            .nav-menu.open { display: flex; }
            .nav-menu > li > a {
                color: #fff; font-size: 15px; padding: 14px 16px; border-radius: 0;
                border-bottom: 1px solid rgba(255,255,255,.1); width: 100%;
            }
            .nav-menu > li > a > .nav-label::before { display: none; }
            .nav-menu > li > a:hover, .nav-menu > li.on > a { text-shadow: none; }
            .dropdown-menu {
                position: static; visibility: visible; pointer-events: auto;
                background: transparent; opacity: 1; max-height: 0; overflow: hidden;
                transition: max-height .35s ease; box-shadow: none;
            }
            .nav-menu > li.dropdown.on > .dropdown-menu { max-height: 2000px; }
            .dropdown-menu > li > a {
                color: #fff; background: rgba(255,255,255,.1); border: none;
                padding: 11px 16px 11px 32px; opacity: 1; transform: none;
            }
            .dropdown-menu > li > a:hover {
                background: rgba(255,255,255,.22) !important; color: #fff !important;
                padding-left: 38px; box-shadow: none;
            }
            .dropdown-menu .dropdown-menu { position: static; top: auto; left: auto; max-height: 0; }
            .dropdown-menu li.dropdown.on > .dropdown-menu { max-height: 2000px; }
            .dropdown-menu li.dropdown.on > .dropdown-menu > li > a { opacity: 1; transform: none; }
            .dropdown-menu li.dropdown > a::after { content: " ▾"; }
            .dropdown-menu li.dropdown.on > a::after { content: " ▴"; }
            .megamenu-content {
                width: 100%; left: 0 !important; padding: 12px; border-top: none;
                border-radius: 0; background: rgba(0,0,0,.45); box-shadow: none;
            }
            .megamenu-row { flex-direction: column; gap: 8px; }
            .col-menu { background: rgba(255,255,255,.12); border-radius: 6px; padding: 12px; }
            .col-menu .title { color: #fff; border-color: rgba(255,255,255,.35); }
            .menu-col li a { color: rgba(255,255,255,.9); border: none; opacity: 1; transform: none; }
            .menu-col li a:hover { background: rgba(255,255,255,.15) !important; color: #fff !important; }
            .nav-menu > li.dropdown.on .megamenu-content .menu-col li a { opacity: 1; transform: none; }
            .content-section h2 { font-size: 1.8rem; }
        }
"""

# ── JS (αντιγράφεται αυτούσιο από το πρότυπο) ─────────────────────────────
JS = """
    (function () {
        'use strict';

        var overlay   = document.getElementById('aboutModal');
        var aboutLink = document.getElementById('aboutLink');
        var closeBtn  = document.getElementById('modalClose');
        var closeBtnF = document.getElementById('modalCloseBtn');

        function openModal(e) { e.preventDefault(); overlay.classList.add('open'); }
        function closeModal()  { overlay.classList.remove('open'); }

        aboutLink.addEventListener('click', openModal);
        closeBtn .addEventListener('click', closeModal);
        closeBtnF.addEventListener('click', closeModal);
        overlay  .addEventListener('click', function (e) {
            if (e.target === overlay) closeModal();
        });
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') closeModal();
        });

        var toggle  = document.getElementById('navToggle');
        var navMenu = document.getElementById('navMenu');

        toggle.addEventListener('click', function () {
            var open = navMenu.classList.toggle('open');
            toggle.setAttribute('aria-expanded', String(open));
        });

        var isMobile = function () { return window.innerWidth <= 990; };

        /* ── Viewport overflow detection ── */
        function fixOverflow(menu) {
            if (!menu) return;
            // Reset πρώτα
            menu.style.left = '';
            menu.style.right = '';

            var rect = menu.getBoundingClientRect();
            var vw   = window.innerWidth || document.documentElement.clientWidth;

            if (rect.right > vw) {
                // Ξεπερνά δεξιά → ανοίγει προς τα αριστερά
                menu.style.left  = 'auto';
                menu.style.right = '0';
            }
            if (rect.left < 0) {
                // Ξεπερνά αριστερά → επαναφορά στα δεξιά
                menu.style.left  = '0';
                menu.style.right = 'auto';
            }
        }

        document.querySelectorAll('.nav-menu > li.dropdown').forEach(function (li) {
            li.addEventListener('mouseenter', function () {
                if (!isMobile()) {
                    li.classList.add('on');
                    fixOverflow(li.querySelector(':scope > .dropdown-menu'));
                }
            });
            li.addEventListener('mouseleave', function () { if (!isMobile()) li.classList.remove('on'); });
        });

        /* Sub-dropdown overflow: ανοίγουν δεξιά by default, αν δεν χωράνε → αριστερά */
        document.querySelectorAll('.dropdown-menu li.dropdown').forEach(function (li) {
            li.addEventListener('mouseenter', function () {
                if (isMobile()) return;
                var sub = li.querySelector(':scope > .dropdown-menu');
                if (!sub) return;
                // Reset
                sub.style.left  = '';
                sub.style.right = '';
                sub.style.top   = '';
                var rect = sub.getBoundingClientRect();
                var vw   = window.innerWidth || document.documentElement.clientWidth;
                if (rect.right > vw) {
                    sub.style.left  = 'auto';
                    sub.style.right = '100%';
                }
            });
        });

        document.querySelectorAll('.nav-menu > li.dropdown > a').forEach(function (a) {
            a.addEventListener('click', function (e) {
                if (!isMobile()) return;
                e.preventDefault();
                var li = a.parentElement;
                var wasOpen = li.classList.contains('on');
                document.querySelectorAll('.nav-menu > li.dropdown').forEach(function (x) { x.classList.remove('on'); });
                if (!wasOpen) li.classList.add('on');
            });
        });

        document.querySelectorAll('.dropdown-menu li.dropdown > a').forEach(function (a) {
            a.addEventListener('click', function (e) {
                if (!isMobile()) return;
                e.preventDefault();
                e.stopPropagation();
                var li = a.parentElement;
                var wasOpen = li.classList.contains('on');
                li.parentElement.querySelectorAll(':scope > li.dropdown').forEach(function (x) { x.classList.remove('on'); });
                if (!wasOpen) li.classList.add('on');
            });
        });

        window.addEventListener('resize', function () {
            if (!isMobile()) {
                navMenu.classList.remove('open');
                document.querySelectorAll('.nav-menu li.dropdown').forEach(function (li) { li.classList.remove('on'); });
            }
        });
    })();
"""


# ══════════════════════════════════════════════════════════════════════════
#  Βοηθητικές συναρτήσεις
# ══════════════════════════════════════════════════════════════════════════

def md_inline(text: str) -> str:
    """Μετατρέπει [κείμενο](url) και --- σε HTML inline."""
    # --- → <hr>  (μόνο αν η γραμμή είναι ακριβώς "---")
    if text.strip() == '---':
        return '<hr>'
    # [text](url)
    def repl(m):
        txt = escape(m.group(1))
        url = m.group(2)
        return f'<a href="{url}" target="_blank">{txt}</a>'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', repl, escape(text))


def parse_link(line: str):
    """Επιστρέφει (κείμενο, url, περιγραφή_ή_None) ή None αν δεν είναι link."""
    m = re.match(r'^\[([^\]]+)\]\((.+?)\)(?:\s*—\s*(.+))?\s*$', line.strip())
    if m:
        return m.group(1), m.group(2), m.group(3)
    return None


def indent(html: str, n: int) -> str:
    pad = '    ' * n
    return '\n'.join(pad + l if l.strip() else l for l in html.splitlines())


# ══════════════════════════════════════════════════════════════════════════
#  Parser του content.txt
# ══════════════════════════════════════════════════════════════════════════

class Parser:
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.pos   = 0

    def peek(self):
        while self.pos < len(self.lines) and self.lines[self.pos].strip() == '':
            self.pos += 1
        return self.lines[self.pos] if self.pos < len(self.lines) else None

    def consume(self):
        line = self.lines[self.pos]
        self.pos += 1
        return line

    def skip_blank(self):
        while self.pos < len(self.lines) and self.lines[self.pos].strip() == '':
            self.pos += 1

    # ── <about> block ──────────────────────────────────────────────────
    def parse_about(self):
        """Επιστρέφει (btn_label, modal_title, modal_body_html)."""
        line = self.consume().strip()
        m = re.match(r'<about>\{([^}]+)\}\{([^}]+)\}</about>', line)
        btn_label   = m.group(1)
        modal_title = m.group(2)

        # Συλλέγουμε γραμμές μέχρι την επόμενη # ή EOF
        body_lines = []
        while self.pos < len(self.lines):
            raw = self.lines[self.pos]
            stripped = raw.strip()
            if re.match(r'^#{1,4}\s', stripped) or re.match(r'^<about>', stripped):
                break
            body_lines.append(raw)
            self.pos += 1

        modal_html = self._body_to_html(body_lines)
        return btn_label, modal_title, modal_html

    def _body_to_html(self, lines) -> str:
        """Μετατρέπει παραγράφους/links/--- σε HTML για το modal body."""
        html_parts = []
        para_lines = []

        def flush_para():
            if para_lines:
                content = ' '.join(md_inline(l) for l in para_lines if l.strip())
                if content.strip():
                    html_parts.append(f'<p>{content}</p>')
                para_lines.clear()

        # Μαζεύουμε links στο τέλος ως <ul>
        trailing_links = []
        # Βρίσκουμε αν υπάρχει ένα block links στο τέλος
        # (γραμμές της μορφής [text](url) χωρίς κείμενο ανάμεσα)
        last_text_idx = -1
        for i, l in enumerate(lines):
            if l.strip() and not re.match(r'^\[([^\]]+)\]\(', l.strip()):
                last_text_idx = i

        link_list_start = last_text_idx + 1

        main_lines  = lines[:link_list_start]
        link_lines  = [l for l in lines[link_list_start:] if l.strip()]

        for raw in main_lines:
            stripped = raw.strip()
            if not stripped:
                flush_para()
            elif stripped == '---':
                flush_para()
                html_parts.append('<hr>')
            else:
                para_lines.append(stripped)
        flush_para()

        if link_lines:
            items = []
            for l in link_lines:
                lnk = parse_link(l)
                if lnk:
                    txt, url, desc = lnk
                    if desc:
                        items.append(
                            f'<li><a href="{url}" target="_blank">{escape(txt)}</a>'
                            f' — {escape(desc)}</li>'
                        )
                    else:
                        items.append(f'<li><a href="{url}" target="_blank">{escape(txt)}</a></li>')
            if items:
                html_parts.append('<ul>\n' + '\n'.join('    ' + i for i in items) + '\n</ul>')

        return '\n'.join(html_parts)

    # ── listmenu ────────────────────────────────────────────────────────
    def parse_listmenu(self, title: str) -> str:
        """Επιστρέφει το <li class="dropdown">…</li> HTML."""
        items_html = self._parse_list_items(base_level=2)
        esc_title = escape(title)
        return (
            f'                    <!-- {esc_title} -->\n'
            f'                    <li class="dropdown">\n'
            f'                        <a href="#" class="dropdown-toggle">\n'
            f'                            <span class="nav-label">{esc_title}</span>\n'
            f'                        </a>\n'
            f'                        <ul class="dropdown-menu">\n'
            f'{items_html}'
            f'                        </ul>\n'
            f'                    </li>\n'
        )

    def _parse_list_items(self, base_level: int) -> str:
        """
        Διαβάζει items μέχρι να συναντήσει # επίπεδο 1 ή EOF.
        base_level: το επίπεδο ## που θεωρείται sub-dropdown.
        Επιστρέφει HTML γραμμές για <li> items.
        """
        html = ''
        indent_str = '    ' * (base_level + 1)  # 12 spaces για level 2

        while self.pos < len(self.lines):
            raw = self.lines[self.pos]
            stripped = raw.strip()

            # Σταματάμε σε επίπεδο-1 heading ή EOF
            if re.match(r'^# ', stripped):
                break

            # Κενή γραμμή → skip
            if not stripped:
                self.pos += 1
                continue

            # Sub-dropdown heading (##, ###, ####)
            hm = re.match(r'^(#{2,4})\s+(.+)$', stripped)
            if hm:
                level = len(hm.group(1))
                sub_title = hm.group(2)
                self.pos += 1
                sub_html = self._parse_sublist_items(level)
                esc_sub = escape(sub_title)
                html += (
                    f'{indent_str}<li class="dropdown">\n'
                    f'{indent_str}    <a href="#">{esc_sub}</a>\n'
                    f'{indent_str}    <ul class="dropdown-menu">\n'
                    f'{sub_html}'
                    f'{indent_str}    </ul>\n'
                    f'{indent_str}</li>\n'
                )
                continue

            # Απλός σύνδεσμος
            lnk = parse_link(stripped)
            if lnk:
                txt, url, _ = lnk
                self.pos += 1
                html += f'{indent_str}<li><a href="{url}">{escape(txt)}</a></li>\n'
                continue

            # Άγνωστη γραμμή → skip
            self.pos += 1

        return html

    def _parse_sublist_items(self, parent_level: int) -> str:
        """
        Διαβάζει items για ένα sub-dropdown.
        Σταματά όταν συναντήσει:
          - heading ίδιου ή ανώτερου επιπέδου
          - # επίπεδο 1
          - γραμμή '---'  →  βγαίνει από το τρέχον επίπεδο (χωρίς να καταναλώσει τη γραμμή)
        """
        html = ''
        indent_str = '    ' * (parent_level + 2)

        while self.pos < len(self.lines):
            raw = self.lines[self.pos]
            stripped = raw.strip()

            if not stripped:
                self.pos += 1
                continue

            # --- → βγαίνουμε από το τρέχον sub-dropdown
            # Καταναλώνουμε τη γραμμή ώστε να μην την ξαναδεί κανείς
            if stripped == '---':
                self.pos += 1
                break

            # Σταματάμε σε heading ίδιου ή χαμηλότερου αριθμού #
            hm = re.match(r'^(#{1,4})\s+', stripped)
            if hm:
                level = len(hm.group(1))
                if level <= parent_level:
                    break
                # Βαθύτερο sub-dropdown
                sub_title = stripped[level:].strip()
                self.pos += 1
                sub_html = self._parse_sublist_items(level)
                esc_sub = escape(sub_title)
                html += (
                    f'{indent_str}<li class="dropdown">\n'
                    f'{indent_str}    <a href="#">{esc_sub}</a>\n'
                    f'{indent_str}    <ul class="dropdown-menu">\n'
                    f'{sub_html}'
                    f'{indent_str}    </ul>\n'
                    f'{indent_str}</li>\n'
                )
                continue

            lnk = parse_link(stripped)
            if lnk:
                txt, url, _ = lnk
                self.pos += 1
                html += f'{indent_str}<li><a href="{url}">{escape(txt)}</a></li>\n'
                continue

            self.pos += 1

        return html

    # ── colmenu (megamenu) ──────────────────────────────────────────────
    def parse_colmenu(self, title: str) -> str:
        cols_html = ''
        while self.pos < len(self.lines):
            raw = self.lines[self.pos]
            stripped = raw.strip()

            if re.match(r'^# ', stripped):
                break
            if not stripped:
                self.pos += 1
                continue

            hm = re.match(r'^## (.+)$', stripped)
            if hm:
                col_title = hm.group(1)
                self.pos += 1
                items_html = self._parse_col_items()
                esc_col = escape(col_title)
                cols_html += (
                    f'                                    <div class="col-menu">\n'
                    f'                                        <h6 class="title">{esc_col}</h6>\n'
                    f'                                        <ul class="menu-col">\n'
                    f'{items_html}'
                    f'                                        </ul>\n'
                    f'                                    </div>\n'
                )
                continue
            self.pos += 1

        esc_title = escape(title)
        return (
            f'                    <!-- {esc_title} (Megamenu) -->\n'
            f'                    <li class="dropdown megamenu-fw">\n'
            f'                        <a href="#" class="dropdown-toggle">\n'
            f'                            <span class="nav-label">{esc_title}</span>\n'
            f'                        </a>\n'
            f'                        <ul class="dropdown-menu megamenu-content">\n'
            f'                            <li>\n'
            f'                                <div class="megamenu-row">\n'
            f'{cols_html}'
            f'                                </div>\n'
            f'                            </li>\n'
            f'                        </ul>\n'
            f'                    </li>\n'
        )

    def _parse_col_items(self) -> str:
        html = ''
        while self.pos < len(self.lines):
            raw = self.lines[self.pos]
            stripped = raw.strip()
            if re.match(r'^#{1,2} ', stripped):
                break
            if not stripped:
                self.pos += 1
                continue
            lnk = parse_link(stripped)
            if lnk:
                txt, url, _ = lnk
                self.pos += 1
                html += f'                                            <li><a href="{url}">{escape(txt)}</a></li>\n'
                continue
            self.pos += 1
        return html

    # ── hero ────────────────────────────────────────────────────────────
    def parse_hero(self) -> tuple:
        """Επιστρέφει (h2_text, [subtitle_lines])."""
        h2 = None
        subs = []
        while self.pos < len(self.lines):
            raw = self.lines[self.pos]
            stripped = raw.strip()
            if re.match(r'^# ', stripped):
                break
            if stripped:
                if h2 is None:
                    h2 = stripped
                else:
                    subs.append(stripped)
            self.pos += 1
        return h2, subs

    # ── Κεντρικός parser ────────────────────────────────────────────────
    def parse(self):
        result = {
            'btn_label':   'Περί...',
            'modal_title': 'Περί τίνος πρόκειται;',
            'modal_body':  '',
            'nav_items':   [],   # list of ('about'|'listmenu'|'colmenu'), title, html
            'hero_h2':     '',
            'hero_subs':   [],
        }

        while self.pos < len(self.lines):
            self.skip_blank()
            if self.pos >= len(self.lines):
                break
            raw = self.lines[self.pos]
            stripped = raw.strip()

            # <about>
            if stripped.startswith('<about>'):
                btn, title, body = self.parse_about()
                result['btn_label']   = btn
                result['modal_title'] = title
                result['modal_body']  = body
                result['nav_items'].append(('about', btn, ''))
                continue

            # # Τίτλος <listmenu|colmenu|hero>
            m = re.match(r'^# (.+?)\s+<(listmenu|colmenu|hero)>\s*$', stripped)
            if m:
                title   = m.group(1)
                kind    = m.group(2)
                self.pos += 1
                if kind == 'listmenu':
                    html = self.parse_listmenu(title)
                    result['nav_items'].append(('listmenu', title, html))
                elif kind == 'colmenu':
                    html = self.parse_colmenu(title)
                    result['nav_items'].append(('colmenu', title, html))
                elif kind == 'hero':
                    h2, subs = self.parse_hero()
                    result['hero_h2']   = h2 or ''
                    result['hero_subs'] = subs
                continue

            self.pos += 1

        return result


# ══════════════════════════════════════════════════════════════════════════
#  Generator HTML
# ══════════════════════════════════════════════════════════════════════════

def generate_html(data: dict) -> str:
    # ── Nav items ──
    nav_html = ''
    for kind, title, html in data['nav_items']:
        if kind == 'about':
            nav_html += (
                f'                    <!-- {escape(title)} -->\n'
                f'                    <li>\n'
                f'                        <a href="#" id="aboutLink">\n'
                f'                            <span class="nav-label">{escape(title)}</span>\n'
                f'                        </a>\n'
                f'                    </li>\n'
            )
        else:
            nav_html += html

    # ── Hero subtitles ──
    subs_html = '\n'.join(
        f'            <p>{escape(s)}</p>' for s in data['hero_subs']
    )

    # ── Full HTML ──
    return f"""<!DOCTYPE html>
<html lang="el">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ἐπιψαύσεις</title>
    <style>{CSS}
    </style>
</head>

<body>

    <!-- ══ Modal ══ -->
    <div class="modal-overlay" id="aboutModal" role="dialog" aria-modal="true" aria-labelledby="aboutModalLabel">
        <div class="modal-box">
            <div class="modal-header">
                <span class="modal-title" id="aboutModalLabel">{escape(data['modal_title'])}</span>
                <button class="modal-close" id="modalClose" aria-label="Κλείσιμο">&times;</button>
            </div>
            <div class="modal-body">
{data['modal_body']}
            </div>
            <div class="modal-footer">
                <button class="btn-close" id="modalCloseBtn">Κλείσιμο</button>
            </div>
        </div>
    </div>

    <!-- ══ Nav ══ -->
    <div class="demo">
        <div class="nav-container">
            <nav class="navbar" role="navigation">
                <button class="navbar-toggle" id="navToggle" aria-label="Μενού" aria-expanded="false">
                    &#9776;
                </button>
                <ul class="nav-menu" id="navMenu">
{nav_html}                </ul>
            </nav>
        </div>
    </div>

    <!-- ══ Hero ══ -->
    <main>
        <div class="content-section">
            <div class="svg-icon">
                <svg width="240px" height="130px" viewBox="0 0 1200 654" role="img" xmlns="http://www.w3.org/2000/svg">
                    <title>ἐπιψαύσεις icon</title>
                        <g transform="translate(0,654) scale(0.1,-0.1)" fill="#a89fd4">
                       <path d="{SVG_PATH}" />
    </g>
                </svg>
            </div>
            <h2>{escape(data['hero_h2'])}</h2>
            <span class="hero-divider"></span>
{subs_html}
        </div>
    </main>

    <script>
{JS}
    </script>
</body>
</html>
"""


# ══════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════

def main():
    script_dir = Path(__file__).parent
    txt_path   = script_dir / 'content.txt'
    html_path  = script_dir / 'index.html'

    if not txt_path.exists():
        print(f'Σφάλμα: δεν βρέθηκε το {txt_path}', file=sys.stderr)
        sys.exit(1)

    text   = txt_path.read_text(encoding='utf-8')
    parser = Parser(text)
    data   = parser.parse()
    html   = generate_html(data)

    html_path.write_text(html, encoding='utf-8')
    print(f'✓  Δημιουργήθηκε: {html_path}')


if __name__ == '__main__':
    main()