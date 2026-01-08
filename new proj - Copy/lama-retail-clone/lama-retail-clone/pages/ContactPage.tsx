
import React from 'react';

const ContactInfoItem: React.FC<{ icon: React.ReactNode; title: string; children: React.ReactNode }> = ({ icon, title, children }) => (
  <div className="flex items-start space-x-4">
    <div className="flex-shrink-0 w-12 h-12 bg-primary text-white rounded-full flex items-center justify-center">
      {icon}
    </div>
    <div>
      <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
      <p className="text-gray-500 mt-1">{children}</p>
    </div>
  </div>
);


const ContactPage: React.FC = () => {
  return (
    <div className="animate-fade-in">
       <div className="bg-gray-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-16 text-center">
          <h1 className="text-5xl font-extrabold text-gray-900 tracking-tight">Get In Touch</h1>
          <p className="mt-4 max-w-3xl mx-auto text-xl text-gray-500">
            We'd love to hear from you. Here's how you can reach us.
          </p>
        </div>
      </div>
      <div className="py-16 lg:py-24">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16">
            {/* Contact Form */}
            <div className="bg-white p-8 rounded-lg shadow-lg animate-fade-in-up">
              <h2 className="text-3xl font-bold text-gray-900 mb-6">Send a Message</h2>
              <form className="space-y-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700">Full Name</label>
                  <input type="text" id="name" className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary" placeholder="Jane Doe"/>
                </div>
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700">Email Address</label>
                  <input type="email" id="email" className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary" placeholder="jane.doe@example.com"/>
                </div>
                <div>
                  <label htmlFor="message" className="block text-sm font-medium text-gray-700">Message</label>
                  <textarea id="message" rows={5} className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-md shadow-sm focus:ring-primary focus:border-primary" placeholder="Your message here..."></textarea>
                </div>
                <div>
                  <button type="submit" className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-lg font-medium text-white bg-primary hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors">
                    Submit
                  </button>
                </div>
              </form>
            </div>

             {/* Contact Info */}
            <div className="space-y-8 animate-fade-in-up" style={{ animationDelay: '0.2s' }}>
                <ContactInfoItem icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"></path><circle cx="12" cy="10" r="3"></circle></svg>} title="Our Address">
                    123 Fashion Ave, Suite 456<br/>
                    New York, NY 10001, USA
                </ContactInfoItem>
                 <ContactInfoItem icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>} title="Call Us">
                    (555) 123-4567<br/>
                    Mon - Fri, 9am - 5pm EST
                </ContactInfoItem>
                 <ContactInfoItem icon={<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"></rect><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path></svg>} title="Email Us">
                    support@lama.com<br/>
                    We'll reply within 24 hours.
                </ContactInfoItem>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ContactPage;
