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
<div id="loader-overlay">
    <div class="pl">
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
    #loader-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        display: grid;
        place-items: center;
        background-color: hsl(223,10%,30%);
        transition: opacity 0.5s ease-out;
        z-index: 9999;
    }
    
    .pl {
        box-shadow: 2em 0 2em hsla(0,0%,0%,0.2) inset, -2em 0 2em hsla(0,0%,100%,0.1) inset;
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        transform: rotateX(30deg) rotateZ(45deg);
        width: 15em;
        height: 15em;
        border-radius: 50%;
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

    .pl__dot:before,
    .pl__dot:after {
        content: "";
        display: block;
        left: 0;
        width: inherit;
        animation-duration: 2s;
        animation-iteration-count: infinite;
        position: absolute;
    }

    .pl__dot:before {
        animation-name: pushInOut1;
        background-color: hsl(223,10%,30%);
        border-radius: inherit;
        box-shadow: 0.05em 0 0.1em hsla(0,0%,100%,0.2) inset;
        height: inherit;
        z-index: 1;
    }

    .pl__dot:after {
        animation-name: pushInOut2;
        background-color: hsl(223,90%,55%);
        border-radius: 0.75em;
        box-shadow: 0.1em 0.3em 0.2em hsla(0,0%,100%,0.4) inset, 
                    0 -0.4em 0.2em hsl(223,10%,20%) inset, 
                    0 -1em 0.25em hsla(0,0%,0%,0.3) inset;
        bottom: 0;
        clip-path: polygon(0 75%, 100% 75%, 100% 100%, 0 100%);
        height: 3em;
        transform: rotate(-45deg);
        transform-origin: 50% 2.25em;
    }

    /* Specific dot positioning and animation delays */
    .pl__dot:nth-child(1) { transform: rotate(-0deg) translateX(5em) rotate(0deg); z-index: 5; }
    .pl__dot:nth-child(2) { transform: rotate(-30deg) translateX(5em) rotate(30deg); z-index: 4; }
    .pl__dot:nth-child(3) { transform: rotate(-60deg) translateX(5em) rotate(60deg); z-index: 3; }
    .pl__dot:nth-child(4) { transform: rotate(-90deg) translateX(5em) rotate(90deg); z-index: 2; }
    .pl__dot:nth-child(5) { transform: rotate(-120deg) translateX(5em) rotate(120deg); z-index: 1; }
    .pl__dot:nth-child(6) { transform: rotate(-150deg) translateX(5em) rotate(150deg); z-index: 1; }
    .pl__dot:nth-child(7) { transform: rotate(-180deg) translateX(5em) rotate(180deg); z-index: 2; }
    .pl__dot:nth-child(8) { transform: rotate(-210deg) translateX(5em) rotate(210deg); z-index: 3; }
    .pl__dot:nth-child(9) { transform: rotate(-240deg) translateX(5em) rotate(240deg); z-index: 4; }
    .pl__dot:nth-child(10) { transform: rotate(-270deg) translateX(5em) rotate(270deg); z-index: 5; }
    .pl__dot:nth-child(11) { transform: rotate(-300deg) translateX(5em) rotate(300deg); z-index: 6; }
    .pl__dot:nth-child(12) { transform: rotate(-330deg) translateX(5em) rotate(330deg); z-index: 6; }

    /* Animation delays */
    .pl__dot:nth-child(1), .pl__dot:nth-child(1):before, .pl__dot:nth-child(1):after { animation-delay: -0.00s; }
    .pl__dot:nth-child(2), .pl__dot:nth-child(2):before, .pl__dot:nth-child(2):after { animation-delay: -0.1667s; }
    .pl__dot:nth-child(3), .pl__dot:nth-child(3):before, .pl__dot:nth-child(3):after { animation-delay: -0.3333s; }
    .pl__dot:nth-child(4), .pl__dot:nth-child(4):before, .pl__dot:nth-child(4):after { animation-delay: -0.5000s; }
    .pl__dot:nth-child(5), .pl__dot:nth-child(5):before, .pl__dot:nth-child(5):after { animation-delay: -0.6667s; }
    .pl__dot:nth-child(6), .pl__dot:nth-child(6):before, .pl__dot:nth-child(6):after { animation-delay: -0.8333s; }
    .pl__dot:nth-child(7), .pl__dot:nth-child(7):before, .pl__dot:nth-child(7):after { animation-delay: -1.0000s; }
    .pl__dot:nth-child(8), .pl__dot:nth-child(8):before, .pl__dot:nth-child(8):after { animation-delay: -1.1667s; }
    .pl__dot:nth-child(9), .pl__dot:nth-child(9):before, .pl__dot:nth-child(9):after { animation-delay: -1.3333s; }
    .pl__dot:nth-child(10), .pl__dot:nth-child(10):before, .pl__dot:nth-child(10):after { animation-delay: -1.5000s; }
    .pl__dot:nth-child(11), .pl__dot:nth-child(11):before, .pl__dot:nth-child(11):after { animation-delay: -1.6667s; }
    .pl__dot:nth-child(12), .pl__dot:nth-child(12):before, .pl__dot:nth-child(12):after { animation-delay: -1.8333s; }

    .pl__text {
        color: hsl(223,10%,90%);
        font-size: 0.75em;
        max-width: 5rem;
        position: relative;
        text-shadow: 0 0 0.1em hsla(223,10%,90%,0.5);
        transform: rotateZ(-45deg);
    }
    
    /* Animations */
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
            background-color: hsl(223,10%,30%);
            transform: translate(0,0);
        }
        25% {
            animation-timing-function: ease-out;
            background-color: hsl(223,90%,65%);
            transform: translate(-71%,-71%);
        }
        50%,
        to {
            background-color: hsl(223,10%,30%);
            transform: translate(0,0);
        }
    }
    
    @keyframes pushInOut2 {
        from {
            animation-timing-function: ease-in;
            background-color: hsl(223,10%,30%);
            clip-path: polygon(0 75%, 100% 75%, 100% 100%, 0 100%);
        }
        25% {
            animation-timing-function: ease-out;
            background-color: hsl(223,90%,55%);
            clip-path: polygon(0 25%, 100% 25%, 100% 100%, 0 100%);
        }
        50%,
        to {
            background-color: hsl(223,10%,30%);
            clip-path: polygon(0 75%, 100% 75%, 100% 100%, 0 100%);
        }
    }

    /* Κρυφό περιτύλιγμα για το περιεχόμενο της σελίδας */
    #main-content-wrapper {
        display: none;
        flex-grow: 1;
        flex-direction: column;
    }

    /* CSS για τη βασική δομή της σελίδας */
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

