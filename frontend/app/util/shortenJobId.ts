export function shortenJobId(id: string, start = 8, end = 6) {
  if (id.length <= start + end + 5) return id;
  return `${id.slice(0, start)}...${id.slice(-end)}`;
}