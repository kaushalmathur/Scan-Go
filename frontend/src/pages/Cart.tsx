import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../api/axios';
import { Trash2, Plus, Minus, CheckCircle, Loader2 } from 'lucide-react';

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
  const [showSuccessOverlay, setShowSuccessOverlay] = useState(false);

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
      // Assuming GET /cart/{user_id} returns { items: [...], total_amount: ... }
      const res = await api.get(`/cart/${user?.user_id}`);
      setItems(res.data.items || []);
    } catch (err) {
      const error = err as { response?: { status?: number } };
      if (error.response?.status !== 404) {
        console.error("Failed to load cart", error);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const updateQuantity = async (item: CartItem, delta: number) => {
    const newQty = item.quantity + delta;
    if (newQty < 1) return;

    // Optimistic update
    const previousItems = [...items];
    setItems((prev) =>
      prev.map((i) => (i.id === item.id ? { ...i, quantity: newQty } : i))
    );

    try {
      await api.put(`/cart/item/${item.id}`, { quantity: newQty });
    } catch (err) {
      console.error("Failed to update quantity", err);
      // Revert optimism
      setItems(previousItems);
    }
  };

  const removeItem = async (itemId: number) => {
    // Optimistic update
    const previousItems = [...items];
    setItems((prev) => prev.filter((i) => i.id !== itemId));

    try {
      await api.delete(`/cart/item/${itemId}`);
    } catch (err) {
      console.error("Failed to remove item", err);
      // Revert optimism
      setItems(previousItems);
    }
  };

  const handleCheckout = async () => {
    if (!user?.user_id || items.length === 0) return;
    setIsCheckingOut(true);

    try {
      await api.post('/cart/checkout', {
        user_id: user.user_id,
        payment_method: "app"
      });

      // Show success overlay immediately
      setShowSuccessOverlay(true);
      
      // Delay navigation to let the animation play
      setTimeout(() => {
        setShowSuccessOverlay(false);
        setItems([]);
        navigate('/scan');
      }, 2000);

    } catch (err) {
      console.error("Checkout failed:", err);
      alert("Checkout failed. Please try again.");
    } finally {
      setIsCheckingOut(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900 text-white">
        <Loader2 className="animate-spin text-[#028090]" size={40} />
      </div>
    );
  }

  // Mathematics
  const subtotal = items.reduce((acc, item) => acc + item.quantity * item.unit_price, 0);
  const gst = subtotal * 0.18;
  const total = subtotal + gst;

  return (
    <div className="flex flex-col min-h-screen bg-slate-900 text-white pb-32">
      {/* Success Overlay */}
      {showSuccessOverlay && (
        <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-slate-900/90 backdrop-blur-sm transition-opacity duration-300">
          <CheckCircle className="text-green-500 mb-4 animate-bounce" size={80} />
          <h2 className="text-2xl font-bold text-white">Payment Successful!</h2>
          <p className="text-slate-300 mt-2">Thank you for shopping with us.</p>
        </div>
      )}

      {/* Header */}
      <header className="sticky top-0 z-10 bg-slate-800 border-b border-slate-700 px-4 py-4 shadow-md">
        <div className="flex items-center justify-between max-w-lg mx-auto">
          <h1 className="text-xl font-bold">Shopping Cart</h1>
          <span className="text-sm font-medium bg-[#028090] text-white px-2 py-1 rounded-full">
            {items.length} {items.length === 1 ? 'item' : 'items'}
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 w-full max-w-lg mx-auto p-4 flex flex-col gap-4">
        {items.length === 0 ? (
          <div className="flex flex-col items-center justify-center flex-1 text-center py-20">
            <div className="bg-slate-800 p-6 rounded-full mb-6">
              <Trash2 size={48} className="text-slate-500" />
            </div>
            <h2 className="text-2xl font-semibold mb-2 text-slate-200">Your cart is empty</h2>
            <p className="text-slate-400 mb-8">Scan items to add them to your cart.</p>
            <Link 
              to="/scan" 
              className="bg-[#028090] hover:bg-[#026c7a] transition-colors py-3 px-8 rounded-full font-bold shadow-lg"
            >
              Start Scanning
            </Link>
          </div>
        ) : (
          <div className="space-y-4 pt-2">
            {items.map((item) => (
              <div 
                key={item.id} 
                className="bg-slate-800 p-4 rounded-xl shadow-sm border border-slate-700 flex flex-col gap-3"
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold text-lg text-slate-100">{item.product_name || `Product #${item.product_id}`}</h3>
                    <p className="text-slate-400 text-sm">${Number(item.unit_price).toFixed(2)} / unit</p>
                  </div>
                  <button 
                    onClick={() => removeItem(item.id)}
                    className="p-2 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded-lg transition-colors"
                  >
                    <Trash2 size={20} />
                  </button>
                </div>

                <div className="flex justify-between items-center mt-1">
                  <div className="flex items-center space-x-3 bg-slate-900 rounded-lg p-1 border border-slate-600">
                    <button 
                      onClick={() => updateQuantity(item, -1)}
                      className="p-1 text-slate-300 hover:text-white hover:bg-slate-700 rounded-md transition-colors"
                      disabled={item.quantity <= 1}
                    >
                      <Minus size={18} />
                    </button>
                    <span className="w-6 text-center font-medium">{item.quantity}</span>
                    <button 
                      onClick={() => updateQuantity(item, 1)}
                      className="p-1 text-slate-300 hover:text-white hover:bg-slate-700 rounded-md transition-colors"
                    >
                      <Plus size={18} />
                    </button>
                  </div>
                  <div className="font-bold text-lg text-[#028090]">
                    ${(item.quantity * item.unit_price).toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Sticky Bottom Bar */}
      {items.length > 0 && (
        <div className="fixed bottom-0 left-0 right-0 bg-slate-800 border-t border-slate-600 shadow-[0_-4px_20px_rgba(0,0,0,0.4)]">
          <div className="max-w-lg mx-auto p-4">
            <div className="space-y-2 mb-4 text-sm text-slate-300">
              <div className="flex justify-between">
                <span>Subtotal</span>
                <span className="font-medium">${subtotal.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span>GST (18%)</span>
                <span className="font-medium">${gst.toFixed(2)}</span>
              </div>
              <div className="flex justify-between pt-2 border-t border-slate-600 text-lg text-white font-bold">
                <span>Total</span>
                <span className="text-[#028090]">${total.toFixed(2)}</span>
              </div>
            </div>
            
            <button
              onClick={handleCheckout}
              disabled={isCheckingOut}
              className="w-full flex items-center justify-center space-x-2 bg-[#028090] hover:bg-[#026c7a] active:scale-[0.98] transition-all text-white font-bold text-lg py-4 rounded-xl shadow-lg disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {isCheckingOut ? (
                <>
                  <Loader2 size={24} className="animate-spin" />
                  <span>Processing...</span>
                </>
              ) : (
                <span>Confirm & Pay ${(total).toFixed(2)}</span>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Cart;
