import React from "react";
import { useNavigate } from "react-router-dom";
import useAuth from "../../auth/useAuth";

// Dummy user object for testing !!!
const DUMMY_USER = { id: 1, email: "user@test.com", name: "Test User" };

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleLogin = () => {
    // Call login with a user object (no JWT yet)
    login(DUMMY_USER);

    // Redirect to dashboard after login
    navigate("/dashboard", { replace: true });
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-900 text-white p-6">
      <h1 className="text-4xl font-bold mb-6">Login</h1>
      <p className="mb-6 text-center max-w-md">
        Welcome to PhishNet! Use the button below to log in for testing. Later this
        will connect to your backend authentication.
      </p>
      <button
        onClick={handleLogin}
        className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 rounded-lg font-medium transition"
      >
        Log in as Test User
      </button>
    </div>
  );
}
