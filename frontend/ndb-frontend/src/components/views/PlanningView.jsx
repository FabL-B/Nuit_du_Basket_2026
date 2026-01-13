export default function PlanningView({ params }) {
  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
      <h2 style={{ marginTop: 0 }}>Planning</h2>

      <p>Cette vue affichera le planning.</p>

      <p style={{ fontSize: 12, opacity: 0.7 }}>
        Params reçus : <code>{JSON.stringify(params)}</code>
      </p>
    </div>
  );
}
