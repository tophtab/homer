#!/usr/bin/env node

const { spawnSync } = require("node:child_process");
const path = require("node:path");

const script = path.resolve(__dirname, "..", "scripts", "homer-install.py");
const candidates = process.platform === "win32"
  ? ["python", "python3", "py"]
  : ["python3", "python"];

let lastError = null;

for (const command of candidates) {
  const args = command === "py"
    ? ["-3", script, ...process.argv.slice(2)]
    : [script, ...process.argv.slice(2)];
  const result = spawnSync(command, args, { stdio: "inherit" });

  if (result.error) {
    if (result.error.code === "ENOENT") {
      lastError = result.error;
      continue;
    }
    console.error(result.error.message);
    process.exit(1);
  }

  process.exit(result.status ?? 0);
}

console.error("Homer requires Python 3 on PATH.");
if (lastError) {
  console.error(lastError.message);
}
process.exit(1);
