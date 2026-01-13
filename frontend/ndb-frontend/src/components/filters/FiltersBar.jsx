import EditionSelect from "./EditionSelect";
import PhaseSelect from "./PhaseSelect";
import TournoiSelect from "./TournoiSelect";
import GroupeSelect from "./GroupeSelect";
import TerrainSelect from "./TerrainSelect";

export default function FiltersBar({
  editions,
  tournois,
  groupes,
  terrains,
  params,
  onParamChange,
}) {
  return (
    <div
      style={{
        display: "grid",
        gap: 12,
        padding: 12,
        border: "1px solid #ddd",
        borderRadius: 12,
        gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
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

      <TournoiSelect
        tournois={tournois}
        value={params.tournoi}
        onChange={(v) => onParamChange("tournoi", v)}
      />

      <GroupeSelect
        groupes={groupes}
        value={params.groupe}
        onChange={(v) => onParamChange("groupe", v)}
      />

      <TerrainSelect
        terrains={terrains}
        value={params.terrain}
        onChange={(v) => onParamChange("terrain", v)}
      />
    </div>
  );
}
