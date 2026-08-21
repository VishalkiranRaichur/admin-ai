const configuredApiUrl = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "");

export const apiUrl = (path: string) => `${configuredApiUrl ?? ""}${path}`;

export type AskSource = {
  id?: string;
  chunk_id?: string;
  document_id?: string;
  chunk_index?: number;
  content?: string;
  snippet?: string;
  file?: string;
  filename?: string;
  title?: string;
  page?: string | number;
};

export type AskRequest = {
  question: string;
  limit: number;
};

export type AskResponse = {
  answer: string;
  sources: AskSource[];
};

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(apiUrl(path), init);
  } catch {
    throw new Error(
      "Cannot reach the Admin AI API. Make sure the backend and local services are running."
    );
  }

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    try {
      const body = (await response.json()) as { detail?: string };
      message = body.detail ?? message;
    } catch {
      // Keep the status-based fallback for non-JSON responses.
    }

    throw new Error(message);
  }

  return (await response.json()) as T;
}
