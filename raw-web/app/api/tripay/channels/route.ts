import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const response = await fetch('https://tripay.co.id/api-sandbox/merchant/payment-channel', {
      headers: {
        'Authorization': `Bearer DEV-9Pq3AYHMRkfQHrIGXFsVTuKO17piU9VAQOoy5Ym2`
      }
    });
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch channels' }, { status: 500 });
  }
}