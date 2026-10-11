'use strict';

const assert = require('node:assert/strict');
const crypto = require('node:crypto');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawn, spawnSync } = require('node:child_process');
const readline = require('node:readline');
const { once } = require('node:events');
const { after, before, test } = require('node:test');

const pluginRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(pluginRoot, '..', '..');
const serverPath = path.join(pluginRoot, 'server.js');
const {
  handleMessage,
  pythonCandidates,
  saveRepositoryConfiguration,
  searchEvidence,
  supportsPythonRuntime
} = require('../server.js');

let temporaryRoot;
let fixture;
let testPython;
let previousPluginData;

const childEnv = (extra = {}) => {
  const result = { PYTHONIOENCODING: 'utf-8', PYTHONUTF8: '1', PYTHONDONTWRITEBYTECODE: '1', ...extra };
  for (const name of ['PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'USERPROFILE']) {
    if (process.env[name]) result[name] = process.env[name];
  }
  Object.assign(result, extra);
  return result;
};

function runPython(script, input, args = []) {
  const result = spawnSync(testPython.command, [...testPython.prefixArgs, '-c', script, ...args], {
    input: input === undefined ? undefined : JSON.stringify(input),
    encoding: 'utf8', env: childEnv(), windowsHide: true, timeout: 15000, maxBuffer: 2 * 1024 * 1024
  });
  assert.ifError(result.error);
  assert.equal(result.status, 0, result.stderr || result.stdout);
  return result.stdout;
}

function fixtureBuilder(backend) {
  const builder = String.raw`
import json, sqlite3, sys
from pathlib import Path
root = Path(json.loads(sys.stdin.read())['root']).resolve()
sys.path.insert(0, str(root / 'docs' / 'knowledge_base'))
import personal_kb as kb
db_path = root / 'docs' / 'knowledge_base' / 'personal_index.sqlite3'
db = sqlite3.connect(db_path)
db.row_factory = sqlite3.Row
kb.init_db(db)
entries = [
 ('docs/topics/For Work/evidence.md', '# หลักฐาน\r\nพลังงาน energy มีตัวเลข 17\r\nขอบเขต remains a hypothesis\r\n', 'active'),
 ('docs/topics/other.md', '# Other\nscopemarker belongs elsewhere\n', 'active'),
 ('docs/topics/deleted.md', '# Removed\ndeletedmarker should be filtered\n', 'deleted'),
 ('docs/topics/stale.md', '# Old\nstaleMarker old indexed text\n', 'active'),
]
for rel, text, status in entries:
 path = root / rel
 path.parent.mkdir(parents=True, exist_ok=True)
 path.write_bytes(text.encode('utf-8'))
 source = kb.read_source(path)
 kb.upsert_source(db, source)
 if status != 'active':
  db.execute('UPDATE documents SET status=? WHERE source_path=?', (status, rel))
if ${JSON.stringify(backend)} == 'like':
 rows = db.execute('SELECT source_path,chunk_index,heading_path,text FROM chunks').fetchall()
 db.execute('DROP TABLE chunks_fts')
 db.execute('CREATE TABLE chunks_fts(source_path TEXT,chunk_index INTEGER,heading_path TEXT,text TEXT)')
 db.executemany('INSERT INTO chunks_fts VALUES (?,?,?,?)', [tuple(row) for row in rows])
 db.execute("UPDATE schema_meta SET value='like' WHERE key='search_backend'")
db.commit()
db.close()
(root / 'docs/topics/stale.md').write_text('# New\nsource has changed\n', encoding='utf-8')
print(json.dumps({'ready': True}))
`;
  return builder;
}

function createFixture(backend = 'fts5') {
  const root = fs.mkdtempSync(path.join(temporaryRoot, 'uet-repo-'));
  fs.writeFileSync(path.join(root, 'AGENTS.md'), 'Fixture repository marker\n');
  const kb = path.join(root, 'docs', 'knowledge_base');
  fs.mkdirSync(kb, { recursive: true });
  fs.copyFileSync(path.join(repoRoot, 'docs', 'knowledge_base', 'personal_kb.py'), path.join(kb, 'personal_kb.py'));
  runPython(fixtureBuilder(backend), { root });
  const sourcePath = path.join(root, 'docs', 'topics', 'For Work', 'evidence.md');
  const original = Buffer.from('# หลักฐาน\r\nพลังงาน energy มีตัวเลข 17\r\nขอบเขต remains a hypothesis\r\n', 'utf8');
  const normalizedChunk = Buffer.from('# หลักฐาน\nพลังงาน energy มีตัวเลข 17\nขอบเขต remains a hypothesis', 'utf8');
  return {
    root,
    dbPath: path.join(kb, 'personal_index.sqlite3'),
    live: { sourceHash: digest(original), chunkHash: digest(normalizedChunk), sourcePath }
  };
}

function digest(bytes) { return crypto.createHash('sha256').update(bytes).digest('hex'); }

before(() => {
  fs.mkdirSync(path.join(repoRoot, 'tmp'), { recursive: true });
  temporaryRoot = fs.mkdtempSync(path.join(repoRoot, 'tmp', 'uet-evidence-tests-'));
  testPython = pythonCandidates().find(supportsPythonRuntime);
  assert.ok(testPython, 'A local Python 3.10+ runtime with SQLite is required by the server.');
  fixture = createFixture();
  previousPluginData = process.env.PLUGIN_DATA;
  process.env.PLUGIN_DATA = path.join(temporaryRoot, 'plugin-data');
});

after(() => {
  if (previousPluginData === undefined) delete process.env.PLUGIN_DATA;
  else process.env.PLUGIN_DATA = previousPluginData;
  if (temporaryRoot) fs.rmSync(temporaryRoot, { recursive: true, force: true });
});

test('plugin manifests bind the local stdio server and contain no credentials or remote endpoint', () => {
  const marketplace = JSON.parse(fs.readFileSync(path.join(repoRoot, '.agents', 'plugins', 'marketplace.json'), 'utf8'));
  assert.equal(marketplace.name, 'uet-research-tools');
  assert.deepEqual(marketplace.plugins.map((entry) => [entry.name, entry.source.source, entry.source.path]), [
    ['uet-evidence', 'local', './plugins/uet-evidence']
  ]);

  const plugin = JSON.parse(fs.readFileSync(path.join(pluginRoot, 'plugin.json'), 'utf8'));
  const mcp = JSON.parse(fs.readFileSync(path.join(pluginRoot, 'mcp.json'), 'utf8'));
  assert.equal(plugin.name, 'uet-evidence');
  assert.equal(mcp.mcpServers['uet-evidence'].type, 'stdio');
  assert.equal(mcp.mcpServers['uet-evidence'].command, 'node');
  assert.deepEqual(mcp.mcpServers['uet-evidence'].args, ['${PLUGIN_ROOT}/server.js']);
  assert.equal(Object.hasOwn(mcp.mcpServers['uet-evidence'], 'env'), false);
  assert.equal(Object.hasOwn(mcp.mcpServers['uet-evidence'], 'url'), false);
});

test('configure_repository stores settings only in plugin data and does not change the index', () => {
  const beforeHash = digest(fs.readFileSync(fixture.dbPath));
  const result = saveRepositoryConfiguration(fixture.root);
  assert.equal(result.configured, true);
  assert.equal(result.index_schema, '3');
  assert.equal(result.access, 'read-only');
  assert.equal(fs.existsSync(path.join(process.env.PLUGIN_DATA, 'uet-evidence-settings.json')), true);
  assert.equal(digest(fs.readFileSync(fixture.dbPath)), beforeHash);
  assert.equal(fs.existsSync(path.join(fixture.root, 'uet-evidence-settings.json')), false);
});

test('search uses canonical BM25 retrieval and returns a compact packet with unknown state fields', () => {
  const beforeHash = digest(fs.readFileSync(fixture.dbPath));
  const result = searchEvidence({ query: 'energy', scope: ['docs/topics/For Work'], limit: 4 });
  assert.equal(result.schema_version, 1);
  assert.equal(result.lane, 'unknown');
  assert.equal(result.controlling_blocker, 'unknown');
  assert.equal(result.evidence.length, 1);
  const evidence = result.evidence[0];
  assert.equal(evidence.source_path, 'docs/topics/For Work/evidence.md');
  assert.equal(evidence.locator, 'docs/topics/For Work/evidence.md#L1-L3');
  assert.equal(evidence.source_hash, fixture.live.sourceHash);
  assert.equal(evidence.chunk_hash, fixture.live.chunkHash);
  assert.match(evidence.snippet, /พลังงาน energy/);
  assert.equal(Object.hasOwn(evidence, 'text'), false);
  assert.equal(digest(fs.readFileSync(fixture.dbPath)), beforeHash);
});

test('search filters deleted documents and scopes, and reports stale source hashes', () => {
  assert.equal(searchEvidence({ query: 'deletedmarker' }).evidence.length, 0);
  assert.equal(searchEvidence({ query: 'scopemarker', scope: ['docs/topics/For Work'] }).evidence.length, 0);
  const stale = searchEvidence({ query: 'staleMarker' });
  assert.equal(stale.evidence.length, 0);
  assert.deepEqual(stale.diagnostics, [{ source_path: 'docs/topics/stale.md', status: 'stale_or_unavailable' }]);
});

test('fallback search uses the canonical deterministic literal backend', () => {
  const likeFixture = createFixture('like');
  saveRepositoryConfiguration(likeFixture.root);
  const result = searchEvidence({ query: 'energy', scope: ['docs/topics/For Work'] });
  assert.equal(result.search_method, 'literal_like');
  assert.equal(result.evidence.length, 1);
  assert.equal(result.evidence[0].search_method, 'literal_like');
  saveRepositoryConfiguration(fixture.root);
});

test('setup selects the separate schema-3 pilot index when the standard index is legacy', () => {
  const fallbackFixture = createFixture();
  const pilotPath = path.join(fallbackFixture.root, 'tmp', 'research-foundation-pilot', 'after-corpus.sqlite3');
  fs.mkdirSync(path.dirname(pilotPath), { recursive: true });
  fs.copyFileSync(fallbackFixture.dbPath, pilotPath);
  fs.rmSync(fallbackFixture.dbPath);
  const createLegacy = String.raw`import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); c.execute('CREATE TABLE schema_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)'); c.execute("INSERT INTO schema_meta VALUES ('schema_version','2')"); c.commit(); c.close()`;
  runPython(createLegacy, undefined, [fallbackFixture.dbPath]);
  const before = [fallbackFixture.dbPath, pilotPath].map(file => digest(fs.readFileSync(file)));
  const result = saveRepositoryConfiguration(fallbackFixture.root);
  assert.equal(result.index_path, 'tmp/research-foundation-pilot/after-corpus.sqlite3');
  assert.equal(result.index_schema, '3');
  assert.deepEqual([fallbackFixture.dbPath, pilotPath].map(file => digest(fs.readFileSync(file))), before);
  saveRepositoryConfiguration(fixture.root);
});

test('fetch returns Thai source lines from CRLF after source/chunk hash verification', () => {
  const response = require('../server.js').fetchSource({
    source_path: 'docs/topics/For Work/evidence.md', line_start: 1, line_end: 3,
    expected_hash: fixture.live.sourceHash, expected_chunk_hash: fixture.live.chunkHash
  });
  assert.equal(response.source_path, 'docs/topics/For Work/evidence.md');
  assert.equal(response.locator, 'docs/topics/For Work/evidence.md#L1-L3');
  assert.equal(response.text, '# หลักฐาน\nพลังงาน energy มีตัวเลข 17\nขอบเขต remains a hypothesis');
  assert.throws(() => require('../server.js').fetchSource({
    source_path: 'docs/topics/For Work/evidence.md', line_start: 1, line_end: 3, expected_hash: '0'.repeat(64)
  }), /stale source/);
  assert.throws(() => require('../server.js').fetchSource({
    source_path: 'docs/topics/For Work/evidence.md', line_start: 1, line_end: 3,
    expected_hash: fixture.live.sourceHash, expected_chunk_hash: '0'.repeat(64)
  }), /stale chunk/);
});

test('fetch rejects traversal, raw/private files, binary sources, and oversized ranges', () => {
  const fetchSource = require('../server.js').fetchSource;
  assert.throws(() => fetchSource({ source_path: '../outside.md', line_start: 1, line_end: 1, expected_hash: fixture.live.sourceHash }), /outside|relative|subpath/i);
  const rawPath = path.join(fixture.root, 'docs', 'raw', 'secret.md');
  fs.mkdirSync(path.dirname(rawPath), { recursive: true });
  fs.writeFileSync(rawPath, 'private research notes\n');
  assert.throws(() => fetchSource({
    source_path: 'docs/raw/secret.md', line_start: 1, line_end: 1,
    expected_hash: digest(fs.readFileSync(rawPath))
  }), /outside public research scope|excluded/i);
  const longPath = path.join(fixture.root, 'docs', 'topics', 'long.txt');
  fs.writeFileSync(longPath, Array.from({ length: 251 }, (_, i) => `line ${i + 1}`).join('\n'), 'utf8');
  assert.throws(() => fetchSource({
    source_path: 'docs/topics/long.txt', line_start: 1, line_end: 251,
    expected_hash: digest(fs.readFileSync(longPath))
  }), /250 lines/);
  const binaryPath = path.join(fixture.root, 'docs', 'topics', 'diagram.png');
  fs.writeFileSync(binaryPath, Buffer.from([137, 80, 78, 71]));
  assert.throws(() => fetchSource({
    source_path: 'docs/topics/diagram.png', line_start: 1, line_end: 1,
    expected_hash: digest(fs.readFileSync(binaryPath))
  }), /Unsupported source type/);
});

test('legacy schema fails closed with rebuild guidance and does not rewrite the database', () => {
  const legacyRoot = fs.mkdtempSync(path.join(temporaryRoot, 'uet-legacy-'));
  fs.writeFileSync(path.join(legacyRoot, 'AGENTS.md'), 'Fixture\n');
  const kbDir = path.join(legacyRoot, 'docs', 'knowledge_base');
  fs.mkdirSync(kbDir, { recursive: true });
  fs.copyFileSync(path.join(repoRoot, 'docs', 'knowledge_base', 'personal_kb.py'), path.join(kbDir, 'personal_kb.py'));
  const dbPath = path.join(kbDir, 'personal_index.sqlite3');
  const createLegacy = String.raw`import sqlite3,sys; c=sqlite3.connect(sys.argv[1]); c.execute('CREATE TABLE schema_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL)'); c.execute("INSERT INTO schema_meta VALUES ('schema_version','2')"); c.commit(); c.close()`;
  runPython(createLegacy, undefined, [dbPath]);
  const beforeHash = digest(fs.readFileSync(dbPath));
  assert.throws(() => saveRepositoryConfiguration(legacyRoot, undefined, 'docs/knowledge_base/personal_index.sqlite3'), /Legacy index: rebuild explicitly/);
  assert.equal(digest(fs.readFileSync(dbPath)), beforeHash);
});

test('MCP handler exposes only setup, search, and fetch with correct read-only hints', () => {
  const initialized = handleMessage({ jsonrpc: '2.0', id: 1, method: 'initialize', params: { protocolVersion: '2025-03-26' } });
  assert.equal(initialized.result.protocolVersion, '2025-03-26');
  assert.match(initialized.result.instructions, /not scientific validation/);
  const tools = handleMessage({ jsonrpc: '2.0', id: 2, method: 'tools/list' }).result.tools;
  assert.deepEqual(tools.map(tool => tool.name), ['configure_repository', 'search_evidence', 'fetch_source']);
  assert.equal(tools.find(tool => tool.name === 'search_evidence').annotations.readOnlyHint, true);
  assert.equal(tools.find(tool => tool.name === 'fetch_source').annotations.readOnlyHint, true);
  assert.equal(handleMessage({ jsonrpc: '2.0', method: 'notifications/initialized' }), null);
});

test('stdio process exchanges newline JSON-RPC and performs configure then search', async () => {
  const dataDirectory = path.join(temporaryRoot, 'protocol-plugin-data');
  const child = spawn(process.execPath, [serverPath], { env: childEnv({ PLUGIN_DATA: dataDirectory }), stdio: ['pipe', 'pipe', 'pipe'] });
  const output = readline.createInterface({ input: child.stdout, crlfDelay: Infinity });
  const waiters = new Map();
  output.on('line', line => {
    let message;
    try { message = JSON.parse(line); } catch (error) {
      for (const waiter of waiters.values()) waiter.reject(error);
      return;
    }
    const waiter = waiters.get(message.id);
    if (waiter) { waiters.delete(message.id); waiter.resolve(message); }
  });
  function send(id, method, params = {}) {
    const response = new Promise((resolve, reject) => waiters.set(id, { resolve, reject }));
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', id, method, params }) + '\n');
    return response;
  }
  function notify(method, params = {}) {
    child.stdin.write(JSON.stringify({ jsonrpc: '2.0', method, params }) + '\n');
  }
  try {
    const init = await send(1, 'initialize', { protocolVersion: '2025-03-26', capabilities: {}, clientInfo: { name: 'test', version: '1' } });
    assert.equal(init.result.serverInfo.name, 'uet-evidence');
    notify('notifications/initialized');
    const listed = await send(2, 'tools/list');
    assert.equal(listed.result.tools.length, 3);
    const configured = await send(3, 'tools/call', { name: 'configure_repository', arguments: { repository_root: fixture.root } });
    assert.equal(configured.result.isError, false);
    const searched = await send(4, 'tools/call', { name: 'search_evidence', arguments: { query: 'energy' } });
    const packet = JSON.parse(searched.result.content[0].text);
    assert.equal(packet.evidence.length, 1);
    assert.equal(packet.lane, 'unknown');
    assert.equal(searched.result.isError, false);
  } finally {
    child.stdin.end();
    await once(child, 'exit');
    output.close();
  }
});
