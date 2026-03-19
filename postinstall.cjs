const { ensureBinary } = require("./lib/native.cjs");

ensureBinary({ quiet: false }).catch((error) => {
  console.warn(`[codex-observatory] Postinstall download skipped: ${error.message}`);
  console.warn("[codex-observatory] The binary will be downloaded on first run instead.");
});
