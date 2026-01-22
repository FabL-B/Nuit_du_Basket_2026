export default function EmptyState({ label = "Aucun résultat." }) {
  return <div className="card">{label}</div>;
}
