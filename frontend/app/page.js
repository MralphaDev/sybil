"use client";

import { useState } from "react";
import GraphCanvas from "./components/GraphCanvas";
import InfoPanel from "./components/InfoPanel";
import useGraph from "./components/useGraph";
import ClustersView from "./components/clustersView";

export default function Home() {
  const { nodes, edges, clusters, similarities, dbscan, sybil_entities } = useGraph();
  const [selected, setSelected] = useState(null);
 const [showHeatmap, setShowHeatmap] = useState(false);
 const [highlightNodes, setHighlightNodes] = useState(null); // Set of wallet ids 闪烁节点


  return (
    <div
      style={{
        display: "flex",
        background: "#121212",
        color: "#fff",
        height: "100vh",
        width: "100vw",
        
      }}
    >
      
      {/* 左侧图 */}
      <GraphCanvas nodes={nodes} edges={edges} onSelect={setSelected} clusters={clusters} highlightNodes={highlightNodes}/>

     {/* Heatmap toggle button */}
      <button
        onClick={() => setShowHeatmap(!showHeatmap)}
        style={{
          position: "absolute",
          top: 20,
          right: 20,
          padding: "8px 14px",
          background: "#444",
          color: "white",
          border: "none",
          borderRadius: 6,
          cursor: "pointer"
        }}
      >
        {showHeatmap ? "Close Heatmap" : "Show Heatmap"}
      </button>

      {/* Heatmap modal */}
      {showHeatmap && (
        <ClustersView
          clusters={clusters}
          similarities={similarities}
          onClose={() => setShowHeatmap(false)}
        />
      )}


      {/* 右侧信息面板 */}
      <InfoPanel
        selected={selected}
        clusters={clusters}
        similarities={similarities}
        dbscan={dbscan}
        sybil_entities={sybil_entities}
        setHighlightNodes={setHighlightNodes}
      />
    </div>
  );
}