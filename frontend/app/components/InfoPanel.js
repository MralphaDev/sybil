import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
//import { Tooltip } from "@material-tailwind/react"; // 可选 tooltip 库

export default function InfoPanel({ selected, clusters ,similarities,dbscan,setHighlightNodes,sybil_entities}) {

  const [page, setPage] = useState(0);
  const [activeCluster, setActiveCluster] = useState(null);
  const [activeDbscan, setActiveDbscan] = useState(null);

  const [showSubgroupWindow, setShowSubgroupWindow] = useState(false); // 是否显示 subgroup 窗口
  const [currentSubgroup, setCurrentSubgroup] = useState(null); // 当前显示的 subgroup / noise 地址列表

  const clustersPerPage = 2;
  const totalPages = Math.ceil(clusters?.length / clustersPerPage || 1);

  const displayedClusters = clusters?.slice(
    page * clustersPerPage,
    page * clustersPerPage + clustersPerPage
  ) || [];

  const [open, setOpen] = useState(false);
  //const safeSybil = Array.isArray(sybil_entities) ? sybil_entities : [];
  const safeSybil = typeof sybil_entities === "object" && sybil_entities !== null ? sybil_entities : {};
  console.log("Sybil entities:", sybil_entities);
  

  const labels = [
  "Total TX Count",
  "First Block timestamp",
  "First Funding Amount"
];

const labeledVector = selected?.data?.behavior_vector.map(
  (value, index) => `${labels[index] || `Feature ${index + 1}`}: ${value}`
);

// 工具函数：只保留前6位和后4位，中间用 … 代替
function shortenHex(hex, start = 6, end = 4) {
  if (!hex || hex.length <= start + end) return hex;
  return `${hex.slice(0, start)}…${hex.slice(-end)}`;
}


  return (
    <div>
    <>
      {/* 左侧书签按钮 */}
      <div className="fixed top-1/2 left-0 z-50">
        <button
          onClick={() => setOpen(!open)}
          className={`px-3 py-4 rounded-r-xl shadow-lg text-white font-bold 
                      bg-gradient-to-b from-purple-600 to-orange-500 
                      hover:from-purple-700 hover:to-orange-600 
                      transition-transform hover:scale-110`}
        >
          {open ? "⯈" : "⯇"}
        </button>
      </div>
       
      {/* Info Panel */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ x: "-100%" }}
            animate={{ x: 0 }}
            exit={{ x: "-100%" }}
            drag="x"
            dragConstraints={{ left: -200, right: 0 }}
            className="fixed top-20 left-0 h-auto max-h-[70vh] w-80 bg-gray-900/95 shadow-2xl p-4 overflow-y-auto z-40 rounded-r-2xl"
          >
            <h2 className="text-xl font-extrabold mb-4 text-orange-400 text-center">
              Sybil Entity Analysis
            </h2>

            {Object.keys(safeSybil).length === 0 ? (
              <p className="text-gray-400 italic text-sm text-center">
                No suspicious entities detected.
              </p>
            ) : (
              Object.entries(safeSybil).map(([clusterId, clusterData]) => {
                const funders = clusterData.funder_to_subgroups
                  ? Object.keys(clusterData.funder_to_subgroups)
                  : [];
                const subToFunder = clusterData.subgroup_to_funder || {};
                const noise = Array.isArray(clusterData.noise) ? clusterData.noise : [];

                return (
                  <div key={clusterId} className="mb-4">
                    <p className="text-purple-300 font-bold text-lg mb-2">
                      Cluster {clusterId}
                    </p>

                    {/* Sybil entities */}
                    {funders.length > 0 &&
                      funders.map((funder, idx) => {
                        const subgroups = clusterData.funder_to_subgroups[funder] || [];
                        //const linkedSubgroups = subgroups.map(s => subToFunder[s]).filter(Boolean);

                        return (
                          <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ duration: 0.3, delay: idx * 0.1 }}
                            className="mb-3 p-3 bg-gray-800 rounded-lg shadow-md border-l-4 border-purple-500"
                          >
                            <p className="text-purple-300 font-semibold">
                              Sybil entity {idx}:
                            </p>

                            {/* 钱包地址处理 */}
                            <p
                              className="text-white font-medium mt-1 truncate w-full"
                              title={funder} // hover 显示完整地址
                            >
                              {funder}
                            </p>

                            <p className="text-gray-300 text-sm mt-1">
  Strong Sybil evidence. <br/> Reason: Funding link found, {subgroups.length} subgroups source back to{' '}
  <span className="text-orange-400 font-semibold">{shortenHex(funder)}</span>. 
                            </p>
                           {subgroups.length > 0 && (
          <div className="mt-1 flex flex-wrap gap-1">
            <span className="text-gray-400 text-xs italic w-full">
              Subgroups linked to this funder:
            </span>
            {subgroups.map((sub, i) => (
              <span
                key={i}
                className="bg-purple-700/70 text-white text-xs px-2 py-1 rounded-md shadow-sm"
              >
                {sub}
              </span>
            ))}
          </div>
        )}
                          </motion.div>
                        );
                      })}

                    {/* Noise accounts */}
                    {noise.length > 0 && (
                      <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: funders.length * 0.1 }}
                        className="p-3 bg-gray-800 rounded-lg shadow-inner border-l-4 border-orange-500"
                      >
                        <p className="text-orange-300 font-semibold">
                          Isolated / Noise Accounts:
                        </p>
                        <ul className="mt-1 flex flex-wrap gap-1">
                          {noise.slice(0, 5).map((n, i) => (
                            <li
                              key={i}
                              className="bg-orange-600/70 text-white px-2 py-1 rounded-full text-xs truncate max-w-[120px]"
                              title={n} // hover 显示完整地址
                            >
                              {n}
                            </li>
                          ))}
                          {noise.length > 5 && (
                            <span className="text-gray-400 text-xs ml-2">
                              +{noise.length - 5} more
                            </span>
                          )}
                        </ul>
                        <p className="mt-1 text-gray-400 text-xs italic">
                          Total isolated accounts: {noise.length}
                        </p>
                      </motion.div>
                    )}
                  </div>
                );
              })
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </>

    <div style={{
      width: 320,
      marginLeft: 20,
      background: "#1c1c1c",
      padding: 14,
      borderRadius: 6,
      overflowY: "auto"
    }}>
      <h3>Info Panel</h3>
      

      {!selected && !activeCluster && (
        <p style={{ opacity: 0.6 }}>Click node or edge</p>
      )}

      {/* Node info */}
      {selected?.type === "node" && (
        <>
          <p><b>Wallet</b></p>
          <p style={{ fontSize: 12 }}>{selected.data.id}</p>

          <p><b>Behavior Vector</b></p>
          <pre style={{ fontSize: 11 }}>
            {labeledVector.join("\n")}
          </pre>
          <br/>

          <p><b>Variant</b></p>
          <pre style={{ fontSize: 11 }}>
            {selected.data.variant}
          </pre>
        </>
      )}

      {/* Edge info */}
      {selected?.type === "edge" && (
        <>
          <p><b>Funding Edge</b></p>
          <p style={{ fontSize: 12 }}>
            {(selected.data.source?.id || selected.data.source)} → {(selected.data.target?.id || selected.data.target)}
          </p>
          <p>Amount: {selected.data.amount}</p>
          <p>{selected.data.timestamp}</p>
        </>
      )}

      {/* Clusters */}
  {clusters && !activeCluster && (
  <>
    <p style={{ fontWeight: 600, marginBottom: 12, color: "#fff", fontSize: 14 }}>
      Clusters (Page {page + 1}/{totalPages})
    </p>

    {displayedClusters.map((cluster, idx) => (
      <div
        key={idx}
        onClick={() => setActiveCluster(cluster)}
        style={{
          marginBottom: 10,
          padding: 12,
          background: "linear-gradient(90deg, #222 0%, #2a2a2a 100%)",
          borderRadius: 8,
          cursor: "pointer",
          boxShadow: "0 2px 5px rgba(0,0,0,0.5)",
          transition: "transform 0.15s ease, background 0.15s ease",
        }}
        onMouseEnter={e => {
          e.currentTarget.style.transform = "scale(1.02)";
          e.currentTarget.style.background = "linear-gradient(90deg, #333 0%, #3a3a3a 100%)";
        }}
        onMouseLeave={e => {
          e.currentTarget.style.transform = "scale(1)";
          e.currentTarget.style.background = "linear-gradient(90deg, #222 0%, #2a2a2a 100%)";
        }}
      >
        <span style={{ color: "#FFD700", fontWeight: 600 }}>
          Cluster {page * clustersPerPage + idx + 1}
        </span>{" "}
        <span style={{ color: "#ccc" }}>({cluster.length} wallets)</span>
      </div>
    ))}

    {/* Pagination */}
    <div style={{ marginTop: 12, display: "flex", justifyContent: "space-between" }}>
      <button
        onClick={() => setPage(Math.max(page - 1, 0))}
        disabled={page === 0}
        style={{
          padding: "6px 14px",
          borderRadius: 6,
          border: "none",
          background: page === 0 ? "#555" : "linear-gradient(90deg, #444, #666)",
          color: "#fff",
          cursor: page === 0 ? "not-allowed" : "pointer",
          transition: "background 0.2s ease",
        }}
      >
        Prev
      </button>
      <button
        onClick={() => setPage(Math.min(page + 1, totalPages - 1))}
        disabled={page >= totalPages - 1}
        style={{
          padding: "6px 14px",
          borderRadius: 6,
          border: "none",
          background: page >= totalPages - 1 ? "#555" : "linear-gradient(90deg, #444, #666)",
          color: "#fff",
          cursor: page >= totalPages - 1 ? "not-allowed" : "pointer",
          transition: "background 0.2s ease",
        }}
      >
        Next
      </button>
    </div>
  </>
)}

