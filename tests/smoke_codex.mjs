// Optional native acceptance check. It never uses the operator's Codex home.
import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { cpSync, mkdirSync, mkdtempSync, readFileSync, readdirSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join, resolve } from 'node:path';
import { createInterface } from 'node:readline';
import { once } from 'node:events';

const input = process.argv.slice(2);
assert(input.length > 0, 'Pass one or more trusted plugin checkout roots');
const root = mkdtempSync(join(tmpdir(), 'pmcro-codex-smoke-'));
const home = join(root, 'home');
const codex = join(home, '.codex');
let server;
let exited;
let timer;
try {
  for (const folder of [codex, join(root, '.agents', 'plugins'), join(root, 'plugins')]) {
    mkdirSync(folder, { recursive: true, mode: 0o700 });
  }
  const marketplacePath = join(root, '.agents', 'plugins', 'marketplace.json');
  const entries = new Map();
  for (const checkout of input.map(path => resolve(path))) {
    const manifest = JSON.parse(readFileSync(join(checkout, 'plugin.json')));
    const name = manifest.name;
    assert(typeof name === 'string' && /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name) && !entries.has(name),
      'Each checkout must have a unique PMCR-O plugin name');
    const target = join(root, 'plugins', name);
    mkdirSync(target);
    for (const entry of ['plugin.json', '.codex-plugin', 'skills']) {
      cpSync(join(checkout, entry), join(target, entry), { recursive: true });
    }
    entries.set(name, readdirSync(join(target, 'skills'), { withFileTypes: true })
      .filter(entry => entry.isDirectory()).map(entry => `${name}:${entry.name}`).sort());
  }
  writeFileSync(marketplacePath, JSON.stringify({
    name: 'pmcro-smoke',
    interface: { displayName: 'PMCR-O smoke test' },
    plugins: [...entries.keys()].map(name => ({
      name, source: { source: 'local', path: `./plugins/${name}` },
      policy: { installation: 'AVAILABLE', authentication: 'ON_INSTALL' }, category: 'Developer Tools',
    })),
  }));

  server = spawn('codex', ['app-server'], {
    cwd: root,
    env: { PATH: process.env.PATH, LANG: 'C.UTF-8', HOME: home, CODEX_HOME: codex },
    stdio: ['pipe', 'pipe', 'ignore'],
  });
  exited = once(server, 'close').catch(() => []);
  const requests = new Map();
  let id = 0;
  const rejectPending = error => {
    for (const pending of requests.values()) pending.reject(error);
    requests.clear();
    server.kill();
  };
  server.on('error', rejectPending);
  server.on('close', () => rejectPending(new Error('Codex app server closed')));
  server.stdin.on('error', rejectPending);
  timer = setTimeout(() => rejectPending(new Error('Codex smoke test timed out')), 60_000);
  createInterface({ input: server.stdout }).on('line', line => {
    try {
      const message = JSON.parse(line);
      const pending = requests.get(message.id);
      if (!pending) return;
      requests.delete(message.id);
      if (message.error) pending.reject(new Error(`Codex error: ${message.error.message}`));
      else pending.resolve(message.result);
    } catch (error) {
      rejectPending(error);
    }
  });
  const send = value => server.stdin.write(JSON.stringify(value) + '\n');
  const request = (method, params) => new Promise((resolve, reject) => {
    const requestId = ++id;
    requests.set(requestId, { resolve, reject });
    send({ id: requestId, method, params });
  });
  await request('initialize', {
    clientInfo: { name: 'pmcro-smoke', version: '1.0.0' }, capabilities: { experimentalApi: true },
  });
  send({ method: 'initialized' });
  let skills = 0;
  for (const [pluginName, expected] of entries) {
    const params = { pluginName, marketplacePath };
    const before = (await request('plugin/read', params)).plugin;
    assert.equal(before.summary.installed, false, `${pluginName}: unexpectedly installed`);
    assert.deepEqual(before.skills.map(skill => skill.name).sort(), expected, `${pluginName}: pre-install skills`);
    const installed = await request('plugin/install', params);
    assert.equal(installed.appsNeedingAuth.length, 0, `${pluginName}: unexpected app authorization`);
    const after = (await request('plugin/read', params)).plugin;
    assert.equal(after.summary.installed, true, `${pluginName}: not installed`);
    assert.equal(after.summary.enabled, true, `${pluginName}: not enabled`);
    assert.deepEqual(after.skills.map(skill => skill.name).sort(), expected, `${pluginName}: installed skills`);
    skills += expected.length;
  }
  console.log(JSON.stringify({ status: 'PASS', installed_and_enabled: entries.size, skills_discovered: skills,
    provider_invocation: 'NOT_INVOKED', model_behavior: 'NOT_TESTED' }));
} finally {
  clearTimeout(timer);
  if (server) {
    server.stdin.end();
    server.kill();
    await exited;
  }
  rmSync(root, { recursive: true, force: true });
}
