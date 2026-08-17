import { brand } from "./brand";

const TOKEN_KEY = "d4ta_shield_jwt";
const TOKEN_COOKIE = "d4ta_shield_jwt";
const TOKEN_MAX_AGE = 3600;

export function getApiBase(): string {
  return process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";
}

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  document.cookie = `${TOKEN_COOKIE}=${encodeURIComponent(token)}; path=/; SameSite=Lax; Max-Age=${TOKEN_MAX_AGE}`;
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
  document.cookie = `${TOKEN_COOKIE}=; path=/; Max-Age=0`;
}

export class ApiError extends Error {
  status: number;
  body: unknown;
  constructor(message: string, status: number, body?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

type FetchOptions = RequestInit & { auth?: boolean; json?: unknown };

async function apiFetch<T = unknown>(path: string, options: FetchOptions = {}): Promise<T> {
  const { auth = true, json, headers: initHeaders, ...rest } = options;
  const headers = new Headers(initHeaders);
  if (json !== undefined) headers.set("Content-Type", "application/json");
  if (auth) {
    const token = getToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  const res = await fetch(`${getApiBase()}${path.startsWith("/") ? path : `/${path}`}`, {
    ...rest,
    headers,
    body: json !== undefined ? JSON.stringify(json) : rest.body,
  });
  const text = await res.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text);
    } catch {
      body = text;
    }
  }
  if (!res.ok) {
    const msg =
      typeof body === "object" && body && "message" in body
        ? String((body as { message: string }).message)
        : `HTTP ${res.status}`;
    throw new ApiError(msg, res.status, body);
  }
  return body as T;
}

export async function login(email: string, password: string): Promise<{ token: string }> {
  return apiFetch("/api/login_check", {
    method: "POST",
    auth: false,
    json: { username: email.trim().toLowerCase(), password },
  });
}

export type ContractSummary = {
  id: string;
  filename: string;
  status: string;
  clause_count: number;
  risk_counts: { alto: number; medio: number; bajo: number };
  discrepancy_count: number;
  created_at: string;
};

export async function listContracts(): Promise<{ data: ContractSummary[]; disclaimer: string }> {
  return apiFetch("/api/contracts");
}

export async function uploadContract(file: File): Promise<{ data: ContractSummary; disclaimer: string }> {
  const form = new FormData();
  form.append("file", file);
  const token = getToken();
  const headers = new Headers();
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${getApiBase()}/api/contracts`, { method: "POST", headers, body: form });
  const body = await res.json();
  if (!res.ok) throw new ApiError("Upload failed", res.status, body);
  return body;
}

export async function analyzeContract(id: string) {
  return apiFetch(`/api/contracts/${id}/analyze`, { method: "POST" });
}

export async function getReport(id: string) {
  return apiFetch<{ data: Record<string, unknown>; disclaimer: string }>(`/api/contracts/${id}/report`);
}

export async function getDiscrepancies(id: string) {
  return apiFetch<{ data: unknown[]; disclaimer: string }>(`/api/contracts/${id}/discrepancies`);
}

export async function reviewFlag(contractId: string, flagId: string) {
  return apiFetch(`/api/contracts/${contractId}/flags/${flagId}/review`, { method: "POST" });
}

export { brand, TOKEN_COOKIE };
