/* ============================================================================
   India Trade Exposure — Design System
   chart_theme.js — Plotly brand template + color scales
   ----------------------------------------------------------------------------
   Minimal data-ink: hairline axes, very faint gridlines, mono tick labels,
   confident on-brand series colors. Apply with:
     Plotly.newPlot(el, data, { ...ITE.layout(), title: {...} });
   or register the template:
     Plotly.setPlotConfig({});  // standard config
     layout.template = ITE.template;
   ========================================================================== */
(function (global) {
  // ---- Brand palette (mirrors colors_and_type.css) ----------------------
  var C = {
    ink900: "#1A1D24", ink500: "#5E646F", ink400: "#858B96",
    grid: "#ECEAE3", line: "#E6E3DB", paper: "#FFFFFF",
    indigo700: "#1F3A5F", indigo500: "#2E6FB0", indigo400: "#5B93C9",
    indigo300: "#9CC0E0", indigo200: "#C9DDEF", indigo100: "#E4EEF7",
    clay500: "#D17048", clay300: "#EFB89F",
    positive: "#3E7C5A", negative: "#C2502F"
  };

  // ---- The six color scales the dashboard needs -------------------------
  var SCALES = {
    // 1. Qualitative — 8 EBOPS service categories. Harmonised, even chroma.
    categorical8: [
      "#2E6FB0", // indigo  — Computer / Other business
      "#3E7C5A", // green   — Financial
      "#8A5FA8", // plum    — IP charges
      "#D17048", // clay    — Personal/cultural
      "#3FA0A8", // teal    — Telecoms
      "#B8902F", // ochre   — Insurance
      "#8C6A52", // brown   — Information
      "#6B7280"  // slate   — Other / residual
    ],

    // 2. Modes of supply — 4 steps, indigo→teal→ochre→clay
    modes4: ["#2E6FB0", "#3FA0A8", "#B8902F", "#D17048"],

    // 3. Diverging — exports (indigo) vs imports (clay), neutral midpoint
    diverging: [
      [0.0, "#1F3A5F"], [0.25, "#5B93C9"], [0.5, "#F4F2EC"],
      [0.75, "#E29070"], [1.0, "#A8472C"]
    ],
    imports: "#D17048",

    // 4. Sequential — exposure / trade intensity (single-hue indigo)
    sequential: [
      [0.0, "#E4EEF7"], [0.25, "#C9DDEF"], [0.5, "#9CC0E0"],
      [0.75, "#5B93C9"], [1.0, "#1F3A5F"]
    ],

    // 5. Sector pair — services (indigo)
    services: "#2E6FB0"
  };

  // ---- Plotly layout template -------------------------------------------
  var axisCommon = {
    showgrid: true, gridcolor: C.grid, gridwidth: 1,
    zeroline: false,
    showline: true, linecolor: C.line, linewidth: 1,
    ticks: "outside", tickcolor: C.line, ticklen: 4,
    tickfont: { family: "IBM Plex Mono, monospace", size: 11, color: C.ink500 },
    title: { font: { family: "IBM Plex Sans, sans-serif", size: 12, color: C.ink400 } },
    automargin: true
  };

  var template = {
    layout: {
      paper_bgcolor: C.paper,
      plot_bgcolor: C.paper,
      font: { family: "IBM Plex Sans, sans-serif", size: 13, color: C.ink900 },
      colorway: SCALES.categorical8,
      colorscale: { sequential: SCALES.sequential, diverging: SCALES.diverging },
      title: {
        font: { family: "IBM Plex Serif, serif", size: 16, color: C.ink900 },
        x: 0, xanchor: "left", xref: "paper", pad: { l: 4, b: 8 }
      },
      xaxis: axisCommon,
      yaxis: axisCommon,
      legend: {
        font: { family: "IBM Plex Sans, sans-serif", size: 12, color: C.ink500 },
        bgcolor: "rgba(0,0,0,0)", borderwidth: 0, traceorder: "normal",
        orientation: "h", yanchor: "bottom", y: 1.02, xanchor: "left", x: 0
      },
      margin: { l: 56, r: 16, t: 48, b: 44 },
      hovermode: "x unified",
      hoverlabel: {
        bgcolor: C.ink900, bordercolor: C.ink900,
        font: { family: "IBM Plex Mono, monospace", size: 12, color: "#fff" }
      },
      colorbar: {
        outlinewidth: 0, thickness: 10, len: 0.7,
        tickfont: { family: "IBM Plex Mono, monospace", size: 10, color: C.ink500 }
      }
    }
  };

  function layout(overrides) {
    var base = JSON.parse(JSON.stringify(template.layout));
    return Object.assign(base, overrides || {});
  }

  var CONFIG = { displayModeBar: false, responsive: true };

  global.ITE = { palette: C, scales: SCALES, template: template, layout: layout, config: CONFIG };
})(window);
