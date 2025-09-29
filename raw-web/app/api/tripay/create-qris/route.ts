import { NextRequest, NextResponse } from 'next/server';
import { createClosedPayment, generateMerchantRef, type TripayTransactionData } from '../../../lib/tripay';

export async function POST(request: NextRequest) {
  try {
    // Add error handling for JSON parsing
    let requestBody;
    try {
      requestBody = await request.json();
    } catch (jsonError) {
      console.error('JSON parsing error:', jsonError);
      return NextResponse.json(
        { error: 'Invalid JSON in request body' },
        { status: 400 }
      );
    }

    const { amount, customerDetails } = requestBody;

    console.log('=== Tripay API Call Debug ===');
    console.log('Received amount:', amount);
    console.log('Received customerDetails:', customerDetails);

    // Validate required fields
    if (!amount || !customerDetails) {
      console.error('Validation failed - missing required fields');
      return NextResponse.json(
        { error: 'Amount and customer details are required' },
        { status: 400 }
      );
    }

    // Validate and adjust amount (pindahkan ke sini)
    if (!amount || amount < 1000) {
      return NextResponse.json(
        { error: 'Amount must be at least Rp 1.000' },
        { status: 400 }
      );
    }

    const merchantRef = generateMerchantRef();
    console.log('Generated Merchant Ref:', merchantRef);

    // Create transaction with Tripay
    console.log('Calling Tripay API...');
    const tripayResponse = await createClosedPayment({
      amount,
      customerDetails,
      merchantRef,
      method: 'QRIS' // Ganti dari 'QRIS' ke channel yang aktif
    });

    console.log('Tripay API Response:', JSON.stringify(tripayResponse, null, 2));

    // Validate response
    if (!tripayResponse.success || !tripayResponse.data) {
      console.error('Invalid response from Tripay');
      throw new Error(tripayResponse.message || 'Tripay did not return valid data');
    }

    const { data } = tripayResponse;

    return NextResponse.json({
      success: true,
      data: {
        reference: data.reference,
        merchant_ref: data.merchant_ref,
        payment_method: data.payment_method,
        payment_name: data.payment_name,
        amount: data.amount,
        fee_customer: data.fee_customer,
        total_amount: data.amount + data.fee_customer,
        pay_code: data.pay_code,
        pay_url: data.pay_url,
        checkout_url: data.checkout_url,
        qr_code: data.qr_code,
        qr_url: data.qr_url,
        status: data.status,
        expired_time: data.expired_time,
        instructions: data.instructions
      }
    });

  } catch (error) {
    console.error('=== Tripay API Error ===');
    console.error('Full error:', error);
    console.error('Error message:', error instanceof Error ? error.message : 'Unknown error');
    
    return NextResponse.json(
      { 
        error: 'Failed to create Tripay transaction',
        details: error instanceof Error ? error.message : 'Unknown error',
        debug: process.env.NODE_ENV === 'development' ? {
          error: error instanceof Error ? error.message : 'Unknown error',
          stack: error instanceof Error ? error.stack : 'No stack'
        } : undefined
      },
      { status: 500 }
    );
  }
}

// HAPUS kode ini yang ada di luar fungsi (baris 95-100):
// if (!amount || amount < 1000) {
//   return NextResponse.json(
//     { error: 'Amount must be at least Rp 1.000' },
//     { status: 400 }
//   );
// }