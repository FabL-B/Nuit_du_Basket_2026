export default function ErrorState({ error }) {
  return (
    <div className="card error">
      <div className="title">Erreur</div>
      <pre className="pre">{JSON.stringify(error, null, 2)}</pre>
    </div>
  );
}
