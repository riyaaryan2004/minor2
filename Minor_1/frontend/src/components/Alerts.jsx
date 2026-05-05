import { useCallback, useEffect, useState } from "react";
import {
  acknowledgeHeartAlert,
  checkHeartAlert,
  getAlerts,
  getHeartAlertConfig,
  getHeartAlertStatus,
  getLatestHeartRate,
} from "../api/api";
import styles from "./Alerts.module.css";

const HEART_RATE_REFRESH_MS = 30000;
const ALERT_STATUS_REFRESH_MS = 5000;

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [heartState, setHeartState] = useState({
    heartRate: null,
    lowBpm: 50,
    highBpm: 120,
  });
  const [pendingAlert, setPendingAlert] = useState(null);
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [lastCheckedReading, setLastCheckedReading] = useState("");

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
        }));
      }
    };

    const fetchData = async () => {
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
        heartRate: latest?.hr ?? current.heartRate,
        readingTime: latest?.time ?? current.readingTime,
        readingDate: latest?.date ?? current.readingDate,
        source: latest?.source ?? current.source,
      }));

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
        if (status.status === "escalated") {
          setMessage("No acknowledgement was received within 1 minute. Emergency email has been sent.");
        }
      }
    }, ALERT_STATUS_REFRESH_MS);

    return () => clearInterval(intervalId);
  }, [pendingAlert?.id, pendingAlert?.status]);

  const runHeartAlertCheck = useCallback(async (heartRate) => {
    setSaving(true);
    const result = await checkHeartAlert({ heartRate: Number(heartRate) });

    if (result.error) {
      setMessage(result.message || "Alert check failed");
    } else if (result.status === "normal") {
      setPendingAlert(null);
      setMessage(`Current heart rate is normal. ${result.message}`);
    } else {
      setPendingAlert(result);
      setMessage("Abnormal heart rate detected. Tap I'm okay within 1 minute to stop the emergency email.");
    }

    setSaving(false);
  }, []);

  useEffect(() => {
    if (!heartState.heartRate || pendingAlert?.status === "pending" || saving) {
      return;
    }

    const readingKey = [
      heartState.readingDate || "",
      heartState.readingTime || "",
      heartState.heartRate,
      heartState.source || "",
    ].join("|");

    if (readingKey === lastCheckedReading) {
      return;
    }

    setLastCheckedReading(readingKey);
    runHeartAlertCheck(heartState.heartRate);
  }, [
    heartState.heartRate,
    heartState.readingDate,
    heartState.readingTime,
    heartState.source,
    lastCheckedReading,
    pendingAlert?.status,
    runHeartAlertCheck,
    saving,
  ]);

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

  return (
    <div className={styles.container}>
      <h2>Alerts</h2>
      <div className={styles.panel}>
        <p>Current HR: <strong>{heartState.heartRate ?? "--"} BPM</strong></p>
        <p>Normal range: <strong>{heartState.lowBpm}-{heartState.highBpm} BPM</strong></p>
        {pendingAlert?.status === "pending" && (
          <button type="button" onClick={handleAcknowledge} disabled={saving}>
            I'm okay
          </button>
        )}
        {saving && <p>Checking latest reading...</p>}
        {message && <p className={styles.message}>{message}</p>}
      </div>

      {alerts.length > 0 ? (
        alerts.map((a, i) => (
          <div key={i} className={styles.card}>
            {a}
          </div>
        ))
      ) : (
        <p>No alerts</p>
      )}
    </div>
  );
}

export default Alerts;