{/* Active cluster detail */}
{activeCluster&& !activeDbscan && (
  <>
    <p style={{ fontWeight: 600, marginBottom: 8, color: "#fff", fontSize: 14 }}>
      Cluster Detail ({activeCluster.length} wallets)
    </p>
    <div style={{
      maxHeight: 240,
      overflowY: "auto",
      padding: 10,
      background: "#1a1a1a",
      borderRadius: 8,
      boxShadow: "0 2px 8px rgba(0,0,0,0.6)"
    }}>
      <pre style={{ fontSize: 12, color: "#ddd", whiteSpace: "pre-wrap", wordBreak: "break-all" }}>
        {activeCluster.join("\n")}
      </pre>
    </div>
    <button
      onClick={() => setActiveCluster(null)}
      style={{
        marginTop: 10,
        padding: "6px 12px",
        borderRadius: 6,
        border: "none",
        background: "linear-gradient(90deg, #444, #666)",
        color: "#fff",
        cursor: "pointer",
        transition: "background 0.2s ease",
      }}
    >
      Back to clusters
    </button>
    <button
  onClick={() => {
    const clusterIndex = clusters.findIndex(
      c => JSON.stringify(c) === JSON.stringify(activeCluster)
    );
    setActiveDbscan(dbscan[clusterIndex]);
  }}
  style={{
    marginBottom: 10,
    marginLeft: 10,
    padding: "6px 12px",
    borderRadius: 6,
    border: "none",
    background: "linear-gradient(90deg,#0066ff,#0099ff)",
    color: "#fff",
    cursor: "pointer"
  }}
>
  DBSCAN
</button>
  </>
)}

