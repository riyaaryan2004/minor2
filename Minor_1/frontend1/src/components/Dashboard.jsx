import { useCallback, useEffect, useState } from "react";
import { getPredictions, getHRData, getHRMinute, syncDay } from "../api/api";
import HeartChart from "./HeartChart";
import HeartChartDetailed from "./HeartChartDetailed";
import styles from "./Dashboard.module.css";
import Card from "./Card";

const formatValue = (value, suffix = "") => {
  if (value === undefined || value === null || value === "") {
    return "--";
  }

  return `${value}${suffix}`;
};

const getTodayDate = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");

  return `${year}-${month}-${day}`;
};

function Dashboard() {
  const [data, setData] = useState(null);
  const [hrData, setHrData] = useState([]);
  const [hrMinute, setHrMinute] = useState([]);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [syncError, setSyncError] = useState("");
  const [lastUpdated, setLastUpdated] = useState("");

  const [selectedDate, setSelectedDate] = useState(
    getTodayDate
  );

  const fetchData = useCallback(async (shouldSync = false) => {
    setSyncError("");

    if (shouldSync) {
      setSyncing(true);
      const syncResult = await syncDay(selectedDate);
      setSyncing(false);

      if (syncResult?.error) {
        setSyncError(syncResult.message);
      } else {
        setLastUpdated(new Date().toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        }));
      }
    }

    setLoading(true);
    const [prediction, hourly] = await Promise.all([
      getPredictions(selectedDate),
      getHRData(selectedDate),
    ]);

    setData(prediction);
    setHrData(hourly);
    setLoading(false);

    setDetailLoading(true);
    const minute = await getHRMinute(selectedDate);
    setHrMinute(minute);
    setDetailLoading(false);
  }, [selectedDate]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const dateActions = (
    <div className={styles.actions}>
      <label className={styles.dateControl}>
        <span>Date</span>
        <input
          type="date"
          value={selectedDate}
          onChange={(e) => setSelectedDate(e.target.value)}
        />
      </label>

      <button
        className={styles.button}
        onClick={() => fetchData(true)}
        disabled={syncing}
      >
        {syncing ? "Syncing..." : "Refresh Data"}
      </button>
    </div>
  );

  if (loading && !data) {
    return (
      <div className={styles.statePanel}>
        <span className={styles.pulseDot} />
        Loading health snapshot...
      </div>
    );
  }

  if (!data || data.error) {
    return (
      <div className={styles.container}>
        <div className={styles.statePanel}>
          No data available for this date.
        </div>
        {dateActions}
        {syncError && <div className={styles.errorPanel}>{syncError}</div>}
      </div>
    );
  }

  const metrics = [
    { label: "Stress", value: formatValue(data.stress), tone: "amber" },
    { label: "Sleep", value: formatValue(data.sleep, " hrs"), tone: "blue" },
    { label: "Productivity", value: formatValue(data.productivity), tone: "green" },
    { label: "Mood", value: formatValue(data.mood), tone: "pink" },
  ];

  return (
    <div className={styles.container}>
      <section className={styles.hero}>
        <div>
          <p className={styles.kicker}>Today&apos;s wellness command center</p>
          <h1 className={styles.title}>FitIntel Dashboard</h1>
          <p className={styles.subtitle}>
            Fitbit activity, sleep, stress, and heart-rate insights in one live view.
          </p>
        </div>

        <div className={styles.heroVisual} aria-hidden="true">
          <div className={styles.heartPulse} />
          <div className={styles.ecgLine}>
            <span />
          </div>
          <p>Live body signals</p>
        </div>

        {dateActions}
      </section>

      <div className={styles.statusBar}>
        <span className={styles.liveIndicator} />
        <span>{syncing ? "Updating Fitbit data" : "Dashboard data loaded"}</span>
        {lastUpdated && <span className={styles.muted}>Last sync {lastUpdated}</span>}
      </div>

      {syncError && <div className={styles.errorPanel}>{syncError}</div>}

      <section className={styles.metricGrid}>
        {metrics.map((metric) => (
          <Card key={metric.label}>
            <div className={`${styles.metricCard} ${styles[metric.tone]}`}>
              <span className={styles.metricMarker} />
              <p className={styles.label}>{metric.label}</p>
              <div className={styles.value}>{metric.value}</div>
            </div>
          </Card>
        ))}
      </section>

      <section className={styles.chartGrid}>
        <Card>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.panelEyebrow}>Hourly trend</p>
              <h2>Heart Rate Summary</h2>
            </div>
            <span className={styles.badge}>{hrData.length} points</span>
          </div>
          <HeartChart data={hrData} />
        </Card>

        <Card>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.panelEyebrow}>Minute-level trace</p>
              <h2>Detailed Heart Rate</h2>
            </div>
            <span className={styles.badge}>
              {detailLoading ? "Loading" : `${hrMinute.length} points`}
            </span>
          </div>
          {detailLoading ? (
            <div className={styles.chartLoading}>Loading detailed heart-rate data...</div>
          ) : (
            <HeartChartDetailed data={hrMinute} />
          )}
        </Card>
      </section>
    </div>
  );
}

export default Dashboard;