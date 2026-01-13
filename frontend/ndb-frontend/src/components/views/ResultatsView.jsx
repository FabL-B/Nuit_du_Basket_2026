export default function ResultatsView({ params }) {
  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
      <h2 style={{ marginTop: 0 }}>Résultats</h2>

      <p>Cette vue affichera les résultats.</p>

      <p style={{ fontSize: 12, opacity: 0.7 }}>
        Params reçus : <code>{JSON.stringify(params)}</code>
      </p>
    </div>
  );
}
