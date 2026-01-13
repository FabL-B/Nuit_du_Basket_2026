import { useEffect, useState } from "react";
import { fetchPlanning } from "../../api/public";
import { normalizeListResponse } from "../../utils/normalize";
import DataTable from "../tables/DataTable";
import { formatParisDateTime } from "../../utils/datetime";
import Badge from "../ui/Badge";
import { groupByTimeSlot } from "../../utils/groupBySlot";


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
        const list = normalizeListResponse(data)
          .slice()
          .sort((a, b) => new Date(a.debut) - new Date(b.debut));
        setItems(list);
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
  const groups = groupByTimeSlot(items, 15);

  return (
    <div style={{ padding: 12, border: "1px solid #ddd", borderRadius: 12 }}>
      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2 style={{ margin: 0 }}>Planning</h2>
        <span style={{ fontSize: 12, opacity: 0.7 }}>
          {count !== null ? `Total : ${count}` : `Lignes : ${items.length}`}
        </span>
      </div>

      {groups.map(({ slot, items }) => (
        <div key={slot} style={{ marginTop: 16 }}>
          <h3 style={{ margin: "8px 0" }}>
            {new Date(slot).toLocaleTimeString("fr-FR", {
              hour: "2-digit",
              minute: "2-digit",
            })}
          </h3>

          <DataTable
            items={items}
            getRowKey={(r) => r.match_id}
            columns={[
              {
                key: "match",
                label: "Match",
                render: (r) => `${r.equipe_a} vs ${r.equipe_b}`,
              },
              { key: "terrain", label: "Terrain" },
              {
                key: "ctx",
                label: "Contexte",
                render: (r) => (
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    <span>{r.tournoi}</span>
                    <span>{r.phase}</span>
                    <span>Groupe {r.groupe}</span>
                  </div>
                ),
              },
              {
                key: "score",
                label: "Score",
                render: (r) => (r.score ? "Saisi" : "—"),
              },
            ]}
          />
        </div>
      ))}
    </div>
  );
}
