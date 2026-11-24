"use client";
import { useEffect, useRef, useState } from "react";
import { api } from "../../lib/api";

export default function Workspace() {
  const [me, setMe] = useState<any>(null);
  const [text, setText] = useState(""); const [style, setStyle] = useState("academic"); const [sample, setSample] = useState("");
  const [job, setJob] = useState<any>(null); const [err, setErr] = useState(""); const timer = useRef<any>();

  const loadMe = () => api("/api/me").then(setMe).catch(e => { if (e.status === 401) location.href = "/"; });
  useEffect(() => { loadMe(); return () => clearInterval(timer.current); }, []);

  const poll = (id: string) => {
    clearInterval(timer.current);
    timer.current = setInterval(async () => {
      const j = await api(`/api/jobs/${id}`).catch(() => null); if (!j) return; setJob(j);
      if (!["queued", "running"].includes(j.status)) { clearInterval(timer.current); loadMe(); }
    }, 1500);
  };
  const run = async () => {
    setErr(""); setJob(null);
    try { const j = await api("/api/jobs", { method: "POST", body: JSON.stringify({ text, style, sample }) }); setJob(j); poll(j.id); }
    catch (e: any) { setErr(e.message); }
  };
  const upload = async (f?: File) => {
    if (!f) return; const fd = new FormData(); fd.append("file", f);
    try { setText((await api("/api/extract", { method: "POST", body: fd })).text); } catch (e: any) { setErr(e.message); }
  };
  const busy = job && ["queued", "running"].includes(job.status);

  return <div className="wrap">
    <div className="row" style={{ justifyContent: "space-between", marginBottom: 16 }}>
      <h2 style={{ margin: 0 }}>Ai-Humanizer</h2>
      {me && <div className="row"><span className="muted">{me.email} · {me.quota.used}/{me.quota.limit} words today</span>
        <button className="btn sec" onClick={async () => { await api("/auth/logout", { method: "POST" }); location.href = "/"; }}>Sign out</button></div>}
    </div>
    <div className="grid">
      <div className="card">
        <textarea placeholder="Paste your text (30+ words)…" value={text} onChange={e => setText(e.target.value)} />
        <div className="row" style={{ marginTop: 12 }}>
          <select style={{ width: 160 }} value={style} onChange={e => setStyle(e.target.value)}>
            <option value="academic">Academic</option><option value="practical">Practical</option><option value="light">Light edit</option><option value="casual">Casual</option></select>
          <input type="file" accept=".txt,.md,.docx,.pdf" onChange={e => upload(e.target.files?.[0])} />
          <button className="btn" disabled={busy || text.trim().split(/\s+/).length < 30} onClick={run}>Humanize</button>
        </div>
        <details style={{ marginTop: 12 }}><summary className="muted">Match my writing style (optional)</summary>
          <textarea style={{ minHeight: 100 }} placeholder="Paste a sample of your own writing" value={sample} onChange={e => setSample(e.target.value)} /></details>
        {err && <p style={{ color: "#ff7a7a" }}>{err}</p>}
      </div>
      <div className="card">
        {!job && <p className="muted">The result appears here.</p>}
        {busy && <><p>{job.status === "queued" ? "Waiting in queue…" : "Rewriting…"}</p>
          <div className="bar"><div style={{ width: `${Math.round(job.progress * 100)}%` }} /></div>
          <button className="btn sec" style={{ marginTop: 12 }} onClick={() => api(`/api/jobs/${job.id}/cancel`, { method: "POST" })}>Cancel</button></>}
        {job?.status === "failed" && <p style={{ color: "#ff7a7a" }}>{job.error}</p>}
        {job?.status === "done" && <>
          <p className="muted">AI-likeness (internal heuristic): {job.before?.score} → {job.after?.score}</p>
          {job.before?.patterns?.length > 0 && (
            <details open><summary>AI-writing patterns found in your input ({job.before.patterns.length})</summary>
              <ul>{job.before.patterns.map((p: any) => (
                <li key={p.id}><b>{p.name}</b> ×{p.count}{p.examples?.[0] ? <> — <i>“{p.examples[0]}”</i></> : null}<br /><span className="muted">{p.fix}</span></li>
              ))}</ul>
              <p className="muted">Still present after rewrite: {job.after?.patterns?.length ?? 0}</p>
            </details>
          )}
          <textarea readOnly value={job.result || ""} />
          <button className="btn sec" style={{ marginTop: 12 }} onClick={() => navigator.clipboard.writeText(job.result)}>Copy</button></>}
      </div>
    </div>
  </div>;
}
