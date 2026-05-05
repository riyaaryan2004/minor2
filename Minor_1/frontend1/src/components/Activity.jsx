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

  if (!data) {
    return (
      <div className={styles.loadingState}>
        <span className={styles.pulseDot} />
        Reading activity intelligence...
      </div>
    );
  }

  const suggestions = data.suggestions || [];
  const historyInsights = data.history_insights || [];
  const visibleHistory = historyInsights.slice(0, 3);

  return (
    <div className={styles.wrapper}>

      <section className={styles.header}>
        <div>
          <p className={styles.kicker}>Activity intelligence</p>
          <div className={styles.dayType}>
            <span className={styles.dot}></span>
            {data.day_type}
          </div>

          <p className={styles.text}>
            <strong>Root Cause:</strong> {data.root_cause}
          </p>
        </div>

        <div className={styles.signalPanel} aria-hidden="true">
          <span style={{ height: "42%" }} />
          <span style={{ height: "70%" }} />
          <span style={{ height: "54%" }} />
          <span style={{ height: "86%" }} />
          <span style={{ height: "62%" }} />
          <span style={{ height: "76%" }} />
        </div>
      </section>

      <section className={styles.mainGrid}>
        <Card>
          <div className={styles.section}>
            <div className={styles.sectionHeader}>
              <div>
                <p className={styles.kicker}>Priority recommendation</p>
                <div className={styles.title}>Primary Action</div>
              </div>
              <span>Now</span>
            </div>
            <p className={styles.text}>{data.primary_action}</p>
          </div>
        </Card>

        <Card>
          <div className={styles.goal}>
            <div className={styles.sectionHeader}>
              <div>
                <p className={styles.kicker}>Outcome target</p>
                <div className={styles.title}>Daily Goal</div>
              </div>
              <span>Goal</span>
            </div>
            <p>{data.daily_goal}</p>
          </div>
        </Card>
      </section>

      <Card>
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <div>
              <p className={styles.kicker}>Execution plan</p>
              <div className={styles.title}>Supporting Actions</div>
            </div>
            <span>{suggestions.length} items</span>
          </div>
          <div className={styles.cardList}>
            {suggestions.length > 0 ? suggestions.map((s, i) => (
              <div key={i} className={styles.cardItem}>
                <span>{String(i + 1).padStart(2, "0")}</span>
                {s}
              </div>
            )) : (
              <p className={styles.empty}>No supporting actions available.</p>
            )}
          </div>
        </div>
      </Card>

      <Card>
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <div>
              <p className={styles.kicker}>Pattern analysis</p>
              <div className={styles.title}>History Insights</div>
            </div>
            <span>Recent</span>
          </div>
          <div className={styles.cardList}>
            {visibleHistory.length > 0 ? visibleHistory.map((h, i) => (
              <div key={i} className={styles.cardItem}>
                <span>H{i + 1}</span>
                {h}
              </div>
            )) : (
              <p className={styles.empty}>No history insights available yet.</p>
            )}
          </div>
        </div>
      </Card>
    </div>
  );
}

export default Activity;
