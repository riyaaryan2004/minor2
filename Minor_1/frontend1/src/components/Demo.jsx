import { useState } from "react";
import { scenarios } from "../mockScenarios";
import Dashboard from "./Dashboard";

function Demo() {
  const [mode, setMode] = useState("highStress");

  return (
    <div>
      {/* 🔥 Simple selector */}
      <div style={{ marginBottom: "20px" }}>
        <button onClick={() => setMode("normal")}>Normal</button>
        <button onClick={() => setMode("highStress")}>High Stress</button>
        <button onClick={() => setMode("lowSleep")}>Low Sleep</button>
        <button onClick={() => setMode("inactive")}>Inactive</button>
      </div>

      {/* 🔥 Pass mock data */}
      <Dashboard demoData={scenarios[mode]} />
    </div>
  );
}

export default Demo;