let slideIndex = 0;
let timeout;

function showSlides() {
  let i;
  const slides = document.getElementsByClassName("mySlides");
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";
  }
  slideIndex++;
  if (slideIndex > slides.length) {
    slideIndex = 1;
  }
  slides[slideIndex - 1].style.display = "flex";
  timeout = setTimeout(showSlides, 5000); // Change slide every 4 seconds (adjust as needed)
}

function plusSlides(n) {
  clearTimeout(timeout);
  slideIndex += n;
  if (slideIndex > document.getElementsByClassName("mySlides").length) {
    slideIndex = 1;
  } else if (slideIndex < 1) {
    slideIndex = document.getElementsByClassName("mySlides").length;
  }
  showSlides();
}

document.addEventListener("DOMContentLoaded", function () {
  showSlides();
});
