'use strict';

// Local stdio MCP adapter; evidence handling delegates to the repository's canonical Python module.
const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const readline = require('node:readline');

const SERVER_VERSION = '0.1.0';
const PROTOCOL_FALLBACK = '2024-11-05';
const SUPPORTED_PROTOCOLS = new Set(['2024-11-05', '2025-03-26', '2025-06-18']);
const INDEXER_RELATIVE_PATH = path.join('docs', 'knowledge_base', 'personal_kb.py');
const DEFAULT_INDEX_PATH = 'docs/knowledge_base/personal_index.sqlite3';
const PILOT_INDEX_PATH = 'tmp/research-foundation-pilot/after-corpus.sqlite3';
const ALLOWED_INDEX_PATHS = new Set([DEFAULT_INDEX_PATH, PILOT_INDEX_PATH]);
const BRIDGE_PATH = path.join(__dirname, 'bridge.py');
const MAX_QUERY_CHARS = 1000;
const MAX_SCOPE_ITEMS = 12;
const MAX_LIMIT = 8;
const MAX_SNIPPET_CHARS = 800;

class ToolError extends Error {}

function pythonCandidates(override) {
  const candidates = [];
  const seen = new Set();
  const add = (command, prefixArgs = []) => {
    if (!command) return;
    const key = `${command.toLowerCase()}\0${prefixArgs.join('\0')}`;
    if (!seen.has(key)) { seen.add(key); candidates.push({ command, prefixArgs }); }
  };
  if (override) {
    if (typeof override !== 'string' || !path.isAbsolute(override.trim())) {
      throw new ToolError('python_executable must be an absolute path to Python 3.');
    }
    add(path.resolve(override.trim()));
    return candidates;
  }
  if (process.env.UET_PYTHON && path.isAbsolute(process.env.UET_PYTHON)) add(path.resolve(process.env.UET_PYTHON));
  const userProfile = process.env.USERPROFILE;
  if (userProfile) {
    add(path.join(userProfile, '.cache', 'codex-runtimes', 'codex-primary-runtime', 'dependencies', 'python', 'python.exe'));
  }
  add('python');
  add('python3');
  add('py', ['-3']);
  return candidates;
}

