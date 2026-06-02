/* India Trade Exposure, Guided Walkthrough
   Charts (reuse ITE template + DATA), scroll-spy rail, definition popovers.
   Every tile and figure is read from window.DATA (generated from the processed
   CSVs by scripts/build_site_data.py), never hardcoded. Exposure scores are
   recomputed live from the two raw components so the scatter, the ranked bar
   and the table always agree (the actual v0 formula). */
(function () {
  var D = window.DATA, P = window.ITE;
  function L(over) { return P.layout(over); }
  var CFG = P.config;
  var M = D.meta;

  function busd(musd) { return musd / 1000; }
  function fmtB(musd) { return "$" + busd(musd).toFixed(1) + "B"; }
  function fmtM(n) { return (n / 1e6).toFixed(n >= 1e7 ? 1 : 2) + "M"; }

  /* ── exposure: recompute components from raw msme + trade ───────────── */
  function minmax(arr) {
    var lo = Math.min.apply(null, arr), hi = Math.max.apply(null, arr), r = hi - lo || 1;
    return arr.map(function (v) { return (v - lo) / r; });
  }
  var exRows = (function () {
    var rows = D.exposure.map(function (r) { return Object.assign({}, r); });
    var sM = minmax(rows.map(function (r) { return r.msme; }));
    var sT = minmax(rows.map(function (r) { return r.trade; }));
    rows.forEach(function (r, i) {
      r.sx = sM[i]; r.sy = sT[i]; r.score = sM[i] + sT[i];
      r.short = r.short || r.cat;
    });
    return rows;
  })();

  /* ── metric tiles (computed live from DATA) ─────────────────────────── */
  function fillOverviewTiles() {
    var n = D.ddsExp.length - 1;
    var expL = D.ddsExp[n], impL = D.ddsImp[n];
    var yoy = ((D.ddsExp[n] - D.ddsExp[n - 1]) / D.ddsExp[n - 1] * 100).toFixed(1);
    var surplus = busd(expL - impL);
    var surplus0 = busd(D.ddsExp[0] - D.ddsImp[0]);
    var ipL = D.ipImp[D.ipImp.length - 1], ip0 = D.ipImp[0];
    var ipx = (ipL / ip0).toFixed(0);
    var yr = M.ddsYear, yr0 = D.years[0];
    document.getElementById("ov-tiles").innerHTML =
      '<div class="tile"><div class="lbl">Exports · ' + yr + '</div><div class="val">' + fmtB(expL) + '</div><div class="dlt up">▲ +' + yoy + '% YoY</div></div>' +
      '<div class="tile"><div class="lbl">Imports · ' + yr + '</div><div class="val">' + fmtB(impL) + '</div><div class="dlt neutral">cross-border, Mode 1</div></div>' +
      '<div class="tile"><div class="lbl">Net surplus</div><div class="val">$' + surplus.toFixed(1) + 'B</div><div class="dlt up">▲ from $' + surplus0.toFixed(0) + 'B in ' + yr0 + '</div></div>' +
      '<div class="tile accent"><div class="lbl">IP licensing fees paid</div><div class="val">' + fmtB(ipL) + '</div><div class="dlt neutral">~' + ipx + '× since ' + yr0 + '</div></div>';
  }
  function fillMsmeTiles() {
    document.getElementById("ms-tiles").innerHTML =
      '<div class="tile"><div class="lbl">Udyam registrations</div><div class="val">' + fmtM(M.udyamTotal) + '</div><div class="dlt neutral">current total</div></div>' +
      '<div class="tile"><div class="lbl">In this sector cut</div><div class="val">' + fmtM(M.sectorCut) + '</div><div class="dlt neutral">Sep 2021, top-50 codes</div></div>' +
      '<div class="tile accent"><div class="lbl">Manufacturing</div><div class="val">' + fmtM(M.mfgTotal) + '</div><div class="dlt neutral">across ' + M.mfgDivs + ' divisions</div></div>' +
      '<div class="tile"><div class="lbl">Services</div><div class="val">' + fmtM(M.svcTotal) + '</div><div class="dlt neutral">across ' + M.svcDivs + ' divisions</div></div>';
  }

  /* ── entrance helper: plot zeroed, then grow elements into place once ── */
  function zeroAxis(data, axis) {
    return data.map(function (t) {
      var s = {}; for (var k in t) s[k] = t[k];
      if (axis === "y") s.y = (t.y || []).map(function () { return 0; });
      else s.x = (t.x || []).map(function () { return 0; });
      return s;
    });
  }
  // Manual rAF tween: restyle the animated axis from 0 → final each frame.
  // (Plotly.animate snaps bar traces; restyling redraws every frame so bars,
  // lines and scatter points all grow in smoothly and reliably.)
  function growIn(id, data, axis, dur) {
    var targets = data.map(function (t) { return (axis === "y" ? t.y : t.x).map(Number); });
    var start = null;
    function ease(p) { return 1 - Math.pow(1 - p, 3); }   // cubic-out
    function frame(now) {
      if (start === null) start = now;
      var p = Math.min(1, (now - start) / dur), e = ease(p);
      var upd = {};
      upd[axis] = targets.map(function (arr) { return arr.map(function (v) { return v * e; }); });
      Plotly.restyle(id, upd);
      if (p < 1) requestAnimationFrame(frame);
    }
    requestAnimationFrame(frame);
  }
  // Compute the fixed extent of the value axis from the FINAL data, so it can
  // be locked while the data grows from 0. Handles stacked bars (cumulative)
  // and diverging bars (negative values) too.
  function axisExtent(data, axis, stacked) {
    var arrs = data.map(function (t) { return (axis === "y" ? t.y : t.x).map(Number); });
    var max, min;
    if (stacked) {
      var sums = arrs[0].map(function (_, i) {
        return arrs.reduce(function (s, a) { return s + (a[i] || 0); }, 0);
      });
      max = Math.max.apply(null, sums); min = Math.min(0, Math.min.apply(null, sums));
    } else {
      var flat = []; arrs.forEach(function (a) { flat = flat.concat(a); });
      max = Math.max(0, Math.max.apply(null, flat));
      min = Math.min(0, Math.min.apply(null, flat));
    }
    var pad = (max - min) * 0.05 || 1;
    return [min < 0 ? min - pad : min, max + pad];
  }
  // When animate is true, the chart is drawn collapsed against its axis and
  // then grows to full — bars extend, lines rise, scatter points lift.
  function plotIn(id, data, layout, axis, animate, dur) {
    if (!animate) { Plotly.newPlot(id, data, layout, CFG); return; }
    // Lock the value axis to its final extent up front — otherwise Plotly
    // auto-rescales it every frame as values grow from 0, so the ticks animate
    // but the bars/line stay full-size and appear static. (Charts that already
    // declare an explicit range, e.g. the scatter, are left untouched.)
    var key = axis === "y" ? "yaxis" : "xaxis";
    if (!(layout[key] && layout[key].range)) {
      layout[key] = Object.assign({}, layout[key],
        { range: axisExtent(data, axis, layout.barmode === "stack"), autorange: false });
    }
    Plotly.newPlot(id, zeroAxis(data, axis), layout, CFG).then(function () {
      growIn(id, data, axis, dur || 800);
    });
  }

  /* ── ACT I charts ───────────────────────────────────────────────────── */
  function drawOverviewLine(animate) {
    var data = [
      { x: D.years, y: D.ddsExp.map(busd), name: "Exports", mode: "lines+markers",
        line: { color: P.palette.indigo500, width: 2.5 }, marker: { size: 5, color: P.palette.indigo500 } },
      { x: D.years, y: D.ddsImp.map(busd), name: "Imports", mode: "lines+markers",
        line: { color: P.scales.imports, width: 2.5 }, marker: { size: 5, color: P.scales.imports } }
    ];
    plotIn("ov-line", data, L({ yaxis: { title: { text: "USD billion" } }, xaxis: { dtick: 5 }, margin: { l: 56, r: 16, t: 30, b: 44 } }), "y", animate, 1000);
  }
  var ovCatDrawn = false, curFlow = "exp";
  function drawCat(flow, animate) {
    curFlow = flow;
    var rows = D.cat2025.slice().sort(function (a, b) { return flow === "exp" ? a.exp - b.exp : a.imp - b.imp; });
    var color = flow === "exp" ? P.palette.indigo500 : P.scales.imports;
    var trace = {
      type: "bar", orientation: "h",
      y: rows.map(function (r) { return r.name; }), x: rows.map(function (r) { return flow === "exp" ? r.exp : r.imp; }),
      marker: { color: color }, hovertemplate: "%{y}<br>$%{x:.1f}B<extra></extra>"
    };
    var layout = L({ xaxis: { title: { text: "USD billion" } }, margin: { l: 180, r: 16, t: 18, b: 44 } });
    if (!ovCatDrawn) { plotIn("ov-cat", [trace], layout, "x", animate); ovCatDrawn = true; }
    else { plotIn("ov-cat", [trace], layout, "x", true, 600); }
  }

  /* ── ACT II charts ──────────────────────────────────────────────────── */
  function drawServiceDiv(animate) {
    var rows = D.cat2025.slice().sort(function (a, b) { return (a.exp + a.imp) - (b.exp + b.imp); });
    var data = [
      { type: "bar", orientation: "h", name: "Exports", y: rows.map(function (r) { return r.name; }), x: rows.map(function (r) { return r.exp; }),
        marker: { color: P.palette.indigo500 }, hovertemplate: "%{y}<br>Exports $%{x:.1f}B<extra></extra>" },
      { type: "bar", orientation: "h", name: "Imports", y: rows.map(function (r) { return r.name; }), x: rows.map(function (r) { return -r.imp; }),
        marker: { color: P.scales.imports }, customdata: rows.map(function (r) { return r.imp; }),
        hovertemplate: "%{y}<br>Imports $%{customdata:.1f}B<extra></extra>" }
    ];
    plotIn("sv-div", data, L({ barmode: "overlay",
      xaxis: { title: { text: "USD billion (imports ◀ | ▶ exports)" }, zeroline: true, zerolinecolor: P.palette.ink400, zerolinewidth: 1 },
      margin: { l: 180, r: 16, t: 30, b: 44 }, hovermode: "closest" }), "x", animate);
  }
  function drawServiceMode(animate) {
    var mm = D.modeMix.slice().sort(function (a, b) { return a.m1 - b.m1; });
    var modes = ["m1", "m2", "m3", "m4"], labels = ["Mode 1", "Mode 2", "Mode 3", "Mode 4"];
    var data = modes.map(function (m, i) {
      return { type: "bar", orientation: "h", name: labels[i], y: mm.map(function (r) { return r.name; }), x: mm.map(function (r) { return r[m]; }),
        marker: { color: P.scales.modes4[i] }, hovertemplate: "%{y}<br>" + labels[i] + ": %{x}%<extra></extra>" };
    });
    plotIn("sv-mode", data, L({ barmode: "stack",
      xaxis: { title: { text: "Share of category total" }, ticksuffix: "%" }, margin: { l: 160, r: 16, t: 30, b: 44 }, hovermode: "closest" }), "x", animate);
  }

  /* ── ACT III charts ─────────────────────────────────────────────────── */
  function drawMsmeSvc(animate) {
    var sv = D.svcDiv.slice().sort(function (a, b) { return a.count - b.count; });
    plotIn("ms-svc", [{ type: "bar", orientation: "h", y: sv.map(function (r) { return r.name; }), x: sv.map(function (r) { return r.count; }),
      marker: { color: P.scales.services }, hovertemplate: "%{y}<br>%{x:,} firms<extra></extra>" }],
      L({ xaxis: { title: { text: "MSME count (Sep 2021)" } }, margin: { l: 210, r: 12, t: 18, b: 44 } }), "x", animate);
  }
  function drawMsmeSec(animate) {
    var sec = D.isicSection.slice().sort(function (a, b) { return a.count - b.count; });
    plotIn("ms-sec", [{ type: "bar", orientation: "h", y: sec.map(function (r) { return r.sec + " " + r.name; }), x: sec.map(function (r) { return r.count; }),
      marker: { color: sec.map(function (r) { return r.count; }), colorscale: P.scales.sequential, showscale: false },
      hovertemplate: "%{y}<br>%{x:,} firms<extra></extra>" }],
      L({ xaxis: { title: { text: "MSME count" } }, margin: { l: 210, r: 12, t: 18, b: 44 } }), "x", animate);
  }

  /* ── ACT IV charts ──────────────────────────────────────────────────── */
  function drawExposureScatter(animate) {
    // Best-effort label placement for the real eleven categories; the ranked
    // bar and table below are the precise reads if any labels crowd.
    var POS = {
      "Other business": "middle left", "Transport": "top center", "Telecom/computer": "middle right",
      "Distribution": "middle right", "Insurance & finance": "middle right", "Personal services": "top right",
      "Tourism": "bottom center", "Construction": "top left", "Education": "bottom right",
      "Health": "middle right", "Heritage & rec.": "bottom left"
    };
    var diagShapes = [0.5, 1.0, 1.5].map(function (c) {
      var x0 = Math.max(0, c - 1), y0 = Math.min(c, 1), x1 = Math.min(c, 1), y1 = Math.max(0, c - 1);
      return { type: "line", x0: x0, y0: y0, x1: x1, y1: y1, layer: "below",
        line: { color: P.palette.indigo300, width: 1, dash: "dot" } };
    });
    var scData = [{
      type: "scatter", mode: "markers+text",
      x: exRows.map(function (r) { return r.sx; }), y: exRows.map(function (r) { return r.sy; }),
      text: exRows.map(function (r) { return r.short; }),
      textposition: exRows.map(function (r) { return POS[r.short] || (r.sx > 0.7 ? "middle left" : "middle right"); }),
      textfont: { family: "IBM Plex Mono, monospace", size: 10.5, color: P.palette.ink500 },
      marker: {
        size: exRows.map(function (r) { return 14 + r.score * 13; }),
        color: exRows.map(function (r) { return r.score; }), colorscale: P.scales.sequential,
        cmin: 0, cmax: 2, line: { color: "#fff", width: 1.5 },
        colorbar: { title: { text: "Exposure" }, x: 1.02 }
      },
      customdata: exRows.map(function (r) { return [r.sx.toFixed(2), r.sy.toFixed(2), r.score.toFixed(2)]; }),
      hovertemplate: "<b>%{text}</b><br>MSME scale %{customdata[0]}<br>Trade intensity %{customdata[1]}<br>Exposure %{customdata[2]}<extra></extra>"
    }];
    plotIn("ex-scatter", scData, L({
      xaxis: { title: { text: "MSME scale  (firm count, normalised 0–1) →" }, range: [-0.05, 1.12], zeroline: false },
      yaxis: { title: { text: "Trade intensity  (Mode 1 $, normalised 0–1) →" }, range: [-0.1, 1.12], zeroline: false },
      margin: { l: 64, r: 90, t: 24, b: 56 }, shapes: diagShapes, hovermode: "closest"
    }), "y", animate, 950);
  }
  function drawExposureBar(animate) {
    var rows = exRows.slice().sort(function (a, b) { return a.score - b.score; });
    plotIn("ex-bar", [{
      type: "bar", orientation: "h", y: rows.map(function (r) { return r.short; }), x: rows.map(function (r) { return r.score; }),
      marker: { color: rows.map(function (r) { return r.score; }), colorscale: P.scales.sequential, cmin: 0, cmax: 2,
        colorbar: { title: { text: "Score" } } },
      hovertemplate: "%{y}<br>Exposure %{x:.2f}<extra></extra>"
    }], L({
      xaxis: { title: { text: "Exposure score (0–2, higher = more exposed)" }, range: [0, 2.1] }, margin: { l: 150, r: 16, t: 18, b: 44 } }), "x", animate);
  }
  // What sits inside the top-ranked category. SJXSJ34 maps to ISIC L+M+N, so
  // its firm count is a composite; these helpers name the sections, the
  // divisions, the sub-sector exposure, and the within-category growth.
  var OBS_SECTION_COLOR = {
    M: P.palette.indigo500,   // professional, scientific & technical
    N: P.scales.modes4[1],    // admin & support (teal)
    L: P.scales.imports       // real estate (clay)
  };
  // Three rollup cards: the L/M/N split of the category's firm count at a glance.
  function fillObsSections() {
    var el = document.getElementById("obs-sections"); if (!el) return;
    var total = D.obsComposition.total;
    var meta = {
      M: { name: "Professional & scientific", note: "consulting, legal, accounting, engineering, advertising, R&D" },
      N: { name: "Admin & support", note: "travel agencies, office & building support, staffing, leasing" },
      L: { name: "Real estate", note: "property activities on a fee or contract basis" }
    };
    var roll = {};
    D.obsComposition.divisions.forEach(function (r) { roll[r.isic] = (roll[r.isic] || 0) + r.count; });
    var order = Object.keys(roll).sort(function (a, b) { return roll[b] - roll[a]; });
    el.innerHTML = order.map(function (s) {
      var c = roll[s] || 0, pct = (c / total * 100).toFixed(0);
      return '<div class="obs-card" style="--sec:' + OBS_SECTION_COLOR[s] + '">' +
        '<div class="obs-sec"><span class="obs-dot"></span>ISIC ' + s + ' · ' + meta[s].name + '</div>' +
        '<div class="obs-num">' + c.toLocaleString() + '</div>' +
        '<div class="obs-pct">' + pct + '% of the category</div>' +
        '<div class="obs-note">' + meta[s].note + '</div></div>';
    }).join("");
  }
  // Composition: the NIC 2-digit divisions inside the category, coloured by the
  // ISIC section each rolls up to. Lives in a collapsed expander; drawn on open.
  function drawObsComposition(animate) {
    var rows = D.obsComposition.divisions.slice().sort(function (a, b) { return a.count - b.count; });
    plotIn("ex-obs", [{
      type: "bar", orientation: "h",
      y: rows.map(function (r) { return r.isic + " · " + r.name; }),
      x: rows.map(function (r) { return r.count; }),
      marker: { color: rows.map(function (r) { return OBS_SECTION_COLOR[r.isic] || P.palette.ink400; }) },
      customdata: rows.map(function (r) { return (r.count / D.obsComposition.total * 100).toFixed(1); }),
      hovertemplate: "%{y}<br>%{x:,} firms (%{customdata}% of the category)<extra></extra>"
    }], L({ xaxis: { title: { text: "MSME count (Sep 2021)" } }, margin: { l: 268, r: 12, t: 18, b: 44 } }), "x", animate);
  }
  // Sub-exposure one level deeper, the same two-axis method min-max normalised
  // WITHIN the category. Each bar is SPLIT into its two halves (trade intensity +
  // firm-count scale) so the score's composition is legible: the digital,
  // cross-border core (indigo) versus firm count alone (slate).
  function drawObsSubExposure(animate) {
    var rows = D.obsSubExposure.map(function (r) { return Object.assign({}, r); });
    var sM = minmax(rows.map(function (r) { return r.msme; }));
    var sT = minmax(rows.map(function (r) { return r.trade; }));
    rows.forEach(function (r, i) { r.sx = sM[i]; r.sy = sT[i]; r.score = sM[i] + sT[i]; });
    rows.sort(function (a, b) { return a.score - b.score; });
    var y = rows.map(function (r) { return r.label; });
    var data = [
      { type: "bar", orientation: "h", name: "Trade intensity · Mode 1 $", y: y, x: rows.map(function (r) { return r.sy; }),
        marker: { color: P.palette.indigo500 },
        customdata: rows.map(function (r) { return [r.trade.toFixed(1), r.score.toFixed(2)]; }),
        hovertemplate: "%{y}<br>Trade intensity %{x:.2f}  ($%{customdata[0]}B Mode 1)<br>Sub-exposure %{customdata[1]}<extra></extra>" },
      { type: "bar", orientation: "h", name: "MSME scale · firm count", y: y, x: rows.map(function (r) { return r.sx; }),
        marker: { color: P.palette.ink400 },
        customdata: rows.map(function (r) { return r.msme.toLocaleString(); }),
        hovertemplate: "%{y}<br>MSME scale %{x:.2f}  (%{customdata} firms)<extra></extra>" }
    ];
    plotIn("ex-obs-sub", data, L({ barmode: "stack",
      xaxis: { title: { text: "Sub-exposure score (trade intensity + firm-count scale, 0–2)" }, range: [0, 2.1] },
      margin: { l: 250, r: 16, t: 30, b: 44 }, hovermode: "closest" }), "x", animate);
  }
  // Within-category growth: professional & management consulting (SJ2) is the
  // entire surge; the technical / other remainder (SJ3) is flat beside it.
  function drawObsTrend(animate) {
    var T = D.obsTrend;
    var data = [
      { x: T.years, y: T.consulting.map(busd), name: "Professional & management consulting", mode: "lines+markers",
        line: { color: P.palette.indigo500, width: 2.6 }, marker: { size: 5, color: P.palette.indigo500 } },
      { x: T.years, y: T.technical.map(busd), name: "Technical, trade-related & other", mode: "lines+markers",
        line: { color: P.palette.ink400, width: 2 }, marker: { size: 4, color: P.palette.ink400 } }
    ];
    plotIn("ex-obs-trend", data, L({ yaxis: { title: { text: "USD billion" } }, xaxis: { dtick: 5 }, margin: { l: 56, r: 16, t: 30, b: 44 } }), "y", animate, 1000);
  }
  function fillExposureTable() {
    var rows = exRows.slice().sort(function (a, b) { return b.score - a.score; });
    var head = '<thead><tr><th class="l">#</th><th class="l">EBOPS category</th><th>ISIC</th><th>MSME count</th><th>Mode 1 $B</th><th>Scale</th><th>Intensity</th><th>Score</th></tr></thead>';
    var body = '<tbody>' + rows.map(function (r, i) {
      var isic = r.isic && r.isic !== "nan" ? r.isic : "n/a";
      return '<tr' + (i === 0 ? ' class="lead-row"' : '') + '><td class="l">' + (i + 1) + '</td><td class="l">' + r.cat + '</td><td>' + isic + '</td><td>' + r.msme.toLocaleString() + '</td><td>' + r.trade.toFixed(1) + '</td><td>' + r.sx.toFixed(2) + '</td><td>' + r.sy.toFixed(2) + '</td><td>' + r.score.toFixed(2) + '</td></tr>';
    }).join("") + '</tbody>';
    document.getElementById("ex-table").innerHTML = head + body;
  }

  /* ── chart titles (rendered as HTML headers above each card, so they use
     the design type system and never collide with the Plotly legend) ──── */
  var TITLES = {
    "ov-line":    ["Digitally delivered services trade", "India · USD billion · Mode 1 · 2005–2025"],
    "ov-cat":     ["Trade by service category", "2025 · USD billion"],
    "sv-div":     ["Services trade by category", "2025 · USD billion · imports ◀ ▶ exports"],
    "sv-mode":    ["How digital is each category", "2022 · mode share of total"],
    "ms-svc":     ["Top service divisions by firm count", "NIC 2-digit · Sep 2021"],
    "ms-sec":     ["Firm count by ISIC section", "Sep 2021"],
    "ex-scatter": ["Exposure: MSME scale against trade intensity", "2022 · normalised 0–1"],
    "ex-bar":     ["Exposure ranking by category", "score 0–2"],
    "ex-obs-sub": ["Sub-exposure inside the category", "EBOPS sub-codes · score split into its two halves"],
    "ex-obs-trend": ["What actually drove the surge", "India · Mode 1 exports · USD billion · 2005–2022"]
  };
  function injectHeads() {
    Object.keys(TITLES).forEach(function (id) {
      var el = document.getElementById(id);
      if (!el) return;
      var card = el.closest(".chart-card");
      if (!card) return;
      var prev = card.previousElementSibling;
      if (prev && prev.classList.contains("fighead")) return;
      var h = document.createElement("div");
      h.className = "fighead";
      h.innerHTML = '<h4 class="figtitle">' + TITLES[id][0] + '</h4><span class="figunit">' + TITLES[id][1] + '</span>';
      card.parentNode.insertBefore(h, card);
    });
  }

  /* ── scroll-reveal (fires once; honoured even under reduce, per request) ─ */
  function initReveal() {
    var sel = ".hero .title, .hero .standfirst, .hero .herometa, .eyebrow, .act-h, h3.sub, .figure, .concept, .finding, .tile, .qcard, .note, .panel, .notice, .mode, .step, .dcard, .obs-card, table.prov, table.dt, .join";
    var els = Array.prototype.slice.call(document.querySelectorAll(sel));
    els.forEach(function (el) {
      el.setAttribute("data-reveal", "");
      var p = el.parentElement;
      if (p && (p.classList.contains("tiles") || p.classList.contains("qgrid") || p.classList.contains("deck") || p.classList.contains("modes") || p.classList.contains("recipe") || p.classList.contains("compare") || p.classList.contains("obs-sections"))) {
        var i = Array.prototype.indexOf.call(p.children, el);
        el.style.transitionDelay = Math.min(i * 60, 240) + "ms";
      }
    });
    // Fire only once the element's top edge has risen past ~78% of the viewport
    // (a meaningful slice is actually on screen), not the instant its top peeks
    // in at the bottom, where the entrance would finish before it is seen.
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -22% 0px", threshold: 0 });
    els.forEach(function (el) { io.observe(el); });
  }

  /* ── lazy chart reveal: each chart draws + animates in when scrolled to ─ */
  function initCharts() {
    var drawers = {
      "ov-line": drawOverviewLine,
      "ov-cat": function (a) { drawCat(curFlow, a); },
      "sv-div": drawServiceDiv,
      "sv-mode": drawServiceMode,
      "ms-svc": drawMsmeSvc,
      "ms-sec": drawMsmeSec,
      "ex-scatter": drawExposureScatter,
      "ex-bar": drawExposureBar,
      "ex-obs-sub": drawObsSubExposure,
      "ex-obs-trend": drawObsTrend
    };
    // The user explicitly asked for these one-shot entrances, so they run even
    // under prefers-reduced-motion (the only thing the preference silences is
    // the looping scroll-cue bob). Each chart grows in once, when scrolled to.
    Object.keys(drawers).forEach(function (id) {
      var el = document.getElementById(id); if (!el) return;
      // Hold the entrance until the chart is well into view: the trigger line
      // sits 22% up from the bottom of the viewport and at least 40% of the
      // chart must be above it, so it grows in once it's clearly on screen
      // rather than the moment its top edge appears.
      var io = new IntersectionObserver(function (ents) {
        ents.forEach(function (e) { if (e.isIntersecting) { drawers[id](true); io.disconnect(); } });
      }, { rootMargin: "0px 0px -22% 0px", threshold: 0.4 });
      io.observe(el);
    });
  }

  /* ── render all (tiles/tables fill now; charts draw lazily on scroll) ── */
  function renderAll() {
    injectHeads();
    fillOverviewTiles(); fillMsmeTiles(); fillObsSections(); fillExposureTable();
    initCharts();

    var seg = document.getElementById("ov-flow");
    seg.addEventListener("click", function (e) {
      var b = e.target.closest("button"); if (!b) return;
      seg.querySelectorAll("button").forEach(function (x) { x.classList.remove("on"); });
      b.classList.add("on"); drawCat(b.dataset.f, true);
    });

    // The composition bar lives in a collapsed expander; draw it the first time
    // it opens (when it has a measurable width), resize on subsequent opens.
    var obsD = document.getElementById("obs-comp-details");
    if (obsD) obsD.addEventListener("toggle", function () {
      if (!obsD.open) return;
      if (!obsD.dataset.drawn) { drawObsComposition(true); obsD.dataset.drawn = "1"; }
      else { setTimeout(resizeAll, 60); }
    });
  }

  function resizeAll() {
    document.querySelectorAll(".chart").forEach(function (c) { try { Plotly.Plots.resize(c); } catch (e) {} });
  }
  var rt;
  window.addEventListener("resize", function () { clearTimeout(rt); rt = setTimeout(resizeAll, 150); });

  /* ── scroll-spy rail + progress ─────────────────────────────────────── */
  function initScrollSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll("#nav a"));
    var sections = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    var prog = document.getElementById("prog"), mprog = document.getElementById("mprog");
    function onScroll() {
      var y = window.scrollY + window.innerHeight * 0.30;
      var idx = 0;
      for (var i = 0; i < sections.length; i++) { if (sections[i] && sections[i].offsetTop <= y) idx = i; }
      links.forEach(function (a, i) { a.classList.toggle("on", i === idx); });
      var doc = document.documentElement;
      var pct = Math.min(100, Math.max(0, (window.scrollY / (doc.scrollHeight - window.innerHeight)) * 100));
      if (prog) prog.style.width = pct + "%";
      if (mprog) mprog.style.width = pct + "%";
    }
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  /* ── definition popovers ────────────────────────────────────────────── */
  var DEFS = {
    msme: { t: "MSME", d: "Micro, Small & Medium Enterprises, India's small businesses. Registered through the government's Udyam system." },
    wto: { t: "WTO", d: "World Trade Organization, sets the international rules and statistical standards for trade, including services trade." },
    gats: { t: "GATS modes", d: "The WTO splits how a service crosses a border into four 'modes of supply'. Mode 1 is the digital channel; Modes 2–4 involve someone or something physically moving." },
    mode1: { t: "Mode 1", d: "Cross-border supply, a service delivered over the internet with nobody travelling. The digital channel where platforms and digital-trade rules operate." },
    ebops: { t: "EBOPS", d: "Extended Balance of Payments Services, the international standard for categorising what kind of service is being traded (computer services, IP charges, etc.). This study uses its 11 top-level categories." },
    isic: { t: "ISIC", d: "International Standard Industrial Classification, organises firms by what industry they're in (rather than by what they trade)." },
    nic: { t: "NIC", d: "India's National Industrial Classification, used to register firms by industry. It lines up with ISIC at the section level." },
    crosswalk: { t: "Crosswalk", d: "A lookup table mapping one classification onto another, here, each EBOPS trade category onto its ISIC industry section(s)." },
    dds: { t: "DDS", d: "WTO Digitally Delivered Services dataset, Mode 1 only, 8 categories, 2005–2025. Used here for the long headline trend." },
    tismos: { t: "TiSMoS", d: "WTO Trade in Services by Mode of Supply, all four modes, 55 categories, 2005–2022. Used here for category and mode detail." },
    udyam: { t: "Udyam", d: "The Government of India portal where MSMEs register. Has accumulated 57.7 million registrations." },
    bulletin7: { t: "Bulletin VII", d: "MoMSME's 'Analysis of Udyam Registration Data', cutoff 30 Sep 2021, the most granular public sector breakdown of registered MSMEs." },
    composite: { t: "Composite indicator", d: "A single number built by combining several measurements, the general family that any 'index' or 'score' belongs to." },
    minmax: { t: "Min-max normalisation", d: "Rescaling so the smallest value becomes 0 and the largest 1. Simple, but the scale is anchored to whichever row is biggest." }
  };
  function initPopovers() {
    var pop = document.getElementById("defpop");
    var current = null;
    function place(el) {
      var key = el.getAttribute("data-term"); var def = DEFS[key]; if (!def) return;
      pop.innerHTML = '<div class="dt">' + def.t + '</div>' + def.d;
      pop.classList.add("show");
      var r = el.getBoundingClientRect();
      var pw = pop.offsetWidth, ph = pop.offsetHeight;
      var left = Math.min(window.innerWidth - pw - 12, Math.max(12, r.left + r.width / 2 - pw / 2));
      var top = r.top - ph - 12; var below = false;
      if (top < 8) { top = r.bottom + 12; below = true; }
      pop.style.left = left + "px"; pop.style.top = top + "px";
      var ax = Math.min(pw - 16, Math.max(6, r.left + r.width / 2 - left - 5));
      pop.style.setProperty("--arrow-x", ax + "px");
      pop.style.setProperty("--arrow-y", below ? "-5px" : (ph - 5) + "px");
    }
    document.querySelectorAll(".term").forEach(function (el) {
      el.setAttribute("tabindex", "0");
      el.addEventListener("mouseenter", function () { current = el; el.classList.add("open"); place(el); });
      el.addEventListener("mouseleave", function () { el.classList.remove("open"); pop.classList.remove("show"); });
      el.addEventListener("focus", function () { current = el; el.classList.add("open"); place(el); });
      el.addEventListener("blur", function () { el.classList.remove("open"); pop.classList.remove("show"); });
      el.addEventListener("click", function (e) { e.preventDefault(); current = el; place(el); });
    });
    window.addEventListener("scroll", function () { if (pop.classList.contains("show") && current) place(current); }, { passive: true });
  }

  function init() {
    renderAll();
    initScrollSpy();
    initPopovers();
    initReveal();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();
