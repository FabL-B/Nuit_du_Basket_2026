import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Tabs from "../components/Tabs";
import { fetchEditions } from "../api/public";
import PlanningView from "../components/views/PlanningView";
import ResultatsView from "../components/views/ResultatsView";
import FiltersBar from "../components/filters/FiltersBar";
import {
  fetchTournois,
  fetchGroupes,
  fetchTerrains,
} from "../api/public";


export default function Home() {
  const [sp, setSp] = useSearchParams();

  const tabFromUrl = sp.get("tab") || "planning";
  const [tab, setTab] = useState(tabFromUrl);

  useEffect(() => {
    setTab(tabFromUrl);
  }, [tabFromUrl]);

  const onTabChange = (next) => {
    const copy = new URLSearchParams(sp);
    copy.set("tab", next);
    setSp(copy, { replace: true });
  };

  const onParamChange = (key, value) => {
    const copy = new URLSearchParams(sp);

    if (!value) copy.delete(key);
    else copy.set(key, value);
    if (key === "edition") {
      copy.delete("tournoi");
      copy.delete("groupe");
      copy.delete("terrain");
    }
    if (key === "tournoi" || key === "phase") {
      copy.delete("groupe");
    }
    setSp(copy, { replace: true });
  };

  const params = useMemo(() => Object.fromEntries(sp.entries()), [sp]);

  const [editions, setEditions] = useState([]);
  const [tournois, setTournois] = useState([]);
  const [groupes, setGroupes] = useState([]);
  const [terrains, setTerrains] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEditions()
      .then((data) => {
        setEditions(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  useEffect(() => {
    if (!params.edition) {
      setTournois([]);
      return;
    }

    fetchTournois({ edition: params.edition })
      .then(setTournois)
      .catch(() => setTournois([]));
  }, [params.edition]);

  useEffect(() => {
    if (!params.edition || !params.tournoi || !params.phase) {
      setGroupes([]);
      return;
    }

    fetchGroupes({
      edition: params.edition,
      tournoi: params.tournoi,
      phase: params.phase,
    })
      .then(setGroupes)
      .catch(() => setGroupes([]));
  }, [params.edition, params.tournoi, params.phase]);

  useEffect(() => {
    if (!params.edition) {
      setTerrains([]);
      return;
    }

    fetchTerrains({ edition: params.edition })
      .then(setTerrains)
      .catch(() => setTerrains([]));
  }, [params.edition]);


  return (
    <div style={{ display: "grid", gap: 12 }}>
      <Tabs
        value={tab}
        onChange={onTabChange}
        items={[
          { value: "planning", label: "Planning" },
          { value: "resultats", label: "Résultats" },
        ]}
      />

      {loading && <p>Chargement des éditions…</p>}
      {error && <p style={{ color: "red" }}>Erreur éditions : {error}</p>}

      {!loading && !error && (
        <FiltersBar
          editions={editions}
          tournois={tournois}
          groupes={groupes}
          terrains={terrains}
          params={params}
          onParamChange={onParamChange}
        />
      )}

      <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontWeight: 600, marginBottom: 8 }}>
          Onglet actif : {tab}
        </div>
        <div style={{ fontSize: 12, opacity: 0.8 }}>
          Query params : <code>{JSON.stringify(params)}</code>
        </div>
      </div>

      {tab === "planning" && <PlanningView params={params} />}
      {tab === "resultats" && <ResultatsView params={params} />}
    </div>
  );
}
