import { createContext, useContext, useEffect, useState } from "react";
import { api, loadSession, setToken } from "./api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    (async () => {
      const token = await loadSession();
      if (token) {
        try {
          setUser(await api.me());
        } catch {
          await setToken(null);
        }
      }
      setReady(true);
    })();
  }, []);

  async function login(email, password) {
    const res = await api.login({ email, password });
    await setToken(res.access_token);
    setUser(res.user);
  }
  async function signup(email, display_name, password) {
    const res = await api.signup({ email, display_name, password });
    await setToken(res.access_token);
    setUser(res.user);
  }
  async function logout() {
    await setToken(null);
    setUser(null);
  }

  return (
    <AuthCtx.Provider value={{ user, ready, login, signup, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
