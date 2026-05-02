import styles from "./About.module.css";

const metrics = [
  { value: "6", label: "Daily signals" },
  { value: "24h", label: "Health timeline" },
  { value: "ML", label: "Mood insights" },
];

const trackedSignals = [
  { title: "Heart Rate", detail: "Resting trends, active spikes, and daily rhythm." },
  { title: "Sleep Quality", detail: "Recovery context for energy and focus." },
  { title: "Activity Load", detail: "Movement patterns that shape the day." },
  { title: "Stress Signals", detail: "Pressure cues surfaced before they pile up." },
  { title: "Mood Prediction", detail: "A simple emotional read from body data." },
  { title: "Productivity Fit", detail: "A practical estimate for planning work." },
];

const workflow = [
  "Fitbit sync",
  "CSV health store",
  "ML prediction",
  "Smart dashboard",
];

function About() {
  return (
    <div className={styles.wrapper}>
      <section className={styles.hero}>
        <div className={styles.heroContent}>
          <p className={styles.kicker}>System overview</p>
          <h1>FitIntel turns body signals into daily clarity.</h1>
          <p>
            A premium health intelligence dashboard that studies Fitbit data, predicts
            mood and productivity, and presents your day in a calm, decision-ready view.
          </p>

          <div className={styles.metricRow}>
            {metrics.map((metric) => (
              <div key={metric.label} className={styles.metric}>
                <strong>{metric.value}</strong>
                <span>{metric.label}</span>
              </div>
            ))}
          </div>
        </div>

        <div className={styles.signalPanel} aria-label="FitIntel health signal preview">
          <div className={styles.panelHeader}>
            <span>Live Readiness</span>
            <strong>86%</strong>
          </div>
          <div className={styles.waveGrid}>
            <span style={{ height: "42%" }} />
            <span style={{ height: "70%" }} />
            <span style={{ height: "55%" }} />
            <span style={{ height: "88%" }} />
            <span style={{ height: "64%" }} />
            <span style={{ height: "76%" }} />
            <span style={{ height: "48%" }} />
            <span style={{ height: "82%" }} />
          </div>
          <div className={styles.panelFooter}>
            <span>Mood stable</span>
            <span>Focus rising</span>
          </div>
        </div>
      </section>

      <section className={styles.storyGrid}>
        <div className={styles.storyCard}>
          <p className={styles.kicker}>What it does</p>
          <h2>Your health data, translated.</h2>
          <p>
            FitIntel connects raw wearable data to everyday choices: when to push, when
            to recover, and what kind of recommendations match your current state.
          </p>
        </div>

        <div className={styles.storyCard}>
          <p className={styles.kicker}>Why it matters</p>
          <h2>Less guessing, better timing.</h2>
          <p>
            Instead of showing isolated numbers, the app combines sleep, heart rate,
            activity, stress, mood, and productivity into a single operating picture.
          </p>
        </div>
      </section>

      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <div>
            <p className={styles.kicker}>Signal map</p>
            <h2>What FitIntel tracks</h2>
          </div>
          <span>Personal dashboard</span>
        </div>

        <div className={styles.signalGrid}>
          {trackedSignals.map((item) => (
            <article key={item.title} className={styles.signalCard}>
              <div className={styles.signalMark}>{item.title.slice(0, 2)}</div>
              <h3>{item.title}</h3>
              <p>{item.detail}</p>
            </article>
          ))}
        </div>
      </section>

      <section className={styles.process}>
        <div>
          <p className={styles.kicker}>How it works</p>
          <h2>From wearable data to useful recommendations.</h2>
        </div>

        <div className={styles.timeline}>
          {workflow.map((step, index) => (
            <div key={step} className={styles.timelineItem}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <strong>{step}</strong>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default About;
