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
    return <p>No heart rate data available</p>;
  }

  // Fill missing hours (0–23)
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
        tension: 0.4, // smooth curve
        spanGaps: true, // connect missing points
        fill: false,

        borderColor: "#5fa077",        
        backgroundColor: "#22c55e",
        pointRadius: 2,
        pointBackgroundColor: "#77be91",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false, 
    plugins: {
      legend: {
        labels: {
          color: "white",
        },
      },
    },
    scales: {
      x: {
        ticks: { color: "white" },
      },
      y: {
        ticks: { color: "white" },
        min: 40,
        max: 160,
      },
    },
  };

  return (
    <div
      style={{
        marginTop: "30px",
        background: "#0f172a",
        padding: "20px",
        borderRadius: "16px",
        height: "350px",
      }}
    >
      <h2 style={{ color: "white" }}>Heart Rate (Latest Data)</h2>
      <Line data={chartData} options={options} />
    </div>
  );
}

export default HeartChart;