import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="card">
      <div className="title">404</div>
      <Link to="/">Retour</Link>
    </div>
  );
}
