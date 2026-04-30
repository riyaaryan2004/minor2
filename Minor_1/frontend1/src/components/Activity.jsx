import { useEffect, useState } from "react";
import { getPredictions } from "../api/api";
import Card from "./Card";
import styles from "./Activity.module.css";

function Activity() {
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const res = await getPredictions();
      setData(res);
    };
    fetchData();
  }, []);

  if (!data) return <p>Loading...</p>;

  return (
    <div className={styles.wrapper}>
      
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.dayType}>
          <span className={styles.dot}></span>
          {data.day_type}
        </div>

        <p className={styles.text}>
          <strong>Root Cause:</strong> {data.root_cause}
        </p>
      </div>

      {/* Primary Action */}
      <Card>
        <div className={styles.section}>
          <div className={styles.title}>Primary Action</div>
          <p className={styles.text}>{data.primary_action}</p>
        </div>
      </Card>

      {/* Supporting Actions */}
      <Card>
        <div className={styles.section}>
          <div className={styles.title}>Supporting Actions</div>

          <div className={styles.cardList}>
            {data.suggestions?.map((s, i) => (
              <div key={i} className={styles.cardItem}>
                {s}
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* History */}
      <Card>
        <div className={styles.section}>
          <div className={styles.title}>History Insights</div>

          <div className={styles.cardList}>
            {data.history_insights?.slice(0, 2).map((h, i) => (
              <div key={i} className={styles.cardItem}>
                {h}
              </div>
            ))}
          </div>
        </div>
      </Card>

      {/* Goal */}
      <Card>
        <div className={styles.goal}>
          <div className={styles.title}>Daily Goal</div>
          {data.daily_goal}
        </div>
      </Card>

    </div>
  );
}

export default Activity;