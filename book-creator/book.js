const { createCanvas, loadImage, registerFont } = require("canvas");
const multiplier = 5;
const canvasWidth = 240 * multiplier;
const canvasHeight = 157 * multiplier;
const canvas = createCanvas(canvasWidth, canvasHeight);
const ctx = canvas.getContext("2d");
const fs = require("fs");
let textEndY = 0;
registerFont("font/sylfaen.ttf", { family: "Sylfaen" });

function fitImageOnCanvas(canvas, img) {
  const ctx = canvas.getContext("2d");
  const canvasRatio = canvas.width / canvas.height;
  const imgRatio = img.width / img.height;

  let newWidth, newHeight, xOffset, yOffset;

  if (canvasRatio > imgRatio) {
    // Canvas is wider than image
    newWidth = canvas.width;
    newHeight = canvas.width / imgRatio;
    xOffset = 0;
    yOffset = -(newHeight - canvas.height) / 2;
  } else {
    // Canvas is taller than image
    newHeight = canvas.height;
    newWidth = canvas.height * imgRatio;
    yOffset = 0;
    xOffset = -(newWidth - canvas.width) / 2;
  }

  ctx.drawImage(img, xOffset, yOffset, newWidth, newHeight);
}

function wrapTextAndDraw(
  ctx,
  text,
  x,
  startY,
  maxWidth,
  lineHeight,
  align = "left"
) {
  ctx.textAlign = align;
  const words = text.split(" ");
  let lines = [];
  let line = "";
  let testLine, metrics;

  for (let i = 0; i < words.length; i++) {
    testLine = line + words[i] + " ";
    metrics = ctx.measureText(testLine);

    if (metrics.width > maxWidth && i > 0) {
      lines.push(line);
      line = words[i] + " ";
    } else {
      line = testLine;
    }
  }
  lines.push(line);

  let y = startY;
  for (let j = 0; j < lines.length; j++) {
    let currentLine = lines[j];
    let xPos = x;
    if (align === "center") {
      xPos = x + maxWidth / 2;
    } else if (align === "right") {
      xPos = x + maxWidth;
    }
    ctx.fillStyle = "#ffffff"; //<======= here
    ctx.fillText(currentLine, xPos, y);
    y += lineHeight;
  }

  // Return the y position at the end of the text
  return y;
}
async function addBackground() {
  const image = await loadImage("backgrounds/forest/night/2.png");
  fitImageOnCanvas(canvas, image);
}

// Now update the addText function
function addText() {
  const text =
    "In the tranquil Magical Forest of Eldoria, where the trees whispered ancient secrets and the stars danced with the night sky, there lived a radiant butterfly named Bella.";
  const canvasWidth = ctx.canvas.width;
  const x = canvasWidth * 0.1; // X position
  const y = canvasWidth * 0.1; // Starting Y position
  const maxWidth = canvasWidth * 0.8; // Maximum line width
  const fontSize = 30;
  const lineHeight = fontSize + 5; // Line height
  const align = "center"; // Can be 'left', 'right', or 'center'

  ctx.font = `${fontSize}px Sylfaen`; // Set the desired font

  // Store the end Y position after the text
  textEndY = wrapTextAndDraw(ctx, text, x, y, maxWidth, lineHeight, align);

  // You can now use endY to position another object right below the text
  // Example: ctx.fillRect(x, endY, 100, 50); // Draw a rectangle below the text
}

async function addImageToCanvas(imgUrl, x, y, newHeight) {
  const image = await loadImage(imgUrl);
  // Calculate new width to maintain aspect ratio
  const aspectRatio = image.width / image.height;
  const newWidth = newHeight * aspectRatio;

  // Draw the image on the canvas
  ctx.drawImage(image, x - (image.width * 0.5) / 2, y, newWidth, newHeight);
}

function gradientOverlay() {
  const grV = ctx.createLinearGradient(0, 0, 0, ctx.canvas.height);
  grV.addColorStop(0, "rgba(0,0,0,1)");
  grV.addColorStop(0.3, "rgba(0,0,0,0.7)");
  grV.addColorStop(0.5, "rgba(0,0,0,0)");
  grV.addColorStop(1, "rgba(0,0,0,0)");

  ctx.fillStyle = grV;
  ctx.fillRect(0, 0, ctx.canvas.width, ctx.canvas.height);
}

(async () => {
  await addBackground();
  gradientOverlay();
  addText();
  await addImageToCanvas(
    "character.png",
    canvasWidth * 0.5,
    textEndY,
    canvasHeight - textEndY
  );
  const buffer = canvas.toBuffer("image/png");
  fs.writeFileSync("output.png", buffer, "utf-8");
})();
