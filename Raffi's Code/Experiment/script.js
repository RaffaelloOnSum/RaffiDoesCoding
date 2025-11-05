document.addEventListener("DOMContentLoaded", () => {
  const ghostLines = document.querySelectorAll(".ghost-text p");
  const startBtn = document.getElementById("start-btn");
  const overlay = document.getElementById("start-overlay");
  const bgAudio = document.getElementById("bg-audio");

  let i = 0;

  function revealText() {
    if (i < ghostLines.length) {
      ghostLines[i].style.opacity = 1;
      i++;
      setTimeout(revealText, 2000);
    }
  }

  revealText();

  startBtn.addEventListener("click", () => {
    overlay.style.display = "none";
    bgAudio.volume = 0.4;
    bgAudio.play().catch(err => {
      console.warn("Audio playback failed: ", err);
    });
  });
});