# --- HTML Templates για header, footer ---
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

# --- JavaScript για την απόκρυψη του loader ---
JS_SCRIPT = """
<script>
    window.addEventListener('load', function() {
        const loader = document.getElementById('loader-overlay');
        const content = document.getElementById('main-content-wrapper');
        
        if (loader) {
            loader.style.opacity = '0';
            setTimeout(function() {
                loader.style.display = 'none';
                if (content) {
                    content.style.display = 'flex';
                }
            }, 500);
        }
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
        existing_styles = head.find('style', string=lambda t: "wljs-wrapper-header" in t if t else False)
        if existing_styles:
            print(f"  [INFO] Τα CSS styles φαίνεται να υπάρχουν ήδη στο <head> του '{os.path.basename(filepath)}'. Παράλειψη.")
            return False  # Παράλειψη επεξεργασίας

        # Προσθήκη των νέων στυλ
        head.append(BeautifulSoup(CSS_STYLES, 'html.parser'))
        print(f"  [INFO] Προστέθηκαν CSS styles στο <head> του '{os.path.basename(filepath)}'.")

        # --- 2. Επεξεργασία του <body> ---
        body = soup.find('body')
        if not body:
            print(f"  [ERROR] Δεν βρέθηκε <body> tag στο αρχείο '{os.path.basename(filepath)}'. Παράλειψη.")
            return False

        # Δημιουργία του περιτυλίγματος για το κύριο περιεχόμενο
        main_content_wrapper = soup.new_tag('div', attrs={'id': 'main-content-wrapper'})
        
        # Δημιουργία του container για το αρχικό περιεχόμενο
        original_content_container = soup.new_tag('div', attrs={'class': 'wljs-original-content-container'})
        
        # Μετακίνηση όλου του υπάρχοντος περιεχομένου στο νέο container
        for child in list(body.contents):
            if child.name and child.name != 'script':  # Αποφυγή μετακίνησης scripts
                original_content_container.append(child.extract())
            elif not child.name:  # Μετακίνηση κειμένου
                original_content_container.append(child.extract())

        # Δημιουργία των HTML elements για header
        header_element = BeautifulSoup(get_header_html(INDEX_FILENAME, PARAGRAPH_TEXT), 'html.parser')
        
        # Λήψη έτους δημιουργίας αρχείου
        try:
            creation_timestamp = os.path.getctime(filepath)
            creation_year = datetime.datetime.fromtimestamp(creation_timestamp).year
        except Exception as e:
            print(f"  [WARNING] Δεν ήταν δυνατή η λήψη του έτους δημιουργίας: {e}")
            creation_year = datetime.datetime.now().year
        
        # Δημιουργία υπογραφής
        dynamic_signature_text = f"{BASE_SIGNATURE_TEXT}{creation_year}"
        footer_element = BeautifulSoup(get_footer_html(dynamic_signature_text), 'html.parser')

        # Προσθήκη στοιχείων στο περιτύλιγμα
        main_content_wrapper.append(header_element)
        main_content_wrapper.append(original_content_container)
        main_content_wrapper.append(footer_element)

        # Δημιουργία του loader
        loader_element = BeautifulSoup(LOADER_HTML, 'html.parser')
        
        # Δημιουργία του script
        script_element = BeautifulSoup(JS_SCRIPT, 'html.parser')

        # Προσθήκη στοιχείων στο body
        body.append(loader_element)
        body.append(main_content_wrapper)
        body.append(script_element)

        # Ορισμός γλώσσας σε ελληνικά
        if soup.html:
            soup.html['lang'] = 'el'
        else:
            current_contents = list(soup.contents)
            soup.clear()
            new_html_tag = soup.new_tag('html', lang='el')
            for item in current_contents:
                new_html_tag.append(item)
            soup.append(new_html_tag)

        # --- 3. Αποθήκευση των αλλαγών ---
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(str(soup.prettify(formatter="html5")))

        print(f"  [SUCCESS] Το αρχείο '{os.path.basename(filepath)}' τροποποιήθηκε επιτυχώς (Έτος: {creation_year}).")
        return True

    except FileNotFoundError:
        print(f"  [ERROR] Το αρχείο '{os.path.basename(filepath)}' δεν βρέθηκε.")
        return False
    except Exception as e:
        print(f"  [ERROR] Σφάλμα επεξεργασίας '{os.path.basename(filepath)}': {e}")
        return False

def main():
    """
    Κύρια συνάρτηση: Επεξεργάζεται όλα τα HTML αρχεία με τη λέξη-κλειδί.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Εκτέλεση script από: {script_dir}")
    print(f"Αναζήτηση για HTML αρχεία με '{FILENAME_KEYWORD}'...")
    
    processed_files = 0
    skipped_files = 0

    for filename in os.listdir(script_dir):
        if FILENAME_KEYWORD in filename and filename.lower().endswith(('.html', '.htm')):
            filepath = os.path.join(script_dir, filename)
            print(f"\nΕπεξεργασία: {filename}")
            if process_html_file(filepath):
                processed_files += 1
            else:
                skipped_files +=1

    print("\n--- Αποτελέσματα ---")
    print(f"Σύνολο αρχείων: {processed_files + skipped_files}")
    print(f"Επεξεργασμένα: {processed_files}")
    print(f"Παραλειπόμενα: {skipped_files}")
    
    if processed_files == 0 and skipped_files == 0:
        print(f"\nΔεν βρέθηκαν αρχεία με '{FILENAME_KEYWORD}' στον φάκελο.")

if __name__ == '__main__':
    print("="*50)
    print("Επεξεργαστής HTML για WLJS Ιστοσελίδες")
    print("="*50)
    print("ΠΡΟΕΙΔΟΠΟΙΗΣΗ: Δημιουργήστε αντίγραφα ασφαλείας πριν εκτελέσετε!")
    main()
    print("\nΟλοκλήρωση επεξεργασίας.")