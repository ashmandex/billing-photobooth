"use client";

import { useState, useEffect, useRef } from "react";

interface TripayPaymentProps {
  onBack: () => void;
  onPaymentSuccess: () => void;
  onTransactionCreated?: (transactionId: string) => void;
}

interface TripayTransactionData {
  reference: string;
  merchant_ref: string;
  payment_method: string;
  payment_name: string;
  amount: number;
  fee_customer: number;
  total_amount: number;
  pay_code: string;
  pay_url: string;
  checkout_url: string;
  qr_code: string;
  qr_url: string;
  status: string;
  expired_time: number;
  instructions: Array<{
    title: string;
    steps: Array<string>;
  }>;
}

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

// Checkmark SVG Icon Component  
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

// Close/X SVG Icon Component
const CloseIcon = ({ className = "" }: { className?: string }) => (
  <svg 
    className={className} 
    viewBox="0 0 24 24" 
    fill="none" 
    xmlns="http://www.w3.org/2000/svg"
  >
    <path 
      d="M18 6L6 18M6 6L18 18" 
      stroke="currentColor" 
      strokeWidth="2.5" 
      strokeLinecap="round" 
      strokeLinejoin="round"
    />
  </svg>
);

export default function TripayPayment({ onBack, onPaymentSuccess, onTransactionCreated }: TripayPaymentProps) {
  const [paymentStatus, setPaymentStatus] = useState<'loading' | 'ready' | 'redirecting' | 'success' | 'failed' | 'processing'>('loading');
  const [transactionData, setTransactionData] = useState<TripayTransactionData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isOfflineCancelled, setIsOfflineCancelled] = useState(false);
  const [showQrisModal, setShowQrisModal] = useState(false);
  const [isCheckingStatus, setIsCheckingStatus] = useState(false);
  
  // Toast state
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [isToastExiting, setIsToastExiting] = useState(false);
  const toastTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  // Add refs to prevent duplicate API calls
  const isCreatingTransaction = useRef(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  const statusCheckIntervalRef = useRef<NodeJS.Timeout | null>(null);

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

  // Create Tripay transaction on component mount
  useEffect(() => {
    const createTransaction = async () => {
      if (isCreatingTransaction.current) {
        console.log('Transaction creation already in progress, skipping...');
        return;
      }

      isCreatingTransaction.current = true;
      abortControllerRef.current = new AbortController();

      try {
        console.log('Creating Tripay transaction...');
        const response = await fetch('/api/tripay/create-qris', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            amount: 30000,
            customerDetails: {
              first_name: 'Customer',
              email: 'customer@snapbooth.com',
              phone: '081234567890'
            }
          }),
          signal: abortControllerRef.current.signal
        });

        const result = await response.json();
        console.log('Tripay API Response:', result);

        if (result.success && result.data) {
          console.log('Transaction created successfully:', result.data);
          setTransactionData(result.data);
          
          if (onTransactionCreated) {
            onTransactionCreated(result.data.reference);
          }
          
          setPaymentStatus('ready');
          
          // Auto-show modal after 1 second
          setTimeout(() => {
            setShowQrisModal(true);
            setPaymentStatus('redirecting');
          }, 1000);
          
          // Start periodic status checking every 5 seconds
          statusCheckIntervalRef.current = setInterval(async () => {
            try {
              const statusResponse = await fetch(`/api/tripay/check-status?reference=${result.data.reference}`);
              const statusResult = await statusResponse.json();
              
              if (statusResult.success && statusResult.data) {
                const mappedStatus = statusResult.data.mapped_status;
                console.log('Periodic status check:', mappedStatus);
                
                if (mappedStatus === 'paid') {
                  console.log('Payment detected as successful!');
                  setShowQrisModal(false);
                  setPaymentStatus('success');
                  if (statusCheckIntervalRef.current) {
                    clearInterval(statusCheckIntervalRef.current);
                  }
                } else if (mappedStatus === 'failed' || mappedStatus === 'expired') {
                  console.log('Payment failed or expired:', mappedStatus);
                  setShowQrisModal(false);
                  setPaymentStatus('failed');
                  setError('Transaksi Gagal atau Kadaluarsa');
                  if (statusCheckIntervalRef.current) {
                    clearInterval(statusCheckIntervalRef.current);
                  }
                }
              }
            } catch (error) {
              console.error('Error in periodic status check:', error);
            }
          }, 5000);
          
          // Clear interval after 30 minutes
          setTimeout(() => {
            if (statusCheckIntervalRef.current) {
              clearInterval(statusCheckIntervalRef.current);
            }
          }, 1800000);
          
        } else {
          console.error('Tripay API failed:', result.error, result.details);
          setPaymentStatus('failed');
          setError(`API Error: ${result.error}`);
        }
      } catch (error) {
        if (error instanceof Error && error.name === 'AbortError') {
          console.log('Transaction creation was cancelled');
          return;
        }
        
        console.error('Error creating transaction:', error);
        setPaymentStatus('failed');
        setError(`Network Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      } finally {
        isCreatingTransaction.current = false;
      }
    };

    createTransaction();

    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (statusCheckIntervalRef.current) {
        clearInterval(statusCheckIntervalRef.current);
      }
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
      isCreatingTransaction.current = false;
    };
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

  // Handle manual payment success check
  const handleManualSuccess = async () => {
    if (!transactionData || isCheckingStatus) return;
    
    console.log('Checking transaction status manually...');
    setIsCheckingStatus(true);
    
    try {
      const response = await fetch(`/api/tripay/check-status?reference=${transactionData.reference}`);
      const result = await response.json();
      
      console.log('Manual status check result:', result);
      
      if (result.success && result.data) {
        const mappedStatus = result.data.mapped_status;
        console.log('Actual transaction status from Tripay:', mappedStatus);
        
        if (mappedStatus === 'paid') {
          console.log('Transaction is PAID, marking as success');
          setShowQrisModal(false);
          setPaymentStatus('success');
        } else if (mappedStatus === 'pending') {
          console.log('Transaction still pending - not paid yet');
          showToastMessage('Belum Dibayar|Silakan bayar terlebih dahulu');
        } else if (mappedStatus === 'failed' || mappedStatus === 'expired') {
          console.log('Transaction failed with status:', mappedStatus);
          setShowQrisModal(false);
          setPaymentStatus('failed');
          setError('Transaksi Gagal atau Kadaluarsa');
        } else {
          console.log('Unknown transaction status:', mappedStatus);
          showToastMessage(`Status Tidak Diketahui|Status: ${mappedStatus}`);
        }
      } else {
        console.error('Failed to check transaction status:', result.error);
        showToastMessage('Gagal Mengecek Status|Silakan coba lagi');
      }
    } catch (error) {
      console.error('Error checking transaction status:', error);
      showToastMessage('Error Jaringan|Silakan coba lagi');
    } finally {
      setIsCheckingStatus(false);
    }
  };

  // Handle modal close
  const handleModalClose = () => {
    console.log('User closed modal, cancelling transaction...');
    setShowQrisModal(false);
    setPaymentStatus('failed');
    setError('Pembayaran Dibatalkan');
  };

  // Monitor network status
  useEffect(() => {
    const handleOffline = () => {
      if (paymentStatus === 'ready' || paymentStatus === 'loading') {
        console.log('Network went offline, cancelling transaction...');
        setIsOfflineCancelled(true);
        setPaymentStatus('failed');
        setError('Terjadi Anomali Jaringan');
        setShowQrisModal(false);
      } else if (showQrisModal && paymentStatus === 'redirecting') {
        console.log('Network went offline during payment, closing modal...');
        setShowQrisModal(false);
        setPaymentStatus('failed');
        setError('Terjadi Anomali Jaringan');
        setIsOfflineCancelled(true);
      }
    };

    const handleOnline = () => {
      console.log('Network back online');
    };

    if (typeof window !== 'undefined') {
      window.addEventListener('offline', handleOffline);
      window.addEventListener('online', handleOnline);

      return () => {
        window.removeEventListener('offline', handleOffline);
        window.removeEventListener('online', handleOnline);
      };
    }
  }, [paymentStatus, showQrisModal]);

  const formatAmount = (amount: string | number) => {
    const numAmount = typeof amount === 'string' ? parseInt(amount, 10) : amount;
    if (isNaN(numAmount)) return '30000';
    return numAmount.toLocaleString('id-ID');
  };

  return (
    <div id="content-3" className="flex flex-col items-center justify-center gap-[20px]">
      <span className="main-font text-[45px] text-[#2E4E3F] font-semibold leading-tight text-center">
        Bayar dengan QRIS
      </span>
      
      <div className="snap-container flex flex-col items-center gap-[20px] w-full max-w-[500px]">
        {/* Show camera icon when payment is successful */}
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
        ) : paymentStatus === 'redirecting' ? (
          <div className="redirecting-container bg-white rounded-[15px] p-[40px] border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F] w-full flex flex-col items-center">
            <span className="normal-font text-[18px] text-[#2E4E3F] font-semibold mb-[20px]">
              QR Code Siap
            </span>
            
            <div className="payment-icon-container w-[120px] h-[120px] bg-purple-500 rounded-full flex items-center justify-center mb-[20px] animate-pulse">
              <div className="text-white text-[40px]">📱</div>
            </div>
            
            <div className="text-center">
              <span className="normal-font text-[16px] text-[#2E4E3F] font-medium block mb-[5px]">
                Silakan scan QR code di modal
              </span>
              <span className="normal-font text-[14px] text-gray-600">
                Modal akan terbuka otomatis
              </span>
            </div>
          </div>
        ) : paymentStatus === 'failed' ? (
          <div className="error-container bg-white rounded-[15px] p-[40px] border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F] w-full flex flex-col items-center">
            <span className="normal-font text-[18px] text-[#2E4E3F] font-semibold mb-[20px]">
              {error === 'Pembayaran Dibatalkan' ? 'Pembayaran Dibatalkan' : 'Pembayaran Gagal'}
            </span>
            
            <div className="text-center">
              <span className="normal-font text-[16px] text-red-600 font-medium block mb-[5px]">
                {error === 'Pembayaran Dibatalkan' ? 'Dibatalkan oleh pengguna' : (error || 'Terjadi kesalahan')}
              </span>
              <span className="normal-font text-[14px] text-gray-600">
                Silakan coba lagi
              </span>
            </div>
          </div>
        ) : (
          <div className="loading-container bg-white rounded-[15px] p-[40px] border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F] w-full flex flex-col items-center">
            <span className="normal-font text-[18px] text-[#2E4E3F] font-semibold mb-[20px]">
              Membuat Transaksi
            </span>
            
            <div className="loading-icon-container w-[120px] h-[120px] bg-[#5AA47C] rounded-full flex items-center justify-center mb-[20px]">
              <div className="loading-spinner w-[60px] h-[60px] border-4 border-white border-t-transparent rounded-full animate-spin"></div>
            </div>
            
            <div className="text-center">
              <span className="normal-font text-[16px] text-[#2E4E3F] font-medium block mb-[5px]">
                Menyiapkan pembayaran...
              </span>
              <span className="normal-font text-[14px] text-gray-600">
                Mohon tunggu sebentar
              </span>
            </div>
          </div>
        )}
      </div>
      
      {paymentStatus !== 'success' && paymentStatus !== 'processing' && (
        <button 
          onClick={onBack}
          className="back-button normal-font cursor-pointer hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] transition-all duration-300 flex flex-row justify-center items-center gap-[10px] py-[12px] px-[20px] bg-[#CCCCCC] rounded-[10px] text-[#2E4E3F] text-[18px] font-bold leading-tight border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]"
        >
          Kembali
        </button>
      )}
      
      {/* QRIS Payment Modal */}
      {showQrisModal && transactionData && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="relative bg-white rounded-[20px] w-full max-w-4xl h-[90vh] flex flex-col border-3 border-[#2E4E3F] shadow-[4px_4px_0px_0px_#2E4E3F]">
            {/* Modal Header */}
            <div className="flex justify-between items-center p-6 border-b-2 border-[#2E4E3F]">
              <div>
                <h2 className="normal-font text-[24px] text-[#2E4E3F] font-bold">
                  Pembayaran QRIS
                </h2>
                <p className="normal-font text-[14px] text-gray-600">
                  Total: Rp {formatAmount(transactionData.total_amount)} • ID: {transactionData.reference}
                </p>
              </div>
              <div className="flex gap-4">
                <button
                  onClick={handleManualSuccess}
                  disabled={isCheckingStatus}
                  className={`normal-font cursor-pointer hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] transition-all duration-300 flex flex-row justify-center items-center gap-[8px] py-[10px] px-[16px] rounded-[10px] text-white text-[16px] font-bold leading-tight border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F] ${
                    isCheckingStatus 
                      ? 'bg-gray-400 cursor-not-allowed opacity-70' 
                      : 'bg-[#5AA47C] hover:bg-[#4a9266]'
                  }`}
                >
                  {isCheckingStatus ? (
                    <>
                      <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Mengecek...
                    </>
                  ) : (
                    <>
                      <CheckIcon className="w-5 h-5" />
                      Selesai
                    </>
                  )}
                </button>
                <button
                  onClick={handleModalClose}
                  className="normal-font cursor-pointer hover:scale-98 hover:shadow-[0px_0px_0px_0px_#2E4E3F] transition-all duration-300 flex flex-row justify-center items-center gap-[8px] py-[10px] px-[16px] bg-[#CCCCCC] rounded-[10px] text-[#2E4E3F] text-[16px] font-bold leading-tight border-3 border-[#2E4E3F] shadow-[2px_2px_0px_0px_#2E4E3F]"
                >
                  <CloseIcon className="w-5 h-5" />
                  Tutup
                </button>
              </div>
            </div>
            
            {/* Modal Content - QR Code Display */}
            <div className="flex-1 p-6 flex items-center justify-center">
              <div className="text-center">
                {/* QR Code */}
                {transactionData.qr_url && (
                  <div className="mb-6">
                    <img 
                      src={transactionData.qr_url} 
                      alt="QR Code" 
                      className="mx-auto w-80 h-80 border-4 border-[#2E4E3F] rounded-[15px] shadow-[2px_2px_0px_0px_#2E4E3F]"
                    />
                  </div>
                )}
                
                {/* Payment Instructions */}
                <div className="hidden bg-gray-50 p-4 rounded-[10px] border-2 border-[#2E4E3F] max-w-md mx-auto">
                  <h3 className="normal-font text-[18px] text-[#2E4E3F] font-bold mb-3">
                    Scan QR Code untuk Bayar
                  </h3>
                  <p className="normal-font text-[14px] text-gray-600 mb-2">
                    <strong>Metode:</strong> {transactionData.payment_name}
                  </p>
                  <p className="normal-font text-[14px] text-gray-600 mb-2">
                    <strong>Jumlah:</strong> Rp {formatAmount(transactionData.total_amount)}
                  </p>
                  <p className="normal-font text-[14px] text-gray-600">
                    <strong>Referensi:</strong> {transactionData.reference}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* Toast Notification */}
      {showToast && (
        <div className={`fixed bottom-4 normal-font right-4 bg-red-500 text-white px-5 py-4 rounded-lg shadow-lg border-2 border-red-600 flex items-center gap-3 z-50 transition-all duration-300 ease-in-out ${
          isToastExiting 
            ? 'opacity-0 transform translate-y-4 scale-95' 
            : 'opacity-100 transform translate-y-0 scale-100'
        }`}>
          <div className="w-3 h-3 bg-red-300 rounded-full animate-pulse"></div>
          <div className="flex flex-col">
            {toastMessage.includes('|') ? (
              <>
                <span className="font-bold text-sm">{toastMessage.split('|')[0]}</span>
                <span className="font-medium text-xs opacity-90">{toastMessage.split('|')[1]}</span>
              </>
            ) : (
              <>
                <span className="font-bold text-sm">Error</span>
                <span className="font-medium text-xs opacity-90">{toastMessage}</span>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}