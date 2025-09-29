import { NextRequest, NextResponse } from 'next/server';
import { checkTransactionStatus, mapTripayStatus } from '../../../lib/tripay';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const reference = searchParams.get('reference');

    if (!reference) {
      return NextResponse.json(
        { error: 'Reference is required' },
        { status: 400 }
      );
    }

    console.log('Checking Tripay transaction status for reference:', reference);

    // Check transaction status with Tripay
    const statusResponse = await checkTransactionStatus(reference);

    if (!statusResponse.success || !statusResponse.data) {
      throw new Error(statusResponse.message || 'Failed to get transaction status');
    }

    const { data } = statusResponse;
    const mappedStatus = mapTripayStatus(data.status);

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
        status: data.status,
        mapped_status: mappedStatus,
        paid_at: data.paid_at
      }
    });

  } catch (error) {
    console.error('Error checking Tripay transaction status:', error);
    return NextResponse.json(
      { 
        error: 'Failed to check transaction status',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}