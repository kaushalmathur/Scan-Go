import React from 'react';
import BarcodeScanner from '../components/BarcodeScanner';
import { ShoppingBag, History } from 'lucide-react';
import { Link } from 'react-router-dom';

const Scan: React.FC = () => {
  return (
    <div className="flex flex-col h-screen bg-black">
      {/* Top Header */}
      <div className="p-6 flex items-center justify-between text-white z-10">
        <h1 className="text-xl font-bold tracking-tight">SCAN & GO</h1>
        <div className="flex gap-4">
          <button className="p-2 bg-white/10 rounded-full">
            <History size={20} />
          </button>
        </div>
      </div>

      {/* Scanner Container */}
      <div className="flex-1 relative mx-4 mb-24 overflow-hidden rounded-3xl shadow-2xl">
        <BarcodeScanner />
      </div>

      {/* Bottom Navigation / Action Bar */}
      <div className="fixed bottom-0 left-0 w-full p-6 bg-gradient-to-t from-black to-transparent">
        <Link 
          to="/cart" 
          className="flex items-center justify-between bg-primary-600 p-4 rounded-2xl text-white shadow-lg active:scale-95 transition-transform"
        >
          <div className="flex items-center gap-3">
            <ShoppingBag size={24} />
            <div>
              <p className="text-xs opacity-80 uppercase font-bold">In your cart</p>
              <p className="text-lg font-bold">Tap to view items</p>
            </div>
          </div>
          <div className="bg-white/20 p-2 rounded-xl">
             <span className="font-bold">→</span>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default Scan;
