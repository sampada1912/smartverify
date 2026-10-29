"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { UserRole, AuthToken } from "./types";
import { api } from "./api";

interface AuthContextType {
  user: AuthToken | null;
  role: UserRole;
  isAuthenticated: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<AuthToken>;
  logout: () => Promise<void>;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [user, setUser] = useState<AuthToken | null>(null);
  const [role, setRole] = useState<UserRole>("REVIEWER");
  const [isLoading, setIsLoading] = useState(true);

  // Initialize session on mount
  useEffect(() => {
    const initializeAuth = async () => {
      if (typeof window === "undefined") {
        setIsLoading(false);
        return;
      }

      const storedToken = localStorage.getItem("smartverify_token");
      const storedUser = localStorage.getItem("smartverify_user");

      if (storedToken && storedUser) {
        try {
          const parsed = JSON.parse(storedUser) as AuthToken;
          setUser(parsed);
          setRole(parsed.role);

          // Verify with backend in background
          try {
            await api.getCurrentUser();
          } catch {
            console.warn("Session expired or token invalid, resetting auth state.");
            await api.logout();
            setUser(null);
          }
        } catch (e) {
          console.error("Failed to parse stored auth session:", e);
          await api.logout();
          setUser(null);
        }
      } else {
        setUser(null);
      }

      setIsLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (usernameOrEmail: string, password: string): Promise<AuthToken> => {
    setIsLoading(true);
    try {
      const authData = await api.login(usernameOrEmail, password);
      setUser(authData);
      setRole(authData.role);
      return authData;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    await api.logout();
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        isAuthenticated: !!user,
        login,
        logout,
        isLoading,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
