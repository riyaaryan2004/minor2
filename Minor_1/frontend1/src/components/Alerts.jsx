import { useEffect, useState } from "react";
import { getAlerts } from "../api/api";
import styles from "./Alerts.module.css";
import Card from "./Card";

function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const data = await getAlerts();
      setAlerts(data?.alerts || []);
      setLoading(false);
    };

    fetchData();
  }, []);

  return (
    <div className={styles.wrapper}>
      <section className={styles.header}>
        <p className={styles.kicker}>Risk monitor</p>
        <h1>Health Alerts</h1>
        <p>Latest anomaly checks based on resting heart rate, daily average, and variability.</p>
      </section>

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
