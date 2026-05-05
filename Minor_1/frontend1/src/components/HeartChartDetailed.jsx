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

function HeartChartDetailed({ data }) {
  if (!Array.isArray(data) || data.length === 0) {
    return (
      <p style={{ opacity: 0.7, fontStyle: "italic" }}>
        No detailed HR data available
      </p>
    );
  }

  const chartData = {
    labels: data.map((d) => d.x),
    datasets: [
      {
        label: "Heart Rate",
        data: data.map((d) => d.hr),
        borderColor: "#a78bfa",
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0,
        fill: true,
        backgroundColor: "rgba(167, 139, 250, 0.1)",
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
        ticks: {
          color: "#94a3b8",
          autoSkip: true,
          maxTicksLimit: 12,
          callback: function (value) {
            if (value % 60 === 0) {
              return value / 60;
            }
            return "";
          },
        },
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
    <div style={{ height: "300px" }}>
      <Line data={chartData} options={options} />
    </div>
  );
}

export default HeartChartDetailed;