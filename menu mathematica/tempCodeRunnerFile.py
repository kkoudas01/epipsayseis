import os

# --- το cyberpunk menu που θέλουμε να μπει στα HTML ---
MENU_CODE = """
<!-- Cyberpunk Menu START -->
<nav>
  <ul>
    <li><a href="index.html" class="glow">Home</a></li>
    <li>
      <a href="#" class="menu-toggle">Dropdown ▼</a>
      <ul class="dropdown">
        <li><a href="#">Option 1</a></li>
        <li>
          <a href="#" class="submenu-toggle">Option 2 ▶</a>
          <ul class="submenu">
            <li><a href="#">Sub 2-1</a></li>
            <li>
              <a href="#" class="submenu-toggle">Sub 2-2 ▶</a>
              <ul class="submenu">
                <li><a href="#">Deep 2-2-1</a></li>
                <li><a href="#">Deep 2-2-2</a></li>
              </ul>
            </li>
            <li><a href="#">Sub 2-3</a></li>
          </ul>
        </li>
        <li><a href="#">Option 3</a></li>
      </ul>
    </li>
    <li>
      <a href="#" class="mega-toggle">Mega Menu ▼</a>
      <div class="mega-menu">
        <div class="section">
          <h3 class="glow">Section A</h3>
          <a href="#">Link A1</a>
          <a href="#">Link A2</a>
        </div>
        <div class="section">
          <h3 class="glow">Section B</h3>
          <a href="#">Link B1</a>
          <a href="#">Link B2</a>
        </div>
        <div class="section">
          <h3 class="glow">Section C</h3>
          <a href="#">Link C1</a>
          <a href="#">Link C2</a>
        </div>
      </div>
    </li>
    <li><a href="#" id="about-btn" class="glow">About</a></li>
  </ul>
</nav>
<!-- Cyberpunk Menu END -->
"""

def insert_menu_in_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # αν υπάρχει ήδη menu, μην το ξαναβάλουμε
    if "Cyberpunk Menu START" in content:
        print(f"Το menu υπάρχει ήδη στο {file_path}")
        return

    # εισάγουμε το menu αμέσως μετά το <body>
    if "<body>" in content:
        new_content = content.replace("<body>", "<body>\n" + MENU_CODE, 1)
    else:
        # fallback: βάλτο πριν το </html>
        new_content = content.replace("</html>", MENU_CODE + "\n</html>", 1)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Προστέθηκε το menu στο {file_path}")

def process_folder(folder_path):
    for root, _, files in os.walk(folder_path):
        for file in files:
            if "wljs" in file and file.endswith(".html"):
                full_path = os.path.join(root, file)
                insert_menu_in_html(full_path)

if __name__ == "__main__":
    # αλλάζεις εδώ με τον φάκελο που θες να σκανάρεις
    folder = "./"  
    process_folder(folder)
