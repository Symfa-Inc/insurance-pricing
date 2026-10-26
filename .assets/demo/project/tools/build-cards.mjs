// Writes the two chapter cards (compositions/card-*.html). Run: node tools/build-cards.mjs
// v2 kinetic headline card (after the InsureCast cards the owner liked, in this product's own words, Geist and emerald):
//  - a #fafafa sheet whips in from the right (0.45 s power3.inOut, motion blur 10 px cleared to `none` once it lands),
//    led by the app's 14 px emerald header bar on its edge;
//  - the line is already there as zinc-200 ghost type; each word sweeps to ink (0.2 s, 90 ms apart), the accent word
//    to emerald-600, then an emerald-400 rule draws under it (shared rule: src/accent.css, same as the poster's "why.");
//  - one card-specific motion graphic (the price under "Why this price?", a strike through "smoking");
//  - the sheet whips out to the left, its trailing emerald edge uncovering the product.
// Everything is centred on both axes. Card length 2.4 s = 4 beats at 100 BPM; enters and leaves on a beat.
import fs from "node:fs";
import path from "node:path";
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const CARDS = [
  { id: "card-why", p: "cy", words: ["Why", "this", "price?"], acc: 2, extra: "price" },
  { id: "card-whatif", p: "cw", words: ["What", "if", "she", "quits", "smoking?"], acc: 3, strike: 4 },
];
const DUR = 2.4, OUT = 1.95;
for (const c of CARDS) {
  const p = c.p;
  const words = c.words
    .map((w, i) => {
      const cls = `${p}-w${i === c.acc ? ` ${p}-acc acc-u` : ""}`;
      const inner = i === c.acc ? `${w}<span class="acc-bar" id="${p}-ul"></span>` : i === c.strike ? `<span class="${p}-sk" id="${p}-sk">${w.replace(/\?$/, "")}<span class="${p}-st" id="${p}-st"></span></span>${w.endsWith("?") ? "?" : ""}` : w;
      return `<span class="${cls}" id="${p}-w${i}">${inner}</span>`;
    })
    .join(" ");
  const extra = c.extra === "price" ? `\n      <p id="${p}-sub" data-layout-allow-overlap>$33,216.29</p>` : "";
  const html = `<template>
  <style>
    @font-face { font-family: "Geist"; font-style: normal; font-weight: 100 900; src: url("assets/fonts/Geist-latin.woff2") format("woff2"); }
    @font-face { font-family: "Geist Mono"; font-style: normal; font-weight: 100 900; src: url("assets/fonts/GeistMono-latin.woff2") format("woff2"); }
    #root { position: absolute; inset: 0; overflow: hidden; font-family: "Geist", sans-serif; -webkit-font-smoothing: antialiased; }
    #${p}-sheet { position: absolute; left: 0; top: 0; width: 1920px; height: 1080px; background: #fafafa; }
    #${p}-sheet::before, #${p}-sheet::after { content: ""; position: absolute; top: 0; width: 14px; height: 1080px; background: #00d294; }
    #${p}-sheet::before { left: -14px; border-radius: 7px 0 0 7px; }
    #${p}-sheet::after { left: 1920px; border-radius: 0 7px 7px 0; }
    #${p}-stack { position: absolute; inset: 0; display: flex; flex-direction: column; align-items: center; justify-content: center; }
    #${p}-line { margin: 0; font-size: 112px; line-height: 1.04; font-weight: 600; letter-spacing: -0.04em; color: #e4e4e7; white-space: nowrap; text-align: center; }
    .${p}-w { display: inline-block; position: relative; color: #e4e4e7; }
    /* accent:start */ /* accent:end */
    .${p}-sk { position: relative; }
    .${p}-st { position: absolute; left: -6px; right: -6px; top: 54%; height: 10px; margin-top: -5px; border-radius: 5px; background: #00d294; transform-origin: 0 50%; }
    #${p}-sub { margin: 40px 0 0; font-family: "Geist Mono", monospace; font-size: 64px; line-height: 1; font-weight: 600; letter-spacing: -0.025em; color: #71717b; opacity: 0; }
  </style>
  <div id="root" data-composition-id="${c.id}" data-width="1920" data-height="1080">
    <div id="${p}-sheet">
      <div id="${p}-stack">
      <h2 id="${p}-line" data-layout-allow-overlap>${words}</h2>${extra}
      </div>
    </div>
  </div>
  <script>
    (function () {
      gsap.config({ force3D: false });
      var tl = gsap.timeline({ paused: true });
      function ft(t, a, b, g) { b.immediateRender = false; tl.fromTo(t, a, b, g); if (b.filter === "blur(0px)") tl.set(t, { filter: "none" }, g + b.duration + 0.02); }
      // whip in from the right, motion blur clears as it lands
      tl.set("#${p}-sheet", { x: 2050, filter: "blur(10px)" }, 0);
      ft("#${p}-sheet", { x: 2050 }, { x: 0, duration: 0.45, ease: "power3.inOut" }, 0);
      ft("#${p}-sheet", { filter: "blur(10px)" }, { filter: "blur(0px)", duration: 0.2, ease: "power2.out" }, 0.25);
      ${c.acc != null ? `tl.set("#${p}-ul", { scaleX: 0 }, 0);` : ""}
      ${c.strike != null ? `tl.set("#${p}-st", { scaleX: 0 }, 0);` : ""}
      // word-by-word sweep from ghost to ink; the accent word lands in emerald and gets its rule
      var W = ${JSON.stringify(c.words.map((_, i) => (i === c.acc ? "#009767" : "#18181b")))};
      for (var i = 0; i < W.length; i++) ft("#${p}-w" + i, { color: "#e4e4e7" }, { color: W[i], duration: 0.2, ease: "power1.out" }, 0.4 + i * 0.09);
      var accEnd = 0.4 + ${c.acc} * 0.09 + 0.16;
      ft("#${p}-ul", { scaleX: 0 }, { scaleX: 1, duration: 0.32, ease: "power2.inOut" }, accEnd);
      ${
        c.extra === "price"
          ? `// the price in question, in the app's number face
      ft("#${p}-sub", { opacity: 0, y: 10, filter: "blur(6px)" }, { opacity: 1, y: 0, filter: "blur(0px)", duration: 0.3, ease: "power2.out" }, 0.86);`
          : ""
      }${
        c.strike != null
          ? `// she quits: the habit is struck out and greys back
      ft("#${p}-st", { scaleX: 0 }, { scaleX: 1, duration: 0.3, ease: "power2.inOut" }, 1.02);
      ft("#${p}-sk", { color: "#18181b" }, { color: "#a1a1aa", duration: 0.22, ease: "power1.out" }, 1.2);`
          : ""
      }
      // whip out to the left; the trailing emerald edge uncovers the product
      ft("#${p}-sheet", { x: 0 }, { x: -2050, duration: 0.45, ease: "power3.inOut" }, ${OUT});
      ft("#${p}-sheet", { filter: "none" }, { filter: "blur(10px)", duration: 0.22, ease: "power2.in" }, ${OUT});
      tl.to({}, { duration: 0.01 }, ${(DUR - 0.02).toFixed(2)});
      window.__timelines["${c.id}"] = tl;
    })();
  </script>
</template>
`;
  fs.writeFileSync(path.join(ROOT, `compositions/${c.id}.html`), html);
  console.log("wrote", c.id);
}
