import { useMemo, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";

const timeFmt = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
});

function parseApiError(err) {
  const status = err?.response?.status;
  const data = err?.response?.data;
  if (!status) return "Erreur inconnue.";
  return `HTTP ${status} ${data ? JSON.stringify(data) : ""}`;
}

export default function AdminPhase2Scores() {
  const { editionsQ, editions, activeEditionId, setActiveEditionId } = useActiveEdition();
  const editionId = activeEditionId;

  const planningQ = useQuery({
    queryKey: ["admin-planning", editionId, "PHASE_2"],
    queryFn: () => adminApi.planning({ edition: editionId, phase: "PHASE_2" }),
    enabled: !!editionId,
  });

  const items = useMemo(() => {
    const d = planningQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [planningQ.data]);

  const matchsSaisissables = useMemo(() => {
    return items.filter(
      (m) => m.statut_match !== "TERMINE"
    );
  }, [items]);

  const [selectedMatchId, setSelectedMatchId] = useState(null);
  const selected = items.find((m) => m.match_id === selectedMatchId) ?? null;

  const [pointsA, setPointsA] = useState("");
  const [pointsB, setPointsB] = useState("");

  const saisirM = useMutation({
    mutationFn: ({ matchId, payload }) => adminApi.saisirScore(matchId, payload),
    onSuccess: () => {
      planningQ.refetch();
    },
  });

  const validerM = useMutation({
    mutationFn: (matchId) => adminApi.validerScore(matchId),
    onSuccess: () => {
      planningQ.refetch();
      setSelectedMatchId(null);
    },
  });

  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;
  if (!editionId) return <EmptyState label="Aucune édition active." />;

  return (
    <div className="grid" style={{ gridTemplateColumns: "1.3fr 1fr", gap: 14 }}>
      <div className="card">
        <div className="title">Phase 2 — Scores</div>

        <div className="filters">
          <AdminEditionSelect editions={editions} value={editionId} onChange={setActiveEditionId} />
        </div>

        {planningQ.isLoading ? (
          <Loading />
        ) : planningQ.isError ? (
          <ErrorState error={planningQ.error} />
        ) : matchsSaisissables.length === 0 ? (
          <EmptyState label="Tous les matchs sont terminés." />
        ) : (
          <ul className="list">
            {matchsSaisissables.map((m) => (
              <li
                key={m.match_id}
                className="row"
                style={{ cursor: "pointer", alignItems: "center" }}
                onClick={() => {
                  setSelectedMatchId(m.match_id);
                  setPointsA("");
                  setPointsB("");
                }}
              >
                <span className="muted">#{m.match_id}</span>
                <span>{m.equipe_a} vs {m.equipe_b}</span>
                <span className="muted">T {m.terrain ?? "—"}</span>
                <span className="muted">{m.debut ? timeFmt.format(new Date(m.debut)) : "—"}</span>
                <Badge variant={m.statut_match === "PLANIFIE" ? "info" : "warning"}>
                  {m.statut_match ?? "?"}
                </Badge>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <div className="title">Saisie / Validation</div>

        {!selected ? (
          <EmptyState label="Sélectionne un match à gauche." />
        ) : (
          <>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
              <Badge variant="info">#{selected.match_id}</Badge>
              <div style={{ fontWeight: 700 }}>
                {selected.equipe_a} vs {selected.equipe_b}
              </div>
              <div className="muted">
                Terrain {selected.terrain ?? "—"} • {selected.debut ? timeFmt.format(new Date(selected.debut)) : "—"}
              </div>
            </div>

            <div className="filters" style={{ marginTop: 12 }}>
              <input
                type="number"
                min="0"
                placeholder={`Points ${selected.equipe_a}`}
                value={pointsA}
                onChange={(e) => setPointsA(e.target.value)}
              />
              <input
                type="number"
                min="0"
                placeholder={`Points ${selected.equipe_b}`}
                value={pointsB}
                onChange={(e) => setPointsB(e.target.value)}
              />

              <button
                className="btn"
                disabled={saisirM.isLoading || pointsA === "" || pointsB === ""}
                onClick={() =>
                  saisirM.mutate({
                    matchId: selected.match_id,
                    payload: { points_a: Number(pointsA), points_b: Number(pointsB) },
                  })
                }
              >
                Saisir score
              </button>

              <button
                className="btn"
                disabled={validerM.isLoading}
                onClick={() => validerM.mutate(selected.match_id)}
              >
                Valider score
              </button>
            </div>

            {(saisirM.isError || validerM.isError) && (
              <div className="muted" style={{ marginTop: 10 }}>
                {parseApiError(saisirM.error || validerM.error)}
              </div>
            )}

            {(saisirM.data || validerM.data) && (
              <pre style={{ marginTop: 10, whiteSpace: "pre-wrap" }}>
                {JSON.stringify(saisirM.data || validerM.data, null, 2)}
              </pre>
            )}
          </>
        )}
      </div>
    </div>
  );
}
