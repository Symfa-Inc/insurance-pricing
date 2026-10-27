// Builds compositions/app.html: the Insurance Pricing page rebuilt as live DOM from the captured app
// (its own production Tailwind CSS, the captured markup and the real /predict responses), plus the
// film's camera, cursor, menus and callouts. Run from the project root:  node tools/build-app.mjs
// Also writes tools/out/app-standalone.html (no <template>) so tools/measure.mjs can measure the rebuild.
import fs from "node:fs";
import path from "node:path";

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const rd = (p) => fs.readFileSync(path.join(ROOT, p), "utf8");
const has = (p) => fs.existsSync(path.join(ROOT, p));
const YES = JSON.parse(rd("assets/data/api-yes.json"));
const NO = JSON.parse(rd("assets/data/api-no.json"));
const SHOTS = JSON.parse(rd("src/shots.json"));
const LIVE = JSON.parse(rd("assets/data/capture-dom.json"));
const MEAS = has("assets/data/geom-recreation.json") ? JSON.parse(rd("assets/data/geom-recreation.json")) : null;

const esc = (s) => String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const usd = (v) => new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 }).format(v);
const cap = (s) => s.charAt(0).toUpperCase() + s.slice(1);
const fmtVal = (v) => (typeof v === "number" ? (Number.isInteger(v) ? `${v}` : v.toFixed(1)) : v);

// ---------- app CSS: the running app's production stylesheet (font-faces removed; we ship the same Geist files) ----------
const appCss = rd("assets/data/app-tailwind.css")
  .replace(/transition(-[a-z-]+)?:[^;}]*;?/g, "") // browser-clock transitions: the timeline owns every change
  .replace(/,?\s*"?Geist( Mono)? Fallback"?/g, "") // next/font metric fallbacks (Arial-based) are not used: the real Geist files load
  .replace(/,\s*"(Apple Color Emoji|Segoe UI Emoji|Segoe UI Symbol|Noto Color Emoji)"/g, "") // no emoji on screen; the renderer would embed a 183 MB system emoji font
  .replace(/@font-face\{font-family:Geist( Mono)?;src:local\(Arial\)[^}]*\}/g, "");
const filmCss = rd("src/app.style.css");

// ---------- pieces copied from the captured DOM ----------
const INFO = `<svg class="h-3.5 w-3.5 cursor-help text-zinc-300" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>`;
const tip = (id, text, iconId) => `<span class="group relative inline-flex items-center" id="${iconId}">${INFO.replace('class="h-3.5', `id="${iconId}-svg" class="h-3.5`)}<span id="${id}" class="pointer-events-none absolute bottom-full left-1/2 z-10 mb-2 w-56 -translate-x-1/2 rounded-lg bg-zinc-900 px-3 py-2 text-xs leading-relaxed text-zinc-100 opacity-0 shadow-lg">${esc(text)}<span class="absolute left-1/2 top-full -translate-x-1/2 border-4 border-transparent border-t-zinc-900"></span></span></span>`;
const SPIN = (cls, sw, id) => `<svg id="${id}" class="${cls}" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="${sw}" class="opacity-20"></circle><path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" stroke-width="${sw}" stroke-linecap="round"></path></svg>`;
const CHECK = `<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 8.5l3 3 6-7"/></svg>`;

function numField(id, label, oldVal) {
  return `<div class="space-y-1.5"><label class="block text-xs font-medium text-zinc-500">${label}</label><div id="ap-${id}" class="block w-full rounded-lg border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900"><span class="ap-txt"><span class="ap-old" id="ap-${id}-old">${oldVal}</span>${[...P[id].new].map((ch, k) => `<span id="ap-${id}-c${k}" style="display:none">${ch}</span>`).join("")}</span><span class="ap-caret" id="ap-${id}-caret"></span></div></div>`;
}
function selField(id, label, v0, v1) {
  return `<div class="space-y-1.5"><label class="block text-xs font-medium text-zinc-500">${label}</label><div id="ap-${id}" class="overflow-hidden rounded-lg border border-zinc-200 bg-white"><div class="ap-select block w-full rounded-none border-none bg-transparent px-3 py-2 text-sm text-zinc-900"><span id="ap-${id}-v0">${v0}</span>${v1 ? `<span class="ap-v1" id="ap-${id}-v1">${v1}</span>` : ""}</div></div></div>`;
}

