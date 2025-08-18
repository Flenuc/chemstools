import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const diagnostics = {
    timestamp: new Date().toISOString(),
    errors_fixed: {
      message_warning: {
        status: 'FIXED',
        solution: 'Created useMessage hook to handle Ant Design message context properly',
        file: 'hooks/useMessage.tsx'
      },
      telemetry_error: {
        status: 'FIXED', 
        solution: 'Removed redundant JSON.stringify in telemetryService.ts',
        file: 'services/telemetryService.ts'
      },
      isLoading_prop: {
        status: 'FIXED',
        solution: 'Added isLoading to ButtonProps interface and mapped to loading prop',
        file: 'components/ui/index.tsx'
      },
      kekule_warning: {
        status: 'INFO',
        note: 'This is just a fallback warning, not an error. Canvas renderer works fine.',
        file: 'components/features/LewisStructureGenerator.tsx'
      }
    },
    recommendations: [
      'Use showMessage.success/error/info/warning instead of message.* directly',
      'Always use the Button component from @/components/ui',
      'The telemetry endpoint may need to be created in backend if not exists',
      'Consider loading Kekule.js from local assets instead of CDN for reliability'
    ],
    test_endpoints: {
      register: '/api/auth/register/',
      login: '/api/auth/token/',
      telemetry: '/api/telemetry/log/'
    }
  };
  
  return NextResponse.json(diagnostics, { status: 200 });
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Test telemetry endpoint
    const telemetryTest = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000'}/api/telemetry/log/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        event_name: 'test_diagnostic',
        details: { test: true },
        session_id: 'test-session'
      })
    }).catch(err => ({ error: err.message }));
    
    return NextResponse.json({
      message: 'Diagnostic test completed',
      telemetry_test: telemetryTest.ok ? 'SUCCESS' : 'FAILED',
      received_data: body
    });
  } catch (error: any) {
    return NextResponse.json({
      error: 'Diagnostic test failed',
      details: error.message
    }, { status: 500 });
  }
}
