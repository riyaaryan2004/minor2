import { useEffect, useState } from "react";
import {
  acknowledgeHeartAlert,
  checkHeartAlert,
  getAlerts,
  getHeartAlertConfig,
  getHeartAlertStatus,
  getLatestHeartRate,
} from "../api/api";
import styles from "./Alerts.module.css";
import Card from "./Card";

const HEART_RATE_REFRESH_MS = 30000;

const formatReadingTime = (time) => {
  if (!time) {
    return "--";
  }

  const [hourText, minuteText = "00"] = String(time).split(":");
  const hour = Number(hourText);

  if (Number.isNaN(hour)) {
    return time;
  }

  const period = hour >= 12 ? "PM" : "AM";
  const hour12 = hour % 12 || 12;

  return `${hour12}:${minuteText.padStart(2, "0")} ${period}`;
};

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [heartState, setHeartState] = useState({
    heartRate: null,
    lowBpm: 50,
    highBpm: 120,
    escalationMinutes: 3,
  });
  const [pendingAlert, setPendingAlert] = useState(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let intervalId;

    const fetchLatestHeartRate = async () => {
      const latest = await getLatestHeartRate();
      if (latest?.hr) {
        setHeartState((current) => ({
          ...current,
          heartRate: latest.hr,
          readingTime: latest.time,
          readingDate: latest.date,
          source: latest.source,
          checkedAt: latest.checkedAt,
        }));
      }
    };

    const fetchData = async () => {
      setLoading(true);
      const [data, config, latest] = await Promise.all([
        getAlerts(),
        getHeartAlertConfig(),
        getLatestHeartRate(),
      ]);
      setAlerts(data?.alerts || []);
      setHeartState((current) => ({
        ...current,
        lowBpm: config?.lowBpm ?? current.lowBpm,
        highBpm: config?.highBpm ?? current.highBpm,
        escalationMinutes: config?.escalationMinutes ?? current.escalationMinutes,
        heartRate: latest?.hr ?? current.heartRate,
        readingTime: latest?.time ?? current.readingTime,
        readingDate: latest?.date ?? current.readingDate,
        source: latest?.source ?? current.source,
        checkedAt: latest?.checkedAt ?? current.checkedAt,
      }));
      setLoading(false);

      intervalId = setInterval(fetchLatestHeartRate, HEART_RATE_REFRESH_MS);
    };

    fetchData();

    return () => clearInterval(intervalId);
  }, []);

  useEffect(() => {
    if (!pendingAlert?.id || pendingAlert.status !== "pending") {
      return undefined;
    }

    const intervalId = setInterval(async () => {
      const status = await getHeartAlertStatus(pendingAlert.id);
      if (status) {
        setPendingAlert(status);
      }
    }, 15000);

    return () => clearInterval(intervalId);
  }, [pendingAlert?.id, pendingAlert?.status]);

  const handleCheck = async () => {
    if (!heartState.heartRate) {
      setMessage("No live heart-rate reading found.");
      return;
    }

    setSaving(true);
    setMessage("");

    const result = await checkHeartAlert({
      heartRate: Number(heartState.heartRate),
    });

    if (result.error) {
      setMessage(result.message || "Alert check failed");
    } else if (result.status === "normal") {
      setPendingAlert(null);
      setMessage(result.message);
    } else {
      setPendingAlert(result);
      setMessage("Self email step started. Acknowledge within the window to stop emergency email.");
    }

    setSaving(false);
  };

  const handleAcknowledge = async () => {
    if (!pendingAlert?.id) {
      return;
    }

    setSaving(true);
    const result = await acknowledgeHeartAlert(pendingAlert.id);
    if (result.error) {
      setMessage(result.message || "Could not acknowledge alert");
    } else {
      setPendingAlert(result);
      setMessage("Alert acknowledged. Emergency email has been stopped.");
    }
    setSaving(false);
  };

  const emailNote = (result) => {
    if (!result) {
      return null;
    }
    return result.sent ? "Email sent" : result.reason;
  };

  return (
    <div className={styles.wrapper}>
      <section className={styles.header}>
        <p className={styles.kicker}>Heart-rate safety</p>
        <h1>Heart Rate Alerts</h1>
        <p>Checks the latest heart-rate reading and uses saved contacts for self and emergency emails.</p>
      </section>

      <Card>
        <div className={styles.alertPanel}>
          <div className={styles.formHeader}>
            <div>
              <p className={styles.kicker}>Saved email escalation</p>
              <h2>Heart-rate check</h2>
            </div>
            {pendingAlert?.status && (
              <span className={`${styles.statusBadge} ${styles[pendingAlert.status] || ""}`}>
                {pendingAlert.status}
              </span>
            )}
          </div>

          <div className={styles.quickStats}>
            <div>
              <span>Current BPM</span>
              <strong className={styles.bpmValue}>
                <span className={styles.beatingHeart} aria-hidden="true" />
                {heartState.heartRate ?? "--"}
              </strong>
            </div>
            <div>
              <span>Reading time</span>
              <strong>{formatReadingTime(heartState.readingTime)}</strong>
            </div>
            <div>
              <span>Last checked</span>
              <strong>{formatReadingTime(heartState.checkedAt)}</strong>
            </div>
            <div>
              <span>Source</span>
              <strong>{heartState.source === "fitbit-live" ? "Live" : "Saved"}</strong>
            </div>
            <div>
              <span>Safe range</span>
              <strong>{heartState.lowBpm}-{heartState.highBpm}</strong>
            </div>
            <div>
              <span>Emergency delay</span>
              <strong>{heartState.escalationMinutes} min</strong>
            </div>
          </div>

          <div className={styles.actions}>
            <button type="button" onClick={handleCheck} disabled={saving || !heartState.heartRate}>
              {saving ? "Checking..." : "Check heart rate"}
            </button>
            <button
              type="button"
              className={styles.secondaryButton}
              onClick={handleAcknowledge}
              disabled={saving || !pendingAlert?.id || pendingAlert.status !== "pending"}
            >
              I'm okay
            </button>
          </div>

          {message && <p className={styles.message}>{message}</p>}
          {pendingAlert && (
            <div className={styles.summary}>
              <p><strong>{pendingAlert.heartRate} BPM</strong> is {pendingAlert.kind} for the {pendingAlert.lowBpm}-{pendingAlert.highBpm} BPM range.</p>
              <p>Self mail: {emailNote(pendingAlert.selfEmailResult)}</p>
              {pendingAlert.emergencyEmailResult && <p>Emergency mail: {emailNote(pendingAlert.emergencyEmailResult)}</p>}
            </div>
          )}
        </div>
      </Card>

      <Card>
        <div className={styles.container}>
          {loading ? (
            <p className={styles.empty}>Checking alerts...</p>
          ) : alerts.length > 0 ? (
            alerts.map((alert, index) => {
              const isNormal = alert.toLowerCase().includes("normal");

              return (
                <div
                  key={index}
                  className={`${styles.alert} ${isNormal ? styles.normal : styles.danger}`}
                >
                  <span className={styles.icon}>{isNormal ? "OK" : "!"}</span>
                  <div>
                    <strong>{isNormal ? "Normal range" : "Attention needed"}</strong>
                    <p>{alert}</p>
                  </div>
                </div>
              );
            })
          ) : (
            <p className={styles.empty}>No alerts</p>
          )}
        </div>
      </Card>
    </div>
  );
}

export default Alerts;