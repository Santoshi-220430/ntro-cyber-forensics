/**
 * Forensic Platform - API Service Client
 * Problem ID: SIH26148 | NTRO Cyber Forensics Prototype
 */

// In production, use VITE_API_URL or relative /api path; in local dev fallback to http://127.0.0.1:8000/api
const API_BASE = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://127.0.0.1:8000/api" : "/api");

export function getToken() {
  return localStorage.getItem("forensic_token");
}

export function setToken(token) {
  localStorage.setItem("forensic_token", token);
}

export function removeToken() {
  localStorage.removeItem("forensic_token");
}

export async function apiRequest(endpoint, options = {}) {
  const token = getToken();
  const headers = {
    "Accept": "application/json",
    ...(options.headers || {})
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  if (options.body && !(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(options.body);
  }

  const res = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers
  });

  if (res.status === 401) {
    removeToken();
  }

  if (!res.ok) {
    let errorDetail = "API Request Failed";
    try {
      const errJson = await res.json();
      errorDetail = errJson.detail || JSON.stringify(errJson);
    } catch {
      errorDetail = await res.text();
    }
    throw new Error(errorDetail);
  }

  // Handle binary/file downloads
  const contentType = res.headers.get("content-type");
  if (contentType && contentType.includes("application/pdf")) {
    return await res.blob();
  }

  return await res.json();
}
