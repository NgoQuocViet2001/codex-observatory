#!/usr/bin/env node
const { maybeAutoSetup } = require("../lib/postinstall.cjs");

maybeAutoSetup().catch((error) => {
  console.warn(`[codex-observatory] Postinstall setup skipped: ${error.message}`);
});
