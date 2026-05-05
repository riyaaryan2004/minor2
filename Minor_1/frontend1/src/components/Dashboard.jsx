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

const getMetricDetail = (label, value) => {
  if (value === undefined || value === null || value === "") {
    return "No value is available for the selected date.";
  }

  const numericValue = Number(value);

  if (label === "Stress") {
    if (numericValue > 0.18) return "High stress signal. Take lighter work and use short breaks.";
    if (numericValue > 0.15) return "Moderate stress signal. Keep tasks focused and avoid overload.";
    return "Low stress signal. Your heart-rate variability looks stable.";
  }

  if (label === "Sleep") {
    if (numericValue < 5) return "Low recovery. The day may need lighter work and rest.";
    if (numericValue < 6) return "Manageable sleep, but consistency can improve energy.";
    return "Good sleep duration for daily recovery.";
  }

  if (label === "Steps") {
    if (numericValue < 3000) return "Low movement today. A short walk can help energy and focus.";
    if (numericValue < 7000) return "Moderate activity. Movement is present but can still improve.";
    return "Strong activity level. This usually supports better energy.";
  }

  if (label === "Productivity") {
    if (numericValue < 4) return "Low predicted productivity. Start with small, simple tasks.";
    if (numericValue < 7) return "Balanced productivity. Prioritize important work with breaks.";
    return "High productivity prediction. Good time for deeper work.";
  }

  if (label === "Mood") {
    if (numericValue < 4) return "Low mood prediction. Choose lighter tasks and recovery actions.";
    if (numericValue < 7) return "Neutral to stable mood. Keep the day balanced.";
    return "Positive mood prediction. Good state for focused plans.";
  }

  return "This metric is calculated from the selected day's health data.";
};

