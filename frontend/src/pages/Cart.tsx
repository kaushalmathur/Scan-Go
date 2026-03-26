import React from 'react';

const Cart: React.FC = () => {
  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold">Your Cart</h1>
      <div className="mt-4 space-y-4">
        {/* Item list placeholder */}
        <p className="text-center text-gray-400">Your cart is currently empty</p>
      </div>
      <div className="fixed bottom-0 left-0 w-full p-4 bg-white border-t">
        <button className="w-full rounded bg-green-600 p-3 text-white">Checkout Total: $0.00</button>
      </div>
    </div>
  );
};

export default Cart;
