export function groupByTimeSlot(items, minutesStep = 15) {
  const groups = {};

  items.forEach((item) => {
    const d = new Date(item.debut);
    const minutes = d.getMinutes();
    const rounded = Math.floor(minutes / minutesStep) * minutesStep;

    const slot = new Date(d);
    slot.setMinutes(rounded, 0, 0);

    const key = slot.toISOString();

    if (!groups[key]) groups[key] = [];
    groups[key].push(item);
  });

  return Object.entries(groups)
    .sort(([a], [b]) => new Date(a) - new Date(b))
    .map(([slot, items]) => ({
      slot,
      items,
    }));
}
