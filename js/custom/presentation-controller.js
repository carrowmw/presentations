// This file controls the dynamic state of the presentation based on the current slide.

function handleStateChanges(event) {
  const currentSlide = event.currentSlide || Reveal.getCurrentSlide();

  // --- 1. Handle Particles.js visibility ---
  const particlesCanvas = document.getElementById("particles-js");
  if (particlesCanvas) {
    if (currentSlide.hasAttribute("data-particles")) {
      particlesCanvas.style.display = "block";
    } else {
      particlesCanvas.style.display = "none";
    }
  }

  // --- 2. Handle all visualizations ---
  if (currentSlide.classList.contains("visualization-slide")) {
    // This function is defined in visualizations.js
    processVisualizationSlide(currentSlide);
  }

  // --- 3. Handle footer logic ---
  const footer = document.getElementById("footer-images");
  if (footer) {
    let isLightBg = false;
    const slideBgColorAttr = currentSlide.getAttribute("data-background-color");
    if (slideBgColorAttr) {
      const color = slideBgColorAttr.toLowerCase().trim();
      const lightColors = ["white", "#fff", "#ffffff", "#f5f5f5", "#f8f9fa"];
      if (lightColors.includes(color)) {
        isLightBg = true;
      }
    }
    if (currentSlide.classList.contains("light-background-slide")) {
      isLightBg = true;
    }

    if (isLightBg) {
      footer.classList.add("footer-logos-inverted");
    } else {
      footer.classList.remove("footer-logos-inverted");
    }

    // Logic to hide footer on title slide
    if (currentSlide.classList.contains("title-slide")) {
      footer.style.opacity = "0";
    } else {
      footer.style.opacity = "1";
    }
  }
}
