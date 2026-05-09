import { Search, MapPin, LayoutPanelLeft, BedDouble, Bath, ChevronDown, SlidersHorizontal } from 'lucide-react';
import { motion } from 'motion/react';
import { Link } from 'react-router-dom';
import { PROPERTIES } from '../data';

export default function Explore() {
  return (
    <div className="max-w-7xl mx-auto px-6 py-12 lg:py-24 flex flex-col gap-12">
      <header className="flex flex-col md:flex-row justify-between items-end gap-8 border-b border-outline-variant pb-12">
        <div className="space-y-4">
          <span className="editorial-label text-primary">Manifesto 02 — Spaces</span>
          <h1 className="font-serif text-[64px] font-black italic tracking-tight leading-none">Curated Spaces</h1>
          <p className="text-xl font-serif italic text-secondary">Discover your serene sanctuary (发现适合您的静谧栖息地)</p>
        </div>

        <div className="flex flex-wrap items-center gap-4">
          <FilterButton label="Location" />
          <FilterButton label="Rent" />
          <FilterButton label="Type" />
          <button className="flex items-center gap-2 px-8 py-3 bg-on-background text-white editorial-label transition-colors hover:bg-primary">
            <SlidersHorizontal className="w-4 h-4" />
            Filters
          </button>
        </div>
      </header>

      <div className="flex justify-between items-center py-4">
        <span className="editorial-label opacity-40">124 Selections Found</span>
        <div className="flex items-center gap-8 editorial-label">
          <span className="opacity-30">Sort By:</span>
          <button className="text-on-background border-b border-on-background pb-1 outline-none">Default</button>
          <button className="opacity-40 hover:opacity-100 transition-opacity">Price</button>
          <button className="opacity-40 hover:opacity-100 transition-opacity">Newest</button>
        </div>
      </div>

      <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-12 mb-12">
        {PROPERTIES.concat(PROPERTIES).map((prop, idx) => (
          <Link 
            key={`${prop.id}-${idx}`}
            to={`/property/${prop.id}`}
            className="group flex flex-col gap-6"
          >
            <div className="aspect-[4/3] overflow-hidden relative bg-surface-variant">
              <img src={prop.image} alt={prop.title} className="w-full h-full object-cover grayscale hover:grayscale-0 transition-all duration-1000" />
              {idx === 0 && (
                <div className="absolute top-0 left-0 bg-primary px-3 py-1 editorial-label text-white">
                  New Arrival
                </div>
              )}
            </div>
            <div className="flex flex-col gap-4">
              <div className="flex justify-between items-start">
                <h2 className="font-serif text-3xl font-black italic group-hover:underline transition-colors leading-tight">{prop.title}</h2>
              </div>
              <div className="editorial-label opacity-40 flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                {prop.location}
              </div>
              <div className="flex gap-4 pt-4 border-t border-outline-variant/30 editorial-label opacity-60">
                <span>{prop.sqm} sqm</span>
                <span>{prop.beds} Beds</span>
                <span>South</span>
              </div>
              <div className="flex justify-between items-end pt-2">
                <div className="font-serif text-3xl italic">¥{prop.price.toLocaleString()}<span className="text-sm font-sans font-normal opacity-40 lowercase">/ month</span></div>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

function FilterButton({ label }: { label: string }) {
  return (
    <button className="flex items-center gap-2 px-6 py-2 bg-white border border-outline-variant rounded-full text-xs font-bold uppercase transition-colors hover:border-primary">
      {label} <ChevronDown className="w-3 h-3" />
    </button>
  );
}
