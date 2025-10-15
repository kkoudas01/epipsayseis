# Εκτελώ στον cmd το παρακάτω:
# python wljsAdd.py
# # Λέξη-κλειδί για αναγνώριση αρχείων HTML (π.χ., "(wljs)")

import os
import datetime
from bs4 import BeautifulSoup

# --- Ρυθμίσεις ---
PARAGRAPH_TEXT = """Υλοποίηση μέσω γλώσσας Wolfram στο <a href="https://jerryi.github.io/wljs-docs/" target="_blank" rel="noopener noreferrer">WLJS Notebook</a>."""
BASE_SIGNATURE_TEXT = "Κώστας Κούδας | &copy; "
INDEX_FILENAME = "index.html"
FILENAME_KEYWORD = "(wljsEDU)"

# --- Loader HTML Template ---
LOADER_HTML = """
<div id="loader" class="tower-overlay">
    <div class="tower">
        <div class="tower__group">
            <div class="tower__brick-layer tower__brick-layer--4">
                <div class="tower__brick tower__brick--0">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--90 tower__brick--red">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--180 tower__brick--orange">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--270 tower__brick--purple">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
            <div class="tower__brick-layer tower__brick-layer--3">
                <div class="tower__brick tower__brick--45 tower__brick--magenta">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--135">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--225 tower__brick--green">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--315 tower__brick--orange">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
            <div class="tower__brick-layer tower__brick-layer--2">
                <div class="tower__brick tower__brick--0 tower__brick--red">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--90 tower__brick--green">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--180 tower__brick--purple">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--270">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
            <div class="tower__brick-layer tower__brick-layer--1">
                <div class="tower__brick tower__brick--45 tower__brick--purple">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--135 tower__brick--magenta">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--225 tower__brick--red">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--315 tower__brick--green">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
            <div class="tower__brick-layer">
                <div class="tower__brick tower__brick--0 tower__brick--move14">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--90 tower__brick--red tower__brick--move13">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--180 tower__brick--orange tower__brick--move16">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--270 tower__brick--purple tower__brick--move15">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
            <div class="tower__brick-layer tower__brick-layer---1">
                <div class="tower__brick tower__brick--45 tower__brick--move10 tower__brick--magenta">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--135 tower__brick--move9">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--225 tower__brick--green tower__brick--move12">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--315 tower__brick--orange tower__brick--move11">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
            <div class="tower__brick-layer tower__brick-layer---2">
                <div class="tower__brick tower__brick--0 tower__brick--red tower__brick--move6">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--90 tower__brick--green tower__brick--move5">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--180 tower__brick--purple tower__brick--move8">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--270 tower__brick--move7">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
            <div class="tower__brick-layer tower__brick-layer---3">
                <div class="tower__brick tower__brick--45 tower__brick--purple tower__brick--move2">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--135 tower__brick--magenta tower__brick--move1">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--225 tower__brick--red tower__brick--move4">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
                <div class="tower__brick tower__brick--315 tower__brick--green tower__brick--move3">
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-side"></div>
                    <div class="tower__brick-stud"></div>
                    <div class="tower__brick-stud"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="message">
        <p class="message__line">Φορτώνει, μη φορτώνεις...</p>
    </div>
</div>
"""

