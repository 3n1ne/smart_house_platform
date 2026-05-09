import React from 'react';
import { Routes, Route, useLocation, Link } from 'react-router-dom';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import Home from './pages/Home';
import Auth from './pages/Auth';
import Explore from './pages/Explore';
import PropertyDetail from './pages/PropertyDetail';

// Placeholder pages for logic
const Dashboard = () => (
  <div className="flex-1 flex flex-col p-12 gap-12">
    <header className="flex flex-col gap-2">
      <p className="text-secondary tracking-widest font-bold text-xs uppercase">Tenant Dashboard</p>
      <h1 className="font-serif text-5xl">欢迎回来，张先生</h1>
    </header>
    
    <div className="grid grid-cols-12 gap-6">
      <div className="col-span-8 bg-white border border-outline-variant p-8 rounded-xl ambient-shadow flex flex-col gap-8">
        <div className="flex justify-between items-center">
          <h2 className="font-serif text-2xl">近期账单 (Upcoming Payments)</h2>
          <span className="bg-surface-variant px-3 py-1 rounded text-xs font-bold uppercase">Due in 5 days</span>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="font-serif text-5xl text-on-background">¥4,500</span>
          <span className="text-secondary">/ Month</span>
        </div>
        <div className="space-y-4">
          <div className="flex justify-between py-3 border-b border-outline-variant/30">
            <span>水费 (Water Utility)</span>
            <span className="font-bold">¥120.00</span>
          </div>
          <div className="flex justify-between py-3 border-b border-outline-variant/30">
            <span>电费 (Electricity)</span>
            <span className="font-bold">¥285.50</span>
          </div>
        </div>
        <button className="bg-primary text-white py-4 rounded-lg font-bold hover:bg-primary-container transition-all">立即支付 (Pay Now)</button>
      </div>

      <div className="col-span-4 flex flex-col gap-6">
        <div className="bg-white border border-outline-variant p-6 rounded-xl ambient-shadow">
          <h3 className="font-serif text-xl border-b border-outline-variant/30 pb-4 mb-4">看房日程</h3>
          <div className="space-y-4">
            <div className="border-l-2 border-primary pl-4">
              <p className="text-xs text-secondary mb-1">明天, 14:00</p>
              <p className="font-bold">绿地世纪城 3号楼</p>
            </div>
            <div className="border-l-2 border-outline-variant pl-4 opacity-50">
              <p className="text-xs text-secondary mb-1">下周二, 10:30</p>
              <p className="font-bold">万科城市花园</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default function App() {
  const location = useLocation();
  const isDashboard = location.pathname.startsWith('/dashboard');

  return (
    <div className={`min-h-screen flex ${isDashboard ? 'flex-row' : 'flex-col'}`}>
      <Header />
      {isDashboard && <Sidebar />}
      
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/explore" element={<Explore />} />
          <Route path="/property/:id" element={<PropertyDetail />} />
          <Route path="/auth" element={<Auth />} />
          <Route path="/dashboard/*" element={<Dashboard />} />
        </Routes>
      </main>

      {!isDashboard && (
        <footer className="bg-surface border-t border-outline-variant py-12 mt-24">
          <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="flex flex-col gap-4">
              <span className="font-serif text-2xl font-bold">智慧租房</span>
              <p className="text-secondary text-sm">© 2024 Smart Rental System. A serene living experience.</p>
            </div>
            <nav className="flex gap-8 text-sm font-serif italic text-secondary">
              <Link to="#" className="hover:text-on-background">Architecture</Link>
              <Link to="#" className="hover:text-on-background">Journal</Link>
              <Link to="#" className="hover:text-on-background">Privacy</Link>
              <Link to="#" className="hover:text-on-background">Sustainability</Link>
            </nav>
          </div>
        </footer>
      )}
    </div>
  );
}
