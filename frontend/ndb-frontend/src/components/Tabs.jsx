export default function Tabs({ value, onChange, items }) {
  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
      {items.map((it) => {
        const active = it.value === value;
        return (
          <button
            key={it.value}
            onClick={() => onChange(it.value)}
            style={{
              borderRadius: 10,
              padding: "8px 12px",
              border: "1px solid #ddd",
              background: active ? "#f2f2ff" : "white",
              cursor: "pointer",
              fontWeight: active ? 600 : 400,
            }}
          >
            {it.label}
          </button>
        );
      })}
    </div>
  );
}