# --- CSS Styles που θα προστεθούν στο <head> ---
CSS_STYLES = """
<style>
    /* CSS για τη βασική δομή της σελίδας */
    body {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
    }

    /* Loader specific styles */
    :root {
        --hue: 223;
        --bg: hsl(var(--hue),90%,90%);
        --fg: hsl(var(--hue),90%,10%);
        --primary: hsl(var(--hue),90%,55%);
        --red: hsl(3,90%,50%);
        --orange: hsl(33,90%,50%);
        --green: hsl(153,90%,30%);
        --purple: hsl(273,90%,50%);
        --magenta: hsl(303,90%,50%);
        --trans-dur: 0.3s;
        font-size: calc(16px + (20 - 16) * (100vw - 320px) / (1280 - 320));
    }
    .tower-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        background-color: var(--bg);
        z-index: 9999;
        overflow: hidden;
        transition: opacity 0.5s ease;
    }
    
    .message {
        height: 1.5em;
        position: relative;
        text-align: center;
        margin-top: 2em; /* Προσθήκη κενού κάτω από τον πύργο */
    }
    .message__line {
        animation: message-fade-in-out 5s linear;
        opacity: 0;
        position: absolute;
        inset: 0;
        text-align: center;
    }

    .message__line:first-child {
        animation-name: message-fade-in;
        animation-fill-mode: forwards;
    }

    .tower,
    .tower__brick,
    .tower__brick-layer,
    .tower__brick-side,
    .tower__brick-stud,
    .tower__group {
        transform-style: preserve-3d;
    }
    .tower {
        position: relative;
        perspective: 800px;
        width: 16em;
        height: 16em;
    }
    .tower__brick,
    .tower__brick-layer,
    .tower__brick-side,
    .tower__brick-stud,
    .tower__group {
        position: absolute;
    }
    .tower__brick,
    .tower__brick-side,
    .tower__group {
        animation-duration: 16s;
        animation-timing-function: linear;
        animation-iteration-count: infinite;
    }
    .tower__brick,
    .tower__brick-side {
        background-color: var(--primary);
    }
    .tower__brick {
        background-image: radial-gradient(100% 100% at center,hsla(0,0%,0%,0.3) 0.3em,hsla(0,0%,0%,0) 0.3em);
        background-size: 1em 1em;
        width: 2em;
        height: 1em;
    }
    .tower__brick-layer--4 { transform: translateZ(4.8em); }
    .tower__brick-layer--3 { transform: translateZ(3.6em); }
    .tower__brick-layer--2 { transform: translateZ(2.4em); }
    .tower__brick-layer--1 { transform: translateZ(1.2em); }
    .tower__brick-layer---1 { transform: translateZ(-1.2em); }
    .tower__brick-layer---2 { transform: translateZ(-2.4em); }
    .tower__brick-layer---3 { transform: translateZ(-3.6em); }
    .tower__brick-side {
        bottom: 100%;
        left: 0;
        width: 100%;
        height: 1.2em;
        transform: rotateX(90deg);
        transform-origin: 50% 100%;
    }
    .tower__brick-side:nth-child(2) {
        top: 0;
        bottom: auto;
        left: 100%;
        width: 1.2em;
        height: 100%;
        transform: rotateY(90deg);
        transform-origin: 0 50%;
    }
    .tower__brick-side:nth-child(3) {
        top: 100%;
        left: 0;
        width: 100%;
        height: 1.2em;
        transform: rotateX(-90deg);
        transform-origin: 50% 0;
    }
    .tower__brick-side:nth-child(4) {
        top: 0;
        right: 100%;
        bottom: auto;
        left: auto;
        width: 1.2em;
        height: 100%;
        transform: rotateY(-90deg);
        transform-origin: 100% 50%;
    }
    .tower__brick-side:nth-child(even),
    .tower__brick--90 .tower__brick-side:nth-child(odd),
    .tower__brick--135 .tower__brick-side:nth-child(odd),
    .tower__brick--270 .tower__brick-side:nth-child(odd),
    .tower__brick--315 .tower__brick-side:nth-child(odd) {
        animation-name: brick-side-1;
        filter: brightness(0.5);
    }
    .tower__brick-side:nth-child(odd),
    .tower__brick--90 .tower__brick-side:nth-child(even),
    .tower__brick--135 .tower__brick-side:nth-child(even),
    .tower__brick--270 .tower__brick-side:nth-child(even),
    .tower__brick--315 .tower__brick-side:nth-child(even) {
        animation-name: brick-side-2;
        filter: brightness(0.75);
    }
    .tower__brick-stud {
        background-color: inherit;
        border-radius: 50%;
        top: 0.2em;
        left: 0.2em;
        width: 0.6em;
        height: 0.6em;
        transform: translateZ(0.2em);
    }
    .tower__brick-stud:nth-child(6) { left: 1.2em; }
    .tower__brick--0 { transform: translate3d(-1.5em,-1.5em,0); }
    .tower__brick--45 { transform: translate3d(-0.5em,-1.5em,0); }
    .tower__brick--90 { transform: translate3d(0,-1em,0) rotateZ(90deg); }
    .tower__brick--135 { transform: translate3d(0,0,0) rotateZ(90deg); }
    .tower__brick--180 { transform: translate3d(-0.5em,0.5em,0); }
    .tower__brick--225 { transform: translate3d(-1.5em,0.5em,0); }
    .tower__brick--270 { transform: translate3d(-2em,0,0) rotateZ(-90deg); }
    .tower__brick--315 { transform: translate3d(-2em,-1em,0) rotateZ(-90deg); }
    .tower__brick--red, .tower__brick--red .tower__brick-side { background-color: var(--red); }
    .tower__brick--orange, .tower__brick--orange .tower__brick-side { background-color: var(--orange); }
    .tower__brick--green, .tower__brick--green .tower__brick-side { background-color: var(--green); }
    .tower__brick--purple, .tower__brick--purple .tower__brick-side { background-color: var(--purple); }
    .tower__brick--magenta, .tower__brick--magenta .tower__brick-side { background-color: var(--magenta); }
    .tower__brick--move1 { animation-name: brick-move-1; }
    .tower__brick--move2 { animation-name: brick-move-2; }
    .tower__brick--move3 { animation-name: brick-move-3; }
    .tower__brick--move4 { animation-name: brick-move-4; }
    .tower__brick--move5 { animation-name: brick-move-5; }
    .tower__brick--move6 { animation-name: brick-move-6; }
    .tower__brick--move7 { animation-name: brick-move-7; }
    .tower__brick--move8 { animation-name: brick-move-8; }
    .tower__brick--move9 { animation-name: brick-move-9; }
    .tower__brick--move10 { animation-name: brick-move-10; }
    .tower__brick--move11 { animation-name: brick-move-11; }
    .tower__brick--move12 { animation-name: brick-move-12; }
    .tower__brick--move13 { animation-name: brick-move-13; }
    .tower__brick--move14 { animation-name: brick-move-14; }
    .tower__brick--move15 { animation-name: brick-move-15; }
    .tower__brick--move16 { animation-name: brick-move-16; }

    .tower__group {
        animation-name: brick-group;
        top: 50%;
        left: 50%;
        transform: rotateX(45deg) rotateZ(45deg);
    }
    
    /* Animations */
    @keyframes brick-group {
        from { transform: rotateX(45deg) rotateZ(0.125turn) translateZ(0); }
        to { transform: rotateX(45deg) rotateZ(2.125turn) translateZ(-4.8em); }
    }
    @keyframes brick-side-1 {
        from, 25%, 50%, 75%, to { filter: brightness(0.5); }
        12.5%, 37.5%, 62.5%, 87.5% { filter: brightness(0.75); }
    }
    @keyframes brick-side-2 {
        from, 25%, 50%, 75%, to { filter: brightness(0.75); }
        12.5%, 37.5%, 62.5%, 87.5% { filter: brightness(0.5); }
    }
    @keyframes brick-move-1 {
        from { animation-timing-function: ease-in; transform: translate3d(0,0,0) rotateZ(90deg); }
        1.25% { animation-timing-function: linear; transform: translate3d(0,0,-0.4em) rotateZ(90deg); }
        2.5% { transform: translate3d(2em,0,-0.4em) rotateZ(90deg); }
        3.75% { transform: translate3d(2em,0,10em) rotateZ(90deg); }
        5% { animation-timing-function: ease-out; transform: translate3d(0,0,10em) rotateZ(90deg); }
        6.25%, to { transform: translate3d(0,0,9.6em) rotateZ(90deg); }
    }
    @keyframes brick-move-2 {
        from, 6.25% { animation-timing-function: ease-in; transform: translate3d(-0.5em,-1.5em,0); }
        7.5% { animation-timing-function: linear; transform: translate3d(-0.5em,-1.5em,-0.4em); }
        8.75% { transform: translate3d(-0.5em,-3.5em,-0.4em); }
        10% { transform: translate3d(-0.5em,-3.5em,10em); }
        11.25% { animation-timing-function: ease-out; transform: translate3d(-0.5em,-1.5em,10em); }
        12.5%, to { transform: translate3d(-0.5em,-1.5em,9.6em); }
    }
    @keyframes brick-move-3 {
        from, 12.5% { animation-timing-function: ease-in; transform: translate3d(-2em,-1em,0) rotateZ(-90deg); }
        13.75% { animation-timing-function: linear; transform: translate3d(-2em,-1em,-0.4em) rotateZ(-90deg); }
        15% { transform: translate3d(-4em,-1em,-0.4em) rotateZ(-90deg); }
        16.25% { transform: translate3d(-4em,-1em,10em) rotateZ(-90deg); }
        17.5% { animation-timing-function: ease-out; transform: translate3d(-2em,-1em,10em) rotateZ(-90deg); }
        18.75%, to { transform: translate3d(-2em,-1em,9.6em) rotateZ(-90deg); }
    }
    @keyframes brick-move-4 {
        from, 18.75% { animation-timing-function: ease-in; transform: translate3d(-1.5em,0.5em,0); }
        20% { animation-timing-function: linear; transform: translate3d(-1.5em,0.5em,-0.4em); }
        21.25% { transform: translate3d(-1.5em,2.5em,-0.4em); }
        22.5% { transform: translate3d(-1.5em,2.5em,10em); }
        23.75% { animation-timing-function: ease-out; transform: translate3d(-1.5em,0.5em,10em); }
        25%, to { transform: translate3d(-1.5em,0.5em,9.6em); }
    }
    @keyframes brick-move-5 {
        from, 25% { animation-timing-function: ease-in; transform: translate3d(0,-1em,0) rotateZ(90deg); }
        26.25% { animation-timing-function: linear; transform: translate3d(0,-1em,-0.4em) rotateZ(90deg); }
        27.5% { transform: translate3d(2em,-1em,-0.4em) rotateZ(90deg); }
        28.75% { transform: translate3d(2em,-1em,10em) rotateZ(90deg); }
        30% { animation-timing-function: ease-out; transform: translate3d(0,-1em,10em) rotateZ(90deg); }
        31.25%, to { transform: translate3d(0,-1em,9.6em) rotateZ(90deg); }
    }
    @keyframes brick-move-6 {
        from, 31.25% { animation-timing-function: ease-in; transform: translate3d(-1.5em,-1.5em,0); }
        32.5% { animation-timing-function: linear; transform: translate3d(-1.5em,-1.5em,-0.4em); }
        33.75% { transform: translate3d(-1.5em,-3.5em,-0.4em); }
        35% { transform: translate3d(-1.5em,-3.5em,10em); }
        36.25% { animation-timing-function: ease-out; transform: translate3d(-1.5em,-1.5em,10em); }
        37.5%, to { transform: translate3d(-1.5em,-1.5em,9.6em); }
    }
    @keyframes brick-move-7 {
        from, 37.5% { animation-timing-function: ease-in; transform: translate3d(-2em,0,0) rotateZ(-90deg); }
        38.75% { animation-timing-function: linear; transform: translate3d(-2em,0,-0.4em) rotateZ(-90deg); }
        40% { transform: translate3d(-4em,0,-0.4em) rotateZ(-90deg); }
        41.25% { transform: translate3d(-4em,0,10em) rotateZ(-90deg); }
        42.5% { animation-timing-function: ease-out; transform: translate3d(-2em,0,10em) rotateZ(-90deg); }
        43.75%, to { transform: translate3d(-2em,0,9.6em) rotateZ(-90deg); }
    }
    @keyframes brick-move-8 {
        from, 43.75% { animation-timing-function: ease-in; transform: translate3d(-0.5em,0.5em,0); }
        45% { animation-timing-function: linear; transform: translate3d(-0.5em,0.5em,-0.4em); }
        46.25% { transform: translate3d(-0.5em,2.5em,-0.4em); }
        47.5% { transform: translate3d(-0.5em,2.5em,10em); }
        48.75% { animation-timing-function: ease-out; transform: translate3d(-0.5em,0.5em,10em); }
        50%, to { transform: translate3d(-0.5em,0.5em,9.6em); }
    }
    @keyframes brick-move-9 {
        from, 50% { animation-timing-function: ease-in; transform: translate3d(0,0,0) rotateZ(90deg); }
        51.25% { animation-timing-function: linear; transform: translate3d(0,0,-0.4em) rotateZ(90deg); }
        52.5% { transform: translate3d(2em,0,-0.4em) rotateZ(90deg); }
        53.75% { transform: translate3d(2em,0,10em) rotateZ(90deg); }
        55% { animation-timing-function: ease-out; transform: translate3d(0,0,10em) rotateZ(90deg); }
        56.25%, to { transform: translate3d(0,0,9.6em) rotateZ(90deg); }
    }
    @keyframes brick-move-10 {
        from, 56.25% { animation-timing-function: ease-in; transform: translate3d(-0.5em,-1.5em,0); }
        57.5% { animation-timing-function: linear; transform: translate3d(-0.5em,-1.5em,-0.4em); }
        58.75% { transform: translate3d(-0.5em,-3.5em,-0.4em); }
        60% { transform: translate3d(-0.5em,-3.5em,10em); }
        61.25% { animation-timing-function: ease-out; transform: translate3d(-0.5em,-1.5em,10em); }
        62.5%, to { transform: translate3d(-0.5em,-1.5em,9.6em); }
    }
    @keyframes brick-move-11 {
        from, 62.5% { animation-timing-function: ease-in; transform: translate3d(-2em,-1em,0) rotateZ(-90deg); }
        63.75% { animation-timing-function: linear; transform: translate3d(-2em,-1em,-0.4em) rotateZ(-90deg); }
        65% { transform: translate3d(-4em,-1em,-0.4em) rotateZ(-90deg); }
        66.25% { transform: translate3d(-4em,-1em,10em) rotateZ(-90deg); }
        67.5% { animation-timing-function: ease-out; transform: translate3d(-2em,-1em,10em) rotateZ(-90deg); }
        68.75%, to { transform: translate3d(-2em,-1em,9.6em) rotateZ(-90deg); }
    }
    @keyframes brick-move-12 {
        from, 68.75% { animation-timing-function: ease-in; transform: translate3d(-1.5em,0.5em,0); }
        70% { animation-timing-function: linear; transform: translate3d(-1.5em,0.5em,-0.4em); }
        71.25% { transform: translate3d(-1.5em,2.5em,-0.4em); }
        72.5% { transform: translate3d(-1.5em,2.5em,10em); }
        73.75% { animation-timing-function: ease-out; transform: translate3d(-1.5em,0.5em,10em); }
        75%, to { transform: translate3d(-1.5em,0.5em,9.6em); }
    }
    @keyframes brick-move-13 {
        from, 75% { animation-timing-function: ease-in; transform: translate3d(0,-1em,0) rotateZ(90deg); }
        76.25% { animation-timing-function: linear; transform: translate3d(0,-1em,-0.4em) rotateZ(90deg); }
        77.5% { transform: translate3d(2em,-1em,-0.4em) rotateZ(90deg); }
        78.75% { transform: translate3d(2em,-1em,10em) rotateZ(90deg); }
        80% { animation-timing-function: ease-out; transform: translate3d(0,-1em,10em) rotateZ(90deg); }
        81.25%, to { transform: translate3d(0,-1em,9.6em) rotateZ(90deg); }
    }
    @keyframes brick-move-14 {
        from, 81.25% { animation-timing-function: ease-in; transform: translate3d(-1.5em,-1.5em,0); }
        82.5% { animation-timing-function: linear; transform: translate3d(-1.5em,-1.5em,-0.4em); }
        83.75% { transform: translate3d(-1.5em,-3.5em,-0.4em); }
        85% { transform: translate3d(-1.5em,-3.5em,10em); }
        86.25% { animation-timing-function: ease-out; transform: translate3d(-1.5em,-1.5em,10em); }
        87.5%, to { transform: translate3d(-1.5em,-1.5em,9.6em); }
    }
    @keyframes brick-move-15 {
        from, 87.5% { animation-timing-function: ease-in; transform: translate3d(-2em,0,0) rotateZ(-90deg); }
        88.75% { animation-timing-function: linear; transform: translate3d(-2em,0,-0.4em) rotateZ(-90deg); }
        90% { transform: translate3d(-4em,0,-0.4em) rotateZ(-90deg); }
        91.25% { transform: translate3d(-4em,0,10em) rotateZ(-90deg); }
        92.5% { animation-timing-function: ease-out; transform: translate3d(-2em,0,10em) rotateZ(-90deg); }
        93.75%, to { transform: translate3d(-2em,0,9.6em) rotateZ(-90deg); }
    }
    @keyframes brick-move-16 {
        from, 93.75% { animation-timing-function: ease-in; transform: translate3d(-0.5em,0.5em,0); }
        95% { animation-timing-function: linear; transform: translate3d(-0.5em,0.5em,-0.4em); }
        96.25% { transform: translate3d(-0.5em,2.5em,-0.4em); }
        97.5% { transform: translate3d(-0.5em,2.5em,10em); }
        98.75% { animation-timing-function: ease-out; transform: translate3d(-0.5em,0.5em,10em); }
        to { transform: translate3d(-0.5em,0.5em,9.6em); }
    }
    @keyframes message-fade-in {
        from { opacity: 0; }
        6%, to { opacity: 1; }
    }
    @keyframes message-fade-in-out {
        from, to { opacity: 0; }
        6%, 94% { opacity: 1; }
    }

    /* Κρυφό περιτύλιγμα για το περιεχόμενο της σελίδας */
    #main-content-wrapper {
        display: none;
        flex-grow: 1;
        flex-direction: column;
    }

    /* CSS για τη βασική δομή της σελίδας (όπως ήταν) */
    .wljs-wrapper-header {
        padding: 15px 25px;
        background-color: #f8f9fa;
        border-bottom: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .wljs-wrapper-return-button {
        display: inline-block;
        padding: 10px 18px;
        background-color: #007bff;
        color: white !important;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        font-size: 0.95em;
        transition: background-color 0.2s ease-in-out;
    }
    .wljs-wrapper-return-button:hover,
    .wljs-wrapper-return-button:focus {
        background-color: #0056b3;
        color: white !important;
        text-decoration: none;
    }
    .wljs-wrapper-paragraph {
        font-size: 0.9em;
        color: #495057;
        margin-top: 12px;
        margin-bottom: 0;
        line-height: 1.5;
    }
    .wljs-original-content-container {
        flex-grow: 1;
        padding: 20px;
        overflow-x: auto;
    }
    .wljs-wrapper-signature {
        padding: 12px 25px;
        text-align: right;
        font-size: 0.8em;
        color: #6c757d;
        border-top: 1px solid #e9ecef;
        margin-top: auto;
        background-color: #f8f9fa;
    }
    .wljs-wrapper-signature p {
        margin: 0;
    }
</style>
"""

