import styles from "./Layout.module.css";
import { Link, useLocation } from "react-router-dom";

function Layout({ children }) {
  const location = useLocation();

  return (
    <div className={styles.wrapper}>
      
      {/* 🔥 NAVBAR */}
      <div className={styles.navbar}>
        <h2 className={styles.logo}>❤️‍🔥 FitIntel</h2>

        <div className={styles.navLinks}>
          <Link
            to="/"
            className={location.pathname === "/" ? styles.active : ""}
          >
            🏠 Dashboard
          </Link>

          <Link
            to="/recommendations"
            className={location.pathname === "/recommendations" ? styles.active : ""}
          >
            ✨ Recommendations
          </Link>

          <Link
            to="/alerts"
            className={location.pathname === "/alerts" ? styles.active : ""}
          >
            🚨 Alerts
          </Link>
          <Link
  to="/about"
  className={location.pathname === "/about" ? styles.active : ""}
>
  ℹ️ About
</Link>
        </div>
      </div>

      {/* 🔥 MAIN CONTENT */}
      <div className={styles.main}>
        <div className={styles.content}>
          {children}
        </div>
      </div>
    </div>
  );
}

export default Layout;