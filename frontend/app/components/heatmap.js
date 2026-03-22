"use client";

import React, { useMemo } from "react";
import { Chart as ChartJS, Tooltip, Legend, Title, CategoryScale } from "chart.js";
import { MatrixController, MatrixElement } from "chartjs-chart-matrix";
import { Chart } from "react-chartjs-2";

ChartJS.register(MatrixController, MatrixElement, Tooltip, Legend, Title, CategoryScale);

export default function Heatmap({ cluster, similarities }) {

  const shortAddr = (addr) => addr.slice(0,6);

  const { data, xLabels, yLabels } = useMemo(() => {

    const n = cluster.length;

    const xLabels = cluster.map(shortAddr);
    const yLabels = cluster.map(shortAddr);

    const data = [];

    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {

        const key1 = `${cluster[i]}-${cluster[j]}`;
        const key2 = `${cluster[j]}-${cluster[i]}`;

        const value = similarities[key1] ?? similarities[key2] ?? 0;

        data.push({
          x: shortAddr(cluster[j]),
          y: shortAddr(cluster[i]),
          v: value,
          fullX: cluster[j],
          fullY: cluster[i]
        });

      }
    }

    return { data, xLabels, yLabels };

  }, [cluster, similarities]);


  const colorScale = (v) => {

    if (v >= 0.9) return "#ff0000";   // 红
    if (v >= 0.7) return "#ff8c00";   // 橙
    if (v >= 0.5) return "#2ecc71";   // 绿
    if (v >= 0.3) return "#90ee90";   // 浅绿

    return "#d8f5d8";                 // 很浅绿
  };


  const chartData = {
    datasets: [
      {
        label: "Similarity Matrix",
        data,
        backgroundColor: ctx => colorScale(ctx.dataset.data[ctx.dataIndex].v),

        width: ({ chart }) =>
          (chart.chartArea?.width || 400) / cluster.length - 2,

        height: ({ chart }) =>
          (chart.chartArea?.height || 400) / cluster.length - 2,
      }
    ]
  };


  const options = {

    responsive: true,

    plugins: {

      legend: { display: false },

      tooltip: {
        callbacks: {
          label: ctx => {
            const d = ctx.raw;
            return `${shortAddr(d.fullY)} - ${shortAddr(d.fullX)} : ${d.v.toFixed(2)}`;
          }
        }
      },

      title: {
        display: true,
        text: `Cluster Heatmap (size: ${cluster.length})`
      }

    },

    scales: {

      x: {
        type: "category",
        labels: xLabels,
        display: false
      },

      y: {
        type: "category",
        labels: yLabels,
        ticks: {
          padding: 2,
          font: { size: 10 }
        },
        grid: { display: false }
      }

    }

  };


  return (
    <div style={{ margin: "20px", width: "80%" ,height: "90%"}}>

      <Chart type="matrix" data={chartData} options={options} />

      {/* Legend */}
      <div
        style={{
          marginTop: 15,
          display: "flex",
          alignItems: "center",
          gap: 6,
          fontSize: 12
        }}
      >

        <span>Low</span>

        <div style={{width:30,height:10,background:"#d8f5d8"}} title="<0.3"/>
        <div style={{width:30,height:10,background:"#90ee90"}} title="0.3+" />
        <div style={{width:30,height:10,background:"#2ecc71"}} title="0.5+" />
        <div style={{width:30,height:10,background:"#ff8c00"}} title="0.7+" />
        <div style={{width:30,height:10,background:"#ff0000"}} title="0.9+" />

        <span>High</span>

      </div>

    </div>
  );
}