import os

MENU_FULL = """
<!-- Cyberpunk Menu START -->
<style>
  body {
    margin: 0;
    font-family: 'Orbitron', sans-serif;
    background: #0d0d0d;
    color: #fff;
  }
  nav {
    display: flex;
    background: rgba(20, 20, 30, 0.9);
    backdrop-filter: blur(6px);
    padding: 10px 20px;
    box-shadow: 0 0 15px #0ff, inset 0 0 5px #f0f;
  }
  nav ul { list-style: none; display: flex; gap: 20px; margin: 0; padding: 0; }
  nav ul li { position: relative; }
  nav a {
    text-decoration: none; color: #fff;
    padding: 8px 14px; display: inline-block;
    transition: 0.3s; border: 1px solid transparent;
  }
  nav a:hover { border-color: #0ff; box-shadow: 0 0 10px #0ff; }
  .dropdown, .submenu {
    display: none; position: absolute;
    background: rgba(30, 30, 50, 0.95);
    top: 100%; left: 0; min-width: 180px;
    box-shadow: 0 0 10px #f0f; padding: 10px 0; z-index: 100;
  }
  .submenu { top: 0; left: 100%; }
  .dropdown a, .submenu a { display: block; padding: 8px 14px; border-left: 2px solid transparent; }
  .dropdown a:hover, .submenu a:hover { border-left: 2px solid #0ff; background: rgba(255, 0, 255, 0.2); }
  .mega-menu {
    display: none; position: absolute;
    top: 100%; left: 0; width: 600px;
    background: rgba(20, 20, 40, 0.95);
    padding: 20px; box-shadow: 0 0 20px #0ff;
    grid-template-columns: repeat(3, 1fr);
    gap: 20px; z-index: 100;
  }
  .mega-menu .section { border: 1px solid #f0f; padding: 10px; }
  .modal {
    display: none; position: fixed; inset: 0;
    background: rgba(0,0,0,0.85); backdrop-filter: blur(8px);
    justify-content: center; align-items: center; z-index: 200;
  }
  .modal-content {
    background: #111; border: 2px solid #0ff;
    box-shadow: 0 0 20px #f0f; padding: 20px;
    max-width: 400px; text-align: center;
  }
  .close { cursor: pointer; float: right; color: #f0f; font-size: 18px; }
  .glow { text-shadow: 0 0 5px #0ff, 0 0 10px #f0f, 0 0 20px #0ff; }
</style>

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

<div class="modal" id="about-modal">
  <div class="modal-content">
    <span class="close" id="close-modal">&times;</span>
    <h2 class="glow">About</h2>
    <p>Αυτό είναι ένα cyberpunk drop-down + mega menu demo.</p>
  </div>
</div>

<script>
  document.querySelectorAll(".menu-toggle").forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();
      let dropdown = btn.nextElementSibling;
      dropdown.style.display = dropdown.style.display === "block" ? "none" : "block";
    });
  });
  document.querySelectorAll(".submenu-toggle").forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();
      let submenu = btn.nextElementSibling;
      submenu.style.display = submenu.style.display === "block" ? "none" : "block";
    });
  });
  document.querySelectorAll(".mega-toggle").forEach(btn => {
    btn.addEventListener("click", e => {
      e.preventDefault();
      let mega = btn.nextElementSibling;
      mega.style.display = mega.style.display === "grid" ? "none" : "grid";
    });
  });
  const modal = document.getElementById("about-modal");
  const aboutBtn = document.getElementById("about-btn");
  const closeBtn = document.getElementById("close-modal");
  aboutBtn.addEventListener("click", e => {
    e.preventDefault();
    modal.style.display = "flex";
  });
  closeBtn.addEventListener("click", () => {
    modal.style.display = "none";
  });
  window.addEventListener("click", e => {
    if (e.target === modal) modal.style.display = "none";
  });
</script>
<!-- Cyberpunk Menu END -->
"""

def insert_menu_in_html(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "Cyberpunk Menu START" in content:
        print(f"Το menu υπάρχει ήδη στο {file_path}")
        return

    if "</body>" in content:
        new_content = content.replace("</body>", MENU_FULL + "\n</body>", 1)
    else:
        new_content = content + MENU_FULL

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Προστέθηκε το menu στο {file_path}")

if __name__ == "__main__":
    folder = os.path.dirname(os.path.abspath(__file__))  # ίδιος φάκελος
    for file in os.listdir(folder):
        if "wljs" in file and file.endswith(".html"):
            insert_menu_in_html(os.path.join(folder, file))
