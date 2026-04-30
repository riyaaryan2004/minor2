import { useEffect, useState } from "react";
import { getMovies } from "../api/api";
import Card from "./Card";
import styles from "./Recommendations.module.css";

const posterUrl = (path) => {
  if (!path) return "";
  return `https://image.tmdb.org/t/p/w342${path}`;
};

function Movies() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      const data = await getMovies();
      setMovies(data?.movies || []);
      setLoading(false);
    };

    fetchData();
  }, []);

  return (
    <div className={styles.wrapper}>
      <section className={styles.header}>
        <h1>Movie Recommendations</h1>
        <p>Based on your current mood and health state</p>
      </section>

      <Card>
        {loading ? (
          <p>Loading...</p>
        ) : movies.length > 0 ? (
          <div className={styles.grid}>
            {movies.map((movie, index) => (
              <div key={index} className={styles.movieCard}>
                <div className={styles.posterShell}>
                  {posterUrl(movie.poster_path) ? (
                    <img
                      src={posterUrl(movie.poster_path)}
                      alt={movie.title}
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
                    <span>
                      {movie.release_date || "N/A"}
                    </span>
                    <span>
                      {movie.vote_average
                        ? `${movie.vote_average}/10`
                        : "No rating"}
                    </span>
                  </div>

                  {/* 🔥 NEW: description */}
                  {movie.overview && (
                    <p
                      style={{
                        fontSize: "12px",
                        marginTop: "6px",
                        opacity: 0.8,
                      }}
                    >
                      {movie.overview.slice(0, 100)}...
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p>No movies available</p>
        )}
      </Card>
    </div>
  );
}

export default Movies;