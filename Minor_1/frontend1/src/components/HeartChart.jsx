import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement);

function HeartChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <p style={{ opacity: 0.6, fontStyle: "italic" }}>
        No heart rate data available
      </p>
    );
  }

  const fullData = Array.from({ length: 24 }, (_, i) => {
    const found = data.find((d) => d.hour === i);
    return { hour: i, hr: found ? found.hr : null };
  });

  const chartData = {
    labels: fullData.map((d) => d.hour),
    datasets: [
      {
        label: "Heart Rate (BPM)",
        data: fullData.map((d) => d.hr),
        borderWidth: 2,
        tension: 0.4,
        spanGaps: true,
        fill: true,

        borderColor: "#22c55e",
        backgroundColor: "rgba(34,197,94,0.15)",
        pointRadius: 2,
        pointBackgroundColor: "#4ade80",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: "#cbd5f5",
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "#94a3b8" },
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
        💓 Heart Rate (Summary)
      </h2>

      <div
        style={{
          height: "320px",
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

export default HeartChart;