"use client";

import { useState, useEffect, useRef } from "react";
import * as d3 from "d3";

export default function GraphCanvas({ nodes, edges, onSelect , highlightNodes, clusters }) {
const [mounted, setMounted] = useState(false);
 const svgRef = useRef(null);
const baseColors = ["#ef7112", "#da00ab", "#00d58c"];
const clusterColorMap = new Map();
// sort clusters by size DESC
const sortedClusters = [...clusters].sort((a, b) => b.length - a.length);
sortedClusters.forEach((cluster, i) => {
  // cycle through baseColors if i >= 3
  const color = baseColors[i % baseColors.length];

  cluster.forEach(address => {
    clusterColorMap.set(address.toLowerCase(), color);
  });
});


  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {

    if (!svgRef.current || nodes.length === 0) return;

    //const width = window.innerWidth * 0.75;
    //const height = window.innerHeight * 0.9;

    const width = window.innerWidth * 0.8;
const height = window.innerHeight;

    // 每个 cluster 的中心点（相对画布中心偏移）
    const clusterCenters = sortedClusters.map((cluster, i) => {
      const angle = (i / sortedClusters.length) * 2 * Math.PI; // 圆周均匀分布
      const radius = 50; // cluster 之间的距离
      return {
        x: width / 2 + Math.cos(angle) * radius,
        y: height / 2 + Math.sin(angle) * radius,
      };
    });

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();
    const defs = svg.append("defs");
const bgGradient = defs.append("radialGradient")
  .attr("id", "bgGradient")
  .attr("cx", "50%")  // center x
  .attr("cy", "50%")  // center y
  .attr("r", "50%")   // glow covers 50% of total width/height
  .attr("fx", "50%")
  .attr("fy", "50%");

// subtle light at center
bgGradient.append("stop")
  .attr("offset", "0%")
  .attr("stop-color", "#03051a") // just a touch lighter than #000000
  .attr("stop-opacity", 1);

// quickly fade to black by ~50% radius
bgGradient.append("stop")
  .attr("offset", "40%")
  .attr("stop-color", "#03041c")
  .attr("stop-opacity", 1);

// outer edges: black
bgGradient.append("stop")
  .attr("offset", "100%")
  .attr("stop-color", "#000000")
  .attr("stop-opacity", 1);

// draw a rect covering the whole viewport
svg.append("rect")
   .attr("width", width)
   .attr("height", height)
   .attr("fill", "url(#bgGradient)");

// edge arrow with bow-shaped head and extended body
defs.append("marker")
  .attr("id", "arrow")
  .attr("viewBox", "0 -5 15 10")  // 放大箭头区域
  .attr("refX", 15)               // 调整箭头距离节点中心的距离
  .attr("refY", 0)
  .attr("markerWidth", 20)
  .attr("markerHeight", 20)
  .attr("orient", "auto")
  .append("path")
    .attr("d", "M0,-5 Q7,0 0,5 L15,0 Z") // 弓形箭头路径
    .attr("fill", "#C0C0C0");

    // get unique cluster colors
const clusterColors = [...new Set(Array.from(clusterColorMap.values()))];

// create one radial gradient per cluster color
clusterColors.forEach((color, i) => {
 const grad = defs.append("radialGradient")
  .attr("id", `nodeOverlay-${i}`)
  .attr("cx", "30%")
  .attr("cy", "30%")
  .attr("r", "80%");

// strong color near light source
grad.append("stop")
  .attr("offset", "0%")
  .attr("stop-color", color)
  .attr("stop-opacity", 0.35);

// smooth spread across whole node
grad.append("stop")
  .attr("offset", "40%")
  .attr("stop-color", color)
  .attr("stop-opacity", 0.15);

// very faint tint across rest
grad.append("stop")
  .attr("offset", "75%")
  .attr("stop-color", color)
  .attr("stop-opacity", 0.05);

// fade out completely
grad.append("stop")
  .attr("offset", "100%")
  .attr("stop-color", color)
  .attr("stop-opacity", 0);
});
    
    const g = svg.append("g");


    // ---------- Build node map ----------
    const nodeMap = new Map(nodes.map(n => [n.id, n]));

    // ---------- Fix edges ----------
    const d3Edges = edges
      .map(e => ({
        ...e,
        source: nodeMap.get(e.source),
        target: nodeMap.get(e.target)
      }))
      .filter(e => e.source && e.target);

      //初始化节点位置靠近 cluster 中心，避免初始重叠
      nodes.forEach(d => {
  const clusterIndex = sortedClusters.findIndex(c => c.includes(d.id));
  const center = clusterCenters[clusterIndex];

  // 节点随机散布在 cluster 中心附近，避免重叠
  const spread = 50; // 节点在 cluster 中的散布半径
  d.x = center.x + (Math.random() - 0.5) * spread;
  d.y = center.y + (Math.random() - 0.5) * spread;
});

    // ---------- Simulation ----------
    const sim = d3.forceSimulation(nodes)
      .force("link",
        d3.forceLink(d3Edges)
          .id(d => d.id)
          .distance(180)//260
      )
      .force("charge",
        d3.forceManyBody().strength(-30)
      )
      .force("center",
        d3.forceCenter(width / 2, height / 2)
      )
      .force("collision",
        d3.forceCollide().radius(15) // 增加碰撞半径，减少节点重叠
      );

      sim.on("end", () => {
  /*nodes.forEach(d => {
    d.fx = d.x;
    d.fy = d.y;
  });*/
});

    // ---------- Draw edges ----------
    const link = g.append("g")
      .selectAll("line")
      .data(d3Edges)
      .join("line")
      .attr("stroke", "#C0C0C0") //#ff9800
      .attr("stroke-width", 1)
      .attr("marker-end", "url(#arrow)")  // <-- THIS IS MISSING
      .style("cursor", "pointer")


    // ---------- Draw nodes ----------
    const node = g.append("g")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .attr("class", "node") // 👈 add this class
      .style("cursor", "pointer")
     
      //apply ripple effect on click and select node
      .on("click", (_, d) => {
  // 1️⃣ Trigger your onSelect callback
  onSelect({ type: "node", data: d });

  // 2️⃣ Get the cluster color
  const color = clusterColorMap.get(d.id.toLowerCase()) || "#fff";

  // 3️⃣ Smooth auto-zoom to the node using existing zoomBehavior
  const svgWidth = window.innerWidth * 0.75;
  const svgHeight = window.innerHeight * 0.9;
  const scale = 2; // zoom amount
  const translateX = svgWidth / 2 - d.x * scale;
  const translateY = svgHeight / 2 - d.y * scale;

  svg.transition()
    .duration(600)
    .call(
      zoomBehavior.transform,
      d3.zoomIdentity.translate(translateX, translateY).scale(scale)
    )
    .on("end", () => {
      // 4️⃣ Trigger ripple effect AFTER zoom ends
      const transform = d3.zoomTransform(svg.node());
      const x = transform.applyX(d.x);
      const y = transform.applyY(d.y);

      const rippleCount = 3;
      const maxRadius = 120;
      const duration = 1000;

      for (let i = 0; i < rippleCount; i++) {
        const ripple = svg.append("circle")
          .attr("cx", x)
          .attr("cy", y)
          .attr("r", 0)
          .attr("stroke", color)
          .attr("stroke-width", 3)
          .attr("fill", "none")
          .attr("opacity", 0.5);

        ripple.transition()
          .delay(i * 150)
          .duration(duration)
          .attr("r", maxRadius)
          .attr("opacity", 0)
          .remove();
      }
    });
})
      .call(
        d3.drag()
          .on("start", (event, d) => {

            if (!event.active) sim.alphaTarget(0.3).restart();

            d.fx = d.x;
            d.fy = d.y;

          })
          .on("drag", (event, d) => {

            d.fx = event.x;
            d.fy = event.y;

          })
          .on("end", (event, d) => {

            if (!event.active) sim.alphaTarget(0);
            d.fx = null; // release the node
            d.fy = null;

          })
      );
    

node.append("circle")
  .attr("r", 21)
  .attr("stroke", d => clusterColorMap.get(d.id.toLowerCase()) || "#999")
  .attr("stroke-width", 6)
.attr("fill", "#000") // 👈 pure black base
.attr("stroke-dasharray", d => {
    // Check if this node appears in any edge
    const isIsolated = !d3Edges.some(e => e.source.id === d.id || e.target.id === d.id);
    return isIsolated ? "6 5" : null;   // broken stroke only for isolated nodes
  })

node.append("circle")
  .attr("r", 21)
  .attr("fill", d => {
    const color = clusterColorMap.get(d.id.toLowerCase());
    const index = clusterColors.indexOf(color);
    return `url(#nodeOverlay-${index})`;
  })
  .attr("pointer-events", "none"); // so clicks still work

    // node label
    node.append("text")
      //.text(d => d.id.slice(0, 6))
      .attr("fill", "#fff")
      .attr("font-size", 10)
      .attr("text-anchor", "middle")
      .attr("dy", 4);

      //const defs = svg.append("defs");

const gradient = defs.append("linearGradient")
  .attr("id", "nodeGradient")
  .attr("x1", "0%")
  .attr("y1", "0%")
  .attr("x2", "100%")
  .attr("y2", "100%");

gradient.append("stop")
  .attr("offset", "0%")
  .attr("stop-color", "#111");

gradient.append("stop")
  .attr("offset", "70%") // keep most area black
  .attr("stop-color", "#111");

gradient.append("stop")
  .attr("offset", "100%")
  .attr("stop-color", "#ef7112")
  .attr("stop-opacity", 0.25); // softer orange

      
    // ---------- Token animation ----------
    const tokenGroup = g.append("g");

    const tokens = tokenGroup
      .selectAll("circle")
      .data(d3Edges)
      .join("circle")
      .attr("r", 3)
      .attr("fill", d => clusterColorMap.get(d.source.id.toLowerCase()) || "#ef7112")
      .each(d => d.t = Math.random());


      //zoom into node on click and create ripple effect
      // ---------- Zoom ----------
const zoomBehavior = d3.zoom()
  .scaleExtent([0.2, 4])
  .on("zoom", (event) => {
    g.attr("transform", event.transform);
  });

svg.call(zoomBehavior);
    //Ripple effect on node click


    // ---------- Simulation tick ----------
    sim.on("tick", () => {

      /*link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);*/
      // 节点半径（要和你 circle 的 r 对齐）
const nodeRadius = 21;

// ---------- Simulation tick ----------
sim.on("tick", () => {

  link
    // 起点 x：从 source 中心往 target 方向移动一个半径
    .attr("x1", d => {
      const dx = d.target.x - d.source.x;
      const dy = d.target.y - d.source.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      // 单位向量 * 半径 → 偏移量
      const offsetX = (dx / dist) * nodeRadius;

      return d.source.x + offsetX;
    })

    // 起点 y
    .attr("y1", d => {
      const dx = d.target.x - d.source.x;
      const dy = d.target.y - d.source.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      const offsetY = (dy / dist) * nodeRadius;

      return d.source.y + offsetY;
    })

    // 终点 x：从 target 中心往 source 方向回缩一个半径
    .attr("x2", d => {
      const dx = d.target.x - d.source.x;
      const dy = d.target.y - d.source.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      const offsetX = (dx / dist) * nodeRadius;

      return d.target.x - offsetX;
    })

    // 终点 y
    .attr("y2", d => {
      const dx = d.target.x - d.source.x;
      const dy = d.target.y - d.source.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      const offsetY = (dy / dist) * nodeRadius;

      return d.target.y - offsetY;
    });

  // 节点位置更新（不变）
    node
      .attr("transform", d => `translate(${d.x},${d.y})`);
  });

    });

    

    // ---------- Animate tokens ----------
    function animateTokens() {

      tokens.each(function(d) {

        if (!d.source?.x || !d.target?.x) return;

        d.t += 0.002;

        if (d.t > 1) d.t = 0;

        const x = d.source.x + (d.target.x - d.source.x) * d.t;
        const y = d.source.y + (d.target.y - d.source.y) * d.t;

        d3.select(this)
          .attr("cx", x)
          .attr("cy", y);

      });

      requestAnimationFrame(animateTokens);

    }

    animateTokens();

     svg.selectAll("circle")
    node.select("circle")
  //.attr("stroke", d => highlightNodes?.has(d.id) ? "#FF0000" : clusterColorMap.get(d.id.toLowerCase()) || "#999");
    //window.alert("the highlight nodes: " + (highlightNodes ? Array.from(highlightNodes) : "None"));

    // ---------- Zoom ----------
    svg.call(
      d3.zoom()
        .scaleExtent([0.2, 4])
        .on("zoom", (event) => {

          g.attr("transform", event.transform);

        })
    );

  }, [nodes, edges]);

  useEffect(() => {
  if (!svgRef.current) return;

  const svg = d3.select(svgRef.current);

  svg.selectAll("g.node circle")
    .attr("stroke", d => highlightNodes?.has(d.id) 
      ? "#FF0000" 
      : clusterColorMap.get(d.id.toLowerCase()) || "#999"
    );

}, [highlightNodes]);

