import { useMemo } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";

export default function AdminPhase2Planning() {
  const { editionsQ, editions, activeEditionId, setActiveEditionId } = useActiveEdition();
  const editionId = activeEditionId;

  const phasesQ = useQuery({
    queryKey: ["admin-phases-globales", editionId],
    queryFn: () => adminApi.phasesGlobales({ edition: editionId }),
    enabled: !!editionId,
  });

  const phases = useMemo(() => {
    const d = phasesQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [phasesQ.data]);

  const phase2 = phases.find((p) => p.type_phase === "PHASE_2") ?? null;

  const planningQ = useQuery({
    queryKey: ["admin-planning", editionId, "PHASE_2"],
    queryFn: () => adminApi.planning({ edition: editionId, phase: "PHASE_2" }),
    enabled: !!editionId,
  });

  const planning = useMemo(() => {
    const d = planningQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [planningQ.data]);

  const genPlanningM = useMutation({
    mutationFn: () => adminApi.genererPlanningPhase(phase2.id),
    onSuccess: () => planningQ.refetch(),
  });

  // returns après hooks
  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;
  if (!editionId) return <EmptyState label="Aucune édition active." />;

  if (phasesQ.isLoading) return <Loading />;
  if (phasesQ.isError) return <ErrorState error={phasesQ.error} />;
  if (!phase2) return <EmptyState label="Phase 2 introuvable." />;

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Phase 2 — Planning</div>

        <div className="filters">
          <AdminEditionSelect
            editions={editions}
            value={editionId}
            onChange={setActiveEditionId}
          />
          <Badge variant="info">Phase2 #{phase2.id}</Badge>

          <button
            className="btn"
            onClick={() => genPlanningM.mutate()}
            disabled={genPlanningM.isLoading}
          >
            Générer le planning
          </button>
        </div>

        {genPlanningM.isError ? <ErrorState error={genPlanningM.error} /> : null}
      </div>

      <div className="card">
        <div className="title">Planning généré</div>

        {planningQ.isLoading ? (
          <Loading />
        ) : planningQ.isError ? (
          <ErrorState error={planningQ.error} />
        ) : planning.length === 0 ? (
          <EmptyState label="Planning vide. Clique sur Générer." />
        ) : (
          <ul className="list">
            {planning.map((m) => (
              <li key={m.match_id} className="row">
                <span className="muted">#{m.match_id}</span>
                <span>{m.equipe_a} vs {m.equipe_b}</span>
                <span className="muted">Terrain {m.terrain ?? "—"}</span>
                <span className="muted">
                  {m.debut ? new Date(m.debut).toLocaleTimeString("fr-FR", { timeZone: "Europe/Paris", hour: "2-digit", minute: "2-digit" }) : "—"}
                </span>
                <span className="muted">{m.statut_match ?? ""}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
