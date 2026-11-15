const BASE = import.meta.env.VITE_API_URL || "";

async function call(path, options) {
  const res = await fetch(BASE + path, options);
  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data && data.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join("; ")
      : detail || `Request failed (${res.status})`;
    throw new Error(message);
  }
  return data;
}

const json = (body) => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const createLeague = (body) => call("/api/leagues", json(body));
export const getLeague = (slug) => call(`/api/leagues/${slug}`);
export const getStandings = (slug) => call(`/api/leagues/${slug}/standings`);
export const getResults = (slug) => call(`/api/leagues/${slug}/results`);
export const getScorers = (slug) => call(`/api/leagues/${slug}/scorers`);
export const submitResult = (slug, fixtureId, token, body) =>
  call(`/api/leagues/${slug}/fixtures/${fixtureId}/result`, {
    ...json(body),
    headers: { "Content-Type": "application/json", "X-Submit-Token": token },
  });