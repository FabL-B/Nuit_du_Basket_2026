export default function AdminEditionSelect({ editions, value, onChange }) {
  return (
    <select value={value ?? ""} onChange={(e) => onChange(Number(e.target.value))}>
      {editions.map((ed) => (
        <option key={ed.id} value={ed.id}>
          {ed.nom ?? `Edition #${ed.id}`}
        </option>
      ))}
    </select>
  );
}
