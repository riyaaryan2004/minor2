import { useEffect, useState } from "react";
import { getPredictions, getHRData, getHRMinute } from "../api/api";
import HeartChart from "./HeartChart";
import HeartChartDetailed from "./HeartChartDetailed";
import styles from "./Dashboard.module.css";

function Dashboard() {
  const [data, setData] = useState(null);
  const [hrData, setHrData] = useState([]);
  const [hrMinute, setHrMinute] = useState([]);   // 🔥 NEW
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);

    const res = await getPredictions();
    setData(res);

    const hr = await getHRData();
    setHrData(hr);

    const minute = await getHRMinute();   // 🔥 NEW
    setHrMinute(minute);

    setLoading(false);
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) return <p style={{ padding: "30px" }}>Loading data...</p>;
  if (!data) return <p style={{ padding: "30px" }}>Failed to load data</p>;

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Fitbit Dashboard</h1>

      {/* Metrics */}
      <div className={styles.grid}>
        <div className={styles.card}>
          <p>Stress</p>
          <div className={styles.value}>{data.stress}</div>
        </div>

        <div className={styles.card}>
          <p>Sleep</p>
          <div className={styles.value}>{data.sleep} hrs</div>
        </div>

        <div className={styles.card}>
          <p>Productivity</p>
          <div className={styles.value}>{data.productivity}</div>
        </div>

        <div className={styles.card}>
          <p>Mood</p>
          <div className={styles.value}>{data.mood}</div>
        </div>
      </div>

      {/* Graph Section */}
      <div className={styles.graphContainer}>
        <h2>Heart Rate (Summary)</h2>
        <HeartChart data={hrData} />   {/* smooth hourly */}
      </div>

      {/* 🔥 NEW Detailed Graph */}
      <div className={styles.graphContainer}>
        <h2>Heart Rate (Detailed)</h2>
        <HeartChartDetailed data={hrMinute} />
      </div>

      <button className={styles.button} onClick={fetchData}>
        Refresh
      </button>
    </div>
  );
}

export default Dashboard;