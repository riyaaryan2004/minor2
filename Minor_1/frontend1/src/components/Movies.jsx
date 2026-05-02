import { useEffect, useState, useCallback } from "react";
import { getMovies } from "../api/api";
import styles from "./Movies.module.css";

const DESCRIPTION_LIMIT = 120;
const FEATURED_DESCRIPTION_LIMIT = 230;

const posterUrl = (path) => {
  if (!path) return "";
  return `https://image.tmdb.org/t/p/w342${path}`;
};

const GENRE_MAP = {
  12: "Adventure",
  14: "Fantasy",
  16: "Animation",
  18: "Drama",
  27: "Horror",
  28: "Action",
  35: "Comedy",
  53: "Thriller",
  80: "Crime",
  9648: "Mystery",
  10749: "Romance",
  10751: "Family",
};

const LANGUAGE_MAP = {
  hi: "Hindi",
  en: "Hollywood",
};

const moodSignals = [
  "Mood-based genres",
  "Popular known movies",
  "Comfort watch balance",
  "Fresh daily queue",
];

const panelStyle = {
  display: "grid",
  gap: "18px",
};

const chipRowStyle = {
  display: "flex",
  flexWrap: "wrap",
  gap: "8px",
};

const compactSectionStyle = {
  display: "grid",
  gap: "14px",
};

const getLanguageLabel = (movie) => {
  return LANGUAGE_MAP[movie.original_language] || "Popular";
};

const getReason = (movie) => {
  if (movie.original_language === "hi") {
    return "";
  }

  if ((movie.vote_count || 0) >= 1000 || (movie.vote_average || 0) >= 8) {
    return "Included as a well-known, high-confidence recommendation.";
  }

  return "Selected because its genre fits today's mood and energy level.";
};

const getMatchScore = (movie) => {
  const rating = movie.vote_average || 0;
  const voteBoost = Math.min(movie.vote_count || 0, 2000) / 2000;
  const languageBoost = movie.original_language === "hi" ? 5 : 0;

  return Math.min(98, Math.round(78 + rating * 1.5 + voteBoost * 5 + languageBoost));
};

const getMovieKey = (movie, index) => {
  return movie.id || movie.title || index;
};

const getDescription = (overview, isExpanded, limit) => {
  if (!overview || overview.length <= limit || isExpanded) {
    return overview;
  }

  return `${overview.slice(0, limit)}...`;
};

