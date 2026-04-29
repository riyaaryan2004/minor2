import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import Recommendations from "./components/Recommendations";
import Alerts from "./components/Alerts";
import About from "./components/About";
import Demo from "./components/Demo";

function App() {
  return (
    <Router>
      <Layout>
        {/* 🔥 ADD THIS WRAPPER */}
        <div
          style={{
            width: "100%",
            maxWidth: "1200px",
            display: "flex",
            flexDirection: "column",
            gap: "30px",
          }}
        >
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/about" element={<About />} />
            <Route path="/demo" element={<Demo />} />
          </Routes>
        </div>
      </Layout>
    </Router>
  );
}

export default App;