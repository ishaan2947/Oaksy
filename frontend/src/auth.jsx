import { createContext, useContext, useEffect, useState } from "react";
import { api, getToken, setToken } from "./api";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!getToken()) {
      setReady(true);
      return;
    }
    api
      .me()
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setReady(true));
  }, []);

  async function login(email, password) {
    const res = await api.login({ email, password });
    setToken(res.access_token);
    setUser(res.user);
  }

  async function signup(email, display_name, password) {
    const res = await api.signup({ email, display_name, password });
    setToken(res.access_token);
    setUser(res.user);
  }

  async function loginWithGoogle(credential) {
    const res = await api.google(credential);
    setToken(res.access_token);
    setUser(res.user);
  }

  function logout() {
    setToken(null);
    setUser(null);
  }

  return (
    <AuthCtx.Provider value={{ user, ready, login, signup, loginWithGoogle, logout }}>
      {children}
    </AuthCtx.Provider>
  );
}

export function useAuth() {
  return useContext(AuthCtx);
}
