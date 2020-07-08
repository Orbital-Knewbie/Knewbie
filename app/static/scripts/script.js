window.addEventListener('load', () => {
    const preload = document.querySelector('.loader-wrapper');
    preload.classList.add('preload-end');
});

$(document).ready(function () {

  // NAVBAR TOGGLE OPEN AND CLOSE
  $('.menu').on('click', function () {
    $(this).toggleClass('open');
    $('.navbar').toggleClass('open');
  });

  $('.navbar .link').on('click', function () {
    $('.menu').removeClass('open');
    $('.navbar').removeClass('open');
  });

  // GSAP ANIMATIONS LANDING PAGE
  gsap.fromTo('.gradient-clipped', {scaleX: 0}, {duration: 1, scaleX: 1});
  gsap.fromTo('.login-form', {opacity: 0}, {duration: 3, delay: 0.5, opacity: 1});
  gsap.fromTo('.menu', {opacity: 0}, {duration: 2, delay: 0.5, opacity: 1});
  gsap.fromTo('.gradient-textbox', {yPercent: 40, opacity: 0}, {duration: 1, delay: 0.8, yPercent: -50, opacity: 1});
});

//SMOOTHSCROLL FOR NAVBAR
$('.navbar a').on('click', function (e) {
  if (this.hash !== '') {
    e.preventDefault();

    const hash = this.hash;

    $('html, body')
      .animate({
        scrollTop: $(hash).offset().top
      },1500);
  }
});

// Reg form, slider
const EducatorButton = document.getElementById('Educator');
const StudentButton = document.getElementById('Student');
const container = document.getElementById('container');

EducatorButton.addEventListener('click', () => {
  container.classList.add("right-panel-active");
});

StudentButton.addEventListener('click', () => {
  container.classList.remove("right-panel-active");
})

// FAQ SEARCH BAR
function searchFunction() {
    var input, textTransform, content, searchText, a, i, ans;
    input = document.getElementById('searchInput');
    textTransform = input.value.toUpperCase();
    content = document.getElementById('accordion');
    searchText = content.getElementsByClassName('accordion-item');

    for (i = 0; i < searchText.length; i++) {
        a = searchText[i].getElementsByTagName('a')[0];
        ans = searchText[i].getElementsByClassName('faq-ans')[0]
        if (a.innerHTML.toUpperCase().indexOf(textTransform) > -1 || ans.innerHTML.toUpperCase().indexOf(textTransform) > -1) {
            searchText[i].style.display = "";
        }

        else {
            searchText[i].style.display = 'none';
        }
    }
}
