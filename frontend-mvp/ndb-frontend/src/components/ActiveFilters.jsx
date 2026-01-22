import Badge from "./Badge";
import { removeParam } from "../utils/filtersUx";

export default function ActiveFilters({ sp, setSp, labels = {} }) {
  const entries = Array.from(sp.entries());

  if (entries.length === 0) return null;

  return (
    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 10 }}>
      {entries.map(([k, v]) => (
        <span
          key={`${k}:${v}`}
          onClick={() => removeParam(sp, setSp, k)}
          style={{ cursor: "pointer" }}
          title="Clique pour retirer ce filtre"
        >
          <Badge variant="info">
            {(labels[k] ?? k)}: {v} ✕
          </Badge>
        </span>
      ))}
    </div>
  );
}
