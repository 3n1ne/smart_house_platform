import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Home, User, Menu, X, LogIn } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

export default function Header() {
  const [isOpen, setIsOpen] = React.useState(false);
  const location = useLocation();

  const isDashboard = location.pathname.includes('dashboard') || location.pathname.includes('console');

  if (isDashboard) return null;

  return (
    <header className="sticky top-0 z-50 bg-background border-b border-outline-variant h-20">
      <div className="max-w-7xl mx-auto px-6 h-full flex justify-between items-center">
        <div className="flex items-center gap-12">
          <Link to="/" className="flex items-center gap-4 group">
            <div className="font-serif italic text-3xl font-black tracking-tighter border-b-4 border-primary leading-none pb-1">Z.</div>
            <div className="flex flex-col">
              <span className="font-serif text-xl font-black tracking-tight leading-none">智慧租房</span>
              <span className="editorial-label text-[8px] opacity-40">Issue No. 001</span>
            </div>
          </Link>

          <nav className="hidden lg:flex items-center gap-10">
            <Link to="/explore" className="editorial-label hover:text-primary transition-colors hover:opacity-100">Explore</Link>
            <Link to="/list" className="editorial-label hover:text-primary transition-colors hover:opacity-100">Manifesto</Link>
          </nav>
        </div>

        <div className="flex items-center gap-8">
          <div className="hidden md:block editorial-label opacity-30">Spring / Summer Edition — 2024</div>
          <Link to="/auth" className="editorial-label bg-on-background text-white px-5 py-2 hover:bg-primary transition-colors hover:opacity-100">
            Subscribe
          </Link>
        </div>

        <button className="md:hidden" onClick={() => setIsOpen(!isOpen)}>
          {isOpen ? <X /> : <Menu />}
        </button>
      </div>

      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="md:hidden bg-surface border-b border-outline-variant p-6 flex flex-col gap-4"
          >
            <Link to="/explore" onClick={() => setIsOpen(false)}>Explore Houses</Link>
            <Link to="/list" onClick={() => setIsOpen(false)}>List Your Space</Link>
            <Link to="/auth" onClick={() => setIsOpen(false)}>Login/Register</Link>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
