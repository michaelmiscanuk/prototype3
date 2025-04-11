"""
Test script to verify Phoenix connectivity using OpenTelemetry
"""
import os
import time
import uuid
from dotenv import load_dotenv
import phoenix as px
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource

# Load environment variables
load_dotenv()

def test_phoenix_connection():
    """Test Phoenix connectivity using OpenTelemetry"""
    # Get API key
    api_key = os.getenv("PHOENIX_API_KEY", "8a4c8e6b440bc9c98e5:d67db08")
    print(f"Testing Phoenix connection with API key: {api_key[:10]}...")
    
    # Set API key environment variable
    os.environ["PHOENIX_API_KEY"] = api_key
    
    # Generate unique test ID
    test_id = f"test-{uuid.uuid4().hex[:8]}"
    print(f"Using test ID: {test_id}")
    
    # Temporarily remove collector endpoint to keep data local
    if "PHOENIX_COLLECTOR_ENDPOINT" in os.environ:
        collector_endpoint = os.environ.pop("PHOENIX_COLLECTOR_ENDPOINT")
    else:
        collector_endpoint = None
    
    try:
        # Initialize Phoenix with minimal settings
        print("Starting Phoenix...")
        session = px.launch_app()
        print("Phoenix started successfully")
        
        # Get a tracer
        tracer = trace.get_tracer("phoenix-test", "1.0.0")
        
        # Create spans
        print("Creating test spans...")
        with tracer.start_as_current_span("test_root_operation") as root:
            root.set_attribute("test.id", test_id)
            root.set_attribute("test.timestamp", str(time.time()))
            
            # Create nested span
            with tracer.start_as_current_span("test_sub_operation") as sub:
                sub.set_attribute("sub.operation", True)
                time.sleep(1)
                
                # Create another level
                with tracer.start_as_current_span("test_nested_operation") as nested:
                    nested.set_attribute("nested.level", 3)
                    nested.add_event("nested_event", {"message": "This is a nested event"})
                    time.sleep(1)
        
        print("Test spans created")
        print("Check the Phoenix UI for traces at http://localhost:6006")
        
        # Wait for spans to be processed
        print("Waiting for spans to be processed...")
        time.sleep(5)
        
        # Restore the collector endpoint
        if collector_endpoint:
            os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = collector_endpoint
        
        return True
    except Exception as e:
        print(f"Error testing Phoenix: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_phoenix_connection()
