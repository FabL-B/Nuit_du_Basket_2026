import { useMemo, useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { adminApi } from "../../api/adminApi";
import Loading from "../../components/Loading";
import ErrorState from "../../components/ErrorState";
import EmptyState from "../../components/EmptyState";
import Badge from "../../components/Badge";
import { useActiveEdition } from "../../hooks/useActiveEdition";
import AdminEditionSelect from "../../components/admin/AdminEditionSelect";


export default function AdminInscriptions() {
  const { editionsQ, editions, activeEditionId, setActiveEditionId } = useActiveEdition();
  const editionId = activeEditionId;

  const tournoisQ = useQuery({
    queryKey: ["admin-tournois", editionId],
    queryFn: () => adminApi.tournois({ edition: editionId }),
    enabled: !!editionId,
  });

  const equipesQ = useQuery({
    queryKey: ["admin-equipes", editionId],
    queryFn: () => adminApi.equipes({ edition: editionId }),
    enabled: !!editionId,
  });

  const tournois = useMemo(() => {
    const d = tournoisQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [tournoisQ.data]);

  const equipes = useMemo(() => {
    const d = equipesQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [equipesQ.data]);

  const [selectedEquipeId, setSelectedEquipeId] = useState(null);
  const selectedEquipe = equipes.find((e) => e.id === selectedEquipeId) ?? null;

  // --- create team form
  const [teamForm, setTeamForm] = useState({
    nom: "",
    nom_club: "",
    tournoi_id: "",
  });

  const createEquipeM = useMutation({
    mutationFn: (payload) => adminApi.createEquipe(payload),
    onSuccess: () => {
      setTeamForm({ nom: "", nom_club: "", tournoi_id: "" });
      equipesQ.refetch();
    },
  });

  const deleteEquipeM = useMutation({
    mutationFn: (id) => adminApi.deleteEquipe(id),
    onSuccess: () => {
      setSelectedEquipeId(null);
      equipesQ.refetch();
    },
  });

  // --- players for selected team
  const joueursQ = useQuery({
    queryKey: ["admin-joueurs", selectedEquipeId],
    queryFn: () => adminApi.joueurs({ equipe: selectedEquipeId }),
    enabled: !!selectedEquipeId,
  });

  const joueurs = useMemo(() => {
    const d = joueursQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [joueursQ.data]);

  const [playerForm, setPlayerForm] = useState({
    prenom: "",
    nom: "",
    date_naissance: "",
    email: "",
    telephone: "",
  });

  const createJoueurM = useMutation({
    mutationFn: (payload) => adminApi.createJoueur(payload),
    onSuccess: () => {
      setPlayerForm({
        prenom: "",
        nom: "",
        date_naissance: "",
        email: "",
        telephone: "",
      });
      joueursQ.refetch();
      equipesQ.refetch();
    },
  });

  const deleteJoueurM = useMutation({
    mutationFn: (id) => adminApi.deleteJoueur(id),
    onSuccess: () => {
      joueursQ.refetch();
      equipesQ.refetch();
    },
  });

  if (editionsQ.isLoading) return <Loading />;
  if (editionsQ.isError) return <ErrorState error={editionsQ.error} />;

  if (!editionId) {
    return (
      <div className="filters">
        <AdminEditionSelect
          editions={editions}
          value={editionId}
          onChange={setActiveEditionId}
        />
      </div>
    );
  }

  if (tournoisQ.isLoading || equipesQ.isLoading) return <Loading />;
  if (tournoisQ.isError) return <ErrorState error={tournoisQ.error} />;
  if (equipesQ.isError) return <ErrorState error={equipesQ.error} />;

  return (
    <div className="stack">
      <div className="card">
        <div className="title">Admin — Inscriptions</div>
        <div className="muted">Édition active : #{editionId}</div>
      </div>

      <div className="grid" style={{ gridTemplateColumns: "1fr 1.2fr", gap: 14 }}>
        {/* Colonne gauche : équipes */}
        <div className="card">
          <div className="title">Équipes</div>

          {equipes.length === 0 ? (
            <EmptyState label="Aucune équipe pour cette édition." />
          ) : (
            <ul className="list">
              {equipes.map((e) => (
                <li
                  key={e.id}
                  className="row"
                  style={{ cursor: "pointer" }}
                  onClick={() => setSelectedEquipeId(e.id)}
                >
                  <span className="muted">#{e.id}</span>
                  <span>{e.nom}</span>
                  <span className="muted">{e.tournoi?.nom ?? e.tournoi ?? ""}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Colonne droite : création + détail */}
        <div className="stack">
          <div className="card">
            <div className="title">Créer une équipe</div>

            <div className="filters">
              <input
                placeholder="Nom équipe"
                value={teamForm.nom}
                onChange={(e) => setTeamForm((s) => ({ ...s, nom: e.target.value }))}
              />
              <input
                placeholder="Nom club"
                value={teamForm.nom_club}
                onChange={(e) => setTeamForm((s) => ({ ...s, nom_club: e.target.value }))}
              />

              <select
                value={teamForm.tournoi_id}
                onChange={(e) => setTeamForm((s) => ({ ...s, tournoi_id: e.target.value }))}
              >
                <option value="">Tournoi</option>
                {tournois.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.nom ?? t.code ?? `Tournoi #${t.id}`}
                  </option>
                ))}
              </select>

              <button
                className="btn"
                disabled={createEquipeM.isLoading || !teamForm.nom || !teamForm.tournoi_id}
                onClick={() =>
                  createEquipeM.mutate({
                    nom: teamForm.nom,
                    nom_club: teamForm.nom_club,
                    edition: editionId,
                    tournoi: Number(teamForm.tournoi_id),
                    statut: "BROUILLON",
                  })
                }
              >
                Créer
              </button>
            </div>

            {createEquipeM.isError ? <ErrorState error={createEquipeM.error} /> : null}
          </div>

          <div className="card">
            <div className="title">Détail équipe</div>

            {!selectedEquipe ? (
              <EmptyState label="Sélectionne une équipe à gauche." />
            ) : (
              <>
                <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
                  <Badge variant="info">#{selectedEquipe.id}</Badge>
                  <div style={{ fontWeight: 700 }}>{selectedEquipe.nom}</div>
                  <div className="muted">{selectedEquipe.nom_club ?? ""}</div>
                </div>

                <div className="muted" style={{ marginTop: 6 }}>
                  Tournoi : {selectedEquipe.tournoi?.nom ?? selectedEquipe.tournoi ?? "—"}
                </div>

                <div style={{ marginTop: 10 }}>
                  <button
                    className="btn"
                    onClick={() => deleteEquipeM.mutate(selectedEquipe.id)}
                    disabled={deleteEquipeM.isLoading}
                  >
                    Supprimer l’équipe
                  </button>
                </div>

                <div style={{ marginTop: 14 }}>
                  <div className="title" style={{ fontSize: 14 }}>
                    Joueurs
                  </div>

                  {joueursQ.isLoading ? (
                    <Loading />
                  ) : joueursQ.isError ? (
                    <ErrorState error={joueursQ.error} />
                  ) : joueurs.length === 0 ? (
                    <EmptyState label="Aucun joueur." />
                  ) : (
                    <ul className="list">
                      {joueurs.map((j) => (
                        <li key={j.id} className="row">
                          <span className="muted">#{j.id}</span>
                          <span>{j.prenom} {j.nom}</span>
                          <button
                            className="btn"
                            onClick={() => deleteJoueurM.mutate(j.id)}
                            disabled={deleteJoueurM.isLoading}
                          >
                            Supprimer
                          </button>
                        </li>
                      ))}
                    </ul>
                  )}

                  <div className="filters" style={{ marginTop: 10 }}>
                    <input
                      placeholder="Prénom"
                      value={playerForm.prenom}
                      onChange={(e) => setPlayerForm((s) => ({ ...s, prenom: e.target.value }))}
                    />
                    <input
                      placeholder="Nom"
                      value={playerForm.nom}
                      onChange={(e) => setPlayerForm((s) => ({ ...s, nom: e.target.value }))}
                    />

                    <input
                      type="date"
                      value={playerForm.date_naissance}
                      onChange={(e) => setPlayerForm((s) => ({ ...s, date_naissance: e.target.value }))}
                    />

                    <input
                      placeholder="Email"
                      value={playerForm.email}
                      onChange={(e) => setPlayerForm((s) => ({ ...s, email: e.target.value }))}
                    />

                    <input
                      placeholder="Téléphone"
                      value={playerForm.telephone}
                      onChange={(e) => setPlayerForm((s) => ({ ...s, telephone: e.target.value }))}
                    />
                    <button
                      className="btn"
                      disabled={
                        createJoueurM.isLoading ||
                        !playerForm.prenom ||
                        !playerForm.nom ||
                        !playerForm.date_naissance ||
                        !playerForm.email ||
                        !playerForm.telephone
                      }
                      onClick={() =>
                        createJoueurM.mutate({
                          equipe: selectedEquipe.id,
                          prenom: playerForm.prenom,
                          nom: playerForm.nom,
                          date_naissance: playerForm.date_naissance,
                          email: playerForm.email,
                          telephone: playerForm.telephone,
                        })
                      }
                    >
                      Ajouter joueur
                    </button>
                  </div>

                  {createJoueurM.isError ? <ErrorState error={createJoueurM.error} /> : null}
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
