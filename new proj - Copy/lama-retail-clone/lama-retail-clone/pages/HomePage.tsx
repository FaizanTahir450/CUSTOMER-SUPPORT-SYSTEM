
import React from 'react';
import { Link } from 'react-router-dom';
import ProductCard from '../components/ProductCard';
import { Product } from '../types';

const featuredProducts: Product[] = [
  { id: 1, name: 'Elegant Blouse', price: '$59.99', imageUrl: 'https://picsum.photos/400/500?random=1', isNew: true },
  { id: 2, name: 'Classic Trench Coat', price: '$189.99', imageUrl: 'https://picsum.photos/400/500?random=2' },
  { id: 3, name: 'Leather Ankle Boots', price: '$129.99', imageUrl: 'https://picsum.photos/400/500?random=3' },
  { id: 4, name: 'Silk Scarf', price: '$39.99', imageUrl: 'https://picsum.photos/400/500?random=4', isNew: true },
];

const trendingProducts: Product[] = [
    { id: 5, name: 'Denim Jacket', price: '$89.99', imageUrl: 'https://picsum.photos/400/500?random=5', isNew: true },
    { id: 6, name: 'Striped T-Shirt', price: '$29.99', imageUrl: 'https://picsum.photos/400/500?random=6' },
    { id: 7, name: 'High-Waist Jeans', price: '$79.99', imageUrl: 'https://picsum.photos/400/500?random=7' },
    { id: 8, name: 'Canvas Tote Bag', price: '$49.99', imageUrl: 'https://picsum.photos/400/500?random=8', isNew: true },
];

const CategoryButton: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <button className="relative w-full h-full text-white font-bold text-xl uppercase tracking-wider overflow-hidden rounded-lg shadow-lg group">
        <img src={`https://picsum.photos/800/600?random=${Math.floor(Math.random()*100)}`} className="absolute inset-0 w-full h-full object-cover transition-transform duration-500 group-hover:scale-110" alt="Category"/>
        <div className="absolute inset-0 bg-black bg-opacity-30"></div>
        <span className="relative z-10">{children}</span>
    </button>
);


const HomePage: React.FC = () => {
  return (
    <div className="animate-fade-in">
      {/* Hero Section */}
      <div className="relative h-[calc(100vh-80px)] w-full">
        <div className="absolute inset-0">
            <img src="https://picsum.photos/1920/1080?random=10" alt="Hero 1" className="w-full h-full object-cover"/>
        </div>
        <div className="absolute bottom-20 left-1/2 -translate-x-1/2 flex space-x-4">
            <Link to="/products" className="px-8 py-3 border border-gray-800 text-gray-800 bg-white bg-opacity-80 backdrop-blur-sm font-semibold hover:bg-gray-800 hover:text-white transition-all duration-300 rounded-md">
                Shop Men
            </Link>
            <Link to="/products" className="px-8 py-3 border border-gray-800 text-gray-800 bg-white bg-opacity-80 backdrop-blur-sm font-semibold hover:bg-gray-800 hover:text-white transition-all duration-300 rounded-md">
                Shop Women
            </Link>
        </div>
      </div>

      {/* Categories Section */}
      <section className="py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-2 md:grid-cols-4 grid-rows-2 gap-4 h-[70vh]">
                <div className="col-span-1 row-span-1"><CategoryButton>Sale</CategoryButton></div>
                <div className="col-span-1 row-span-1"><CategoryButton>Women</CategoryButton></div>
                <div className="col-span-1 row-span-2"><CategoryButton>New Season</CategoryButton></div>
                <div className="col-span-2 row-span-1"><CategoryButton>Men</CategoryButton></div>
                <div className="col-span-1 row-span-1"><CategoryButton>Accessories</CategoryButton></div>
            </div>
        </div>
      </section>

      {/* Featured Products */}
      <section className="py-16 lg:py-24 bg-gray-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 animate-fade-in-up">
            <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">Featured Products</h2>
            <p className="mt-4 max-w-2xl mx-auto text-lg text-gray-500">
              Handpicked styles that are setting the trend this season.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-y-10 sm:grid-cols-2 lg:grid-cols-4 gap-x-6">
            {featuredProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>
      
      {/* Trending Products */}
      <section className="py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 animate-fade-in-up">
            <h2 className="text-4xl font-extrabold tracking-tight text-gray-900 sm:text-5xl">Trending Now</h2>
            <p className="mt-4 max-w-2xl mx-auto text-lg text-gray-500">
              See what's popular and join the style wave.
            </p>
          </div>
          <div className="grid grid-cols-1 gap-y-10 sm:grid-cols-2 lg:grid-cols-4 gap-x-6">
            {trendingProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </div>
      </section>

      {/* Contact/Newsletter Section */}
      <section className="bg-primary py-12">
          <div className="container mx-auto px-4 sm:px-6 lg:px-8 text-white flex flex-col md:flex-row justify-center items-center text-center md:text-left space-y-4 md:space-y-0 md:space-x-8">
              <h3 className="text-2xl font-semibold uppercase tracking-wider">Be in touch with us:</h3>
              <div className="flex bg-white rounded-md overflow-hidden">
                  <input type="email" placeholder="Enter your e-mail..." className="px-4 py-2 text-gray-800 focus:outline-none"/>
                  <button className="px-6 py-2 bg-secondary text-white font-semibold hover:bg-gray-700 transition-colors">JOIN US</button>
              </div>
          </div>
      </section>
    </div>
  );
};

export default HomePage;