function Movies() {
  const [movies, setMovies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedMovies, setExpandedMovies] = useState({});

  const fetchMovies = useCallback(async () => {
    setLoading(true);
    setError("");

    const data = await getMovies();

    if (data?.error) {
      setError("Unable to load movie recommendations right now.");
      setMovies([]);
    } else {
      setMovies(data?.movies || []);
      setExpandedMovies({});
    }

    setLoading(false);
  }, []);

  useEffect(() => {
    fetchMovies();
  }, [fetchMovies]);

  const toggleDescription = (movieKey) => {
    setExpandedMovies((current) => ({
      ...current,
      [movieKey]: !current[movieKey],
    }));
  };

  const renderDescription = (movie, movieKey, limit = DESCRIPTION_LIMIT) => {
    const overview = movie.overview || "";
    const isLongOverview = overview.length > limit;
    const isExpanded = Boolean(expandedMovies[movieKey]);
    const description = getDescription(overview, isExpanded, limit);

    if (!overview) return null;

    return (
      <div className={styles.descriptionBlock}>
        <p className={styles.description}>{description}</p>

        {isLongOverview && (
          <button
            type="button"
            className={styles.readMoreButton}
            onClick={() => toggleDescription(movieKey)}
          >
            {isExpanded ? "Show less" : "Read more"}
          </button>
        )}
      </div>
    );
  };

  const renderMovieCard = (movie, index) => {
    const movieKey = getMovieKey(movie, index);
    const reason = getReason(movie);

    return (
      <div key={movieKey} className={styles.movieCard}>
        <div className={styles.posterShell}>
          {posterUrl(movie.poster_path) ? (
            <img src={posterUrl(movie.poster_path)} alt={movie.title} />
          ) : (
            <div className={styles.posterFallback}>
              <span>FitIntel Pick</span>
            </div>
          )}

          <span className={styles.rank}>
            {String(index + 1).padStart(2, "0")}
          </span>

          <span className={styles.matchScore}>
            <span aria-hidden="true">*</span> {getMatchScore(movie)}%
          </span>
        </div>

        <div className={styles.movieInfo}>
          <div className={styles.titleRow}>
            <strong>{movie.title}</strong>
            <span className={styles.languagePill}>{getLanguageLabel(movie)}</span>
          </div>

          <div className={styles.metaRow}>
            <span>{movie.release_date ? movie.release_date.slice(0, 4) : "Known pick"}</span>
            <span>{movie.vote_average ? `* ${movie.vote_average.toFixed(1)}/10` : "No rating"}</span>
          </div>

          <div className={styles.tags}>
            {movie.genre_ids?.slice(0, 2).map((genre) => (
              <span key={genre} className={styles.tag}>
                {GENRE_MAP[genre] || "Popular"}
              </span>
            ))}
          </div>

          {renderDescription(movie, movieKey)}

          {reason && (
            <div className={styles.reason}>
              <span aria-hidden="true">*</span>
              {reason}
            </div>
          )}
        </div>
      </div>
    );
  };

  const topPick = movies[0];
  const remainingMovies = movies.slice(1);
  const hindiMovies = remainingMovies.filter((movie) => movie.original_language === "hi");
  const hollywoodMovies = remainingMovies.filter((movie) => movie.original_language === "en");
  const otherMovies = remainingMovies.filter(
    (movie) => movie.original_language !== "hi" && movie.original_language !== "en"
  );

  return (
    <div className={styles.wrapper}>
      <section className={styles.header}>
        <div>
          <p className={styles.kicker}>FitIntel Cinema</p>
          <h1>Movie Recommendations</h1>
          <p>
            A watchlist built from your predicted mood, productivity, and energy for the day.
          </p>
        </div>

        <div className={styles.heroBadge} aria-hidden="true">
          <span className={styles.heroIcon}>FI</span>
          <span>{movies.length || 30} curated picks</span>
        </div>
      </section>

      <div className={styles.insightBox}>
        <span className={styles.insightIcon} aria-hidden="true">ML</span>
        <div>
          <h3>Why These Movies?</h3>
          <p>
            The recommender chooses genres from today&apos;s mood and productivity, then ranks Hindi
            titles first while keeping famous Hollywood movies when they are a strong match.
          </p>
        </div>
      </div>

      <div style={chipRowStyle}>
        {moodSignals.map((signal) => (
          <span key={signal} className={styles.tag}>
            {signal}
          </span>
        ))}
      </div>

      <section className={styles.moviePanel}>
        {loading ? (
          <div style={panelStyle}>
            <div className={styles.statePanel}>
              <span className={styles.loadingIcon} aria-hidden="true" />
              <p>Building your movie queue...</p>
            </div>

            <div className={styles.grid} aria-hidden="true">
              {[1, 2, 3, 4].map((item) => (
                <div key={item} className={styles.movieCard}>
                  <div className={styles.posterFallback}>
                    <span>Loading</span>
                  </div>
                  <div className={styles.movieInfo}>
                    <span className={styles.tag}>Finding matches</span>
                    <p className={styles.description}>Checking mood, genre, language, and popularity signals.</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : error ? (
          <div className={styles.errorPanel}>
            <strong>Unable to load movies</strong>
            <p>{error}</p>
          </div>
        ) : movies.length > 0 ? (
          <div style={panelStyle}>
            <div className={styles.sectionHeader}>
              <div>
                <p className={styles.panelEyebrow}>Today&apos;s best match</p>
                <h2 className={styles.sectionTitle}>Start With This</h2>
              </div>
              <span className={styles.countBadge}>{movies.length} movies</span>
            </div>

            {topPick && (
              <div className={styles.featuredPick}>
                <div className={styles.featuredPoster}>
                  {posterUrl(topPick.poster_path) ? (
                    <img src={posterUrl(topPick.poster_path)} alt={topPick.title} />
                  ) : (
                    <div className={styles.posterFallback}>
                      <span>FitIntel Pick</span>
                    </div>
                  )}
                  <span className={styles.rank}>01</span>
                </div>

                <div className={styles.featuredInfo}>
                  <div className={styles.featuredHeader}>
                    <div>
                      <p className={styles.panelEyebrow}>Best match today</p>
                      <h3>{topPick.title}</h3>
                    </div>
                    <span className={styles.matchScore}>
                      <span aria-hidden="true">*</span> {getMatchScore(topPick)}%
                    </span>
                  </div>

                  <p className={styles.featuredCopy}>
                    This movie is ranked first after combining today&apos;s mood fit, productivity fit,
                    language preference, public rating, and popularity.
                  </p>

                  <div className={styles.tags}>
                    <span className={styles.tag}>{getLanguageLabel(topPick)}</span>
                    {topPick.vote_average && (
                      <span className={styles.tag}>{topPick.vote_average.toFixed(1)}/10 rating</span>
                    )}
                    {topPick.genre_ids?.slice(0, 3).map((genre) => (
                      <span key={genre} className={styles.tag}>
                        {GENRE_MAP[genre] || "Popular"}
                      </span>
                    ))}
                  </div>

                  {renderDescription(topPick, getMovieKey(topPick, 0), FEATURED_DESCRIPTION_LIMIT)}
                </div>
              </div>
            )}

            {hindiMovies.length > 0 && (
              <div style={compactSectionStyle}>
                <div className={styles.sectionHeader}>
                  <div>
                    <p className={styles.panelEyebrow}>Hindi-first queue</p>
                    <h2 className={styles.sectionTitle}>Bollywood and Hindi Picks</h2>
                  </div>
                  <span className={styles.countBadge}>{hindiMovies.length} movies</span>
                </div>
                <div className={styles.grid}>
                  {hindiMovies.map((movie, index) => renderMovieCard(movie, index + 1))}
                </div>
              </div>
            )}

            {hollywoodMovies.length > 0 && (
              <div style={compactSectionStyle}>
                <div className={styles.sectionHeader}>
                  <div>
                    <p className={styles.panelEyebrow}>Global matches</p>
                    <h2 className={styles.sectionTitle}>Famous Hollywood Matches</h2>
                  </div>
                  <span className={styles.countBadge}>{hollywoodMovies.length} movies</span>
                </div>
                <div className={styles.grid}>
                  {hollywoodMovies.map((movie, index) =>
                    renderMovieCard(movie, hindiMovies.length + index + 1)
                  )}
                </div>
              </div>
            )}

            {otherMovies.length > 0 && (
              <div style={compactSectionStyle}>
                <div className={styles.sectionHeader}>
                  <div>
                    <p className={styles.panelEyebrow}>More to consider</p>
                    <h2 className={styles.sectionTitle}>Additional Picks</h2>
                  </div>
                  <span className={styles.countBadge}>{otherMovies.length} movies</span>
                </div>
                <div className={styles.grid}>
                  {otherMovies.map((movie, index) =>
                    renderMovieCard(movie, hindiMovies.length + hollywoodMovies.length + index + 1)
                  )}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className={styles.statePanel}>
            <p>No movies available for today&apos;s recommendation.</p>
          </div>
        )}
      </section>
    </div>
  );
}

export default Movies;
