import { create } from 'zustand';

interface Property {
  id: string;
  title: string;
  location: string;
  price: number;
  image: string;
  sqm: number;
  beds: number;
  baths: number;
  tags: string[];
  type: 'Premium' | 'Standard';
}

export const PROPERTIES: Property[] = [
  {
    id: '1',
    title: '静安区 · 采光极佳的艺术Loft',
    location: '上海市静安区武定路',
    price: 12000,
    image: 'https://images.unsplash.com/photo-1536376074432-bf72346fbd14?q=80&w=2670&auto=format&fit=crop',
    sqm: 120,
    beds: 2,
    baths: 2,
    tags: ['最新上架'],
    type: 'Premium'
  },
  {
    id: '2',
    title: '徐汇区 · 林荫道旁的日式庭院洋房',
    location: '湖南路历史文化风貌区',
    price: 18500,
    image: 'https://images.unsplash.com/photo-1544457070-4cd773b4d71e?q=80&w=2626&auto=format&fit=crop',
    sqm: 150,
    beds: 3,
    baths: 2,
    tags: ['花园别墅'],
    type: 'Premium'
  },
  {
    id: '3',
    title: '黄浦区 · 拥抱江景的现代平层',
    location: '南外滩滨江区',
    price: 25000,
    image: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?q=80&w=2580&auto=format&fit=crop',
    sqm: 180,
    beds: 3,
    baths: 3,
    tags: ['江景房'],
    type: 'Premium'
  }
];
