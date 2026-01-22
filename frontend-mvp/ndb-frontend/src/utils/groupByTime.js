export function groupByTime(items, formatter) {
  return items.reduce((acc, m) => {
    const key = m.debut
      ? formatter.format(new Date(m.debut))
      : "—";

    if (!acc[key]) acc[key] = [];
    acc[key].push(m);
    return acc;
  }, {});
}
