const BASE_URL = "http://127.0.0.1:5000";
const REQUEST_TIMEOUT = 12000;
const MOVIE_REQUEST_TIMEOUT = 30000;

const withDate = (path, date) => {
  if (!date) {
    return `${BASE_URL}${path}`;
  }

  return `${BASE_URL}${path}?date=${encodeURIComponent(date)}`;
};

const fetchJson = async (url, options = {}, timeout = REQUEST_TIMEOUT) => {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeout);

  try {
    const res = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    const data = await res.json();

    return { ok: res.ok, data };
  } finally {
    clearTimeout(timeoutId);
  }
};

// Get health predictions
export const getPredictions = async (date) => {
  try {
    const res = await fetchJson(withDate("/predict", date));

    if (!res.ok) {
      return { error: true };
    }

    return res.data;
  } catch (err) {
    console.error("Error fetching predictions:", err);
    return null;
  }
};

export const syncDay = async (date) => {
  try {
    const res = await fetchJson(withDate("/sync-day", date), {
      method: "POST",
    });

    if (!res.ok) {
      return { error: true, message: res.data?.error || "Failed to sync data" };
    }

    return res.data;
  } catch (err) {
    console.error("Error syncing Fitbit data:", err);
    return { error: true, message: "Failed to sync data" };
  }
};

// Movies
export const getMovies = async (date) => {
  try {
    const res = await fetchJson(withDate("/movies", date), {}, MOVIE_REQUEST_TIMEOUT);
    return res.ok ? res.data : { movies: [], error: true };
  } catch (err) {
    console.error("Error fetching movies:", err);
    return { movies: [], error: true };
  }
};

export const refreshMoviePool = async () => {
  try {
    const res = await fetchJson(`${BASE_URL}/movies/refresh`, {}, MOVIE_REQUEST_TIMEOUT);
    return res.ok ? res.data : { error: true };
  } catch (err) {
    console.error("Error refreshing movies:", err);
    return { error: true };
  }
};

export const getMovieProfile = async () => {
  try {
    const res = await fetchJson(`${BASE_URL}/movies/profile`);
    return res.ok ? res.data : { liked: [], disliked: [], history: [] };
  } catch (err) {
    console.error("Error fetching movie profile:", err);
    return { liked: [], disliked: [], history: [] };
  }
};

export const likeMovie = async (title) => {
  try {
    const res = await fetchJson(`${BASE_URL}/movies/like`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    return res.ok ? res.data : { error: true };
  } catch (err) {
    console.error("Error liking movie:", err);
    return { error: true };
  }
};

export const dislikeMovie = async (title) => {
  try {
    const res = await fetchJson(`${BASE_URL}/movies/dislike`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title }),
    });
    return res.ok ? res.data : { error: true };
  } catch (err) {
    console.error("Error disliking movie:", err);
    return { error: true };
  }
};

// Activities
export const getActivities = async (date) => {
  try {
    const res = await fetchJson(withDate("/activity", date));
    return res.ok ? res.data : { suggestions: [] };
  } catch (err) {
    console.error(err);
    return { suggestions: [] };
  }
};

// Alerts
export const getAlerts = async (date) => {
  try {
    const res = await fetchJson(withDate("/alerts", date));
    return res.ok ? res.data : { alerts: [] };
  } catch (err) {
    console.error(err);
    return { alerts: [] };
  }
};

// Heart rate (hourly)
export const getHRData = async (date) => {
  try {
    const res = await fetchJson(withDate("/hr-data", date));
    return res.ok && Array.isArray(res.data) ? res.data : [];
  } catch (err) {
    console.error(err);
    return [];
  }
};

// Heart rate (minute)
export const getHRMinute = async (date) => {
  try {
    const res = await fetchJson(withDate("/hr-minute", date));
    return res.ok && Array.isArray(res.data) ? res.data : [];
  } catch (err) {
    console.error(err);
    return [];
  }
};
