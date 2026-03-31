import { useMemo, useState, useEffect } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";
import { Link } from "react-router-dom"


function tournamentOk(tournois) {
  const codes = new Set(
    (tournois || []).map((t) => (t.code ?? t.nom ?? "").toString().toUpperCase())
  );
  // selon ton modèle, ça peut être code ou nom (Loisir/Rookie/Compétiteur)
  const hasRookie = codes.has("ROOKIE") || codes.has("ROOKIE".toUpperCase()) || codes.has("ROOKIE");
  const hasLoisir = codes.has("LOISIR") || codes.has("LOISIR".toUpperCase()) || codes.has("LOISIR");
  const hasCompet = codes.has("COMPETITEUR") || codes.has("COMPETITEUR".toUpperCase()) || codes.has("COMPETITEUR");
  return { hasRookie, hasLoisir, hasCompet, ok: hasRookie && hasLoisir && hasCompet };
}

export default function AdminEdition() {
  const { editionsQ, editions, activeEditionId, setActiveEditionId } = useActiveEdition();
  const activeId = activeEditionId;

  const tournoisQ = useQuery({
    queryKey: ["admin-tournois", activeId],
    queryFn: () => adminApi.tournois({ edition: activeId }),
    enabled: !!activeId,
  });

  const tournois = useMemo(() => {
    const d = tournoisQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [tournoisQ.data]);

  const status = tournamentOk(tournois);

  // --- create edition form (minimal)
  const [form, setForm] = useState({
    nom: "",
    date_evenement: "",
  });

  const createM = useMutation({
    mutationFn: (payload) => adminApi.createEdition(payload),
    onSuccess: (created) => {
      editionsQ.refetch();
      if (created?.id) {
        setActiveEditionId(created.id);
        tournoisQ.refetch();
      }
    },
  });

  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;

  if (!editions || editions.length === 0) {
    return (
      <div className="stack">
        <div className="card">
          <div className="title">Admin — Éditions</div>
          <EmptyState label="Aucune édition. Crée la première." />
        </div>

        <CreateEditionCard form={form} setForm={setForm} createM={createM} />
      </div>
    );
  }

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Admin — Éditions</div>
        <div className="filters">
          <AdminEditionSelect
            editions={editions}
            value={activeId}
            onChange={setActiveEditionId}
          />
          <Badge variant="info">Édition active: #{activeId}</Badge>
        </div>
      </div>

      <div className="card">
        <div className="title">Tournois liés</div>

        {tournoisQ.isLoading ? (
          <Loading />
        ) : tournoisQ.isError ? (
          <ErrorState error={tournoisQ.error} />
        ) : (
          <>
            <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 10 }}>
              <Badge variant={status.hasRookie ? "success" : "danger"}>ROOKIE</Badge>
              <Badge variant={status.hasLoisir ? "success" : "danger"}>LOISIR</Badge>
              <Badge variant={status.hasCompet ? "success" : "danger"}>COMPÉTITEUR</Badge>
              <Badge variant={status.ok ? "success" : "warning"}>
                {status.ok ? "OK" : "Tournois manquants"}
              </Badge>
            </div>

            {tournois.length === 0 ? (
              <EmptyState label="Aucun tournoi trouvé pour cette édition." />
            ) : (
              <ul className="list">
                {tournois.map((t) => (
                  <li key={t.id} className="row">
                    <span className="muted">#{t.id}</span>
                    <span>{t.nom ?? t.code ?? "Tournoi"}</span>
                    <span className="muted">{t.code ?? ""}</span>
                  </li>
                ))}
              </ul>
            )}
            <Link to="/admin/inscriptions">→ Inscriptions (équipes & joueurs)</Link>
          </>
          
        )}
      </div>

      <CreateEditionCard form={form} setForm={setForm} createM={createM} />
    </div>
  );
}

function CreateEditionCard({ form, setForm, createM }) {
  return (
    <div className="card">
      <div className="title">Créer une édition</div>

      <div className="filters">
        <input
          placeholder="Nom (ex: NDB 2026)"
          value={form.nom}
          onChange={(e) => setForm((s) => ({ ...s, nom: e.target.value }))}
        />
        <input
          type="date"
          value={form.date_evenement}
          onChange={(e) => setForm((s) => ({ ...s, date_evenement: e.target.value }))}
        />
        <button
          className="btn"
          onClick={() => createM.mutate(form)}
          disabled={createM.isLoading || !form.nom || !form.date_evenement}
        >
          Créer
        </button>
      </div>

      {createM.isError ? <ErrorState error={createM.error} /> : null}
    </div>
  );
}
