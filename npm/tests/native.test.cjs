const test = require("node:test");
const assert = require("node:assert/strict");

const { releaseTag, releaseUrl } = require("../../lib/native.cjs");
const { detectPlatform } = require("../../lib/platform.cjs");

test("releaseTag matches the package version", () => {
  assert.match(releaseTag(), /^v\d+\.\d+\.\d+$/);
});

test("releaseUrl points at the release asset for a known platform", () => {
  const url = releaseUrl(detectPlatform("linux", "x64"));
  assert.match(url, /releases\/download\/v\d+\.\d+\.\d+\/codex-observatory-linux-x64$/);
});

test("releaseUrl points at the release asset for new arm64 platforms", () => {
  const linuxArmUrl = releaseUrl(detectPlatform("linux", "arm64"));
  const windowsArmUrl = releaseUrl(detectPlatform("win32", "arm64"));
  assert.match(linuxArmUrl, /releases\/download\/v\d+\.\d+\.\d+\/codex-observatory-linux-arm64$/);
  assert.match(windowsArmUrl, /releases\/download\/v\d+\.\d+\.\d+\/codex-observatory-windows-arm64\.exe$/);
});
