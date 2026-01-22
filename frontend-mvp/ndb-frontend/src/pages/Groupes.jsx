import { useMemo } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../api/publicApi";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import { cleanParams, getSearchParams } from "../utils/queryParams";
import FiltersActions from "../components/FiltersActions";
import ActiveFilters from "../components/ActiveFilters";


const FILTER_KEYS = ["edition", "tournoi", "phase", "branche"];

export default function Groupes() {
  const [sp, setSp] = useSearchParams();
  const filters = useMemo(() => getSearchParams(sp, FILTER_KEYS), [sp]);
  const params = cleanParams(filters);
  const editionsQ = useQuery({
    queryKey: ["editions"],
    queryFn: () => publicApi.editions(),
  });

  const q = useQuery({
    queryKey: ["groupes", params],
    queryFn: () => publicApi.groupes(params),
  });

  const items = q.data?.results ?? q.data ?? [];

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
          <select
            value={filters.edition ?? ""}
            onChange={(e) => setFilter("edition", e.target.value)}
            disabled={editionsQ.isLoading || editionsQ.isError}
          >
            <option value="">Édition (dernière)</option>
            {(Array.isArray(editionsQ.data) ? editionsQ.data : []).map((ed) => (
              <option key={ed.id} value={ed.id}>
                {ed.nom ?? `Edition #${ed.id}`}
              </option>
            ))}
          </select>
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
          <select value={filters.branche ?? ""} onChange={(e) => setFilter("branche", e.target.value)}>
            <option value="">Branche (toutes)</option>
            <option value="AUCUNE">AUCUNE</option>
            <option value="CHALLENGE">CHALLENGE</option>
            <option value="CONSOLANTE">CONSOLANTE</option>
          </select>
        </div>
        <FiltersActions sp={sp} setSp={setSp} />
        <ActiveFilters
          sp={sp}
          setSp={setSp}
          labels={{
            edition: "Édition",
            tournoi: "Tournoi",
            phase: "Phase",
            branche: "Branche",
          }}
        />
      </div>

      {q.isLoading && <Loading />}
      {q.isError && <ErrorState error={q.error} />}

      {!q.isLoading && !q.isError && (
        <div className="card">
          <div className="title">Groupes</div>
          {items.length === 0 ? (
            <EmptyState />
          ) : (
            <ul className="list">
              {items.map((g) => (
                <li key={g.id} className="row">
                  <span className="muted">#{g.id}</span>
                  <span>{g.nom ?? g.name ?? "Groupe"}</span>
                  <span className="muted">{g.tournoi?.nom ?? ""}</span>
                  <span className="muted">{g.phase_globale?.type_phase ?? ""}</span>
                  <Link to={`/groupes/${g.id}`}>Détail</Link>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
