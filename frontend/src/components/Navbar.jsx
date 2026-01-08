import { Fish, Menu } from "lucide-react";
import { useState } from "react";


export default function Navbar() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Fish className="w-8 h-8 text-cyan-400" />
            <span className="text-xl text-white">PhishNet</span>
          </div>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-8">
            <a
              href="#features"
              className="text-slate-300 hover:text-cyan-400 transition-colors"
            >
              Features
            </a>
            <a
              href="#training"
              className="text-slate-300 hover:text-cyan-400 transition-colors"
            >
              Training
            </a>
            <a
              href="#pricing"
              className="text-slate-300 hover:text-cyan-400 transition-colors"
            >
              Pricing
            </a>
            <a
              href="#about"
              className="text-slate-300 hover:text-cyan-400 transition-colors"
            >
              About
            </a>
          </div>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center gap-4">
            <button
              variant="ghost"
              className="text-slate-300 hover:text-cyan-400"
              
            >
              Sign In
            </button>
            <button
              className="bg-cyan-500 hover:bg-cyan-600 text-white"
            >
              Get Started
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden text-white"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          >
            <Menu className="w-6 h-6" />
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden py-4 border-t border-slate-800">
            <div className="flex flex-col gap-4">
              <a
                href="#features"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                Features
              </a>
              <a
                href="#training"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                Training
              </a>
              <a
                href="#pricing"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                Pricing
              </a>
              <a
                href="#about"
                className="text-slate-300 hover:text-cyan-400 transition-colors"
              >
                About
              </a>
              <div className="flex flex-col gap-2 pt-4 border-t border-slate-800">
                <button
                  variant="ghost"
                  className="text-slate-300 hover:text-cyan-400 justify-start"
                >
                  Sign In
                </button>
                <button
                  className="bg-cyan-500 hover:bg-cyan-600 text-white"
                >
                  Get Started
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}