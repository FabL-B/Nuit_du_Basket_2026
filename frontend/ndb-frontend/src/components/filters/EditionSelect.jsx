export default function EditionSelect({ editions, value, onChange }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span>Édition</span>
      <select value={value || ""} onChange={(e) => onChange(e.target.value)}>
        <option value="">—</option>
        {editions.map((ed) => (
          <option key={ed.id} value={ed.id}>
            {ed.nom}
          </option>
        ))}
      </select>
    </label>
  );
}
