#!/usr/bin/env node
const { spawn } = require("node:child_process");
const path = require("node:path");
const { ensureBinary } = require("../lib/native.cjs");
const { resolveCodexHome, rewriteNpmToolScripts, syncPromptHistory } = require("../lib/history.cjs");

function shouldSyncPromptHistory(argv) {
  return (
    argv[0] !== "install-codex" &&
    argv[0] !== "uninstall-codex" &&
    !argv.includes("--help") &&
    !argv.includes("-h") &&
    !argv.includes("--version")
  );
}

function runBinary(binaryPath, argv) {
  return new Promise((resolve, reject) => {
    const child = spawn(binaryPath, argv, {
      stdio: "inherit"
    });

    child.on("error", (error) => {
      reject(new Error(`Failed to launch native binary: ${error.message}`));
    });

    child.on("exit", (code, signal) => {
      resolve({ code: code ?? 0, signal });
    });
  });
}

async function main() {
  const argv = process.argv.slice(2);
  const codexHome = resolveCodexHome(argv);

  if (shouldSyncPromptHistory(argv)) {
    try {
      const syncResult = await syncPromptHistory(codexHome);
      if (syncResult.created) {
        process.stderr.write(
          `[codex-observatory] Reconstructed ${path.basename(syncResult.historyPath)} from session logs\n`
        );
      }
    } catch (error) {
      process.stderr.write(`[codex-observatory] Failed to prepare prompt history: ${error.message}\n`);
    }
  }

  const binaryPath = await ensureBinary({ quiet: false });
  const result = await runBinary(binaryPath, argv);

  if (!result.signal && result.code === 0 && argv[0] === "install-codex") {
    await rewriteNpmToolScripts(codexHome, {
      nodePath: process.execPath,
      entryScriptPath: __filename
    });
    process.stderr.write(
      `[codex-observatory] Refreshed npm helper scripts under ${path.join(codexHome, "tools")}\n`
    );
  }

  if (result.signal) {
    process.kill(process.pid, result.signal);
    return;
  }

  process.exit(result.code);
}

main().catch((error) => {
  console.error(`[codex-observatory] ${error.message}`);
  process.exit(1);
});
