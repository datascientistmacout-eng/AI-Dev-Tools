import { useEffect, useState } from "react";
import * as api from "./api.js";

const useRoute = () => {
  const [hash, setHash] = useState(window.location.hash || "#/");
  useEffect(() => {
    const onChange = () => setHash(window.location.hash || "#/");
    window.addEventListener("hashchange", onChange);
    return () => window.removeEventListener("hashchange", onChange);
  }, []);
  return hash.replace(/^#/, "").split("/").filter(Boolean);
};

export default function App() {
  const [a, slug, c] = useRoute();
  let page = <Home />;
  if (a === "l" && slug) page = c === "submit" ? <SubmitPage slug={slug} /> : <PublicPage slug={slug} />;
  return (
    <main>
      <h1><a href="#/">Match Day</a></h1>
      {page}
    </main>
  );
}

function Home() {
  const [name, setName] = useState("");
  const [teams, setTeams] = useState("");
  const [created, setCreated] = useState(null);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    const list = teams.split("\n").map((t) => t.trim()).filter(Boolean);
    const fixtures = [];
    for (let i = 0; i < list.length; i++)
      for (let j = i + 1; j < list.length; j++) fixtures.push({ home: list[i], away: list[j] });
    try {
      setCreated(await api.createLeague({ name, teams: list, fixtures }));
    } catch (err) {
      setError(err.message);
    }
  }

  if (created) {
    const base = `${window.location.origin}/#/l/${created.slug}`;
    return (
      <div className="card">
        <h2>{created.name} is ready</h2>
        <p>Public page: <a href={`#/l/${created.slug}`}>{base}</a></p>
        <p>Submit page: <a href={`#/l/${created.slug}/submit`}>{base}/submit</a></p>
        <p>Secret submit token (shown once, save it now):</p>
        <p><code>{created.submit_token}</code></p>
      </div>
    );
  }
  return (
    <form className="card" onSubmit={onSubmit}>
      <h2>Create a league</h2>
      <label>League name<input value={name} onChange={(e) => setName(e.target.value)} required /></label>
      <label>Teams, one per line (everyone plays everyone once)
        <textarea rows={5} value={teams} onChange={(e) => setTeams(e.target.value)} required />
      </label>
      <button type="submit">Create league</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}

function PublicPage({ slug }) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.getLeague(slug), api.getStandings(slug), api.getResults(slug), api.getScorers(slug)])
      .then(([league, standings, results, scorers]) => setData({ league, standings, results, scorers }))
      .catch((err) => setError(err.message));
  }, [slug]);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p className="muted">Loading...</p>;
  const { league, standings, results, scorers } = data;
  return (
    <>
      <h2>{league.name}</h2>
      {results.length === 0 && <p className="card muted">No results yet. Standings will appear after the first match is submitted.</p>}
      <table>
        <thead><tr><th>#</th><th>Team</th><th>P</th><th>W</th><th>D</th><th>L</th><th>GD</th><th>Pts</th></tr></thead>
        <tbody>
          {standings.map((r) => (
            <tr key={r.team}><td>{r.position}</td><td>{r.team}</td><td>{r.played}</td><td>{r.won}</td><td>{r.drawn}</td><td>{r.lost}</td><td>{r.goal_difference}</td><td><b>{r.points}</b></td></tr>
          ))}
        </tbody>
      </table>
      <h3>Recent results</h3>
      {results.length === 0 ? <p className="muted">None yet.</p> : (
        <ul>{results.map((r) => <li key={r.fixture_id}>{r.home} {r.home_score} - {r.away_score} {r.away}</li>)}</ul>
      )}
      <h3>Top scorers</h3>
      {scorers.length === 0 ? <p className="muted">None yet.</p> : (
        <ol>{scorers.map((s) => <li key={s.player + s.team}>{s.player} ({s.team}): {s.goals}</li>)}</ol>
      )}
      <p><a href={`#/l/${slug}/submit`}>Coach? Submit a result</a></p>
    </>
  );
}

function SubmitPage({ slug }) {
  const [league, setLeague] = useState(null);
  const [token, setToken] = useState("");
  const [fixtureId, setFixtureId] = useState("");
  const [home, setHome] = useState(0);
  const [away, setAway] = useState(0);
  const [scorers, setScorers] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    api.getLeague(slug).then(setLeague).catch((err) => setError(err.message));
  }, [slug]);

  async function onSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    // Scorers: one per line as "Team, Player, goals"
    const parsed = scorers.split("\n").map((l) => l.trim()).filter(Boolean).map((l) => {
      const [team, player, goals] = l.split(",").map((p) => p.trim());
      return { team, player, goals: Number(goals) };
    });
    try {
      const r = await api.submitResult(slug, fixtureId, token, {
        home_score: Number(home),
        away_score: Number(away),
        scorers: parsed,
      });
      setMessage(r.corrected ? "Result corrected." : "Result saved.");
    } catch (err) {
      setError(err.message);
    }
  }

  if (!league) return error ? <p className="error">{error}</p> : <p className="muted">Loading...</p>;
  return (
    <form className="card" onSubmit={onSubmit}>
      <h2>Submit a result: {league.name}</h2>
      <label>Submit token<input type="password" value={token} onChange={(e) => setToken(e.target.value)} required /></label>
      <label>Match
        <select value={fixtureId} onChange={(e) => setFixtureId(e.target.value)} required>
          <option value="">Choose a fixture</option>
          {league.fixtures.map((f) => (
            <option key={f.id} value={f.id}>{f.home} vs {f.away}{f.played ? " (played)" : ""}</option>
          ))}
        </select>
      </label>
      <label>Home score<input type="number" min="0" value={home} onChange={(e) => setHome(e.target.value)} required /></label>
      <label>Away score<input type="number" min="0" value={away} onChange={(e) => setAway(e.target.value)} required /></label>
      <label>Scorers (optional), one per line as: Team, Player, goals
        <textarea rows={3} value={scorers} onChange={(e) => setScorers(e.target.value)} />
      </label>
      <button type="submit">Submit result</button>
      {message && <p>{message} <a href={`#/l/${slug}`}>View standings</a></p>}
      {error && <p className="error">{error}</p>}
    </form>
  );
}