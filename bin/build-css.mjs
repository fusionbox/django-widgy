// Compile widgy's SCSS entry points to CSS with Dart Sass.
//
// Usage: node bin/build-css.mjs   (or `make css`)
//
// Each entry point below is compiled to a .css file next to it. Other .scss
// files (widgy_common, *-theme.admin, ...) are only @imported.
//
// Widgy's SCSS is also compiled by django-pyscss in downstream projects
// (through django-compressor), so the sources keep its import convention: a
// leading slash means "relative to the static root", e.g.
// @import "/widgy/css/widgy_common.scss". The importer below resolves those
// against each app's static directory.

import { readdirSync, existsSync, writeFileSync } from 'node:fs';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import * as sass from 'sass';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const contrib = join(root, 'widgy/contrib');

const staticDirs = [
  join(root, 'widgy/static'),
  ...readdirSync(contrib)
    .map((app) => join(contrib, app, 'static'))
    .filter((dir) => existsSync(dir)),
];

const entries = [
  'widgy/static/widgy/css/widgy.scss',
  'widgy/static/widgy/css/history.scss',
  'widgy/static/widgy/css/layout_select.scss',
  'widgy/static/widgy/css/popup.scss',
  'widgy/static/widgy/css/unapproved_commits.scss',
  'widgy/static/widgy/mixins/tabbed.admin.scss',
  // Every widget/app stylesheet in the contrib apps, except imported-only files.
  ...staticDirs.slice(1).flatMap((dir) => {
    const widgyDir = join(dir, 'widgy');
    return readdirSync(widgyDir).flatMap((app) =>
      readdirSync(join(widgyDir, app))
        .filter((f) => f.endsWith('.scss') && !f.endsWith('-theme.admin.scss'))
        .map((f) => join(widgyDir, app, f).slice(root.length + 1)),
    );
  }),
  'demo/public/css/demo.scss',
];

// Candidate files Sass would try for an import path.
function candidates(path) {
  const dir = dirname(path);
  const name = basename(path);
  const stems = name.endsWith('.scss') ? [name.slice(0, -5)] : [name];
  return stems.flatMap((stem) => [join(dir, `${stem}.scss`), join(dir, `_${stem}.scss`)]);
}

const staticRootImporter = {
  findFileUrl(url) {
    if (!url.startsWith('/')) return null;
    for (const dir of staticDirs) {
      if (candidates(join(dir, url)).some((f) => existsSync(f))) {
        return pathToFileURL(join(dir, url));
      }
    }
    return null;
  },
};

let failed = false;
for (const entry of entries.sort()) {
  const src = join(root, entry);
  try {
    const { css } = sass.compile(src, {
      style: 'expanded',
      importers: [staticRootImporter],
      silenceDeprecations: ['import', 'global-builtin', 'color-functions'],
    });
    writeFileSync(src.replace(/\.scss$/, '.css'), css + '\n');
    console.log(`compiled ${entry}`);
  } catch (err) {
    failed = true;
    console.error(`FAILED ${entry}\n${err.message}`);
  }
}
process.exit(failed ? 1 : 0);
