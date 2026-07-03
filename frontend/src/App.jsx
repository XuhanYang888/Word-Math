import React, { useState } from "react";

function App() {
  const [equation, setEquation] = useState("king - man + woman");
  const [loading, setLoading] = useState(false);
  const [clusterData, setClusterData] = useState([]);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/api/analogy", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ equation, k: 20 }),
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

  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden select-none bg-slate-950 text-slate-100">
      <header className="h-16 border-b border-slate-800 flex items-center px-6 justify-between bg-slate-900/50 backdrop-blur">
        <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
          Vector Analogy Sandbox 3D
        </h1>
        <div className="text-xs text-slate-400 font-mono">
          Status: Connected to API
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
                placeholder="e.g. paris - france + italy"
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
            <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar flex flex-col gap-1 text-sm font-mono">
              {clusterData.length === 0 ? (
                <div className="text-slate-500 text-xs italic mt-4">
                  Enter an algebraic expression to populate the vector space.
                </div>
              ) : (
                clusterData.map((node, idx) => (
                  <div
                    key={idx}
                    className={`p-2 rounded flex justify-between items-center ${
                      node.type === "input"
                        ? "bg-amber-500/10 border border-amber-500/20 text-amber-300"
                        : node.type === "math_point"
                          ? "bg-purple-500/10 border border-purple-500/20 text-purple-300"
                          : "bg-slate-800/40 text-slate-300"
                    }`}
                  >
                    <span>{node.word}</span>
                    <span className="text-[10px] opacity-60 uppercase tracking-widest">
                      {node.type}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>

        <main className="flex-1 relative bg-slate-950">
          <div className="absolute inset-0 flex items-center justify-center text-slate-600 text-sm italic">
            [3D Visualization Placeholder]
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;
