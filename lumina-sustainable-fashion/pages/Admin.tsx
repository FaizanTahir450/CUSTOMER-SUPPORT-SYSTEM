
import React from 'react';
import { Navigate } from 'react-router-dom';
import { authUtils } from '../services/authUtils';
import { PRODUCTS } from '../constants';

const Admin: React.FC = () => {
  const user = authUtils.getUser();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check if user is admin using role field
  if (user.role !== 'admin') {
    return <Navigate to="/" replace />;
  }

  const stats = [
    { name: 'Total Revenue', value: '$45,231', change: '+12.5%', icon: '💰' },
    { name: 'Active Orders', value: '154', change: '+3.2%', icon: '📦' },
    { name: 'Total Customers', value: '2,845', change: '+18.7%', icon: '👥' },
    { name: 'Conversion Rate', value: '4.8%', change: '-0.4%', icon: '📈' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 hidden md:block">
        <div className="p-6">
          <h2 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Dashboard</h2>
          <nav className="mt-6 space-y-1">
            {['Overview', 'Products', 'Orders', 'Customers', 'Marketing', 'Settings'].map((item) => (
              <a
                key={item}
                href="#"
                className={`flex items-center px-4 py-3 text-sm font-medium rounded-xl transition-all ${
                  item === 'Overview' ? 'bg-indigo-50 text-indigo-600' : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                {item}
              </a>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <div className="max-w-6xl mx-auto space-y-8">
          <header className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Admin Dashboard</h1>
              <p className="text-slate-500">Welcome back, {user.name}. Here's what's happening today.</p>
            </div>
            <button className="px-5 py-2.5 bg-indigo-600 text-white font-bold rounded-xl hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-200 flex items-center gap-2">
              <span>+ Add Product</span>
            </button>
          </header>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {stats.map((stat) => (
              <div key={stat.name} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
                <div className="flex justify-between items-start mb-4">
                  <span className="text-2xl">{stat.icon}</span>
                  <span className={`text-xs font-bold px-2 py-1 rounded-full ${stat.change.startsWith('+') ? 'bg-green-50 text-green-600' : 'bg-red-50 text-red-600'}`}>
                    {stat.change}
                  </span>
                </div>
                <h3 className="text-slate-500 text-sm font-medium">{stat.name}</h3>
                <p className="text-2xl font-bold text-slate-900 mt-1">{stat.value}</p>
              </div>
            ))}
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Recent Orders / Product Management */}
            <div className="lg:col-span-2 bg-white rounded-2xl shadow-sm border border-slate-100 overflow-hidden">
              <div className="px-6 py-5 border-b border-slate-100 flex justify-between items-center">
                <h3 className="font-bold text-slate-900">Inventory Status</h3>
                <button className="text-sm text-indigo-600 font-semibold hover:underline">View All</button>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead className="bg-slate-50 text-slate-500 text-xs font-bold uppercase">
                    <tr>
                      <th className="px-6 py-4">Product</th>
                      <th className="px-6 py-4">Category</th>
                      <th className="px-6 py-4">Price</th>
                      <th className="px-6 py-4">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {PRODUCTS.map((product) => (
                      <tr key={product.id} className="hover:bg-slate-50 transition-colors">
                        <td className="px-6 py-4 flex items-center gap-3">
                          <img src={product.image} className="w-8 h-10 rounded-md object-cover" alt="" />
                          <span className="text-sm font-medium text-slate-900">{product.name}</span>
                        </td>
                        <td className="px-6 py-4 text-sm text-slate-500">{product.category}</td>
                        <td className="px-6 py-4 text-sm font-semibold text-slate-900">${product.price}</td>
                        <td className="px-6 py-4">
                          <span className="px-2.5 py-1 bg-green-50 text-green-600 rounded-full text-[10px] font-bold uppercase">In Stock</span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Support Feed Mockup */}
            <div className="bg-white rounded-2xl shadow-sm border border-slate-100 p-6 space-y-6">
              <h3 className="font-bold text-slate-900">Recent Support Chats</h3>
              <div className="space-y-4">
                {[
                  { user: 'Mark R.', query: 'Returns for order #LUM-521', time: '2m ago' },
                  { user: 'Sasha P.', query: 'Sustainability sourcing info', time: '14m ago' },
                  { user: 'Elena V.', query: 'Restock notification for Silk Dress', time: '1h ago' }
                ].map((chat, i) => (
                  <div key={i} className="p-4 bg-slate-50 rounded-xl hover:bg-slate-100 transition-all cursor-pointer border border-transparent hover:border-indigo-100">
                    <div className="flex justify-between items-start mb-1">
                      <span className="text-sm font-bold text-slate-900">{chat.user}</span>
                      <span className="text-[10px] text-slate-400 uppercase">{chat.time}</span>
                    </div>
                    <p className="text-xs text-slate-500 truncate">{chat.query}</p>
                  </div>
                ))}
              </div>
              <button className="w-full py-3 border-2 border-slate-100 text-slate-600 rounded-xl text-sm font-bold hover:bg-slate-50 transition-all">
                View Chat Logs
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Admin;
