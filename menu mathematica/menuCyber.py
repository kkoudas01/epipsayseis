import os
from bs4 import BeautifulSoup, Tag, Comment

# Το HTML του navigation bar που θέλουμε να εισάγουμε.
navigation_html = r"""
<div class="demo">
    <div class="container">
        <div class="row">
            <div class="col-md-12">
                <nav class="navbar navbar-default navbar-mobile bootsnav">
                    <div class="navbar-header">
                        <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#navbar-menu">
                            <i class="fa fa-bars"></i>
                        </button>
                    </div>
                    <div class="collapse navbar-collapse" id="navbar-menu">
                        <ul class="nav navbar-nav" data-in="fadeInDown" data-out="fadeOutUp">
                            <li class="active"><a href="index.html" data-hover="Home">Home <span data-hover="Home"></span></a></li>
                            <li><a href="#" data-toggle="modal" data-target="#aboutModal" data-hover="About">About <span data-hover="About"></span></a></li>
                            <li class="dropdown">
                                <a href="#" class="dropdown-toggle" data-toggle="dropdown" data-hover="Shortcodes">Shortcodes <span data-hover="Shortcodes"></span></a>
                                <ul class="dropdown-menu animated">
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li class="dropdown">
                                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Sub Menu sort</a>
                                        <ul class="dropdown-menu animated">
                                            <li><a href="#">Custom Menu 1</a></li>
                                            <li><a href="#">Custom Menu 2</a></li>
                                            <li class="dropdown">
                                                <a href="#" class="dropdown-toggle" data-toggle="dropdown">Sub Menu b</a>
                                                <ul class="dropdown-menu animated">
                                                    <li><a href="#">Custom Menu a1</a></li>
                                                    <li><a href="#">Custom Menu a2</a></li>
                                                    <li><a href="#">Custom Menu a3</a></li>
                                                    <li><a href="#">Custom Menu a4</a></li>
                                                </ul>
                                            </li>
                                            <li><a href="#">Custom Menu 3</a></li>
                                        </ul>
                                    </li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                </ul>
                            </li>
                            <li class="dropdown">
                                <a href="#" class="dropdown-toggle" data-toggle="dropdown" data-hover="Pages">Pages <span data-hover="Pages"></span></a>
                                <ul class="dropdown-menu animated">
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li class="dropdown">
                                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">Sub Menu</a>
                                        <ul class="dropdown-menu animated">
                                            <li><a href="#">Custom Menu</a></li>
                                            <li><a href="#">Custom Menu</a></li>
                                            <li class="dropdown">
                                                <a href="#" class="dropdown-toggle" data-toggle="dropdown">Sub Menu</a>
                                                <ul class="dropdown-menu animated">
                                                    <li><a href="#">Custom Menu</a></li>
                                                    <li><a href="#">Custom Menu</a></li>
                                                    <li><a href="#">Custom Menu</a></li>
                                                    <li><a href="#">Custom Menu</a></li>
                                                </ul>
                                            </li>
                                            <li><a href="#">Custom Menu</a></li>
                                        </ul>
                                    </li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                    <li><a href="#">Custom Menu</a></li>
                                </ul>
                            </li>
                            <li><a href="#" data-hover="Portfolio">Portfolio <span data-hover="Portfolio"></span></a></li>
                            <li class="dropdown megamenu-fw">
                                <a href="#" class="dropdown-toggle" data-toggle="dropdown" data-hover="Megamenu">Megamenu <span data-hover="Megamenu"></span></a>
                                <ul class="dropdown-menu megamenu-content animated" role="menu">
                                    <li>
                                        <div class="row">
                                            <div class="col-menu col-md-3">
                                                <h6 class="title">Title Menu One</h6>
                                                <div class="content">
                                                    <ul class="menu-col">
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                    </ul>
                                                </div>
                                            </div>
                                            <div class="col-menu col-md-3">
                                                <h6 class="title">Title Menu Two</h6>
                                                <div class="content">
                                                    <ul class="menu-col">
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                    </ul>
                                                </div>
                                            </div>
                                            <div class="col-menu col-md-3">
                                                <h6 class="title">Title Menu Three</h6>
                                                <div class="content">
                                                    <ul class="menu-col">
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                    </ul>
                                                </div>
                                            </div>
                                            <div class="col-menu col-md-3">
                                                <h6 class="title">Title Menu Four</h6>
                                                <div class="content">
                                                    <ul class="menu-col">
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                        <li><a href="#">Custom Menu</a></li>
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </li>
                                </ul>
                            </li>
                            <li><a href="#" data-hover="Contact">Contact <span data-hover="Contact"></span></a></li>
                        </ul>
                    </div>
                </nav>
            </div>
        </div>
    </div>
</div>
<script>
    $(document).ready(function() {
        // Enable dropdown functionality for desktop
        function setupDesktopMenu() {
            $('.navbar .dropdown').off('hover');
            $('.navbar .dropdown').hover(function() {
                $(this).addClass('on');
                $(this).find('.dropdown-menu').first().stop(true, true).slideDown();
            }, function() {
                $(this).removeClass('on');
                $(this).find('.dropdown-menu').first().stop(true, true).slideUp();
            });
        }
        
        // Enable dropdown functionality for mobile
        function setupMobileMenu() {
            $('.navbar .dropdown').off('hover');
            
            // Αρχικά κλείστε όλα τα dropdowns
            $('.navbar .dropdown').removeClass('on');
            $('.navbar .dropdown-menu').hide();
            
            // Handle dropdown clicks
            $('.navbar .dropdown > a').off('click').on('click', function(e) {
                if ($(window).width() <= 990) {
                    e.preventDefault();
                    var $parent = $(this).parent();
                    var wasOpen = $parent.hasClass('on');
                    
                    // Close all dropdowns first
                    $('.navbar .dropdown').removeClass('on');
                    $('.navbar .dropdown-menu').slideUp();
                    
                    // If the clicked dropdown was not open, open it
                    if (!wasOpen) {
                        $parent.addClass('on');
                        $parent.find('.dropdown-menu').first().stop(true, true).slideDown();
                    }
                    
                    return false;
                }
            });
            
            // Handle subdropdown clicks
            $('.navbar .dropdown .dropdown > a').off('click').on('click', function(e) {
                if ($(window).width() <= 990) {
                    e.preventDefault();
                    e.stopPropagation(); // Prevent event from bubbling to parent dropdown
                    
                    var $parent = $(this).parent();
                    var wasOpen = $parent.hasClass('on');
                    
                    // Close other subdropdowns at this level
                    $parent.siblings('.dropdown').removeClass('on').find('.dropdown-menu').slideUp();
                    
                    // Toggle this subdropdown
                    if (wasOpen) {
                        $parent.removeClass('on');
                        $parent.find('.dropdown-menu').slideUp();
                    } else {
                        $parent.addClass('on');
                        $parent.find('.dropdown-menu').first().stop(true, true).slideDown();
                    }
                    
                    return false;
                }
            });
        }
        
        // Initialize based on screen size
        function initMenu() {
            if ($(window).width() > 990) {
                setupDesktopMenu();
            } else {
                setupMobileMenu();
            }
        }
        
        // Initial setup
        initMenu();
        
        // Handle window resize
        $(window).resize(function() {
            initMenu();
        });
        
        // Mobile menu toggle - use Bootstrap's built-in collapse
        $('.navbar-toggle').click(function() {
            // This is handled by Bootstrap's collapse plugin
        });
    });
</script>
"""

