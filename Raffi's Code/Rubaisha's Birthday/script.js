// --- 1. Canvas Falling Characters ---
const canvas = document.getElementById('matrix-bg');
const ctx = canvas.getContext('2d');

canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let characters = '♥*+<317'.split('');
let fontSize = 16;
let columns = canvas.width / fontSize;
let drops = [];

for (let x = 0; x < columns; x++) {
    drops[x] = 1;
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(5, 2, 31, 0.05)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = '#ff3aff'; // Neon Pink
    ctx.font = fontSize + 'px VT323';

    for (let i = 0; i < drops.length; i++) {
        let text = characters[Math.floor(Math.random() * characters.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    }
}
setInterval(drawMatrix, 40);


// --- 2. Interactive Heart & Sound ---
const heart = document.getElementById('interactiveHeart');
const clickSound = document.getElementById('clickSound');

heart.addEventListener('click', () => {
    heart.classList.add('beating');
    clickSound.currentTime = 0;
    clickSound.play();
    setTimeout(() => {
        heart.classList.remove('beating');
    }, 500);
});


// --- 3. Blinking Browser Tab Title ---
const titles = [
    "For Ruby",
    "A Message...",
    "Happy 17th",
    "<3"
];
let titleIndex = 0;

setInterval(() => {
    document.title = titles[titleIndex % titles.length];
    titleIndex++;
}, 2500);


// --- 4. Delayed Message Reveal ---
const hiddenMessage = document.getElementById('hiddenMessage');
setTimeout(() => {
    hiddenMessage.classList.add('visible');
}, 4000); // Reveal after 4 seconds


// --- 5. Auto-Typing Status Log ---
const statusLogElement = document.getElementById('status-log');
const logMessages = [
    "// loading memory: ruby_bday.dat",
    "// connection unstable...",
    "// running nostalgia protocol...",
    "// happy_birthday.exe executed."
];
let messageIndex = 0;
let charIndex = 0;
let isDeleting = false;

function typeStatus() {
    const currentMessage = logMessages[messageIndex];
    if (isDeleting) {
        statusLogElement.textContent = currentMessage.substring(0, charIndex - 1);
        charIndex--;
        if (charIndex === 0) {
            isDeleting = false;
            messageIndex = (messageIndex + 1) % logMessages.length;
        }
    } else {
        statusLogElement.textContent = currentMessage.substring(0, charIndex + 1);
        charIndex++;
        if (charIndex === currentMessage.length) {
            isDeleting = true;
            setTimeout(typeStatus, 2000); // Pause before deleting
            return;
        }
    }
    setTimeout(typeStatus, isDeleting ? 50 : 100);
}

document.addEventListener('DOMContentLoaded', typeStatus);