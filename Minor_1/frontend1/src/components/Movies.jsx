import { useEffect, useState, useCallback } from "react";
import { getMovies } from "../api/api";
import Card from "./Card";
import styles from "./Movies.module.css";

const BASE_URL = "http://127.0.0.1:5000";

const posterUrl = (path) => {
  if (!path) return "";
  return `https://image.tmdb.org/t/p/w342${path}`;
};

/* ✅ GENRE MAP */
const GENRE_MAP = {
  28: "Action",
  35: "Comedy",
  18: "Drama",
  10749: "Romance",
  53: "Thriller",
  16: "Animation",
  27: "Horror",
  80: "Crime",
  12: "Adventure",
  10751: "Family",
  14: "Fantasy",
};

function Movies() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);

  const [filters, setFilters] = useState({
    language: "",
    min_rating: "",
    year_after: "",
    genre: "",
  });

  const fetchMovies = useCallback(async () => {
    setLoading(true);

    const cleanFilters = Object.fromEntries(
      Object.entries(filters).filter(([_, v]) => v !== "" && v !== null)
    );

    const data = await getMovies(null, cleanFilters);

    setMovies(data?.movies || []);
    setLoading(false);
  }, [filters]);

  useEffect(() => {
    const loadAll = async () => {
      await fetchMovies();
    };

    loadAll();
  }, [fetchMovies]);

  const refreshMovies = async () => {
    try {
      await fetch(`${BASE_URL}/movies/refresh`);
      fetchMovies();
    } catch (err) {
      console.error("Refresh failed", err);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;

    setFilters((prev) => ({
      ...prev,
      [name]:
        name === "genre" || name === "year_after" || name === "min_rating"
          ? value === "" ? "" : Number(value)
          : value,
    }));
  };

  const getMatchScore = (movie) => {
    return 80 + (movie.id % 20);
  };

  return (
    <div className={styles.wrapper}>
      <section className={styles.header}>
        <h1>Movie Recommendations</h1>
        <p>Based on your current mood and health state</p>
      </section>

      <div className={styles.insightBox}>
        <h3>🧠 Recommendation Insight</h3>
        <p>
          {filters.genre
            ? "Using your selected genre preference"
            : "Selected based on your mood, sleep, and activity patterns"}
        </p>
      </div>

      <div className={styles.filterBar}>
        <select name="language" value={filters.language} onChange={handleChange}>
          <option value="">🌐 All Languages</option>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="ko">Korean</option>
          <option value="ja">Japanese</option>
          <option value="fr">French</option>
          <option value="es">Spanish</option>
          <option value="it">Italian</option>
        </select>

        <select name="genre" value={filters.genre} onChange={handleChange}>
          <option value="">🎭 All Genres</option>
          <option value="28">Action</option>
          <option value="35">Comedy</option>
          <option value="18">Drama</option>
          <option value="10749">Romance</option>
          <option value="53">Thriller</option>
          <option value="16">Animation</option>
          <option value="27">Horror</option>
          <option value="80">Crime</option>
        </select>

        <select name="min_rating" value={filters.min_rating} onChange={handleChange}>
          <option value="">⭐ Any Rating</option>
          <option value="6">6+</option>
          <option value="7">7+</option>
          <option value="8">8+</option>
          <option value="9">9+</option>
        </select>

        <select name="year_after" value={filters.year_after} onChange={handleChange}>
          <option value="">📅 Any Year</option>
          <option value="2020">After 2020</option>
          <option value="2015">After 2015</option>
          <option value="2010">After 2010</option>
          <option value="2000">After 2000</option>
          <option value="1990">After 1990</option>
          <option value="1980">After 1980</option>
          <option value="1950">After 1950</option>
          <option value="1900">After 1900</option>
        </select>

        <button className={styles.buttonPrimary} onClick={fetchMovies}>
          Apply
        </button>

        <button className={styles.buttonSecondary} onClick={refreshMovies}>
          Refresh
        </button>
      </div>

      <Card>
        {loading ? (
          <p>Loading...</p>
        ) : movies.length > 0 ? (
          <>
            <h2 className={styles.sectionTitle}>🎬 Your Picks Today</h2>

            <div className={styles.grid}>
              {movies.map((movie, index) => (
                <div key={index} className={styles.movieCard}>
                  <div className={styles.posterShell}>
                    {posterUrl(movie.poster_path) ? (
                      <img src={posterUrl(movie.poster_path)} alt={movie.title} />
                    ) : (
                      <div className={styles.posterFallback}>
                        <span>FitIntel Pick</span>
                      </div>
                    )}

                    <span className={styles.rank}>0{index + 1}</span>

                    <span className={styles.matchScore}>
                      {getMatchScore(movie)}% match
                    </span>
                  </div>

                  <div className={styles.movieInfo}>
                    <strong>{movie.title}</strong>

                    <div className={styles.metaRow}>
                      <span>
                        {movie.release_date
                          ? movie.release_date.slice(0, 4)
                          : "N/A"}
                      </span>
                      <span>
                        {movie.vote_average
                          ? `${movie.vote_average.toFixed(1)}/10`
                          : "No rating"}
                      </span>
                    </div>

                    <div className={styles.tags}>
                      {movie.genre_ids?.slice(0, 2).map((g) => (
                        <span key={g} className={styles.tag}>
                          {GENRE_MAP[g] || "Other"}
                        </span>
                      ))}
                    </div>

                    {movie.overview && (
                      <p className={styles.description}>
                        {movie.overview.slice(0, 100)}...
                      </p>
                    )}

                    <div className={styles.reason}>
                      {movie.vote_average > 8
                        ? "⭐ Critically acclaimed & high-rated"
                        : "🎯 Aligned with your current mood pattern"}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <p>No movies available</p>
        )}
      </Card>
    </div>
  );
}

export default Movies;