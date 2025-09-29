"use client";

import { useState, useEffect, useRef } from "react";

interface CashVoucherPaymentProps {
  onBack: () => void;
  onPaymentSuccess: () => void;
}

// Card/Voucher SVG Icon Component
const CardIcon = ({ className = "" }: { className?: string }) => (
  <svg 
    className={className} 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M2 6C2 4.89543 2.89543 4 4 4H20C21.1046 4 22 4.89543 22 6V18C22 19.1046 21.1046 20 20 20H4C2.89543 20 2 19.1046 2 18V6Z" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M2 10H22" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
);

// Check Icon Component
const CheckIcon = ({ className = "" }: { className?: string }) => (
  <svg 
    className={className} 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" 
      stroke="currentColor" 
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
);

// NFC Icon Component
const NFCIcon = ({ className = "" }: { className?: string }) => (
  <svg 
    className={className} 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M6 8.32a3 3 0 0 1 0 7.36" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M9.5 6.5a7 7 0 0 1 0 11" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M13 4.5a11 11 0 0 1 0 15" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <circle 
      cx="18" 
      cy="12" 
      r="2" 
      stroke="currentColor" 
      strokeWidth="2"
    />
  </svg>
);

// Camera SVG Icon Component
const CameraIcon = ({ className = "" }: { className?: string }) => (
  <svg 
    className={className} 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M23 19C23 19.5304 22.7893 20.0391 22.4142 20.4142C22.0391 20.7893 21.5304 21 21 21H3C2.46957 21 1.96086 20.7893 1.58579 20.4142C1.21071 20.0391 1 19.5304 1 19V8C1 7.46957 1.21071 6.96086 1.58579 6.58579C1.96086 6.21071 2.46957 6 3 6H7L9 4H15L17 6H21C21.5304 6 22.0391 6.21071 22.4142 6.58579C22.7893 6.96086 23 7.46957 23 8V19Z" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
    <path 
      d="M12 17C14.2091 17 16 15.2091 16 13C16 10.7909 14.2091 9 12 9C9.79086 9 8 10.7909 8 13C8 15.2091 9.79086 17 12 17Z" 
      stroke="currentColor" 
      strokeWidth="2" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
);

