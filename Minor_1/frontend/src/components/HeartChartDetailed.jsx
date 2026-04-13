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
    return <p>No detailed HR data available</p>;
  }

  const chartData = {
    // KEEP raw minute labels (0–1440)
    labels: data.map((d) => d.x),

    datasets: [
      {
        label: "Heart Rate (Minute-Level)",
        data: data.map((d) => d.hr),
        borderColor: "#38bdf8",
        borderWidth: 1,
        pointRadius: 0,
        tension: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,

    scales: {
      x: {
        ticks: {
          color: "white",
          autoSkip : false, // 🔥 clean axis

          callback: function (value) {
            // show only hour labels
            if (value % 60 === 0) {
              return value / 60; // convert minute → hour
            }
            return "";
          },
        },
      },

      y: {
        ticks: { color: "white" },
        min: 40,
        max: 160,
      },
    },

    plugins: {
      legend: {
        labels: { color: "white" },
      },
    },
  };

  return (
    <div style={{ height: "300px", marginTop: "20px" }}>
      <h2 style={{ color: "white" }}>Detailed Heart Rate</h2>
      <Line data={chartData} options={options} />
    </div>
  );
}

export default HeartChartDetailed;