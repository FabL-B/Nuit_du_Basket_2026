import { useEffect, useState } from "react";
import { fetchEditions } from "../api/public";

export default function Home() {
  const [editions, setEditions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEditions()
      .then((data) => {
        setEditions(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h2>Éditions</h2>

      {loading && <p>Chargement…</p>}
      {error && <p style={{ color: "red" }}>Erreur : {error}</p>}

      {!loading && !error && (
        <ul>
          {editions.map((edition) => (
            <li key={edition.id}>
              {edition.nom} (id={edition.id})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