# Το CSS για το navigation bar, αποθηκευμένο σε μια μεταβλητή για καλύτερη οργάνωση.
style_content = """
.demo{ background: #6c5ce7; }
nav.navbar.bootsnav{
    background-color: transparent;
    font-family: 'Ubuntu', sans-serif;
    margin-bottom: 50px;
    border: none;
}
nav.navbar.bootsnav ul.nav > li{ margin: 0 15px 0 0; }
nav.navbar.bootsnav ul.nav > li > a{
    color: #fff;
    font-size: 16px;
    font-weight: 700;
    text-transform: uppercase;
    padding: 7px 15px;
    border-radius: 5px 5px 0 0;
    overflow: hidden;
    position: relative;
    z-index: 1;
    transition: all .5s ease;
}
nav.navbar.bootsnav ul.nav > li.dropdown > a{ padding: 7px 30px 7px 15px; }
nav.navbar.bootsnav ul.nav > li.active > a,
nav.navbar.bootsnav ul.nav > li.active > a:hover,
nav.navbar.bootsnav ul.nav > li > a:hover,
nav.navbar.bootsnav ul.nav > li.on > a{
    color: #fff;
    text-shadow: 0 0 3px #000;
    background-color: transparent;
}
nav.navbar.bootsnav ul.nav > li > a>span:before{
    content: '';
    background-color: rgba(255,255,255,0.5);
    width: 100px;
    height: 100px;
    position: absolute;
    left: 50%;
    top: 0;
    transform: translateX(-50%) rotate(45deg) scale(0);
    z-index: -1;
    transition: all 0.3s;
}
nav.navbar.bootsnav ul.nav > li.on > a > span:before,
nav.navbar.bootsnav ul.nav > li.active > a > span:before,
nav.navbar.bootsnav ul.nav > li > a:hover > span:before{
    transform: translateX(-50%) rotate(45deg) scale(1.8);
}
nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content li a:hover,
nav.navbar.bootsnav li.dropdown ul.dropdown-menu li a:hover,
nav.navbar.bootsnav li.dropdown ul.dropdown-menu li a.dropdown-toggle:active,
nav.navbar ul.nav li.dropdown.on ul.dropdown-menu li.dropdown.on > a{
    color: #fff !important;
    background-color: #6c5ce7 !important;
    font-weight: 600;
    box-shadow: 0 0 5px #000;
}
nav.navbar.bootsnav ul.nav > li.dropdown > a.dropdown-toggle:after{
    content: "\f107";
    font-family: 'FontAwesome';
    color: #fff;
    margin: 0 0 0 7px;
    position: absolute;
    top: 7px;
    right: 7px;
    transition: all 0.3s;
}
nav.navbar.bootsnav ul.nav > li.dropdown > ul{
    opacity: 0;
    visibility: hidden;
    left: 0;
    display: block;
}
nav.navbar.bootsnav ul.nav > li.dropdown.on > ul{
    opacity: 1 !important;
    visibility: visible !important;
}

/* Βελτίωση για το Shortcodes και Pages menu - πιο κοντά στο κουμπί */
nav.navbar.bootsnav ul.nav > li.dropdown:nth-child(3) > ul,
nav.navbar.bootsnav ul.nav > li.dropdown:nth-child(4) > ul {
    top: 95% !important;
}

/* Διόρθωση για megamenu */
.dropdown-menu.megamenu-content {
    width: 700px;
    left: -200px !important;
    padding: 15px;
}
.dropdown-menu.megamenu-content .row {
    display: flex;
    flex-wrap: wrap;
}
.dropdown-menu.megamenu-content .col-menu {
    flex: 0 0 25%;
    max-width: 25%;
}
.dropdown-menu.megamenu-content .title {
    color: #222;
    font-size: 16px;
    font-weight: bold;
    margin-top: 0;
    padding-bottom: 10px;
    border-bottom: 1px solid #ddd;
    margin-bottom: 10px;
}
.dropdown-menu.megamenu-content .menu-col {
    list-style: none;
    padding: 0;
    margin: 0;
}
.dropdown-menu.megamenu-content .menu-col li a {
    display: block;
    padding: 5px 0;
    color: #666;
    text-decoration: none;
    transition: all 0.3s;
}
.dropdown-menu.megamenu-content .menu-col li a:hover {
    color: #6c5ce7;
    padding-left: 5px;
}

/* Διόρθωση για sub-menus - ανοίγουν στο πλάι και στο ίδιο ύψος */
.dropdown-menu .dropdown-menu {
    top: -10px !important;
    left: 100%;
    margin-top: 0;
    margin-left: 0;
}
.dropdown-menu li {
    position: relative;
}
.dropdown-menu > li > a {
    padding: 10px 20px;
    display: block;
    clear: both;
    font-weight: 400;
    line-height: 1.42857143;
    color: #333;
    white-space: nowrap;
}
.dropdown-menu > li > a:hover, 
.dropdown-menu > li > a:focus {
    text-decoration: none;
    color: #262626;
    background-color: #f5f5f5;
}

nav.navbar.bootsnav li.dropdown ul.dropdown-menu{
    background-color: transparent;
    border: none;
    border-radius: 0;
    top: 120%;
    z-index: 1;
}
nav.navbar.bootsnav li.dropdown ul.dropdown-menu > li > a{
    color: #666;
    background-color: #e7e7e7;
    border: none;
    opacity: 0;
    transform: rotateY(180deg);
    transition: all 0.3s ease 0s;
}
nav.navbar.bootsnav li.dropdown.on ul.dropdown-menu > li > a{
    opacity: 1;
    transform: rotateY(0);
}
nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content{
    background-color: #f5f5f5;
    top: 75%;
    left: 0;
}
nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content li{ font-size: 14px; }
nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content .menu-col li a{
    color: #666;
    border: 1px solid rgba(0,0,0,0.1);
    padding-left: 10px;
    margin: 0 0 5px;
    opacity: 0;
    transform: rotateY(180deg);
    transition: all 0.3s;
}
nav.navbar.bootsnav li.dropdown.on ul.dropdown-menu.megamenu-content .menu-col li a{
    opacity: 1;
    transform: rotateY(0);
}

/* Βελτίωση για hover στα sub-menus */
.dropdown-menu li:hover > .dropdown-menu {
    display: block;
}

/* Modal styling */
.modal-content {
    border-radius: 10px;
    box-shadow: 0 5px 25px rgba(0,0,0,0.3);
}
.modal-header {
    background-color: #6c5ce7;
    color: white;
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}
.modal-title {
    font-weight: 700;
}
.close {
    color: white;
    opacity: 0.8;
}
.close:hover {
    color: white;
    opacity: 1;
}

/* Βελτιώσεις για κινητά */
@media only screen and (max-width:990px){
    .demo {
        padding: 10px 0;
    }

    nav.navbar.bootsnav {
        margin-bottom: 50px;
    }

    .navbar-header {
        display: flex;
        justify-content: flex-end;
        width: 100%;
    }

    .dropdown-menu.megamenu-content {
        width: 100%;
        left: 0 !important;
        padding: 10px;
    }
    .dropdown-menu.megamenu-content .col-menu {
        flex: 0 0 100%;
        max-width: 100%;
        margin-bottom: 15px;
    }
    .dropdown-menu .dropdown-menu {
        position: static;
        float: none;
        width: auto;
        margin-top: 0;
        background-color: transparent;
        border: 0;
        box-shadow: none;
        top: 0 !important;
        left: 0 !important;
        display: none;
    }

    nav.navbar.bootsnav .navbar-toggle{
        color: #fff;
        background: rgba(255, 255, 255, 0.2) !important;
        border: 1px solid #fff;
        border-radius: 4px;
        padding: 9px 12px;
        margin: 15px;
        display: block;
    }

    nav.navbar.bootsnav .navbar-toggle .fa-bars {
        font-size: 24px;
    }

    nav.navbar.bootsnav.navbar-mobile .navbar-collapse{ 
        background-color: #6c5ce7; 
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        display: block !important;
    }

    nav.navbar.bootsnav.navbar-mobile .navbar-collapse.in {
        max-height: 80vh;
        overflow-y: auto;
    }

    nav.navbar.bootsnav ul.nav{ 
        margin: 0;
        width: 100%;
    }

    nav.navbar.bootsnav ul.nav>li{ 
        margin: 0;
        width: 100%;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Αρχική κατάσταση - dropdowns κλειστά */
    nav.navbar.bootsnav ul.nav>li.dropdown > a:after {
        content: "\f107" !important; /* Βέλος προς τα κάτω */
        transform: rotate(0deg);
        transition: transform 0.3s;
    }

    nav.navbar.bootsnav ul.nav>li.dropdown.on > a:after {
        content: "\f106" !important; /* Βέλος προς τα πάνω */
    }

    nav.navbar.bootsnav.navbar-mobile ul.nav>li>a{
        text-align: left;
        padding: 15px;
        border: none;
        color: #fff;
        font-size: 16px;
        width: 100%;
    }

    nav.navbar.bootsnav ul.nav>li.dropdown>a{ 
        padding: 15px 40px 15px 15px;
    }

    nav.navbar.bootsnav.navbar-mobile ul.nav>li>a>span:before{
        display: none;
    }

    nav.navbar.bootsnav ul.nav > li.on > a > span:before,
    nav.navbar.bootsnav ul.nav > li.active > a > span:before,
    nav.navbar.bootsnav ul.nav > li > a:hover > span:before{
        display: none;
    }

    nav.navbar.bootsnav ul.nav>li.dropdown>a.dropdown-toggle:after{ 
        right: 15px;
        top: 15px;
        font-size: 18px;
    }

    nav.navbar.bootsnav ul.nav li.dropdown ul.dropdown-menu>li>a{
        color: #fff;
        padding: 12px 15px 12px 30px;
        border: none;
        background-color: rgba(255, 255, 255, 0.1);
    }

    nav.navbar.bootsnav .dropdown-menu{ 
        z-index: 0;
        position: static;
        float: none;
        width: auto;
        margin-top: 0;
        background-color: transparent;
        border: 0;
        box-shadow: none;
        display: none;
    }

    nav.navbar.bootsnav li.dropdown.on > .dropdown-menu {
        display: block;
    }

    /* Βελτίωση 1: Καλύτερα χρώματα για το mega-menu */
    nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content {
        background-color: rgba(0, 0, 0, 0.3); /* Πιο σκούρο φόντο για καλύτερη αντίθεση */
    }

    nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content .col-menu{
        background-color: rgba(255, 255, 255, 0.15); /* Πιο ανοιχτό φόντο για τις στήλες */
        padding: 15px;
        margin-bottom: 10px;
        border-radius: 5px;
    }

    nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content .title{
        font-size: 16px;
        font-weight: bold;
        color: #fff;
        border-bottom: 1px solid rgba(255, 255, 255, 0.3); /* Πιο έντονο border */
    }

    nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content .col-menu.on .title{ 
        color: #fff; 
    }

    nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content .col-menu li a{
       color: rgba(255, 255, 255, 0.95); /* Πιο λευκό κείμενο */
       border: none;
       padding: 8px 0;
   }
   
   nav.navbar.bootsnav li.dropdown ul.dropdown-menu.megamenu-content .col-menu li a:hover {
       color: #fff;
       padding-left: 5px;
       background-color: rgba(255, 255, 255, 0.1); /* Προσθήκη φόντου στο hover */
   }
   
   /* Βελτίωση 2: Υπο-μενού να ανοίγουν πιο δεξιά */
   nav.navbar.bootsnav ul.nav li.dropdown ul.dropdown-menu li ul.dropdown-menu {
       padding-left: 20px; /* Επιπλέον padding για να φαίνονται πιο δεξιά */
   }
}

/* Additional styling for demo page */
body {
    font-family: 'Ubuntu', sans-serif;
}
.content-section {
    padding: 50px 0;
}
.content-section h2 {
    margin-bottom: 30px;
}

/* Mobile specific improvements */
@media only screen and (max-width:768px){
    .content-section {
        padding: 30px 0;
    }
    
    .content-section h2 {
        font-size: 24px;
        margin-bottom: 20px;
    }
}
"""

