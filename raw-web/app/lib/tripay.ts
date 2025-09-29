// Tripay Configuration
const IS_PRODUCTION = true; // Set to true for production
const USE_PHP_FORWARDER = true; // Set to true to use PHP forwarder

// PHP Forwarder Configuration
const PHP_FORWARDER_CONFIG = {
  baseUrl: 'https://forwarder.snapbooth.click/tripay-forwarder.php', // Ganti dengan URL hosting cPanel Anda
  apiKey: 'KnSJAP2881392SQIisuQ' // Harus sama dengan yang di PHP
};

// Production credentials
const PRODUCTION_CONFIG = {
  apiKey: 'aNe8LAdn2lRfj4lrkfFkTz3vqzJJ8k646ccQyOLg',
  privateKey: 'GmsLp-OwNlg-XG9Zp-0Plas-zw5lo', 
  merchantCode: 'T44241',
  baseUrl: USE_PHP_FORWARDER ? PHP_FORWARDER_CONFIG.baseUrl : 'https://tripay.co.id/api'
};

// Sandbox credentials (gunakan kredensial yang sudah ada)
const SANDBOX_CONFIG = {
  apiKey: 'DEV-Md9QQzemuIVCweydCuChMrHilzKOD2LoBlIoJ7yG',
  privateKey: 'hsB6m-qB7eN-dkNqH-pxJDk-AjnIu', 
  merchantCode: 'T43142',
  baseUrl: 'https://tripay.co.id/api-sandbox'
};

// Use appropriate configuration
export const tripayConfig = {
  ...(IS_PRODUCTION ? PRODUCTION_CONFIG : SANDBOX_CONFIG),
  isProduction: IS_PRODUCTION
};

export interface TripayTransactionData {
  method: string;
  merchant_ref: string;
  amount: number;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  order_items: Array<{
    sku: string;
    name: string;
    price: number;
    quantity: number;
  }>;
  expired_time: number;
  signature: string;
}

export interface TripayTransactionResponse {
  success: boolean;
  message: string;
  data: {
    reference: string;
    merchant_ref: string;
    payment_selection_type: string;
    payment_method: string;
    payment_name: string;
    customer_name: string;
    customer_email: string;
    customer_phone: string;
    callback_url: string;
    return_url: string;
    amount: number;
    fee_merchant: number;
    fee_customer: number;
    total_fee: number;
    amount_received: number;
    pay_code: string;
    pay_url: string;
    checkout_url: string;
    status: string;
    expired_time: number;
    order_items: Array<any>;
    instructions: Array<{
      title: string;
      steps: Array<string>;
    }>;
    qr_code: string;
    qr_url: string;
  };
}

export interface TripayStatusResponse {
  success: boolean;
  message: string;
  data: {
    reference: string;
    merchant_ref: string;
    payment_method: string;
    payment_name: string;
    customer_name: string;
    customer_email: string;
    customer_phone: string;
    amount: number;
    fee_merchant: number;
    fee_customer: number;
    total_fee: number;
    amount_received: number;
    status: string;
    paid_at: string;
  };
}

// Generate signature for Tripay API
export function generateSignature(merchantCode: string, merchantRef: string, amount: number): string {
  const crypto = require('crypto');
  const data = merchantCode + merchantRef + amount;
  return crypto.createHmac('sha256', tripayConfig.privateKey).update(data).digest('hex');
}

// Create closed payment transaction
export async function createClosedPayment(orderData: {
  amount: number;
  customerDetails: {
    first_name: string;
    email: string;
    phone: string;
  };
  merchantRef: string;
  method?: string;
}): Promise<TripayTransactionResponse> {
  try {
    console.log('=== Tripay Create Transaction ===');
    console.log('Environment:', IS_PRODUCTION ? 'PRODUCTION' : 'SANDBOX');
    console.log('Using PHP Forwarder:', USE_PHP_FORWARDER);
    console.log('Base URL:', tripayConfig.baseUrl);
    
    const method = orderData.method || 'QRIS';
    
    if (USE_PHP_FORWARDER) {
      // Use PHP forwarder
      const response = await fetch(`${tripayConfig.baseUrl}?action=create-transaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': PHP_FORWARDER_CONFIG.apiKey,
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          amount: orderData.amount,
          customerDetails: orderData.customerDetails,
          merchantRef: orderData.merchantRef,
          method: method
        })
      });

      console.log('📊 Response Status:', response.status);
      const responseText = await response.text();
      console.log('📊 Raw Response:', responseText);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}, response: ${responseText}`);
      }

      const data = JSON.parse(responseText);
      console.log('✅ Success Response:', JSON.stringify(data, null, 2));
      return data;
    } else {
      // Original direct API call logic
      const expiredTime = Math.floor(Date.now() / 1000) + (24 * 60 * 60);
      const signature = generateSignature(
        tripayConfig.merchantCode,
        orderData.merchantRef,
        orderData.amount
      );
      
      const transactionData: TripayTransactionData = {
        method: method,
        merchant_ref: orderData.merchantRef,
        amount: orderData.amount,
        customer_name: orderData.customerDetails.first_name,
        customer_email: orderData.customerDetails.email,
        customer_phone: orderData.customerDetails.phone,
        order_items: [
          {
            sku: 'snapbooth-session',
            name: 'Snapbooth Photo Session',
            price: orderData.amount,
            quantity: 1
          }
        ],
        expired_time: expiredTime,
        signature: signature
      };
      
      const response = await fetch(`${tripayConfig.baseUrl}/transaction/create`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${tripayConfig.apiKey}`,
          'Accept': 'application/json'
        },
        body: JSON.stringify(transactionData)
      });

      const responseText = await response.text();
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}, response: ${responseText}`);
      }

      const data = JSON.parse(responseText);
      return data;
    }
  } catch (error) {
    console.error('❌ Error creating Tripay transaction:', error);
    throw error;
  }
}

// Check transaction status
export async function checkTransactionStatus(reference: string): Promise<TripayStatusResponse> {
  try {
    console.log('=== Tripay Check Status ===');
    console.log('Reference:', reference);
    
    if (USE_PHP_FORWARDER) {
      const response = await fetch(`${tripayConfig.baseUrl}?action=check-status&reference=${encodeURIComponent(reference)}`, {
        method: 'GET',
        headers: {
          'X-API-Key': PHP_FORWARDER_CONFIG.apiKey,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorData}`);
      }

      const data = await response.json();
      console.log('✅ Status Check Response:', JSON.stringify(data, null, 2));
      return data;
    } else {
      const response = await fetch(`${tripayConfig.baseUrl}/transaction/detail?reference=${reference}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${tripayConfig.apiKey}`,
          'Accept': 'application/json'
        }
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorData.message || 'Unknown error'}`);
      }

      const data = await response.json();
      return data;
    }
  } catch (error) {
    console.error('❌ Error checking Tripay transaction status:', error);
    throw error;
  }
}

// Generate unique merchant reference
export function generateMerchantRef(): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substring(2, 8).toUpperCase();
  return `SNAPBOOTH-${timestamp}-${random}`;
}

// Check if online
export function isOnline(): boolean {
  return typeof navigator !== 'undefined' && navigator.onLine;
}

// Map Tripay status to standardized status
export function mapTripayStatus(tripayStatus: string): 'pending' | 'paid' | 'failed' | 'expired' {
  switch (tripayStatus.toUpperCase()) {
    case 'PAID':
      return 'paid';
    case 'UNPAID':
      return 'pending';
    case 'EXPIRED':
      return 'expired';
    case 'FAILED':
      return 'failed';
    default:
      return 'pending';
  }
}