function isPrimitive(v) {
  return v === null || ["string", "number", "boolean"].includes(typeof v);
}

function formatCell(value) {
  if (isPrimitive(value)) return String(value ?? "");
  // objets/listes: on stringify mais court
  const s = JSON.stringify(value);
  return s.length > 120 ? s.slice(0, 120) + "…" : s;
}

export default function DataTable({ items, columns, getRowKey }) {
  if (!items?.length) return null;

  // Colonnes auto si pas fournies
  const autoColumns =
    columns ||
    Object.keys(items[0] || {}).slice(0, 8).map((k) => ({ key: k, label: k }));

  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            {autoColumns.map((col) => (
              <th
                key={col.key}
                style={{
                  textAlign: "left",
                  padding: "8px 10px",
                  borderBottom: "1px solid #ddd",
                  fontSize: 13,
                  whiteSpace: "nowrap",
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {items.map((row, idx) => (
            <tr key={getRowKey ? getRowKey(row) : row.id ?? idx}>
              {autoColumns.map((col) => (
                <td
                  key={col.key}
                  style={{
                    padding: "8px 10px",
                    borderBottom: "1px solid #eee",
                    fontSize: 13,
                    verticalAlign: "top",
                  }}
                >
                  {col.render ? col.render(row) : formatCell(row[col.key])}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
