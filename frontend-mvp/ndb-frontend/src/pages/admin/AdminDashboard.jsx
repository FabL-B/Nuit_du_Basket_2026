import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";
import { useActiveEdition } from "../../hooks/useActiveEdition";

export default function AdminDashboard() {
  const { editionsQ, editions, activeEditionId, setActiveEditionId } = useActiveEdition();
  const editionId = activeEditionId;

  const statsQ = useQuery({
    queryKey: ["admin-edition-stats", editionId],
    queryFn: () => adminApi.editionStats(editionId),
    enabled: !!editionId,
  });

  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;

  if (!editionId) {
    return (
      <div className="card">
        <div className="title">Admin — Dashboard</div>
        <EmptyState label="Aucune édition disponible." />
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Admin — Dashboard</div>

        <div className="filters">
          <AdminEditionSelect
            editions={editions}
            value={editionId}
            onChange={setActiveEditionId}
          />
        </div>

        <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 6 }}>
          <Link to="/admin/edition">→ 1. Gérer les éditions</Link>
          <Link to="/admin/inscriptions">→ 2. Inscriptions (équipes & joueurs)</Link>
          <Link to="/admin/phase1/groupes">→ 3. Phase 1 : Groupes</Link>
          <Link to="/admin/phase1/matchs">→ 4. Phase 1 : Matchs</Link>
          <Link to="/admin/phase1/planning">→ 5. Phase 1 : Planning</Link>
          <Link to="/admin/phase1/feuilles">→ 6. Phase 1 : Feuilles de match</Link>
          <Link to="/admin/phase1/scores">→ 7. Phase 1 : Scores</Link>
          <Link to="/admin/phase1/phase2">→ 8. Phase 2 : Clôture + Preview + Génération</Link>
          <Link to="/admin/phase2/matchs">→ Phase 2 : Matchs</Link>
          <Link to="/admin/phase2/planning">→ Phase 2 : Planning</Link>
          <Link to="/admin/phase2/feuilles">→ Phase 2 : Feuilles</Link>
          <Link to="/admin/phase2/scores">→ Phase 2 : Scores</Link>
        </div>
      </div>

      <div className="card">
        <div className="title">Stats</div>

        {statsQ.isLoading ? (
          <Loading />
        ) : statsQ.isError ? (
          <ErrorState error={statsQ.error} />
        ) : !statsQ.data ? (
          <EmptyState label="Aucune stat." />
        ) : (
          <pre style={{ margin: 0, whiteSpace: "pre-wrap" }}>
            {JSON.stringify(statsQ.data, null, 2)}
          </pre>
        )}
      </div>
    </div>
  );
}
