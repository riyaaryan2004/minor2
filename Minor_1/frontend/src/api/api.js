const BASE_URL = "http://127.0.0.1:5000";

// Get health predictions
export const getPredictions = async () => {
  try {
    const res = await fetch(`${BASE_URL}/predict`);

    if (!res.ok) {
      throw new Error("Failed to fetch predictions");
    }

    return await res.json();
  } catch (err) {
    console.error("Error fetching predictions:", err);
    return null;
  }
};

// Movies
export const getMovies = async () => {
  try {
    const res = await fetch(`${BASE_URL}/movies`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
};

// Activities
export const getActivities = async () => {
  try {
    const res = await fetch(`${BASE_URL}/activity`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
};

// Alerts
export const getAlerts = async () => {
  try {
    const res = await fetch(`${BASE_URL}/alerts`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
};

export const getHeartAlertConfig = async () => {
  try {
    const res = await fetch(`${BASE_URL}/heart-alert/config`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return null;
  }
};

export const checkHeartAlert = async (payload) => {
  try {
    const res = await fetch(`${BASE_URL}/heart-alert/check`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    const data = await res.json();

    return res.ok ? data : { error: true, message: data?.error || "Alert check failed" };
  } catch (err) {
    console.error(err);
    return { error: true, message: "Alert check failed" };
  }
};

export const acknowledgeHeartAlert = async (alertId) => {
  try {
    const res = await fetch(`${BASE_URL}/heart-alert/acknowledge`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ alertId }),
    });
    const data = await res.json();

    return res.ok ? data : { error: true, message: data?.error || "Could not acknowledge alert" };
  } catch (err) {
    console.error(err);
    return { error: true, message: "Could not acknowledge alert" };
  }
};

export const getHeartAlertStatus = async (alertId) => {
  try {
    const res = await fetch(`${BASE_URL}/heart-alert/status/${encodeURIComponent(alertId)}`);
    return res.ok ? await res.json() : null;
  } catch (err) {
    console.error(err);
    return null;
  }
};

// Get heart rate data (hourly graph)
export const getHRData = async () => {
  try {
    const res = await fetch(`${BASE_URL}/hr-data`);
    return await res.json();
  } catch (err) {
    console.error(err);
    return [];
  }
};

export const getHRMinute = async () => {
  const res = await fetch("http://127.0.0.1:5000/hr-minute");
  return await res.json();
};

export const getLatestHeartRate = async () => {
  try {
    const res = await fetch(`${BASE_URL}/hr-latest?t=${Date.now()}`);
    return res.ok ? await res.json() : null;
  } catch (err) {
    console.error(err);
    return null;
  }
};
