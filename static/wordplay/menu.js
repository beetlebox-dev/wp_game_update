
// Copyright 2021 Johnathan Pennington | All rights reserved.


// HTML elements
let mobileMenuIsOpen = false;
const menuButton = document.getElementById('menu-button');
const mobileMenuOpenImg = document.getElementById('menu-button-open-img');
const mobileMenuClosedImg = document.getElementById('menu-button-closed-img');
const menuBar = document.getElementById('menu-bar');
const menuItems = document.querySelectorAll('.menu-items a');
const menuBugArea = document.getElementById('wordplay-menu-bug');
const bugImg = document.getElementById('bug');

// Event listeners
window.addEventListener('resize', resizeWindow);
menuButton.addEventListener('click', function() {
    mobileMenuIsOpen = mobileMenuIsOpen === false;
    resizeWindow();
});
document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && mobileMenuIsOpen) {
        event.preventDefault();
        mobileMenuIsOpen = false;
        resizeWindow();
    };
});
menuBugArea.addEventListener('mouseenter', () => {
    bugImg.style.filter = 'invert(100%)';
});
menuBugArea.addEventListener('mouseleave', () => {
    bugImg.style.filter = 'invert(11%) sepia(68%) saturate(6420%) hue-rotate(149deg) brightness(105%) contrast(105%)';
});

resizeWindow();

function resizeWindow() {
    if (window.innerWidth < 800) {  // narrow/mobile display
        document.body.style.paddingTop = '0';
        for (const menuItem of menuItems) {
            menuItem.style.display = 'block';
            menuItem.style.textAlign = 'left';
        };
        if (mobileMenuIsOpen) {
            menuBar.style.display = 'block';
            menuBar.style.height = '100%';
            menuBar.style.paddingTop = '6em';
            menuBar.style.textAlign = 'left';
            menuBar.style.backgroundColor = 'hsla(0, 0%, 0%, 85%)';
            mobileMenuClosedImg.style.display = 'none';
            mobileMenuOpenImg.style.display = 'block';
        } else {  // Mobile menu is closed.
            menuBar.style.display = 'none';
            mobileMenuClosedImg.style.display = 'block';
            mobileMenuOpenImg.style.display = 'none';
        };
    } else {  // wide/desktop display
        document.body.style.paddingTop = '4em';
        for (const menuItem of menuItems) {
            menuItem.style.display = 'inline-block';
            menuItem.style.textAlign = 'center';
        };
        menuBar.style.display = 'block';
        menuBar.style.height = 'auto';
        menuBar.style.paddingTop = '0';
        mobileMenuClosedImg.style.display = 'none';
        mobileMenuOpenImg.style.display = 'none';
        menuBar.style.backgroundColor = 'hsla(0, 0%, 0%, 100%)';
        mobileMenuIsOpen = false;
    };
};
