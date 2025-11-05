const scenes = [
  {
    image: "images/bedroom.jpg",
    dialogue: "The room reeks of despair. A razor sits on the dresser.",
    audio: "whisper",
    next: 1
  },
  {
    image: "images/bathroom.jpg",
    dialogue: "The bathtub is tinged with red. The mirror cracks silently.",
    audio: "door",
    next: 2
  },
  {
    image: "images/window.jpg",
    dialogue: "You see the note. Blood trails on the glass.",
    audio: "scream",
    next: null
  }
];

let currentScene = 0;

const sceneImage = document.getElementById("scene-image");
const dialogueBox = document.getElementById("dialogue-box");
const nextBtn = document.getElementById("next-room-btn");

function showScene(index) {
  const scene = scenes[index];
  sceneImage.src = scene.image;
  dialogueBox.textContent = scene.dialogue;

  const sound = document.getElementById(scene.audio);
  sound.play();

  if (scene.next !== null) {
    nextBtn.style.display = "block";
    nextBtn.onclick = () => {
      currentScene = scene.next;
      showScene(currentScene);
    };
  } else {
    nextBtn.style.display = "none";
    dialogueBox.textContent += "\n\nRuby’s ghost appears behind you...";
  }
}

window.onload = () => {
  document.getElementById("game-container").style.display = "none";
};
document.getElementById("start-btn").addEventListener("click", () => {
  document.getElementById("opening-screen").style.display = "none";
  document.getElementById("game-container").style.display = "block";
  showScene(currentScene);
});
