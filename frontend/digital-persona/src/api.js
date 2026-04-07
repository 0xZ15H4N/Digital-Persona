const BASE_URL = "https://ec2-3-110-143-248.ap-south-1.compute.amazonaws.com";

export async function fetchLinkedInProfile(userID) {
  const res = await fetch(`${BASE_URL}/api/v1/requestLDdata`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ userID }),
  });
  if (!res.ok) throw new Error(`Could not fetch profile (server ${res.status}).`);
  const json = await res.json();
  return json.data;
}

export async function createChunks(data) {
  const res = await fetch(`${BASE_URL}/api/v1/createChunks`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data }),
  });
  if (!res.ok) throw new Error(`Failed to process profile data (server ${res.status}).`);
  return res.json();
}

export async function createDB(chunks) {
  const res = await fetch(`${BASE_URL}/api/v1/createDB`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chunks }),
  });
  if (!res.ok) throw new Error(`Failed to build AI database (server ${res.status}).`);
  return res.json();
}

export async function loadVectorDB(vector_id) {
  const res = await fetch(`${BASE_URL}/api/v1/loadVD`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ vector_id }),
  });
  if (!res.ok) throw new Error(`Failed to load AI context (server ${res.status}).`);
  return res.json();
}

export async function sendChat(query) {
  const res = await fetch(`${BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status} — the server couldn't process your request.`);
  return res.json();
}

export async function exitChat(vector_id) {
  try {
    await fetch(`${BASE_URL}/api/v1/exit-chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ vector_id }),
    });
  } catch (_) {
    /* best-effort */
  }
}
