import { useEffect, useState } from "react";
import { getMovies, getActivities } from "../api/api";
import styles from "./Recommendations.module.css";
import Card from "./Card";

function Recommendations() {
  const [movies, setMovies] = useState({});
  const [activities, setActivities] = useState({});

  useEffect(() => {
    const fetchData = async () => {
      const movieData = await getMovies();
      const activityData = await getActivities();

      setMovies(movieData || {});
      setActivities(activityData || {});
    };

    fetchData();
  }, []);

  return (
    <div className={styles.wrapper}>
      
      {/* 🎬 MOVIES CARD */}
      <Card>
        <div className={styles.container}>
          <h2 className={styles.heading}>✨ Recommendations</h2>

          <div className={styles.section}>
            <h3>🎬 Movies</h3>

            {movies.movies?.length > 0 ? (
              <>
                <p>{movies.why}</p>

                <div className={styles.grid}>
                  {movies.movies.slice(0, 4).map((m, i) => (
                    <div key={i} className={styles.card}>
                      <strong>{m.title}</strong>

                      {m.release_date && (
                        <p className={styles.meta}>📅 {m.release_date}</p>
                      )}

                      {m.vote_average && (
                        <p className={styles.rating}>⭐ {m.vote_average}</p>
                      )}
                    </div>
                  ))}
                </div>
              </>
            ) : (
              <p className={styles.empty}>No movies available</p>
            )}
          </div>
        </div>
      </Card>

      {/* 🏃 ACTIVITY CARD */}
      <Card>
        <div className={styles.container}>
          <div className={styles.section}>
            <h3>🏃 Activity Suggestions</h3>

            {activities.suggestion ? (
              <>
                <div className={styles.activityCard}>
                  {activities.suggestion}
                </div>

                <p style={{ opacity: 0.7 }}>
                  {activities.why}
                </p>
              </>
            ) : (
              <p className={styles.empty}>No suggestions available</p>
            )}
          </div>
        </div>
      </Card>

    </div>
  );
}

export default Recommendations;