import { useEffect, useState } from "react";
import { api, setCredentials, clearCredentials, getStoredUsername } from "./api";

export function useAuth() {
  const [username, setUsername] = useState<string | null>(getStoredUsername());

  useEffect(() => {
    if (!username) return;
    api
      .get<{ username: string | null }>("/auth/whoami/")
      .then((r) => setUsername(r.username))
      .catch(() => {
        clearCredentials();
        setUsername(null);
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = async (u: string, p: string) => {
    setCredentials(u, p);
    try {
      const r = await api.post<{ username: string }>("/auth/login/", { username: u, password: p });
      setUsername(r.username);
    } catch (err) {
      clearCredentials();
      throw err;
    }
  };

  const logout = () => {
    clearCredentials();
    setUsername(null);
  };

  return { username, login, logout };
}
