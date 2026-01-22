import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../api/publicApi";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import Badge from "../components/Badge";
import { groupByTime } from "../utils/groupByTime";


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

export default function EquipeDetail() {
  const { id } = useParams();
  const equipeId = Number(id);

  const equipeQ = useQuery({
    queryKey: ["equipe", id],
    queryFn: () => publicApi.equipeDetail(id),
  });

  const matchsQ = useQuery({
    queryKey: ["planning", { equipe: id }],
    queryFn: () => publicApi.planning({ equipe: id }),
  });

  if (equipeQ.isLoading || matchsQ.isLoading) return <Loading />;
  if (equipeQ.isError) return <ErrorState error={equipeQ.error} />;
  if (matchsQ.isError) return <ErrorState error={matchsQ.error} />;

  const equipe = equipeQ.data;

  const rawMatchs = Array.isArray(matchsQ.data) ? matchsQ.data : [];
  const matchs = rawMatchs.filter(
    (m) => m.equipe_a_id === equipeId || m.equipe_b_id === equipeId
  );

  const joueurs = Array.isArray(equipe?.joueurs) ? equipe.joueurs : [];

  return (
    <div className="stack">
      <div className="card">
        <div className="title">{equipe?.nom ?? `Équipe #${id}`}</div>

        <div className="muted" style={{ marginTop: 6 }}>
          {equipe?.nom_club ? `Club : ${equipe.nom_club}` : null}
          {equipe?.tournoi ? ` · Tournoi : ${equipe.tournoi}` : null}
          {equipe?.groupe_code ? ` · Groupe : ${equipe.groupe_code}` : null}
        </div>

        <div style={{ marginTop: 10, display: "flex", gap: 10, flexWrap: "wrap" }}>
          {equipe?.statut ? <Badge variant="info">{equipe.statut}</Badge> : null}
          <Link to="/groupes">← Retour groupes</Link>
          <span className="muted">·</span>
          <Link to={`/planning?equipe=${id}`}>Voir dans Planning</Link>
        </div>
      </div>

      <div className="card">
        <div className="title">Joueurs</div>

        {joueurs.length === 0 ? (
          <EmptyState label="Aucun joueur." />
        ) : (
          <ul className="list">
            {joueurs.map((j) => (
              <li key={j.id} className="row">
                <span className="muted">#{j.id}</span>
                <span>{j.prenom} {j.nom}</span>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="card">
        <div className="title">Matchs</div>

        {matchs.length === 0 ? (
          <EmptyState label="Aucun match trouvé pour cette équipe." />
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
                <div>{m.equipe_a} vs {m.equipe_b}</div>
                <div className="muted">{m.terrain}</div>
                <div className="muted">
                  {m.debut ? timeFormatter.format(new Date(m.debut)) : "—"}
                </div>
                <div className="muted">
                  {m.score ? `${m.score.points_a} - ${m.score.points_b}` : "—"}{" "}
                  {m.score?.valide_le ? (
                    <Badge variant="success">VALIDÉ</Badge>
                  ) : m.score ? (
                    <Badge variant="danger">NON VALIDÉ</Badge>
                  ) : null}
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
