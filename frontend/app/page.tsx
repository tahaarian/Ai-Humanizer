export default function Home() {
  return <div className="wrap" style={{ textAlign: "center", paddingTop: 100 }}>
    <h1 style={{ fontSize: 44 }}>Ai-Humanizer</h1>
    <p className="muted" style={{ fontSize: 18, maxWidth: 560, margin: "12px auto 28px" }}>
      Turn stiff, machine-sounding drafts into clear, natural writing. Numbers, citations and meaning stay intact.
      Runs on a private local model. Your text is deleted after processing.</p>
    <a className="btn" href="/auth/login">Sign in with Google</a>
    <p className="muted" style={{ marginTop: 40, fontSize: 13 }}>An editing tool. Follow your institution’s AI-use rules; no tool can guarantee any detector result.</p>
  </div>;
}
