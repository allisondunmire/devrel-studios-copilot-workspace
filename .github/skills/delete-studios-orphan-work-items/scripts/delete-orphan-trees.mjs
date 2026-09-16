#!/usr/bin/env node

import { execFile } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const ORGANIZATION = 'https://dev.azure.com/devrel';
const PROJECT = 'Studios';
const MAX_ITEMS = 50;
const SUPPORTED_TYPES = new Set([
  'Episode',
  'Scheduling',
  'Editing',
  'Uploading',
  'Publishing',
  'Thumbnails',
  'Graphics',
  'Shorts',
  'Full course video',
  'Upwork',
  'Postmortem',
]);
const ALLOWED_PARENT_TYPES = new Map([
  ['Episode', new Set([
    'Events', 'Shows', 'Series', 'Moments', 'General', 'Support requests',
    'Post production support', 'Publishing request',
  ])],
  ['Scheduling', new Set(['Episode', 'General'])],
  ['Editing', new Set(['Episode'])],
  ['Uploading', new Set(['Episode'])],
  ['Publishing', new Set(['Episode'])],
  ['Thumbnails', new Set(['Episode'])],
  ['Graphics', new Set([
    'Episode', 'Events', 'Shows', 'Series', 'Moments', 'General',
    'Support requests', 'Post production support', 'Publishing request',
  ])],
  ['Shorts', new Set(['Episode'])],
  ['Full course video', new Set()],
  ['Upwork', new Set(['Episode'])],
  ['Postmortem', new Set(['Events', 'Shows', 'Series', 'Support requests'])],
]);

export class OrphanDeletionError extends Error {}

function requireObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new OrphanDeletionError(`${label} must be an object.`);
  }
}

function requirePositiveInteger(value, label) {
  if (!Number.isInteger(value) || value < 1) {
    throw new OrphanDeletionError(`${label} must be a positive integer.`);
  }
}

function sortedUniqueIntegers(values, label) {
  if (!Array.isArray(values)) {
    throw new OrphanDeletionError(`${label} must be an array.`);
  }
  const result = [];
  const seen = new Set();
  for (const value of values) {
    requirePositiveInteger(value, `${label} item`);
    if (seen.has(value)) {
      throw new OrphanDeletionError(`${label} contains duplicate ID ${value}.`);
    }
    seen.add(value);
    result.push(value);
  }
  return result.sort((left, right) => left - right);
}

export function parseArgs(argv) {
  const options = { manifestPath: null, execute: false };
  for (let index = 0; index < argv.length; index += 1) {
    const argument = argv[index];
    if (argument === '--manifest') {
      const manifestPath = argv[index + 1] ?? null;
      if (!manifestPath || manifestPath.startsWith('--')) {
        throw new OrphanDeletionError('--manifest requires a path value.');
      }
      options.manifestPath = manifestPath;
      index += 1;
    } else if (argument === '--execute') {
      options.execute = true;
    } else {
      throw new OrphanDeletionError(`Unknown argument "${argument}".`);
    }
  }
  if (!options.manifestPath) {
    throw new OrphanDeletionError('--manifest is required.');
  }
  return options;
}

