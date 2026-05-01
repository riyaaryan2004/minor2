import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import Alerts from "./components/Alerts";
import About from "./components/About";
import Activity from "./components/Activity";
import Movies from "./components/Movies";

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/activity" element={<Activity />} />
          <Route path="/movies" element={<Movies />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/about" element={<About />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
