import { useEffect, useState } from "react";
import { fetchPlanning } from "../../api/public";
import { normalizeListResponse } from "../../utils/normalize";
import DataTable from "../tables/DataTable";

export default function PlanningView({ params }) {
  const [items, setItems] = useState([]);
  const [rawCount, setRawCount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchPlanning(params)
      .then((data) => {
        // support DRF pagination
        setRawCount(typeof data?.count === "number" ? data.count : null);
        setItems(normalizeListResponse(data));
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [JSON.stringify(params)]);

  if (loading) return <p>Chargement du planning…</p>;
  if (error) return <p style={{ color: "red" }}>Erreur : {error}</p>;
  if (!items.length) return <p>Aucun match trouvé.</p>;

  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <h2 style={{ margin: 0 }}>Planning</h2>
        <div style={{ fontSize: 12, opacity: 0.75 }}>
          {rawCount !== null ? `Total: ${rawCount}` : `Lignes: ${items.length}`}
        </div>
      </div>

      <div style={{ marginTop: 12 }}>
        <DataTable items={items} />
      </div>
    </div>
  );
}
