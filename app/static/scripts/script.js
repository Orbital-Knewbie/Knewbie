$(document).ready(function () {

  // TRANSITION FOR SPLIT SCREEN
  const left = document.querySelector('.left');
  const right = document.querySelector('.right');
  const container = document.querySelector('.split-container');

  left.addEventListener('mouseenter', () => {
    container.classList.add('hover-left');
  });

  left.addEventListener('mouseleave', () => {
    container.classList.remove('hover-left');
  });

  right.addEventListener('mouseenter', () => {
    container.classList.add('hover-right');
  });

  right.addEventListener('mouseleave', () => {
    container.classList.remove('hover-right');
  });

  // LOADING PAGE
  // $(window).on("load", function(){
  //   $(".loader-wrapper").fadeOut("fast");
  //   $("#name").addClass("animateName");
  //   $("#sub").addClass("animateSub");
  //   $('body').removeClass('loading');
  // });

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
  gsap.fromTo('.logo', {x: -200, opacity: 0}, {duration: 1, delay: 0.5, x: 0, opacity: 1});
  gsap.fromTo('.menu', {opacity: 0}, {duration: 2, delay: 0.5, opacity: 1});
  gsap.fromTo('.gradient-textbox', {yPercent: 40, opacity: 0}, {duration: 1, delay: 0.8, yPercent: -50, opacity: 1});

  //ANIMATE ON SCROLL QUERY
  //initialize
  // AOS.init({
  //   easing: 'ease',
  //   duration: 1800,
  //   once: true
  // });


});

//SMOOTHSCROLL FOR NAVBAR
// const scroll = new SmoothScroll('.navbar a[href*="#"]', {
//   speed: 1500
// });
//
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

// MODAL FORM SIGNUP
const EducatorButton = document.getElementById('Educator');
const StudentButton = document.getElementById('Student');
const container = document.getElementById('container');

EducatorButton.addEventListener('click', () => {
  container.classList.add("right-panel-active");
});

StudentButton.addEventListener('click', () => {
  container.classList.remove("right-panel-active");
})

document.getElementById('signupnow').addEventListener("click", function() {
	document.querySelector('.modal-container').style.display = "inline";
});

document.querySelector('.close').addEventListener("click", function() {
	document.querySelector('.modal-container').style.display = "none";
});

document.querySelector('.close1').addEventListener("click", function() {
	document.querySelector('.modal-container').style.display = "none";
});

// MODAL FOR LOGIN
document.getElementById('std-login').addEventListener("click", function () {
   document.querySelector('.login-modal').style.display = "flex";
});

document.getElementById('tcr-login').addEventListener("click", function () {
   document.querySelector('.login-modal').style.display = "flex";
});

document.querySelector('.loginclose').addEventListener("click", function () {
   document.querySelector('.login-modal').style.display = "none";
});
