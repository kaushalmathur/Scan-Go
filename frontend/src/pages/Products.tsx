import React from 'react';

const Products: React.FC = () => {
  return (
    <div className="p-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Inventory Control</h1>
        <button className="rounded bg-primary-600 px-4 py-2 text-white">+ Add Item</button>
      </div>
      <table className="mt-6 w-full text-left">
        <thead className="border-b bg-gray-50">
          <tr>
            <th className="px-4 py-2">Item</th>
            <th className="px-4 py-2">SKU</th>
            <th className="px-4 py-2">Price</th>
            <th className="px-4 py-2">Stock</th>
          </tr>
        </thead>
        <tbody>
          <tr className="border-b hover:bg-gray-50">
            <td className="px-4 py-3">Premium Coffee Beans</td>
            <td className="px-4 py-3">COF-001</td>
            <td className="px-4 py-3">$14.99</td>
            <td className="px-4 py-3">125</td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

export default Products;
