import {
  Chart as ChartJS,
  LineElement,
  CategoryScale,
  LinearScale,
  PointElement,
  Tooltip,
  Filler,
} from "chart.js";

import { Line } from "react-chartjs-2";

ChartJS.register(LineElement, CategoryScale, LinearScale, PointElement, Tooltip, Filler);

function HeartChart({ data }) {
  if (!data || data.length === 0) {
    return (
      <p style={{ opacity: 0.7, fontStyle: "italic" }}>
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
        label: "Heart Rate",
        data: fullData.map((d) => d.hr),
        borderWidth: 2,
        tension: 0.35,
        spanGaps: true,
        fill: true,
        borderColor: "#22d3ee",
        backgroundColor: "rgba(34, 211, 238, 0.12)",
        pointRadius: 2,
        pointBackgroundColor: "#67e8f9",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "rgba(15, 23, 42, 0.95)",
        borderColor: "rgba(148, 163, 184, 0.2)",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: { color: "#94a3b8" },
        grid: { color: "rgba(148, 163, 184, 0.08)" },
      },
      y: {
        ticks: { color: "#94a3b8" },
        min: 40,
        max: 160,
        grid: { color: "rgba(148, 163, 184, 0.08)" },
      },
    },
  };

  return (
    <div style={{ height: "320px" }}>
      <Line data={chartData} options={options} />
    </div>
  );
}

export default HeartChart;