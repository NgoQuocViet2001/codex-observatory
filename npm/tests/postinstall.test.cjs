const test = require("node:test");
const assert = require("node:assert/strict");

const { isGlobalInstall, shouldAutoSetup } = require("../../lib/postinstall.cjs");

test("isGlobalInstall detects npm global install env", () => {
  assert.equal(isGlobalInstall({ npm_config_global: "true" }), true);
  assert.equal(isGlobalInstall({ npm_config_location: "global" }), true);
  assert.equal(isGlobalInstall({}), false);
});

test("shouldAutoSetup only enables global npm installs by default", () => {
  assert.equal(shouldAutoSetup({ npm_config_global: "true" }), true);
  assert.equal(shouldAutoSetup({ npm_config_location: "global" }), true);
  assert.equal(shouldAutoSetup({}), false);
});

test("shouldAutoSetup honors CI and explicit skip env flags", () => {
  assert.equal(shouldAutoSetup({ npm_config_global: "true", CI: "true" }), false);
  assert.equal(shouldAutoSetup({ npm_config_global: "true", CODEX_OBSERVATORY_SKIP_AUTO_SETUP: "1" }), false);
});
