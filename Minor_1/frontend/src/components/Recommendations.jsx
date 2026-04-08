import { useEffect, useState } from "react";
import { getMovies, getActivities } from "../api/api";
import styles from "./Recommendations.module.css";

function Recommendations() {
  const [movies, setMovies] = useState([]);
  const [activities, setActivities] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const movieData = await getMovies();
      const activityData = await getActivities();

      setMovies(movieData?.movies || []);
      setActivities(activityData?.suggestions || []);
    };

    fetchData();
  }, []);

  return (
    <div className={styles.container}>
      <h2>Recommendations</h2>

      {/* Movies */}
      <div className={styles.section}>
        <h3>Movies</h3>
        {movies.length > 0 ? (
          movies.map((m, i) => (
            <div key={i} className={styles.card}>
              <strong>{m.title}</strong>
              {m.release_date && <p>Year: {m.release_date}</p>}
              {m.vote_average && <p>⭐ {m.vote_average}</p>}
            </div>
          ))
        ) : (
          <p>No movies available</p>
        )}
      </div>

      {/* Activities */}
      <div className={styles.section}>
        <h3>Activity Suggestions</h3>
        {activities.length > 0 ? (
          activities.map((a, i) => (
            <div key={i} className={styles.card}>
              {a}
            </div>
          ))
        ) : (
          <p>No suggestions available</p>
        )}
      </div>
    </div>
  );
}

export default Recommendations;