export function validateManifest(manifest) {
  requireObject(manifest, 'Manifest');
  if (manifest.version !== 1) {
    throw new OrphanDeletionError('Manifest version must be 1.');
  }
  if (manifest.organization !== ORGANIZATION) {
    throw new OrphanDeletionError(`Organization must be ${ORGANIZATION}.`);
  }
  if (manifest.project !== PROJECT) {
    throw new OrphanDeletionError(`Project must be ${PROJECT}.`);
  }
  if (!Array.isArray(manifest.trees) || manifest.trees.length === 0) {
    throw new OrphanDeletionError('Manifest trees must be a non-empty array.');
  }

  const globalIds = new Set();
  let totalItems = 0;
  const trees = manifest.trees.map((tree, treeIndex) => {
    requireObject(tree, `Tree ${treeIndex}`);
    requirePositiveInteger(tree.rootId, `Tree ${treeIndex} rootId`);
    if (!Array.isArray(tree.nodes) || tree.nodes.length === 0) {
      throw new OrphanDeletionError(`Tree ${tree.rootId} nodes must be non-empty.`);
    }

    const nodes = tree.nodes.map((node, nodeIndex) => {
      requireObject(node, `Tree ${tree.rootId} node ${nodeIndex}`);
      requirePositiveInteger(node.id, `Tree ${tree.rootId} node ID`);
      requirePositiveInteger(node.revision, `Work item ${node.id} revision`);
      if (!SUPPORTED_TYPES.has(node.type)) {
        throw new OrphanDeletionError(`Work item ${node.id} has unsupported type "${node.type}".`);
      }
      if (node.parentId !== null) {
        requirePositiveInteger(node.parentId, `Work item ${node.id} parentId`);
      }
      return {
        id: node.id,
        type: node.type,
        revision: node.revision,
        parentId: node.parentId,
        children: sortedUniqueIntegers(node.children, `Work item ${node.id} children`),
      };
    });

    const nodeById = new Map();
    for (const node of nodes) {
      if (nodeById.has(node.id) || globalIds.has(node.id)) {
        throw new OrphanDeletionError(`Work item ${node.id} appears more than once.`);
      }
      nodeById.set(node.id, node);
      globalIds.add(node.id);
    }
    totalItems += nodes.length;

    const root = nodeById.get(tree.rootId);
    if (!root) {
      throw new OrphanDeletionError(`Tree ${tree.rootId} does not contain its root.`);
    }
    if (root.parentId !== null) {
      throw new OrphanDeletionError(`Tree ${tree.rootId} root must have parentId null.`);
    }

    for (const node of nodes) {
      if (node.id !== tree.rootId && !nodeById.has(node.parentId)) {
        throw new OrphanDeletionError(`Work item ${node.id} parent is outside tree ${tree.rootId}.`);
      }
      if (node.id !== tree.rootId) {
        const parent = nodeById.get(node.parentId);
        if (!ALLOWED_PARENT_TYPES.get(node.type)?.has(parent.type)) {
          throw new OrphanDeletionError(
            `Work item ${node.id} type ${node.type} cannot be a child of ${parent.type}.`,
          );
        }
      }
      for (const childId of node.children) {
        const child = nodeById.get(childId);
        if (!child) {
          throw new OrphanDeletionError(`Work item ${node.id} child ${childId} is outside tree ${tree.rootId}.`);
        }
        if (child.parentId !== node.id) {
          throw new OrphanDeletionError(`Work item ${childId} does not point back to parent ${node.id}.`);
        }
      }
    }

    const order = leafFirstOrder(tree.rootId, nodeById);
    if (order.length !== nodes.length) {
      throw new OrphanDeletionError(`Tree ${tree.rootId} is disconnected.`);
    }
    return { rootId: tree.rootId, nodes, nodeById, order };
  });

  if (totalItems > MAX_ITEMS) {
    throw new OrphanDeletionError(`Manifest contains ${totalItems} items; maximum is ${MAX_ITEMS}.`);
  }
  return { version: 1, organization: ORGANIZATION, project: PROJECT, trees, totalItems };
}

export function leafFirstOrder(rootId, nodeById) {
  const order = [];
  const visiting = new Set();
  const visited = new Set();

  function visit(id) {
    if (visiting.has(id)) {
      throw new OrphanDeletionError(`Tree contains a cycle at work item ${id}.`);
    }
    if (visited.has(id)) return;
    visiting.add(id);
    const node = nodeById.get(id);
    if (!node) {
      throw new OrphanDeletionError(`Tree references missing work item ${id}.`);
    }
    for (const childId of node.children) visit(childId);
    visiting.delete(id);
    visited.add(id);
    order.push(id);
  }

  visit(rootId);
  return order;
}

function parseJson(stdout, label) {
  try {
    return JSON.parse(stdout);
  } catch {
    throw new OrphanDeletionError(`${label} returned invalid JSON.`);
  }
}

