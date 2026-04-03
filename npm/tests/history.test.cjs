const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");

const HISTORY_MODULE_PATH = "../../lib/history.cjs";
const {
  SYNTHETIC_HISTORY_HEADER,
  buildPromptRowsFromSessionFile,
  resolveCodexHome,
  rewriteNpmToolScripts,
  syncPromptHistory
} = require(HISTORY_MODULE_PATH);

function makeTempDir(t) {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "codex-observatory-"));
  t.after(() => fs.rmSync(tempDir, { recursive: true, force: true }));
  return tempDir;
}

function writeJsonl(filePath, rows) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
  fs.writeFileSync(filePath, `${rows.map((row) => JSON.stringify(row)).join("\n")}\n`, "utf8");
}

function readSyntheticHistoryRows(historyPath) {
  return fs
    .readFileSync(historyPath, "utf8")
    .trim()
    .split(/\r?\n/)
    .filter((line) => line.trim() && !line.startsWith("#"))
    .map((line) => JSON.parse(line));
}

function loadHistoryModule() {
  delete require.cache[require.resolve(HISTORY_MODULE_PATH)];
  return require(HISTORY_MODULE_PATH);
}

test("syncPromptHistory backfills history.jsonl from session logs", async (t) => {
  const tempDir = makeTempDir(t);
  const codexHome = path.join(tempDir, ".codex");
  const sessionFile = path.join(codexHome, "sessions", "2026", "03", "19", "session-a.jsonl");

  writeJsonl(sessionFile, [
    { timestamp: "2026-03-19T00:59:00Z", type: "session_meta", payload: { id: "session-a" } },
    {
      timestamp: "2026-03-19T00:59:30Z",
      type: "response_item",
      payload: {
        type: "message",
        role: "user",
        content: [{ type: "input_text", text: "<environment_context>\n  <cwd>/tmp</cwd>\n</environment_context>" }]
      }
    },
    {
      timestamp: "2026-03-19T01:00:00Z",
      type: "response_item",
      payload: {
        type: "message",
        role: "user",
        content: [{ type: "input_text", text: "prompt one" }]
      }
    },
    { timestamp: "2026-03-19T01:00:00Z", type: "event_msg", payload: { type: "user_message", message: "prompt one" } },
    { timestamp: "2026-03-19T01:05:00Z", type: "event_msg", payload: { type: "user_message", message: "prompt two" } }
  ]);

  const result = await syncPromptHistory(codexHome);
  assert.equal(result.updated, true);
  assert.equal(result.created, true);
  assert.equal(result.rowCount, 2);

  const historyLines = fs.readFileSync(path.join(codexHome, "history.jsonl"), "utf8").trim().split(/\r?\n/);
  assert.equal(historyLines[0], SYNTHETIC_HISTORY_HEADER);
  assert.equal(historyLines[1], "# max-session-file-bytes=268435456");
  const rows = historyLines.slice(2).map((line) => JSON.parse(line));
  assert.deepEqual(
    rows.map((row) => row.session_id),
    ["session-a", "session-a"]
  );
  assert.deepEqual(
    rows.map((row) => row.ts),
    [Math.floor(Date.parse("2026-03-19T01:00:00Z") / 1000), Math.floor(Date.parse("2026-03-19T01:05:00Z") / 1000)]
  );
});

test("buildPromptRowsFromSessionFile falls back to response_item user messages", (t) => {
  const tempDir = makeTempDir(t);
  const sessionFile = path.join(tempDir, "session-fallback.jsonl");

  writeJsonl(sessionFile, [
    { timestamp: "2026-03-19T00:59:00Z", type: "session_meta", payload: { id: "session-fallback" } },
    {
      timestamp: "2026-03-19T00:59:30Z",
      type: "response_item",
      payload: {
        type: "message",
        role: "user",
        content: [{ type: "input_text", text: "<environment_context>\n  <cwd>/tmp</cwd>\n</environment_context>" }]
      }
    },
    {
      timestamp: "2026-03-19T01:00:00Z",
      type: "response_item",
      payload: {
        type: "message",
        role: "user",
        content: [{ type: "input_text", text: "fallback prompt" }]
      }
    }
  ]);

  const rows = buildPromptRowsFromSessionFile(sessionFile);
  assert.equal(rows.length, 1);
  assert.equal(rows[0].session_id, "session-fallback");
  assert.equal(rows[0].ts, Math.floor(Date.parse("2026-03-19T01:00:00Z") / 1000));
});

