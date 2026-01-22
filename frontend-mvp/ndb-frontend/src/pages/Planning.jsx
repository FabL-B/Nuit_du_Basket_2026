import { useMemo } from "react";
import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { publicApi } from "../api/publicApi";
import Loading from "../components/Loading";
import ErrorState from "../components/ErrorState";
import EmptyState from "../components/EmptyState";
import { cleanParams, getSearchParams } from "../utils/queryParams";
import Badge from "../components/Badge";
import FiltersActions from "../components/FiltersActions";
import ActiveFilters from "../components/ActiveFilters";
import { groupByTime } from "../utils/groupByTime";


const timeFormatter = new Intl.DateTimeFormat("fr-FR", {
  timeZone: "Europe/Paris",
  hour: "2-digit",
  minute: "2-digit",
});

const FILTER_KEYS = ["edition", "tournoi", "phase", "groupe", "terrain", "statut", "limit"];

function statutVariant(statut) {
  if (statut === "EN_COURS") return "warning";
  if (statut === "A_VENIR") return "info";
  if (statut === "TERMINE") return "default";
  return "default";
}

export default function Planning() {
  const [sp, setSp] = useSearchParams();
  const filters = useMemo(() => getSearchParams(sp, FILTER_KEYS), [sp]);

  const params = cleanParams(filters);

  const q = useQuery({
    queryKey: ["planning", params],
    queryFn: () => publicApi.planning(params),
  });

  const groupesQ = useQuery({
    queryKey: ["groupes", { edition: filters.edition, tournoi: filters.tournoi, phase: filters.phase }],
    queryFn: () => publicApi.groupes(cleanParams({ edition: filters.edition, tournoi: filters.tournoi, phase: filters.phase })),
  });

  const terrainsQ = useQuery({
    queryKey: ["terrains", { edition: filters.edition }],
    queryFn: () => publicApi.terrains(cleanParams({ edition: filters.edition })),
  });

  if (q.isLoading) return <Loading />;
  if (q.isError) return <ErrorState error={q.error} />;

  // ton endpoint renvoie une liste brute
  const items = Array.isArray(q.data) ? q.data : [];

  const grouped = groupByTime(items, timeFormatter);

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
          {/* Tournoi = code (ex: LOISIR/ROOKIE/COMPETITEUR) selon ton serializer */}
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

          <select value={filters.statut ?? ""} onChange={(e) => setFilter("statut", e.target.value)}>
            <option value="">Statut (tous)</option>
            <option value="A_VENIR">A_VENIR</option>
            <option value="EN_COURS">EN_COURS</option>
            <option value="TERMINE">TERMINE</option>
          </select>

          {/* Groupe (select dynamique) */}
          <select
            value={filters.groupe ?? ""}
            onChange={(e) => setFilter("groupe", e.target.value)}
            disabled={groupesQ.isLoading || groupesQ.isError}
          >
            <option value="">Groupe (tous)</option>
            {(Array.isArray(groupesQ.data) ? groupesQ.data : []).map((g) => (
              <option key={g.id} value={g.id}>
                {g.nom} (#{g.id})
              </option>
            ))}
          </select>

          {/* Terrain (select dynamique) */}
          <select
            value={filters.terrain ?? ""}
            onChange={(e) => setFilter("terrain", e.target.value)}
            disabled={terrainsQ.isLoading || terrainsQ.isError}
          >
            <option value="">Terrain (tous)</option>
            {(Array.isArray(terrainsQ.data) ? terrainsQ.data : []).map((t) => (
              <option key={t.id} value={t.id}>
                {t.nom} (#{t.id})
              </option>
            ))}
          </select>

          <input
            placeholder="Edition ID"
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
            statut: "Statut",
            limit: "Limit",
          }}
        />
      </div>

      <div className="card">
        <div className="title">Planning</div>

        {items.length === 0 ? (
          <EmptyState />
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
            {Object.entries(grouped).map(([time, matches]) => (
              <div key={time} className="card" style={{ marginBottom: 14 }}>
                <div className="title">⏱ {time}</div>

                <div className="table">
                  <div className="thead">
                    <div>ID</div>
                    <div>Match</div>
                    <div>Terrain</div>
                    <div>Heure</div>
                    <div>Score</div>
                    <div>Statut</div>
                  </div>

                  {matches.map((m) => (
                    <div className="trow" key={m.match_id}>
                      <div className="muted">{m.match_id}</div>
                      <div>{m.equipe_a} vs {m.equipe_b}</div>
                      <div className="muted">{m.terrain}</div>
                      <div className="muted">
                        {m.debut ? timeFormatter.format(new Date(m.debut)) : "—"}
                      </div>
                      <div className="muted">
                        {m.score ? `${m.score.points_a} - ${m.score.points_b}` : "—"}
                      </div>
                      <div>
                        <Badge variant={statutVariant(m.statut)}>{m.statut}</Badge>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
