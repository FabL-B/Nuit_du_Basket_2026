export function formatParisDateTime(isoString) {
  if (!isoString) return "";
  const d = new Date(isoString);
  return new Intl.DateTimeFormat("fr-FR", {
    timeZone: "Europe/Paris",
    day: "2-digit",
    month: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  }).format(d);
}
