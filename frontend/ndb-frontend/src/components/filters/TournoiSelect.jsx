export default function TournoiSelect({ tournois, value, onChange }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span>Tournoi</span>
      <select value={value || ""} onChange={(e) => onChange(e.target.value)}>
        <option value="">—</option>
        {tournois.map((t) => (
          <option key={t.code} value={t.code}>
            {t.nom}
          </option>
        ))}
      </select>
    </label>
  );
}
