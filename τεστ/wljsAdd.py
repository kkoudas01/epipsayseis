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
FILENAME_KEYWORD = "(wljs)"

# --- Loader HTML Template ---
LOADER_HTML = """
<div id="loader" class="pl">
    <div class="pl__ring"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__dot"></div>
    <div class="pl__text">Φορτώνει…</div>
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
        --bg: hsl(223, 10%, 30%);
        --fg: hsl(223, 10%, 90%);
        --fg-t: hsla(223, 10%, 90%, 0.5);
        --primary1: hsl(223, 90%, 55%);
        --primary2: hsl(223, 90%, 65%);
        --trans-dur: 0.3s;
        font-size: calc(16px + (20 - 16) * (100vw - 320px) / (1280 - 320));
    }
    
    /* CSS για τον loader (overlay) */
    #loader {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: var(--bg);
        z-index: 9999;
        overflow: hidden;
        transition: opacity 0.5s ease;
    }
    .pl {
        letter-spacing: 0.1em;
        text-transform: uppercase;
        transform: rotateX(30deg) rotateZ(45deg);
        width: 15em;
        height: 15em;
        border-radius: 50%;
    }

    .pl__ring {
        position: absolute;
        width: 14em;
        height: 14em;
        border-radius: 50%;
        box-shadow: 0 0 0 0.12em hsla(0,0%,100%,0.3) inset, 0 0 0 0.25em hsla(0,0%,0%,0.2) inset, 0 0.5em 1em hsla(0,0%,0%,0.3), 0 -0.5em 1em hsla(0,0%,100%,0.1);
    }
    
    .pl__dot {
        animation-name: shadow;
        box-shadow: 0.1em 0.1em 0 0.1em hsl(0,0%,0%), 0.3em 0 0.3em hsla(0,0%,0%,0.5);
        top: calc(50% - 0.75em);
        left: calc(50% - 0.75em);
        width: 1.5em;
        height: 1.5em;
        border-radius: 50%;
        position: absolute;
        animation-duration: 2s;
        animation-iteration-count: infinite;
    }

    .pl__dot:before, .pl__dot:after {
        content: "";
        display: block;
        left: 0;
        width: inherit;
        transition: background-color var(--trans-dur);
        animation-duration: 2s;
        animation-iteration-count: infinite;
        position: absolute;
    }

    .pl__dot:before {
        animation-name: pushInOut1;
        background-color: var(--bg);
        border-radius: inherit;
        box-shadow: 0.05em 0 0.1em hsla(0,0%,100%,0.2) inset;
        height: inherit;
        z-index: 1;
    }

    .pl__dot:after {
        animation-name: pushInOut2;
        background-color: var(--primary1);
        border-radius: 0.75em;
        box-shadow: 0.1em 0.3em 0.2em hsla(0,0%,100%,0.4) inset, 0 -0.4em 0.2em hsl(223, 10%, 20%) inset, 0 -1em 0.25em hsla(0,0%,0%,0.3) inset;
        bottom: 0;
        clip-path: polygon(0 75%, 100% 75%, 100% 100%, 0 100%);
        height: 3em;
        transform: rotate(-45deg);
        transform-origin: 50% 2.25em;
    }
    
    /* Specific dot positioning and animation delays based on Sass loop */
    .pl__dot:nth-child(2) { transform: rotate(0deg) translateX(5em) rotate(0deg); z-index: 5; animation-delay: 0s; }
    .pl__dot:nth-child(2):before, .pl__dot:nth-child(2):after { animation-delay: 0s; }
    .pl__dot:nth-child(3) { transform: rotate(-30deg) translateX(5em) rotate(30deg); z-index: 4; animation-delay: -0.1666666667s; }
    .pl__dot:nth-child(3):before, .pl__dot:nth-child(3):after { animation-delay: -0.1666666667s; }
    .pl__dot:nth-child(4) { transform: rotate(-60deg) translateX(5em) rotate(60deg); z-index: 3; animation-delay: -0.3333333333s; }
    .pl__dot:nth-child(4):before, .pl__dot:nth-child(4):after { animation-delay: -0.3333333333s; }
    .pl__dot:nth-child(5) { transform: rotate(-90deg) translateX(5em) rotate(90deg); z-index: 2; animation-delay: -0.5s; }
    .pl__dot:nth-child(5):before, .pl__dot:nth-child(5):after { animation-delay: -0.5s; }
    .pl__dot:nth-child(6) { transform: rotate(-120deg) translateX(5em) rotate(120deg); z-index: 1; animation-delay: -0.6666666667s; }
    .pl__dot:nth-child(6):before, .pl__dot:nth-child(6):after { animation-delay: -0.6666666667s; }
    .pl__dot:nth-child(7) { transform: rotate(-150deg) translateX(5em) rotate(150deg); z-index: 1; animation-delay: -0.8333333333s; }
    .pl__dot:nth-child(7):before, .pl__dot:nth-child(7):after { animation-delay: -0.8333333333s; }
    .pl__dot:nth-child(8) { transform: rotate(-180deg) translateX(5em) rotate(180deg); z-index: 2; animation-delay: -1s; }
    .pl__dot:nth-child(8):before, .pl__dot:nth-child(8):after { animation-delay: -1s; }
    .pl__dot:nth-child(9) { transform: rotate(-210deg) translateX(5em) rotate(210deg); z-index: 3; animation-delay: -1.1666666667s; }
    .pl__dot:nth-child(9):before, .pl__dot:nth-child(9):after { animation-delay: -1.1666666667s; }
    .pl__dot:nth-child(10) { transform: rotate(-240deg) translateX(5em) rotate(240deg); z-index: 4; animation-delay: -1.3333333333s; }
    .pl__dot:nth-child(10):before, .pl__dot:nth-child(10):after { animation-delay: -1.3333333333s; }
    .pl__dot:nth-child(11) { transform: rotate(-270deg) translateX(5em) rotate(270deg); z-index: 5; animation-delay: -1.5s; }
    .pl__dot:nth-child(11):before, .pl__dot:nth-child(11):after { animation-delay: -1.5s; }
    .pl__dot:nth-child(12) { transform: rotate(-300deg) translateX(5em) rotate(300deg); z-index: 6; animation-delay: -1.6666666667s; }
    .pl__dot:nth-child(12):before, .pl__dot:nth-child(12):after { animation-delay: -1.6666666667s; }
    .pl__dot:nth-child(13) { transform: rotate(-330deg) translateX(5em) rotate(330deg); z-index: 6; animation-delay: -1.8333333333s; }
    .pl__dot:nth-child(13):before, .pl__dot:nth-child(13):after { animation-delay: -1.8333333333s; }

    .pl__text {
        font-size: 0.75em;
        max-width: 5rem;
        position: relative;
        text-shadow: 0 0 0.1em var(--fg-t);
        transform: rotateZ(-45deg);
    }
    
    /* Animations from the Sass code */
    @keyframes shadow {
        from {
            animation-timing-function: ease-in;
            box-shadow: 0.1em 0.1em 0 0.1em hsl(0,0%,0%), 0.3em 0 0.3em hsla(0,0%,0%,0.3);
        }
        25% {
            animation-timing-function: ease-out;
            box-shadow: 0.1em 0.1em 0 0.1em hsl(0,0%,0%), 0.8em 0 0.8em hsla(0,0%,0%,0.5);
        }
        50%,
        to {
            box-shadow: 0.1em 0.1em 0 0.1em hsl(0,0%,0%), 0.3em 0 0.3em hsla(0,0%,0%,0.3);
        }
    }

    @keyframes pushInOut1 {
        from {
            animation-timing-function: ease-in;
            background-color: var(--bg);
            transform: translate(0,0);
        }
        25% {
            animation-timing-function: ease-out;
            background-color: var(--primary2);
            transform: translate(-71%,-71%);
        }
        50%,
        to {
            background-color: var(--bg);
            transform: translate(0,0);
        }
    }

    @keyframes pushInOut2 {
        from {
            animation-timing-function: ease-in;
            background-color: var(--bg);
            clip-path: polygon(0 75%, 100% 75%, 100% 100%, 0 100%);
        }
        25% {
            animation-timing-function: ease-out;
            background-color: var(--primary1);
            clip-path: polygon(0 25%, 100% 25%, 100% 100%, 0 100%);
        }
        50%,
        to {
            background-color: var(--bg);
            clip-path: polygon(0 75%, 100% 75%, 100% 100%, 0 100%);
        }
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
