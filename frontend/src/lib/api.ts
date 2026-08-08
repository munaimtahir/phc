export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

const AUTH_STORAGE_KEY = "phc_auth";

export function setCredentials(username: string, password: string) {
  sessionStorage.setItem(AUTH_STORAGE_KEY, btoa(`${username}:${password}`));
  sessionStorage.setItem("phc_username", username);
}

export function clearCredentials() {
  sessionStorage.removeItem(AUTH_STORAGE_KEY);
  sessionStorage.removeItem("phc_username");
}

export function getStoredUsername(): string | null {
  return sessionStorage.getItem("phc_username");
}

function authHeader(): Record<string, string> {
  const token = sessionStorage.getItem(AUTH_STORAGE_KEY);
  return token ? { Authorization: `Basic ${token}` } : {};
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const isFormData = options.body instanceof FormData;
  const headers: Record<string, string> = {
    ...(isFormData ? {} : { "Content-Type": "application/json" }),
    ...authHeader(),
    ...(options.headers as Record<string, string>),
  };

  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = body.detail || JSON.stringify(body);
    } catch {
      // ignore
    }
    throw new Error(detail);
  }

  if (res.status === 204) return undefined as T;

  const contentType = res.headers.get("content-type") || "";
  if (contentType.includes("application/pdf")) {
    return (await res.blob()) as unknown as T;
  }
  return res.json();
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body instanceof FormData ? body : JSON.stringify(body ?? {}),
    }),
  postForm: <T>(path: string, form: FormData) =>
    request<T>(path, { method: "POST", body: form }),
};

export interface Indicator {
  id: number;
  domain_code: string;
  domain_name: string;
  standard_code: string;
  standard_title: string;
  text: string;
  weightage: number;
  allows_partial: boolean;
  category: "physical" | "one_time" | "recurring";
  frequency: string | null;
  evidence_format: "photo" | "document" | "structured_form";
  compliance_requirements: string[];
  survey_process: string[];
}

export interface DueListItem {
  indicator_id: number;
  indicator_text: string;
  frequency: string;
  evidence_format: string;
  period_label: string;
  done: boolean;
}

export interface Draft {
  id: number;
  indicator?: number;
  indicator_ids: number[];
  kind: "document" | "template";
  template_version: string;
  prompt_text: string;
  raw_output: string;
  working_content: string;
  content: string;
  created_at: string;
  created_by: string;
  status: "draft" | "pending_review" | "approved" | "rejected";
  reviewed_by: string | null;
  reviewed_at: string | null;
  version_no: number;
  linked_document_id?: number | null;
}

export interface ComplianceSummary {
  overall_pct: number;
  earned_total: number;
  possible_total: number;
  per_indicator: {
    indicator_id: number;
    status: string | null;
    earned_weightage: number;
    possible_weightage: number;
  }[];
}
