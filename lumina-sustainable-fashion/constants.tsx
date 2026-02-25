
import React from 'react';
import { Product } from './types';

export const PRODUCTS: Product[] = [
  {
    id: '1',
    name: 'Essential Organic Tee',
    price: 45,
    category: 'Tops',
    image: 'https://picsum.photos/id/1011/600/800',
    description: '100% GOTS certified organic cotton t-shirt with a relaxed fit.'
  },
  {
    id: '2',
    name: 'Linen Chore Coat',
    price: 185,
    category: 'Outerwear',
    image: 'https://picsum.photos/id/1020/600/800',
    description: 'Sustainable linen blend jacket, perfect for transitional layering.'
  },
  {
    id: '3',
    name: 'Recycled Denim Jeans',
    price: 120,
    category: 'Bottoms',
    image: 'https://picsum.photos/id/1025/600/800',
    description: 'High-waisted straight leg jeans made from 80% recycled post-consumer denim.'
  },
  {
    id: '4',
    name: 'Silk Slip Dress',
    price: 240,
    category: 'Dresses',
    image: 'https://picsum.photos/id/1033/600/800',
    description: 'Eco-conscious silk slip dress with adjustable straps and a side slit.'
  },
  {
    id: '5',
    name: 'Canvas Tote Bag',
    price: 35,
    category: 'Accessories',
    image: 'https://picsum.photos/id/1043/600/800',
    description: 'Heavyweight organic cotton canvas tote for all your essentials.'
  },
  {
    id: '6',
    name: 'Knit Merino Sweater',
    price: 160,
    category: 'Knitwear',
    image: 'https://picsum.photos/id/1050/600/800',
    description: 'Responsibly sourced merino wool sweater with a chunky knit texture.'
  }
];

export const NAV_LINKS = [
  { name: 'Home', path: '/' },
  { name: 'Shop All', path: '/shop' },
  { name: 'Collections', path: '/#collections' },
  { name: 'About', path: '/#about' },
];
