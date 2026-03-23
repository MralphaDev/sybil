"use client";

import { useState } from "react";
import GraphCanvas from "./components/GraphCanvas";
import InfoPanel from "./components/InfoPanel";
import useGraph from "./components/useGraph";
import ClustersView from "./components/clustersView";
import { index } from "d3";

export default function Home() {
  const { nodes, edges, clusters, similarities, dbscan, sybil_entities,aggregated_relations } = useGraph();
  const [selected, setSelected] = useState(null);
 const [showHeatmap, setShowHeatmap] = useState(false);
 const [highlightNodes, setHighlightNodes] = useState(null); // Set of wallet ids 闪烁节点


  return (
    <div
      style={{
        display: "flex",
        background: "#121212",
        color: "#fff",

        
      }}
    >
      
      {/* 左侧图 */}
      <GraphCanvas nodes={nodes} edges={edges} selected={selected} onSelect={setSelected} clusters={clusters} highlightNodes={highlightNodes} setHighlightNodes={setHighlightNodes} />

     {/* Heatmap toggle button */}
      {<button
        onClick={() => setShowHeatmap(!showHeatmap)}
        style={{
          position: "absolute",
          top: 25,
          right: 25,
          padding: "8px 14px",
          background: "#444",
          color: "white",
          border: "none",
          borderRadius: 10,
          cursor: "pointer",
          zIndex: 1000
        }}
      >
        {showHeatmap ? "Close Heatmap" : "Show Heatmap"}
      </button>}

      {/* Heatmap modal */}
      {showHeatmap && (
        <ClustersView
          clusters={clusters}
          similarities={similarities}
          onClose={() => setShowHeatmap(false)}
        />
      )}


      {/* 左侧信息面板 */}
      {<InfoPanel
        selected={selected}
        clusters={clusters}
        similarities={similarities}
        dbscan={dbscan}
        sybil_entities={sybil_entities}
        aggregated_relations={aggregated_relations}
        setHighlightNodes={setHighlightNodes}

      />}
    </div>
  );
}