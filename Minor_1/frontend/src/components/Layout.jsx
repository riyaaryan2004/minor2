import styles from "./Layout.module.css";

function Layout({ children }) {
  return (
    <div className={styles.wrapper}>
      <div className={styles.sidebar}>
        <h2 className={styles.logo}>Fitbit</h2>

        <div className={styles.menu}>
          <p>Dashboard</p>
          <p>Recommendations</p>
          <p>Alerts</p>
        </div>
      </div>

      <div className={styles.main}>
        {children}
      </div>
    </div>
  );
}

export default Layout;