import { useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../api/publicApi";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import { Link } from "react-router-dom";

const timeFormatter = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
});

export default function GroupeDetail() {
  const { id } = useParams();

  const groupeQuery = useQuery({
    queryKey: ["groupe", id],
    queryFn: () => publicApi.groupeDetail(id),
  });

  const matchsQuery = useQuery({
    queryKey: ["planning", { groupe: id }],
    queryFn: () => publicApi.planning({ groupe: id }),
  });

  if (groupeQuery.isLoading || matchsQuery.isLoading) return <Loading />;
  if (groupeQuery.isError) return <ErrorState error={groupeQuery.error} />;
  if (matchsQuery.isError) return <ErrorState error={matchsQuery.error} />;

  const groupe = groupeQuery.data;
  const matchs = Array.isArray(matchsQuery.data) ? matchsQuery.data : [];

  return (
    <div className="stack">
      {/* Infos groupe */}
      <div className="card">
        <div className="title">{groupe.nom}</div>
        <div className="muted">
          Tournoi : {groupe.tournoi?.nom ?? "—"} · Phase : {groupe.phase_globale?.type_phase ?? "—"}
        </div>
      </div>

      {/* Équipes */}
      <div className="card">
        <div className="title">Équipes</div>

        {!groupe.equipes || groupe.equipes.length === 0 ? (
          <EmptyState label="Aucune équipe dans ce groupe." />
        ) : (
          <ul className="list">
            {groupe.equipes.map((e) => (
              <li key={e.id} className="row">
                <span className="muted">#{e.id}</span>
                <span>
                  <Link to={`/equipes/${e.id}`}>{e.nom}</Link>
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Matchs du groupe */}
      <div className="card">
        <div className="title">Matchs du groupe</div>

        {matchs.length === 0 ? (
          <EmptyState label="Aucun match pour ce groupe." />
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

            {matchs.map((m) => (
              <div className="trow" key={m.match_id}>
                <div className="muted">{m.match_id}</div>
                <div>
                  {m.equipe_a} vs {m.equipe_b}
                </div>
                <div className="muted">{m.terrain}</div>
                <div className="muted">
                  {m.debut ? timeFormatter.format(new Date(m.debut)) : "—"}
                </div>
                <div className="muted">
                  {m.score ? `${m.score.points_a} - ${m.score.points_b}` : "—"}
                </div>
                <div className="muted">{m.statut}</div>
              </div>
            ))}
          </div>
        )}

        <div style={{ marginTop: 12 }}>
          <Link to={`/planning?groupe=${id}`}>Voir dans le planning global</Link>
        </div>
      </div>
    </div>
  );
}
