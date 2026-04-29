import Card from "./Card";

function About() {
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        gap: "32px",
      }}
    >
      {/* Title */}
      <h1
        style={{
          fontSize: "36px",   // ⬆️ bigger
          fontWeight: "700",
          background: "linear-gradient(to right, #60a5fa, #22d3ee)",
          WebkitBackgroundClip: "text",
          color: "transparent",
        }}
      >
        💙 About FitIntel
      </h1>

      {/* Intro */}
      <Card>
        <p
          style={{
            fontSize: "20px",   // ⬇️ balanced (25 was too big)
            lineHeight: "1.7",
            color: "#e2e8f0",
          }}
        >
          HealthAI is a smart health monitoring system that analyzes Fitbit data
          to provide real-time insights about your physical and mental well-being.
          It helps users stay aware of their health through alerts, activity
          suggestions, and personalized recommendations.
        </p>
      </Card>

      {/* Features */}
      <Card>
        <h2
          style={{
            fontSize: "26px",   // ⬇️ balanced (30 → 26)
            marginBottom: "16px",
            color: "#f1f5f9",
          }}
        >
          🚀 Key Features
        </h2>

        <ul
          style={{
            lineHeight: "1.9",
            fontSize: "18px",   // ⬆️ bigger list text
            color: "#cbd5f5",
          }}
        >
          <li>📊 Real-time heart rate monitoring</li>
          <li>🚨 Smart alerts based on health conditions</li>
          <li>🎬 Movie recommendations based on mood</li>
          <li>🏃 Activity suggestions for better health</li>
          <li>📈 Detailed analytics and insights</li>
        </ul>
      </Card>

      {/* How it works */}
      <Card>
        <h2
          style={{
            fontSize: "26px",
            marginBottom: "16px",
            color: "#f1f5f9",
          }}
        >
          ⚙️ How It Works
        </h2>

        <p
          style={{
            fontSize: "18px",   // ⬆️ bigger
            lineHeight: "1.7",
            color: "#cbd5f5",
          }}
        >
          The system collects data from Fitbit devices and processes it using
          machine learning models. Based on your heart rate, stress levels, and
          activity patterns, it generates alerts and personalized suggestions
          to improve your daily routine.
        </p>
      </Card>

      {/* Footer note */}
      <Card>
        <p
          style={{
            fontSize: "17px",
            opacity: 0.7,
          }}
        >
        Designed and developed with ❤️ for smarter health monitoring.
        </p>
      </Card>
    </div>
  );
}

export default About;