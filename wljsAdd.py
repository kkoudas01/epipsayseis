# Εκτελώ στον cmd το παρακάτω:
# python wljsAdd.py

import os
import datetime # Προστέθηκε για τη διαχείριση ημερομηνιών
from bs4 import BeautifulSoup # Για την επεξεργασία HTML

# --- Ρυθμίσεις ---
# Κείμενο για την παράγραφο κάτω από το κουμπί επιστροφής
# Τώρα χρησιμοποιούμε απευθείας HTML για τον σύνδεσμο
PARAGRAPH_TEXT = """Υλοποίηση μέσω γλώσσας Wolfram στο <a href="https://jerryi.github.io/wljs-docs/" target="_blank" rel="noopener noreferrer">WLJS Notebook</a>."""
# Το βασικό κείμενο της υπογραφής, το έτος θα προστεθεί δυναμικά
BASE_SIGNATURE_TEXT = "Κώστας Κούδας | &copy; "
# Όνομα αρχείου για το κουμπί επιστροφής
INDEX_FILENAME = "index.html"
# Λέξη-κλειδί για αναγνώριση αρχείων HTML (π.χ., "(wljs)")
FILENAME_KEYWORD = "(wljs)"

# --- CSS Styles που θα προστεθούν στο <head> ---
CSS_STYLES = """
<style>
    body {
        display: flex;
        flex-direction: column;
        min-height: 100vh;
        margin: 0;
        padding: 0;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol";
    }
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
        color: white !important; /* !important για να υπερισχύσει πιθανών άλλων κανόνων */
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
        padding: 20px; /* Προαιρετικό padding γύρω από το αρχικό περιεχόμενο */
        overflow-x: auto; /* Για περίπτωση που το περιεχόμενο είναι φαρδύ */
    }
    .wljs-wrapper-signature {
        padding: 12px 25px;
        text-align: right;
        font-size: 0.8em;
        color: #6c757d;
        border-top: 1px solid #e9ecef;
        margin-top: auto; /* Σπρώχνει την υπογραφή στο κάτω μέρος */
        background-color: #f8f9fa;
    }
    .wljs-wrapper-signature p {
        margin: 0;
    }
</style>
"""

# --- HTML Templates για header και footer ---
def get_header_html(index_file, paragraph_text):
    return f"""
<div class="wljs-wrapper-header">
    <a href="{index_file}" class="wljs-wrapper-return-button">ΕΠΙΣΤΡΟΦΗ</a>
    <p class="wljs-wrapper-paragraph">{paragraph_text}</p>
</div>
"""

def get_footer_html(signature_text): # Η signature_text θα περιλαμβάνει πλέον και το έτος
    return f"""
<div class="wljs-wrapper-signature">
    <p>{signature_text}</p>
</div>
"""

