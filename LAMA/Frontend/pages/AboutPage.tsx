
import React from 'react';

const AboutPage: React.FC = () => {
  return (
    <div className="animate-fade-in">
      <div className="bg-gray-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight">About LAMA</h1>
          <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
            Dressing the world, one person at a time.
          </p>
        </div>
      </div>

      <div className="py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div className="animate-fade-in-up">
              <img
                src="https://picsum.photos/800/600?random=11"
                alt="Our team"
                className="rounded-lg shadow-2xl"
              />
            </div>
            <div className="prose prose-lg text-gray-600 max-w-none animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
              <h2 className="text-3xl font-bold text-gray-900">Our Story</h2>
              <p>
                Founded in 2010, LAMA began with a simple idea: to create fashion that is not only beautiful and trendy but also accessible and sustainable. We believe that style is a form of self-expression, and everyone deserves to feel confident in what they wear.
              </p>
              <p>
                From a small boutique in the heart of the fashion district, we have grown into a global brand, but our core values remain the same. We are committed to quality craftsmanship, ethical sourcing, and creating timeless pieces that you'll love for years to come.
              </p>
              <h2 className="text-3xl font-bold text-gray-900 mt-8">Our Mission</h2>
              <p>
                Our mission is to empower individuals through fashion. We strive to inspire confidence and creativity by offering a diverse range of clothing and accessories that cater to all styles and personalities. We are dedicated to making a positive impact on the fashion industry and the world by prioritizing sustainability and ethical practices in everything we do.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
