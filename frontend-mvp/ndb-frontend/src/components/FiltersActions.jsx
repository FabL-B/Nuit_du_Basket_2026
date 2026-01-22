import { resetSearchParams } from "../utils/filtersUx";

export default function FiltersActions({ sp, setSp }) {
  const hasAny = sp.toString().length > 0;

  return (
    <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 10 }}>
      <button
        type="button"
        className="btn"
        onClick={() => resetSearchParams(setSp)}
        disabled={!hasAny}
      >
        Réinitialiser
      </button>
    </div>
  );
}
