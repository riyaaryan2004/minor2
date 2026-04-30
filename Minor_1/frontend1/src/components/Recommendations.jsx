import { useEffect, useState } from "react";
import { getMovies, getActivities } from "../api/api";
import styles from "./Recommendations.module.css";
import Card from "./Card";

const posterUrl = (path) => {
  if (!path) {
    return "";
  }

  return `https://image.tmdb.org/t/p/w342${path}`;
};

function Recommendations() {
  const [movies, setMovies] = useState([]);
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const [movieData, activityData] = await Promise.all([
        getMovies(),
        getActivities(),
      ]);

      setMovies(movieData?.movies || []);
      setActivities(activityData?.suggestions || []);
      setLoading(false);
    };

    fetchData();
  }, []);

  return (
    <div className={styles.wrapper}>
      <section className={styles.header}>
        <p className={styles.kicker}>Personalized picks</p>
        <h1>Recommendations</h1>
        <p>Content and activity ideas generated from the latest health snapshot.</p>
      </section>

      {loading ? (
        <div className={styles.state}>Loading recommendations...</div>
      ) : (
        <div className={styles.columns}>
          <Card>
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>Movies</h2>
                <span>{movies.length} picks</span>
              </div>

              {movies.length > 0 ? (
                <div className={styles.grid}>
                  {movies.slice(0, 4).map((movie, index) => (
                    <article key={`${movie.title}-${index}`} className={styles.movieCard}>
                      <div className={styles.posterShell}>
                        {posterUrl(movie.poster_path) ? (
                          <img
                            src={posterUrl(movie.poster_path)}
                            alt={`${movie.title} poster`}
                            loading="lazy"
                          />
                        ) : (
                          <div className={styles.posterFallback}>
                            <span>FitIntel Pick</span>
                          </div>
                        )}
                        <span className={styles.rank}>0{index + 1}</span>
                      </div>

                      <div className={styles.movieInfo}>
                        <strong>{movie.title}</strong>
                        <div className={styles.metaRow}>
                          <span>{movie.release_date || "N/A"}</span>
                          <span>{movie.vote_average ? `${movie.vote_average}/10` : "No rating"}</span>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              ) : (
                <p className={styles.empty}>No movies available</p>
              )}
            </div>
          </Card>

          <Card>
            <div className={styles.section}>
              <div className={styles.sectionHeader}>
                <h2>Activity Plan</h2>
                <span>{activities.length} tips</span>
              </div>

              {activities.length > 0 ? (
                <div className={styles.activities}>
                  {activities.slice(0, 4).map((activity, index) => (
                    <div key={index} className={styles.activityCard}>
                      <span>{index + 1}</span>
                      <p>{activity}</p>
                    </div>
                  ))}
                </div>
              ) : (
                <p className={styles.empty}>No suggestions available</p>
              )}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

export default Recommendations;
