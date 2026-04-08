import { useEffect, useState } from "react";
import { getAlerts } from "../api/api";
import styles from "./Alerts.module.css";

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
    <div className={styles.container}>
      <h2>Alerts</h2>

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