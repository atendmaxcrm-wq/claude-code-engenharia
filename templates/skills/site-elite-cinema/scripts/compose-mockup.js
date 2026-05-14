#!/usr/bin/env node
// compose-mockup.js
// Composite a screenshot inside a device mockup PNG and emit a 1920x1080 frame.
// Usage: compose-mockup.js --screenshot=path --device=macbook|iphone --output=path

"use strict";

const fs = require("fs");
const path = require("path");
const { spawnSync } = require("child_process");

const SCRIPT_DIR = __dirname;
const SKILL_DIR = path.resolve(SCRIPT_DIR, "..");
const MOCKUPS_DIR = path.join(SKILL_DIR, "mockups");
const NODE_MODULES = path.join(SKILL_DIR, "node_modules");

function parseArgs(argv) {
  const out = {};
  for (const raw of argv) {
    if (!raw.startsWith("--")) continue;
    const eq = raw.indexOf("=");
    if (eq === -1) {
      out[raw.slice(2)] = true;
    } else {
      out[raw.slice(2, eq)] = raw.slice(eq + 1);
    }
  }
  return out;
}

function ensureSharp() {
  try {
    return require("sharp");
  } catch (_e) {
    console.error("[compose-mockup] sharp missing, installing locally ...");
    const r = spawnSync("npm", ["install", "--prefix", SKILL_DIR, "--no-audit", "--no-fund", "sharp@^0.33.0"], {
      stdio: "inherit",
    });
    if (r.status !== 0) {
      console.error("ERROR: failed to install sharp");
      process.exit(1);
    }
    return require(path.join(NODE_MODULES, "sharp"));
  }
}

const DEVICES = {
  macbook: {
    width: 2880,
    height: 1800,
    screen: { x: 224, y: 100, w: 2432, h: 1600 },
    mockup: "macbook.png",
  },
  iphone: {
    width: 1170,
    height: 2532,
    screen: { x: 100, y: 200, w: 970, h: 2132 },
    mockup: "iphone.png",
  },
};

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const screenshot = args.screenshot;
  const device = args.device || "macbook";
  const output = args.output || `./mockup-${Date.now()}.png`;

  if (!screenshot) {
    console.error("Usage: compose-mockup.js --screenshot=PATH --device=macbook|iphone --output=PATH");
    process.exit(64);
  }
  if (!fs.existsSync(screenshot)) {
    console.error(`ERROR: screenshot not found at ${screenshot}`);
    process.exit(66);
  }
  const cfg = DEVICES[device];
  if (!cfg) {
    console.error(`ERROR: unknown device '${device}'. Use macbook or iphone.`);
    process.exit(64);
  }

  const sharp = ensureSharp();
  const mockupPath = path.join(MOCKUPS_DIR, cfg.mockup);
  if (!fs.existsSync(mockupPath)) {
    console.error(`[compose-mockup] missing mockup PNG at ${mockupPath}`);
    console.error("Place a transparent device mockup PNG with these dimensions there:");
    console.error(`  device=${device}  size=${cfg.width}x${cfg.height}  screen=(${cfg.screen.x},${cfg.screen.y}) ${cfg.screen.w}x${cfg.screen.h}`);
    console.error("Suggested sources: figma community device mockups, mockuphone.com, or design-system kits.");
    process.exit(74);
  }

  const fittedScreenshot = await sharp(screenshot)
    .resize(cfg.screen.w, cfg.screen.h, { fit: "cover", position: "top" })
    .toBuffer();

  const composedDevice = await sharp(mockupPath)
    .composite([{ input: fittedScreenshot, left: cfg.screen.x, top: cfg.screen.y }])
    .png()
    .toBuffer();

  const FINAL_W = 1920;
  const FINAL_H = 1080;
  const BG = { r: 10, g: 10, b: 10, alpha: 1 };

  const fitWidth = Math.round(FINAL_W * 0.7);
  const ratio = cfg.height / cfg.width;
  let drawW = fitWidth;
  let drawH = Math.round(drawW * ratio);
  if (drawH > FINAL_H * 0.85) {
    drawH = Math.round(FINAL_H * 0.85);
    drawW = Math.round(drawH / ratio);
  }
  const resizedDevice = await sharp(composedDevice).resize(drawW, drawH, { fit: "inside" }).toBuffer();

  const left = Math.round((FINAL_W - drawW) / 2);
  const top = Math.round((FINAL_H - drawH) / 2);

  await sharp({
    create: { width: FINAL_W, height: FINAL_H, channels: 4, background: BG },
  })
    .composite([{ input: resizedDevice, left, top }])
    .png()
    .toFile(output);

  const stat = fs.statSync(output);
  console.log("---");
  console.log(`OUTPUT:  ${output}`);
  console.log(`SIZE:    ${Math.round(stat.size / 1024)} KB`);
  console.log(`DIM:     ${FINAL_W}x${FINAL_H}`);
  console.log(`DEVICE:  ${device} placed at (${left},${top}) sized ${drawW}x${drawH}`);
  console.log("---");
}

main().catch((err) => {
  console.error("ERROR:", err && err.message ? err.message : err);
  process.exit(1);
});