export function executeAz(args) {
  const invocation = azureCliInvocation(args);
  return new Promise((resolvePromise, rejectPromise) => {
    execFile(invocation.file, invocation.args, { maxBuffer: 10 * 1024 * 1024 }, (error, stdout, stderr) => {
      if (error) {
        rejectPromise(new OrphanDeletionError(
          `az ${args.slice(0, 3).join(' ')} failed: ${stderr.trim() || error.message}`,
        ));
        return;
      }
      resolvePromise({ stdout, stderr });
    });
  });
}

export function azureCliInvocation(args, platform = process.platform, comspec = process.env.ComSpec) {
  if (platform !== 'win32') {
    return { file: 'az', args };
  }
  const safeArguments = ['az', ...args].map((argument) => {
    if (!/^[A-Za-z0-9.:/_-]+$/.test(argument)) {
      throw new OrphanDeletionError(`Unsafe Azure CLI argument "${argument}".`);
    }
    return argument;
  });
  return {
    file: comspec || 'cmd.exe',
    args: ['/d', '/s', '/c', safeArguments.join(' ')],
  };
}

function relationIds(item, relationName) {
  const ids = [];
  for (const relation of item.relations ?? []) {
    if (relation.rel !== relationName) continue;
    let path;
    try {
      path = new URL(relation.url).pathname;
    } catch {
      throw new OrphanDeletionError(`Work item ${item.id} has an invalid hierarchy relation URL.`);
    }
    const match = path.match(/\/(\d+)$/);
    const id = match ? Number(match[1]) : null;
    if (!Number.isInteger(id) || id < 1) {
      throw new OrphanDeletionError(`Work item ${item.id} has an unparseable hierarchy relation.`);
    }
    ids.push(id);
  }
  return [...new Set(ids)].sort((left, right) => left - right);
}

function actualParentIds(item) {
  const ids = relationIds(item, 'System.LinkTypes.Hierarchy-Reverse');
  if (Object.hasOwn(item.fields ?? {}, 'System.Parent')) {
    const fieldParent = item.fields['System.Parent'];
    if (!Number.isInteger(fieldParent) || fieldParent < 1) {
      throw new OrphanDeletionError(`Work item ${item.id} has an invalid System.Parent value.`);
    }
    if (!ids.includes(fieldParent)) ids.push(fieldParent);
  }
  return ids.sort((left, right) => left - right);
}

function actualChildIds(item) {
  return relationIds(item, 'System.LinkTypes.Hierarchy-Forward');
}

function sameIds(left, right) {
  return left.length === right.length && left.every((value, index) => value === right[index]);
}

async function readWorkItem(id, organization, dependencies) {
  const result = await dependencies.executeAz([
    'boards', 'work-item', 'show',
    '--id', String(id),
    '--org', organization,
    '--expand', 'relations',
    '--output', 'json',
  ]);
  return parseJson(result.stdout, `Work item ${id}`);
}

export async function preflightTree(tree, manifest, dependencies) {
  const actualById = new Map();
  for (const expected of tree.nodes) {
    const actual = await readWorkItem(expected.id, manifest.organization, dependencies);
    actualById.set(expected.id, actual);

    if (actual.id !== expected.id) {
      throw new OrphanDeletionError(`Work item ${expected.id} returned mismatched ID ${actual.id}.`);
    }
    if (actual.rev !== expected.revision) {
      throw new OrphanDeletionError(
        `Work item ${expected.id} revision changed from ${expected.revision} to ${actual.rev}.`,
      );
    }
    if (actual.fields?.['System.TeamProject'] !== manifest.project) {
      throw new OrphanDeletionError(`Work item ${expected.id} is not in ${manifest.project}.`);
    }
    if (actual.fields?.['System.WorkItemType'] !== expected.type) {
      throw new OrphanDeletionError(`Work item ${expected.id} type changed.`);
    }

    const expectedParents = expected.parentId === null ? [] : [expected.parentId];
    if (!sameIds(actualParentIds(actual), expectedParents)) {
      throw new OrphanDeletionError(`Work item ${expected.id} parent relationship changed.`);
    }
    if (!sameIds(actualChildIds(actual), expected.children)) {
      throw new OrphanDeletionError(`Work item ${expected.id} child relationships changed.`);
    }
  }
  return actualById;
}

