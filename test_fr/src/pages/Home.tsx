import { Search, MapPin, ArrowRight, ShieldCheck, Palette, Sparkles, LayoutPanelLeft, BedDouble, Bath } from 'lucide-react';
import { motion } from 'motion/react';
import { Link } from 'react-router-dom';
import { PROPERTIES } from '../data';

export default function Home() {
  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-12 lg:py-24 grid lg:grid-cols-12 gap-12 items-center border-b border-outline-variant">
        <motion.div 
          initial={{ opacity: 0, x: -30 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="lg:col-span-12 flex flex-col items-center text-center gap-10"
        >
          <div className="flex flex-col items-center">
            <span className="editorial-label text-[#D4AF37] mb-6">Manifesto 01 — Modern Living</span>
            <h1 className="font-serif text-[80px] md:text-[120px] font-black leading-[0.85] tracking-[-0.04em] mb-8">
              THE QUIET<br />HABITAT
            </h1>
          </div>
          
          <p className="text-xl md:text-2xl font-serif italic max-w-2xl text-secondary leading-relaxed">
            Exploring the intersection of brutalist architecture and organic minimalism in the heart of modern-day sanctuary.
          </p>

          <div className="bg-white border border-outline p-2 flex flex-col sm:flex-row gap-2 w-full max-w-2xl">
            <div className="flex flex-1 items-center px-4 gap-3">
              <Search className="text-outline w-5 h-5 opacity-40" />
              <input 
                type="text" 
                placeholder="Where should quiet take you? (Location, vibe, or city...)" 
                className="w-full h-12 bg-transparent focus:outline-none editorial-label opacity-100 placeholder:opacity-30 p-0 text-left capitalize"
              />
            </div>
            <button className="bg-on-background text-white px-10 py-3 hover:bg-primary transition-colors whitespace-nowrap editorial-label">
              Inquire
            </button>
          </div>
        </motion.div>
      </section>

      {/* Featured Vertical Layout Integration */}
      <section className="max-w-7xl mx-auto flex flex-col md:flex-row border-b border-outline-variant">
        <div className="md:w-3/5 p-12 border-r border-outline-variant flex flex-col gap-8">
          <div className="aspect-[16/9] w-full bg-surface-variant overflow-hidden">
            <img 
              src="https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?q=80&w=2670&auto=format&fit=crop" 
              alt="Featured Interior" 
              className="w-full h-full object-cover grayscale hover:grayscale-0 transition-all duration-700"
            />
          </div>
          <div className="space-y-4">
            <span className="editorial-label text-[#D4AF37]">Photography by Julian V. Rossi</span>
            <h2 className="font-serif text-4xl font-black italic">A Study of Forms & Silence</h2>
            <p className="text-lg leading-relaxed font-serif text-secondary max-w-xl">
              Concrete Softness: How the use of raw materials is redefining luxury interiors in 2024.
            </p>
          </div>
        </div>
        <div className="md:w-2/5 flex flex-col">
          <div className="p-12 border-b border-outline-variant">
            <h3 className="editorial-label mb-8">Recent Dispatches</h3>
            <div className="space-y-10 text-left">
              <article className="group cursor-pointer">
                <div className="editorial-label text-primary mb-2">01 / Architecture</div>
                <h4 className="text-xl font-serif leading-tight group-hover:underline">The Serif Resurgence</h4>
              </article>
              <article className="group cursor-pointer">
                <div className="editorial-label text-primary mb-2">02 / Lifestyle</div>
                <h4 className="text-xl font-serif leading-tight group-hover:underline">Silence as a Service</h4>
              </article>
            </div>
          </div>
          <div className="flex-1 bg-on-background p-12 text-background flex flex-col justify-between items-start text-left">
            <div>
              <p className="editorial-label text-background font-normal mb-4 opacity-70">Weekly Briefing</p>
              <h5 className="text-2xl font-serif italic text-left">Join the inner circle for exclusive design insights.</h5>
            </div>
            <div className="w-full flex border-b border-background/30 pb-2 mt-8">
              <input type="text" placeholder="Email address" className="bg-transparent text-[12px] w-full focus:outline-none placeholder:text-background/30" />
              <button className="editorial-label text-background">Send</button>
            </div>
          </div>
        </div>
      </section>

      {/* Philosophy */}
      <section className="border-b border-outline-variant py-24 bg-surface">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-left mb-16 space-y-4 max-w-xl">
            <span className="editorial-label text-primary">Our Ethos</span>
            <h2 className="font-serif text-5xl font-black italic">Curating Quality & Discretion</h2>
            <p className="text-secondary leading-relaxed font-serif text-lg">以匠心打造平台，让每一次租赁都充满信任与宁静。We believe that physical space should reinforce mental clarity.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-12 text-left">
            <FeatureCard 
              icon={ShieldCheck}
              title="Verified Truth"
              description="所有房源均经过严格的人工实地勘验，确保信息真实无误，杜绝虚假承诺。"
            />
            <FeatureCard 
              icon={Palette}
              title="Aesthetic Intent"
              description="我们精选具有设计感和生活品质的房源，满足您对居住空间的挑剔眼光。"
            />
            <FeatureCard 
              icon={Sparkles}
              title="Quiet Process"
              description="从看房到签约，提供全程无打扰的专业管家服务，让租房过程如流水般自然。"
            />
          </div>
        </div>
      </section>

      {/* Featured Listings */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <div className="flex justify-between items-end mb-12 border-b border-outline-variant pb-8">
          <div className="space-y-4">
            <span className="editorial-label text-primary">Collection 01</span>
            <h2 className="font-serif text-5xl font-black">Featured Habitats</h2>
          </div>
          <Link to="/explore" className="editorial-label flex items-center gap-2 hover:text-primary pb-1 border-b border-on-background">
            View All <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        <div className="grid md:grid-cols-12 gap-12">
          {PROPERTIES.map((prop, idx) => (
            <Link 
              key={prop.id}
              to={`/property/${prop.id}`}
              className={`${idx === 0 ? 'md:col-span-8' : 'md:col-span-4'} group cursor-pointer flex flex-col gap-6`}
            >
              <div className="aspect-[4/3] overflow-hidden bg-surface-variant">
                <img src={prop.image} alt={prop.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 grayscale hover:grayscale-0" />
              </div>
              <div className="flex flex-col gap-3">
                <div className="flex justify-between items-baseline">
                  <h3 className="font-serif text-3xl font-black italic">{prop.title}</h3>
                  <div className="editorial-label">From ¥{prop.price.toLocaleString()}</div>
                </div>
                <div className="editorial-label opacity-40 flex items-center gap-2">
                  <MapPin className="w-3 h-3" />
                  {prop.location}
                </div>
                <div className="flex gap-4 pt-4 border-t border-outline-variant/30 editorial-label opacity-60">
                  <span>{prop.sqm} sqm</span>
                  <span>{prop.beds} Beds</span>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </section>
    </div>
  );
}

function FeatureCard({ icon: Icon, title, description }: { icon: any, title: string, description: string }) {
  return (
    <div className="flex flex-col gap-6 group text-left">
      <div className="w-12 h-12 border border-outline-variant flex items-center justify-center transition-colors group-hover:bg-on-background group-hover:text-background">
        <Icon className="w-6 h-6" />
      </div>
      <div className="space-y-4">
        <h3 className="font-serif text-2xl font-black italic">{title}</h3>
        <p className="text-secondary leading-relaxed font-serif">{description}</p>
      </div>
    </div>
  );
}
