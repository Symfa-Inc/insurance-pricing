(function () {
  "use strict";
  var D = window.__AP, G = D.geom, SH = D.shots, F = SH.framings;
  // Keep every transform 2D: force3D:"auto" would switch to translate3d mid-tween, promoting the camera to a
  // compositor layer that Chrome rasterizes once and stretches (soft zooms, text that flickers between rasters).
  gsap.config({ force3D: false });
  var tl = gsap.timeline({ paused: true });
  var A0 = SH.appStart; // host data-start in index.html; every time below is GLOBAL film seconds
  // v2 cut: the chapter cards are 2.4 s instead of 3.0 s. Times below stay in the v1 film's seconds (as in
  // shots.json); R() maps them to the v2 film: -0.6 s after the "Why" card, -1.2 s after the "What if" card.
  var R = function (g) { return g < 21.6 ? g : g < 37.8 ? g - 0.6 : g - 1.2; };
  var T = function (g) { return Math.max(0, +(R(g) - A0).toFixed(4)); };
  var FPS = 30;
  var $ = function (id) { return document.getElementById(id); };

  // fromTo that never renders early (overlapping tweens on one property) and clears leftover blur filters
  function ft(t, a, b, g) {
    b.immediateRender = false;
    tl.fromTo(t, a, b, T(g));
    if (b.filter === "blur(0px)") tl.set(t, { filter: "none" }, T(g + (b.duration || 0.5) + 0.02));
  }
  function to(t, v, g) { tl.to(t, v, T(g)); }
  function set(t, v, g) { tl.set(t, v, T(g)); }

  // per-frame text (seek-safe counters and typing)
  function countText(el, g, d, fn, ease) {
    var e = gsap.parseEase(ease || "power2.out"), n = Math.max(1, Math.round(d * FPS)), last = null;
    for (var f = 0; f <= n; f++) {
      var s = fn(e(f / n));
      if (s !== last) { set(el, { textContent: s }, g + f / FPS); last = s; }
    }
  }
  var usd = function (v) { return "$" + v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 }); };

  // ---------------- camera ----------------
  function camAt(f) { return { x: 960 - f.cx * f.s, y: 540 - f.cy * f.s, scale: f.s }; }
  function camSet(g, name) { set("#ap-cam", camAt(F[name]), g); }
  function cam(g, name, d) { var v = camAt(F[name]); v.duration = d || 1.0; v.ease = "power2.inOut"; to("#ap-cam", v, g); }

  // ---------------- cursor ----------------
  var HX = 5, HY = 2.6, cur = { x: 0, y: 0 };
  function curSet(g, x, y) { cur = { x: x, y: y }; set("#ap-cursor", { x: x - HX, y: y - HY }, g); }
  function curMove(g, x, y, d, ease) {
    d = d || 0.6; ease = ease || "power3.inOut";
    to("#ap-cursor", { x: x - HX, y: y - HY, duration: d, ease: ease }, g);
    var mv = { from: cur, to: { x: x, y: y }, g: g, d: d, ease: ease };
    cur = { x: x, y: y };
    return mv;
  }
  function click(g) {
    to("#ap-cursor", { scale: 0.86, duration: 0.07, ease: "power2.out" }, g);
    to("#ap-cursor", { scale: 1, duration: 0.14, ease: "power2.out" }, g + 0.1);
  }
  var mid = function (b, dx) { return [b.x + (dx == null ? b.w / 2 : dx), b.y + b.h / 2]; };

  // ---------------- fields ----------------
  var RING = "0 0 0 1px #18181b", NORING = "0 0 0 0px rgba(24,24,27,0)";
  function focusOn(id, g) { set("#ap-" + id, { borderColor: "#18181b", boxShadow: RING }, g); }
  function focusOff(id, g) { set("#ap-" + id, { borderColor: "#e4e4e7", boxShadow: NORING }, g); if ($("ap-" + id + "-caret")) set("#ap-" + id + "-caret", { opacity: 0 }, g); }
  // click into a number input, select its value, type the new one character by character
  function typeInto(id, gClick, gType, dt) {
    focusOn(id, gClick);
    set("#ap-" + id + "-caret", { opacity: 1 }, gClick + 0.02);
    set("#ap-" + id + "-old", { backgroundColor: "#b3d7ff" }, gClick + 0.16); // select all
    set("#ap-" + id + "-caret", { opacity: 0 }, gClick + 0.16);
    var s = D.type[id].new;
    set("#ap-" + id + "-old", { display: "none", backgroundColor: "rgba(0,0,0,0)" }, gType);
    set("#ap-" + id + "-caret", { opacity: 1 }, gType);
    // one span per typed character (setting "30." as textContent would be read as the number 30)
    for (var i = 0; i < s.length; i++) set("#ap-" + id + "-c" + i, { display: "inline" }, gType + i * dt);
    return gType + (s.length - 1) * dt;
  }
  function swapValue(id, g) { // select value change, a short crossfade
    ft("#ap-" + id + "-v0", { opacity: 1 }, { opacity: 0, duration: 0.1, ease: "power1.in" }, g);
    ft("#ap-" + id + "-v1", { opacity: 0 }, { opacity: 1, duration: 0.14, ease: "power1.out" }, g + 0.04);
  }

  // ---------------- dropdown menus ----------------
  function menuTop(k) { return G[k].y + G[k].h + 4; }
  function rowY(k, i) { return menuTop(k) + 1 + 4 + 32 * i + 16; }
  function menuOpen(k, g) { ft("#ap-menu-" + k, { opacity: 0, scaleY: 0.96, y: -4 }, { opacity: 1, scaleY: 1, y: 0, duration: 0.2, ease: "power2.out" }, g); }
  function menuClose(k, g) { to("#ap-menu-" + k, { opacity: 0, scaleY: 0.98, y: -2, duration: 0.14, ease: "power2.in" }, g); }
  // the highlight follows the cursor tip across rows, frame by frame
  function menuTrack(k, n, mv) {
    var e = gsap.parseEase(mv.ease), nf = Math.round(mv.d * FPS), prev = -1, top = menuTop(k) + 5;
    for (var f = 0; f <= nf; f++) {
      var y = mv.from.y + (mv.to.y - mv.from.y) * e(f / nf);
      var idx = Math.floor((y - top) / 32);
      if (idx < 0 || idx >= n) idx = -1;
      if (idx !== prev) {
        var g = mv.g + f / FPS;
        if (idx >= 0) set("#ap-menu-" + k + "-hl", { y: idx * 32, opacity: 1 }, g);
        else set("#ap-menu-" + k + "-hl", { opacity: 0 }, g);
        prev = idx;
      }
    }
  }
  function pick(k, g) { to("#ap-menu-" + k + "-hl", { backgroundColor: "#e4e4e7", duration: 0.06 }, g); }

  // ---------------- Estimate button ----------------
  function btnHover(g) { to("#ap-btn", { backgroundColor: "#27272a", duration: 0.12, ease: "power1.out" }, g); }
  function btnPress(g) {
    to("#ap-btn", { scale: 0.98, duration: 0.06, ease: "power2.out" }, g);
    to("#ap-btn", { scale: 1, duration: 0.14, ease: "power2.out" }, g + 0.09);
  }
  function btnPending(g, until) { // disabled:opacity-40 + spinner + "Estimating" (the app's own pending state)
    to("#ap-btn", { opacity: 0.4, backgroundColor: "#18181b", duration: 0.12 }, g);
    ft("#ap-btn-a", { opacity: 1 }, { opacity: 0, duration: 0.1 }, g);
    ft("#ap-btn-b", { opacity: 0 }, { opacity: 1, duration: 0.12 }, g + 0.03);
    spin("#ap-btn-spin", g, until);
  }
  function btnDone(g) { // back to "Estimate", still disabled until an input changes
    ft("#ap-btn-b", { opacity: 1 }, { opacity: 0, duration: 0.12 }, g);
    ft("#ap-btn-a", { opacity: 0 }, { opacity: 1, duration: 0.14 }, g + 0.04);
  }
  function spin(sel, g0, g1) { // animate-spin: one turn per second, linear
    ft(sel, { rotation: 0, transformOrigin: "50% 50%" }, { rotation: 360 * (g1 - g0), duration: g1 - g0, ease: "none" }, g0);
  }

  // ---------------- callouts ----------------
  function callout(c) {
    var g = c.t, h = c.hold, id = "#" + c.id;
    var len = parseFloat($(c.id + "-ln").getAttribute("stroke-dasharray"));
    ft(id, { opacity: 0 }, { opacity: 1, duration: 0.18, ease: "power2.out" }, g);
    ft(id + "-ln", { attr: { "stroke-dashoffset": len } }, { attr: { "stroke-dashoffset": 0 }, duration: 0.28, ease: "power2.out" }, g);
    ft(id + "-box", { opacity: 0, filter: "blur(6px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.22, ease: "power2.out" }, g + 0.14);
    to(id, { opacity: 0, duration: 0.2, ease: "power2.in" }, g + h);
  }
  // ---------------- focus: the panels the shot is not about fade to the ground, so a push-in never shows a
  // neighbouring panel cut by the frame edge (and the idle "Enter your details" card is never on screen) ----------------
  var FG = { hdr: "#ap-hdr", fcol: "#ap-fcol", rcol: "#ap-rcol", price: "#ap-w-price", interp: "#ap-w-interp", shap: "#ap-w-shap" };
  var fs = {};
  function focus(g, on, d) {
    Object.keys(on).forEach(function (k) {
      var v = on[k];
      if (fs[k] === v) return;
      if (!d || fs[k] == null) set(FG[k], { opacity: v }, g);
      else ft(FG[k], { opacity: fs[k] }, { opacity: v, duration: d, ease: "power2.inOut" }, g);
      fs[k] = v;
    });
  }

  var CALL = {};
  SH.callouts.forEach(function (c) { CALL[c.id] = c; });

  // =====================================================================================
  // initial state (app host starts at 5.3; it is covered by the intro sheet until 5.4)
  camSet(A0, "F1");
  set("#ap-cursor", { scale: 1 }, A0);
  set(["#ap-card-price", "#ap-card-interp", "#ap-card-shap"], { opacity: 0, y: 8 }, A0);
  for (var r = 0; r < 6; r++) set(["#ap-bp-" + r, "#ap-bn-" + r], { width: "0%" }, A0);
  set("#ap-ilist", { height: G.ilistYes.h }, A0);
  set(".ap-call", { opacity: 0 }, A0);
  set("#ap-menu-region-hl", { opacity: 0, y: 0 }, A0);
  set("#ap-menu-smoker-hl", { opacity: 0, y: 0 }, A0);
  curSet(A0, 660, 760); // below the frame at F1
  focus(A0, { hdr: 0, fcol: 1, rcol: 0, price: 1, interp: 1, shap: 1 });

  // ---- S2 (5.95-10.2): type the applicant's age, BMI and children ----
  var p = mid(G.age, 46);
  curMove(6.0, p[0], p[1], 0.62);
  click(6.65);
  typeInto("age", 6.65, 7.05, 0.12);

  p = mid(G.bmi, 46);
  curMove(7.45, p[0], p[1], 0.55);
  focusOff("age", 8.05);
  click(8.05);
  typeInto("bmi", 8.05, 8.4, 0.11);

  p = mid(G.children, 46);
  curMove(9.0, p[0], p[1], 0.5);
  focusOff("bmi", 9.55);
  click(9.55);
  typeInto("children", 9.55, 9.9, 0.12);

  // ---- S3 (10.2-14.0): pick the region, press Estimate ----
  cam(10.2, "F2", 1.0);
  p = mid(G.region, 60);
  curMove(10.95, p[0], p[1], 0.55);
  focusOff("children", 11.65);
  click(11.65);
  focusOn("region", 11.65);
  menuOpen("region", 11.7);
  var mv = curMove(12.0, G.region.x + 64, rowY("region", 1), 0.45, "power2.inOut");
  menuTrack("region", 4, mv);
  click(12.6);
  pick("region", 12.6);
  menuClose("region", 12.7);
  swapValue("region", 12.72);

  p = mid(G.button);
  curMove(12.95, p[0] - 8, p[1] + 2, 0.55);
  btnHover(13.5);
  click(13.75);
  btnPress(13.75);
  focusOff("region", 13.75);
  btnPending(13.85, 15.9);
  // result column: idle -> the app's pending card
  ft("#ap-idle", { opacity: 1 }, { opacity: 0, duration: 0.15 }, 13.85);
  ft("#ap-pending", { opacity: 0 }, { opacity: 1, duration: 0.15 }, 13.85);
  spin("#ap-pend-spin", 13.85, 16.05);

  // ---- S4 (14.0-21.0): the estimate arrives ----
  cam(14.0, "CTXa", 1.1);
  focus(14.0, { hdr: 1, rcol: 1 }, 1.1);
  ft("#ap-pending", { opacity: 1 }, { opacity: 0, duration: 0.15 }, 15.9);
  btnDone(15.9);
  // animate-fade-in-up: 0.4 s ease-out, 100 ms apart (the app's own entrance)
  ["#ap-card-price", "#ap-card-interp", "#ap-card-shap"].forEach(function (c, i) {
    ft(c, { opacity: 0, y: 8 }, { opacity: 1, y: 0, duration: 0.4, ease: "power1.out" }, 15.9 + 0.1 * i);
  });
  countText("#ap-price", 15.9, 1.1, function (k) { return usd(Math.round(D.price.yes * k * 100) / 100); });
  D.rows.forEach(function (row, i) {
    var y = row.yes, g = 16.2 + 0.06 * i;
    ft(y.pos ? "#ap-bp-" + i : "#ap-bn-" + i, { width: "0%" }, { width: y.w + "%", duration: 0.7, ease: "power2.out" }, g);
    countText("#ap-nv-" + i, g, 0.7, function (k) { return String(Math.round(y.v * k) || 0); });
  });
  curMove(15.0, 700, 760, 0.7, "power2.inOut");

  cam(16.0, "CTX", 1.0);   // the page grows as the cards arrive: follow it down
  cam(17.6, "F3", 1.0);
  focus(17.6, { hdr: 0, fcol: 0, interp: 0, shap: 0 }, 1.0);
  callout(CALL["ap-call-model"]);

  // ---- card "Why this price?" covers 21.0-24.0; reframe behind it ----
  camSet(22.2, "F4");
  focus(22.2, { price: 0, shap: 1 });
  curSet(22.2, 1250, 1040);

  // ---- S5 (24.0-31.0): feature impact ----
  p = mid(G.icShap);
  curMove(24.1, p[0], p[1], 0.6);
  to("#ap-ic-shap-svg", { color: "#71717b", duration: 0.12 }, 24.7);
  ft("#ap-tip-shap", { opacity: 0 }, { opacity: 1, duration: 0.15, ease: "power1.out" }, 24.75);
  curMove(26.85, 1250, 1040, 0.6, "power2.inOut");
  to("#ap-tip-shap", { opacity: 0, duration: 0.15 }, 26.9);
  to("#ap-ic-shap-svg", { color: "#d4d4d8", duration: 0.15 }, 26.9);
  callout(CALL["ap-call-smoke"]);
  callout(CALL["ap-call-color"]);

  // ---- S6 (31.0-37.2): the written interpretation ----
  cam(31.0, "F5", 1.0);
  focus(31.0, { shap: 0, interp: 1 }, 1.0);
  curMove(31.0, 1520, 700, 1.0, "power2.inOut");
  callout(CALL["ap-call-ai"]);
  ft("#ap-mark-0", { opacity: 1, scaleX: 0 }, { opacity: 1, scaleX: 1, duration: 0.55, ease: "power2.inOut" }, 34.15);
  callout(CALL["ap-call-match"]);

  // ---- card "What if she quits smoking?" covers 37.2-40.2 ----
  camSet(38.7, "F6"); // v2 38.7 -> 37.5, the middle of the "What if" card
  focus(38.7, { fcol: 1, rcol: 0, price: 1, interp: 1, shap: 1 });
  curSet(38.7, 700, 760);

  // ---- S7 (40.2-43.8): smoker -> No, Estimate again ----
  p = mid(G.smoker, 60);
  curMove(40.3, p[0], p[1], 0.6);
  click(41.05);
  focusOn("smoker", 41.05);
  menuOpen("smoker", 41.1);
  mv = curMove(41.45, G.smoker.x + 64, rowY("smoker", 0), 0.4, "power2.inOut");
  menuTrack("smoker", 2, mv);
  click(42.0);
  pick("smoker", 42.0);
  menuClose("smoker", 42.1);
  swapValue("smoker", 42.12);
  to("#ap-btn", { opacity: 1, duration: 0.25, ease: "power1.out" }, 42.2); // inputs changed: Estimate is enabled again

  p = mid(G.button);
  curMove(42.6, p[0] - 8, p[1] + 2, 0.6);
  btnHover(43.2);
  click(43.45);
  btnPress(43.45);
  focusOff("smoker", 43.45);
  btnPending(43.55, 44.8);
  to("#ap-results", { opacity: 0.45, duration: 0.2, ease: "power1.out" }, 43.6);

  // ---- S8 (43.8-55.2): the new estimate ----
  cam(43.8, "CTX", 1.1);
  focus(43.8, { hdr: 1, rcol: 1 }, 1.1);
  to("#ap-results", { opacity: 1, duration: 0.25, ease: "power1.out" }, 44.8);
  btnDone(44.8);
  countText("#ap-price", 44.85, 1.4, function (k) {
    return usd(Math.round((D.price.yes + (D.price.no - D.price.yes) * k) * 100) / 100);
  }, "power2.inOut");
  D.rows.forEach(function (row, i) {
    var a = row.yes, b = row.no, g = 44.9 + 0.05 * i;
    if (a.pos === b.pos) {
      var bar = a.pos ? "#ap-bp-" + i : "#ap-bn-" + i;
      if (a.w !== b.w) ft(bar, { width: a.w + "%" }, { width: b.w + "%", duration: 0.9, ease: "power2.inOut" }, g);
    } else {
      ft(a.pos ? "#ap-bp-" + i : "#ap-bn-" + i, { width: a.w + "%" }, { width: "0%", duration: 0.45, ease: "power2.in" }, g);
      ft(b.pos ? "#ap-bp-" + i : "#ap-bn-" + i, { width: "0%" }, { width: b.w + "%", duration: 0.55, ease: "power2.out" }, g + 0.45);
    }
    if (a.v !== b.v) {
      var e = gsap.parseEase("power2.inOut"), n = Math.round(1.0 * FPS), lastS = null, lastNeg = a.v < 0;
      for (var f = 0; f <= n; f++) {
        var v = Math.round(a.v + (b.v - a.v) * e(f / n)) || 0, s = String(v), gg = g + f / FPS;
        if (s !== lastS) { set("#ap-nv-" + i, { textContent: s }, gg); lastS = s; }
        var neg = v < 0;
        if (neg !== lastNeg) {
          set("#ap-num-" + i, { color: neg ? "#ff2357" : "#009767" }, gg);
          set("#ap-ns-" + i, { display: neg ? "none" : "inline" }, gg);
          lastNeg = neg;
        }
      }
    }
    if ($("ap-rv-" + i + "-b")) {
      ft("#ap-rv-" + i + "-a", { opacity: 1 }, { opacity: 0, duration: 0.12 }, g + 0.05);
      ft("#ap-rv-" + i + "-b", { opacity: 0 }, { opacity: 1, duration: 0.16 }, g + 0.1);
    }
  });
  // interpretation: each bullet swaps to the new run's text, and the card resizes smoothly
  for (var li = 0; li < 5; li++) {
    ft("#ap-li-yes-" + li, { opacity: 1, filter: "blur(0px)" }, { opacity: 0, filter: "blur(4px)", duration: 0.18, ease: "power2.in" }, 44.9 + 0.06 * li);
    ft("#ap-li-no-" + li, { opacity: 0, filter: "blur(4px)" }, { opacity: 1, filter: "blur(0px)", duration: 0.24, ease: "power2.out" }, 45.08 + 0.06 * li);
  }
  ft("#ap-ilist", { height: G.ilistYes.h }, { height: G.ilistNo.h, duration: 0.6, ease: "power2.inOut" }, 44.95);
  curMove(45.0, 700, 760, 0.6, "power2.inOut");

  curMove(46.6, 1250, 1080, 0.8, "power2.inOut"); // park the cursor below the frame for the push-ins and the wide end shot
  cam(46.6, "F3", 1.0);
  focus(46.6, { hdr: 0, fcol: 0, interp: 0, shap: 0 }, 1.0);
  callout(CALL["ap-call-drop"]);
  cam(50.2, "F4n", 1.0);
  focus(50.2, { price: 0, shap: 1 }, 1.0);
  callout(CALL["ap-call-flip"]);
  cam(53.7, "FULL", 1.1);
  focus(53.7, { hdr: 1, fcol: 1, price: 1, interp: 1 }, 1.1);

  tl.to({}, { duration: 0.01 }, T(55.79));
  window.__timelines["app"] = tl;
})();
