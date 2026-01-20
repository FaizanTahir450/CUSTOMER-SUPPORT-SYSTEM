
import React from 'react';
import { Product } from '../types';

interface ProductCardProps {
  product: Product;
}

const ProductCard: React.FC<ProductCardProps> = ({ product }) => {
  return (
    <div className="group relative animate-fade-in-up">
      <div className="aspect-w-3 aspect-h-4 w-full overflow-hidden rounded-lg bg-gray-100">
        <img
          src={product.imageUrl}
          alt={product.name}
          className="h-full w-full object-cover object-center transition-transform duration-500 group-hover:scale-110"
        />
        {product.isNew && (
          <span className="absolute top-3 left-3 bg-white text-primary text-xs font-semibold px-3 py-1 rounded-md shadow">
            New Season
          </span>
        )}
      </div>
      <div className="mt-4 flex justify-between">
        <div>
          <h3 className="text-md text-gray-700">
            <a href="#">
              <span aria-hidden="true" className="absolute inset-0" />
              {product.name}
            </a>
          </h3>
        </div>
        <p className="text-md font-medium text-gray-900">{product.price}</p>
      </div>
    </div>
  );
};

export default ProductCard;