{/* DBSCAN view */}
{activeDbscan &&  (
  <>
    <p style={{ fontWeight: 600, marginBottom: 8, color: "#fff", fontSize: 14 }}>
      DBSCAN Subgroups
    </p>

    {!showSubgroupWindow && (
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: 12 }}>
        {Object.entries(activeDbscan.subgroups).map(([label, wallets]) => (
          <button
            key={label}
            onClick={() => {
              setCurrentSubgroup(wallets);
              setHighlightNodes(new Set(wallets));
              setShowSubgroupWindow(true); // 打开 subgroup 窗口
            }}
            style={{
              padding: "6px 12px",
              borderRadius: 6,
              border: "none",
              background: "#222",
              color: "#FFD700",
              cursor: "pointer",
            }}
          >
            Subgroup {label} ({wallets.length})
          </button>
        ))}

        {activeDbscan.noise.length > 0 && (
          <button
            onClick={() => {
              setCurrentSubgroup(activeDbscan.noise);
              setHighlightNodes(new Set(activeDbscan.noise));
              setShowSubgroupWindow(true); // 打开 subgroup 窗口
            }}
            style={{
              padding: "6px 12px",
              borderRadius: 6,
              border: "none",
              background: "#400",
              color: "#fff",
              cursor: "pointer",
            }}
          >
            Noise ({activeDbscan.noise.length})
          </button>
        )}
      </div>
    )}

    {/* Subgroup / Noise Window */}
{/* Subgroup / Noise Window */}
{showSubgroupWindow && currentSubgroup && (
  <div
    style={{
      position: "absolute",
      top: "20%",
      left: "20%",
      width: "400px",       // 固定宽度
      height: "300px",      // 固定高度
      background: "#1a1a1a",
      padding: 16,
      borderRadius: 8,
      boxShadow: "0 4px 12px rgba(0,0,0,0.8)",
      overflowY: "auto",    // 可滚动
      zIndex: 9999,
      cursor: "grab",       // 鼠标提示可拖动
    }}
    onMouseDown={(e) => {
      const div = e.currentTarget;
      div.style.cursor = "grabbing";
      const startX = e.clientX - div.offsetLeft;
      const startY = e.clientY - div.offsetTop;

      function onMouseMove(eMove) {
        div.style.left = `${eMove.clientX - startX}px`;
        div.style.top = `${eMove.clientY - startY}px`;
      }

      function onMouseUp() {
        div.style.cursor = "grab";
        window.removeEventListener("mousemove", onMouseMove);
        window.removeEventListener("mouseup", onMouseUp);
      }

      window.addEventListener("mousemove", onMouseMove);
      window.addEventListener("mouseup", onMouseUp);
    }}
  >
    <p style={{ fontWeight: 600, color: "#fff", marginBottom: 12 }}>
      Addresses ({currentSubgroup.length})
    </p>
    <pre style={{
      fontSize: 12,
      color: "#ccc",
      whiteSpace: "pre-wrap",
      wordBreak: "break-all",
      maxHeight: "220px",  // 内容超过窗口高度滚动
      overflowY: "auto",
    }}>
      {currentSubgroup.join("\n")}
    </pre>

    <button
      onClick={() => {
        setShowSubgroupWindow(false);
        setActiveDbscan(false);
        setHighlightNodes(null);
        setCurrentSubgroup(null);
      }}
      style={{
        marginTop: 12,
        padding: "6px 12px",
        borderRadius: 6,
        border: "none",
        background: "linear-gradient(90deg,#444,#666)",
        color: "#fff",
        cursor: "pointer"
      }}
    >
      Back
    </button>
  </div>
)}
  </>
)}


