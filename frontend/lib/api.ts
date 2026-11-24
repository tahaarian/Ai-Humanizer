export async function api<T = any>(path: string, init?: RequestInit): Promise<T> {
  const r = await fetch(path, { credentials: "include", headers: init?.body && !(init.body instanceof FormData) ? { "Content-Type": "application/json" } : undefined, ...init });
  if (!r.ok) { let m = r.statusText; try { m = (await r.json()).detail || m } catch {} ; throw Object.assign(new Error(m), { status: r.status }); }
  return r.status === 204 ? (null as T) : r.json();
}
