/**
 * dino-game.js
 * A simple Dino Run style game for the maintenance page.
 */

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const msgEl = document.getElementById('game-msg');
const submsgEl = document.getElementById('game-submsg');
const restartBtn = document.getElementById('restart-btn');
const highScoreEl = document.getElementById('high-score');

// Game constants
const GRAVITY = 0.6;
const JUMP_FORCE = -12;
const GROUND_Y = 170;
const DINO_WIDTH = 40;
const DINO_HEIGHT = 40;
const OBSTACLE_WIDTH = 20;
const OBSTACLE_HEIGHT = 40;

// Game state
let isRunning = false;
let score = 0;
let highScore = localStorage.getItem('dino_highscore') || 0;
highScoreEl.innerText = highScore;

let dino = {
    x: 50,
    y: GROUND_Y - DINO_HEIGHT,
    vy: 0,
    width: DINO_WIDTH,
    height: DINO_HEIGHT,
    isJumping: false
};

let obstacles = [];
let gameSpeed = 5;
let frameCount = 0;

function resetGame() {
    dino.y = GROUND_Y - DINO_HEIGHT;
    dino.vy = 0;
    dino.isJumping = false;
    obstacles = [];
    score = 0;
    gameSpeed = 5;
    frameCount = 0;
    isRunning = true;
    
    msgEl.style.display = 'none';
    submsgEl.style.display = 'none';
    restartBtn.style.display = 'none';
    
    requestAnimationFrame(update);
}

function update() {
    if (!isRunning) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Ground
    ctx.strokeStyle = '#4e4e6a';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, GROUND_Y);
    ctx.lineTo(canvas.width, GROUND_Y);
    ctx.stroke();

    // Dino Physics
    dino.vy += GRAVITY;
    dino.y += dino.vy;

    if (dino.y > GROUND_Y - dino.height) {
        dino.y = GROUND_Y - dino.height;
        dino.vy = 0;
        dino.isJumping = false;
    }

    // Draw Dino (Neon Square for now)
    ctx.fillStyle = '#00d2ff';
    ctx.shadowBlur = 10;
    ctx.shadowColor = '#00d2ff';
    ctx.fillRect(dino.x, dino.y, dino.width, dino.height);
    ctx.shadowBlur = 0;

    // Spawn Obstacles
    if (frameCount % 100 === 0) {
        obstacles.push({
            x: canvas.width,
            y: GROUND_Y - OBSTACLE_HEIGHT,
            width: OBSTACLE_WIDTH,
            height: OBSTACLE_HEIGHT
        });
    }

    // Move & Draw Obstacles
    for (let i = obstacles.length - 1; i >= 0; i--) {
        let obs = obstacles[i];
        obs.x -= gameSpeed;

        // Draw Obstacle (Neon Triangle)
        ctx.fillStyle = '#ff0055';
        ctx.shadowBlur = 10;
        ctx.shadowColor = '#ff0055';
        ctx.beginPath();
        ctx.moveTo(obs.x, obs.y + obs.height);
        ctx.lineTo(obs.x + obs.width / 2, obs.y);
        ctx.lineTo(obs.x + obs.width, obs.y + obs.height);
        ctx.fill();
        ctx.shadowBlur = 0;

        // Collision Detection
        if (
            dino.x < obs.x + obs.width &&
            dino.x + dino.width > obs.x &&
            dino.y < obs.y + obs.height &&
            dino.y + dino.height > obs.y
        ) {
            gameOver();
        }

        // Remove off-screen obstacles
        if (obs.x + obs.width < 0) {
            obstacles.splice(i, 1);
            score++;
            if (score % 5 === 0) gameSpeed += 0.2;
        }
    }

    // Draw Score
    ctx.fillStyle = '#fff';
    ctx.font = 'bold 16px Inter, sans-serif';
    ctx.fillText(`Score: ${score}`, 20, 30);

    frameCount++;
    requestAnimationFrame(update);
}

function gameOver() {
    isRunning = false;
    msgEl.innerText = I18n.t('maintenance.game_over');
    msgEl.style.display = 'block';
    submsgEl.innerText = `${I18n.t('maintenance.final_score')}: ${score}`;
    submsgEl.style.display = 'block';
    restartBtn.style.display = 'inline-block';

    if (score > highScore) {
        highScore = score;
        localStorage.setItem('dino_highscore', highScore);
        highScoreEl.innerText = highScore;
        submsgEl.innerText += ` (${I18n.t('maintenance.new_high_score')})`;
    }
}

function jump() {
    if (!isRunning && restartBtn.style.display === 'none') {
        resetGame();
    } else if (isRunning && !dino.isJumping) {
        dino.vy = JUMP_FORCE;
        dino.isJumping = true;
    }
}

// Input listeners
window.addEventListener('keydown', (e) => {
    if (e.code === 'Space' || e.code === 'ArrowUp') {
        e.preventDefault();
        jump();
    }
});

canvas.addEventListener('mousedown', (e) => {
    jump();
});

restartBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    resetGame();
});