test("syncPromptHistory rebuilds synthetic history when the size limit changes", async (t) => {
  const tempDir = makeTempDir(t);
  const codexHome = path.join(tempDir, ".codex");
  const sessionsDir = path.join(codexHome, "sessions", "2026", "04", "01");
  const historyPath = path.join(codexHome, "history.jsonl");
  const originalMaxSessionFileBytes = process.env.CODEX_OBSERVATORY_MAX_SESSION_FILE_BYTES;

  t.after(() => {
    if (typeof originalMaxSessionFileBytes === "string") {
      process.env.CODEX_OBSERVATORY_MAX_SESSION_FILE_BYTES = originalMaxSessionFileBytes;
    } else {
      delete process.env.CODEX_OBSERVATORY_MAX_SESSION_FILE_BYTES;
    }
    delete require.cache[require.resolve(HISTORY_MODULE_PATH)];
  });

  writeJsonl(path.join(sessionsDir, "small.jsonl"), [
    { timestamp: "2026-04-01T00:00:00Z", type: "session_meta", payload: { id: "small" } },
    { timestamp: "2026-04-01T00:01:00Z", type: "event_msg", payload: { type: "user_message", message: "small prompt" } }
  ]);

  writeJsonl(path.join(sessionsDir, "large.jsonl"), [
    { timestamp: "2026-04-01T00:00:00Z", type: "session_meta", payload: { id: "large" } },
    {
      timestamp: "2026-04-01T00:02:00Z",
      type: "event_msg",
      payload: { type: "user_message", message: `large prompt ${"x".repeat(1024)}` }
    }
  ]);

  const sharedMtime = new Date("2026-04-01T00:05:00Z");
  fs.utimesSync(path.join(sessionsDir, "small.jsonl"), sharedMtime, sharedMtime);
  fs.utimesSync(path.join(sessionsDir, "large.jsonl"), sharedMtime, sharedMtime);

  process.env.CODEX_OBSERVATORY_MAX_SESSION_FILE_BYTES = "300";
  let historyModule = loadHistoryModule();
  let result = await historyModule.syncPromptHistory(codexHome);
  assert.equal(result.updated, true);
  assert.equal(result.rowCount, 1);
  assert.deepEqual(
    readSyntheticHistoryRows(historyPath).map((row) => row.session_id),
    ["small"]
  );

  process.env.CODEX_OBSERVATORY_MAX_SESSION_FILE_BYTES = "0";
  historyModule = loadHistoryModule();
  result = await historyModule.syncPromptHistory(codexHome);
  assert.equal(result.updated, true);
  assert.equal(result.rowCount, 2);
  assert.deepEqual(
    readSyntheticHistoryRows(historyPath).map((row) => row.session_id).sort(),
    ["large", "small"]
  );
});

test("resolveCodexHome finds nested session-only .codex directories", () => {
  const tempDir = fs.mkdtempSync(path.join(os.tmpdir(), "codex-observatory-"));
  try {
    fs.mkdirSync(path.join(tempDir, ".codex", "sessions"), { recursive: true });
    assert.equal(resolveCodexHome(["--codex-home", tempDir], {}, tempDir), path.join(tempDir, ".codex"));
  } finally {
    fs.rmSync(tempDir, { recursive: true, force: true });
  }
});

test("rewriteNpmToolScripts points helper tools back to the npm wrapper", async (t) => {
  const tempDir = makeTempDir(t);
  const codexHome = path.join(tempDir, ".codex");

  const rewritten = await rewriteNpmToolScripts(codexHome, {
    nodePath: "/usr/local/bin/node",
    entryScriptPath: "/tmp/codex-observatory/bin/codex-observatory.cjs"
  });

  const ps1Content = fs.readFileSync(rewritten.ps1Path, "utf8");
  const shContent = fs.readFileSync(rewritten.shPath, "utf8");
  assert.match(ps1Content, /codex-observatory\.cjs/);
  assert.match(ps1Content, /node/);
  assert.match(shContent, /codex-observatory\.cjs/);
  assert.match(shContent, /node/);
});
