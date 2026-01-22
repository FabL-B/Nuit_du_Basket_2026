import { NavLink, Outlet } from "react-router-dom";

export default function Layout() {
  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">Nuit du Basket</div>
        <nav className="nav">
          <NavLink to="/" end className={({ isActive }) => (isActive ? "active" : "")}>
            Home
          </NavLink>
          <NavLink to="/planning" className={({ isActive }) => (isActive ? "active" : "")}>
            Planning
          </NavLink>
          <NavLink to="/groupes" className={({ isActive }) => (isActive ? "active" : "")}>
            Groupes
          </NavLink>
          <NavLink to="/resultats" className={({ isActive }) => (isActive ? "active" : "")}>
            Résultats
          </NavLink>
        </nav>
      </header>
      <main className="container">
        <Outlet />
      </main>
    </div>
  );
}
