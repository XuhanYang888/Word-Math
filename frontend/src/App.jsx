import React, { useState, useEffect, useRef } from "react";
import Plotly from "plotly.js-dist-min";

function App() {
  const [equation, setEquation] = useState("king - man + woman");
  const [loading, setLoading] = useState(false);
  const [clusterData, setClusterData] = useState([]);
  const [error, setError] = useState(null);
  const plotContainerRef = useRef(null);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/analogy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ equation, k: 25 }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Something went wrong.");
      }

      const data = await response.json();
      setClusterData(data.cluster);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleSubmit();
  }, []);

  useEffect(() => {
    if (!plotContainerRef.current || clusterData.length === 0) return;

    const inputs = clusterData.filter((d) => d.type === "input");
    const neighbors = clusterData.filter((d) => d.type === "neighbor");
    const mathPoint = clusterData.filter((d) => d.type === "math_point");

    const traces = [
      {
        name: "Query Inputs",
        x: inputs.map((d) => d.x),
        y: inputs.map((d) => d.y),
        z: inputs.map((d) => d.z),
        text: inputs.map((d) => d.word),
        mode: "markers+text",
        type: "scatter3d",
        marker: { size: 7, color: "#f59e0b", symbol: "circle", opacity: 0.9 },
        textposition: "top center",
        font: { family: "monospace", size: 12, color: "#fde68a" },
      },
      {
        name: "Discovered Neighbors",
        x: neighbors.map((d) => d.x),
        y: neighbors.map((d) => d.y),
        z: neighbors.map((d) => d.z),
        text: neighbors.map((d) => d.word),
        mode: "markers+text",
        type: "scatter3d",
        marker: { size: 5, color: "#06b6d4", opacity: 0.7 },
        textposition: "top center",
        font: { family: "monospace", size: 10, color: "#e0f7fa" },
      },
      {
        name: "Math Destination Coordinate",
        x: mathPoint.map((d) => d.x),
        y: mathPoint.map((d) => d.y),
        z: mathPoint.map((d) => d.z),
        text: mathPoint.map((d) => d.word),
        mode: "markers+text",
        type: "scatter3d",
        marker: { size: 9, color: "#d946ef", symbol: "diamond", opacity: 1.0 },
        textposition: "top center",
        font: { family: "monospace", size: 13, color: "#fdf2f8" },
      },
    ];

    const layout = {
      margin: { l: 0, r: 0, b: 0, t: 0 },
      paper_bgcolor: "#020617",
      plot_bgcolor: "#020617",
      showlegend: true,
      legend: {
        x: 0,
        y: 1,
        font: { color: "#94a3b8", size: 11 },
      },
      scene: {
        xaxis: {
          gridcolor: "#1e293b",
          zerolinecolor: "#334155",
          color: "#64748b",
        },
        yaxis: {
          gridcolor: "#1e293b",
          zerolinecolor: "#334155",
          color: "#64748b",
        },
        zaxis: {
          gridcolor: "#1e293b",
          zerolinecolor: "#334155",
          color: "#64748b",
        },
        camera: {
          eye: { x: 1.5, y: 1.5, z: 1.5 },
        },
      },
    };

    const config = { responsive: true, displayModeBar: false };

    Plotly.newPlot(plotContainerRef.current, traces, layout, config);

    const handleResize = () => Plotly.Plots.resize(plotContainerRef.current);
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [clusterData]);

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden select-none bg-slate-950 text-slate-100">
      <header className="h-16 border-b border-slate-800 flex items-center px-6 justify-between bg-slate-900/50 backdrop-blur">
        <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
          Vector Analogy Sandbox 3D
        </h1>
        <div className="text-xs text-slate-400 font-mono">
          Status: Engine Online
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-80 border-r border-slate-800 p-6 flex flex-col gap-6 bg-slate-900/30 z-10">
          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <label className="text-xs font-semibold tracking-wider uppercase text-slate-400">
              Vector Equation
            </label>
            <div className="flex gap-2">
              <input
                type="text"
                value={equation}
                onChange={(e) => setEquation(e.target.value)}
                className="flex-1 px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg focus:outline-none focus:border-cyan-500 font-mono text-sm"
                placeholder="e.g. king - man + woman"
              />
              <button
                type="submit"
                disabled={loading}
                className="px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-lg font-medium text-sm hover:opacity-90 transition disabled:opacity-50"
              >
                {loading ? "..." : "Run"}
              </button>
            </div>
          </form>

          {error && (
            <div className="p-3 bg-red-950/50 border border-red-800 text-red-200 text-xs rounded-lg font-medium">
              ⚠️ {error}
            </div>
          )}

          <div className="flex-1 flex flex-col min-h-0">
            <h3 className="text-xs font-semibold tracking-wider uppercase text-slate-400 mb-2">
              Neighborhood Cluster ({clusterData.length})
            </h3>
            <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-1 text-sm font-mono">
              {clusterData.map((node, idx) => (
                <div
                  key={idx}
                  className={`p-2 rounded flex justify-between items-center ${
                    node.type === "input"
                      ? "bg-amber-500/10 border border-amber-500/20 text-amber-300"
                      : node.type === "math_point"
                        ? "bg-purple-500/10 border border-purple-500/20 text-purple-300 font-bold"
                        : "bg-slate-800/40 text-slate-300"
                  }`}
                >
                  <span>{node.word}</span>
                  <span className="text-[10px] opacity-60 uppercase tracking-widest">
                    {node.type === "math_point" ? "target" : node.type}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </aside>

        <main className="flex-1 relative bg-slate-950">
          <div ref={plotContainerRef} className="w-full h-full" />
          {loading && (
            <div className="absolute inset-0 bg-slate-950/60 backdrop-blur-xs flex items-center justify-center text-cyan-400 font-mono text-sm">
              Recalculating multi-dimensional spaces...
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
