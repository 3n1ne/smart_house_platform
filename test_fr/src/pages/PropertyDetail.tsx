import { MapPin, Wifi, Wind, WashingMachine, Refrigerator, Tv, Flame, Building2, ArrowUpDown, ShieldCheck, MessageSquare, Map as MapIcon } from 'lucide-react';
import { motion } from 'motion/react';

export default function PropertyDetail() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-12 flex flex-col gap-12">
      {/* Gallery Bento Grid */}
      <section className="grid md:grid-cols-4 gap-2 h-[600px] overflow-hidden border border-outline-variant">
        <div className="md:col-span-3 h-full group overflow-hidden">
          <img 
            src="https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?q=80&w=2670&auto=format&fit=crop" 
            alt="Main View" 
            className="w-full h-full object-cover transition-transform duration-1000 group-hover:scale-105 grayscale hover:grayscale-0"
          />
        </div>
        <div className="hidden md:flex flex-col gap-2 h-full">
          <div className="h-1/3 overflow-hidden">
            <img src="https://images.unsplash.com/photo-1556911223-e4524c286f62?q=80&w=2670&auto=format&fit=crop" alt="Kitchen" className="w-full h-full object-cover grayscale hover:grayscale-0 transition-all" />
          </div>
          <div className="h-1/3 overflow-hidden">
            <img src="https://images.unsplash.com/photo-1540518614846-7eded433c457?q=80&w=2626&auto=format&fit=crop" alt="Bedroom" className="w-full h-full object-cover grayscale hover:grayscale-0 transition-all" />
          </div>
          <div className="h-1/3 overflow-hidden">
            <img src="https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?q=80&w=2574&auto=format&fit=crop" alt="Bathroom" className="w-full h-full object-cover grayscale hover:grayscale-0 transition-all" />
          </div>
        </div>
      </section>

      <div className="grid lg:grid-cols-12 gap-16">
        <div className="lg:col-span-8 flex flex-col gap-16">
          {/* Header Info */}
          <section className="border-b border-outline-variant pb-12">
            <div className="flex flex-col md:flex-row justify-between items-start gap-8 mb-12">
              <div className="space-y-6">
                <span className="editorial-label text-primary">Residence No. 042</span>
                <h1 className="font-serif text-[64px] font-black italic tracking-tight leading-[0.85]">静谧雅筑 · 全景落地窗高层公寓</h1>
                <p className="flex items-center gap-2 editorial-label">
                  <MapPin className="w-4 h-4" /> 朝阳区，望京SOHO附近 1.2km
                </p>
              </div>
              <div className="text-right flex flex-col items-end">
                <div className="editorial-label opacity-40 mb-2">Monthly Lease</div>
                <div className="font-serif text-6xl text-on-background font-black italic tracking-tight">¥12,500<span className="text-lg font-sans font-normal ml-2 opacity-40 italic">/ pm</span></div>
                <div className="mt-8 flex flex-col sm:flex-row gap-4 w-full">
                  <button className="bg-on-background text-white px-10 py-5 hover:bg-primary transition-all editorial-label text-center">Book Viewing</button>
                  <button className="border border-outline text-on-background px-10 py-5 hover:bg-surface transition-all editorial-label flex items-center justify-center gap-2 whitespace-nowrap">
                    <MessageSquare className="w-5 h-5" /> Message Owner
                  </button>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-2 lg:grid-cols-4 gap-px bg-outline-variant border border-outline-variant">
              <MetaTag label="Layout" value="2室1厅1卫" />
              <MetaTag label="Area" value="89 Sqm" />
              <MetaTag label="Floor" value="Mid-Level" />
              <MetaTag label="Direct" value="South" />
            </div>
          </section>

          {/* Description */}
          <section className="space-y-8">
            <h2 className="font-serif text-3xl">房源描述</h2>
            <div className="text-body-large text-on-surface-variant space-y-6 leading-relaxed">
              <p>这套精致的两居室公寓位于繁华的望京商圈核心地带，为追求生活品质的都市精英提供了一处静密性的休憩之所。公寓采用现代极简主义设计，全屋铺设高级橡木地板，搭配温润的米色系墙面，营造出舒适宁静的居住氛围。</p>
              <p>宽敞的客厅配备了全景落地窗，不仅保证了极佳的采光，还能让您在夜晚俯瞰迷人的城市天际线。开放式厨房配备了全套高端嵌入式电器，满足您对烹饪的所有期待。</p>
            </div>
          </section>

          {/* Amenities */}
          <section className="space-y-8">
            <h2 className="font-serif text-3xl">房屋配置</h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <Amenity icon={Wifi} label="无线网络" />
              <Amenity icon={Wind} label="中央空调" />
              <Amenity icon={WashingMachine} label="洗衣机" />
              <Amenity icon={Refrigerator} label="冰箱" />
              <Amenity icon={Tv} label="智能电视" />
              <Amenity icon={Flame} label="暖气" />
              <Amenity icon={Building2} label="阳台" />
              <ElevatorIcon />
            </div>
          </section>
        </div>

        {/* Sidebar */}
        <aside className="lg:col-span-4 flex flex-col gap-12">
          {/* Landlord Card */}
          <div className="bg-white border border-outline p-10 space-y-8">
            <h3 className="editorial-label">Curator Information</h3>
            <div className="flex items-center gap-6">
              <img src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?q=80&w=2670&auto=format&fit=crop" alt="Sarah" className="w-20 h-20 grayscale border border-outline-variant" />
              <div className="space-y-1">
                <div className="text-2xl font-serif font-black italic">Sarah Li</div>
                <div className="editorial-label text-primary flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3" /> Certified Curator
                </div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-8 py-6 border-y border-outline-variant text-left">
              <div>
                <div className="text-2xl font-serif font-black italic">4.9</div>
                <div className="editorial-label opacity-40">Rating</div>
              </div>
              <div>
                <div className="text-2xl font-serif font-black italic">12</div>
                <div className="editorial-label opacity-40">Invites</div>
              </div>
              <div>
                <div className="text-2xl font-serif font-black italic">3</div>
                <div className="editorial-label opacity-40">Spaces</div>
              </div>
            </div>
            <button className="w-full bg-on-background text-white py-4 editorial-label hover:bg-primary transition-all">Manifesto Profile</button>
          </div>

          {/* Map/Location */}
          <div className="bg-white border border-outline p-10 space-y-6">
            <h3 className="editorial-label">Coordinates</h3>
            <div className="aspect-square bg-surface-variant flex items-center justify-center relative overflow-hidden group border border-outline-variant">
              <MapIcon className="w-12 h-12 text-outline opacity-20" />
              <img 
                src="https://images.unsplash.com/photo-1524661135-423995f22d0b?q=80&w=2674&auto=format&fit=crop" 
                alt="Map View" 
                className="absolute inset-0 w-full h-full object-cover opacity-20 grayscale" 
              />
            </div>
            <div className="space-y-4 font-serif text-lg text-secondary leading-relaxed italic">
              <p>Located in the heart of Chaoyang, 800m from the geometric precision of Wangjing Station.</p>
              <p>Surrounded by silent architecture and premium amenities.</p>
            </div>
          </div>
        </aside>
      </div>
    </div>
  );
}

function MetaTag({ label, value }: { label: string, value: string }) {
  return (
    <div className="bg-background px-6 py-6 flex flex-col gap-2">
      <span className="editorial-label text-primary">{label}</span>
      <span className="font-serif font-black italic text-lg">{value}</span>
    </div>
  );
}

function Amenity({ icon: Icon, label }: { icon: any, label: string }) {
  return (
    <div className="flex items-center gap-3 text-on-surface-variant group">
      <Icon className="w-5 h-5 text-secondary group-hover:text-primary transition-colors" />
      <span className="text-sm font-medium">{label}</span>
    </div>
  );
}

function ElevatorIcon() {
  return (
    <div className="flex items-center gap-3 text-on-surface-variant group">
      <ArrowUpDown className="w-5 h-5 text-secondary group-hover:text-primary transition-colors" />
      <span className="text-sm font-medium">电梯</span>
    </div>
  );
}
