let searchBar = document.querySelector('.search');
let search = document.getElementById('show-search');
let ftr = document.querySelector('footer');
let hideftr = document.getElementById('hide-ftr');
let showftr = document.getElementById('show-ftr');
let logo = document.querySelector('.logo');

function showSearch(){
	searchBar.style.display = "flex";
	search.style.display = "none";
	logo.style.display = "none";
}

function hideSearch() {
	searchBar.style.display = "none";
	search.style.display = "block";
	logo.style.display = "block";
}

function showFooter() {
	ftr.classList.add('slide-up');
	showftr.style.display = "none";
	hideftr.style.display = "block";
}

function hideFooter() {
	ftr.classList.remove('slide-up');
	showftr.style.display = "block";
	hideftr.style.display = "none";
}

function hideFlash() {
    let flashBox = document.getElementById('flash-box');
    if (flashBox) {
        flashBox.style.display = "none";
    }
}