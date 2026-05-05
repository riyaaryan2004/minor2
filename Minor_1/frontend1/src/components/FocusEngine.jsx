import { useState } from "react";
import styles from "./FocusEngine.module.css";

const FocusEngine = () => {
  const [tasks, setTasks] = useState([]);
  const [taskName, setTaskName] = useState("");
  const [priority, setPriority] = useState(3);
  const [duration, setDuration] = useState(60);
  const [type, setType] = useState("medium");

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const addTask = () => {
    if (!taskName.trim()) return;

    setTasks([
      ...tasks,
      {
        task: taskName,
        priority: Number(priority),
        duration: Number(duration),
        type: type,
      },
    ]);

    setTaskName("");
  };

  const removeTask = (index) => {
    setTasks(tasks.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (tasks.length === 0) return;

    setLoading(true);

    try {
      const res = await fetch("http://localhost:5000/focus", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ tasks }),
      });

      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error(err);
    }

    setLoading(false);
  };

  return (
    <div className={styles.wrapper}>
      {/* HEADER */}
      <div className={styles.header}>
        <p className={styles.kicker}>Adaptive Focus Engine</p>
        <h1>Smart Task Recommendation</h1>
        <p>
          Add your tasks and let the system decide what you should do based on
          your current cognitive state.
        </p>
      </div>

      <div className={styles.columns}>
        {/* LEFT */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>➕ Add Tasks</h2>
            <span>{tasks.length} tasks</span>
          </div>

          <div className={styles.taskForm}>
            <input
              placeholder="Enter task"
              value={taskName}
              onChange={(e) => setTaskName(e.target.value)}
            />

            <div className={styles.taskRow}>
              <input
                className={styles.smallInput}
                type="number"
                min="1"
                max="5"
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
              />

              <input
                className={styles.smallInput}
                type="number"
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
              />

              <select
                className={styles.select}
                value={type}
                onChange={(e) => setType(e.target.value)}
              >
                <option value="deep">Deep</option>
                <option value="medium">Moderate</option>
                <option value="light">Light</option>
                <option value="passive">Passive</option>
              </select>

              <button className={styles.addBtn} onClick={addTask}>
                Add
              </button>
            </div>
          </div>

          {/* TASK LIST */}
          <div className={styles.activities}>
            {tasks.map((t, i) => (
              <div key={i} className={styles.activityCard}>
                <span>{i + 1}</span>
                <p>
                  <strong>{t.task}</strong>
                  <br />
                  Priority: {t.priority} | {t.duration} mins | {t.type}
                </p>
                <button onClick={() => removeTask(i)}>❌</button>
              </div>
            ))}
          </div>

          <button onClick={handleSubmit} disabled={loading}>
            {loading ? "Analyzing..." : "Get Recommendation"}
          </button>
        </div>

        {/* RIGHT */}
        <div className={styles.section}>
          <div className={styles.sectionHeader}>
            <h2>🎯 Recommendation</h2>
          </div>

          {!result ? (
            <p className={styles.empty}>
              Add tasks and click "Get Recommendation"
            </p>
          ) : (
            <>
              {/* MAIN TASK */}
              <div className={`${styles.activityCard} ${styles.resultHighlight}`}>
                <span>⚡</span>
                <p>
                  <strong>{result.task}</strong>
                  <br />
                  {result.reason}
                </p>
              </div>

              {/* SUCCESS PROBABILITY */}
              <div className={styles.activityCard}>
                <span>📊</span>
                <p>
                  <strong>Success Probability:</strong>{" "}
                  {result.success_probability ?? result.confidence}%
                </p>
              </div>

              {/* BURNOUT RISK */}
              <div className={styles.activityCard}>
                <span>🔥</span>
                <p>
                  <strong>Burnout Risk:</strong>{" "}
                  {result.burnout_risk || "N/A"}
                </p>
              </div>

              {/* CONFIDENCE */}
              <div className={styles.activityCard}>
                <span>📈</span>
                <p>
                  <strong>Confidence:</strong> {result.confidence}%
                </p>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default FocusEngine;