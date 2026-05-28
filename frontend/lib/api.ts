const API_BASE = "http://localhost:8000";

async function request(path: string, options: RequestInit = {}) {
  const token = localStorage.getItem("token");
  const headers: Record<string, string> = {
    ...((options.headers as Record<string, string>) || {}),
  };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!res.ok) {
    throw new Error(`API error: ${res.status}`);
  }
  return res.json();
}

// Auth
export async function login(email: string, password: string) {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function register(username: string, email: string, password: string) {
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ username, email, password }),
  });
}

// Knowledge Bases
export async function listKnowledgeBases() {
  return request("/api/kb/list");
}

export async function createKnowledgeBase(name: string, description: string) {
  return request("/api/kb/create", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });
}

// Documents
export async function uploadDocument(kbId: number, file: File) {
  const token = localStorage.getItem("token");
  const formData = new FormData();
  formData.append("kb_id", kbId.toString());
  formData.append("file", file);

  const res = await fetch(`${API_BASE}/api/document/upload`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
    },
    body: formData,
  });

  if (!res.ok) {
    throw new Error(`Upload error: ${res.status}`);
  }
  return res.json();
}

export async function listDocuments(kbId: number) {
  return request(`/api/document/list?kb_id=${kbId}`);
}

export async function deleteDocument(docId: number) {
  return request(`/api/document/${docId}`, {
    method: "DELETE",
  });
}

// Chat
export async function sendMessage(kbId: number, message: string, chatId?: number) {
  return request("/api/chat", {
    method: "POST",
    body: JSON.stringify({ kb_id: kbId, message, chat_id: chatId }),
  });
}

export async function getChatHistory(chatId: number) {
  return request(`/api/chat/history?chat_id=${chatId}`);
}
