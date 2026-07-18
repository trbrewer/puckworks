/* PV-05 "More Physics Made It Worse" — static interactive.
   Framework-free. Reads the generated, hash-bound data.json; never hard-codes a science number;
   safe DOM only (no innerHTML/eval); same-origin fetch only. */
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
    var need = ["values", "series", "time_axis_s", "units", "composition_checklist",
                "scope", "caveat", "attribution", "badge", "evidence_strength"];
    for (var i = 0; i < need.length; i++) {
      if (!(need[i] in d)) { throw new Error("missing field " + need[i]); }
    }
    if (!Array.isArray(d.series) || !Array.isArray(d.time_axis_s)) {
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

  function seriesBy(d, sub) {
    for (var i = 0; i < d.series.length; i++) {
      if (d.series[i].label.indexOf(sub) !== -1) { return d.series[i]; }
    }
    return null;
  }

  function init(d) {
    var s = doc.getElementById("load-status");
    if (s) { s.parentNode.removeChild(s); }
    setText(doc.getElementById("badge"), d.badge);
    setText(doc.getElementById("strength"), d.evidence_strength);

    // fill numeric placeholders
    var nodes = doc.querySelectorAll("[data-field]");
    Array.prototype.forEach.call(nodes, function (el) {
      var key = el.getAttribute("data-field");
      var kind = el.getAttribute("data-fmt") || "raw";
      var val = (key in d.values) ? d.values[key] : d[key];
      if (val === undefined || val === null) { return; }
      setText(el, fmt(val, kind));
    });
    // fill text placeholders (scope / caveat / attribution)
    Array.prototype.forEach.call(doc.querySelectorAll("[data-field-text]"), function (el) {
      var key = el.getAttribute("data-field-text");
      if (d[key] !== undefined) { setText(el, String(d[key])); }
    });

    // checklist
    var ul = doc.getElementById("checklist");
    d.composition_checklist.forEach(function (q) {
      var li = doc.createElement("li");
      setText(li, q);
      ul.appendChild(li);
    });

    var obs = seriesBy(d, "Observed");
    var models = {
      const: { s: seriesBy(d, "Constant baseline"), rmse: d.values.const_baseline_rmse_g_per_s,
               eps: null, name: "Constant baseline" },
      extraction: { s: seriesBy(d, "Extraction-only prediction"),
                    rmse: d.values.extraction_only_rmse_g_per_s,
                    eps: seriesBy(d, "porosity — extraction"), name: "Extraction only" },
      composite: { s: seriesBy(d, "swelling composite"),
                   rmse: d.values.composite_rmse_g_per_s,
                   eps: seriesBy(d, "porosity — composite"), name: "Extraction + swelling" }
    };

    var state = { key: "extraction", showEps: false };

    function redraw() {
      var m = models[state.key];
      drawFlow(d, obs, m);
      setText(doc.getElementById("flow-readout"),
        m.name + ": error " + fmt(m.rmse, "num3") + " g/s over the " +
        fmt(d.values.eval_window_start_s, "int") + "–" + fmt(d.values.eval_window_end_s, "int") +
        " s window (observed target shown in black).");
      buildTable("flow-table", ["time (s)", "observed (g/s)", m.name + " (g/s)"],
        d.time_axis_s.map(function (t, i) {
          return [fmt(t, "num2"), fmt(obs.values[i], "num3"), fmt(m.s.values[i], "num3")];
        }));
      var epsFig = doc.getElementById("eps-fig");
      var epsDet = doc.getElementById("eps-details");
      if (state.showEps) {
        epsFig.classList.remove("hidden"); epsDet.classList.remove("hidden");
        epsFig.setAttribute("aria-hidden", "false");
        drawEps(d, models.extraction.eps, models.composite.eps, state.key);
        buildTable("eps-table", ["time (s)", "extraction porosity", "composite porosity"],
          d.time_axis_s.map(function (t, i) {
            return [fmt(t, "num2"), fmt(models.extraction.eps.values[i], "num3"),
                    fmt(models.composite.eps.values[i], "num3")];
          }));
      } else {
        epsFig.classList.add("hidden"); epsDet.classList.add("hidden");
        epsFig.setAttribute("aria-hidden", "true");
      }
    }

    Array.prototype.forEach.call(doc.querySelectorAll('input[name="model"]'), function (r) {
      if (r.value === state.key) { r.checked = true; }
      r.addEventListener("change", function () { if (r.checked) { state.key = r.value; redraw(); } });
    });
    doc.getElementById("show-porosity").addEventListener("change", function (e) {
      state.showEps = e.target.checked; redraw();
    });
    redraw();
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
  function poly(pts, cls) {
    var p = doc.createElementNS(SVGNS, "polyline");
    p.setAttribute("points", pts.join(" "));
    p.setAttribute("class", cls);
    return p;
  }
  function rect(x, y, w, h, cls) {
    var r = doc.createElementNS(SVGNS, "rect");
    r.setAttribute("x", x); r.setAttribute("y", y);
    r.setAttribute("width", w); r.setAttribute("height", h);
    r.setAttribute("class", cls);
    return r;
  }
  function text(x, y, str, cls) {
    var t = doc.createElementNS(SVGNS, "text");
    t.setAttribute("x", x); t.setAttribute("y", y);
    if (cls) { t.setAttribute("class", cls); }
    setText(t, str);
    return t;
  }

  var W = 720, H = 360, ML = 56, MR = 16, MT = 20, MB = 44;

  function scaler(dmin, dmax, pmin, pmax) {
    var span = (dmax - dmin) || 1;
    return function (v) { return pmin + (v - dmin) / span * (pmax - pmin); };
  }
  function pathFor(xs, ys, sx, sy) {
    var pts = [];
    for (var i = 0; i < xs.length; i++) { pts.push(Math.round(sx(xs[i])) + "," + Math.round(sy(ys[i]))); }
    return pts;
  }
  function axes(svg, xlab, ylab, yticks, sx, sy, xmin, xmax) {
    svg.appendChild(line(ML, H - MB, W - MR, H - MB, "axis"));
    svg.appendChild(line(ML, MT, ML, H - MB, "axis"));
    yticks.forEach(function (yv) {
      var py = Math.round(sy(yv));
      svg.appendChild(line(ML, py, W - MR, py, "grid"));
      svg.appendChild(text(ML - 8, py + 4, String(yv), "tick-y"));
    });
    [xmin, Math.round((xmin + xmax) / 2), xmax].forEach(function (xv) {
      var px = Math.round(sx(xv));
      svg.appendChild(text(px, H - MB + 18, String(xv), "tick-x"));
    });
    svg.appendChild(text((ML + W - MR) / 2, H - 6, xlab, "axis-label"));
    var yl = text(0, 0, ylab, "axis-label-y");
    yl.setAttribute("x", 14); yl.setAttribute("y", (MT + H - MB) / 2);
    yl.setAttribute("transform", "rotate(-90 14 " + Math.round((MT + H - MB) / 2) + ")");
    svg.appendChild(yl);
  }

  function drawFlow(d, obs, m) {
    var fig = doc.getElementById("flow-fig");
    var old = fig.querySelector("svg"); if (old) { fig.removeChild(old); }
    var t = d.time_axis_s;
    var xmin = 0, xmax = Math.ceil(t[t.length - 1] / 10) * 10;
    var yvals = obs.values.concat(m.s.values);
    var ymax = Math.ceil(Math.max.apply(null, yvals) * 5) / 5;
    var svg = svgEl(W, H, "Flow versus time: the observed espresso flow in black with the " +
      m.name + " prediction overlaid. " +
      (m.name === "Extraction only" ? "The prediction tracks the rising flow closely." :
       m.name === "Extraction + swelling" ? "The composite prediction is a flat line at the wrong " +
         "level that misses the rise." : "The constant baseline is a flat horizontal line."));
    var sx = scaler(xmin, xmax, ML, W - MR), sy = scaler(0, ymax, H - MB, MT);
    // scored window band
    svg.appendChild(rect(Math.round(sx(d.values.eval_window_start_s)), MT,
      Math.round(sx(d.values.eval_window_end_s) - sx(d.values.eval_window_start_s)), H - MB - MT, "band"));
    var yt = []; for (var k = 0; k <= 5; k++) { yt.push(Math.round(ymax / 5 * k * 100) / 100); }
    axes(svg, "time (s)", "flow (g/s)", yt, sx, sy, xmin, xmax);
    svg.appendChild(poly(pathFor(t, m.s.values, sx, sy), "pred"));
    svg.appendChild(poly(pathFor(t, obs.values, sx, sy), "observed"));
    // direct labels
    svg.appendChild(text(sx(xmax) - 4, sy(obs.values[obs.values.length - 1]) - 6, "observed", "lbl-obs"));
    svg.appendChild(text(sx(xmax) - 4, sy(m.s.values[m.s.values.length - 1]) + 14, m.name, "lbl-pred"));
    fig.appendChild(svg);
  }

  function drawEps(d, epsE, epsC, key) {
    var fig = doc.getElementById("eps-fig");
    var old = fig.querySelector("svg"); if (old) { fig.removeChild(old); }
    var t = d.time_axis_s;
    var xmin = 0, xmax = Math.ceil(t[t.length - 1] / 10) * 10;
    var all = epsE.values.concat(epsC.values).concat([d.values.eps0_reference_porosity]);
    var lo = Math.floor(Math.min.apply(null, all) * 20) / 20;
    var hi = Math.ceil(Math.max.apply(null, all) * 20) / 20;
    var svg = svgEl(W, 300, "Shared porosity versus time. A dashed reference line marks the starting " +
      "porosity. The extraction branch rises just above it; the composite over-closes far below it.");
    var sx = scaler(xmin, xmax, ML, W - MR), sy = scaler(lo, hi, 300 - MB, MT);
    var yt = []; for (var k = 0; k <= 4; k++) { yt.push(Math.round((lo + (hi - lo) / 4 * k) * 100) / 100); }
    // axes for the shorter panel
    svg.appendChild(line(ML, 300 - MB, W - MR, 300 - MB, "axis"));
    svg.appendChild(line(ML, MT, ML, 300 - MB, "axis"));
    yt.forEach(function (yv) {
      var py = Math.round(sy(yv));
      svg.appendChild(line(ML, py, W - MR, py, "grid"));
      svg.appendChild(text(ML - 8, py + 4, String(yv), "tick-y"));
    });
    [xmin, Math.round((xmin + xmax) / 2), xmax].forEach(function (xv) {
      svg.appendChild(text(Math.round(sx(xv)), 300 - MB + 18, String(xv), "tick-x"));
    });
    svg.appendChild(text((ML + W - MR) / 2, 300 - 6, "time (s)", "axis-label"));
    // reference line at eps0
    var y0 = Math.round(sy(d.values.eps0_reference_porosity));
    svg.appendChild(line(ML, y0, W - MR, y0, "ref"));
    svg.appendChild(text(ML + 6, y0 - 6, "starting porosity", "lbl-ref"));
    svg.appendChild(poly(pathFor(t, epsE.values, sx, sy), key === "extraction" ? "pred" : "faint"));
    svg.appendChild(poly(pathFor(t, epsC.values, sx, sy), key === "composite" ? "pred" : "faint"));
    svg.appendChild(text(sx(xmax) - 4, sy(epsE.values[epsE.values.length - 1]) - 6, "extraction", "lbl-obs"));
    svg.appendChild(text(sx(xmax) - 4, sy(epsC.values[epsC.values.length - 1]) + 14, "composite", "lbl-pred"));
    fig.appendChild(svg);
  }

  function buildTable(id, headers, rows) {
    var host = doc.getElementById(id);
    while (host.firstChild) { host.removeChild(host.firstChild); }
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
    tbl.appendChild(tb); host.appendChild(tbl);
  }
})();
