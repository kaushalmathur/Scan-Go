import React, { useEffect, useRef, useState } from 'react';
import { BrowserMultiFormatReader, NotFoundException } from '@zxing/library';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { toast, Toaster } from 'react-hot-toast';
import { Camera, XCircle, Loader2 } from 'lucide-react';

interface BarcodeScannerProps {
  onScanSuccess?: (data: any) => void;
}

const BarcodeScanner: React.FC<BarcodeScannerProps> = ({ onScanSuccess }) => {
  const { user } = useAuth();
  const videoRef = useRef<HTMLVideoElement>(null);
  const codeReader = useRef(new BrowserMultiFormatReader());
  const [isScanning, setIsScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    startScanner();
    return () => {
      stopScanner();
    };
  }, []);

  const startScanner = async () => {
    setIsScanning(true);
    setError(null);
    try {
      const videoInputDevices = await codeReader.current.listVideoInputDevices();
      if (videoInputDevices.length === 0) {
        throw new Error('No camera found');
      }

      // Try to use back camera first on mobile
      const selectedDeviceId = videoInputDevices.find(device => 
        device.label.toLowerCase().includes('back')
      )?.deviceId || videoInputDevices[0].deviceId;

      codeReader.current.decodeFromVideoDevice(
        selectedDeviceId,
        videoRef.current!,
        async (result, err) => {
          if (result) {
            await handleBarcodeResult(result.getText());
          }
          if (err && !(err instanceof NotFoundException)) {
            // Ignore minor errors like "no barcode found in frame"
            console.error(err);
          }
        }
      );
    } catch (err: any) {
      setError(err.message === 'No camera found' ? 'Camera access is required' : 'Camera error');
      setIsScanning(false);
      toast.error('Failed to start camera');
    }
  };

  const stopScanner = () => {
    codeReader.current.reset();
  };

  const handleBarcodeResult = async (barcode: str) => {
    // Prevent double scanning within short time
    codeReader.current.reset(); // Pause scanner
    
    try {
      const response = await api.post('/cart/scan', {
        barcode,
        user_id: user?.user_id
      });
      
      const lastItem = response.data.items.find((item: any) => item.product_name); // Simplified for now
      toast.success(`Added ${lastItem?.product_name || 'Item'} - $${lastItem?.unit_price || '0.00'}`, {
        icon: '🛒',
        duration: 3000,
        position: 'top-center',
      });

      if (onScanSuccess) onScanSuccess(response.data);
      
      // Resume scanning after 1.5 seconds delay
      setTimeout(() => {
        startScanner();
      }, 1500);

    } catch (err: any) {
      const detail = err.response?.data?.detail || "Network Error";
      toast.error(detail);
      console.error(err);
      
      // Resume scanner regardless of error
      setTimeout(() => {
        startScanner();
      }, 2000);
    }
  };

  return (
    <div className="relative h-full w-full overflow-hidden bg-black rounded-3xl">
      <Toaster />
      
      {/* Viewfinder */}
      <video
        ref={videoRef}
        className="h-full w-full object-cover"
        playsInline
        muted
      />

      {/* Modern Overlay Reticle */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Darkened edges */}
        <div className="absolute inset-0 bg-black/40 shadow-[inset_0_0_100px_rgba(0,0,0,0.5)]"></div>
        
        {/* Scanning Window */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 border-2 border-white/30 rounded-2xl">
          {/* Corner highlights */}
          <div className="absolute -top-1 -left-1 w-8 h-8 border-t-4 border-l-4 border-primary-500 rounded-tl-lg"></div>
          <div className="absolute -top-1 -right-1 w-8 h-8 border-t-4 border-r-4 border-primary-500 rounded-tr-lg"></div>
          <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-4 border-l-4 border-primary-500 rounded-bl-lg"></div>
          <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-4 border-r-4 border-primary-500 rounded-br-lg"></div>
          
          {/* Scanning Line Animation */}
          <div className="absolute top-0 left-0 w-full h-1 bg-primary-500/80 shadow-[0_0_15px_#0ea5e9] animate-scan"></div>
        </div>
      </div>

      {/* UI Controls */}
      <div className="absolute top-6 left-1/2 -translate-x-1/2 text-center text-white">
        <div className="bg-white/10 backdrop-blur-md px-4 py-2 rounded-full flex items-center gap-2 border border-white/20">
          <Camera size={18} className="text-primary-400" />
          <span className="text-sm font-medium">Position code inside frame</span>
        </div>
      </div>

      {/* Error State Overlay */}
      {error && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/80 text-white p-6 text-center">
          <XCircle size={48} className="text-red-500 mb-4" />
          <h3 className="text-xl font-bold mb-2">{error}</h3>
          <button 
            onClick={startScanner}
            className="mt-4 px-6 py-2 bg-primary-600 rounded-full hover:bg-primary-700 transition"
          >
            Retry Camera Access
          </button>
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { top: 0%; opacity: 0.1; }
          50% { opacity: 1; }
          100% { top: 100%; opacity: 0.1; }
        }
        .animate-scan {
          animation: scan 2s linear infinite;
        }
      `}} />
    </div>
  );
};

export default BarcodeScanner;
