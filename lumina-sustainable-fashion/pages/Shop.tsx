
import React from 'react';
import ProductCard from '../components/ProductCard';
import { PRODUCTS } from '../constants';

const Shop: React.FC = () => {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-slate-900 tracking-tight">The Full Collection</h1>
        <p className="text-slate-500 mt-4 text-lg">Browse our entire range of sustainable premium clothing.</p>
      </div>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-x-8 gap-y-12">
        {PRODUCTS.map(product => (
          <ProductCard key={product.id} product={product} />
        ))}
      </div>
    </div>
  );
};

export default Shop;
