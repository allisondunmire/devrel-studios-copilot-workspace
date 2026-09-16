import test from 'node:test';
import assert from 'node:assert/strict';

import {
  OrphanDeletionError,
  azureCliInvocation,
  leafFirstOrder,
  parseArgs,
  runManifest,
  validateManifest,
} from './delete-orphan-trees.mjs';

function manifest(overrides = {}) {
  return {
    version: 1,
    organization: 'https://dev.azure.com/devrel',
    project: 'Studios',
    trees: [{
      rootId: 100,
      nodes: [
        { id: 100, type: 'Episode', revision: 4, parentId: null, children: [101, 102, 103] },
        { id: 101, type: 'Editing', revision: 2, parentId: 100, children: [] },
        { id: 102, type: 'Publishing', revision: 3, parentId: 100, children: [] },
        { id: 103, type: 'Graphics', revision: 1, parentId: 100, children: [] },
      ],
    }],
    ...overrides,
  };
}

function item(expected, overrides = {}) {
  const relations = [];
  if (expected.parentId !== null) {
    relations.push({
      rel: 'System.LinkTypes.Hierarchy-Reverse',
      url: `https://dev.azure.com/devrel/_apis/wit/workItems/${expected.parentId}`,
    });
  }
  for (const childId of expected.children) {
    relations.push({
      rel: 'System.LinkTypes.Hierarchy-Forward',
      url: `https://dev.azure.com/devrel/_apis/wit/workItems/${childId}`,
    });
  }
  return {
    id: expected.id,
    rev: expected.revision,
    fields: {
      'System.TeamProject': 'Studios',
      'System.WorkItemType': expected.type,
      ...(expected.parentId === null ? {} : { 'System.Parent': expected.parentId }),
    },
    relations,
    ...overrides,
  };
}

function fakeAz(input, options = {}) {
  const normalized = validateManifest(input);
  const expectedById = new Map(
    normalized.trees.flatMap((tree) => tree.nodes.map((node) => [node.id, node])),
  );
  const calls = [];
  const deletedIds = new Set();
  const showCounts = new Map();
  const executeAz = async (args) => {
    calls.push(args);
    const id = Number(args[args.indexOf('--id') + 1]);
    if (args[2] === 'show') {
      const expected = expectedById.get(id);
      const count = showCounts.get(id) ?? 0;
      showCounts.set(id, count + 1);
      const sequence = options.itemSequences?.get(id);
      if (sequence?.[count]) return { stdout: JSON.stringify(sequence[count]), stderr: '' };
      const payload = options.items?.get(id) ?? item({
        ...expected,
        revision: expected.revision + expected.children.filter((childId) => deletedIds.has(childId)).length,
        children: expected.children.filter((childId) => !deletedIds.has(childId)),
      });
      return { stdout: JSON.stringify(payload), stderr: '' };
    }
    if (options.failDeleteId === id) {
      throw new OrphanDeletionError(`delete failed for ${id}`);
    }
    deletedIds.add(id);
    return { stdout: '{}', stderr: '' };
  };
  return { executeAz, calls };
}

test('parseArgs requires a manifest and treats execution as opt-in', () => {
  assert.deepEqual(parseArgs(['--manifest', 'items.json']), {
    manifestPath: 'items.json',
    execute: false,
  });
  assert.deepEqual(parseArgs(['--manifest', 'items.json', '--execute']), {
    manifestPath: 'items.json',
    execute: true,
  });
  assert.throws(() => parseArgs([]), /--manifest is required/);
  assert.throws(() => parseArgs(['--destroy']), /Unknown argument/);
});

test('uses a platform-aware Azure CLI launcher without shell interpolation', () => {
  assert.deepEqual(azureCliInvocation(['boards', 'work-item', 'show'], 'linux'), {
    file: 'az',
    args: ['boards', 'work-item', 'show'],
  });
  assert.deepEqual(
    azureCliInvocation(
      ['boards', 'work-item', 'show', '--org', 'https://dev.azure.com/devrel'],
      'win32',
      'C:\\Windows\\System32\\cmd.exe',
    ),
    {
      file: 'C:\\Windows\\System32\\cmd.exe',
      args: ['/d', '/s', '/c', 'az boards work-item show --org https://dev.azure.com/devrel'],
    },
  );
  assert.throws(
    () => azureCliInvocation(['boards', '&', 'whoami'], 'win32'),
    /Unsafe Azure CLI argument/,
  );
});

