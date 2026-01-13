export default function Badge({ children }) {
  return (
    <span
      style={{
        display: "inline-block",
        padding: "2px 8px",
        borderRadius: 999,
        border: "1px solid #ddd",
        background: "#f7f7f7",
        fontSize: 12,
        lineHeight: "18px",
        whiteSpace: "nowrap",
      }}
    >
      {children}
    </span>
  );
}
