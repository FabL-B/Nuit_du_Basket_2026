import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Planning from "./pages/Planning.jsx";
import Groupes from "./pages/Groupes.jsx";
import GroupeDetail from "./pages/GroupeDetail.jsx";
import NotFound from "./pages/NotFound.jsx";
import Resultats from "./pages/Resultats.jsx";
import EquipeDetail from "./pages/EquipeDetail.jsx";
import RequireAdmin from "./components/RequireAdmin";
import AdminLogin from "./pages/admin/AdminLogin";
import AdminDashboard from "./pages/admin/AdminDashboard";
import AdminPlanning from "./pages/admin/AdminPlanning";
import AdminEdition from "./pages/admin/AdminEdition";
import AdminInscriptions from "./pages/admin/AdminInscriptions";
import AdminPhase1Groupes from "./pages/admin/AdminPhase1Groupes";
import AdminPhase1Matchs from "./pages/admin/AdminPhase1Matchs";
import AdminPhase1Planning from "./pages/admin/AdminPhase1Planning";
import AdminPhase1Feuilles from "./pages/admin/AdminPhase1Feuilles";
import AdminPhase1Scores from "./pages/admin/AdminPhase1Scores";
import AdminPhase2FromPhase1 from "./pages/admin/AdminPhase2FromPhase1";
import AdminPhase2Matchs from "./pages/admin/AdminPhase2Matchs";
import AdminPhase2Planning from "./pages/admin/AdminPhase2Planning";
import AdminPhase2Feuilles from "./pages/admin/AdminPhase2Feuilles";
import AdminPhase2Scores from "./pages/admin/AdminPhase2Scores";


export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Home />} />
        <Route path="/planning" element={<Planning />} />
        <Route path="/groupes" element={<Groupes />} />
        <Route path="/groupes/:id" element={<GroupeDetail />} />
        <Route path="*" element={<NotFound />} />
        <Route path="/resultats" element={<Resultats />} />
        <Route path="/equipes/:id" element={<EquipeDetail />} />
      </Route>
      <Route path="/admin/login" element={<AdminLogin />} />
        <Route
          path="/admin"
          element={
            <RequireAdmin>
              <AdminDashboard />
            </RequireAdmin>
          }
        />
      <Route
        path="/admin/planning"
        element={
          <RequireAdmin>
            <AdminPlanning />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/edition"
        element={
          <RequireAdmin>
            <AdminEdition />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/inscriptions"
        element={
          <RequireAdmin>
            <AdminInscriptions />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/phase1/groupes"
        element={
          <RequireAdmin>
            <AdminPhase1Groupes />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/phase1/matchs"
        element={
          <RequireAdmin>
            <AdminPhase1Matchs />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/phase1/planning"
        element={
          <RequireAdmin>
            <AdminPhase1Planning />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/phase1/feuilles"
        element={
          <RequireAdmin>
            <AdminPhase1Feuilles />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/phase1/scores"
        element={
          <RequireAdmin>
            <AdminPhase1Scores />
          </RequireAdmin>
        }
      />
      <Route
        path="/admin/phase1/phase2"
        element={
          <RequireAdmin>
            <AdminPhase2FromPhase1 />
          </RequireAdmin>
        }
      />
      <Route path="/admin/phase2/matchs" element={<RequireAdmin><AdminPhase2Matchs /></RequireAdmin>} />
      <Route path="/admin/phase2/planning" element={<RequireAdmin><AdminPhase2Planning /></RequireAdmin>} />
      <Route path="/admin/phase2/feuilles" element={<RequireAdmin><AdminPhase2Feuilles /></RequireAdmin>} />
      <Route path="/admin/phase2/scores" element={<RequireAdmin><AdminPhase2Scores /></RequireAdmin>} />
    </Routes>
  );
}
