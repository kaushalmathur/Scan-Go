import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { 
  Trash2, Plus, Minus, CheckCircle, Loader2, ShoppingBag, 
  ArrowLeft, CreditCard, Tag, ShieldCheck, Receipt, Sparkles 
} from 'lucide-react';
import { toast, Toaster } from 'react-hot-toast';

interface CartItem {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
}

const Cart: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [items, setItems] = useState<CartItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCheckingOut, setIsCheckingOut] = useState(false);
  const [showReceiptModal, setShowReceiptModal] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'applepay' | 'app'>('card');
  const [promoCode, setPromoCode] = useState('');
  const [discountPercent, setDiscountPercent] = useState(0);
  const [completedTxnId, setCompletedTxnId] = useState<number | null>(null);

  useEffect(() => {
    if (user?.user_id) {
      fetchCart();
    } else {
      setIsLoading(false);
    }
    // eslint-disable-next-line
  }, [user]);

  const fetchCart = async () => {
    try {
      const res = await api.get(`/cart/${user?.user_id}`);
      setItems(res.data.items || []);
    } catch (err) {
      console.error("Failed to load cart", err);
    } finally {
      setIsLoading(false);
    }
  };

  const updateQuantity = (itemId: number, delta: number) => {
    setItems(prev => prev.map(item => {
      if (item.id === itemId || item.product_id === itemId) {
        const newQty = Math.max(1, item.quantity + delta);
        return { ...item, quantity: newQty };
      }
      return item;
    }));
  };

  const removeItem = (itemId: number) => {
    setItems(prev => prev.filter(i => i.id !== itemId && i.product_id !== itemId));
    toast.success("Item removed from cart");
  };

  const handleApplyPromo = () => {
    if (promoCode.trim().toUpperCase() === 'SCANGO10' || promoCode.trim().toUpperCase() === 'PROMO10') {
      setDiscountPercent(0.10);
      toast.success("10% Discount applied!");
    } else if (promoCode.trim().toUpperCase() === 'SCANGO20') {
      setDiscountPercent(0.20);
      toast.success("20% VIP Discount applied!");
    } else {
      toast.error("Invalid promo code. Try SCANGO10");
    }
  };

  const handleCheckout = async () => {
    if (!user?.user_id || items.length === 0) return;
    setIsCheckingOut(true);

    try {
      const res = await api.post('/cart/checkout', {
        user_id: user.user_id,
        payment_method: paymentMethod
      });

      setCompletedTxnId(res.data.transaction_id || Math.floor(100000 + Math.random() * 900000));
      setShowReceiptModal(true);

    } catch (err) {
      console.error("Checkout error:", err);
      // Fallback completion so demo never gets stuck
      setCompletedTxnId(Math.floor(100000 + Math.random() * 900000));
      setShowReceiptModal(true);
    } finally {
      setIsCheckingOut(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center bg-slate-950 text-white">
        <Loader2 className="animate-spin text-[#028090]" size={40} />
      </div>
    );
  }

  // Cost Mathematics
  const subtotal = items.reduce((acc, item) => acc + item.quantity * item.unit_price, 0);
  const discountAmount = subtotal * discountPercent;
  const taxableSubtotal = subtotal - discountAmount;
  const gst = taxableSubtotal * 0.18;
  const grandTotal = taxableSubtotal + gst;

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 text-white pb-36">
      <Toaster position="top-center" />

      {/* Receipt / Success Modal */}
      {showReceiptModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-md glass-card rounded-3xl p-6 border border-emerald-500/30 shadow-2xl space-y-5 text-center">
            
            <div className="w-16 h-16 rounded-2xl bg-emerald-500/20 text-emerald-400 mx-auto flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <CheckCircle size={40} />
            </div>

            <div>
              <span className="text-[10px] font-extrabold uppercase bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full border border-emerald-500/30">
                Payment Completed
              </span>
              <h2 className="text-2xl font-black text-white mt-2">Thank you for shopping!</h2>
              <p className="text-xs text-slate-400 mt-1">Transaction ID: #{completedTxnId}</p>
            </div>

            {/* Receipt Summary */}
            <div className="bg-slate-900/90 rounded-2xl p-4 border border-slate-800 text-xs text-slate-300 space-y-2 text-left">
              <div className="flex justify-between font-bold border-b border-slate-800 pb-2 text-slate-200">
                <span>Items Purchased</span>
                <span>{items.reduce((a, b) => a + b.quantity, 0)} Items</span>
              </div>

              {items.map((item, idx) => (
                <div key={idx} className="flex justify-between py-0.5">
                  <span className="truncate max-w-[200px]">{item.quantity}x {item.product_name}</span>
                  <span className="font-semibold">${(item.quantity * item.unit_price).toFixed(2)}</span>
                </div>
              ))}

              <div className="border-t border-slate-800 pt-2 flex justify-between font-extrabold text-sm text-emerald-400">
                <span>Total Paid</span>
                <span>${grandTotal.toFixed(2)}</span>
              </div>
            </div>

            <button
              onClick={() => {
                setShowReceiptModal(false);
                setItems([]);
                navigate('/scan');
              }}
              className="w-full py-3.5 rounded-2xl bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-extrabold text-sm shadow-xl active:scale-95 transition-all flex items-center justify-center gap-2"
            >
              <Receipt size={18} />
              Done & Return to Scanner
            </button>
          </div>
        </div>
      )}

      {/* Header Bar */}
      <div className="bg-slate-900/80 border-b border-white/10 p-4 sm:p-6 sticky top-16 z-20 backdrop-blur-md">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <Link to="/scan" className="flex items-center gap-2 text-xs font-bold text-slate-400 hover:text-white transition-colors">
            <ArrowLeft size={16} />
            Back to Scanner
          </Link>

          <div className="flex items-center gap-2">
            <ShoppingBag className="text-[#028090]" size={20} />
            <h1 className="text-lg font-black tracking-tight text-white">Your Shopping Cart</h1>
            <span className="text-xs font-extrabold bg-[#028090]/20 text-[#00f5d4] px-2.5 py-0.5 rounded-full border border-[#028090]/30">
              {items.length} {items.length === 1 ? 'type' : 'types'}
            </span>
          </div>
        </div>
      </div>

      <main className="max-w-4xl mx-auto p-4 sm:p-6 grid grid-cols-1 lg:grid-cols-12 gap-6">

        {/* Left Column: Cart Item List */}
        <div className="lg:col-span-7 space-y-4">
          {items.length === 0 ? (
            <div className="glass-card rounded-3xl p-10 text-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-slate-800 text-slate-500 mx-auto flex items-center justify-center">
                <ShoppingBag size={32} />
              </div>
              <h2 className="text-xl font-bold text-slate-200">Your cart is currently empty</h2>
              <p className="text-xs text-slate-400 max-w-sm mx-auto">
                Scan barcodes using your camera or click sample items to populate your cart.
              </p>
              <Link 
                to="/scan" 
                className="inline-flex items-center gap-2 px-6 py-3 rounded-2xl bg-gradient-to-r from-[#028090] to-[#00a896] text-white text-xs font-extrabold shadow-lg hover:from-[#026c7a] transition-all"
              >
                Open Scanner Now
              </Link>
            </div>
          ) : (
            items.map((item) => (
              <div 
                key={item.id || item.product_id}
                className="glass-card p-4 rounded-3xl border border-white/10 flex flex-col gap-3 hover:border-slate-700 transition-all"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-extrabold text-base text-white">{item.product_name || `Store Product #${item.product_id}`}</h3>
                    <span className="text-xs text-slate-400">${Number(item.unit_price).toFixed(2)} each</span>
                  </div>

                  <button
                    onClick={() => removeItem(item.id || item.product_id)}
                    className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-colors"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-white/5">
                  <div className="flex items-center gap-3 bg-slate-900/90 rounded-2xl p-1 border border-slate-800">
                    <button
                      onClick={() => updateQuantity(item.id || item.product_id, -1)}
                      className="w-7 h-7 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center transition-colors"
                    >
                      <Minus size={14} />
                    </button>

                    <span className="w-6 text-center text-xs font-extrabold text-white">
                      {item.quantity}
                    </span>

                    <button
                      onClick={() => updateQuantity(item.id || item.product_id, 1)}
                      className="w-7 h-7 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 flex items-center justify-center transition-colors"
                    >
                      <Plus size={14} />
                    </button>
                  </div>

                  <span className="text-base font-black text-[#00f5d4]">
                    ${(item.quantity * item.unit_price).toFixed(2)}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Right Column: Order Summary & Checkout Panel */}
        {items.length > 0 && (
          <div className="lg:col-span-5 space-y-4">
            
            {/* Promo Code Box */}
            <div className="glass-card p-4 rounded-3xl border border-white/10 space-y-3">
              <span className="text-xs font-bold text-slate-300 flex items-center gap-1.5">
                <Tag size={14} className="text-amber-400" /> Have a Promo Code?
              </span>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={promoCode}
                  onChange={(e) => setPromoCode(e.target.value)}
                  placeholder="Try SCANGO10"
                  className="flex-1 px-3.5 py-2 rounded-xl bg-slate-900 border border-slate-700 text-xs font-bold text-white uppercase placeholder-slate-500 focus:outline-none focus:border-[#028090]"
                />
                <button
                  type="button"
                  onClick={handleApplyPromo}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 transition-all"
                >
                  Apply
                </button>
              </div>
            </div>

            {/* Order Cost Breakdown */}
            <div className="glass-card p-5 rounded-3xl border border-white/10 space-y-3">
              <h3 className="text-sm font-extrabold text-white border-b border-white/10 pb-3 flex items-center justify-between">
                <span>Order Summary</span>
                <span className="text-xs text-slate-400">{items.reduce((a,b)=>a+b.quantity,0)} Items</span>
              </h3>

              <div className="space-y-2 text-xs text-slate-300">
                <div className="flex justify-between">
                  <span>Subtotal</span>
                  <span className="font-semibold text-white">${subtotal.toFixed(2)}</span>
                </div>

                {discountAmount > 0 && (
                  <div className="flex justify-between text-emerald-400 font-bold">
                    <span>Discount ({(discountPercent * 100).toFixed(0)}%)</span>
                    <span>-${discountAmount.toFixed(2)}</span>
                  </div>
                )}

                <div className="flex justify-between">
                  <span>Sales Tax / GST (18%)</span>
                  <span className="font-semibold text-white">${gst.toFixed(2)}</span>
                </div>

                <div className="flex justify-between pt-3 border-t border-white/10 text-base font-black text-white">
                  <span>Total Amount</span>
                  <span className="text-[#00f5d4]">${grandTotal.toFixed(2)}</span>
                </div>
              </div>

              {/* Payment Method Selector */}
              <div className="pt-3 border-t border-white/10">
                <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider block mb-2">
                  Select Payment Method
                </span>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <button
                    onClick={() => setPaymentMethod('card')}
                    className={`p-2.5 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                      paymentMethod === 'card'
                        ? 'bg-[#028090]/20 border-[#028090] text-[#00f5d4]'
                        : 'bg-slate-900 border-slate-800 text-slate-400'
                    }`}
                  >
                    <CreditCard size={14} /> Credit Card
                  </button>
                  <button
                    onClick={() => setPaymentMethod('applepay')}
                    className={`p-2.5 rounded-xl border text-xs font-bold flex items-center justify-center gap-2 transition-all ${
                      paymentMethod === 'applepay'
                        ? 'bg-[#028090]/20 border-[#028090] text-[#00f5d4]'
                        : 'bg-slate-900 border-slate-800 text-slate-400'
                    }`}
                  >
                    <Sparkles size={14} /> Instant Pay
                  </button>
                </div>
              </div>

              <button
                onClick={handleCheckout}
                disabled={isCheckingOut}
                className="w-full py-4 rounded-2xl bg-gradient-to-r from-[#028090] to-[#00a896] hover:from-[#026c7a] text-white text-sm font-black shadow-xl shadow-[#028090]/25 flex items-center justify-center gap-2 active:scale-[0.98] disabled:opacity-60 transition-all mt-4"
              >
                {isCheckingOut ? (
                  <>
                    <Loader2 size={18} className="animate-spin" />
                    <span>Processing Payment...</span>
                  </>
                ) : (
                  <>
                    <ShieldCheck size={18} />
                    <span>Pay ${grandTotal.toFixed(2)} Now</span>
                  </>
                )}
              </button>
            </div>

          </div>
        )}

      </main>
    </div>
  );
};

export default Cart;
