import { Outlet, Link } from "react-router-dom";

export default function Layout() {
  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: 16 }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
        <Link to="/" style={{ textDecoration: "none", color: "inherit" }}>
          <h1 style={{ margin: 0, fontSize: 20 }}>Nuit du Basket</h1>
        </Link>
        <span style={{ opacity: 0.7, fontSize: 12 }}>Frontend MVP</span>
      </header>

      <hr style={{ margin: "12px 0 16px" }} />

      <Outlet />
    </div>
  );
}
