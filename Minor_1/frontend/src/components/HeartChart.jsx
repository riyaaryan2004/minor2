function HeartChart({ data }) {
  return (
    <div
      style={{
        marginTop: "30px",
        background: "#0f172a",
        padding: "20px",
        borderRadius: "16px",
        color: "white",
      }}
    >
      <h2>Heart Rate (Today)</h2>

      <div style={{ display: "flex", alignItems: "flex-end", height: "200px" }}>
        {data.map((point, i) => (
          <div
            key={i}
            style={{
              flex: 1,
              margin: "0 2px",
              textAlign: "center",
            }}
          >
            <div
              style={{
                height: `${point.hr * 1.2}px`,
                background: "#22c55e",
                borderRadius: "4px",
              }}
            ></div>

            <span style={{ fontSize: "10px" }}>
              {point.hour}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default HeartChart;