async function guardDelete(tree, expected, deletedIds, manifest, dependencies) {
  const actual = await readWorkItem(expected.id, manifest.organization, dependencies);
  const deletedDirectChildren = expected.children.filter((id) => deletedIds.has(id));
  const remainingChildren = expected.children.filter((id) => !deletedIds.has(id));
  const expectedRevision = expected.revision + deletedDirectChildren.length;

  if (actual.id !== expected.id) {
    throw new OrphanDeletionError(`Work item ${expected.id} returned mismatched ID ${actual.id}.`);
  }
  if (actual.rev !== expectedRevision) {
    throw new OrphanDeletionError(
      `Work item ${expected.id} revision changed unexpectedly from ${expectedRevision} to ${actual.rev}.`,
    );
  }
  if (actual.fields?.['System.TeamProject'] !== manifest.project) {
    throw new OrphanDeletionError(`Work item ${expected.id} is not in ${manifest.project}.`);
  }
  if (actual.fields?.['System.WorkItemType'] !== expected.type) {
    throw new OrphanDeletionError(`Work item ${expected.id} type changed.`);
  }
  const expectedParents = expected.parentId === null ? [] : [expected.parentId];
  if (!sameIds(actualParentIds(actual), expectedParents)) {
    throw new OrphanDeletionError(`Work item ${expected.id} parent relationship changed.`);
  }
  if (!sameIds(actualChildIds(actual), remainingChildren)) {
    throw new OrphanDeletionError(`Work item ${expected.id} child relationships changed.`);
  }
}

async function deleteWorkItem(id, manifest, dependencies) {
  await dependencies.executeAz([
    'boards', 'work-item', 'delete',
    '--id', String(id),
    '--org', manifest.organization,
    '--project', manifest.project,
    '--yes',
  ]);
}

export async function runManifest(input, options = {}, dependencyOverrides = {}) {
  const manifest = validateManifest(input);
  const dependencies = { executeAz, ...dependencyOverrides };
  const execute = options.execute === true;
  const results = [];

  for (const tree of manifest.trees) {
    const result = {
      rootId: tree.rootId,
      planned: tree.order,
      deleted: [],
      status: execute ? 'pending' : 'validated',
      error: null,
    };
    try {
      await preflightTree(tree, manifest, dependencies);
      if (execute) {
        const deletedIds = new Set();
        for (const id of tree.order) {
          try {
            await guardDelete(tree, tree.nodeById.get(id), deletedIds, manifest, dependencies);
            await deleteWorkItem(id, manifest, dependencies);
            result.deleted.push(id);
            deletedIds.add(id);
          } catch (error) {
            result.status = 'failed';
            result.error = error.message;
            break;
          }
        }
        if (result.status !== 'failed') result.status = 'deleted';
      }
    } catch (error) {
      result.status = 'skipped';
      result.error = error.message;
    }
    results.push(result);
  }

  return {
    mode: execute ? 'execute' : 'dry-run',
    organization: manifest.organization,
    project: manifest.project,
    totalItems: manifest.totalItems,
    results,
  };
}

async function main(argv) {
  const options = parseArgs(argv);
  const manifest = JSON.parse(await readFile(options.manifestPath, 'utf8'));
  const result = await runManifest(manifest, options);
  process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  if (result.results.some((tree) => tree.status === 'failed' || tree.status === 'skipped')) {
    process.exitCode = 1;
  }
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url))) {
  try {
    await main(process.argv.slice(2));
  } catch (error) {
    process.stderr.write(`delete-orphan-trees: ${error.message}\n`);
    process.exitCode = 1;
  }
}
