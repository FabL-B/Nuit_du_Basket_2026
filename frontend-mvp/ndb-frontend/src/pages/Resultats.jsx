import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../api/publicApi";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import Badge from "../components/Badge";
import { cleanParams, getSearchParams } from "../utils/queryParams";
import FiltersActions from "../components/FiltersActions";
import ActiveFilters from "../components/ActiveFilters";


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

const FILTER_KEYS = ["edition", "tournoi", "phase", "groupe", "terrain", "limit"];

export default function Resultats() {
  const [sp, setSp] = useSearchParams();
  const filters = useMemo(() => getSearchParams(sp, FILTER_KEYS), [sp]);

  // On force statut=TERMINE côté API (si supporté) + fallback front
  const params = cleanParams({ ...filters, statut: "TERMINE" });

  const q = useQuery({
    queryKey: ["planning", params],
    queryFn: () => publicApi.planning(params),
  });

  if (q.isLoading) return <Loading />;
  if (q.isError) return <ErrorState error={q.error} />;

  const items = Array.isArray(q.data) ? q.data : [];

  // Résultats = score présent ET validé
  const results = items.filter((m) => !!m.score?.valide_le);

  function setFilter(key, value) {
    const next = new URLSearchParams(sp);
    if (!value) next.delete(key);
    else next.set(key, value);
    setSp(next, { replace: true });
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Filtres</div>
        <div className="filters">
          <select value={filters.tournoi ?? ""} onChange={(e) => setFilter("tournoi", e.target.value)}>
            <option value="">Tournoi (tous)</option>
            <option value="ROOKIE">ROOKIE</option>
            <option value="LOISIR">LOISIR</option>
            <option value="COMPETITEUR">COMPETITEUR</option>
          </select>

          <select value={filters.phase ?? ""} onChange={(e) => setFilter("phase", e.target.value)}>
            <option value="">Phase (toutes)</option>
            <option value="PHASE_1">PHASE_1</option>
            <option value="PHASE_2">PHASE_2</option>
            <option value="FINALE">FINALE</option>
          </select>

          <input
            placeholder="Édition ID"
            value={filters.edition ?? ""}
            onChange={(e) => setFilter("edition", e.target.value)}
          />

          <input
            placeholder="Limit"
            value={filters.limit ?? ""}
            onChange={(e) => setFilter("limit", e.target.value)}
          />
        </div>
        <FiltersActions sp={sp} setSp={setSp} />
        <ActiveFilters
          sp={sp}
          setSp={setSp}
          labels={{
            edition: "Édition",
            tournoi: "Tournoi",
            phase: "Phase",
            groupe: "Groupe",
            terrain: "Terrain",
            limit: "Limit",
          }}
        />
      </div>

      <div className="card">
        <div className="title">Résultats (validés)</div>

        {results.length === 0 ? (
          <EmptyState label="Aucun résultat validé." />
        ) : (
          <div className="table">
            <div className="thead">
              <div>ID</div>
              <div>Match</div>
              <div>Terrain</div>
              <div>Heure</div>
              <div>Score</div>
              <div>Statut</div>
              <div>Tournoi</div>
              <div>Phase</div>
              <div>Groupe</div>
            </div>

            {results.map((m) => (
              <div className="trow" key={m.match_id}>
                <div className="muted">{m.match_id}</div>
                <div>
                  {m.equipe_a} vs {m.equipe_b}
                </div>
                <div className="muted">{m.terrain}</div>
                <div className="muted">{m.debut ? timeFormatter.format(new Date(m.debut)) : "—"}</div>

                <div className="muted">
                  {m.score ? `${m.score.points_a} - ${m.score.points_b}` : "—"}{" "}
                  <Badge variant="success">VALIDÉ</Badge>
                </div>

                <div>
                  <Badge variant={statutVariant(m.statut)}>{m.statut}</Badge>
                </div>

                <div className="muted">{m.tournoi ?? ""}</div>
                <div className="muted">{m.phase ?? ""}</div>
                <div className="muted">{m.groupe_code ?? (m.groupe_id ? `#${m.groupe_id}` : "")}</div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
