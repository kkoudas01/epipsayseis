
document.getElementById('info-icon').onclick = function() {
    document.getElementById('info-popup').style.display = 'block';
}

document.getElementById('books-icon').onclick = function() {
    document.getElementById('books-popup').style.display = 'block';
}

function closePopup(id) {
    document.getElementById(id).style.display = 'none';
}
