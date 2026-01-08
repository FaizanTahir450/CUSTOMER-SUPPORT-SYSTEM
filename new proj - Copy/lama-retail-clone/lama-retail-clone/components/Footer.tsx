
import React from 'react';

const FooterLink: React.FC<{ href: string; children: React.ReactNode }> = ({ href, children }) => (
  <a href={href} className="text-gray-500 hover:text-gray-800 transition-colors">{children}</a>
);

const Footer: React.FC = () => {
  return (
    <footer className="bg-white border-t border-gray-200">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Categories */}
          <div>
            <h3 className="text-lg font-bold mb-4">Categories</h3>
            <ul className="space-y-2">
              <li><FooterLink href="#">Women</FooterLink></li>
              <li><FooterLink href="#">Men</FooterLink></li>
              <li><FooterLink href="#">Shoes</FooterLink></li>
              <li><FooterLink href="#">Accessories</FooterLink></li>
              <li><FooterLink href="#">New Arrivals</FooterLink></li>
            </ul>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-lg font-bold mb-4">Links</h3>
            <ul className="space-y-2">
              <li><FooterLink href="#">FAQ</FooterLink></li>
              <li><FooterLink href="#">Pages</FooterLink></li>
              <li><FooterLink href="#">Stores</FooterLink></li>
              <li><FooterLink href="#">Compare</FooterLink></li>
              <li><FooterLink href="#">Cookies</FooterLink></li>
            </ul>
          </div>

          {/* About */}
          <div>
            <h3 className="text-lg font-bold mb-4">About</h3>
            <p className="text-gray-500 leading-relaxed">
              Discover the latest trends in fashion with LAMA. We offer high-quality apparel and accessories for every occasion. Our mission is to provide stylish and affordable fashion for everyone.
            </p>
          </div>

          {/* Contact */}
          <div>
            <h3 className="text-lg font-bold mb-4">Contact</h3>
            <p className="text-gray-500 leading-relaxed">
              Have questions? Reach out to us anytime! We are here to help you with your orders, returns, and any other inquiries. Your satisfaction is our priority.
            </p>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center mt-12 pt-8 border-t border-gray-200">
          <div className="flex items-center space-x-4 mb-4 md:mb-0">
            <span className="text-2xl font-extrabold text-secondary">LAMA</span>
            <span className="text-gray-400 text-sm">&copy; {new Date().getFullYear()} All Rights Reserved</span>
          </div>
          <div>
            <img src="https://i.ibb.co/Qfvn4z6/payment.png" alt="Payment methods" className="h-8"/>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
