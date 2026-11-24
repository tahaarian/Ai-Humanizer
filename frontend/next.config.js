const API = process.env.API_URL || "http://127.0.0.1:8000";
module.exports = { async rewrites() { return [
  { source: "/api/:p*", destination: `${API}/api/:p*` },
  { source: "/auth/:p*", destination: `${API}/auth/:p*` } ]; } };