test('validates the fixed organization, project, types, and batch limit', () => {
  assert.throws(
    () => validateManifest(manifest({ organization: 'https://dev.azure.com/other' })),
    /Organization must be/,
  );
  assert.throws(() => validateManifest(manifest({ project: 'MVP' })), /Project must be Studios/);

  const unsupported = manifest();
  unsupported.trees[0].nodes[1].type = 'Task';
  assert.throws(() => validateManifest(unsupported), /unsupported type/);

  const oversizedNodes = Array.from({ length: 51 }, (_, index) => ({
    id: index + 1,
    type: index === 0 ? 'Episode' : 'Editing',
    revision: 1,
    parentId: index === 0 ? null : 1,
    children: index === 0 ? Array.from({ length: 50 }, (_, child) => child + 2) : [],
  }));
  assert.throws(
    () => validateManifest({
      version: 1,
      organization: 'https://dev.azure.com/devrel',
      project: 'Studios',
      trees: [{ rootId: 1, nodes: oversizedNodes }],
    }),
    /maximum is 50/,
  );
});

test('supports the additional Studios types with conservative hierarchy rules', () => {
  for (const type of ['Shorts', 'Full course video', 'Upwork', 'Postmortem']) {
    assert.doesNotThrow(() => validateManifest({
      version: 1,
      organization: 'https://dev.azure.com/devrel',
      project: 'Studios',
      trees: [{
        rootId: 1,
        nodes: [{ id: 1, type, revision: 1, parentId: null, children: [] }],
      }],
    }));
  }

  for (const childType of ['Shorts', 'Upwork']) {
    const input = {
      version: 1,
      organization: 'https://dev.azure.com/devrel',
      project: 'Studios',
      trees: [{
        rootId: 1,
        nodes: [
          { id: 1, type: 'Episode', revision: 1, parentId: null, children: [2] },
          { id: 2, type: childType, revision: 1, parentId: 1, children: [] },
        ],
      }],
    };
    assert.doesNotThrow(() => validateManifest(input));
  }

  const parentedFullCourseVideo = {
    version: 1,
    organization: 'https://dev.azure.com/devrel',
    project: 'Studios',
    trees: [{
      rootId: 1,
      nodes: [
        { id: 1, type: 'Episode', revision: 1, parentId: null, children: [2] },
        { id: 2, type: 'Full course video', revision: 1, parentId: 1, children: [] },
      ],
    }],
  };
  assert.throws(
    () => validateManifest(parentedFullCourseVideo),
    /Full course video cannot be a child of Episode/,
  );
});

test('rejects duplicate, disconnected, and cyclic tree structures', () => {
  const duplicate = manifest();
  duplicate.trees[0].nodes.push({ ...duplicate.trees[0].nodes[1] });
  assert.throws(() => validateManifest(duplicate), /appears more than once/);

  const disconnected = manifest();
  disconnected.trees[0].nodes.push({
    id: 104, type: 'Graphics', revision: 1, parentId: 100, children: [],
  });
  assert.throws(() => validateManifest(disconnected), /disconnected/);

  const cyclic = manifest();
  cyclic.trees[0].nodes[0].parentId = 103;
  cyclic.trees[0].nodes[3].children = [100];
  assert.throws(() => validateManifest(cyclic), /root must have parentId null/);
});

test('rejects wrong-hierarchy descendants even when the tree is structurally consistent', () => {
  const wrongHierarchy = {
    version: 1,
    organization: 'https://dev.azure.com/devrel',
    project: 'Studios',
    trees: [{
      rootId: 1,
      nodes: [
        { id: 1, type: 'Editing', revision: 1, parentId: null, children: [2] },
        { id: 2, type: 'Episode', revision: 1, parentId: 1, children: [] },
      ],
    }],
  };
  assert.throws(
    () => validateManifest(wrongHierarchy),
    /Episode cannot be a child of Editing/,
  );
});

test('orders every tree leaf-first', () => {
  const tree = validateManifest(manifest()).trees[0];
  assert.deepEqual(leafFirstOrder(tree.rootId, tree.nodeById), [101, 102, 103, 100]);
});

test('dry-run revalidates every node without issuing delete commands', async () => {
  const input = manifest();
  const fake = fakeAz(input);
  const result = await runManifest(input, { execute: false }, fake);
  assert.equal(result.mode, 'dry-run');
  assert.equal(result.results[0].status, 'validated');
  assert.deepEqual(result.results[0].deleted, []);
  assert.equal(fake.calls.filter((args) => args[2] === 'show').length, 4);
  assert.equal(fake.calls.filter((args) => args[2] === 'delete').length, 0);
});

