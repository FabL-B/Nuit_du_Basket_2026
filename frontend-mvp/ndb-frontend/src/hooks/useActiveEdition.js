import { useMemo, useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { adminApi } from "../api/adminApi";

const KEY = "ndb_admin_edition_id";

function readStoredId() {
  const raw = localStorage.getItem(KEY);
  const n = raw ? Number(raw) : null;
  return Number.isFinite(n) ? n : null;
}

function writeStoredId(id) {
  localStorage.setItem(KEY, String(id));
}

export function useActiveEdition() {
  const editionsQ = useQuery({
    queryKey: ["admin-editions"],
    queryFn: () => adminApi.editions(),
  });

  const editions = useMemo(() => {
    const d = editionsQ.data;
    return Array.isArray(d) ? d : (d?.results ?? []);
  }, [editionsQ.data]);

  // state local (source de vérité côté UI)
  const [activeId, setActiveIdState] = useState(readStoredId());

  // 1) si l'id stocké n'existe plus -> fallback premier
  const resolvedId = useMemo(() => {
    if (!editions || editions.length === 0) return null;
    if (activeId && editions.some((e) => e.id === activeId)) return activeId;
    return editions[0].id;
  }, [editions, activeId]);

  // 2) sync localStorage + state si on a dû fallback
  useEffect(() => {
    if (!resolvedId) return;
    if (resolvedId !== activeId) {
      setActiveIdState(resolvedId);
      writeStoredId(resolvedId);
    }
  }, [resolvedId, activeId]);

  // API pour changer proprement
  function setActiveEditionId(id) {
    const n = Number(id);
    if (!Number.isFinite(n)) return;
    setActiveIdState(n);
    writeStoredId(n);
  }

  const activeEdition = useMemo(() => {
    if (!resolvedId) return null;
    return editions.find((e) => e.id === resolvedId) ?? null;
  }, [editions, resolvedId]);

  return {
    editionsQ,
    editions,
    activeEditionId: resolvedId,
    activeEdition,
    setActiveEditionId,
  };
}
