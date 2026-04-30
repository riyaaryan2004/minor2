import Card from "./Card";

function About() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "18px" }}>
      <section
        style={{
          padding: "24px",
          borderRadius: "8px",
          border: "1px solid rgba(148, 163, 184, 0.18)",
          background:
            "linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(8, 145, 178, 0.25))",
        }}
      >
        <p
          style={{
            margin: "0 0 8px",
            color: "#67e8f9",
            fontSize: "12px",
            fontWeight: 800,
            textTransform: "uppercase",
          }}
        >
          System overview
        </p>
        <h1 style={{ fontSize: "34px", color: "#f8fafc" }}>About FitIntel</h1>
        <p
          style={{
            maxWidth: "760px",
            margin: "10px 0 0",
            color: "#cbd5e1",
            lineHeight: 1.65,
          }}
        >
          FitIntel analyzes Fitbit health data and turns heart rate, sleep, activity,
          stress, mood, and productivity signals into a daily operating dashboard.
        </p>
      </section>

      <Card>
        <h2 style={{ color: "#f8fafc", fontSize: "20px", marginBottom: "14px" }}>
          What It Tracks
        </h2>
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
            gap: "12px",
          }}
        >
          {[
            "Heart rate trends",
            "Sleep quality",
            "Activity load",
            "Stress signals",
            "Mood prediction",
            "Productivity prediction",
          ].map((item) => (
            <div
              key={item}
              style={{
                padding: "14px",
                borderRadius: "8px",
                background: "rgba(2, 6, 23, 0.35)",
                border: "1px solid rgba(148, 163, 184, 0.16)",
                color: "#e2e8f0",
                fontWeight: 700,
              }}
            >
              {item}
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <h2 style={{ color: "#f8fafc", fontSize: "20px", marginBottom: "10px" }}>
          How It Works
        </h2>
        <p style={{ margin: 0, color: "#cbd5e1", lineHeight: 1.7 }}>
          The backend syncs Fitbit data into CSV files, machine learning models generate
          mood and productivity estimates, and the frontend presents the latest health
          state with alerts, suggestions, recommendations, and heart-rate charts.
        </p>
      </Card>
    </div>
  );
}

export default About;
