document.addEventListener('DOMContentLoaded', () => {
    // --- 1. Pre-loader Intro Sequence ---
    const preloaderText = document.getElementById('preloader-text');
    const introLines = [
        "Booting system...",
        "Accessing memory core...",
        "Searching for file: hisham_bday_archive.dat...",
        "File found.",
        "Establishing connection..."
    ];
    let lineIndex = 0;

    const typeIntro = () => {
        if (lineIndex < introLines.length) {
            preloaderText.innerHTML = introLines[lineIndex];
            lineIndex++;
            setTimeout(typeIntro, 800);
        } else {
            const preloader = document.getElementById('preloader');
            preloader.classList.add('fade-out');
            setTimeout(() => {
                preloader.style.display = 'none';
                document.getElementById('main-content').classList.remove('hidden');
                startMainContent(); // Initialize main page scripts
            }, 1000);
        }
    };
    typeIntro();

    function startMainContent() {
        // --- 2. Canvas Falling Characters ---
        const canvas = document.getElementById('matrix-bg');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        let characters = 'HISHAM*+<322'.split('');
        let fontSize = 16;
        let columns = canvas.width / fontSize;
        let drops = Array.from({ length: columns }).fill(1);
        const neonColors = ['#FF1818', '#FFFFFF', '#B20000'];

        function drawMatrix() {
            ctx.fillStyle = 'rgba(0, 0, 0, 0.05)';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.font = fontSize + 'px VT323';
            for (let i = 0; i < drops.length; i++) {
                let text = characters[Math.floor(Math.random() * characters.length)];
                ctx.fillStyle = neonColors[Math.floor(Math.random() * neonColors.length)];
                ctx.fillText(text, i * fontSize, drops[i] * fontSize);
                if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
                    drops[i] = 0;
                }
                drops[i]++;
            }
        }
        setInterval(drawMatrix, 40);

        // --- 3. Interactive Heart & Screen Glitch ---
        const heart = document.getElementById('interactiveHeart');
        const container = document.querySelector('.container');
        heart.addEventListener('click', () => {
            heart.classList.add('beating');
            container.classList.add('screen-glitch');
            setTimeout(() => {
                heart.classList.remove('beating');
                container.classList.remove('screen-glitch');
            }, 500);
        });

        // --- 4. Delayed Message Reveal ---
        setTimeout(() => {
            document.getElementById('hiddenMessage').classList.add('visible');
        }, 4000);

        // --- 5. Auto-Typing Status Log ---
        const statusLogElement = document.getElementById('status-log');
        const logMessages = ["// connection unstable...", "// nostalgia protocol running...", "// happy_birthday.exe executed."];
        let messageIndex = 0; charIndex = 0; let isDeleting = false;
        function typeStatus() {
            const currentMessage = logMessages[messageIndex];
            if (isDeleting) {
                statusLogElement.textContent = currentMessage.substring(0, charIndex--);
                if (charIndex === 0) { isDeleting = false; messageIndex = (messageIndex + 1) % logMessages.length; }
            } else {
                statusLogElement.textContent = currentMessage.substring(0, charIndex++);
                if (charIndex === currentMessage.length) { isDeleting = true; setTimeout(typeStatus, 2000); return; }
            }
            setTimeout(typeStatus, isDeleting ? 50 : 100);
        }
        typeStatus();
        
        // --- 6. Interactive Memory Fragments ---
        const memories = ["long distance sucks", "remember that call?", "the good old days", "future plans", "miss you bro", "22!"];
        document.body.addEventListener('click', (event) => {
            if (event.target.closest('.container') || event.target.id === 'play-pause-btn') return;
            let fragment = document.createElement('div');
            fragment.className = 'memory-fragment';
            fragment.style.left = `${event.clientX - 50}px`;
            fragment.style.top = `${event.clientY - 20}px`;
            fragment.textContent = memories[Math.floor(Math.random() * memories.length)];
            document.body.appendChild(fragment);
            setTimeout(() => { fragment.remove(); }, 2000);
        });

        // --- 7. Music Player ---
        const song = document.getElementById('background-song');
        const playBtn = document.getElementById('play-pause-btn');
        playBtn.addEventListener('click', () => {
            if (song.paused) {
                song.play().catch(error => console.log("Audio play failed: " + error));
                playBtn.textContent = "Pause Song";
            } else {
                song.pause();
                playBtn.textContent = "Play Song";
            }
        });

        // Auto-play music on first interaction
        document.body.addEventListener('click', () => {
            if (song.paused && playBtn.textContent === "Play Song") {
                song.play().catch(error => console.log("Audio play failed: " + error));
                playBtn.textContent = "Pause Song";
            }
        }, { once: true });
    }
});