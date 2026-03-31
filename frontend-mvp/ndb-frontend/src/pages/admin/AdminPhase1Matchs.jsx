import { useMemo } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";

export default function AdminPhase1Matchs() {
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

  const phase1 = phases.find((p) => p.type_phase === "PHASE_1") ?? null;

  const matchsQ = useQuery({
    queryKey: ["admin-matchs", editionId, "PHASE_1"],
    queryFn: () => adminApi.matchs({ edition: editionId, phase: "PHASE_1" }),
    enabled: !!editionId,
  });

  const matchs = useMemo(() => {
    const d = matchsQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [matchsQ.data]);

  const genMatchsM = useMutation({
    mutationFn: () => adminApi.genererMatchsPhase(phase1.id),
    onSuccess: () => matchsQ.refetch(),
  });

  // Returns APRES hooks
  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;
  if (!editionId) return <EmptyState label="Aucune édition active." />;

  if (phasesQ.isLoading) return <Loading />;
  if (phasesQ.isError) return <ErrorState error={phasesQ.error} />;
  if (!phase1) return <EmptyState label="Phase 1 introuvable. Crée-la d’abord." />;

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Phase 1 — Matchs</div>

        <div className="filters">
          <AdminEditionSelect
            editions={editions}
            value={editionId}
            onChange={setActiveEditionId}
          />
          <Badge variant="info">Phase1 #{phase1.id}</Badge>

          <button
            className="btn"
            onClick={() => genMatchsM.mutate()}
            disabled={genMatchsM.isLoading}
          >
            Générer les matchs (Phase 1)
          </button>
        </div>

        {genMatchsM.isError ? <ErrorState error={genMatchsM.error} /> : null}
      </div>

      <div className="card">
        <div className="title">Matchs existants</div>

        {matchsQ.isLoading ? (
          <Loading />
        ) : matchsQ.isError ? (
          <ErrorState error={matchsQ.error} />
        ) : matchs.length === 0 ? (
          <EmptyState label="Aucun match. Clique 'Générer les matchs'." />
        ) : (
          <ul className="list">
            {matchs.map((m) => (
              <li key={m.id} className="row">
                <span className="muted">#{m.id}</span>
                <span>
                  {m.equipe_a_nom ?? `Équipe #${m.equipe_a}`} vs {m.equipe_b_nom ?? `Équipe #${m.equipe_b}`}
                </span>
                <span className="muted">Groupe {m.groupe_code ?? ""}</span>
                <span className="muted">{m.tournoi_code ?? ""}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
