/**
 * Single source of truth for token storage. Deliberately separate from
 * AuthContext (React) so the axios interceptor in client.ts - which has no
 * business importing React - can read/write tokens without a circular
 * dependency between the API layer and the app layer.
 *
 * Storage tradeoff (stated, not silently decided): the refresh token lives
 * in localStorage (opaque, rotated on every use, bounded blast radius if
 * leaked); the access token lives only in memory and is lost on reload,
 * which is why AuthContext performs a silent refresh on app mount.
 */
const REFRESH_TOKEN_KEY = "alz_refresh_token";

let accessToken: string | null = null;

export function getAccessToken(): string | null {
  return accessToken;
}

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getRefreshToken(): string | null {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setRefreshToken(token: string | null) {
  if (token) {
    localStorage.setItem(REFRESH_TOKEN_KEY, token);
  } else {
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  }
}

export function clearTokens() {
  accessToken = null;
  setRefreshToken(null);
}
