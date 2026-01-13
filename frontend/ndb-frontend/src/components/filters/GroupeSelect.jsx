export default function GroupeSelect({ groupes, value, onChange }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span>Groupe</span>
      <select value={value || ""} onChange={(e) => onChange(e.target.value)}>
        <option value="">—</option>
        {groupes.map((g) => (
          <option key={g.id} value={g.id}>
            {g.nom || `Groupe ${g.id}`}
          </option>
        ))}
      </select>
    </label>
  );
}
