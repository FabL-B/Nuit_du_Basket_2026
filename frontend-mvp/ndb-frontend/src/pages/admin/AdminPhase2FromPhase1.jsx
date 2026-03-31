import { useMemo } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";

export default function AdminPhase2FromPhase1() {
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
  const phase2 = phases.find((p) => p.type_phase === "PHASE_2") ?? null;

  const previewQ = useQuery({
    queryKey: ["admin-phase2-preview", phase1?.id],
    queryFn: () => adminApi.phase2Preview(phase1.id),
    enabled: !!phase1?.id,
  });

  const cloturerM = useMutation({
    mutationFn: () => adminApi.cloturerPhase(phase1.id),
    onSuccess: () => {
      phasesQ.refetch();
      previewQ.refetch();
    },
  });

  const genererPhase2M = useMutation({
    mutationFn: () => adminApi.phase2Generer(phase1.id),
    onSuccess: () => {
      phasesQ.refetch();
      previewQ.refetch();
    },
  });

  // returns après hooks
  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;
  if (!editionId) return <EmptyState label="Aucune édition active." />;

  if (phasesQ.isLoading) return <Loading />;
  if (phasesQ.isError) return <ErrorState error={phasesQ.error} />;
  if (!phase1) return <EmptyState label="Phase 1 introuvable. Crée-la d’abord." />;

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Phase 2 — Génération depuis Phase 1</div>

        <div className="filters">
          <AdminEditionSelect editions={editions} value={editionId} onChange={setActiveEditionId} />
          <Badge variant="info">Phase1 #{phase1.id}</Badge>
          {phase2 ? <Badge variant="info">Phase2 #{phase2.id}</Badge> : <Badge variant="warning">Phase2 non créée</Badge>}
        </div>

        <div className="filters" style={{ marginTop: 8 }}>
          <button className="btn" onClick={() => cloturerM.mutate()} disabled={cloturerM.isLoading}>
            1) Clôturer Phase 1
          </button>

          <button
            className="btn"
            onClick={() => previewQ.refetch()}
            disabled={previewQ.isFetching}
          >
            2) Rafraîchir preview Phase 2
          </button>

          <button
            className="btn"
            onClick={() => genererPhase2M.mutate()}
            disabled={genererPhase2M.isLoading}
          >
            3) Générer Phase 2
          </button>
        </div>

        {cloturerM.isError ? <ErrorState error={cloturerM.error} /> : null}
        {genererPhase2M.isError ? <ErrorState error={genererPhase2M.error} /> : null}
      </div>

      <div className="card">
        <div className="title">Preview Phase 2</div>

        {previewQ.isLoading || previewQ.isFetching ? (
          <Loading />
        ) : previewQ.isError ? (
          <ErrorState error={previewQ.error} />
        ) : !previewQ.data ? (
          <EmptyState label="Aucune preview. Clique “Rafraîchir preview Phase 2”." />
        ) : (
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(previewQ.data, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
