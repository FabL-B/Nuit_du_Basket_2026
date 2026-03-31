import { useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { adminApi } from "../api/adminApi";
import Loading from "./Loading";
import ErrorState from "./ErrorState";

export default function RequireAdmin({ children }) {
  const ping = useQuery({
    queryKey: ["admin-auth-check"],
    queryFn: () => adminApi.editions({ limit: 1 }),
    retry: false,
  });

  if (ping.isLoading) return <Loading label="Vérification admin..." />;

  if (ping.isError) {
    if (ping.error?.status === 401 || ping.error?.status === 403) {
      return <Navigate to="/admin/login" replace />;
    }
    return <ErrorState error={ping.error} />;
  }

  return children;
}