function childEnvironment() {
  const result = { PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1', PYTHONDONTWRITEBYTECODE: '1' };
  for (const name of ['PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'LOCALAPPDATA', 'APPDATA', 'USERPROFILE']) {
    if (process.env[name]) result[name] = process.env[name];
  }
  return result;
}

function invokeBridge(candidate, request) {
  let result;
  try {
    result = spawnSync(candidate.command, [...candidate.prefixArgs, BRIDGE_PATH], {
      input: JSON.stringify(request),
      encoding: 'utf8',
      env: childEnvironment(),
      windowsHide: true,
      timeout: 20000,
      maxBuffer: 1024 * 1024
    });
  } catch {
    throw new ToolError('Could not start the local Python evidence bridge.');
  }
  if (result.error) {
    if (result.error.code === 'ETIMEDOUT') throw new ToolError('Local evidence search timed out; check the index and try a narrower question.');
    throw new ToolError('Could not start the local Python evidence bridge.');
  }
  let envelope;
  try { envelope = JSON.parse((result.stdout || '').trim()); }
  catch { throw new ToolError('Local Python bridge returned an invalid response. Check the installed Python runtime.'); }
  if (!envelope || envelope.ok !== true) {
    throw new ToolError(typeof envelope.error === 'string' ? envelope.error : 'Local evidence operation failed.');
  }
  return envelope.value;
}

function supportsPythonRuntime(candidate) {
  const check = 'import sqlite3,sys; assert sys.version_info >= (3,10); c=sqlite3.connect(\':memory:\'); c.execute(\'SELECT 1\'); c.close(); print(\'ok\')';
  try {
    const result = spawnSync(candidate.command, [...candidate.prefixArgs, '-c', check], {
      encoding: 'utf8', env: childEnvironment(), windowsHide: true, timeout: 10000, maxBuffer: 1024 * 1024
    });
    return !result.error && result.status === 0 && (result.stdout || '').trim() === 'ok';
  } catch {
    return false;
  }
}

function isRepositoryRoot(repositoryRoot) {
  if (typeof repositoryRoot !== 'string' || !repositoryRoot.trim() || !path.isAbsolute(repositoryRoot.trim())) {
    throw new ToolError('repository_root must be an absolute path to the local UET repository.');
  }
  let root;
  try { root = fs.realpathSync(path.resolve(repositoryRoot.trim())); }
  catch { throw new ToolError('Repository folder is missing or unavailable.'); }
  if (!fs.statSync(root).isDirectory()) throw new ToolError('Repository path must point to a folder.');
  if (!fs.existsSync(path.join(root, 'AGENTS.md')) || !fs.existsSync(path.join(root, INDEXER_RELATIVE_PATH))) {
    throw new ToolError('This folder does not look like the UET repository: AGENTS.md and docs/knowledge_base/personal_kb.py are required.');
  }
  return root;
}

function resolveIndexPath(root, indexPath) {
  if (!ALLOWED_INDEX_PATHS.has(indexPath)) {
    throw new ToolError('index_path must be either the standard UET index or the local research-foundation pilot index.');
  }
  const candidate = path.resolve(root, ...indexPath.split('/'));
  let real;
  try { real = fs.realpathSync(candidate); }
  catch { throw new ToolError(`Evidence index is missing at ${indexPath}. This plugin never ingests or rebuilds it.`); }
  const relative = path.relative(root, real);
  if (path.isAbsolute(relative) || relative === '..' || relative.startsWith(`..${path.sep}`)) {
    throw new ToolError('Evidence index symlink resolves outside the configured repository.');
  }
  if (!fs.statSync(real).isFile()) throw new ToolError('Evidence index path must be a SQLite file.');
  return real;
}

function pluginDataDirectory() {
  const configured = process.env.PLUGIN_DATA;
  if (!configured || !path.isAbsolute(configured)) {
    throw new ToolError('PLUGIN_DATA is not available. Restart or reinstall the local plugin from ChatGPT Desktop.');
  }
  return path.resolve(configured);
}

function settingsFile() {
  return path.join(pluginDataDirectory(), 'uet-evidence-settings.json');
}

function saveRepositoryConfiguration(repositoryRoot, pythonOverride, requestedIndexPath) {
  const root = isRepositoryRoot(repositoryRoot);
  if (requestedIndexPath !== undefined && !ALLOWED_INDEX_PATHS.has(requestedIndexPath)) {
    throw new ToolError('index_path must be either docs/knowledge_base/personal_index.sqlite3 or tmp/research-foundation-pilot/after-corpus.sqlite3.');
  }
  const candidates = pythonCandidates(pythonOverride);
  const compatible = candidates.filter(supportsPythonRuntime);
  if (!compatible.length) {
    throw new ToolError('No compatible Python 3.10+ runtime with SQLite was found. Install Python 3 or call setup again with python_executable set to its absolute path.');
  }
  let selected;
  let probe;
  let selectedIndexPath;
  let lastIndexError;
  let missingFts5 = false;
  const indexChoices = requestedIndexPath ? [requestedIndexPath] : [DEFAULT_INDEX_PATH, PILOT_INDEX_PATH];
  for (const indexPath of indexChoices) {
    try { resolveIndexPath(root, indexPath); }
    catch (error) { if (!lastIndexError) lastIndexError = error; continue; }
    for (const candidate of compatible) {
      try {
        probe = invokeBridge(candidate, { operation: 'probe', repository_root: root, index_path: indexPath });
        selected = candidate;
        selectedIndexPath = indexPath;
        break;
      } catch (error) {
        if (/no such module: fts5|fts5.*not available/i.test(error.message)) {
          missingFts5 = true;
          continue;
        }
        lastIndexError = error;
        // A different allowed local index may be schema-3 even when the standard one is legacy.
        break;
      }
    }
    if (selected) break;
  }
  if (!selected) {
    if (lastIndexError) throw lastIndexError;
    throw new ToolError(missingFts5
      ? 'This index uses FTS5, but the available Python SQLite runtimes cannot read FTS5 indexes. Install Python with SQLite FTS5 and configure it explicitly.'
      : 'No supported schema-3 evidence index was found. Build a new schema-3 index explicitly; this plugin will not rebuild the live index.');
  }
  const directory = pluginDataDirectory();
  fs.mkdirSync(directory, { recursive: true });
  const destination = path.join(directory, 'uet-evidence-settings.json');
  const temporary = `${destination}.${process.pid}.tmp`;
  const body = JSON.stringify({
    version: 1,
    repository_root: root,
    index_path: selectedIndexPath,
    python_command: selected.command,
    python_prefix_args: selected.prefixArgs
  }, null, 2) + '\n';
  try {
    fs.writeFileSync(temporary, body, { encoding: 'utf8', mode: 0o600, flag: 'wx' });
    fs.renameSync(temporary, destination);
  } catch {
    try { fs.rmSync(temporary, { force: true }); } catch { /* best-effort cleanup inside plugin data */ }
    throw new ToolError('Could not save settings in the plugin-local data directory.');
  }
  return {
    configured: true,
    repository: path.basename(root),
    index_schema: String(probe.index_schema),
    search_backend: probe.search_backend,
    index_path: selectedIndexPath,
    python_runtime: 'available',
    access: 'read-only',
    settings_location: 'plugin-local data; no repository or index files were changed'
  };
}

function loadRepositoryConfiguration() {
  let settings;
  try { settings = JSON.parse(fs.readFileSync(settingsFile(), 'utf8')); }
  catch { throw new ToolError('Repository is not configured. Call configure_repository once with the absolute path to the local UET repository.'); }
  if (!settings || settings.version !== 1 || typeof settings.repository_root !== 'string' ||
      !ALLOWED_INDEX_PATHS.has(settings.index_path) || typeof settings.python_command !== 'string' || !Array.isArray(settings.python_prefix_args)) {
    throw new ToolError('Saved plugin settings are invalid. Call configure_repository again.');
  }
  const root = isRepositoryRoot(settings.repository_root);
  resolveIndexPath(root, settings.index_path);
  return { root, indexPath: settings.index_path, candidate: { command: settings.python_command, prefixArgs: settings.python_prefix_args } };
}

function runConfiguredBridge(settings, request) {
  return invokeBridge(settings.candidate, { ...request, repository_root: settings.root, index_path: settings.indexPath });
}

function searchEvidence(args) {
  if (!args || typeof args.query !== 'string' || !args.query.trim()) throw new ToolError('query must be a nonempty string.');
  if (args.query.length > MAX_QUERY_CHARS) throw new ToolError(`query may not exceed ${MAX_QUERY_CHARS} characters.`);
  const limit = args.limit === undefined ? 6 : args.limit;
  const snippetChars = args.snippet_chars === undefined ? 360 : args.snippet_chars;
  const scope = args.scope === undefined ? [] : args.scope;
  if (!Number.isInteger(limit) || limit < 1 || limit > MAX_LIMIT) throw new ToolError(`limit must be an integer from 1 to ${MAX_LIMIT}.`);
  if (!Number.isInteger(snippetChars) || snippetChars < 1 || snippetChars > MAX_SNIPPET_CHARS) {
    throw new ToolError(`snippet_chars must be an integer from 1 to ${MAX_SNIPPET_CHARS}.`);
  }
  if (!Array.isArray(scope) || scope.some(item => typeof item !== 'string')) throw new ToolError('scope must be an array of repository-relative paths.');
  const settings = loadRepositoryConfiguration();
  return runConfiguredBridge(settings, { operation: 'search', query: args.query, limit, snippet_chars: snippetChars, scope });
}

function fetchSource(args) {
  if (!args || typeof args.source_path !== 'string') throw new ToolError('source_path is required.');
  if (!Number.isInteger(args.line_start) || !Number.isInteger(args.line_end)) throw new ToolError('line_start and line_end must be integers.');
  if (typeof args.expected_hash !== 'string' || !/^[0-9a-f]{64}$/.test(args.expected_hash)) {
    throw new ToolError('expected_hash must be the 64-character SHA256 from search_evidence.');
  }
  if (args.expected_chunk_hash !== undefined && (typeof args.expected_chunk_hash !== 'string' || !/^[0-9a-f]{64}$/.test(args.expected_chunk_hash))) {
    throw new ToolError('expected_chunk_hash must be a 64-character SHA256 when supplied.');
  }
  const settings = loadRepositoryConfiguration();
  return runConfiguredBridge(settings, {
    operation: 'fetch',
    source_path: args.source_path,
    line_start: args.line_start,
    line_end: args.line_end,
    expected_hash: args.expected_hash,
    expected_chunk_hash: args.expected_chunk_hash
  });
}

const TOOL_DEFINITIONS = [
  {
    name: 'configure_repository',
    description: 'One-time local setup. Validate the schema-3 UET index with a compatible local Python runtime and save the repository path in this plugin’s private local data. Does not write to the repository or index.',
    inputSchema: {
      type: 'object',
      properties: {
        repository_root: { type: 'string', description: 'Absolute path to the local UET repository folder.' },
        python_executable: { type: 'string', description: 'Optional absolute path to Python 3 if automatic detection does not find the compatible runtime.' },
        index_path: { type: 'string', enum: [DEFAULT_INDEX_PATH, PILOT_INDEX_PATH], description: 'Optional explicit index path; when omitted, use the standard index if valid, otherwise the local schema-3 pilot index.' }
      },
      required: ['repository_root'],
      additionalProperties: false
    },
    annotations: { readOnlyHint: false, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  },
  {
    name: 'search_evidence',
    description: 'Read-only BM25 or deterministic literal search by the repository’s canonical personal_kb.py. Verifies source and chunk hashes against original files, excludes stale/private/raw material, returns short snippets and line locators, and leaves lane and controlling blocker unknown.',
    inputSchema: {
      type: 'object',
      properties: {
        query: { type: 'string', minLength: 1, maxLength: MAX_QUERY_CHARS },
        scope: { type: 'array', maxItems: MAX_SCOPE_ITEMS, items: { type: 'string' }, description: 'Optional repository-relative file or directory paths.' },
        limit: { type: 'integer', minimum: 1, maximum: MAX_LIMIT, default: 6 },
        snippet_chars: { type: 'integer', minimum: 1, maximum: MAX_SNIPPET_CHARS, default: 360 }
      },
      required: ['query'],
      additionalProperties: false
    },
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  },
  {
    name: 'fetch_source',
    description: 'Read-only retrieval of up to 250 original source lines after checking the expected SHA256. Use the repository-relative path, line range, and source_hash returned by search_evidence. Raw/private/secret/config paths are rejected.',
    inputSchema: {
      type: 'object',
      properties: {
        source_path: { type: 'string', description: 'Repository-relative path returned by search_evidence.' },
        line_start: { type: 'integer', minimum: 1 },
        line_end: { type: 'integer', minimum: 1, maximum: 250 },
        expected_hash: { type: 'string', pattern: '^[0-9a-f]{64}$' },
        expected_chunk_hash: { type: 'string', pattern: '^[0-9a-f]{64}$', description: 'Optional; use only with the exact full chunk line range.' }
      },
      required: ['source_path', 'line_start', 'line_end', 'expected_hash'],
      additionalProperties: false
    },
    annotations: { readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false }
  }
];

function jsonResult(id, result) { return { jsonrpc: '2.0', id, result }; }
function jsonError(id, code, message) { return { jsonrpc: '2.0', id, error: { code, message } }; }
function asToolResult(value) { return { content: [{ type: 'text', text: JSON.stringify(value) }], isError: false }; }
function asToolError(error) { return { content: [{ type: 'text', text: JSON.stringify({ error: error.message || 'Tool failed.' }) }], isError: true }; }

function handleMessage(message) {
  if (!message || typeof message !== 'object' || message.jsonrpc !== '2.0' || typeof message.method !== 'string') {
    const id = message && typeof message === 'object' && Object.hasOwn(message, 'id') ? message.id : null;
    return jsonError(id, -32600, 'Invalid Request');
  }
  const hasId = Object.hasOwn(message, 'id');
  if (!hasId && message.method.startsWith('notifications/')) return null;
  if (!hasId) return jsonError(null, -32600, 'Invalid Request');
  if (message.method === 'initialize') {
    const requested = message.params && message.params.protocolVersion;
    return jsonResult(message.id, {
      protocolVersion: SUPPORTED_PROTOCOLS.has(requested) ? requested : PROTOCOL_FALLBACK,
      capabilities: { tools: { listChanged: false } },
      serverInfo: { name: 'uet-evidence', version: SERVER_VERSION },
      instructions: 'Use search_evidence to locate public-scope UET sources, then fetch_source to verify exact original lines before citing. Search results are evidence candidates, not scientific validation. Never infer theory status, lane, blocker, or claim strength from retrieval scores; those remain unknown unless the cited source establishes them. This server cannot edit files or ingest data.'
    });
  }
  if (message.method === 'ping') return jsonResult(message.id, {});
  if (message.method === 'tools/list') return jsonResult(message.id, { tools: TOOL_DEFINITIONS });
  if (message.method === 'tools/call') {
    try {
      const params = message.params || {};
      const args = params.arguments || {};
      let value;
      if (params.name === 'configure_repository') value = saveRepositoryConfiguration(args.repository_root, args.python_executable, args.index_path);
      else if (params.name === 'search_evidence') value = searchEvidence(args);
      else if (params.name === 'fetch_source') value = fetchSource(args);
      else return jsonResult(message.id, asToolError(new ToolError(`Unknown tool: ${String(params.name || '')}`)));
      return jsonResult(message.id, asToolResult(value));
    } catch (error) {
      return jsonResult(message.id, asToolError(error instanceof ToolError ? error : new ToolError('Local evidence operation failed. Check the repository index and plugin settings.')));
    }
  }
  if (!hasId) return null;
  return jsonError(message.id, -32601, 'Method not found');
}

function runStdio() {
  const input = readline.createInterface({ input: process.stdin, crlfDelay: Infinity, terminal: false });
  input.on('line', line => {
    let message;
    try { message = JSON.parse(line); }
    catch { process.stdout.write(`${JSON.stringify(jsonError(null, -32700, 'Parse error'))}\n`); return; }
    const response = handleMessage(message);
    if (response !== null) process.stdout.write(`${JSON.stringify(response)}\n`);
  });
}

if (require.main === module) runStdio();

module.exports = {
  fetchSource,
  handleMessage,
  invokeBridge,
  pythonCandidates,
  saveRepositoryConfiguration,
  searchEvidence,
  supportsPythonRuntime
};
