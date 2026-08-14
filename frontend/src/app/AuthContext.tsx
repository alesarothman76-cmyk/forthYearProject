import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { apiClient, registerSessionExpiredHandler } from "../api/client";
import { login as loginRequest, logout as logoutRequest } from "../api/endpoints/auth";
import {
  clearTokens,
  getRefreshToken,
  setAccessToken,
  setRefreshToken,
} from "../api/tokenStore";
import type { Role } from "../api/types";

interface DecodedAccessToken {
  role: Role;
  username: string;
  user_id: number;
  exp: number;
}

interface AuthUser {
  username: string;
  role: Role;
}

interface AuthContextValue {
  user: AuthUser | null;
  isLoading: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

/** Access tokens embed role/username as claims - decode locally, no /me/ round-trip needed just to know the role. */
function decodeAccessToken(token: string): DecodedAccessToken | null {
  try {
    const payload = token.split(".")[1];
    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const padded = base64 + "===".slice(0, (4 - (base64.length % 4)) % 4);
    const json = atob(padded);
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function userFromToken(token: string): AuthUser | null {
  const decoded = decodeAccessToken(token);
  if (!decoded) return null;
  return { username: decoded.username, role: decoded.role };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    registerSessionExpiredHandler(() => {
      setUser(null);
    });
  }, []);

  useEffect(() => {
    async function silentRefreshOnLoad() {
      const refreshToken = getRefreshToken();
      if (!refreshToken) {
        setIsLoading(false);
        return;
      }
      try {
        const response = await loginRefresh(refreshToken);
        setAccessToken(response.access);
        setUser(userFromToken(response.access));
      } catch {
        clearTokens();
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }
    silentRefreshOnLoad();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isLoading,
      async login(username, password) {
        const response = await loginRequest(username, password);
        setAccessToken(response.access);
        setRefreshToken(response.refresh);
        setUser(userFromToken(response.access));
      },
      async logout() {
        const refreshToken = getRefreshToken();
        try {
          if (refreshToken) await logoutRequest(refreshToken);
        } catch {
          // Best-effort server-side blacklist - clear client state regardless.
        }
        clearTokens();
        setUser(null);
      },
    }),
    [user, isLoading]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

/** Raw call to /auth/refresh/, bypassing the apiClient interceptor (used only during the initial silent-refresh check). */
async function loginRefresh(refresh: string) {
  const { data } = await apiClient.post<{ access: string; refresh?: string }>("/auth/refresh/", {
    refresh,
  });
  if (data.refresh) setRefreshToken(data.refresh);
  return data;
}
