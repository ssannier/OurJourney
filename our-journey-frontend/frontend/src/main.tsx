import { createRoot } from "react-dom/client";
import App from "./app/App.tsx";
import "./styles/index.css";
import { configureAmplify } from "./config/amplify-config";

/**
 * Application Entry Point
 * 
 * This file initializes the React application and configures AWS Amplify
 * with Cognito authentication settings before rendering the app.
 * 
 * Flow:
 * 1. Configure Amplify with Cognito settings from S3
 * 2. Render the React application
 * 3. Handle any initialization errors gracefully
 */

// Get root element
const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element not found. Check your index.html file.");
}

// Create React root
const root = createRoot(rootElement);

/**
 * Initialize and render application
 */
async function initializeApp() {
  try {
    console.log("Initializing application...");
    
    // Configure AWS Amplify with Cognito settings
    // This fetches cognito-config.json from the deployed app
    await configureAmplify();
    
    console.log("Amplify configured successfully, rendering app...");
    
    // Render the application
    root.render(<App />);
    
  } catch (error) {
    console.error("Failed to initialize application:", error);
    
    // Render error UI
    root.render(
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        padding: '40px',
        textAlign: 'center',
        backgroundColor: '#f8f9fa',
        fontFamily: 'system-ui, -apple-system, sans-serif'
      }}>
        <div style={{
          maxWidth: '600px',
          backgroundColor: 'white',
          padding: '40px',
          borderRadius: '8px',
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
          
          <h1 style={{
            fontSize: '24px',
            fontWeight: 'bold',
            color: '#dc3545',
            marginBottom: '16px'
          }}>
            Application Initialization Failed
          </h1>
          
          <p style={{
            fontSize: '16px',
            color: '#6c757d',
            marginBottom: '24px',
            lineHeight: '1.6'
          }}>
            We encountered an error while loading the authentication configuration.
            This usually happens when the app is not properly deployed or the
            configuration file is missing.
          </p>
          
          <div style={{
            backgroundColor: '#f8f9fa',
            padding: '16px',
            borderRadius: '4px',
            marginBottom: '24px',
            textAlign: 'left'
          }}>
            <p style={{
              fontSize: '14px',
              color: '#495057',
              margin: 0,
              fontFamily: 'monospace'
            }}>
              <strong>Error:</strong> {error instanceof Error ? error.message : 'Unknown error'}
            </p>
          </div>
          
          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button
              onClick={() => window.location.reload()}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '500',
                color: 'white',
                backgroundColor: '#007bff',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'background-color 0.2s'
              }}
              onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#0056b3'}
              onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#007bff'}
            >
              Retry
            </button>
            
            <button
              onClick={() => console.log('Error details:', error)}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '500',
                color: '#6c757d',
                backgroundColor: 'white',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                cursor: 'pointer'
              }}
            >
              View Console
            </button>
          </div>
          
          <p style={{
            fontSize: '14px',
            color: '#adb5bd',
            marginTop: '24px',
            marginBottom: 0
          }}>
            If this problem persists, please contact support.
          </p>
        </div>
      </div>
    );
  }
}

// Start application initialization
initializeApp();