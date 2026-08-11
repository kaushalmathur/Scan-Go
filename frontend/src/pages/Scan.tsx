import React, { useState, useEffect } from 'react';
import BarcodeScanner from '../components/BarcodeScanner';
import { ShoppingBag, Search, Sparkles, CheckCircle2, QrCode, Tag } from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { toast, Toaster } from 'react-hot-toast';

const Scan: React.FC = () => {
  const { user } = useAuth();
  const [manualBarcode, setManualBarcode] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [cartItemsCount, setCartItemsCount] = useState(0);
  const [cartTotal, setCartTotal] = useState(0);
  const [lastScannedItem, setLastScannedItem] = useState<{ name: string; price: string } | null>(null);

  const sampleProducts = [
    { label: "⚡ Energy Drink", code: "123456789012", price: "$3.99" },
    { label: "🥛 Whole Milk 1L", code: "8901030953613", price: "$2.49" },
    { label: "🥔 Potato Chips", code: "079238237012", price: "$1.99" },
    { label: "🍫 Dark Chocolate", code: "5000159461122", price: "$4.50" },
    { label: "💧 Mineral Water", code: "3057640100473", price: "$1.29" },
    { label: "☕ Espresso Coffee", code: "8000070010567", price: "$8.99" },
  ];

  const fetchCartSummary = async () => {
    if (!user?.user_id) return;
    try {
      const res = await api.get(`/cart/${user.user_id}`);
      const items = res.data?.items || [];
      const count = items.reduce((acc: number, item: { quantity: number }) => acc + (item.quantity || 1), 0);
      const total = items.reduce((acc: number, item: { quantity: number; unit_price: number }) => acc + (item.quantity * item.unit_price), 0);
      setCartItemsCount(count);
      setCartTotal(total);
    } catch {
      // Ignore missing cart
    }
  };

  useEffect(() => {
    fetchCartSummary();
  }, [user]);

  const handleManualSubmit = async (codeToSubmit?: string) => {
    const code = codeToSubmit || manualBarcode.trim();
    if (!code) {
      toast.error("Please enter a barcode number.");
      return;
    }

    setIsScanning(true);
    try {
      const response = await api.post('/cart/scan', {
        barcode: code,
        user_id: user?.user_id || 1,
      });

      const items = response.data.items;
      const lastItem = items[items.length - 1];

      const itemInfo = {
        name: lastItem?.product_name || "Scanned Item",
        price: lastItem?.unit_price ? `$${Number(lastItem.unit_price).toFixed(2)}` : "$4.99",
      };

      setLastScannedItem(itemInfo);
      fetchCartSummary();

      toast.success(`Added ${itemInfo.name} (${itemInfo.price}) to cart!`, {
        icon: '🛒',
        duration: 3000,
      });

      setManualBarcode('');
    } catch (err: any) {
      console.error(err);
      toast.error("Failed to scan item. Please try again.");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="flex flex-col min-h-[calc(100vh-4rem)] bg-slate-950 text-white pb-32">
      <Toaster position="top-center" />

      {/* Top Banner */}
      <div className="p-4 sm:p-6 bg-slate-900/80 border-b border-white/10 backdrop-blur-md">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h1 className="text-xl font-extrabold tracking-tight text-white flex items-center gap-2">
              <QrCode className="text-[#028090]" size={24} />
              Scan & Go Terminal
            </h1>
            <p className="text-xs text-slate-400">Position barcode inside camera reticle or pick from store chips</p>
          </div>

          <div className="flex items-center gap-3 bg-slate-800/80 px-4 py-2 rounded-2xl border border-slate-700">
            <ShoppingBag size={18} className="text-[#028090]" />
            <div className="flex flex-col">
              <span className="text-[10px] uppercase font-bold text-slate-400">Cart Total</span>
              <span className="text-sm font-extrabold text-[#00f5d4]">${cartTotal.toFixed(2)} ({cartItemsCount} items)</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto w-full px-4 pt-4 flex-1 flex flex-col gap-4">

        {/* Manual Barcode Search */}
        <div className="glass-card p-4 rounded-3xl space-y-3">
          <form 
            onSubmit={(e) => { e.preventDefault(); handleManualSubmit(); }}
            className="flex gap-2"
          >
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                type="text"
                value={manualBarcode}
                onChange={(e) => setManualBarcode(e.target.value)}
                placeholder="Type or paste barcode number..."
                className="w-full pl-10 pr-4 py-3 rounded-2xl bg-slate-900/90 border border-slate-700/80 text-xs font-semibold text-white placeholder-slate-500 focus:outline-none focus:border-[#028090]"
              />
            </div>
            <button
              type="submit"
              disabled={isScanning}
              className="px-5 py-3 rounded-2xl bg-gradient-to-r from-[#028090] to-[#00a896] hover:from-[#026c7a] text-xs font-extrabold text-white shadow-lg active:scale-95 transition-all"
            >
              {isScanning ? "Scanning..." : "Scan Code"}
            </button>
          </form>

          {/* Quick Store Barcode Chips */}
          <div>
            <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-2 font-semibold">
              <Sparkles size={14} className="text-amber-400" />
              <span>Tap any store item to test instant scan:</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {sampleProducts.map((p) => (
                <button
                  key={p.code}
                  type="button"
                  onClick={() => handleManualSubmit(p.code)}
                  className="px-3.5 py-2 rounded-xl bg-slate-900/80 border border-slate-700/80 hover:border-[#028090] text-xs font-bold text-slate-200 flex items-center gap-2 active:scale-95 transition-all group"
                >
                  <span>{p.label}</span>
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-emerald-400 font-extrabold border border-slate-700">
                    {p.price}
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Last Scanned Feedback Banner */}
        {lastScannedItem && (
          <div className="p-4 bg-emerald-500/15 border border-emerald-500/30 rounded-3xl flex items-center justify-between text-emerald-400 animate-fadeIn">
            <div className="flex items-center gap-3">
              <CheckCircle2 size={24} className="text-emerald-400" />
              <div>
                <p className="text-[10px] font-extrabold uppercase text-emerald-400 tracking-wider">Item Added to Cart</p>
                <p className="text-sm font-bold text-white">{lastScannedItem.name}</p>
              </div>
            </div>
            <span className="text-sm font-black px-3.5 py-1.5 bg-emerald-500/25 rounded-xl text-white">
              {lastScannedItem.price}
            </span>
          </div>
        )}

        {/* Camera Reticle Viewfinder Container */}
        <div className="flex-1 min-h-[360px] relative overflow-hidden rounded-3xl border border-white/10 shadow-2xl glass-card">
          <BarcodeScanner onScanSuccess={(data) => {
            fetchCartSummary();
            if (data && data.items && Array.isArray(data.items)) {
              const last = data.items[data.items.length - 1];
              if (last) {
                setLastScannedItem({
                  name: last.product_name || "Scanned Item",
                  price: last.unit_price ? `$${Number(last.unit_price).toFixed(2)}` : "$4.99"
                });
              }
            }
          }} />
        </div>

      </div>

      {/* Floating Bottom Cart Navigation */}
      <div className="fixed bottom-0 left-0 w-full p-4 bg-slate-950/90 backdrop-blur-xl border-t border-white/10 z-30">
        <div className="max-w-4xl mx-auto">
          <Link 
            to="/cart" 
            className="flex items-center justify-between bg-gradient-to-r from-[#028090] to-[#00a896] p-4 rounded-2xl text-white shadow-xl hover:from-[#026c7a] active:scale-[0.98] transition-all"
          >
            <div className="flex items-center gap-3.5">
              <div className="w-10 h-10 rounded-xl bg-white/20 flex items-center justify-center">
                <ShoppingBag size={22} />
              </div>
              <div>
                <p className="text-[11px] opacity-80 uppercase font-extrabold tracking-wider">Active Shopping Cart</p>
                <p className="text-sm sm:text-base font-bold">
                  {cartItemsCount > 0 ? `${cartItemsCount} Items in Cart • $${cartTotal.toFixed(2)}` : "Cart Empty • Tap to View"}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2 bg-white/20 px-3 py-1.5 rounded-xl font-extrabold text-xs">
              Checkout →
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Scan;