# --- HTML Templates για header, footer και script ---
def get_header_html(index_file, paragraph_text):
    return f"""
<div class="wljs-wrapper-header">
    <a href="{index_file}" class="wljs-wrapper-return-button">ΕΠΙΣΤΡΟΦΗ</a>
    <p class="wljs-wrapper-paragraph">{paragraph_text}</p>
</div>
"""

def get_footer_html(signature_text):
    return f"""
<div class="wljs-wrapper-signature">
    <p>{signature_text}</p>
</div>
"""

def get_script_html():
    return """
<script>
    document.addEventListener('DOMContentLoaded', () => {
        const loader = document.getElementById('loader');
        const content = document.getElementById('main-content-wrapper');

        // Θέτουμε ένα χρονόμετρο για να κρύψουμε τον loader και να εμφανίσουμε το περιεχόμενο
        setTimeout(() => {
            // Κρύβουμε τον loader
            loader.style.opacity = '0';
            
            // Μετά το τέλος της μετάβασης, το κρύβουμε εντελώς
            setTimeout(() => {
                loader.style.display = 'none';
                if (content) {
                    content.style.display = 'flex';
                }
            }, 500); // 500ms, ίδιο με το CSS transition
        }, 3000); // 3000ms = 3 δευτερόλεπτα (μπορείτε να το αλλάξετε)
    });
</script>
"""

