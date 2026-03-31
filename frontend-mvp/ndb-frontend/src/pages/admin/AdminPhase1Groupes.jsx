import { useMemo } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";


export default function AdminPhase1Groupes() {
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

  const sousPhasesQ = useQuery({
    queryKey: ["admin-sous-phases", phase1?.id],
    queryFn: () => adminApi.sousPhases({ phase_globale: phase1.id }),
    enabled: !!phase1?.id,
  });

  const sousPhases = useMemo(() => {
    const d = sousPhasesQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [sousPhasesQ.data]);

  const groupesQ = useQuery({
    queryKey: ["admin-groupes", editionId],
    queryFn: () => adminApi.groupes({ edition: editionId }),
    enabled: !!editionId,
  });

  const groupes = useMemo(() => {
    const d = groupesQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [groupesQ.data]);

  const genSousPhasesM = useMutation({
    mutationFn: () => adminApi.genererSousPhases(phase1.id),
    onSuccess: () => {
      sousPhasesQ.refetch();
      groupesQ.refetch();
    },
  });

  const genGroupesM = useMutation({
    mutationFn: (sousPhaseId) => adminApi.genererGroupesPhase1(sousPhaseId),
    onSuccess: () => {
      groupesQ.refetch();
      sousPhasesQ.refetch();
    },
  });

    const tournoisQ = useQuery({
    queryKey: ["admin-tournois", editionId],
    queryFn: () => adminApi.tournois({ edition: editionId }),
    enabled: !!editionId,
    });

    const tournois = useMemo(() => {
    const d = tournoisQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
    }, [tournoisQ.data]);

    const tournoisById = useMemo(() => {
    const m = new Map();
    for (const t of tournois) m.set(t.id, t);
    return m;
    }, [tournois]);

    const createPhase1M = useMutation({
    mutationFn: () =>
        adminApi.createPhaseGlobale({
        edition: editionId,
        type_phase: "PHASE_1",
        sequence: 1,
        statut: "OUVERTE",
        }),
    onSuccess: () => phasesQ.refetch(),
    });

  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;

  if (!editionId) {
    return (
      <div className="card">
        <div className="title">Admin — Phase 1 / Groupes</div>
        <EmptyState label="Aucune édition active. Sélectionne une édition dans Admin Édition." />
      </div>
    );
  }

  if (phasesQ.isLoading) return <Loading />;
  if (phasesQ.isError) return <ErrorState error={phasesQ.error} />;

    if (!phase1) {
    return (
        <div className="stack">
        <div className="card">
            <div className="title">Admin — Phase 1</div>
            <div className="muted">
            Aucune PhaseGlobale PHASE_1 pour l’édition #{editionId}.
            </div>

            <div style={{ marginTop: 10 }}>
            <button
                className="btn"
                onClick={() => createPhase1M.mutate()}
                disabled={createPhase1M.isLoading}
            >
                Créer la Phase 1
            </button>
            </div>

            {createPhase1M.isError ? <ErrorState error={createPhase1M.error} /> : null}
        </div>
        </div>
    );
    }

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Admin — Phase 1</div>
        <div className="filters">
          <AdminEditionSelect
            editions={editions}
            value={editionId}
            onChange={setActiveEditionId}
          />
        </div>
      </div>
      <div className="card">
        <div className="title">Phase 1 — Groupes</div>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
          <Badge variant="info">Édition #{editionId}</Badge>
          <Badge variant="info">Phase1 #{phase1.id}</Badge>

          <button
            className="btn"
            onClick={() => genSousPhasesM.mutate()}
            disabled={genSousPhasesM.isLoading}
          >
            Générer sous-phases
          </button>
        </div>

        {genSousPhasesM.isError ? <ErrorState error={genSousPhasesM.error} /> : null}
      </div>

      <div className="card">
        <div className="title">Sous-phases</div>

        {sousPhasesQ.isLoading ? (
          <Loading />
        ) : sousPhasesQ.isError ? (
          <ErrorState error={sousPhasesQ.error} />
        ) : sousPhases.length === 0 ? (
          <EmptyState label="Aucune sous-phase. Clique 'Générer sous-phases'." />
        ) : (
            <ul className="list">
            {sousPhases.map((sp) => (
                <li key={sp.id} className="row" style={{ alignItems: "center" }}>
                <span style={{ fontWeight: 700 }}>
                    {tournoisById.get(sp.tournoi)?.code ?? `Tournoi #${sp.tournoi}`}
                </span>
                {/* Afficher la branche seulement si elle existe vraiment */}
                {sp.branche && sp.branche !== "AUCUNE" && (
                    <span className="muted">Branche : {sp.branche}</span>
                )}

                <button
                    className="btn"
                    onClick={() => genGroupesM.mutate(sp.id)}
                    disabled={genGroupesM.isLoading}
                >
                    Générer groupes
                </button>
                </li>
            ))}
            </ul>
        )}

        {genGroupesM.isError ? <ErrorState error={genGroupesM.error} /> : null}
      </div>

      <div className="card">
        <div className="title">Groupes existants</div>

        {groupesQ.isLoading ? (
          <Loading />
        ) : groupesQ.isError ? (
          <ErrorState error={groupesQ.error} />
        ) : groupes.length === 0 ? (
          <EmptyState label="Aucun groupe pour l’instant." />
        ) : (
          <ul className="list">
            {groupes.map((g) => (
              <li key={g.id} className="row">
                <span className="muted">#{g.id}</span>
                <span>{g.nom ?? g.code ?? "Groupe"}</span>
                <span className="muted">{g.tournoi?.code ?? g.tournoi ?? ""}</span>
                <span className="muted">{g.phase_globale?.type_phase ?? ""}</span>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
