import { useEffect, useState } from "react";
import { fetchResultats } from "../../api/public";
import { normalizeListResponse } from "../../utils/normalize";
import DataTable from "../tables/DataTable";
import { formatParisDateTime } from "../../utils/datetime";


export default function ResultatsView({ params }) {
  const [items, setItems] = useState([]);
  const [rawCount, setRawCount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);

    fetchResultats(params)
      .then((data) => {
        setRawCount(typeof data?.count === "number" ? data.count : null);
        setItems(normalizeListResponse(data));
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [JSON.stringify(params)]);

  if (loading) return <p>Chargement des résultats…</p>;
  if (error) return <p style={{ color: "red" }}>Erreur : {error}</p>;
  if (!items.length) return <p>Aucun résultat.</p>;

  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 12, flexWrap: "wrap" }}>
        <h2 style={{ margin: 0 }}>Résultats</h2>
        <div style={{ fontSize: 12, opacity: 0.75 }}>
          {rawCount !== null ? `Total: ${rawCount}` : `Lignes: ${items.length}`}
        </div>
      </div>

      <div style={{ marginTop: 12 }}>
        <DataTable
          items={items}
          getRowKey={(r) => r.match_id}
          columns={[
            {
              key: "debut",
              label: "Heure",
              render: (r) => formatParisDateTime(r.debut),
            },
            { key: "terrain", label: "Terrain" },
            { key: "tournoi", label: "Tournoi" },
            { key: "phase", label: "Phase" },
            { key: "groupe", label: "Groupe" },
            {
              key: "match",
              label: "Match",
              render: (r) => `${r.equipe_a} vs ${r.equipe_b}`,
            },
            {
              key: "score",
              label: "Score",
              render: (r) => {
                if (!r.score) return "—";
                const { points_a, points_b } = r.score;
                return `${points_a} - ${points_b}`;
              },
            },
          ]}
        />
      </div>
    </div>
  );
}