def process_html_file(filepath):
    """
    Επεξεργάζεται ένα αρχείο HTML, προσθέτοντας header, footer, loader και JavaScript.
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')

        # --- 1. Προσθήκη CSS στο <head> ---
        head = soup.find('head')
        if not head:
            head = soup.new_tag('head')
            if soup.html:
                soup.html.insert(0, head)
            else:
                html_tag = soup.new_tag('html')
                html_tag.append(head)
                soup.insert(0, html_tag)

        # Έλεγχος αν τα στυλ υπάρχουν ήδη
        existing_styles = head.find_all('style', string=lambda t: "wljs-wrapper-header" in t if t else False)
        if existing_styles:
            print(f"  [INFO] Τα CSS styles φαίνεται να υπάρχουν ήδη στο <head> του '{os.path.basename(filepath)}'. Παράλειψη.")
            return False # Παράκαμψη αν έχει ήδη επεξεργαστεί

        # Προσθήκη των νέων στυλ
        head.append(BeautifulSoup(CSS_STYLES, 'html.parser'))
        print(f"  [INFO] Προστέθηκαν CSS styles στο <head> του '{os.path.basename(filepath)}'.")

        # --- 2. Επεξεργασία του <body> ---
        body = soup.find('body')
        if not body:
            print(f"  [ERROR] Δεν βρέθηκε <body> tag στο αρχείο '{os.path.basename(filepath)}'. Παράλειψη.")
            return False

        # Εξαγωγή του αρχικού περιεχομένου
        original_content = ""
        main_content_wrapper = body.find(id='main-content-wrapper')
        if main_content_wrapper:
            original_content_container = main_content_wrapper.find(class_='wljs-original-content-container')
            if original_content_container:
                original_content = ''.join(str(c) for c in original_content_container.children)
            body.clear()
        else:
            original_content = ''.join(str(c) for c in list(body.children))
            body.clear()

        # Δημιουργία του container για το αρχικό περιεχόμενο
        original_content_container = soup.new_tag('div', attrs={'class': 'wljs-original-content-container'})
        original_content_container.append(BeautifulSoup(original_content, 'html.parser'))

        # Δημιουργία του περιτυλίγματος που θα περιέχει το header, το περιεχόμενο και το footer
        main_content_wrapper = soup.new_tag('div', attrs={'id': 'main-content-wrapper'})

        # Δημιουργία των HTML elements για header και footer
        header_element = BeautifulSoup(get_header_html(INDEX_FILENAME, PARAGRAPH_TEXT), 'html.parser')
        
        try:
            creation_timestamp = os.path.getctime(filepath)
            creation_year = datetime.datetime.fromtimestamp(creation_timestamp).year
        except Exception as e:
            print(f"  [WARNING] Δεν ήταν δυνατή η λήψη του έτους δημιουργίας για το αρχείο '{os.path.basename(filepath)}'. Χρήση τρέχοντος έτους. Σφάλμα: {e}")
            creation_year = datetime.datetime.now().year
        
        dynamic_signature_text = f"{BASE_SIGNATURE_TEXT}{creation_year}"
        footer_element = BeautifulSoup(get_footer_html(dynamic_signature_text), 'html.parser')

        # Προσθέτουμε τα στοιχεία στο περιτύλιγμα
        main_content_wrapper.append(header_element)
        main_content_wrapper.append(original_content_container)
        main_content_wrapper.append(footer_element)

        # Δημιουργία του loader και του script
        loader_element = BeautifulSoup(LOADER_HTML, 'html.parser')
        script_element = BeautifulSoup(get_script_html(), 'html.parser')

        # Προσθέτουμε τον loader, το περιτύλιγμα και το script στο body
        body.append(loader_element)
        body.append(main_content_wrapper)
        body.append(script_element)

        # Προσθήκη του lang attribute στο html tag
        if soup.html:
            soup.html['lang'] = 'el'

        # --- 3. Αποθήκευση των αλλαγών ---
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify(formatter="html5")))

        print(f"  [SUCCESS] Το αρχείο '{os.path.basename(filepath)}' τροποποιήθηκε επιτυχώς (Έτος υπογραφής: {creation_year}).")
        return True

    except FileNotFoundError:
        print(f"  [ERROR] Το αρχείο '{os.path.basename(filepath)}' δεν βρέθηκε.")
        return False
    except Exception as e:
        print(f"  [ERROR] Παρουσιάστηκε σφάλμα κατά την επεξεργασία του '{os.path.basename(filepath)}': {e}")
        return False

def main():
    """
    Κύρια συνάρτηση του script.
    Βρίσκει και επεξεργάζεται τα κατάλληλα HTML αρχεία.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Το script εκτελείται από τον φάκελο: {script_dir}")
    print(f"Αναζήτηση για αρχεία HTML που περιέχουν '{FILENAME_KEYWORD}' στο όνομά τους...")
    
    processed_files = 0
    skipped_files = 0
    
    for filename in os.listdir(script_dir):
        if FILENAME_KEYWORD in filename and filename.lower().endswith(('.html', '.htm')):
            filepath = os.path.join(script_dir, filename)
            print(f"\nΕπεξεργασία αρχείου: {filename}")
            if process_html_file(filepath):
                processed_files += 1
            else:
                skipped_files +=1 

    print("\n--- Σύνοψη Επεξεργασίας ---")
    print(f"Συνολικά αρχεία που ταιριάζουν με τα κριτήρια και ελέγχθηκαν: {processed_files + skipped_files}")
    print(f"Αρχεία που τροποποιήθηκαν επιτυχώς: {processed_files}")
    print(f"Αρχεία που παραλείφθηκαν (π.χ. ήδη επεξεργασμένα ή με σφάλματα): {skipped_files}")
    
    if processed_files == 0 and skipped_files == 0:
        print(f"\nΔεν βρέθηκαν αρχεία που να περιέχουν '{FILENAME_KEYWORD}' και να τελειώνουν σε .html/.htm στον φάκελο του script.")
        print("Βεβαιωθείτε ότι το script βρίσκεται στον ίδιο φάκελο με τα HTML αρχεία σας.")

if __name__ == '__main__':
    print("="*50)
    print("Script Τροποποίησης HTML για Wolfram Websites (v3)")
    print("="*50)
    print("ΣΗΜΑΝΤΙΚΟ: Κρατήστε αντίγραφα ασφαλείας των αρχείων σας πριν συνεχίσετε!")
    main()
    print("\nΗ επεξεργασία ολοκληρώθηκε.")
