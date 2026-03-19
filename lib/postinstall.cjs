const path = require("node:path");
const { spawn } = require("node:child_process");

function isGlobalInstall(env = process.env) {
  return env.npm_config_global === "true" || env.npm_config_location === "global";
}

function shouldAutoSetup(env = process.env) {
  return (
    isGlobalInstall(env) &&
    env.CI !== "true" &&
    env.CODEX_OBSERVATORY_SKIP_AUTO_SETUP !== "1"
  );
}

function runAutoSetup({
  nodePath = process.execPath,
  entryScriptPath = path.join(__dirname, "..", "bin", "codex-observatory.cjs"),
  env = process.env,
  stdio = "inherit"
} = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(
      nodePath,
      [entryScriptPath, "install-codex", "--patch-codex"],
      {
        stdio,
        env
      }
    );

    child.on("error", (error) => {
      reject(new Error(`Failed to run automatic Codex setup: ${error.message}`));
    });

    child.on("exit", (code, signal) => {
      if (signal) {
        reject(new Error(`Automatic Codex setup terminated with signal ${signal}`));
        return;
      }
      if ((code ?? 0) !== 0) {
        reject(new Error(`Automatic Codex setup exited with code ${code ?? 0}`));
        return;
      }
      resolve({ code: code ?? 0 });
    });
  });
}

async function maybeAutoSetup(options = {}) {
  const env = options.env || process.env;
  if (!shouldAutoSetup(env)) {
    return { attempted: false, skipped: true };
  }

  try {
    await runAutoSetup({ ...options, env });
    return { attempted: true, skipped: false };
  } catch (error) {
    const stream = options.stderr || process.stderr;
    stream.write(`[codex-observatory] Automatic \`codex stats\` setup skipped: ${error.message}\n`);
    stream.write("[codex-observatory] Run `codex-observatory install-codex --patch-codex` manually if needed.\n");
    return { attempted: true, skipped: false, error };
  }
}

module.exports = {
  isGlobalInstall,
  maybeAutoSetup,
  runAutoSetup,
  shouldAutoSetup
};