export default function CashVoucherPayment({ onBack, onPaymentSuccess }: CashVoucherPaymentProps) {
  const [voucherCode, setVoucherCode] = useState('');
  const [isValidating, setIsValidating] = useState(false);
  const [validationStatus, setValidationStatus] = useState<'idle' | 'success' | 'error'>('idle');
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'success' | 'processing'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [isNFCListening, setIsNFCListening] = useState(true);
  
  // Toast state
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [isToastExiting, setIsToastExiting] = useState(false);
  const toastTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const nfcTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Toast functions
  const showToastMessage = (message: string) => {
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    
    setToastMessage(message);
    setShowToast(true);
    setIsToastExiting(false);
    
    toastTimeoutRef.current = setTimeout(() => {
      setIsToastExiting(true);
      setTimeout(() => {
        setShowToast(false);
        setIsToastExiting(false);
      }, 300);
    }, 4000);
  };

  // NFC listener simulation - listens for rapid input changes
  useEffect(() => {
    const handleNFCInput = () => {
      if (nfcTimeoutRef.current) {
        clearTimeout(nfcTimeoutRef.current);
      }
      
      // If input changes rapidly (typical of NFC tap), auto-validate after short delay
      nfcTimeoutRef.current = setTimeout(() => {
        if (voucherCode.length > 5 && isNFCListening && validationStatus !== 'success') {
          console.log('NFC input detected, auto-validating...');
          handleValidateVoucher();
        }
      }, 500);
    };

    if (voucherCode && isNFCListening && validationStatus !== 'success') {
      handleNFCInput();
    }

    return () => {
      if (nfcTimeoutRef.current) {
        clearTimeout(nfcTimeoutRef.current);
      }
    };
  }, [voucherCode, isNFCListening, validationStatus]);

  // Focus input on mount
  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }, []);

  // Handle camera button click
  const handleCameraClick = async () => {
    setPaymentStatus('processing');
    
    try {
      // First API call to fallback
      console.log('Making first API call to fallback...');
      try {
        const fallbackResponse = await fetch('http://localhost:4499/api/fallback?successpayment=1', {
          method: 'GET',
        });
        
        if (fallbackResponse.ok) {
          console.log('First API call successful');
        } else {
          console.warn('First API call failed with status:', fallbackResponse.status);
        }
      } catch (apiError) {
        console.warn('First API call failed:', apiError);
      }

      // Wait 1.5 seconds
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Second API call to start print
      console.log('Making second API call to start print...');
      try {
        const startResponse = await fetch('http://localhost:1500/api/start?mode=print&password=B5L7NxMAkG66-ZAY', {
          method: 'GET',
        });
        
        if (startResponse.ok) {
          console.log('Second API call successful');
        } else {
          console.warn('Second API call failed with status:', startResponse.status);
        }
      } catch (apiError) {
        console.warn('Second API call failed:', apiError);
      }

      // Navigate back to welcome page after a short delay
      setTimeout(() => {
        console.log('Navigating back to welcome page...');
        onPaymentSuccess();
      }, 1000);

    } catch (error) {
      console.error('Error in camera click flow:', error);
      // Still navigate back even if API calls fail
      setTimeout(() => {
        console.log('Navigating back to welcome page after error...');
        onPaymentSuccess();
      }, 1000);
    }
  };

  const handleValidateVoucher = async () => {
    if (!voucherCode.trim()) {
      showToastMessage('Masukkan kode voucher terlebih dahulu');
      return;
    }

    setIsValidating(true);
    setValidationStatus('idle');
    setErrorMessage('');
    setIsNFCListening(false);

    try {
      const response = await fetch('/api/voucher-verify', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          kamucantikbanged: voucherCode.trim()
        })
      });

      const result = await response.json();
      
      // Log API response for debugging
      console.log('Frontend - Voucher API Response:', {
        status: response.status,
        data: result,
        request: { kamucantikbanged: voucherCode.trim() }
      });

      if (result.success) {
        setValidationStatus('success');
        setPaymentStatus('success');
        setIsNFCListening(false); // Disable NFC listening permanently after success
        showToastMessage('Voucher berhasil diverifikasi! Kartu telah digunakan.');
        
        // Clear input after successful validation
        setVoucherCode('');
      } else {
        setValidationStatus('error');
        let errorMsg = 'Terjadi kesalahan';
        
        switch (result.error_code) {
          case 'VOUCHER_NOT_FOUND':
            errorMsg = 'Kode voucher tidak ditemukan';
            break;
          case 'VOUCHER_ALREADY_USED':
            errorMsg = 'Voucher sudah pernah digunakan';
            break;
          case 'INVALID_HAI_MANIS':
            errorMsg = 'Autentikasi tidak valid';
            break;
          default:
            errorMsg = result.message || 'Terjadi kesalahan server';
        }
        
        setErrorMessage(errorMsg);
        showToastMessage(errorMsg);
        
        // Re-enable NFC listening after error
        setTimeout(() => {
          setIsNFCListening(true);
        }, 2000);
      }
    } catch (error) {
      console.error('Voucher validation error:', error);
      setValidationStatus('error');
      setErrorMessage('Gagal terhubung ke server');
      showToastMessage('Gagal terhubung ke server');
      
      // Re-enable NFC listening after error
      setTimeout(() => {
        setIsNFCListening(true);
      }, 2000);
    } finally {
      setIsValidating(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Prevent input changes if voucher was already successfully used
    if (validationStatus === 'success') {
      return;
    }
    
    const value = e.target.value.toUpperCase();
    setVoucherCode(value);
    
    // Reset validation status when user types
    if (validationStatus !== 'idle') {
      setValidationStatus('idle');
      setErrorMessage('');
      setIsNFCListening(true);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isValidating) {
      handleValidateVoucher();
    }
  };

  // Cleanup timeouts on unmount
  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
      if (nfcTimeoutRef.current) {
        clearTimeout(nfcTimeoutRef.current);
      }
    };
  }, []);

  return (
    <div className="flex flex-col items-center justify-center gap-[25px] w-full max-w-[600px]">
      <span className="main-font text-[45px] text-[#2E4E3F] font-semibold leading-tight text-center">
        Pembayaran Tunai / Voucher
      </span>
      
      {/* Show camera interface when payment is successful */}
      {paymentStatus === 'success' ? (
        <div className="success-container bg-white rounded-[15px] p-[40px] border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F] w-full flex flex-col items-center">
          <span className="normal-font text-[18px] text-[#2E4E3F] font-semibold mb-[20px]">
            Pembayaran Berhasil!
          </span>
          
          <button
            onClick={(e) => {
              e.preventDefault();
              handleCameraClick();
            }}
            className="camera-button cursor-pointer hover:scale-105 transition-all duration-300"
          >
            <div className="camera-icon-container w-[120px] h-[120px] bg-[#5AA47C] rounded-full flex items-center justify-center mb-[20px] hover:bg-[#4a9266] transition-colors duration-300">
              <CameraIcon className="w-[60px] h-[60px] text-white" />
            </div>
          </button>
          
          <div className="text-center">
            <span className="normal-font text-[16px] text-[#2E4E3F] font-medium block mb-[5px]">
              Klik kamera untuk mulai sesi foto
            </span>
            <span className="normal-font text-[14px] text-gray-600">
              Foto akan diproses setelah klik
            </span>
          </div>
        </div>
      ) : paymentStatus === 'processing' ? (
        <div className="processing-container bg-white rounded-[15px] p-[40px] border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F] w-full flex flex-col items-center">
          <span className="normal-font text-[18px] text-[#2E4E3F] font-semibold mb-[20px]">
            Memulai Aplikasi
          </span>
          
          <div className="camera-icon-container w-[120px] h-[120px] bg-[#5AA47C] rounded-full flex items-center justify-center mb-[20px] animate-pulse">
            <CameraIcon className="w-[60px] h-[60px] text-white" />
          </div>
          
          <div className="text-center">
            <span className="normal-font text-[16px] text-[#2E4E3F] font-medium block mb-[5px]">
              Aplikasi sedang dijalankan...
            </span>
            <span className="normal-font text-[14px] text-gray-600">
              Mohon tunggu sebentar
            </span>
          </div>
        </div>
      ) : (
        <>
        {/* NFC Status Indicator */}
      <div className={`flex items-center gap-[10px] px-[15px] py-[8px] rounded-[8px] transition-all duration-300 ${
        validationStatus === 'success'
          ? 'bg-[#FF8C42] text-white'
          : isNFCListening 
          ? 'bg-[#5AA47C] text-white' 
          : 'bg-[#CCCCCC] text-[#2E4E3F]'
      }`}>
        <NFCIcon className="w-[20px] h-[20px]" />
        <span className="normal-font text-[14px] font-medium">
          {validationStatus === 'success'
            ? 'Kartu telah digunakan'
            : isNFCListening 
            ? 'Siap menerima NFC' 
            : 'NFC tidak aktif'
          }
        </span>
        {isNFCListening && validationStatus !== 'success' && (
          <div className="w-[8px] h-[8px] bg-white rounded-full animate-pulse"></div>
        )}
      </div>

      {/* Voucher Input Form */}
      <div className="voucher-form flex flex-col gap-[20px] w-full">
        <div className="input-container relative">
          <div className="flex items-center gap-[10px] mb-[8px]">
            <CardIcon className="w-[20px] h-[20px] text-[#2E4E3F]" />
            <span className="normal-font text-[18px] text-[#2E4E3F] font-medium">
              Masukkan Kode Voucher
            </span>
          </div>
          
          <input
            ref={inputRef}
            type="password"
            value={voucherCode}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Ketik kode voucher atau tap kartu NFC"
            disabled={isValidating || validationStatus === 'success'}
            className={`w-full px-[20px] py-[15px] text-[18px] font-mono rounded-[10px] border-3 transition-all duration-300 focus:outline-none ${
              validationStatus === 'success'
                ? 'border-[#5AA47C] bg-[#f0f9f4] text-[#2E4E3F]'
                : validationStatus === 'error'
                ? 'border-[#FF6B6B] bg-[#fff5f5] text-[#2E4E3F]'
                : 'border-[#2E4E3F] bg-white text-[#2E4E3F] focus:border-[#5AA47C] focus:shadow-[0px_0px_0px_3px_rgba(90,164,124,0.1)]'
            }`}
          />
          
          {/* Validation Status Icon */}
          {validationStatus === 'success' && (
            <div className="absolute right-[15px] top-[50px] transform -translate-y-1/2">
              <CheckIcon className="w-[24px] h-[24px] text-[#5AA47C]" />
            </div>
          )}
        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="error-message bg-[#fff5f5] border-2 border-[#FF6B6B] rounded-[8px] px-[15px] py-[10px]">
            <span className="normal-font text-[14px] text-[#FF6B6B] font-medium">
              {errorMessage}
            </span>
          </div>
        )}

        {/* Button Container */}
        <div className="flex flex-col gap-[15px] w-full">
          {/* Validate Button */}
          <button
            onClick={handleValidateVoucher}
            disabled={isValidating || !voucherCode.trim() || validationStatus === 'success'}
            className={`validate-button hidden normal-font cursor-pointer transition-all duration-300 flex flex-row justify-center items-center gap-[10px] py-[15px] px-[25px] rounded-[10px] text-[18px] font-bold leading-tight border-3 border-[#2E4E3F] ${
              isValidating
                ? 'bg-[#CCCCCC] text-[#666666] cursor-not-allowed'
                : validationStatus === 'success'
                ? 'bg-[#5AA47C] text-white shadow-[2px_2px_0px_0px_#2E4E3F]'
                : !voucherCode.trim()
                ? 'bg-[#CCCCCC] text-[#666666] cursor-not-allowed'
                : 'bg-[#FF8C42] text-white hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]'
            }`}
          >
            {isValidating ? (
              <>
                <div className="w-[20px] h-[20px] border-2 border-[#666666] border-t-transparent rounded-full animate-spin"></div>
                Memvalidasi...
              </>
            ) : validationStatus === 'success' ? (
              <>
                <CheckIcon className="w-[20px] h-[20px]" />
                Voucher Valid
              </>
            ) : (
              'Validasi Voucher'
            )}
          </button>

          {/* Clear NFC Button */}
           <button
             onClick={() => {
               setVoucherCode('');
               setValidationStatus('idle');
               setErrorMessage('');
               setIsNFCListening(true);
               if (inputRef.current) {
                 inputRef.current.focus();
               }
             }}
             disabled={isValidating || validationStatus === 'success'}
             className={`clear-button normal-font cursor-pointer transition-all duration-300 flex flex-row justify-center items-center gap-[10px] py-[14px] px-[20px] rounded-[10px] text-[18px] font-bold leading-tight border-3 border-[#2E4E3F] ${
               isValidating || validationStatus === 'success'
                 ? 'bg-[#CCCCCC] text-[#666666] cursor-not-allowed'
                 : 'bg-white text-[#2E4E3F] hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]'
             }`}
           >
             Clear NFC
           </button>
        </div>
      </div>

      {/* Back Button - always enabled, never disabled */}
      <button 
        onClick={onBack}
        className="back-button normal-font cursor-pointer transition-all duration-300 flex flex-row justify-center items-center gap-[10px] py-[12px] px-[20px] rounded-[10px] text-[18px] font-bold leading-tight border-3 border-[#2E4E3F] bg-[#CCCCCC] text-[#2E4E3F] hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]"
      >
        Kembali
      </button>

        </>
      )}

      {/* Toast Notification */}
      {showToast && (
        <div className={`fixed bottom-4 normal-font right-4 px-5 py-4 rounded-lg shadow-lg border-2 flex items-center gap-3 z-50 transition-all duration-300 ease-in-out ${
          validationStatus === 'success'
            ? 'bg-green-500 text-white border-green-600'
            : 'bg-red-500 text-white border-red-600'
        } ${
          isToastExiting 
            ? 'opacity-0 transform translate-y-4 scale-95' 
            : 'opacity-100 transform translate-y-0 scale-100'
        }`}>
          <div className={`w-3 h-3 rounded-full animate-pulse ${
            validationStatus === 'success' ? 'bg-green-300' : 'bg-red-300'
          }`}></div>
          <span className="font-medium text-sm">{toastMessage}</span>
        </div>
      )}
    </div>
  );
}