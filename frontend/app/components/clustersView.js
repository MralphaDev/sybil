"use client";

import React, { useState,useEffect } from "react";
import Heatmap from "./heatmap";

// 展示 clusters 的组件，包含分页和 heatmap
export default function ClustersView({ clusters, similarities, onClose  }) {
  const [currentCluster, setCurrentCluster] = useState(0);
const [loading, setLoading] = useState(true);
  if (!clusters || !clusters.length) return <div>Loading...</div>;

  useEffect(() => {
  const timer = setTimeout(() => {
    setLoading(false);
  }, 1000); // 关键：让 UI 先渲染出来

  return () => clearTimeout(timer);
}, []);

  return (
    
    <div style={{  position: "fixed",   // 🔥 关键
    top: 0,
    left: 0,
    width: "100vw",
    height: "100vh",
    background: "#121212",
    zIndex: 9999,
    overflowY: "auto",
    padding: 20,}}>
      <button
  onClick={onClose}
  style={{
    position: "absolute",
    top: 20,
    right: 20,
    padding: "8px 14px",
    background: "#444",
    color: "#fff",
    border: "none",
    borderRadius: 6,
    cursor: "pointer",
    fontSize: 14
  }}
>
  ✕ Close
</button>
      {/* 分页按钮 */}
      <div style={{ margin: "10px 0" }}>
        <button
          onClick={() =>
            setCurrentCluster(
              (currentCluster - 1 + clusters.length) % clusters.length
            )
          }
        >
          Prev
        </button>
        <span style={{ margin: "0 10px" }}>
          Cluster {currentCluster + 1} / {clusters.length}
        </span>
        <button
          onClick={() =>
            setCurrentCluster((currentCluster + 1) % clusters.length)
          }
        >
          Next
        </button>
      </div>

      {/* heatmap */}
{loading ? (
<div
  style={{
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    height: "80vh",
    flexDirection: "column",
    gap: 10
  }}
>
  <div
    style={{
      width: 40,
      height: 40,
      border: "4px solid #444",
      borderTop: "4px solid #fff",
      borderRadius: "50%",
      animation: "spin 1s linear infinite"
    }}
  />
  <div>Loading heatmap...</div>

  <style>
    {`
      @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
      }
    `}
  </style>
</div>
) : (
  <Heatmap
    cluster={clusters[currentCluster]}
    similarities={similarities?.weighted || {}}
  />
)}
    </div>
  );
}