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
    <div style={{ display: "flex", flexDirection: "column", gap: "15px" }}>

      {/* 🔥 TODAY INSIGHT */}
      <h2 style={{ fontSize: "20px", color: "#60a5fa" }}>
        🧠 Today's Insight
      </h2>
      <div>{data.today_insight}</div>

      {/* 📊 METRICS */}
      <h3>📊 Metrics</h3>
      <div>😴 Sleep: {data.metrics.sleep} hrs</div>
      <div>❤️ Avg HR: {data.metrics.avg_hr}</div>
      <div>🚶 Steps: {data.metrics.steps}</div>

      {/* 🔍 MEANING */}
      <h3>🔍 What this means</h3>
      {data.meaning.map((m, i) => (
        <div key={i}>• {m}</div>
      ))}

      {/* 🔗 WHY */}
      <h3>🔗 Why this matters</h3>
      <div>{data.reasoning}</div>

      {/* 🎯 ACTIVITY */}
      <h3>🏃 Suggested Action</h3>
      <div>👉 {data.activity.suggestion}</div>
      <div style={{ opacity: 0.7 }}>
        {data.activity.why}
      </div>

      {/* 🎬 MOVIE */}
      <h3>🎬 Why Movie?</h3>
      <div>{data.movie.why}</div>

      {/* 📉 TRENDS */}
      <h3>📉 Trends</h3>
      <div>Sleep: {data.trends.sleep}</div>
      <div>Stress: {data.trends.stress}</div>
      <div>Steps: {data.trends.steps}</div>

    </div>
  </Card>
);
}

export default Insights;