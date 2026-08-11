import React, { useEffect, useState } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { 
  Package, Plus, Search, Filter, QrCode, Tag, 
  Layers, CheckCircle2, AlertCircle, PlusCircle, X 
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';

interface Product {
  id: number;
  merchant_id: number;
  sku: string;
  name: string;
  price: number;
  stock: number;
  category: string;
  barcode: str;
}

const Products: React.FC = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isLoading, setIsLoading] = useState(true);

  // New Product Modal State
  const [showAddModal, setShowAddModal] = useState(false);
  const [newProductName, setNewProductName] = useState('');
  const [newPrice, setNewPrice] = useState('');
  const [newStock, setNewStock] = useState('');
  const [newCategory, setNewCategory] = useState('General Grocery');
  const [newBarcode, setNewBarcode] = useState('');

  const merchantId = user?.merchant_id || 1;

  const fetchProducts = async () => {
    try {
      const res = await api.get(`/products/?merchant_id=${merchantId}`);
      setProducts(res.data || []);
    } catch (err) {
      console.error("Failed to fetch products:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, [merchantId]);

  const generateRandomBarcode = () => {
    const code = '890' + Math.floor(100000000 + Math.random() * 900000000);
    setNewBarcode(code);
  };

  const handleAddProduct = async () => {
    if (!newProductName || !newPrice || !newBarcode) {
      toast.error("Please fill in item name, price, and barcode.");
      return;
    }

    try {
      await api.post('/products/', {
        sku: `SKU-${Math.floor(100 + Math.random() * 900)}`,
        name: newProductName,
        price: parseFloat(newPrice),
        stock: parseInt(newStock || '50'),
        category: newCategory,
        barcode: newBarcode
      });

      toast.success(`Product '${newProductName}' created successfully!`);
      setShowAddModal(false);
      setNewProductName('');
      setNewPrice('');
      setNewStock('');
      setNewBarcode('');
      fetchProducts();
    } catch (err) {
      console.error("Error creating product:", err);
      toast.error("Failed to create product.");
    }
  };

  const categories = ['All', ...Array.from(new Set(products.map(p => p.category || 'General')))];

  const filteredProducts = products.filter(p => {
    const matchesSearch = p.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          p.barcode.includes(searchTerm) || 
                          p.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = selectedCategory === 'All' || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  return (
    <div className="min-h-[calc(100vh-4rem)] bg-slate-950 text-white p-4 sm:p-6 lg:p-8 space-y-6">
      <Toaster position="top-right" />

      {/* Add Product Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md animate-fadeIn">
          <div className="w-full max-w-lg glass-card rounded-3xl p-6 border border-white/10 shadow-2xl space-y-5">
            <div className="flex items-center justify-between border-b border-white/10 pb-4">
              <h2 className="text-lg font-black text-white flex items-center gap-2">
                <PlusCircle className="text-[#00f5d4]" size={20} />
                Add New Store Product
              </h2>
              <button 
                onClick={() => setShowAddModal(false)}
                className="p-1 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800"
              >
                <X size={20} />
              </button>
            </div>

            <div className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-300 font-bold mb-1">Product Name</label>
                <input 
                  type="text"
                  value={newProductName}
                  onChange={(e) => setNewProductName(e.target.value)}
                  placeholder="e.g. Organic Almond Milk 1L"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-[#028090]"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-slate-300 font-bold mb-1">Price ($)</label>
                  <input 
                    type="number"
                    step="0.01"
                    value={newPrice}
                    onChange={(e) => setNewPrice(e.target.value)}
                    placeholder="3.99"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-[#028090]"
                  />
                </div>

                <div>
                  <label className="block text-slate-300 font-bold mb-1">Initial Stock Qty</label>
                  <input 
                    type="number"
                    value={newStock}
                    onChange={(e) => setNewStock(e.target.value)}
                    placeholder="100"
                    className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-[#028090]"
                  />
                </div>
              </div>

              <div>
                <label className="block text-slate-300 font-bold mb-1">Category</label>
                <input 
                  type="text"
                  value={newCategory}
                  onChange={(e) => setNewCategory(e.target.value)}
                  placeholder="Beverages, Bakery, Dairy..."
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-semibold focus:outline-none focus:border-[#028090]"
                />
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-slate-300 font-bold">Barcode Number</label>
                  <button 
                    type="button" 
                    onClick={generateRandomBarcode} 
                    className="text-[#00f5d4] hover:underline font-bold text-[11px]"
                  >
                    Generate Random Barcode
                  </button>
                </div>
                <input 
                  type="text"
                  value={newBarcode}
                  onChange={(e) => setNewBarcode(e.target.value)}
                  placeholder="123456789012"
                  className="w-full px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-white text-xs font-mono font-semibold focus:outline-none focus:border-[#028090]"
                />
              </div>
            </div>

            <button
              onClick={handleAddProduct}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-[#028090] to-[#00a896] hover:from-[#026c7a] text-white text-xs font-extrabold shadow-xl flex items-center justify-center gap-2 active:scale-[0.98] transition-all"
            >
              <Plus size={16} />
              Save Product & Generate Barcode
            </button>
          </div>
        </div>
      )}

      {/* Top Header */}
      <div className="glass-card p-6 rounded-3xl border border-white/10 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight flex items-center gap-2.5">
            <Package className="text-[#028090]" size={28} />
            Store Inventory & Barcodes
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Manage product pricing, stock quantities, and barcode mapping for Scan & Go.
          </p>
        </div>

        <button
          onClick={() => { generateRandomBarcode(); setShowAddModal(true); }}
          className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-[#028090] to-[#00a896] hover:from-[#026c7a] text-xs font-extrabold text-white shadow-xl active:scale-95 transition-all"
        >
          <Plus size={16} />
          Add New Product
        </button>
      </div>

      {/* Search & Category Filter */}
      <div className="glass-card p-4 rounded-3xl border border-white/10 flex flex-col md:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by product name, SKU, or barcode..."
            className="w-full pl-10 pr-4 py-2.5 rounded-2xl bg-slate-900 border border-slate-700/80 text-xs font-semibold text-white placeholder-slate-500 focus:outline-none focus:border-[#028090]"
          />
        </div>

        <div className="flex items-center gap-2 overflow-x-auto">
          <Filter size={16} className="text-slate-400 ml-1" />
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-2 rounded-xl text-xs font-bold transition-all whitespace-nowrap ${
                selectedCategory === cat
                  ? 'bg-[#028090] text-white shadow-lg'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Inventory Table */}
      <div className="glass-card rounded-3xl border border-white/10 overflow-hidden shadow-2xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900/90 text-slate-400 font-extrabold uppercase border-b border-white/10">
              <tr>
                <th className="px-6 py-4">Item Name</th>
                <th className="px-6 py-4">Category</th>
                <th className="px-6 py-4">Barcode / SKU</th>
                <th className="px-6 py-4">Price</th>
                <th className="px-6 py-4">Stock Level</th>
                <th className="px-6 py-4 text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5">
              {filteredProducts.map((p) => (
                <tr key={p.id} className="hover:bg-slate-800/40 transition-colors">
                  <td className="px-6 py-4 font-bold text-white flex items-center gap-3">
                    <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center text-sm">
                      📦
                    </div>
                    {p.name}
                  </td>
                  <td className="px-6 py-4 text-slate-300">
                    <span className="px-2.5 py-1 rounded-lg bg-slate-800 border border-slate-700 font-semibold">
                      {p.category || 'General'}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-col">
                      <span className="font-mono text-emerald-400 font-bold flex items-center gap-1">
                        <QrCode size={12} /> {p.barcode}
                      </span>
                      <span className="text-[10px] text-slate-500 font-medium">SKU: {p.sku}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 font-extrabold text-white text-sm">
                    ${Number(p.price).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 font-semibold text-slate-300">
                    {p.stock} units
                  </td>
                  <td className="px-6 py-4 text-right">
                    {p.stock < 15 ? (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-amber-500/10 text-amber-400 font-bold border border-amber-500/20">
                        <AlertCircle size={12} /> Low Stock
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-500/10 text-emerald-400 font-bold border border-emerald-500/20">
                        <CheckCircle2 size={12} /> In Stock
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
};

export default Products;
