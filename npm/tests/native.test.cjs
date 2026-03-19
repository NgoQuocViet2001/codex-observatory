const test = require("node:test");
const assert = require("node:assert/strict");

const { releaseTag, releaseUrl } = require("../lib/native.cjs");
const { detectPlatform } = require("../lib/platform.cjs");

test("releaseTag matches the package version", () => {
  assert.match(releaseTag(), /^v\d+\.\d+\.\d+$/);
});

test("releaseUrl points at the release asset for a known platform", () => {
  const url = releaseUrl(detectPlatform("linux", "x64"));
  assert.match(url, /releases\/download\/v\d+\.\d+\.\d+\/codex-observatory-linux-x64$/);
});
