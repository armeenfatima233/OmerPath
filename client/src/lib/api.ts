const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!API_BASE_URL) {
  throw new Error(
    "VITE_API_BASE_URL is not set. Add it to client/.env.local (e.g. VITE_API_BASE_URL=http://127.0.0.1:8000)."
  );
}

export async function apiFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: "include",
    headers: {
      Accept: "application/json",
      // FormData bodies (e.g. file uploads) must let the browser set its own
      // multipart Content-Type with boundary - overriding it corrupts the request.
      ...(options.body && !(options.body instanceof FormData) ? { "Content-Type": "application/json" } : {}),
      ...options.headers,
    },
  });
}