// interpretation bullets, rendered like InterpretationCard's BulletText (bold up to a colon within 40 chars)
function bullet(text, i, set) {
  const c = text.indexOf(":");
  const body = c > 0 && c < 40 ? `<strong class="font-semibold text-zinc-800">${esc(text.slice(0, c + 1))}</strong>${esc(text.slice(c + 1))}` : esc(text);
  const mark = set === "yes" && i === 0 ? `<span class="ap-mark" id="ap-mark-0"></span>` : "";
  return `<li class="ap-li flex gap-2.5 text-sm leading-relaxed text-zinc-600" id="ap-li-${set}-${i}">${mark}<span class="mt-2 h-1 w-1 flex-none rounded-full bg-zinc-300"></span><span>${body}</span></li>`;
}

// feature impact rows (ShapChart): width = max(2, |v| / max|v| * 45) %
function widths(contribs) {
  const m = Math.max(...contribs.map((c) => Math.abs(c.shap_value)), 1e-9);
  return contribs.map((c) => ({ pos: c.shap_value >= 0, w: Math.max(2, (Math.abs(c.shap_value) / m) * 45), v: c.shap_value }));
}
const WY = widths(YES.shap.contributions), WN = widths(NO.shap.contributions);
const ROWS = YES.shap.contributions.map((c, i) => {
  const n = NO.shap.contributions[i];
  if (n.feature !== c.feature) throw new Error("row order differs between the two runs");
  const sameVal = String(fmtVal(c.value)) === String(fmtVal(n.value));
  const y = WY[i];
  return `<li id="ap-row-${i}"><div class="flex items-baseline justify-between gap-2 text-sm"><span class="font-medium text-zinc-700">${esc(c.feature)} <span class="font-normal text-zinc-400" style="position:relative"><span id="ap-rv-${i}-a">${esc(fmtVal(c.value))}</span>${sameVal ? "" : `<span id="ap-rv-${i}-b" style="position:absolute;left:0;top:0;opacity:0">${esc(fmtVal(n.value))}</span>`}</span></span><span id="ap-num-${i}" class="font-mono text-xs font-medium tabular-nums ${y.pos ? "text-emerald-600" : "text-rose-500"}"><span id="ap-ns-${i}">${y.pos ? "+" : ""}</span><span id="ap-nv-${i}">${y.v.toFixed(0)}</span></span></div><div class="relative mt-1.5 h-2 rounded-full bg-zinc-100" id="ap-track-${i}"><div class="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-zinc-300"></div><div id="ap-bp-${i}" class="absolute inset-y-0 left-1/2 rounded-r-full bg-emerald-500" style="width:0%"></div><div id="ap-bn-${i}" class="absolute inset-y-0 right-1/2 rounded-l-full bg-rose-400" style="width:0%"></div></div></li>`;
}).join("");

const P = {
  age: { old: "35", new: "48" }, bmi: { old: "27.5", new: "30.4" }, children: { old: "1", new: "2" },
};

