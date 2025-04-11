"""
Integration module for Arize Phoenix with CrewAI - updated version
"""
import os
import time
import uuid
import atexit
import threading
import phoenix as px
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from openinference.instrumentation.crewai import CrewAIInstrumentor
from openinference.instrumentation.litellm import LiteLLMInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor

# Global session and trace objects
_tracer = None
_phoenix_app = None
_app_thread = None

def initialize_phoenix():
    """Initialize Phoenix with CrewAI integration"""
    global _tracer, _phoenix_app, _app_thread
    
    try:
        # Ensure API key is set
        api_key = os.getenv("PHOENIX_API_KEY", None)
        if not api_key:
            print("⚠️ Phoenix API key not set. Tracing will not be enabled.")
            return None
            
        print(f"Initializing Phoenix with API key: {api_key[:10]}...")
        
        # Generate a unique session ID
        session_id = f"crewai-{uuid.uuid4().hex[:8]}"
        
        # Configure environment for Phoenix
        os.environ["PHOENIX_API_KEY"] = api_key
        # Temporarily delete the collector endpoint to avoid conflicts
        if "PHOENIX_COLLECTOR_ENDPOINT" in os.environ:
            collector_endpoint = os.environ["PHOENIX_COLLECTOR_ENDPOINT"]
            del os.environ["PHOENIX_COLLECTOR_ENDPOINT"]
        else:
            collector_endpoint = None
            
        # Start Phoenix in a separate thread to avoid blocking
        def start_phoenix():
            try:
                px.launch_app()
            except Exception as e:
                print(f"Phoenix thread error: {e}")
                
        _app_thread = threading.Thread(target=start_phoenix, daemon=True)
        _app_thread.start()
        time.sleep(2)  # Give Phoenix time to start up
        
        # Restore the collector endpoint if it was set
        if collector_endpoint:
            os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = collector_endpoint
            
        # Initialize OpenTelemetry trace provider
        trace_provider = trace.get_tracer_provider()
        
        # Initialize tracer
        _tracer = trace.get_tracer("crewai-phoenix", "1.0.0")
        
        # Instrument libraries
        CrewAIInstrumentor().instrument(skip_dep_check=True)
        LiteLLMInstrumentor().instrument() 
        OpenAIInstrumentor().instrument()
        
        # Register cleanup
        atexit.register(cleanup)
        
        print("✅ Phoenix initialized with session ID:", session_id)
        print("✅ Phoenix trace provider initialized")
        print("✅ Phoenix is now collecting traces to:", 
              os.environ.get("PHOENIX_COLLECTOR_ENDPOINT", "local UI"))
        
        return True
    except Exception as e:
        print(f"⚠️ Phoenix initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def cleanup():
    """Clean up Phoenix resources"""
    global _app_thread
    
    # No need to explicitly close anything
    # Phoenix will clean up its own resources
    print("Phoenix resources cleaned up")

def track_operation(name, attributes=None):
    """Track an operation in Phoenix using OpenTelemetry"""
    global _tracer
    if not _tracer:
        return None
        
    # Create a span using the tracer
    return _tracer.start_as_current_span(name, attributes=attributes)
