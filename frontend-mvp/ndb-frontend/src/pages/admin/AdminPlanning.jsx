import { useMemo, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";

const timeFormatter = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
});

function statutVariant(statut) {
  if (statut === "EN_COURS") return "warning";
  if (statut === "A_VENIR") return "info";
  if (statut === "TERMINE") return "default";
  return "default";
}

export default function AdminPlanning() {
  const editionsQ = useQuery({
    queryKey: ["admin-editions"],
    queryFn: () => adminApi.editions(),
  });

  const editions = useMemo(() => {
    const d = editionsQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [editionsQ.data]);

  const [editionId, setEditionId] = useState(null);

  const planningQ = useQuery({
    queryKey: ["admin-planning", editionId],
    queryFn: () => adminApi.planning({ edition: editionId }),
    enabled: !!editionId,
  });

  const generateM = useMutation({
    mutationFn: (payload) => adminApi.planningGenerer(payload),
    onSuccess: () => {
      planningQ.refetch();
    },
  });

  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;

  const selectedEditionId = editionId ?? editions?.[0]?.id ?? null;

  function onGenerate() {
    if (!selectedEditionId) return;
    generateM.mutate({ edition_id: selectedEditionId });
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Admin — Planning</div>

        <div className="filters">
          <select
            value={selectedEditionId ?? ""}
            onChange={(e) => setEditionId(Number(e.target.value))}
          >
            {editions.map((ed) => (
              <option key={ed.id} value={ed.id}>
                {ed.nom ?? `Edition #${ed.id}`}
              </option>
            ))}
          </select>

          <button className="btn" onClick={onGenerate} disabled={generateM.isLoading}>
            Générer planning
          </button>
        </div>

        {generateM.isError ? <ErrorState error={generateM.error} /> : null}
      </div>

      <div className="card">
        <div className="title">Planning (admin)</div>

        {!selectedEditionId ? (
          <EmptyState label="Sélectionne une édition." />
        ) : planningQ.isLoading ? (
          <Loading />
        ) : planningQ.isError ? (
          <ErrorState error={planningQ.error} />
        ) : (
          <div className="table">
            <div className="thead">
              <div>ID</div>
              <div>Match</div>
              <div>Terrain</div>
              <div>Heure</div>
              <div>Score</div>
              <div>Statut</div>
            </div>

            {(Array.isArray(planningQ.data) ? planningQ.data : []).map((m) => (
              <div className="trow" key={m.id}>
                <div className="muted">{m.id}</div>
                <div>{m.equipe_a?.nom} vs {m.equipe_b?.nom}</div>
                <div className="muted">{m.terrain?.nom}</div>
                <div className="muted">
                  {m.creneau?.debut
                    ? timeFormatter.format(new Date(m.creneau.debut))
                    : "—"}
                </div>
                <div className="muted">
                  {m.score_equipe_a != null
                    ? `${m.score_equipe_a} - ${m.score_equipe_b}`
                    : "—"}
                </div>
                <div>
                  <Badge variant={statutVariant(m.statut)}>{m.statut}</Badge>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