const MetricIcon = ({ name, className }) => {
  const icons = {
    stress: (
      <>
        <path d="M4 13h4l2-5 4 10 2-5h4" />
        <path d="M6 5.5A7 7 0 0 1 18 7" />
      </>
    ),
    sleep: (
      <>
        <path d="M17.5 14.5A7.5 7.5 0 0 1 9.5 4a6 6 0 1 0 8 10.5Z" />
        <path d="M15 4h4l-4 4h4" />
      </>
    ),
    steps: (
      <>
        <path d="M8.5 13.5c-1.7 0-3 1.2-3 2.8 0 1.8 1.3 3.2 3 3.2 1.9 0 3-1.5 3-3.2 0-1.6-1.1-2.8-3-2.8Z" />
        <path d="M15.5 4.5c-1.9 0-3 1.4-3 3.1 0 1.6 1.1 2.9 3 2.9 1.7 0 3-1.2 3-2.9 0-1.7-1.3-3.1-3-3.1Z" />
        <path d="M6 11l2-3" />
        <path d="M16 13l2 3" />
      </>
    ),
    productivity: (
      <>
        <path d="M4 18h16" />
        <path d="M6 15l4-4 3 3 5-7" />
        <path d="M15 7h3v3" />
      </>
    ),
    mood: (
      <>
        <circle cx="12" cy="12" r="8" />
        <path d="M9 10h.01" />
        <path d="M15 10h.01" />
        <path d="M8.5 14.5c1.8 2 5.2 2 7 0" />
      </>
    ),
  };

  return (
    <span className={className} aria-hidden="true">
      <svg viewBox="0 0 24 24" focusable="false">
        {icons[name]}
      </svg>
    </span>
  );
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
  const [showHourlyExplanation, setShowHourlyExplanation] = useState(false);
  const [showDetailedExplanation, setShowDetailedExplanation] = useState(false);
  const [showMetricExplanation, setShowMetricExplanation] = useState(false);

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
    { label: "Stress", rawValue: data.stress, value: formatValue(data.stress), tone: "red", icon: "stress" },
    { label: "Sleep", rawValue: data.sleep, value: formatValue(data.sleep, " hrs"), tone: "blue", icon: "sleep" },
    { label: "Steps", rawValue: data.steps ?? data.total_steps, value: formatValue(data.steps ?? data.total_steps), tone: "teal", icon: "steps" },
    { label: "Productivity", rawValue: data.productivity, value: formatValue(data.productivity), tone: "green", icon: "productivity" },
    { label: "Mood", rawValue: data.mood, value: formatValue(data.mood), tone: "pink", icon: "mood" },
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
              <div className={styles.metricTop}>
                <MetricIcon
                  name={metric.icon}
                  className={styles.metricIcon}
                />
                <span className={styles.metricMarker} />
              </div>
              <p className={styles.label}>{metric.label}</p>
              <div className={styles.value}>{metric.value}</div>
            </div>
          </Card>
        ))}
      </section>

      <div className={styles.metricExplainBar}>
        <button
          type="button"
          className={styles.explainButton}
          onClick={() => setShowMetricExplanation((show) => !show)}
          aria-expanded={showMetricExplanation}
        >
          {showMetricExplanation ? "Hide Metric Insights" : "Explain Metrics"}
        </button>
      </div>

      {showMetricExplanation && (
        <section className={styles.metricExplanationGrid}>
          {metrics.map((metric) => (
            <div key={metric.label}>
              <span>{metric.label}</span>
              <p>{getMetricDetail(metric.label, metric.rawValue)}</p>
            </div>
          ))}
        </section>
      )}

      <section className={styles.chartGrid}>
        <Card>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.panelEyebrow}>Hourly trend</p>
              <h2>Heart Rate Summary</h2>
            </div>
            <div className={styles.panelActions}>
              <button
                type="button"
                className={styles.explainButton}
                onClick={() => setShowHourlyExplanation((show) => !show)}
                aria-expanded={showHourlyExplanation}
              >
                {showHourlyExplanation ? "Hide" : "Explain"}
              </button>
              <span className={styles.badge}>{hrData.length} points</span>
            </div>
          </div>
          <HeartChart data={hrData} />
          {showHourlyExplanation && (
            <div className={styles.chartNotes}>
              <div>
                <span>Rhythm</span>
                Shows how your heart rate rises and settles through the day.
              </div>
              <div>
                <span>Spikes</span>
                Sharp climbs can point to activity, stress, caffeine, or sudden movement.
              </div>
              <div>
                <span>Recovery</span>
                Lower, steadier stretches usually suggest calmer periods or better rest.
              </div>
            </div>
          )}
        </Card>

        <Card>
          <div className={styles.panelHeader}>
            <div>
              <p className={styles.panelEyebrow}>Minute-level trace</p>
              <h2>Detailed Heart Rate</h2>
            </div>
            <div className={styles.panelActions}>
              <button
                type="button"
                className={styles.explainButton}
                onClick={() => setShowDetailedExplanation((show) => !show)}
                aria-expanded={showDetailedExplanation}
              >
                {showDetailedExplanation ? "Hide" : "Explain"}
              </button>
              <span className={styles.badge}>
                {detailLoading ? "Loading" : `${hrMinute.length} points`}
              </span>
            </div>
          </div>
          {detailLoading ? (
            <div className={styles.chartLoading}>Loading detailed heart-rate data...</div>
          ) : (
            <>
              <HeartChartDetailed data={hrMinute} />
              {showDetailedExplanation && (
                <div className={styles.chartNotes}>
                  <div>
                    <span>Minute pulse</span>
                    Shows the small heart-rate changes that hourly averages can smooth out.
                  </div>
                  <div>
                    <span>Hidden load</span>
                    Repeated tiny rises may reveal stress, movement, or recovery pressure.
                  </div>
                  <div>
                    <span>Quiet zones</span>
                    Flat, lower stretches usually mark calmer periods with steadier recovery.
                  </div>
                </div>
              )}
            </>
          )}
        </Card>
      </section>
    </div>
  );
}

export default Dashboard;
