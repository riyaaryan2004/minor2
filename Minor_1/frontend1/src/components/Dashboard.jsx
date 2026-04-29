import { useEffect, useState } from "react";
import { getPredictions, getHRData, getHRMinute } from "../api/api";
import HeartChart from "./HeartChart";
import HeartChartDetailed from "./HeartChartDetailed";
import styles from "./Dashboard.module.css";
import Card from "./Card";

function Dashboard({ demoData })  {
  const [data, setData] = useState(null);
  const [hrData, setHrData] = useState([]);
  const [hrMinute, setHrMinute] = useState([]);
  const [loading, setLoading] = useState(!demoData);

  const fetchData = async () => {
    setLoading(true);

    const res = await getPredictions();
    setData(res);

    const hr = await getHRData();
    setHrData(hr);

    const minute = await getHRMinute();
    setHrMinute(minute);

    setLoading(false);
  };

  useEffect(() => {
    if (demoData) {
      setData(demoData);
      setLoading(false);
    } else {
      fetchData();
    }
  }, [demoData]);

  if (loading) return <p className={styles.loading}>Loading data...</p>;
  if (!data) return <p className={styles.loading}>Failed to load data</p>;

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>FitIntel Dashboard</h1>

      {/* Metrics */}
      <div className={styles.grid}>
        <Card>
          <p className={styles.label}>Stress</p>
          <div className={styles.value}>
            {data.metrics?.stress ?? data.stress}
          </div>
        </Card>

        <Card>
          <p className={styles.label}>Sleep</p>
          <div className={styles.value}>
            {data.metrics?.sleep ?? data.sleep} hrs
          </div>
        </Card>

        <Card>
          <p className={styles.label}>Productivity</p>
          <div className={styles.value}>{data.productivity}</div>
        </Card>

        <Card>
          <p className={styles.label}>Mood</p>
          <div className={styles.value}>{data.mood}</div>
        </Card>
      </div>

      {/* Graph Section */}
      <Card>
        <div className={styles.graphContainer}>
          <h2>📊 Heart Rate (Summary)</h2>
          <HeartChart data={hrData} />
        </div>
      </Card>

      {/* Detailed Graph */}
      <Card>
        <div className={styles.graphContainer}>
          <h2>📈 Heart Rate (Detailed)</h2>
          <HeartChartDetailed data={hrMinute} />
        </div>
      </Card>

      <button className={styles.button} onClick={fetchData}>
        🔄 Refresh Data
      </button>
    </div>
  );
}

export default Dashboard;