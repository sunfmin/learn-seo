// Generate the served copies of the self-contained lesson pages.
//
// Single source of truth: lessons/*.html and reference/glossary.html are the
// authored originals. Astro serves files from public/ verbatim, so we copy
// them there and rewrite the few repo-relative links (../RESOURCES.md,
// ../MISSION.md, ../lessons/) onto the site's real routes. public/lessons/
// and public/reference/ are GENERATED — gitignored, never hand-edited.
import { readFileSync, writeFileSync, mkdirSync, readdirSync, rmSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

const linkRewrites = (html) =>
  html
    .replaceAll('../RESOURCES.md', '/resources/')
    .replaceAll('../MISSION.md', '/');

// Clear-then-rebuild so a lesson migrated to an MDX collection entry (ADR 0002)
// leaves NO stale public/ copy — otherwise it would collide with the Astro route
// that now owns that URL. Lessons migrate one at a time; this shrinks to nothing
// once all originals are gone (Slice 9 deletes this script entirely).
rmSync(join(root, 'public/lessons'), { recursive: true, force: true });
rmSync(join(root, 'public/reference'), { recursive: true, force: true });
mkdirSync(join(root, 'public/lessons'), { recursive: true });
mkdirSync(join(root, 'public/reference'), { recursive: true });

const lessonFiles = readdirSync(join(root, 'lessons')).filter((f) => f.endsWith('.html'));
for (const f of lessonFiles) {
  const src = readFileSync(join(root, 'lessons', f), 'utf8');
  writeFileSync(join(root, 'public/lessons', f), linkRewrites(src));
}

// glossary additionally links back to ../lessons/*
const glossary = readFileSync(join(root, 'reference/glossary.html'), 'utf8');
writeFileSync(
  join(root, 'public/reference/glossary.html'),
  linkRewrites(glossary).replaceAll('../lessons/', '/lessons/'),
);

console.log(`synced ${lessonFiles.length} lessons + glossary -> public/`);
