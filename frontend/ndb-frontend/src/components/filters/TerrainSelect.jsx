export default function TerrainSelect({ terrains, value, onChange }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span>Terrain</span>
      <select value={value || ""} onChange={(e) => onChange(e.target.value)}>
        <option value="">—</option>
        {terrains.map((t) => (
          <option key={t.id} value={t.id}>
            {t.nom}
          </option>
        ))}
      </select>
    </label>
  );
}
