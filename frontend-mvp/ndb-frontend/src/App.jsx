import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Home from "./pages/Home.jsx";
import Planning from "./pages/Planning.jsx";
import Groupes from "./pages/Groupes.jsx";
import GroupeDetail from "./pages/GroupeDetail.jsx";
import NotFound from "./pages/NotFound.jsx";
import Resultats from "./pages/Resultats.jsx";
import EquipeDetail from "./pages/EquipeDetail.jsx";


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
    </Routes>
  );
}
