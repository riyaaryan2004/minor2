import styles from "./Layout.module.css";
import { Link, useLocation } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard" },
  { to: "/activity", label: "Activity" },
  { to: "/focus", label: "Focus Engine" },
  { to: "/movies", label: "Movies" },
  { to: "/alerts", label: "Alerts" },
  { to: "/about", label: "About" },
];

function Layout({ children }) {
  const location = useLocation();

  return (
    <div className={styles.wrapper}>
      <header className={styles.navbar}>
        <Link to="/" className={styles.logo}>
          <span className={styles.logoMark}>F</span>
          <span>FitIntel</span>
        </Link>

        <nav className={styles.navLinks}>
          {navItems.map((item) => (
            <Link
              key={item.to}
              to={item.to}
              className={location.pathname === item.to ? styles.active : ""}
            >
              {item.label}
            </Link>
          ))}
        </nav>
      </header>

      <main className={styles.main}>
        <div className={styles.content}>{children}</div>
      </main>
    </div>
  );
}

export default Layout;
