"use client";

import Image from "next/image";
import { useState, useEffect, useRef, useCallback } from "react";
import Choose from "./components/choose";
import SnapPayment from "./components/qris-payment";
import CashVoucherPayment from "./components/cash-voucher-payment";
import "./styles/main.css";

export default function Home() {
  const [currentStep, setCurrentStep] = useState("welcome");
  const [showOfflineToast, setShowOfflineToast] = useState(false);
  const [isToastExiting, setIsToastExiting] = useState(false);
  const [isToastEntering, setIsToastEntering] = useState(false);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const enterTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Add transaction state management to prevent duplicates
  const [currentTransactionId, setCurrentTransactionId] = useState<string | null>(null);
  const [transactionStartTime, setTransactionStartTime] = useState<number | null>(null);
  const sessionTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const isOnline = () => {
    return typeof navigator !== 'undefined' && navigator.onLine;
  };

  const clearAllTimeouts = () => {
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
    if (enterTimeoutRef.current) {
      clearTimeout(enterTimeoutRef.current);
      enterTimeoutRef.current = null;
    }
  };

  // Clear transaction session timeout
  const clearSessionTimeout = () => {
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current);
      sessionTimeoutRef.current = null;
    }
  };

  // Reset transaction state
  const resetTransactionState = () => {
    setCurrentTransactionId(null);
    setTransactionStartTime(null);
    clearSessionTimeout();
  };

  // Start transaction session with timeout
  const startTransactionSession = () => {
    const now = Date.now();
    setTransactionStartTime(now);
    
    // Set timeout to reset transaction after 10 minutes (600000ms)
    // This prevents old transactions from blocking new ones
    clearSessionTimeout();
    sessionTimeoutRef.current = setTimeout(() => {
      console.log('Transaction session timed out, resetting state...');
      resetTransactionState();
    }, 600000); // 10 minutes
  };

  // Check if current transaction is still valid (within 10 minutes)
  const isCurrentTransactionValid = () => {
    if (!transactionStartTime) return false;
    const now = Date.now();
    const elapsed = now - transactionStartTime;
    return elapsed < 600000; // 10 minutes
  };

  const showToast = () => {
    // Clear any existing timeouts
    clearAllTimeouts();
    
    // If toast is already showing, just reset the timer
    if (showOfflineToast && !isToastExiting) {
      // Reset hide timer
      hideTimeoutRef.current = setTimeout(() => {
        setIsToastExiting(true);
        hideTimeoutRef.current = setTimeout(() => {
          setShowOfflineToast(false);
          setIsToastExiting(false);
        }, 300);
      }, 4000);
      return;
    }
    
    // Show new toast
    setShowOfflineToast(true);
    setIsToastExiting(false);
    setIsToastEntering(true);
    
    // Start enter animation
    enterTimeoutRef.current = setTimeout(() => {
      setIsToastEntering(false);
    }, 50);
    
    // Hide toast after 4 seconds
    hideTimeoutRef.current = setTimeout(() => {
      setIsToastExiting(true);
      hideTimeoutRef.current = setTimeout(() => {
        setShowOfflineToast(false);
        setIsToastExiting(false);
      }, 300);
    }, 4000);
  };

  const hideToast = () => {
    clearAllTimeouts();
    setIsToastEntering(false);
    setIsToastExiting(true);
    hideTimeoutRef.current = setTimeout(() => {
      setShowOfflineToast(false);
      setIsToastExiting(false);
    }, 300);
  };

  const handleStartSession = () => {
    // Reset any existing transaction when starting new session
    resetTransactionState();
    setCurrentStep("choose");
  };

  const handleBack = () => {
    // Reset transaction when going back to welcome
    resetTransactionState();
    setCurrentStep("welcome");
  };

  const handleSnapPayment = () => {
    // Check if online before navigating to payment
    if (!isOnline()) {
      showToast();
      return;
    }
    
    // Always start new transaction - no blocking for previous cancelled/failed transactions
    console.log('Starting new transaction session...');
    resetTransactionState();
    startTransactionSession();
    setCurrentStep("snap-payment");
  };

  const handleCashPayment = () => {
    // Check if online before navigating to payment
    if (!isOnline()) {
      showToast();
      return;
    }
    
    // Navigate to cash/voucher payment
    console.log('Starting cash/voucher payment...');
    setCurrentStep("cash-voucher-payment");
  };

  const handleBackToChoose = () => {
    // Don't reset transaction when going back to choose
    // This allows user to return to same transaction
    setCurrentStep("choose");
  };

  const handlePaymentSuccess = () => {
    // Reset transaction state on successful payment
    resetTransactionState();
    setCurrentStep("welcome");
  };

  // Handle transaction creation callback - USE CALLBACK TO PREVENT RE-RENDERS
  const handleTransactionCreated = useCallback((transactionId: string) => {
    setCurrentTransactionId(transactionId);
    console.log('Transaction created and tracked:', transactionId);
  }, []);

  // Monitor online status
  useEffect(() => {
    const handleOnline = () => {
      if (showOfflineToast) {
        hideToast();
      }
    };

    const handleOffline = () => {
      showToast();
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('online', handleOnline);
      window.addEventListener('offline', handleOffline);

      return () => {
        window.removeEventListener('online', handleOnline);
        window.removeEventListener('offline', handleOffline);
      };
    }
  }, [showOfflineToast]);

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current);
      }
      if (enterTimeoutRef.current) {
        clearTimeout(enterTimeoutRef.current);
      }
      // Add cleanup for session timeout
      if (sessionTimeoutRef.current) {
        clearTimeout(sessionTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div id="main-container" className="flex flex-col items-center justify-center h-[100dvh] w-full">
      <div className="middle-panel h-[85dvh] max-h-[800px] w-full max-w-[1200px] bg-[#99C6F4] rounded-3xl p-[25px] flex flex-col border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F] justify-center items-center">
        <div id="content-area">
          {currentStep === "welcome" && (
            <div id="content-1" className="flex flex-col items-center justify-center gap-[20px]">
              <span className="main-font text-[55px] text-[#2E4E3F] font-semibold leading-tight">Selamat datang di :</span>
              <div className="logo-area bg-[#ffe4de] rounded-[15px] p-[15px] flex flex-col items-center justify-center border-3 border-[#2E4E3F] w-full">
                <span className="normal-font text-[35px] text-[#2E4E3F] font-extrabold leading-tight uppercase">SNAPBOOTH</span>
              </div>
              <span className="normal-font text-[16px] font-medium leading-wide tracking-tight text-center max-w-[450px]">Kami mengabadikan momen berharga dalam kebersamaan melalui foto yang indah dan berkesan.</span>
              <button 
                onClick={handleStartSession}
                className="normal-font cursor-pointer hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] transition-all duration-300 flex flex-row justify-center items-center gap-[10px] py-[14px] px-[20px] bg-[#5AA47C] rounded-[10px] text-[white] text-[20px] font-bold leading-tight border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]"
              >
                Mulai Sesi Foto <img src="https://hunz6oof8m.ufs.sh/f/VgAMAWJatI06pts0SOyYj5vz9CJyrVEaNBPOh40Qu1m7fF3g" alt="arrow" className="p-[4px] bg-white rounded-[8px] w-[25px] h-[25px]" />
              </button>
            </div>
          )}
          
          {currentStep === "choose" && (
            <Choose 
              onBack={handleBack} 
              onQrisPayment={handleSnapPayment}
              onCashPayment={handleCashPayment}
            />
          )}

          {currentStep === "snap-payment" && (
            <SnapPayment 
              onBack={handleBackToChoose} 
              onPaymentSuccess={handlePaymentSuccess}
              onTransactionCreated={handleTransactionCreated}
            />
          )}

          {currentStep === "cash-voucher-payment" && (
            <CashVoucherPayment 
              onBack={handleBackToChoose} 
              onPaymentSuccess={handlePaymentSuccess}
            />
          )}
        </div>
      </div>
      
      {/* Offline Toast Notification */}
      {showOfflineToast && (
        <div className={`fixed bottom-4 normal-font right-4 bg-red-500 text-white px-5 py-4 rounded-lg shadow-lg border-2 border-red-600 flex items-center gap-3 z-50 transition-all duration-300 ease-in-out ${
          isToastEntering 
            ? 'opacity-0 transform translate-y-4 scale-95' 
            : isToastExiting 
            ? 'opacity-0 transform translate-y-4 scale-95' 
            : 'opacity-100 transform translate-y-0 scale-100'
        }`}>
          <div className="w-3 h-3 bg-red-300 rounded-full animate-pulse"></div>
          <div className="flex flex-col">
            <span className="font-bold text-sm">Pembayaran Tidak Dapat Dilakukan</span>
            <span className="font-medium text-xs opacity-90">Karena jaringan offline</span>
          </div>
        </div>
      )}
    </div>
  );
}
