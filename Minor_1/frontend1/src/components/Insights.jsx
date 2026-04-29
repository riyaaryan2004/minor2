import Card from "./Card";

function Insights({ data }) {
  if (!data) {
    return (
      <p style={{ opacity: 0.6, fontStyle: "italic" }}>
        No insights available
      </p>
    );
  }

  return (
    <Card>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          gap: "15px",
        }}
      >
        <h2
          style={{
            fontSize: "20px",
            fontWeight: "600",
            color: "#60a5fa",
          }}
        >
          📊 Insights
        </h2>

        <div
          style={{
            display: "flex",
            flexDirection: "column",
            gap: "10px",
          }}
        >
          <div
            style={{
              padding: "10px",
              borderRadius: "10px",
              background: "rgba(255,255,255,0.05)",
            }}
          >
            💓 Stress level is <strong>{data.stress}</strong>
          </div>

          <div
            style={{
              padding: "10px",
              borderRadius: "10px",
              background: "rgba(255,255,255,0.05)",
            }}
          >
            😴 Sleep duration: <strong>{data.sleep} hrs</strong>
          </div>

          <div
            style={{
              padding: "10px",
              borderRadius: "10px",
              background: "rgba(255,255,255,0.05)",
            }}
          >
            ⚡ Productivity score: <strong>{data.productivity}</strong>
          </div>

          <div
            style={{
              padding: "10px",
              borderRadius: "10px",
              background: "rgba(255,255,255,0.05)",
            }}
          >
            😊 Mood: <strong>{data.mood}</strong>
          </div>
        </div>

        <div
          style={{
            marginTop: "10px",
            padding: "12px",
            borderRadius: "10px",
            background:
              data.stress > 70
                ? "rgba(239,68,68,0.15)"
                : "rgba(34,197,94,0.1)",
            borderLeft:
              data.stress > 70
                ? "4px solid #ef4444"
                : "4px solid #22c55e",
            fontWeight: "500",
          }}
        >
          {data.stress > 70
            ? "⚠️ High stress detected. Consider relaxation."
            : "✅ You're doing well today. Keep it up!"}
        </div>
      </div>
    </Card>
  );
}

export default Insights;