test('execute deletes only after preflight and uses safe argument arrays', async () => {
  const input = manifest();
  const fake = fakeAz(input);
  const result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'deleted');
  assert.deepEqual(result.results[0].deleted, [101, 102, 103, 100]);

  const deleteCalls = fake.calls.filter((args) => args[2] === 'delete');
  assert.deepEqual(deleteCalls.map((args) => Number(args[args.indexOf('--id') + 1])), [101, 102, 103, 100]);
  assert.ok(deleteCalls.every((args) => args.includes('--yes')));
  assert.ok(deleteCalls.every((args) => !args.some((arg) => /destroy/i.test(arg))));
  assert.ok(deleteCalls.every((args) => args.includes('Studios')));
  assert.equal(fake.calls.filter((args) => args[2] === 'show').length, 8);
});

test('skips the entire tree when a revision changes', async () => {
  const input = manifest();
  const changedItems = new Map();
  const expected = input.trees[0].nodes[1];
  changedItems.set(expected.id, item(expected, { rev: expected.revision + 1 }));
  const fake = fakeAz(input, { items: changedItems });
  const result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'skipped');
  assert.match(result.results[0].error, /revision changed/);
  assert.equal(fake.calls.filter((args) => args[2] === 'delete').length, 0);
});

test('skips the entire tree when a root gains a parent', async () => {
  const input = manifest();
  const changedItems = new Map();
  const expected = input.trees[0].nodes[0];
  changedItems.set(expected.id, item(expected, {
    fields: {
      'System.TeamProject': 'Studios',
      'System.WorkItemType': 'Episode',
      'System.Parent': 999,
    },
    relations: [{
      rel: 'System.LinkTypes.Hierarchy-Reverse',
      url: 'https://dev.azure.com/devrel/_apis/wit/workItems/999',
    }],
  }));
  const fake = fakeAz(input, { items: changedItems });
  const result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'skipped');
  assert.match(result.results[0].error, /parent relationship changed/);
  assert.equal(fake.calls.filter((args) => args[2] === 'delete').length, 0);
});

test('skips the entire tree when a new child appears', async () => {
  const input = manifest();
  const changedItems = new Map();
  const expected = input.trees[0].nodes[0];
  const actual = item(expected);
  actual.relations.push({
    rel: 'System.LinkTypes.Hierarchy-Forward',
    url: 'https://dev.azure.com/devrel/_apis/wit/workItems/999',
  });
  changedItems.set(expected.id, actual);
  const fake = fakeAz(input, { items: changedItems });
  const result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'skipped');
  assert.match(result.results[0].error, /child relationships changed/);
  assert.equal(fake.calls.filter((args) => args[2] === 'delete').length, 0);
});

test('stops when a node changes between preflight and point-of-delete guard', async () => {
  const input = manifest();
  const expected = input.trees[0].nodes[1];
  const itemSequences = new Map([[
    expected.id,
    [
      item(expected),
      item(expected, { rev: expected.revision + 1 }),
    ],
  ]]);
  const fake = fakeAz(input, { itemSequences });
  const result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'failed');
  assert.match(result.results[0].error, /revision changed unexpectedly/);
  assert.deepEqual(result.results[0].deleted, []);
  assert.equal(fake.calls.filter((args) => args[2] === 'delete').length, 0);
});

test('fails closed on malformed hierarchy relations and parent fields', async () => {
  const input = manifest();
  const expected = input.trees[0].nodes[1];
  const malformedRelation = item(expected);
  malformedRelation.relations[0].url = 'not-a-url';
  let fake = fakeAz(input, { items: new Map([[expected.id, malformedRelation]]) });
  let result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'skipped');
  assert.match(result.results[0].error, /invalid hierarchy relation URL/);

  const invalidParent = item(expected);
  invalidParent.fields['System.Parent'] = '100';
  fake = fakeAz(input, { items: new Map([[expected.id, invalidParent]]) });
  result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'skipped');
  assert.match(result.results[0].error, /invalid System.Parent/);
});

test('parses hierarchy relation URLs with query strings without hiding the ID', async () => {
  const input = manifest();
  const expected = input.trees[0].nodes[1];
  const withQuery = item(expected);
  withQuery.relations[0].url += '?api-version=7.1';
  const fake = fakeAz(input, { items: new Map([[expected.id, withQuery]]) });
  const result = await runManifest(input, { execute: false }, fake);
  assert.equal(result.results[0].status, 'validated');
});

test('stops the current tree after the first deletion failure', async () => {
  const input = manifest();
  const fake = fakeAz(input, { failDeleteId: 102 });
  const result = await runManifest(input, { execute: true }, fake);
  assert.equal(result.results[0].status, 'failed');
  assert.deepEqual(result.results[0].deleted, [101]);
  const deleteIds = fake.calls
    .filter((args) => args[2] === 'delete')
    .map((args) => Number(args[args.indexOf('--id') + 1]));
  assert.deepEqual(deleteIds, [101, 102]);
});
