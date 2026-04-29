import { useEffect, useState } from "react";
import { getAlerts } from "../api/api";
import styles from "./Alerts.module.css";
import Card from "./Card";

function Alerts() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getAlerts();
      setAlerts(data?.alerts || []);
    };

    fetchData();
  }, []);

  return (
    <Card>
      <div className={styles.container}>
        <h2 className={styles.heading}>🚨 Alerts</h2>

        {alerts.length > 0 ? (
          alerts.map((a, i) => {
            // 🔥 safety (no logic change)
            if (!a || typeof a !== "object") {
              return (
                <div key={i} className={styles.alert}>
                  <span>{a}</span>
                </div>
              );
            }

            const isNormal = a.issue === "Normal";

            return (
              <div
                key={i}
                className={`${styles.alert} ${
                  isNormal ? styles.normal : styles.danger
                }`}
              >
                <span className={styles.icon}>
                  {isNormal ? "✅" : "⚠️"}
                </span>

                <div>
                  <strong>{a.issue}</strong>
                  <p>{a.why}</p>
                  <p style={{ opacity: 0.7 }}>{a.action}</p>
                </div>
              </div>
            );
          })
        ) : (
          <p className={styles.empty}>No alerts</p>
        )}
      </div>
    </Card>
  );
}

export default Alerts;