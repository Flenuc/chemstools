import React, { Component, ReactNode } from 'react';
import { Result, Button, Typography, Collapse } from 'antd';
import { ExclamationCircleOutlined, BugOutlined, ReloadOutlined } from '@ant-design/icons';

const { Paragraph, Text } = Typography;
const { Panel } = Collapse;

interface Props {
    children: ReactNode;
    fallback?: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
    errorInfo: React.ErrorInfo | null;
}

class ErrorBoundary extends Component<Props, State> {
    constructor(props: Props) {
        super(props);
        this.state = {
            hasError: false,
            error: null,
            errorInfo: null,
        };
    }

    static getDerivedStateFromError(error: Error): State {
        // Actualizar el estado para que el próximo renderizado muestre la UI de error
        return { hasError: true, error, errorInfo: null };
    }

    componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
        // Log del error a un servicio de reporte de errores
        console.error('Error capturado por ErrorBoundary:', error, errorInfo);
        
        // Guardar detalles del error en el estado
        this.setState({
            error,
            errorInfo,
        });

        // Aquí podrías enviar el error a un servicio externo como Sentry
        // logErrorToService(error, errorInfo);
    }

    handleReset = () => {
        this.setState({ hasError: false, error: null, errorInfo: null });
        // Opcionalmente, recargar la página
        // window.location.reload();
    };

    render() {
        if (this.state.hasError) {
            if (this.props.fallback) {
                return <>{this.props.fallback}</>;
            }

            const isDevelopment = process.env.NODE_ENV === 'development';

            return (
                <Result
                    status="error"
                    icon={<BugOutlined style={{ color: '#ff4d4f' }} />}
                    title="¡Ups! Algo salió mal"
                    subTitle="Ha ocurrido un error inesperado. Por favor, intenta recargar la página o contacta al soporte si el problema persiste."
                    extra={[
                        <Button 
                            type="primary" 
                            key="retry" 
                            onClick={this.handleReset}
                            icon={<ReloadOutlined />}
                        >
                            Intentar de Nuevo
                        </Button>,
                        <Button 
                            key="home" 
                            onClick={() => window.location.href = '/'}
                        >
                            Ir al Inicio
                        </Button>,
                    ]}
                >
                    {isDevelopment && this.state.error && (
                        <Collapse className="mt-4">
                            <Panel 
                                header={
                                    <span>
                                        <ExclamationCircleOutlined className="mr-2" />
                                        Detalles del Error (Solo en desarrollo)
                                    </span>
                                } 
                                key="1"
                            >
                                <Paragraph>
                                    <Text strong>Mensaje de Error:</Text>
                                </Paragraph>
                                <Paragraph code className="error-message">
                                    {this.state.error.message}
                                </Paragraph>
                                
                                {this.state.errorInfo && (
                                    <>
                                        <Paragraph>
                                            <Text strong>Stack Trace:</Text>
                                        </Paragraph>
                                        <Paragraph>
                                            <pre className="error-stack">
                                                {this.state.error.stack}
                                            </pre>
                                        </Paragraph>
                                        <Paragraph>
                                            <Text strong>Component Stack:</Text>
                                        </Paragraph>
                                        <Paragraph>
                                            <pre className="error-component-stack">
                                                {this.state.errorInfo.componentStack}
                                            </pre>
                                        </Paragraph>
                                    </>
                                )}
                            </Panel>
                        </Collapse>
                    )}
                </Result>
            );
        }

        return this.props.children;
    }
}

export default ErrorBoundary;
