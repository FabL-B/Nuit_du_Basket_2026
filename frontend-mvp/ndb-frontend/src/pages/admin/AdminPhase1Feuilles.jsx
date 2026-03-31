import { useMemo, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";

const timeFmt = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
});

export default function AdminPhase1Feuilles() {
  const { editionsQ, editions, activeEditionId, setActiveEditionId } = useActiveEdition();
  const editionId = activeEditionId;

  const planningQ = useQuery({
    queryKey: ["admin-planning", editionId, "PHASE_1"],
    queryFn: () => adminApi.planning({ edition: editionId, phase: "PHASE_1" }),
    enabled: !!editionId,
  });

  const items = useMemo(() => {
    const d = planningQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [planningQ.data]);

  const [selected, setSelected] = useState(null);

  const feuilleM = useMutation({
    mutationFn: (matchId) => adminApi.feuilleMatch(matchId),
    onSuccess: (data) => setSelected(data),
  });

  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;
  if (!editionId) return <EmptyState label="Aucune édition active." />;

  return (
    <div className="grid" style={{ gridTemplateColumns: "1.2fr 1fr", gap: 14 }}>
      <div className="card">
        <div className="title">Phase 1 — Feuilles de match</div>

        <div className="filters">
          <AdminEditionSelect
            editions={editions}
            value={editionId}
            onChange={setActiveEditionId}
          />
        </div>

        {planningQ.isLoading ? (
          <Loading />
        ) : planningQ.isError ? (
          <ErrorState error={planningQ.error} />
        ) : items.length === 0 ? (
          <EmptyState label="Aucun match planifié." />
        ) : (
          <ul className="list">
            {items.map((m) => (
              <li key={m.match_id} className="row" style={{ alignItems: "center" }}>
                <span className="muted">#{m.match_id}</span>
                <span>{m.equipe_a} vs {m.equipe_b}</span>
                <span className="muted">Terrain {m.terrain ?? "—"}</span>
                <span className="muted">
                  {m.debut ? timeFmt.format(new Date(m.debut)) : "—"}
                </span>

                <button
                  className="btn"
                  onClick={() => feuilleM.mutate(m.match_id)}
                  disabled={feuilleM.isLoading}
                >
                  Générer / ouvrir
                </button>
              </li>
            ))}
          </ul>
        )}

        {feuilleM.isError ? <ErrorState error={feuilleM.error} /> : null}
      </div>

      <div className="card">
        <div className="title">Feuille</div>

        {!selected ? (
          <EmptyState label="Clique sur “Générer / ouvrir” sur un match." />
        ) : (
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(selected, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