{selected?.type === "node" && similarities && (
  <div style={{ marginTop: 12 }}>
    {/* Container */}
    <p style={{ fontWeight: 600, marginBottom: 8 }}>Top Similar Wallets</p>

    <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
      {/* Behavior Similarity Card */}
      <div style={{
        flex: 1,
        minWidth: 140,
        background: "#1f1f1f",
        borderRadius: 6,
        padding: 10,
        maxHeight: 160,
        overflowY: "auto",
        boxShadow: "0 2px 6px rgba(0,0,0,0.5)"
      }}>
        <p style={{ fontSize: 12, fontWeight: 500, marginBottom: 6, color: "#aaa" }}>Behavior</p>
        <ul style={{ paddingLeft: 16, fontSize: 11, margin: 0 }}>
          {Object.entries(similarities.behavior)
            .filter(([key]) => key.includes(selected.data.id))
            .sort((a,b) => b[1] - a[1])
            //.slice(0,5)
            .map(([key, sim]) => {
              const other = key.replace(selected.data.id, "").replace("-", "").replace(",", "");
              return (
                <li key={key} style={{ marginBottom: 4, display: "flex", justifyContent: "space-between" }}>
                  <span>{other}</span>
                  <span style={{
                    background: "#333",
                    color: "#0f0",
                    padding: "0 6px",
                    borderRadius: 4,
                    fontSize: 10,
                    fontWeight: 600
                  }}>{sim.toFixed(3)}</span>
                </li>
              )
            })
          }
        </ul>
      </div>

      {/* Variant Similarity Card */}
      <div style={{
        flex: 1,
        minWidth: 140,
        background: "#1f1f1f",
        borderRadius: 6,
        padding: 10,
        maxHeight: 160,
        overflowY: "auto",
        boxShadow: "0 2px 6px rgba(0,0,0,0.5)"
      }}>
        <p style={{ fontSize: 12, fontWeight: 500, marginBottom: 6, color: "#aaa" }}>Variant</p>
        <ul style={{ paddingLeft: 16, fontSize: 11, margin: 0 }}>
          {Object.entries(similarities.variant)
            .filter(([key]) => key.includes(selected.data.id))
            .sort((a,b) => b[1] - a[1])
            //.slice(0,5)
            .map(([key, sim]) => {
              const other = key.replace(selected.data.id, "").replace("-", "").replace(",", "");
              return (
                <li key={key} style={{ marginBottom: 4, display: "flex", justifyContent: "space-between" }}>
                  <span>{other}</span>
                  <span style={{
                    background: "#333",
                    color: "#0f0",
                    padding: "0 6px",
                    borderRadius: 4,
                    fontSize: 10,
                    fontWeight: 600
                  }}>{sim.toFixed(3)}</span>
                </li>
              )
            })
          }
        </ul>
      </div>

      {/* Weighted Similarity Card */}
      <div style={{
        flex: 1,
        minWidth: 140,
        background: "#1f1f1f",
        borderRadius: 6,
        padding: 10,
        maxHeight: 160,
        overflowY: "auto",
        boxShadow: "0 2px 6px rgba(0,0,0,0.5)",
        marginTop: 8
      }}>
        <p style={{ fontSize: 12, fontWeight: 500, marginBottom: 6, color: "#aaa" }}>Weighted Similarity (≥85%)</p>
        <ul style={{ paddingLeft: 16, fontSize: 11, margin: 0 }}>
          {Object.entries(similarities.weighted)
            .filter(([key, sim]) => key.includes(selected.data.id) && sim >= 0.5) // 只保留 ≥85%
            .sort((a,b) => b[1] - a[1])
            //.slice(0,5)
            .map(([key, sim]) => {
              const other = key.replace(selected.data.id, "").replace("-", "").replace(",", "");
              return (
                <li key={key} style={{ marginBottom: 4, display: "flex", justifyContent: "space-between" }}>
                  <span>{other}</span>
                  <span style={{
                    background: "#333",
                    color: "#0f0",
                    padding: "0 6px",
                    borderRadius: 4,
                    fontSize: 10,
                    fontWeight: 600
                  }}>{sim.toFixed(3)}</span>
                </li>
              )
            })
          }
        </ul>
      </div>

    </div>
  </div>
)}

    </div>

    </div>
  );
}