def process_html_file(filepath):
    """
    Επεξεργάζεται ένα αρχείο HTML, προσθέτοντας header, footer και CSS.
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
            else: # Αν δεν υπάρχει ούτε html tag, το προσθέτουμε (ακραία περίπτωση)
                html_tag = soup.new_tag('html')
                html_tag.append(head)
                soup.insert(0, html_tag)

        # Έλεγχος αν τα στυλ υπάρχουν ήδη για να μην τα διπλοπροσθέσουμε
        existing_styles = head.find_all('style', string=lambda t: "wljs-wrapper-header" in t if t else False)
        if not existing_styles:
            head.append(BeautifulSoup(CSS_STYLES, 'html.parser'))
            print(f"  [INFO] Προστέθηκαν CSS styles στο <head> του '{os.path.basename(filepath)}'.")
        else:
            print(f"  [INFO] Τα CSS styles φαίνεται να υπάρχουν ήδη στο <head> του '{os.path.basename(filepath)}'. Παράλειψη.")


        # --- 2. Επεξεργασία του <body> ---
        body = soup.find('body')
        if not body:
            print(f"  [ERROR] Δεν βρέθηκε <body> tag στο αρχείο '{os.path.basename(filepath)}'. Παράλειψη.")
            return False

        # Έλεγχος αν το περιεχόμενο έχει ήδη "ντυθεί"
        # Αυτός ο έλεγχος παραμένει για να αποφευχθεί η πολλαπλή εφαρμογή της δομής
        if body.find('div', class_='wljs-wrapper-header') and body.find('div', class_='wljs-original-content-container'):
            print(f"  [INFO] Το αρχείο '{os.path.basename(filepath)}' φαίνεται να έχει ήδη επεξεργαστεί δομικά. Παράλειψη περαιτέρω περιτυλίγματος.")
            # Αν θέλουμε να ενημερώνουμε πάντα το header/footer ακόμα κι αν η δομή υπάρχει:
            # 1. Βρίσκουμε το υπάρχον header και το αντικαθιστούμε.
            # 2. Βρίσκουμε το υπάρχον footer και το αντικαθιστούμε.
            # Για τώρα, το αφήνουμε να παραλείπει την πλήρη επανεπεξεργασία αν η δομή υπάρχει.
            # Αν θέλεις να γίνεται πάντα update, θα πρέπει να αφαιρέσεις αυτό το return False
            # και να προσθέσεις λογική για αντικατάσταση των υπαρχόντων header/footer.
            return False # ΣΗΜΑΝΤΙΚΟ: Αν θέλεις να ενημερώνεται πάντα η υπογραφή, αυτό πρέπει να αλλάξει.

        # Δημιουργία του container για το αρχικό περιεχόμενο
        original_content_container = soup.new_tag('div', attrs={'class': 'wljs-original-content-container'})
        
        for child_element in list(body.children):
            original_content_container.append(child_element.extract())

        # Δημιουργία των HTML elements για header
        header_element = BeautifulSoup(get_header_html(INDEX_FILENAME, PARAGRAPH_TEXT), 'html.parser')
        
        # Λήψη του έτους δημιουργίας του αρχείου
        try:
            creation_timestamp = os.path.getctime(filepath)
            creation_year = datetime.datetime.fromtimestamp(creation_timestamp).year
        except Exception as e:
            print(f"  [WARNING] Δεν ήταν δυνατή η λήψη του έτους δημιουργίας για το αρχείο '{os.path.basename(filepath)}'. Χρήση τρέχοντος έτους. Σφάλμα: {e}")
            creation_year = datetime.datetime.now().year # Εναλλακτικά, αν αποτύχει
        
        # Δημιουργία του κειμένου υπογραφής με το σωστό έτος
        dynamic_signature_text = f"{BASE_SIGNATURE_TEXT}{creation_year}"
        footer_element = BeautifulSoup(get_footer_html(dynamic_signature_text), 'html.parser')

        body.append(header_element)
        body.append(original_content_container)
        body.append(footer_element)
        
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

        print(f"  [SUCCESS] Το αρχείο '{os.path.basename(filepath)}' τροποποιήθηκε επιτυχώς (Έτος υπογραφής: {creation_year}).")
        return True

    except FileNotFoundError:
        print(f"  [ERROR] Το αρχείο '{os.path.basename(filepath)}' δεν βρέθηκε.")
        return False
    except Exception as e:
        print(f"  [ERROR] Παρουσιάστηκε σφάλμα κατά την επεξεργασία του '{os.path.basename(filepath)}': {e}")
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
    # failed_files = 0 # Δεν χρησιμοποιείται ενεργά με την τρέχουσα λογική μέτρησης

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
    print("Script Τροποποίησης HTML για Wolfram Websites (v2)")
    print("="*50)
    print("ΣΗΜΑΝΤΙΚΟ: Κρατήστε αντίγραφα ασφαλείας των αρχείων σας πριν συνεχίσετε!")
    main()
    print("\nΗ επεξεργασία ολοκληρώθηκε.")
