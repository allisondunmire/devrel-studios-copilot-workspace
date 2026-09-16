// Tests for the deterministic caption-verification core in captions.js.
// Network-free: exercises evaluateUpload() directly with inline track lists.
// Run: node --test captions.test.mjs  (or `npm run test:scripts` from repo root)

import test from 'node:test';
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const require = createRequire(import.meta.url);
const here = path.dirname(fileURLToPath(import.meta.url));
const { evaluateUpload } = require(path.join(here, 'captions.js'));

const asr = { id: 'asr1', language: 'en', name: '', trackKind: 'ASR', isDraft: false };
const standard = (over = {}) => ({ id: 'std1', language: 'en', name: 'English', trackKind: 'standard', isDraft: false, ...over });

test('verified when the published standard track is present (matched by id)', () => {
  const r = evaluateUpload([standard()], 'std1', 'en');
  assert.equal(r.verified, true);
  assert.equal(r.track.id, 'std1');
  assert.deepEqual(r.warnings, []);
});

test('falls back to matching a standard track by language when id is not found', () => {
  const r = evaluateUpload([standard({ id: 'other' })], 'missing-id', 'en');
  assert.equal(r.verified, true);
  assert.equal(r.track.id, 'other');
  assert.deepEqual(r.warnings, []);
});

test('warns and is not verified when the corrected track is missing', () => {
  const r = evaluateUpload([asr], 'std1', 'en');
  assert.equal(r.verified, false);
  assert.equal(r.track, null);
  assert.equal(r.warnings.length, 1);
  assert.match(r.warnings[0], /not found/i);
});

test('warns about DRAFT and, with an ASR present, that viewers still see auto-captions', () => {
  const r = evaluateUpload([asr, standard({ isDraft: true })], 'std1', 'en');
  assert.equal(r.verified, false);
  assert.equal(r.warnings.length, 2);
  assert.match(r.warnings[0], /DRAFT/);
  assert.match(r.warnings[1], /still seeing the auto-captions/i);
});

test('warns only about draft (no propagation note) when no ASR track exists', () => {
  const r = evaluateUpload([standard({ isDraft: true })], 'std1', 'en');
  assert.equal(r.verified, false);
  assert.equal(r.warnings.length, 1);
  assert.match(r.warnings[0], /DRAFT/);
});

test('published standard alongside a lingering ASR yields only the propagation note', () => {
  const r = evaluateUpload([asr, standard()], 'std1', 'en');
  assert.equal(r.verified, true);
  assert.equal(r.warnings.length, 1);
  assert.match(r.warnings[0], /propagate/i);
});

test('language filter ignores tracks in other languages', () => {
  const frStandard = standard({ id: 'fr1', language: 'fr' });
  const r = evaluateUpload([frStandard], 'missing-id', 'en');
  assert.equal(r.verified, false);
  assert.equal(r.track, null);
  assert.match(r.warnings[0], /not found/i);
});
