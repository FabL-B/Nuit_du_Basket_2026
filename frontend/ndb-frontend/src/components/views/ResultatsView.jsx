import { useEffect, useState } from "react";
import { fetchResultats } from "../../api/public";

export default function ResultatsView({ params }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchResultats(params)
      .then((data) => {
        setItems(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [params]);

  if (loading) return <p>Chargement des résultats…</p>;
  if (error) return <p style={{ color: "red" }}>Erreur : {error}</p>;
  if (!items.length) return <p>Aucun résultat.</p>;

  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
      <h2 style={{ marginTop: 0 }}>Résultats</h2>

      <ul>
        {items.map((item) => (
          <li key={item.id}>Résultat #{item.id}</li>
        ))}
      </ul>
    </div>
  );
}