return (
  <div style={{ width: "100vw", height: "100v", position: "relative" }}>

    {!mounted || nodes.length === 0 && (
      <div
        style={{
          position: "absolute",
          inset: 0,
          zIndex: 10,
          overflow: "hidden",
          background: "radial-gradient(circle at center, #02030f 0%, #000 80%)"
        }}
      >
        {/* 宇宙 glow */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: 500,
            height: 500,
            transform: "translate(-50%, -50%)",
            background: "radial-gradient(circle, rgba(120,0,255,0.25), transparent 70%)",
            filter: "blur(120px)"
          }}
        />

        {/* 🌠 流星向右，尾巴在左，大头在右，从屏幕左侧刷新 */}
        {/*[...Array(15)].map((_, i) => (
  <div
    key={i}
    style={{
      position: "absolute",
      top: `${Math.random() * 90}%`,
      left: `${Math.random() * 20}%`,
      width: 120 + Math.random() * 80,
      height: 2,
      background: "linear-gradient(to left, white, transparent)",
      opacity: 0.8,
      borderRadius: 2,
      animationName: "meteorRightLong",
      animationDuration: "2.5s",
      animationTimingFunction: "linear",
      animationIterationCount: "infinite",
      animationDelay: `${i * 0.15}s`, // 每颗流星错开启动
      boxShadow: "0 0 8px rgba(255,255,255,0.8)"
    }}
  />
))*/}

        {/* 星点 */}
        {[...Array(40)].map((_, i) => (
          <div
            key={i}
            style={{
              position: "absolute",
              width: Math.random() * 2 + 1,
              height: Math.random() * 2 + 1,
              background: "white",
              borderRadius: "50%",
              top: `${Math.random() * 100}%`,
              left: `${Math.random() * 100}%`,
              opacity: 0.3,
              animation: `twinkle ${2 + Math.random() * 3}s infinite`
            }}
          />
        ))}

        {/* 🔺 三角形 + 核心 */}
        <div
          style={{
            position: "absolute",
            top: "50%",
            left: "50%",
            width: 200,
            height: 200,
            transform: "translate(-50%, -50%)"
          }}
        >
          {/* 外环 */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 140,
              height: 140,
              transform: "translate(-50%, -50%)",
              borderRadius: "50%",
              border: "2px dashed rgba(255,255,255,0.2)",
              animation: "spinDash 6s linear infinite, pulseRing 3s ease-in-out infinite",
              boxShadow: "0 0 25px rgba(168,85,247,0.4)"
            }}
          />

          {/* 内核光圈 */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 80,
              height: 80,
              transform: "translate(-50%, -50%)",
              borderRadius: "50%",
              background: "radial-gradient(circle, rgba(255,255,255,0.15), transparent 70%)",
              animation: "pulseCore 2.5s ease-in-out infinite"
            }}
          />

          {/* 三角形 */}
          {[0, 1, 2].map((i) => {
            const colors = ["#a855f7", "#ec4899", "#f97316"];
            return (
              <div
                key={i}
                style={{
                  position: "absolute",
                  width: 0,
                  height: 0,
                  borderLeft: "25px solid transparent",
                  borderRight: "25px solid transparent",
                  borderBottom: `45px solid ${colors[i]}`,
                  top: "50%",
                  left: "50%",
                  transform: "translate(-50%, -50%)",
                  filter: `drop-shadow(0 0 18px ${colors[i]})`,
                  animation: `
                    rotateTri 6s linear infinite,
                    breatheTri 3s ease-in-out infinite
                  `,
                  animationDelay: `${i * 0.4}s`
                }}
              />
            );
          })}

          {/* LOADING */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              transform: "translate(-50%, -50%)",
              fontSize: 12,
              letterSpacing: "4px",
              fontWeight: 600,
              color: "rgba(255,255,255,0.85)",
              textShadow: "0 0 12px rgba(168,85,247,0.9)",
              animation: "loadingPulse 2s ease-in-out infinite"
            }}
          >
            LOADING
          </div>

          {/* 扫描线 */}
          <div
            style={{
              position: "absolute",
              top: "50%",
              left: "50%",
              width: 120,
              height: 20,
              transform: "translate(-50%, -50%)",
              overflow: "hidden"
            }}
          >
            <div
              style={{
                width: "40%",
                height: "100%",
                background: "linear-gradient(90deg, transparent, rgba(255,255,255,0.9), transparent)",
                animation: "scanMove 2s linear infinite"
              }}
            />
          </div>

        </div>

        {/* KEYFRAMES */}
        <style>
          {`
          @keyframes rotateTri {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
          }
          @keyframes breatheTri {
            0%,100% { margin-top: -10px; opacity: 0.8; }
            50% { margin-top: 20px; opacity: 1; }
          }
          @keyframes spinDash {
            0% { transform: translate(-50%, -50%) rotate(0deg); }
            100% { transform: translate(-50%, -50%) rotate(360deg); }
          }
          @keyframes pulseRing {
            0%,100% { transform: translate(-50%, -50%) scale(1); opacity: 0.6; }
            50% { transform: translate(-50%, -50%) scale(1.15); opacity: 1; }
          }
          @keyframes pulseCore {
            0%,100% { transform: translate(-50%, -50%) scale(0.9); opacity: 0.6; }
            50% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
          }
          @keyframes twinkle {
            0%,100% { opacity: 0.1; }
            50% { opacity: 0.6; }
          }
          /* 流星滑行长距离，大头朝右，尾巴在左 */
          @keyframes meteorRightLong {
            0% { transform: translateX(0); opacity: 1; }
            75% { opacity: 1; }
            100% { transform: translateX(800px); opacity: 0; }
          }
          @keyframes loadingPulse {
            0%,100% { opacity: 0.6; letter-spacing: 4px; }
            50% { opacity: 1; letter-spacing: 6px; }
          }
          @keyframes scanMove {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(250%); }
          }
        `}
        </style>

      </div>
    )}

    {/* 原始 SVG */}
    <svg
      ref={svgRef}
      width="100%"
      height="100vh"
      style={{ display: "block" }}
    />
  </div>
);

}