import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Tabs from "../components/Tabs";
import { fetchEditions } from "../api/public";

export default function Home() {
  const [sp, setSp] = useSearchParams();

  const tabFromUrl = sp.get("tab") || "planning";
  const [tab, setTab] = useState(tabFromUrl);

  // garde tab synchronisé si l'URL change
  useEffect(() => {
    setTab(tabFromUrl);
  }, [tabFromUrl]);

  const onTabChange = (next) => {
    const copy = new URLSearchParams(sp);
    copy.set("tab", next);
    setSp(copy, { replace: true });
  };

  const params = useMemo(() => Object.fromEntries(sp.entries()), [sp]);

  const [editions, setEditions] = useState([]);
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

      <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <div style={{ fontWeight: 600, marginBottom: 8 }}>
          Onglet actif : {tab}
        </div>
        <div style={{ fontSize: 12, opacity: 0.8 }}>
          Query params : <code>{JSON.stringify(params)}</code>
        </div>
      </div>

      <div style={{ padding: 12, border: "1px solid #eee", borderRadius: 12 }}>
        <h2 style={{ marginTop: 0 }}>Éditions</h2>

        {loading && <p>Chargement…</p>}
        {error && <p style={{ color: "red" }}>Erreur : {error}</p>}

        {!loading && !error && (
          <ul>
            {editions.map((edition) => (
              <li key={edition.id}>
                {edition.nom} (id={edition.id})
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
