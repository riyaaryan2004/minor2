import Layout from "./components/Layout";
import Dashboard from "./components/Dashboard";
import Recommendations from "./components/Recommendations";
import Alerts from "./components/Alerts";

function App() {
  return (
    <Layout>
      <Dashboard />
      <Recommendations />
      <Alerts />
    </Layout>
  );
}

export default App;