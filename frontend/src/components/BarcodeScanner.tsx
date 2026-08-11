import React, { useEffect, useRef, useState } from 'react';
import { BrowserMultiFormatReader, NotFoundException } from '@zxing/library';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { toast, Toaster } from 'react-hot-toast';
import { Camera, Sparkles, AlertCircle } from 'lucide-react';

interface BarcodeScannerProps {
  onScanSuccess?: (data: Record<string, unknown>) => void;
}

const BarcodeScanner: React.FC<BarcodeScannerProps> = ({ onScanSuccess }) => {
  const { user } = useAuth();
  const videoRef = useRef<HTMLVideoElement>(null);
  const codeReader = useRef(new BrowserMultiFormatReader());

  const [hasCamera, setHasCamera] = useState<boolean | null>(null);
  const [cameraStatus, setCameraStatus] = useState<string>('Initializing camera...');

  useEffect(() => {
    startScanner();
    return () => {
      stopScanner();
    };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const startScanner = async () => {
    setCameraStatus('Checking camera devices...');
    try {
      const videoInputDevices = await codeReader.current.listVideoInputDevices();
      if (!videoInputDevices || videoInputDevices.length === 0) {
        setHasCamera(false);
        setCameraStatus('No active camera detected. Use sample item chips or manual barcode input.');
        return;
      }

      const selectedDeviceId = videoInputDevices.find(device => 
        device.label.toLowerCase().includes('back')
      )?.deviceId || videoInputDevices[0].deviceId;

      setHasCamera(true);
      setCameraStatus('Camera Active');

      codeReader.current.decodeFromVideoDevice(
        selectedDeviceId,
        videoRef.current!,
        async (result, err) => {
          if (result) {
            await handleBarcodeResult(result.getText());
          }
          if (err && !(err instanceof NotFoundException)) {
            // Ignore frame decode misses
          }
        }
      );
    } catch (err) {
      console.warn("Camera init exception:", err);
      setHasCamera(false);
      setCameraStatus('Camera access restricted. Use sample item chips or manual search.');
    }
  };

  const stopScanner = () => {
    try {
      codeReader.current.reset();
    } catch {
      // Ignore cleanup error
    }
  };

  const handleBarcodeResult = async (barcode: string) => {
    stopScanner();
    try {
      const response = await api.post('/cart/scan', {
        barcode,
        user_id: user?.user_id || 1
      });
      
      const items = response.data?.items || [];
      const lastItem = items[items.length - 1];
      toast.success(`Added ${lastItem?.product_name || 'Item'} - $${lastItem?.unit_price || '4.99'}`, {
        icon: '🛒',
        duration: 3000,
      });

      if (onScanSuccess) onScanSuccess(response.data);
      
      setTimeout(() => {
        startScanner();
      }, 1500);

    } catch (err) {
      console.error(err);
      toast.error("Failed to register scan");
      setTimeout(() => {
        startScanner();
      }, 2000);
    }
  };

  return (
    <div className="relative h-full min-h-[360px] w-full overflow-hidden bg-slate-900/90 rounded-3xl flex flex-col justify-between p-4">
      <Toaster />

      {/* Video element for active camera */}
      <video
        ref={videoRef}
        className={`absolute inset-0 h-full w-full object-cover rounded-3xl ${hasCamera ? 'block' : 'hidden'}`}
        playsInline
        muted
      />

      {/* Standby Viewfinder Fallback Graphics (When camera permissions/devices are pending or unavailable) */}
      {!hasCamera && (
        <div className="absolute inset-0 bg-gradient-to-b from-slate-900 via-slate-950 to-slate-900 flex flex-col items-center justify-center p-6 text-center z-0">
          <div className="w-20 h-20 rounded-3xl bg-[#028090]/20 text-[#00f5d4] border border-[#028090]/40 flex items-center justify-center mb-4 shadow-xl shadow-[#028090]/20 animate-pulse">
            <Camera size={36} />
          </div>
          <h3 className="text-base font-extrabold text-white mb-1">Camera Viewfinder Ready</h3>
          <p className="text-xs text-slate-400 max-w-xs leading-relaxed mb-4">
            {cameraStatus}
          </p>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20 text-xs font-bold">
            <Sparkles size={14} />
            <span>Tip: Click any store item chip above to test scanning!</span>
          </div>
        </div>
      )}

      {/* Overlay Reticle Scanner Grid */}
      <div className="absolute inset-0 pointer-events-none z-10">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-56 h-56 sm:w-64 sm:h-64 border-2 border-white/20 rounded-3xl">
          {/* Glowing Corner Accents */}
          <div className="absolute -top-1 -left-1 w-8 h-8 border-t-4 border-l-4 border-[#00f5d4] rounded-tl-xl"></div>
          <div className="absolute -top-1 -right-1 w-8 h-8 border-t-4 border-r-4 border-[#00f5d4] rounded-tr-xl"></div>
          <div className="absolute -bottom-1 -left-1 w-8 h-8 border-b-4 border-l-4 border-[#00f5d4] rounded-bl-xl"></div>
          <div className="absolute -bottom-1 -right-1 w-8 h-8 border-b-4 border-r-4 border-[#00f5d4] rounded-br-xl"></div>
          
          {/* Laser Animated Line */}
          <div className="absolute top-0 left-0 w-full h-1 bg-[#00f5d4] shadow-[0_0_20px_#00f5d4] animate-scan"></div>
        </div>
      </div>

      {/* HUD Top Bar Status */}
      <div className="relative z-20 flex justify-center">
        <div className="bg-slate-950/80 backdrop-blur-md px-4 py-1.5 rounded-full flex items-center gap-2 border border-white/10 text-xs text-slate-300 font-semibold shadow-lg">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span>Position barcode inside reticle</span>
        </div>
      </div>

      {/* HUD Bottom Retry Button */}
      {!hasCamera && (
        <div className="relative z-20 flex justify-center pt-4">
          <button
            onClick={startScanner}
            className="px-4 py-2 rounded-xl bg-slate-800/80 hover:bg-slate-700 text-xs font-bold text-slate-200 border border-slate-700 shadow-lg active:scale-95 transition-all flex items-center gap-2"
          >
            <AlertCircle size={14} className="text-[#028090]" />
            Retry Camera Access
          </button>
        </div>
      )}

      <style dangerouslySetInnerHTML={{ __html: `
        @keyframes scan {
          0% { top: 0%; opacity: 0.2; }
          50% { opacity: 1; }
          100% { top: 100%; opacity: 0.2; }
        }
        .animate-scan {
          animation: scan 2s ease-in-out infinite;
        }
      `}} />
    </div>
  );
};

export default BarcodeScanner;
