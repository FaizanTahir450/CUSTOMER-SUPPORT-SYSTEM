
import React from 'react';
import ProductCard from '../components/ProductCard';
import { Product } from '../types';

const allProducts: Product[] = [
  { id: 1, name: 'Summer Floral Dress', price: '$79.99', imageUrl: 'https://picsum.photos/400/500?random=21', isNew: true },
  { id: 2, name: 'Men\'s Leather Jacket', price: '$249.99', imageUrl: 'https://picsum.photos/400/500?random=22' },
  { id: 3, name: 'Vintage Wash Jeans', price: '$89.99', imageUrl: 'https://picsum.photos/400/500?random=23' },
  { id: 4, name: 'Cashmere Sweater', price: '$159.99', imageUrl: 'https://picsum.photos/400/500?random=24', isNew: true },
  { id: 5, name: 'Urban Sneakers', price: '$119.99', imageUrl: 'https://picsum.photos/400/500?random=25' },
  { id: 6, name: 'Silk Button-Up Shirt', price: '$99.99', imageUrl: 'https://picsum.photos/400/500?random=26' },
  { id: 7, name: 'Wool Peacoat', price: '$299.99', imageUrl: 'https://picsum.photos/400/500?random=27', isNew: true },
  { id: 8, name: 'Classic Chronograph Watch', price: '$349.99', imageUrl: 'https://picsum.photos/400/500?random=28' },
];

const FilterSection: React.FC<{ title: string; children: React.ReactNode }> = ({ title, children }) => (
    <div className="mb-6">
        <h3 className="font-semibold text-lg mb-3">{title}</h3>
        <div className="space-y-2">{children}</div>
    </div>
);

const CheckboxItem: React.FC<{ id: string; label: string }> = ({ id, label }) => (
    <div className="flex items-center">
        <input id={id} type="checkbox" className="h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"/>
        <label htmlFor={id} className="ml-3 text-gray-600">{label}</label>
    </div>
);


const ProductsPage: React.FC = () => {
  return (
    <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12 animate-fade-in">
      <div className="flex flex-col lg:flex-row gap-12">
        {/* Sidebar */}
        <aside className="w-full lg:w-1/4">
          <FilterSection title="Product Categories">
            <CheckboxItem id="women" label="Women" />
            <CheckboxItem id="men" label="Men" />
            <CheckboxItem id="accessories" label="Accessories" />
            <CheckboxItem id="shoes" label="Shoes" />
          </FilterSection>

          <FilterSection title="Filter by price">
             <div className="flex items-center space-x-2 text-gray-600">
                <span>$0</span>
                <input type="range" min="0" max="1000" defaultValue="500" className="w-full"/>
                <span>$1000</span>
             </div>
          </FilterSection>

          <FilterSection title="Sort by">
            <div className="flex items-center">
                <input id="price-asc" name="sort" type="radio" className="h-4 w-4 border-gray-300 text-primary focus:ring-primary"/>
                <label htmlFor="price-asc" className="ml-3 text-gray-600">Price (Lowest first)</label>
            </div>
             <div className="flex items-center">
                <input id="price-desc" name="sort" type="radio" className="h-4 w-4 border-gray-300 text-primary focus:ring-primary"/>
                <label htmlFor="price-desc" className="ml-3 text-gray-600">Price (Highest first)</label>
            </div>
          </FilterSection>
        </aside>

        {/* Product Grid */}
        <main className="w-full lg:w-3/4">
          <div className="relative w-full h-64 rounded-lg overflow-hidden mb-8">
            <img src="https://picsum.photos/1200/400?random=30" alt="Category banner" className="w-full h-full object-cover"/>
            <div className="absolute inset-0 bg-black bg-opacity-30 flex items-center justify-center">
                <h2 className="text-white text-4xl font-extrabold tracking-wider">All Products</h2>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-8">
            {allProducts.map((product) => (
              <ProductCard key={product.id} product={product} />
            ))}
          </div>
        </main>
      </div>
    </div>
  );
};

export default ProductsPage;
