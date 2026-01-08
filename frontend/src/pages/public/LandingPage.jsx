import React from "react";
import { useNavigate } from "react-router-dom";

export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-linear-to-b from-slate-800 to-slate-900 text-white p-6">
      <h1 className="text-5xl font-bold mb-6">Welcome to PhishNet</h1>
      <p className="text-center max-w-2xl mb-8">
        PhishNet helps you train against phishing attacks and simulate realistic
        phishing scenarios for educational purposes. Stay safe and learn how to
        spot phishing attempts effectively.
      </p>
      <div className="flex gap-4">
        <button
          onClick={() => navigate("/login")}
          className="px-6 py-3 bg-cyan-500 hover:bg-cyan-600 rounded-lg font-medium transition"
        >
          Log In
        </button>
        <button
          onClick={() => navigate("/signup")} // later if you implement signup
          className="px-6 py-3 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition"
        >
          Sign Up
        </button>
      </div>
    </div>
  );
}