const PAGE = `<div id="ap-page" class="antialiased"><div class="min-h-screen bg-zinc-50 text-zinc-900" style="min-height:1080px">
<main class="mx-auto w-full max-w-5xl px-6 py-10">
<header id="ap-hdr"><div class="flex gap-3"><div class="w-1 shrink-0 rounded-full bg-emerald-400"></div><div><h1 class="text-2xl font-semibold tracking-tight text-zinc-900">Insurance Pricing</h1><p class="mt-1 text-sm text-zinc-500">Estimate insurance costs with ML-powered predictions and explainable AI insights</p></div></div><div class="mt-4 h-px bg-gradient-to-r from-transparent via-zinc-200 to-transparent"></div></header>
<section class="mt-8 flex flex-col gap-6 md:flex-row md:items-stretch">
<div class="w-full md:w-60 md:flex-none" id="ap-fcol"><div id="ap-panel" class="rounded-xl border border-zinc-100 bg-white p-5 shadow-sm"><div class="space-y-5"><div class="space-y-4">
${numField("age", "Age", P.age.old)}
${selField("sex", "Sex", "Female")}
${numField("bmi", "BMI", P.bmi.old)}
${numField("children", "Children", P.children.old)}
${selField("smoker", "Smoker", "Yes", "No")}
${selField("region", "Region", "Northeast", "Northwest")}
</div>
<button type="button" id="ap-btn" class="w-full cursor-pointer rounded-lg bg-zinc-900 px-4 py-2.5 text-sm font-medium text-white" style="position:relative"><span id="ap-btn-a">Estimate</span><span id="ap-btn-b" style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;gap:8px;opacity:0">${SPIN("h-4 w-4", 2.5, "ap-btn-spin")}Estimating</span></button>
</div></div></div>
<div class="w-full flex-1" id="ap-rcol">
<div id="ap-idle" class="flex h-full min-h-48 flex-col items-center justify-center gap-5 rounded-xl border border-zinc-100 bg-white p-12 shadow-sm"><div class="pulse-ring shrink-0"></div><p class="text-sm text-zinc-400">Enter your details and click Estimate</p></div>
<div id="ap-pending" class="flex h-full min-h-48 items-center justify-center rounded-xl border border-zinc-100 bg-white p-12 shadow-sm"><div class="flex flex-col items-center gap-3">${SPIN("h-5 w-5 text-zinc-400", 2, "ap-pend-spin")}<p class="text-sm text-zinc-400">Running estimate...</p></div></div>
<div class="space-y-4" id="ap-results">
<div id="ap-w-price"><div id="ap-card-price" class="relative rounded-xl border border-zinc-100 bg-white p-6 shadow-sm" style="opacity:0"><div class="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-emerald-400 to-transparent"></div><div class="flex items-center gap-1.5"><p class="text-xs font-medium uppercase tracking-wider text-zinc-400">Estimated Annual Charges</p>${tip("ap-tip-price", "Predicted annual insurance cost based on the inputs you provided.", "ap-ic-price")}</div><p id="ap-price" class="mt-3 font-mono text-4xl font-semibold tracking-tight text-zinc-900">${usd(YES.charges)}</p></div></div>
<div id="ap-w-interp"><div id="ap-card-interp" class="rounded-xl border border-zinc-100 bg-white p-6 shadow-sm" style="opacity:0"><section><div class="flex items-center gap-1.5"><p class="text-xs font-medium uppercase tracking-wider text-zinc-400">Interpretation</p>${tip("ap-tip-interp", `Highlights the primary factors and their influence on the estimated charges. Baseline value: ${usd(YES.shap.base_value)}.`, "ap-ic-interp")}<span id="ap-badge" class="ml-1 inline-flex items-center rounded-full border px-2 py-0.5 text-[10px] font-semibold tracking-wide border-emerald-200 bg-emerald-50 text-emerald-700">${esc(YES.interpretation_source.toUpperCase())}</span></div>
<div id="ap-ilist"><ul class="mt-3 space-y-2" id="ap-ul-yes">${YES.interpretation.bullets.map((b, i) => bullet(b, i, "yes")).join("")}</ul><ul class="mt-3 space-y-2" id="ap-ul-no">${NO.interpretation.bullets.map((b, i) => bullet(b, i, "no")).join("")}</ul></div></section></div></div>
<div id="ap-w-shap"><div id="ap-card-shap" class="rounded-xl border border-zinc-100 bg-white p-6 shadow-sm" style="opacity:0"><section><div class="flex items-center gap-1.5"><p class="text-xs font-medium uppercase tracking-wider text-zinc-400">Feature Impact</p>${tip("ap-tip-shap", "Shows how each input pushed the estimate higher or lower relative to the average.", "ap-ic-shap")}</div><ul class="mt-4 space-y-3">${ROWS}</ul></section></div></div>
</div></div>
</section></main></div></div>`;

// ---------- geometry: the rebuilt page measured in a browser (tools/measure.mjs), else the live app capture ----------
const L = LIVE.g1;
const G = MEAS || {
  age: L.age, bmi: L.bmi, children: L.children, smoker: L.smoker, region: L.region, button: L.button,
  price: L.price, badge: L.badge, rows: [], icShap: null, ilistYes: null, ilistNo: null, li0: L.lis[0],
};
const box = (b) => b; // {x,y,w,h} in app px
// select wrappers: the measured element is the bordered wrapper; menus open 4 px under it
const menu = (k, items, cur) => {
  const s = G[k];
  return `<div class="ap-menu" id="ap-menu-${k}" data-layout-allow-overlap data-layout-allow-occlusion style="left:${s.x}px; top:${(s.y + s.h + 4).toFixed(2)}px; width:${s.w}px"><div class="ap-menu-hl" id="ap-menu-${k}-hl"></div>${items.map((it, i) => `<div class="ap-item" id="ap-menu-${k}-i${i}"><span>${it}</span>${i === cur ? CHECK : ""}</div>`).join("")}</div>`;
};
const MENUS = menu("region", ["Northeast", "Northwest", "Southeast", "Southwest"], 0) + menu("smoker", ["No", "Yes"], 1);

const CURSOR = `<div id="ap-cursor"><svg width="24" height="24" viewBox="0 0 26 26"><path d="M5 2.6 L5 20.8 L9.6 16.7 L12.7 23.5 L15.6 22.2 L12.6 15.6 L18.8 15.4 Z" fill="#111111" stroke="#ffffff" stroke-width="1.6" stroke-linejoin="round"/></svg></div>`;

