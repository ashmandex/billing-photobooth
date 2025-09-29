import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { kamucantikbanged } = body;

    // Validate required fields
    if (!kamucantikbanged) {
      return NextResponse.json(
        {
          success: false,
          message: "Terjadi kesalahan server",
          error_code: "INTERNAL_SERVER_ERROR",
          details: "validation.required"
        },
        { status: 500 }
      );
    }

    // Use explicit haimanis value
    const haimanis = 'LobanGPrMO928UhhhLewaTTT';

    // Make request to external API
    const response = await fetch('https://card.snapbooth.click/api/nfc-verify', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        haimanis,
        kamucantikbanged
      })
    });

    const result = await response.json();
    
    // Log API response for debugging
    console.log('Voucher API Response:', {
      status: response.status,
      data: result,
      request: { haimanis, kamucantikbanged }
    });

    // Return the response with appropriate status code
    return NextResponse.json(result, { status: response.status });

  } catch (error) {
    console.error('Voucher verification error:', error);
    return NextResponse.json(
      {
        success: false,
        message: "Terjadi kesalahan server",
        error_code: "INTERNAL_SERVER_ERROR",
        details: "Network or server error"
      },
      { status: 500 }
    );
  }
}