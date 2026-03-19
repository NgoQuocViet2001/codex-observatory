#!/usr/bin/env node
const { spawn } = require("node:child_process");
const { ensureBinary } = require("../lib/native.cjs");

async function main() {
  const binaryPath = await ensureBinary({ quiet: false });
  const child = spawn(binaryPath, process.argv.slice(2), {
    stdio: "inherit"
  });

  child.on("error", (error) => {
    console.error(`[codex-observatory] Failed to launch native binary: ${error.message}`);
    process.exit(1);
  });

  child.on("exit", (code, signal) => {
    if (signal) {
      process.kill(process.pid, signal);
      return;
    }
    process.exit(code ?? 0);
  });
}

main().catch((error) => {
  console.error(`[codex-observatory] ${error.message}`);
  process.exit(1);
});