// ---------- callouts (screen space): anchor in app px, seen at a fixed camera framing ----------
const F = SHOTS.framings;
function toScreen(ax, ay, f) {
  const left = f.cx - 960 / f.s, top = f.cy - 540 / f.s;
  return [(ax - left) * f.s, (ay - top) * f.s];
}
function anchorOf(name) {
  // named anchors on the rebuilt page
  const r = G.rows || [];
  switch (name) {
    case "price-end": return [G.price.x + G.price.textW + 6, G.price.y + G.price.h / 2];
    case "smoker-bar-pos": return [r[0].trackX + r[0].trackW * (0.5 + WY[0].w / 100), r[0].trackY + 4];
    case "region-bar-neg": return [r[4].trackX + r[4].trackW * (0.5 - WY[4].w / 100), r[4].trackY + 4];
    case "smoker-bar-neg": return [r[0].trackX + r[0].trackW * (0.5 - WN[0].w / 100), r[0].trackY + 4 + (G.ilistNo.h - G.ilistYes.h)];
    case "smoker-value": return [r[0].row.x + r[0].row.w - 18, r[0].row.y - 2];
    // just right of the smoker value ("-9056"), on its centre line, like "price-end": the leader leaves upward from
    // outside the number and never crosses it
    case "smoker-value-end": return [r[0].row.x + r[0].row.w + 9, r[0].row.y + 10];
    case "badge": return [G.badge.x + G.badge.w, G.badge.y + G.badge.h / 2];
    case "bullet-0": return [G.li0.amt.x + G.li0.amt.w / 2, G.li0.amt.y - 5]; // just above "$8,602" (v1 sat on its full stop)
    default: throw new Error("unknown anchor " + name);
  }
}
const CALLS = !MEAS ? "" : SHOTS.callouts.map((c) => {
  const f = F[c.framing];
  const [ax, ay] = toScreen(...anchorOf(c.anchor), f);
  const bx = ax + c.dx, by = ay + c.dy; // the box edge point the leader meets (left-middle when dx>0, right-middle when dx<0)
  const boxStyle = c.dx >= 0 ? `left:${bx.toFixed(1)}px; top:${(by - 33).toFixed(1)}px` : `right:${(1920 - bx).toFixed(1)}px; top:${(by - 33).toFixed(1)}px`;
  const len = Math.hypot(bx - ax, by - ay);
  return `<div class="ap-call" id="${c.id}" data-layout-allow-overlap data-layout-allow-occlusion>
  <svg width="1920" height="1080" viewBox="0 0 1920 1080"><line id="${c.id}-ln" x1="${ax.toFixed(1)}" y1="${ay.toFixed(1)}" x2="${bx.toFixed(1)}" y2="${by.toFixed(1)}" stroke="#71717b" stroke-width="2" stroke-dasharray="${len.toFixed(1)}" stroke-dashoffset="${len.toFixed(1)}"/><circle cx="${ax.toFixed(1)}" cy="${ay.toFixed(1)}" r="8" fill="#00bb7f" stroke="#ffffff" stroke-width="3"/></svg>
  <div class="ap-call-box" id="${c.id}-box" style="${boxStyle}">${esc(c.text)}</div>
</div>`;
}).join("\n");

// ---------- data for the timeline ----------
const DATA = {
  shots: SHOTS,
  geom: G,
  price: { yes: YES.charges, no: NO.charges },
  rows: YES.shap.contributions.map((c, i) => ({ yes: WY[i], no: WN[i] })),
  type: P,
};

const timeline = rd("src/app.timeline.js");
const body = `<div id="root" data-composition-id="app" data-width="1920" data-height="1080">
  <div id="ap-cam">
${PAGE}
${MENUS}
${CURSOR}
  </div>
  <div id="ap-calls">
${CALLS}
  </div>
</div>`;

const out = `<template>
<style>
${appCss}
${filmCss}
</style>
${body}
<script>window.__AP = ${JSON.stringify(DATA)};</script>
<script>
${timeline}
</script>
</template>
`;
fs.writeFileSync(path.join(ROOT, "compositions/app.html"), out);

// standalone page for measuring the rebuilt layout (served over http by tools/measure.mjs)
fs.mkdirSync(path.join(ROOT, "tools/out"), { recursive: true });
fs.writeFileSync(path.join(ROOT, "tools/out/app-standalone.html"), `<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0;width:1920px;height:1080px}${appCss}${filmCss.replaceAll('url("assets/', 'url("/assets/')}</style></head><body><div style="position:relative;width:1920px;height:1080px">${body}</div></body></html>`);
console.log("wrote compositions/app.html", (out.length / 1024).toFixed(0) + " KB", MEAS ? "(measured geometry)" : "(live geometry, measure with tools/measure.js)");
