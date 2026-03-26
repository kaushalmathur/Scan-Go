import React, { useEffect, useState } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import api from '../api/axios';
import {
  TrendingUp,
  Users,
  Activity,
  ShoppingBag,
  AlertTriangle,
  RefreshCw,
} from 'lucide-react';
import toast, { Toaster } from 'react-hot-toast';
import { useAuth } from '../context/AuthContext';

// Define types based on backend responses
interface DashboardSummary {
  total_revenue: number;
  active_shoppers: number;
  scans_per_hour: number;
  avg_basket_value: number;
}

interface SalesDataPoint {
  date: string;
  sales: number;
}

interface Product {
  id: number;
  name: string;
  sku: string;
  stock: number;
  price: number;
  category: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary>({
    total_revenue: 0,
    active_shoppers: 0,
    scans_per_hour: 0,
    avg_basket_value: 0,
  });
  const [salesData, setSalesData] = useState<SalesDataPoint[]>([]);
  const [lowStockProducts, setLowStockProducts] = useState<Product[]>([]);
  const [categoryData, setCategoryData] = useState([
    { name: 'Beverages', revenue: 4500 },
    { name: 'Snacks', revenue: 3200 },
    { name: 'Electronics', revenue: 2800 },
    { name: 'Dairy', revenue: 1900 },
    { name: 'Produce', revenue: 1500 },
  ]); // Mocked data since backend doesn't provide this yet
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Use a hardcoded merchant ID for displaying data if user context isn't fully mocked
  const merchantId = user?.merchant_id || 1;

  const fetchData = async () => {
    setIsRefreshing(true);
    try {
      // Fetch Dashboard Summary
      const summaryRes = await api.get('/dashboard/summary');
      setSummary(summaryRes.data);

      // Fetch Sales Data
      const salesRes = await api.get('/dashboard/sales?period=7d');
      setSalesData(salesRes.data.data);

      // Fetch Products to determine low stock
      // Assuming a generic merchant_id=1 for now, ideally derived from auth context
      const productsRes = await api.get(`/products?merchant_id=${merchantId}`);
      const lowStock = productsRes.data.filter((p: Product) => p.stock < 10);
      setLowStockProducts(lowStock);

    } catch (error) {
      console.error('Failed to fetch dashboard data', error);
      toast.error('Failed to refresh data');
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData(); // Initial fetch

    const intervalId = setInterval(() => {
      fetchData();
    }, 30000); // 30 seconds

    return () => clearInterval(intervalId); // Cleanup
  }, [merchantId]);

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6 md:p-10 font-sans">
      <Toaster position="top-right" />
      
