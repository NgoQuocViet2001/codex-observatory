const test = require("node:test");
const assert = require("node:assert/strict");

const { detectPlatform } = require("../../lib/platform.cjs");

test("detectPlatform maps supported targets", () => {
  assert.equal(detectPlatform("win32", "x64").assetName, "codex-observatory-windows-x64.exe");
  assert.equal(detectPlatform("win32", "arm64").assetName, "codex-observatory-windows-arm64.exe");
  assert.equal(detectPlatform("darwin", "arm64").assetName, "codex-observatory-macos-arm64");
  assert.equal(detectPlatform("linux", "x64").assetName, "codex-observatory-linux-x64");
  assert.equal(detectPlatform("linux", "arm64").assetName, "codex-observatory-linux-arm64");
});

test("detectPlatform returns null for unsupported targets", () => {
  assert.equal(detectPlatform("freebsd", "x64"), null);
  assert.equal(detectPlatform("linux", "ppc64"), null);
});
