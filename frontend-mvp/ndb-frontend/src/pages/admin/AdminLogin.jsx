import { useNavigate } from "react-router-dom";

export default function AdminLogin() {
  const navigate = useNavigate();

  return (
    <div className="card">
      <div className="title">Connexion admin</div>
      <p className="muted">
        Connecte-toi via le backend (session Django), puis reviens ici.
      </p>

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
        <a className="btn" href="http://localhost:8000/admin/" target="_blank" rel="noreferrer">
          Ouvrir login backend
        </a>
        <button className="btn" onClick={() => navigate("/admin", { replace: true })}>
          Je suis connecté → Accéder à l’admin
        </button>
      </div>
    </div>
  );
}