      {/* Header Section */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">Merchant Dashboard</h1>
          <p className="text-gray-400 mt-1">Real-time store performance and analytics.</p>
        </div>
        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm font-medium transition-colors border border-gray-700"
          disabled={isRefreshing}
        >
          <RefreshCw size={16} className={isRefreshing ? 'animate-spin' : ''} />
          {isRefreshing ? 'Refreshing...' : 'Refresh Now'}
        </button>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <TrendingUp size={64} />
          </div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-green-500/20 rounded-lg text-green-400">
              <TrendingUp size={20} />
            </div>
            <h3 className="text-gray-400 font-medium text-sm">Today's Revenue</h3>
          </div>
          <p className="text-3xl font-bold">₹{summary.total_revenue.toLocaleString()}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Users size={64} />
          </div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400">
              <Users size={20} />
            </div>
            <h3 className="text-gray-400 font-medium text-sm">Active Shoppers</h3>
          </div>
          <p className="text-3xl font-bold">{summary.active_shoppers}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <Activity size={64} />
          </div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-purple-500/20 rounded-lg text-purple-400">
              <Activity size={20} />
            </div>
            <h3 className="text-gray-400 font-medium text-sm">Scans / Hour</h3>
          </div>
          <p className="text-3xl font-bold">{summary.scans_per_hour}</p>
        </div>

        <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-10">
            <ShoppingBag size={64} />
          </div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-orange-500/20 rounded-lg text-orange-400">
              <ShoppingBag size={20} />
            </div>
            <h3 className="text-gray-400 font-medium text-sm">Avg Basket Size</h3>
          </div>
          <p className="text-3xl font-bold">₹{summary.avg_basket_value.toLocaleString()}</p>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Charts Column (Takes up 2/3 width on large screens) */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Sales Trends Chart */}
          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
            <h3 className="text-lg font-bold mb-6 text-gray-200">Revenue Trends (Past 7 Days)</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={salesData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                  <XAxis 
                    dataKey="date" 
                    stroke="#9ca3af" 
                    tick={{fill: '#9ca3af', fontSize: 12}}
                    tickMargin={10}
                  />
                  <YAxis 
                    stroke="#9ca3af" 
                    tick={{fill: '#9ca3af', fontSize: 12}}
                    tickFormatter={(value) => `₹${value}`}
                    width={60}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#fff' }}
                    itemStyle={{ color: '#60a5fa' }}
                    formatter={(value: number) => [`₹${value}`, 'Revenue']}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="sales" 
                    stroke="#3b82f6" 
                    strokeWidth={3} 
                    dot={{ r: 4, fill: '#1f2937', stroke: '#3b82f6', strokeWidth: 2 }}
                    activeDot={{ r: 6, fill: '#3b82f6' }}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Top Categories Chart */}
          <div className="bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-lg">
            <h3 className="text-lg font-bold mb-6 text-gray-200">Top Categories by Revenue</h3>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryData} margin={{ top: 5, right: 20, bottom: 5, left: 0 }} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#374151" horizontal={true} vertical={false} />
                  <XAxis 
                    type="number"
                    stroke="#9ca3af" 
                    tick={{fill: '#9ca3af', fontSize: 12}}
                    tickFormatter={(value) => `₹${value}`}
                  />
                  <YAxis 
                    dataKey="name"
                    type="category"
                    stroke="#9ca3af" 
                    width={80}
                    tick={{fill: '#9ca3af', fontSize: 12}}
                  />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#1f2937', border: '1px solid #374151', borderRadius: '0.5rem', color: '#fff' }}
                    cursor={{fill: '#374151', opacity: 0.4}}
                  />
                  <Legend wrapperStyle={{ paddingTop: '20px' }} />
                  <Bar 
                    dataKey="revenue" 
                    fill="#10b981" 
                    radius={[0, 4, 4, 0]} 
                    name="Revenue (₹)"
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Side Panel */}
        <div className="space-y-8">
          
          {/* Inventory Alerts */}
          <div className="bg-gray-800 rounded-2xl border border-gray-700 shadow-lg overflow-hidden flex flex-col h-full max-h-[calc(100vh-12rem)]">
            <div className="p-6 border-b border-gray-700 flex justify-between items-center bg-gray-800 sticky top-0">
              <div className="flex items-center gap-2">
                <AlertTriangle className="text-red-400" size={20} />
                <h3 className="text-lg font-bold text-gray-200">Inventory Alerts</h3>
              </div>
              <span className="bg-red-500/20 text-red-400 text-xs px-2 py-1 rounded-full font-bold">
                {lowStockProducts.length} Items Low
              </span>
            </div>
            
            <div className="p-4 overflow-y-auto flex-1">
              {lowStockProducts.length > 0 ? (
                <ul className="space-y-3">
                  {lowStockProducts.map((product) => (
                    <li key={product.id} className="bg-gray-700/50 p-4 rounded-xl border border-red-500/20 flex flex-col gap-2 transition-all hover:bg-gray-700">
                      <div className="flex justify-between items-start">
                        <span className="font-semibold text-gray-200">{product.name}</span>
                        <span className="text-red-400 font-bold text-sm bg-red-900/30 px-2 py-0.5 rounded">Stock: {product.stock}</span>
                      </div>
                      <div className="flex justify-between items-center text-xs text-gray-400">
                        <span>SKU: {product.sku}</span>
                        <span>{product.category || 'Uncategorized'}</span>
                      </div>
                    </li>
                  ))}
                </ul>
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-center p-6 text-gray-400">
                  <div className="p-4 bg-gray-700/50 rounded-full mb-3">
                    <ShoppingBag size={32} className="opacity-50" />
                  </div>
                  <p className="font-medium text-gray-300">All caught up!</p>
                  <p className="text-sm mt-1">No products currently low on stock.</p>
                </div>
              )}
            </div>
            
            <div className="p-4 border-t border-gray-700 bg-gray-800">
               <button className="w-full py-2.5 bg-gray-700 hover:bg-gray-600 rounded-lg text-sm font-medium transition-colors border border-gray-600">
                 Manage Inventory
               </button>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;
