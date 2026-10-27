// In-page measurement of the rebuilt app (tools/out/app-standalone.html, served from the project root over http).
// Paste/evaluate this function in a 1920x1080 page; it returns JSON for assets/data/geom-recreation.json.
// The cursor targets and callout anchors in the film come from these numbers, never from guesses.
async () => {
  await document.fonts.ready;
  const r = (el) => { const b = el.getBoundingClientRect(); return { x: +b.x.toFixed(2), y: +b.y.toFixed(2), w: +b.width.toFixed(2), h: +b.height.toFixed(2) }; };
  const $ = (id) => document.getElementById(id);
  const textRect = (el, needle) => {
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      const i = n.data.indexOf(needle);
      if (i >= 0) { const rg = document.createRange(); rg.setStart(n, i); rg.setEnd(n, i + needle.length); return r(rg); }
    }
    return null;
  };
  // results visible for measuring
  for (const id of ["ap-card-price", "ap-card-interp", "ap-card-shap"]) $(id).style.opacity = 1;
  const out = {};
  for (const k of ["age", "bmi", "children", "smoker", "region", "sex"]) out[k] = r($("ap-" + k));
  out.button = r($("ap-btn"));
  out.panel = r($("ap-panel"));
  out.header = r($("ap-hdr"));
  out.li0dot = r($("ap-li-yes-0").querySelector("span.rounded-full"));
  out.li1dot = r($("ap-li-yes-1").querySelector("span.rounded-full"));
  const price = r($("ap-price"));
  const prg = document.createRange(); prg.selectNodeContents($("ap-price"));
  price.textW = +prg.getBoundingClientRect().width.toFixed(2);
  out.price = price;
  out.badge = r($("ap-badge"));
  out.icShap = r($("ap-ic-shap"));
  out.tipShap = r($("ap-tip-shap"));
  out.cards = ["ap-card-price", "ap-card-interp", "ap-card-shap"].map((id) => r($(id)));
  out.ilistYes = { h: $("ap-ilist").getBoundingClientRect().height };
  const ulNo = $("ap-ul-no");
  out.ilistNo = { h: ulNo.getBoundingClientRect().height };
  out.lisYes = [...document.querySelectorAll("#ap-ul-yes li")].map(r);
  out.lisNo = [...document.querySelectorAll("#ap-ul-no li")].map(r);
  const li0 = r($("ap-li-yes-0"));
  const amt = textRect($("ap-li-yes-0"), "$8,602");
  out.li0 = Object.assign(li0, { amt });
  out.rows = [...Array(6).keys()].map((i) => { const t = r($("ap-track-" + i)); return { trackX: t.x, trackY: t.y, trackW: t.w, row: r($("ap-row-" + i)) }; });
  out.menuRegion = r($("ap-menu-region"));
  out.menuSmoker = r($("ap-menu-smoker"));
  out.fontCheck = { geist: document.fonts.check('16px "Geist"'), mono: document.fonts.check('16px "Geist Mono"'), priceFont: getComputedStyle($("ap-price")).fontFamily };
  return JSON.stringify(out);
}
