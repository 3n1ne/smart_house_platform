import { Home, LayoutGrid, FileText, CreditCard, Headphones, Settings, Bell, ChevronRight, CheckCircle, Plus } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { icon: LayoutGrid, label: 'Overview', path: '/dashboard/overview' },
  { icon: Home, label: 'Properties', path: '/dashboard/properties' },
  { icon: FileText, label: 'Leases', path: '/dashboard/leases' },
  { icon: CreditCard, label: 'Payments', path: '/dashboard/payments' },
  { icon: Headphones, label: 'Support', path: '/dashboard/support' },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <nav className="w-64 border-r border-outline-variant h-screen sticky top-0 p-6 flex flex-col gap-8 bg-background">
      <div className="flex items-center gap-3 px-2">
        <div className="w-10 h-10 rounded-full bg-surface-variant overflow-hidden">
          <img src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=2670&auto=format&fit=crop" alt="User" className="w-full h-full object-cover" />
        </div>
        <div>
          <h2 className="font-serif font-bold text-lg leading-none">Console</h2>
          <p className="font-serif text-[10px] uppercase tracking-widest text-secondary mt-1">Quiet Intelligence</p>
        </div>
      </div>

      <div className="flex flex-col gap-1">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.label}
              to={item.path}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive 
                  ? 'bg-white border border-outline-variant text-primary font-bold ambient-shadow' 
                  : 'text-secondary hover:text-on-background hover:bg-surface-variant/50'
              }`}
            >
              <item.icon className={`w-5 h-5 ${isActive ? 'fill-primary/20' : ''}`} />
              <span className="font-serif text-sm uppercase tracking-widest">{item.label}</span>
            </Link>
          );
        })}
      </div>

      <div className="mt-auto">
        <Link
          to="/dashboard/settings"
          className="flex items-center gap-3 px-4 py-3 text-secondary hover:text-on-background transition-colors"
        >
          <Settings className="w-5 h-5" />
          <span className="font-serif text-sm uppercase tracking-widest">Settings</span>
        </Link>
      </div>
    </nav>
  );
}
