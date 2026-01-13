import EditionSelect from "./EditionSelect";
import PhaseSelect from "./PhaseSelect";

export default function FiltersBar({ editions, params, onParamChange }) {
  return (
    <div
      style={{
        display: "flex",
        gap: 16,
        flexWrap: "wrap",
        padding: 12,
        border: "1px solid #ddd",
        borderRadius: 12,
      }}
    >
      <EditionSelect
        editions={editions}
        value={params.edition}
        onChange={(v) => onParamChange("edition", v)}
      />

      <PhaseSelect
        value={params.phase}
        onChange={(v) => onParamChange("phase", v)}
      />
    </div>
  );
}
