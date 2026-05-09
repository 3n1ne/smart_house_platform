import { Mail, Lock, Eye, ArrowRight, User as UserIcon } from 'lucide-react';
import { motion } from 'motion/react';
import { Link } from 'react-router-dom';

export default function Auth() {
  return (
    <div className="min-h-[calc(100vh-80px)] flex flex-col md:flex-row">
      {/* Left Panel */}
      <section className="hidden md:block md:w-1/2 lg:w-7/12 relative bg-surface-variant">
        <img 
          src="https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?q=80&w=2670&auto=format&fit=crop" 
          alt="Serene Living"
          className="absolute inset-0 w-full h-full object-cover grayscale"
        />
        <div className="absolute inset-0 bg-black/10" />
        <div className="absolute bottom-12 left-12 max-w-md text-white p-8">
          <span className="editorial-label text-primary-container mb-4 block">Manifesto 03</span>
          <h2 className="font-serif text-7xl font-black italic mb-4 leading-none">The Quiet Room.</h2>
          <p className="text-xl font-serif italic opacity-90">Discover spaces designed for quiet intelligence and refined comfort.</p>
        </div>
      </section>

      {/* Right Panel */}
      <section className="w-full md:w-1/2 lg:w-5/12 flex items-center justify-center p-8 bg-background md:border-l border-outline-variant">
        <div className="w-full max-w-md space-y-12">
          <div className="text-center space-y-4">
            <h1 className="font-serif text-5xl font-black italic">Welcome Back</h1>
            <p className="editorial-label text-[#D4AF37]">Enter the Inner Circle</p>
          </div>

          <div className="space-y-8">
            <div className="flex border-b border-outline">
              <button className="flex-1 py-4 editorial-label border-b-2 border-on-background">Login</button>
              <button className="flex-1 py-4 editorial-label opacity-40 hover:opacity-100 transition-opacity">Register</button>
            </div>

            <form className="space-y-8">
              <div className="space-y-2">
                <label className="editorial-label opacity-40">Email / ID</label>
                <div className="relative">
                  <UserIcon className="absolute left-0 top-1/2 -translate-y-1/2 w-4 h-4 text-outline opacity-40" />
                  <input 
                    type="text" 
                    placeholder="Inquire identity..."
                    className="w-full pl-8 py-3 bg-transparent border-b border-outline-variant focus:border-on-background focus:outline-none transition-colors editorial-label opacity-100 placeholder:opacity-20"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <label className="editorial-label opacity-40">Passcode</label>
                  <Link to="#" className="editorial-label text-primary hover:underline">Forgot?</Link>
                </div>
                <div className="relative">
                  <Lock className="absolute left-0 top-1/2 -translate-y-1/2 w-4 h-4 text-outline opacity-40" />
                  <input 
                    type="password" 
                    placeholder="••••••••"
                    className="w-full pl-8 pr-10 py-3 bg-transparent border-b border-outline-variant focus:border-on-background focus:outline-none transition-colors editorial-label opacity-100 placeholder:opacity-20"
                  />
                  <button type="button" className="absolute right-0 top-1/2 -translate-y-1/2 text-outline opacity-40 hover:opacity-100">
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <div className="pt-6 space-y-6">
                <Link to="/dashboard/overview">
                    <button className="w-full bg-on-background text-white py-5 editorial-label flex justify-center items-center gap-2 hover:bg-primary transition-all">
                    Sign In <ArrowRight className="w-5 h-5" />
                    </button>
                </Link>
                <div className="text-center">
                  <Link to="#" className="editorial-label opacity-40 hover:opacity-100">Request Invitation</Link>
                </div>
              </div>
            </form>
          </div>

          <p className="editorial-label !text-[8px] text-center opacity-30 leading-relaxed px-12">
            By proceeding, you agree to our <Link to="#" className="underline">Manifesto</Link> and <Link to="#" className="underline">Privacy Laws</Link>
          </p>
        </div>
      </section>
    </div>
  );
}
