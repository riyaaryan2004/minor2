import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement);

function HeartChartDetailed({ data }) {
  if (!data || data.length === 0) {
    return (
      <p style={{ opacity: 0.6, fontStyle: "italic" }}>
        No detailed HR data available
      </p>
    );
  }

  const chartData = {
    labels: data.map((d) => d.x),
    datasets: [
      {
        label: "Heart Rate (Minute-Level)",
        data: data.map((d) => d.hr),
        borderColor: "#38bdf8",
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0,
        fill: true,
        backgroundColor: "rgba(56,189,248,0.08)",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,

    scales: {
      x: {
        ticks: {
          color: "#94a3b8",
          autoSkip: false,
          callback: function (value) {
            if (value % 60 === 0) {
              return value / 60;
            }
            return "";
          },
        },
        grid: {
          color: "rgba(255,255,255,0.05)",
        },
      },

      y: {
        ticks: { color: "#94a3b8" },
        min: 40,
        max: 160,
        grid: {
          color: "rgba(255,255,255,0.05)",
        },
      },
    },

    plugins: {
      legend: {
        labels: { color: "#cbd5f5" },
      },
    },
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "10px",
      }}
    >
      <h2
        style={{
          fontSize: "18px",
          fontWeight: "600",
          color: "#e2e8f0",
        }}
      >
        📈 Detailed Heart Rate
      </h2>

      <div
        style={{
          height: "300px",
          padding: "15px",
          borderRadius: "14px",
          background: "rgba(255, 255, 255, 0.03)",
          border: "1px solid rgba(255,255,255,0.06)",
        }}
      >
        <Line data={chartData} options={options} />
      </div>
    </div>
  );
}

export default HeartChartDetailed;