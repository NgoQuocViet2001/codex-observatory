const fs = require("node:fs");
const fsp = require("node:fs/promises");
const https = require("node:https");
const path = require("node:path");

const packageJson = require("../../package.json");
const { detectPlatform } = require("./platform.cjs");

const REPO_OWNER = "NgoQuocViet2001";
const REPO_NAME = "codex-observatory";

function releaseTag() {
  return `v${packageJson.version}`;
}

function binaryDir() {
  return path.join(__dirname, "..", "native");
}

function binaryPath(platformInfo = detectPlatform()) {
  if (!platformInfo) {
    return null;
  }
  return path.join(binaryDir(), platformInfo.binaryName);
}

function releaseUrl(platformInfo = detectPlatform()) {
  if (!platformInfo) {
    return null;
  }
  if (process.env.CODEX_OBSERVATORY_BINARY_URL) {
    return process.env.CODEX_OBSERVATORY_BINARY_URL;
  }
  return `https://github.com/${REPO_OWNER}/${REPO_NAME}/releases/download/${releaseTag()}/${platformInfo.assetName}`;
}

function fallbackHelp() {
  return [
    "Prebuilt binaries are available for Windows x64, macOS Intel, macOS Apple Silicon, and Linux x64.",
    "Fallback options:",
    `  1. Download the matching asset from https://github.com/${REPO_OWNER}/${REPO_NAME}/releases`,
    `  2. Install from source with Python: python -m pip install git+https://github.com/${REPO_OWNER}/${REPO_NAME}.git`
  ].join("\n");
}

function downloadFile(url, destination) {
  return new Promise((resolve, reject) => {
    const request = https.get(
      url,
      {
        headers: {
          "User-Agent": "codex-observatory/npm"
        }
      },
      (response) => {
        if (response.statusCode && response.statusCode >= 300 && response.statusCode < 400 && response.headers.location) {
          response.resume();
          downloadFile(response.headers.location, destination).then(resolve, reject);
          return;
        }

        if (response.statusCode !== 200) {
          response.resume();
          reject(new Error(`Download failed with HTTP ${response.statusCode}: ${url}`));
          return;
        }

        const file = fs.createWriteStream(destination);
        response.pipe(file);
        file.on("finish", () => {
          file.close(resolve);
        });
        file.on("error", (error) => {
          file.close(() => reject(error));
        });
      }
    );

    request.on("error", reject);
  });
}

async function ensureBinary({ quiet = false } = {}) {
  const platformInfo = detectPlatform();
  if (!platformInfo) {
    throw new Error(`Unsupported platform: ${process.platform} ${process.arch}\n${fallbackHelp()}`);
  }

  const targetPath = binaryPath(platformInfo);
  if (targetPath && fs.existsSync(targetPath)) {
    return targetPath;
  }

  await fsp.mkdir(binaryDir(), { recursive: true });
  const sourceUrl = releaseUrl(platformInfo);
  if (!quiet) {
    process.stderr.write(`[codex-observatory] Downloading ${platformInfo.label} binary from ${sourceUrl}\n`);
  }
  await downloadFile(sourceUrl, targetPath);

  if (process.platform !== "win32") {
    await fsp.chmod(targetPath, 0o755);
  }

  return targetPath;
}

module.exports = {
  binaryPath,
  ensureBinary,
  fallbackHelp,
  releaseTag,
  releaseUrl
};
