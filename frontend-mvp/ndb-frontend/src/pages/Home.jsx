import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../api/publicApi";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import Badge from "../components/Badge";

const dateFormatter = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
});


function List({ title, items }) {
  return (
    <div className="card">
      <div className="title">{title}</div>
      {!items || items.length === 0 ? (
        <EmptyState />
      ) : (
        <ul className="list">
          {items.map((m) => (
            <li key={m.match_id} className="row">
              <span className="muted">#{m.match_id}</span>

              <span>
                {m.equipe_a ?? `#${m.equipe_a_id}`} vs {m.equipe_b ?? `#${m.equipe_b_id}`}
              </span>

              <span className="muted">{m.terrain ?? `#${m.terrain_id}`}</span>

              <span className="muted">
                {m.debut ? dateFormatter.format(new Date(m.debut)) : "—"}
              </span>

              <span className="muted">
                {m.score ? `${m.score.points_a} - ${m.score.points_b}` : "—"}
              </span>

              {m.score?.valide_le ? (
                <Badge variant="success">VALIDÉ</Badge>
              ) : m.score ? (
                <Badge variant="danger">NON VALIDÉ</Badge>
              ) : null}

              <Badge variant={statutVariant(m.statut)}>{m.statut}</Badge>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function statutVariant(statut) {
  if (statut === "EN_COURS") return "warning";
  if (statut === "A_VENIR") return "info";
  if (statut === "TERMINE") return "default";
  return "default";
}

export default function Home() {
  const planning = useQuery({
    queryKey: ["planning", { limit: 50 }],
    queryFn: () => publicApi.planning({ limit: 50 }),
  });

  if (planning.isLoading) return <Loading />;
  if (planning.isError) return <ErrorState error={planning.error} />;

  // ton API renvoie une liste brute => pas de .results
  const items = Array.isArray(planning.data) ? planning.data : [];

  const validated = items.filter((m) => !!m.score?.valide_le).slice(0, 5);
  const latest = items.slice(0, 5);

  return (
    <div className="grid">
      <List title="Derniers matchs (validés)" items={validated} />
      <List title="Derniers matchs" items={latest} />
    </div>
  );
}
