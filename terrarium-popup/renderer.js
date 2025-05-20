// This is just a little test bit to make sure this'll work, I've never used electron

const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

let x = 10;
let dx = 2;

function draw() {
    ctx.fillStyle = 'red';
    ctx.fillRect(0, 0, canvas.width, canvas.height); // Kind of cursed way of doing it, should probably fix in final version.
    ctx.fillStyle - 'red';
    ctx.beginPath();
    ctx.arc(x, canvas.height / 2, 10, 0, Math.PI * 2);
    ctx.fill();

    x += dx;
    if (x > canvas.width - 10 || x < 10) dx *= -1;

    requestAnimationFrame(draw);
}

draw();