# Σημάδι που θα εισάγουμε για να αποφύγουμε την επανεπεξεργασία
MARKER_COMMENT = ""

def add_navbar_to_html_files():
    """
    Εντοπίζει αρχεία HTML που περιέχουν τη λέξη 'wljs' στο όνομά τους,
    και προσθέτει ένα navigation bar στην αρχή του body, εφόσον δεν έχει ήδη προστεθεί.
    """
    
    # Αλλάζουμε τον φάκελο εργασίας του script στον φάκελο που βρίσκεται το ίδιο.
    script_directory = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_directory)
    current_directory = os.getcwd()
    
    print(f"Αναζήτηση αρχείων HTML στον φάκελο: {current_directory}")

    # Διατρέχουμε όλα τα αρχεία του τρέχοντος φακέλου
    for filename in os.listdir(current_directory):
        if filename.endswith(".html") and "wljs" in filename:
            file_path = os.path.join(current_directory, filename)
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Ελέγχουμε αν έχει προστεθεί ήδη το menu
                if MARKER_COMMENT in content:
                    print(f"Αρχείο '{filename}' έχει ήδη επεξεργαστεί. Παράβλεψη. ⚠️")
                    continue

                # Parse το HTML
                soup = BeautifulSoup(content, 'html.parser')
                
                # Βρίσκουμε το <body> tag
                body_tag = soup.find('body')

                if body_tag:
                    # Εισάγουμε το comment-σημάδι για να αποφύγουμε την επανεπεξεργασία
                    marker = Comment(MARKER_COMMENT)
                    body_tag.insert(0, marker)
                    
                    # Εισάγουμε το navigation bar ως πρώτο παιδί του <body>
                    navbar_soup = BeautifulSoup(navigation_html, 'html.parser')
                    for child in reversed(list(navbar_soup.body.children)):
                        if isinstance(child, Tag) or isinstance(child, Comment):
                            body_tag.insert(1, child)

                    # Εισάγουμε το CSS και τα JS links στο <head>
                    head_tag = soup.find('head')
                    if head_tag:
                        # CSS links
                        bootstrap_css = soup.new_tag('link', rel='stylesheet', href='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css')
                        font_awesome_css = soup.new_tag('link', rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css')
                        google_fonts = soup.new_tag('link', rel='stylesheet', href='https://fonts.googleapis.com/css?family=Ubuntu:400,700')
                        
                        head_tag.append(bootstrap_css)
                        head_tag.append(font_awesome_css)
                        head_tag.append(google_fonts)
                        
                        # Style tag
                        style_tag = soup.new_tag('style')
                        style_tag.string = style_content
                        head_tag.append(style_tag)
                        
                    # Εισάγουμε τα JS links στο τέλος του <body>
                    if body_tag:
                        jquery_script = soup.new_tag('script', type='text/javascript', src='https://code.jquery.com/jquery-1.12.0.min.js')
                        bootstrap_js = soup.new_tag('script', src='https://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js', integrity='sha384-0mSbJDEHialfmuBBQP6A4Qrprq5OVfW37PRR3j5ELqxss1yVqOtnepnHVP9aJ7xS', crossorigin='anonymous')
                        
                        body_tag.append(jquery_script)
                        body_tag.append(bootstrap_js)

                    # Αποθηκεύουμε το τροποποιημένο αρχείο
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(str(soup))
                    
                    print(f"Επιτυχής επεξεργασία του αρχείου: '{filename}' 👍")
                else:
                    print(f"Αρχείο '{filename}' δεν έχει <body> tag. Παράβλεψη.")

            except Exception as e:
                print(f"Προέκυψε σφάλμα κατά την επεξεργασία του αρχείου '{filename}': {e} ❌")

if __name__ == "__main__":
    add_navbar_to_html_files()