// Copies src/accent.css (the shared accent-underline rule) into every composition between its markers.
// Run after editing the rule or rebuilding the cards: node tools/build-cards.mjs && node tools/sync-accent.mjs
import fs from "node:fs";
import path from "node:path";
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const rule = fs.readFileSync(path.join(ROOT, "src/accent.css"), "utf8").trim();
const re = /\/\* accent:start[\s\S]*?\/\* accent:end \*\//;
for (const f of ["intro.html", "card-why.html", "card-whatif.html"]) {
  const p = path.join(ROOT, "compositions", f);
  let s = fs.readFileSync(p, "utf8");
  if (!re.test(s)) throw new Error(f + ": no accent markers");
  s = s.replace(re, rule);
  fs.writeFileSync(p, s);
  console.log("synced", f);
}
