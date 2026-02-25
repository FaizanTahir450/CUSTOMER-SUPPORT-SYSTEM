
import React from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { PRODUCTS } from '../constants';

const Home: React.FC = () => {
  const featuredProducts = PRODUCTS.slice(0, 4);

  return (
    <div className="space-y-24 pb-24">
      {/* Hero Section */}
      <section className="relative h-[80vh] flex items-center justify-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img 
            src="https://picsum.photos/id/1015/1920/1080" 
            alt="Hero background" 
            className="w-full h-full object-cover filter brightness-[0.8]"
          />
        </div>
        <div className="relative z-10 text-center text-white px-4">
          <span className="inline-block px-4 py-1.5 bg-white/20 backdrop-blur-md rounded-full text-xs font-semibold uppercase tracking-widest mb-6 border border-white/20">
            Season 2024 Collection
          </span>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-tight">
            Sustainability Meets <br /> Sophistication
          </h1>
          <p className="max-w-xl mx-auto text-lg md:text-xl text-slate-100 mb-10 leading-relaxed">
            Discover a curated collection of essentials designed for the conscious modern individual. Ethically sourced and beautifully crafted.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link to="/shop" className="px-8 py-4 bg-white text-slate-900 font-bold rounded-full hover:bg-slate-100 transition-all shadow-xl">
              Shop The Collection
            </Link>
            <Link to="/support" className="px-8 py-4 bg-white/10 backdrop-blur-md text-white border border-white/30 font-bold rounded-full hover:bg-white/20 transition-all">
              Live Support
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
          <div className="space-y-4">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"></path>
              </svg>
            </div>
            <h3 className="text-xl font-bold text-slate-900">Eco-Friendly Materials</h3>
            <p className="text-slate-500 leading-relaxed">We exclusively use GOTS organic cotton and recycled fibers to minimize our environmental footprint.</p>
          </div>
          <div className="space-y-4">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <h3 className="text-xl font-bold text-slate-900">Ethical Pricing</h3>
            <p className="text-slate-500 leading-relaxed">Direct-to-consumer model ensures fair wages for artisans and premium quality without traditional markups.</p>
          </div>
          <div className="space-y-4">
            <div className="w-12 h-12 bg-indigo-50 text-indigo-600 rounded-2xl flex items-center justify-center mx-auto mb-6">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path>
              </svg>
            </div>
            <h3 className="text-xl font-bold text-slate-900">Gives Back</h3>
            <p className="text-slate-500 leading-relaxed">Every purchase contributes to re-forestation projects worldwide. Over 1 million trees planted to date.</p>
          </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-end mb-12">
          <div>
            <h2 className="text-3xl font-bold text-slate-900">Featured Essentials</h2>
            <p className="text-slate-500 mt-2">Timeless designs for your everyday rotation.</p>
          </div>
          <Link to="/shop" className="text-indigo-600 font-bold hover:text-indigo-700 transition-colors inline-flex items-center gap-2">
            View All <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
          </Link>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
          {featuredProducts.map(product => (
            <ProductCard key={product.id} product={product} />
          ))}
        </div>
      </section>

      {/* CTA Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-slate-900 rounded-[3rem] overflow-hidden relative">
          <div className="absolute inset-0 opacity-20 bg-[radial-gradient(circle_at_top_right,indigo,transparent_50%)]" />
          <div className="relative px-8 py-20 md:px-20 text-center max-w-3xl mx-auto space-y-8">
            <h2 className="text-3xl md:text-5xl font-bold text-white tracking-tight">Need help finding your perfect fit?</h2>
            <p className="text-slate-400 text-lg">Our AI support agent is available 24/7 to guide you through sizing, materials, and styling tips.</p>
            <Link to="/support" className="inline-block px-10 py-4 bg-indigo-600 text-white font-bold rounded-full hover:bg-indigo-700 transition-all shadow-xl shadow-indigo-600/20">
              Start Chatting Now
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
