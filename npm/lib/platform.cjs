const PLATFORM_MATRIX = {
  "win32:x64": {
    assetName: "codex-observatory-windows-x64.exe",
    binaryName: "codex-observatory.exe",
    label: "Windows x64"
  },
  "darwin:x64": {
    assetName: "codex-observatory-macos-x64",
    binaryName: "codex-observatory",
    label: "macOS Intel"
  },
  "darwin:arm64": {
    assetName: "codex-observatory-macos-arm64",
    binaryName: "codex-observatory",
    label: "macOS Apple Silicon"
  },
  "linux:x64": {
    assetName: "codex-observatory-linux-x64",
    binaryName: "codex-observatory",
    label: "Linux x64"
  }
};

function detectPlatform(platform = process.platform, arch = process.arch) {
  return PLATFORM_MATRIX[`${platform}:${arch}`] || null;
}

module.exports = {
  detectPlatform
};
