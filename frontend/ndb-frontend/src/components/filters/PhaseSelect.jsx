const PHASES = [
  { value: "PHASE_1", label: "Phase 1" },
  { value: "PHASE_2", label: "Phase 2" },
  { value: "FINALE", label: "Finale" },
];

export default function PhaseSelect({ value, onChange }) {
  return (
    <label style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <span>Phase</span>
      <select value={value || ""} onChange={(e) => onChange(e.target.value)}>
        <option value="">—</option>
        {PHASES.map((p) => (
          <option key={p.value} value={p.value}>
            {p.label}
          </option>
        ))}
      </select>
    </label>
  );
}
