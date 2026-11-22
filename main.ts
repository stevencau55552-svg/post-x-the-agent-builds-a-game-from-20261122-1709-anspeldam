// ORBIT DODGE entry — main.ts (Node 22, standard library only).
//
// The entry itself is the X post: an AI agent built a tiny browser game
// (game.html) from a single prompt, filmed it, and posted the video on X.
// This program does the one job the gate needs: copy POST.json from the
// repository root into the output directory, byte for byte, so the gate can
// read the post's address. It reaches for no network, no wall clock, and no
// file outside the repository, so two runs always write the same bytes.
//
// Local run (mirrors the grader):
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

// Inside the grader these are /bot and /output; the env vars let us run the
// same file locally without changing anything.
const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

const SOURCE = join(BOT_DIR, 'POST.json');
const TARGET = join(OUTPUT_DIR, 'POST.json');

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(SOURCE, TARGET);
} catch (err) {
  console.error(`could not copy ${SOURCE} to ${TARGET}: ${(err as Error).message}`);
  process.exit(1);
}
