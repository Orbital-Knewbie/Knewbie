$(document).ready(function () {

  // LOADING PAGE
  $(window).on("load", function(){
    $(".loader-wrapper").fadeOut("fast");
    $("#name").addClass("animateName");
    $("#sub").addClass("animateSub");
    $('body').removeClass('loading');
  });

  // NAVBAR TOGGLE OPEN AND CLOSE
  $('.menu').on('click', function () {
    $(this).toggleClass('open');
    $('.navbar').toggleClass('open');
  });

  $('.navbar .link').on('click', function () {
    $('.menu').removeClass('open');
    $('.navbar').removeClass('open');
  });

// SMOOTH SCROLL EFFECT
  const scroll = new SmoothScroll('.navbar a[href*="#"]', {
    speed: 1500
  });

//RETURN TO TOP BUTTTON
  const backtotop = document.querySelector("#backtotop");
  backtotop.addEventListener("click", function () {
    $("html, body").animate({ scrollTop: 0 }, "slow");
  });

// ANIMATIONS
  AOS.init({
    easing: 'ease',
    duration: 1800,
    once: true
  });

});
