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
import Card from "./Card";

const HEART_RATE_REFRESH_MS = 30000;
const ALERT_STATUS_REFRESH_MS = 5000;

const formatCountdown = (seconds) => {
  const safeSeconds = Math.max(0, seconds);
  const minutes = Math.floor(safeSeconds / 60);
  const remainingSeconds = safeSeconds % 60;

  return `${minutes}:${String(remainingSeconds).padStart(2, "0")}`;
};

const getAlertSecondsLeft = (alert, nowMs) => {
  if (!alert?.createdAt) {
    return 60;
  }

  const createdAtMs = new Date(alert.createdAt).getTime();
  if (Number.isNaN(createdAtMs)) {
    return 60;
  }

  const escalationSeconds = Math.max(Number(alert.escalationMinutes || 1), 1) * 60;
  const elapsedSeconds = Math.floor((nowMs - createdAtMs) / 1000);

  return Math.max(escalationSeconds - elapsedSeconds, 0);
};

const getEscalationMessage = (alert) => {
  if (alert?.emergencyEmailResult?.sent) {
    return "No acknowledgement was received within 1 minute. Emergency email has been sent.";
  }

  const reason = alert?.emergencyEmailResult?.reason;
  if (reason) {
    return `No acknowledgement was received within 1 minute. Emergency email was attempted but not sent: ${reason}`;
  }

  return "No acknowledgement was received within 1 minute. Emergency email is being processed.";
};

const getSourceLabel = (source) => {
  if (source === "fitbit-live") {
    return "Live";
  }

  if (source === "saved-hourly") {
    return "Saved";
  }

  return "--";
};

const getLiveSourceMessage = (liveError) => {
  if (liveError === "expired_token") {
    return "Fitbit login expired. Using saved HR data.";
  }

  if (liveError === "no_live_points") {
    return "No live Fitbit points found yet. Using saved HR data.";
  }

  if (liveError === "fitbit_connection_error") {
    return "Could not reach Fitbit. Using saved HR data.";
  }

  if (liveError) {
    return "Fitbit live HR is unavailable. Using saved HR data.";
  }

  return "";
};

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
  const [messageTone, setMessageTone] = useState("safeMessage");
  const [lastCheckedReading, setLastCheckedReading] = useState("");
  const [nowMs, setNowMs] = useState(Date.now());

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
          liveError: latest.liveError,
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
        liveError: latest?.liveError ?? current.liveError,
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
        if (status.status === "escalated") {
          setMessageTone("dangerMessage");
          setMessage(getEscalationMessage(status));
        }
      } else {
        setPendingAlert(null);
        setMessageTone("dangerMessage");
        setMessage("This alert is no longer active on the backend. The backend may have restarted; checking the latest heart rate again.");
      }
    }, ALERT_STATUS_REFRESH_MS);

    return () => clearInterval(intervalId);
  }, [pendingAlert?.id, pendingAlert?.status]);

  useEffect(() => {
    if (pendingAlert?.status !== "pending") {
      return undefined;
    }

    setNowMs(Date.now());
    const intervalId = setInterval(() => setNowMs(Date.now()), 1000);

    return () => clearInterval(intervalId);
  }, [pendingAlert?.status]);

  const runHeartAlertCheck = useCallback(async (heartRate, silent = false) => {
    setSaving(true);
    if (!silent) {
      setMessage("");
    }

    const result = await checkHeartAlert({
      heartRate: Number(heartRate),
    });

    if (result.error) {
      setMessageTone("dangerMessage");
      setMessage(result.message || "Alert check failed");
    } else if (result.status === "normal") {
      setPendingAlert(null);
      setMessageTone("safeMessage");
      setMessage(`Current heart rate is normal. ${result.message}`);
    } else {
      setPendingAlert(result);
      setMessageTone("dangerMessage");
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
    runHeartAlertCheck(heartState.heartRate, true);
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
      setMessageTone("dangerMessage");
      setMessage(result.message || "Could not acknowledge alert");
    } else {
      setPendingAlert(result);
      setMessageTone("safeMessage");
      setMessage("Alert acknowledged. Emergency email has been stopped.");
    }
    setSaving(false);
  };

  const emailNote = (result) => {
    if (!result) {
      return null;
    }
    return result.sent ? "Email sent" : `Not sent: ${result.reason}`;
  };

  const secondsLeft = getAlertSecondsLeft(pendingAlert, nowMs);

  return (
    <div className={styles.wrapper}>
      <section className={styles.header}>
        <p className={styles.kicker}>Heart-rate safety</p>
        <h1>Heart Rate Alerts</h1>
        <p>Checks the latest heart-rate reading and alerts the emergency contact if there is no response.</p>
      </section>

      <Card>
        <div className={styles.alertPanel}>
          <div className={styles.formHeader}>
            <div>
              <p className={styles.kicker}>Emergency escalation</p>
              <h2>Automatic heart-rate check</h2>
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
              <strong>{getSourceLabel(heartState.source)}</strong>
            </div>
            <div>
              <span>Safe range</span>
              <strong>{heartState.lowBpm}-{heartState.highBpm}</strong>
            </div>
            <div>
              <span>Emergency delay</span>
              <strong>1 min</strong>
            </div>
          </div>
          {heartState.source === "saved-hourly" && heartState.liveError && (
            <div className={styles.sourceWarning}>
              <span>{getLiveSourceMessage(heartState.liveError)}</span>
              {heartState.liveError === "expired_token" && (
                <a href="http://127.0.0.1:5000/login">Reconnect Fitbit</a>
              )}
            </div>
          )}

          <div className={styles.actions}>
            {pendingAlert?.status === "pending" && (
              <>
                <button
                  type="button"
                  className={styles.secondaryButton}
                  onClick={handleAcknowledge}
                  disabled={saving}
                >
                  I'm okay
                </button>
                <span className={styles.timerBadge}>
                  {formatCountdown(secondsLeft)}
                </span>
              </>
            )}
            {saving && <span className={styles.checkingText}>Checking latest reading...</span>}
          </div>

          {message && (
            <p className={`${styles.message} ${styles[messageTone] || styles.safeMessage}`}>
              {message}
            </p>
          )}
          {pendingAlert && (
            <div className={styles.summary}>
              <p><strong>{pendingAlert.heartRate} BPM</strong> is {pendingAlert.kind} for the {pendingAlert.lowBpm}-{pendingAlert.highBpm} BPM range.</p>
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
                  className={`${styles.alert} ${isNormal ? styles.normal : styles.dangerAlert}`}
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
