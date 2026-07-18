/* PV-04 "How We Falsified Our Own Espresso Headline" — static interactive.
   Framework-free. Reads the generated, hash-bound data.json; never hard-codes a science number;
   safe DOM only (textContent / createElement / createElementNS; no HTML-string injection, no eval);
   same-origin fetch only. */
(function () {
  "use strict";
  var SVGNS = "http://www.w3.org/2000/svg";
  var doc = document;
  doc.documentElement.className = "js";

  function setText(el, s) {
    while (el.firstChild) { el.removeChild(el.firstChild); }
    el.appendChild(doc.createTextNode(s));
  }
  function fail(msg) {
    var s = doc.getElementById("load-status");
    if (s) { s.className = "error"; setText(s, msg); }
  }

  fetch("data.json", { credentials: "omit" })
    .then(function (r) { if (!r.ok) { throw new Error("HTTP " + r.status); } return r.json(); })
    .then(function (data) { validate(data); init(data); })
    .catch(function () {
      fail("Could not load the generated data on this host. The full result — every number and " +
           "caveat — is in the static summary linked at the top of this page.");
    });

  function validate(d) {
    var need = ["values", "series", "units", "evidence_partitions", "revision_record",
                "scope", "caveat", "fidelity_ceiling", "attribution", "badge", "evidence_strength"];
    for (var i = 0; i < need.length; i++) {
      if (!(need[i] in d)) { throw new Error("missing field " + need[i]); }
    }
    if (!Array.isArray(d.series) || !Array.isArray(d.evidence_partitions)) {
      throw new Error("bad shape");
    }
  }

  // ---- formatting (display rounding only) ----
  function fmt(v, kind) {
    if (typeof v === "boolean") { return v ? "yes" : "no"; }
    var n = Number(v);
    if (kind === "int") { return String(Math.round(n)); }
    if (kind === "num2") { return n.toFixed(2); }
    if (kind === "num3") { return n.toFixed(3); }
    return String(v);
  }

  function seriesByRole(d, role) {
    for (var i = 0; i < d.series.length; i++) {
      if (d.series[i].role === role) { return d.series[i]; }
    }
    return null;
  }

  function init(d) {
    var s = doc.getElementById("load-status");
    if (s) { s.parentNode.removeChild(s); }
    setText(doc.getElementById("badge"), d.badge);
    setText(doc.getElementById("strength"), d.evidence_strength);

    // fill numeric placeholders from d.values (or top-level)
    Array.prototype.forEach.call(doc.querySelectorAll("[data-field]"), function (el) {
      var key = el.getAttribute("data-field");
      var kind = el.getAttribute("data-fmt") || "raw";
      var val = (key in d.values) ? d.values[key] : d[key];
      if (val === undefined || val === null) { return; }
      setText(el, fmt(val, kind));
    });
    // fill text placeholders (scope / caveat / attribution / fidelity_ceiling)
    Array.prototype.forEach.call(doc.querySelectorAll("[data-field-text]"), function (el) {
      var key = el.getAttribute("data-field-text");
      if (d[key] !== undefined) { setText(el, String(d[key])); }
    });

    // Scene 1 — the ordered revision record
    var ol = doc.getElementById("revision-record");
    d.revision_record.forEach(function (q) {
      var li = doc.createElement("li");
      setText(li, q);
      ol.appendChild(li);
    });

    // Scene 2A — a plain unit-lint demonstration (built from the units, no science numbers)
    buildUnitLint(d);

    // evidence partitions table
    buildPartitions(d);

    var obs = seriesByRole(d, "observed");
    var rsm = seriesByRole(d, "derived");
    var model = seriesByRole(d, "simulated");

    // Scene 2 — RSM audit bar chart + table
    drawBars("rsm-fig", rsm,
      "Central-condition cup-mass value in grams, three ways: a literal evaluation of the rounded " +
      "published coefficients (the tallest bar), the project refit, and the observed central mean. The " +
      "refit and the observed mean are close; the literal rounded value is far higher because of " +
      "limited printed precision.");
    buildCatTable("rsm-table", rsm, "cup mass (g)", "num3");

    // Scene 4 — model prominence vs replicate spread bar chart + table
    drawBars("model-fig", model,
      "Model interior prominence in extraction-yield points at 5 bar and 9 bar, next to the mean " +
      "within-cell sample SD. Both model bars are shorter than the descriptive replicate-spread bar.");
    buildCatTable("model-table", model, "EY-points", "num3");

    // Scene 3 — observed replicate dot chart + table (default = raw points)
    var scene3 = { showMeans: false, showSds: false };
    function redrawObs() {
      drawObserved("obs-fig", d, obs, scene3);
      var parts = ["Showing the individual observed replicate points per dial"];
      if (scene3.showMeans) { parts.push("cell means overlaid"); }
      if (scene3.showSds) { parts.push("each cell's own within-cell SD (descriptive, ddof=0) overlaid"); }
      setText(doc.getElementById("obs-readout"),
        parts.join("; ") + ". Middle-minus-coarse (dial 1.7 − dial 2.0) contrast " +
        fmt(d.values.mid_vs_coarse_contrast_EYpt, "num3") + " EY-points (Welch 95% CI [" +
        fmt(d.values.welch_ci95_lo_EYpt, "num3") + ", " + fmt(d.values.welch_ci95_hi_EYpt, "num3") +
        "]); the middle dial is below the coarse dial, so no observed interior maximum.");
    }
    buildObsTable("obs-table", obs);
    doc.getElementById("show-means").addEventListener("change", function (e) {
      scene3.showMeans = e.target.checked; redrawObs();
    });
    doc.getElementById("show-sds").addEventListener("change", function (e) {
      scene3.showSds = e.target.checked; redrawObs();
    });
    redrawObs();

    // scene switching (native radios)
    var titles = { "1": "The headline we wanted (superseded)", "2": "The audit",
                   "3": "The corrected data", "4": "A model can draw it without identifying it" };
    var panels = doc.querySelectorAll(".scene-panel");
    function showScene(n) {
      Array.prototype.forEach.call(panels, function (p) {
        var on = p.getAttribute("data-scene") === n;
        if (on) { p.classList.remove("hidden"); } else { p.classList.add("hidden"); }
      });
      setText(doc.getElementById("scene-readout"), "Scene " + n + " · " + titles[n]);
    }
    Array.prototype.forEach.call(doc.querySelectorAll('input[name="scene"]'), function (r) {
      r.addEventListener("change", function () { if (r.checked) { showScene(r.value); } });
    });
    showScene("1");
  }

  function buildUnitLint(d) {
    var pre = doc.getElementById("unit-lint");
    if (!pre) { return; }
    var lines = [
      "unit-lint: aggregating an extraction target",
      "  solute mass ........ milligram scale (mg)",
      "  TDS / cup mass ..... gram scale (g)",
      "  aggregate(mg, g) ... ERROR: incompatible units — convert to one",
      "                       coherent TDS-derived extraction yield (% EY) first"
    ];
    setText(pre, lines.join("\n"));
  }

  function buildPartitions(d) {
    var host = doc.getElementById("partitions");
    var tbl = doc.createElement("table");
    var thead = doc.createElement("thead"), htr = doc.createElement("tr");
    ["panel", "role", "badge", "strength", "scope"].forEach(function (h) {
      var th = doc.createElement("th"); setText(th, h); htr.appendChild(th);
    });
    thead.appendChild(htr); tbl.appendChild(thead);
    var tb = doc.createElement("tbody");
    d.evidence_partitions.forEach(function (ep) {
      var tr = doc.createElement("tr");
      [ep.partition, ep.role, (ep.badge || "— none —"),
       (ep.strength || ep.status || "—"), ep.scope].forEach(function (c) {
        var td = doc.createElement("td"); setText(td, String(c)); tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
    tbl.appendChild(tb); host.appendChild(tbl);
  }

  // ---- SVG helpers (presentation attributes only; styling via CSS classes) ----
  function svgEl(w, h, label) {
    var el = doc.createElementNS(SVGNS, "svg");
    el.setAttribute("viewBox", "0 0 " + w + " " + h);
    el.setAttribute("role", "img");
    el.setAttribute("width", "100%");
    el.setAttribute("aria-label", label);
    return el;
  }
  function line(x1, y1, x2, y2, cls) {
    var l = doc.createElementNS(SVGNS, "line");
    l.setAttribute("x1", x1); l.setAttribute("y1", y1);
    l.setAttribute("x2", x2); l.setAttribute("y2", y2);
    if (cls) { l.setAttribute("class", cls); }
    return l;
  }
  function rect(x, y, w, h, cls) {
    var r = doc.createElementNS(SVGNS, "rect");
    r.setAttribute("x", x); r.setAttribute("y", y);
    r.setAttribute("width", w); r.setAttribute("height", h);
    if (cls) { r.setAttribute("class", cls); }
    return r;
  }
  function text(x, y, str, cls) {
    var t = doc.createElementNS(SVGNS, "text");
    t.setAttribute("x", x); t.setAttribute("y", y);
    if (cls) { t.setAttribute("class", cls); }
    setText(t, str);
    return t;
  }

  var W = 720, H = 380, ML = 64, MR = 20, MT = 28, MB = 56;

  function niceMax(v) { return Math.ceil(v); }

  function drawBars(figId, series, label) {
    var fig = doc.getElementById(figId);
    var old = fig.querySelector("svg"); if (old) { fig.removeChild(old); }
    var vals = series.values, cats = series.categories;
    var ymax = niceMax(Math.max.apply(null, vals));
    if (ymax <= 0) { ymax = 1; }
    var svg = svgEl(W, H, label);
    var plotH = H - MT - MB, plotW = W - ML - MR;
    function sy(v) { return MT + (1 - v / ymax) * plotH; }
    // axes
    svg.appendChild(line(ML, H - MB, W - MR, H - MB, "axis"));
    svg.appendChild(line(ML, MT, ML, H - MB, "axis"));
    // y ticks (0 .. ymax in integer steps)
    for (var k = 0; k <= ymax; k++) {
      var py = sy(k);
      svg.appendChild(line(ML, py, W - MR, py, "grid"));
      svg.appendChild(text(ML - 8, py + 4, String(k), "tick-y"));
    }
    var n = vals.length, band = plotW / n, bw = band * 0.5;
    for (var i = 0; i < n; i++) {
      var cx = ML + band * (i + 0.5);
      var top = sy(vals[i]);
      svg.appendChild(rect(cx - bw / 2, top, bw, (H - MB) - top, "bar"));
      svg.appendChild(text(cx, top - 6, fmt(vals[i], "num3"), "bar-val"));
      svg.appendChild(text(cx, H - MB + 18, cats[i], "tick-x"));
    }
    svg.appendChild(text((ML + W - MR) / 2, H - 6, series.unit, "axis-label"));
    fig.appendChild(svg);
  }

  function drawObserved(figId, d, obs, opt) {
    var fig = doc.getElementById(figId);
    var old = fig.querySelector("svg"); if (old) { fig.removeChild(old); }
    var reps = obs.replicates, means = obs.values, sds = obs.cell_stds, cats = obs.categories;
    var flat = [];
    reps.forEach(function (c) { c.forEach(function (v) { flat.push(v); }); });
    var lo = Math.floor(Math.min.apply(null, flat));
    var hi = Math.ceil(Math.max.apply(null, flat));
    if (hi - lo < 2) { hi = lo + 2; }
    var svg = svgEl(W, H, "Observed extraction yield in percent by grinder dial. Each dial cell shows " +
      "individual replicate points; the finer cell is lowest and the middle cell is just below the " +
      "coarse cell, so there is no interior maximum.");
    var plotH = H - MT - MB, plotW = W - ML - MR;
    function sy(v) { return MT + (hi - v) / (hi - lo) * plotH; }
    svg.appendChild(line(ML, H - MB, W - MR, H - MB, "axis"));
    svg.appendChild(line(ML, MT, ML, H - MB, "axis"));
    for (var yv = lo; yv <= hi; yv++) {
      var py = sy(yv);
      svg.appendChild(line(ML, py, W - MR, py, "grid"));
      svg.appendChild(text(ML - 8, py + 4, String(yv), "tick-y"));
    }
    var n = reps.length, band = plotW / n;
    for (var i = 0; i < n; i++) {
      var cx = ML + band * (i + 0.5);
      var cell = reps[i], m = cell.length;
      // optional SD whisker (mean ± cell SD) drawn first so points sit on top
      if (opt.showSds) {
        var yTop = sy(means[i] + sds[i]), yBot = sy(means[i] - sds[i]);
        svg.appendChild(line(cx, yTop, cx, yBot, "whisker"));
        svg.appendChild(line(cx - 8, yTop, cx + 8, yTop, "whisker"));
        svg.appendChild(line(cx - 8, yBot, cx + 8, yBot, "whisker"));
      }
      for (var j = 0; j < m; j++) {
        var ox = (j - (m - 1) / 2) * 16;   // deterministic display-only offset (px)
        var px = cx + ox, py2 = sy(cell[j]);
        svg.appendChild(rect(px - 4, py2 - 4, 8, 8, "dot"));
      }
      if (opt.showMeans) {
        var my = sy(means[i]);
        svg.appendChild(line(cx - band / 3, my, cx + band / 3, my, "mean"));
      }
      svg.appendChild(text(cx, H - MB + 18, cats[i], "tick-x"));
    }
    svg.appendChild(text(ML - 44, MT - 10, "% EY", "axis-label"));
    svg.appendChild(text((ML + W - MR) / 2, H - 6, "grinder dial", "axis-label"));
    fig.appendChild(svg);
  }

  // ---- text tables ----
  function tableEl(headers, rows) {
    var tbl = doc.createElement("table");
    var thead = doc.createElement("thead"), tr = doc.createElement("tr");
    headers.forEach(function (h) { var th = doc.createElement("th"); setText(th, h); tr.appendChild(th); });
    thead.appendChild(tr); tbl.appendChild(thead);
    var tb = doc.createElement("tbody");
    rows.forEach(function (r) {
      var row = doc.createElement("tr");
      r.forEach(function (c) { var td = doc.createElement("td"); setText(td, c); row.appendChild(td); });
      tb.appendChild(row);
    });
    tbl.appendChild(tb);
    return tbl;
  }
  function buildCatTable(id, series, valHead, kind) {
    var host = doc.getElementById(id);
    while (host.firstChild) { host.removeChild(host.firstChild); }
    host.appendChild(tableEl(["category", valHead], series.categories.map(function (c, i) {
      return [c, fmt(series.values[i], kind)];
    })));
  }
  function buildObsTable(id, obs) {
    var host = doc.getElementById(id);
    while (host.firstChild) { host.removeChild(host.firstChild); }
    var rows = [];
    obs.categories.forEach(function (c, i) {
      rows.push([c, obs.replicates[i].map(function (v) { return fmt(v, "num3"); }).join(", "),
                 fmt(obs.values[i], "num2"), fmt(obs.cell_stds[i], "num3"), String(obs.ns[i])]);
    });
    host.appendChild(tableEl(["dial", "replicate points (% EY)", "cell mean (% EY)",
                              "cell SD (EY-pt, descriptive)", "n"], rows));
  }
})();
