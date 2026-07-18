"use strict";
/* PV-03 "The Cup Hides the Clock" — framework-free progressive enhancement.
 * Reads the generated, hash-bound data.json (no hand-typed science numbers; no network beyond the
 * same-origin data file; no eval / new Function / innerHTML of untrusted data). All displayed values
 * come from the data; SVG coordinates are computed, not literal. */
(function () {
  var SVGNS = "http://www.w3.org/2000/svg";
  var root = document.documentElement;
  root.classList.remove("no-js");
  root.classList.add("js");

  function dig(obj, path) {
    var cur = obj, segs = path.split("."), i;
    for (i = 0; i < segs.length; i++) {
      if (cur == null) return undefined;
      cur = Array.isArray(cur) ? cur[parseInt(segs[i], 10)] : cur[segs[i]];
    }
    return cur;
  }
  function nearest10(x) { return Math.round(x / 10) * 10; }
  function commas(n) { return String(n).replace(/\B(?=(\d{3})+(?!\d))/g, ","); }
  function pct(x, dp) { return (Math.round(x * Math.pow(10, dp)) / Math.pow(10, dp)) + "%"; }
  function num(x, dp) { var f = Math.pow(10, dp); return String(Math.round(x * f) / f); }
  function setText(el, s) { while (el.firstChild) el.removeChild(el.firstChild); el.appendChild(document.createTextNode(s)); }

  function fail(msg) {
    var el = document.getElementById("load-status");
    if (el) { setText(el, msg); el.classList.add("notproof"); }
  }

  fetch("data.json", { credentials: "omit" })
    .then(function (r) { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
    .then(function (data) { init(data); })
    .catch(function () {
      fail("Could not load the generated data on this host. The full result — every number and " +
           "caveat — is in the static summary linked at the top of this page.");
    });

  function init(data) {
    var v = data.values, ax = data.axes, tol = data.near_optimal_sse_tol;
    var status = document.getElementById("load-status");
    if (status) { status.parentNode.removeChild(status); }

    /* fill every [data-field] placeholder from the data (display rounding only) */
    fillFields(data);

    /* provenance line */
    var prov = document.getElementById("provenance");
    if (prov) setText(prov, "Generated from " + data.source_bundle + " · source commit " +
      data.source_commit.slice(0, 10) + " · bundle SHA-256 " + data.source_bundle_sha256.slice(0, 12) + "…");

    scene1(v, ax, tol);
    scene2(ax);
    scene3(v);
  }

  function fillFields(data) {
    var nodes = document.querySelectorAll("[data-field]");
    Array.prototype.forEach.call(nodes, function (el) {
      var key = el.getAttribute("data-field");
      var fmt = el.getAttribute("data-fmt") || "raw";
      var val = dig(data.values, key);
      if (val === undefined) val = dig(data, key);
      if (val === undefined) return;
      var out;
      if (fmt === "approx1000") out = "≈" + commas(nearest10(val));
      else if (fmt === "pct1") out = pct(val, 1);
      else if (fmt === "num2") out = num(val, 2);
      else if (fmt === "pctgrid") out = Math.round(val * 100) + "%";
      else if (fmt === "int") out = commas(Math.round(val));
      else out = String(val);
      setText(el, out);
    });
  }

  /* ---- Scene 1: same cup, different hidden parameters ---- */
  function scene1(v, ax, tol) {
    var rates = ax.profile_rates, cstar = ax.profile_c_star, sse = ax.profile_sse, sseMin = ax.profile_sse_min;
    var n = rates.length, i;
    var nearOpt = [];
    for (i = 0; i < n; i++) if (sse[i] <= sseMin * (1 + tol)) nearOpt.push(i);
    var start = rates.indexOf(v.rate_star);
    if (start < 0) start = Math.floor(n / 2);

    var slider = document.getElementById("rate-slider");
    slider.min = "0"; slider.max = String(n - 1); slider.step = "1"; slider.value = String(start);

    var rRate = document.getElementById("r-rate");
    var rInv = document.getElementById("r-inv");
    var rSse = document.getElementById("r-sse");
    var rNear = document.getElementById("r-near");

    var svg = drawProfile(rates, sse, sseMin, tol);
    document.getElementById("profile-fig").appendChild(svg);
    var marker = svg.querySelector(".marker");

    function update(idx) {
      var isNear = sse[idx] <= sseMin * (1 + tol);
      setText(rRate, num(rates[idx], 2));
      setText(rInv, num(cstar[idx], 2) + " g/L");
      setText(rSse, num(sse[idx] / sseMin, 2) + "× the best fit");
      rNear.className = "pill" + (isNear ? " near" : "");
      setText(rNear, isNear ? "near-optimal (fit within 10%)" : "outside the near-optimal set");
      var p = plot(rates, sse, idx);
      marker.setAttribute("cx", String(p.x));
      marker.setAttribute("cy", String(p.y));
    }
    slider.addEventListener("input", function () { update(parseInt(slider.value, 10)); });
    update(start);

    /* "follow the valley": step through the near-optimal indices */
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    var btn = document.getElementById("follow-valley");
    var k = 0, timer = null;
    btn.addEventListener("click", function () {
      if (timer) { clearInterval(timer); timer = null; setText(btn, "Follow the valley"); return; }
      if (reduce) {                       /* no animation: jump across the near-optimal set */
        slider.value = String(nearOpt[nearOpt.length - 1]); update(nearOpt[nearOpt.length - 1]);
        return;
      }
      setText(btn, "Stop");
      timer = setInterval(function () {
        var idx = nearOpt[k % nearOpt.length]; k++;
        slider.value = String(idx); update(idx);
        if (k >= nearOpt.length) { clearInterval(timer); timer = null; setText(btn, "Follow the valley"); }
      }, 260);
    });

    /* text-table equivalent of the profile plot */
    buildTable("profile-table", ["rate", "best-fit inventory (g/L)", "fit vs best (×)", "near-optimal"],
      rates.map(function (r, j) {
        return [num(r, 2), num(cstar[j], 2), num(sse[j] / sseMin, 2),
                (sse[j] <= sseMin * (1 + tol)) ? "yes" : "no"];
      }));
  }

  /* ---- Scene 2: keep or throw away the clock ---- */
  function scene2(ax) {
    var rates = ax.pc_caffeine_rates, frac = ax.pc_caffeine_fraction_mape, cup = ax.pc_caffeine_cup_mape;
    var svg = drawTwo(rates, frac, cup);
    document.getElementById("clock-fig").appendChild(svg);
    var radios = document.querySelectorAll("input[name='clock']");
    var lineF = svg.querySelector(".line-frac"), lineC = svg.querySelector(".line-cup");
    var note = document.getElementById("clock-note");
    function apply() {
      var mode = document.querySelector("input[name='clock']:checked").value;
      var showF = mode === "fractions";
      lineF.style.opacity = showF ? "1" : "0.15";
      lineC.style.opacity = showF ? "0.15" : "1";
      setText(note, showF
        ? "Timed fractions keep a sharp rate optimum (a deep trough) — the rate is constrained."
        : "The whole cup flattens the objective — the rate is barely constrained.");
    }
    Array.prototype.forEach.call(radios, function (r) { r.addEventListener("change", apply); });
    apply();
    buildTable("clock-table", ["rate", "timed-fraction fit (MAPE %)", "whole-cup fit (MAPE %)"],
      rates.map(function (r, j) { return [num(r, 2), num(frac[j], 2), num(cup[j], 2)]; }));
  }

  /* ---- Scene 3: prediction is not identification ---- */
  function scene3(v) {
    var m = v.held_out_model_mape, c = v.held_out_const_mape;
    var better = m < c;
    var el = document.getElementById("skill-verdict");
    setText(el, better
      ? "The mechanistic model is slightly better on the pooled average, but barely — and it is worse on many individual points."
      : "The mechanistic model does not beat the level-only constant on the pooled average.");
  }

  /* ---- accessible SVG plots (role=img + aria-label + text table alongside) ---- */
  var W = 340, H = 190, PADL = 40, PADB = 30, PADT = 12, PADR = 12;
  function sx(t, lo, hi) { return PADL + (Math.log(t) - Math.log(lo)) / (Math.log(hi) - Math.log(lo)) * (W - PADL - PADR); }
  function sy(y, lo, hi) { return PADT + (1 - (y - lo) / (hi - lo)) * (H - PADT - PADB); }

  function plot(rates, sse, idx) {
    var lo = rates[0], hi = rates[rates.length - 1], ymin = Math.min.apply(null, sse), ymax = Math.max.apply(null, sse);
    return { x: sx(rates[idx], lo, hi), y: sy(sse[idx], ymin, ymax) };
  }
  function svgEl() {
    var s = document.createElementNS(SVGNS, "svg");
    s.setAttribute("viewBox", "0 0 " + W + " " + H);
    s.setAttribute("role", "img");
    return s;
  }
  function polyline(pts, cls, dash) {
    var pl = document.createElementNS(SVGNS, "polyline");
    pl.setAttribute("points", pts.map(function (p) { return p[0] + "," + p[1]; }).join(" "));
    pl.setAttribute("fill", "none"); pl.setAttribute("stroke-width", "2");
    pl.setAttribute("class", cls);
    if (dash) pl.setAttribute("stroke-dasharray", dash);
    return pl;
  }
  function axes(s) {
    var ax = document.createElementNS(SVGNS, "path");
    ax.setAttribute("d", "M " + PADL + " " + PADT + " L " + PADL + " " + (H - PADB) + " L " + (W - PADR) + " " + (H - PADB));
    ax.setAttribute("fill", "none"); ax.setAttribute("stroke", "currentColor"); ax.setAttribute("stroke-width", "1");
    s.appendChild(ax);
  }
  function drawProfile(rates, sse, sseMin, tol) {
    var s = svgEl();
    s.setAttribute("aria-label", "Fit error versus release rate: a flat valley near the best fit over most of the tested rate range.");
    axes(s);
    var lo = rates[0], hi = rates[rates.length - 1], ymin = Math.min.apply(null, sse), ymax = Math.max.apply(null, sse);
    /* 10% near-optimal band */
    var bandY = sy(sseMin * (1 + tol), ymin, ymax);
    var band = document.createElementNS(SVGNS, "rect");
    band.setAttribute("x", String(PADL)); band.setAttribute("y", String(sy(ymin, ymin, ymax)));
    band.setAttribute("width", String(W - PADL - PADR)); band.setAttribute("height", String(bandY - sy(ymin, ymin, ymax)));
    band.setAttribute("class", "band");
    s.appendChild(band);
    s.appendChild(polyline(rates.map(function (r, j) { return [sx(r, lo, hi), sy(sse[j], ymin, ymax)]; }), "line-sse"));
    var mk = document.createElementNS(SVGNS, "circle");
    mk.setAttribute("r", "5"); mk.setAttribute("class", "marker");
    s.appendChild(mk);
    label(s, "release rate (log)", "fit error (SSE)");
    return s;
  }
  function drawTwo(rates, a, b) {
    var s = svgEl();
    s.setAttribute("aria-label", "Fit error versus rate for two ways of scoring: timed fractions give a sharp trough; the whole cup is nearly flat.");
    axes(s);
    var lo = rates[0], hi = rates[rates.length - 1];
    var ymax = Math.max(Math.max.apply(null, a), Math.max.apply(null, b)), ymin = 0;
    s.appendChild(polyline(rates.map(function (r, j) { return [sx(r, lo, hi), sy(a[j], ymin, ymax)]; }), "line-frac"));
    s.appendChild(polyline(rates.map(function (r, j) { return [sx(r, lo, hi), sy(b[j], ymin, ymax)]; }), "line-cup", "6 4"));
    label(s, "release rate (log)", "fit error (MAPE)");
    return s;
  }
  function label(s, xl, yl) {
    var t1 = document.createElementNS(SVGNS, "text");
    t1.setAttribute("x", String((W) / 2)); t1.setAttribute("y", String(H - 4));
    t1.setAttribute("text-anchor", "middle"); t1.setAttribute("font-size", "10"); setText(t1, xl); s.appendChild(t1);
    var t2 = document.createElementNS(SVGNS, "text");
    t2.setAttribute("transform", "translate(11," + (H / 2) + ") rotate(-90)");
    t2.setAttribute("text-anchor", "middle"); t2.setAttribute("font-size", "10"); setText(t2, yl); s.appendChild(t2);
  }

  function buildTable(id, headers, rows) {
    var host = document.getElementById(id);
    if (!host) return;
    var t = document.createElement("table"); t.className = "data";
    var thead = document.createElement("thead"), htr = document.createElement("tr");
    headers.forEach(function (h) { var th = document.createElement("th"); setText(th, h); htr.appendChild(th); });
    thead.appendChild(htr); t.appendChild(thead);
    var tb = document.createElement("tbody");
    rows.forEach(function (r) {
      var tr = document.createElement("tr");
      r.forEach(function (c) { var td = document.createElement("td"); setText(td, String(c)); tr.appendChild(td); });
      tb.appendChild(tr);
    });
    t.appendChild(tb); host.appendChild(t);
  }
})();
