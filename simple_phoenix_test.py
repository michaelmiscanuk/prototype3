"""
Minimal test script to verify Arize Phoenix cloud connectivity
"""
import os
import time
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Load environment variables from .env file
load_dotenv()

def test_cloud_connection():
    """Test direct connection to Arize Phoenix cloud"""
    # Get API key from environment
    api_key = os.getenv("PHOENIX_API_KEY", "8a4c8e6b440bc9c98e5:d67db08")
    print(f"Using API key: {api_key[:10]}...")
    
    # Create resource
    resource = Resource.create({
        "service.name": "SimplePhoenixTest",
        "service.version": "1.0.0"
    })
    
    # Set up exporter with direct connection to Arize Phoenix cloud
    exporter = OTLPSpanExporter(
        endpoint="https://app.phoenix.arize.com/v1/traces",
        headers={"api_key": api_key}
    )
    
    # Create tracer provider and processor
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
    
    # Set global tracer provider
    trace.set_tracer_provider(tracer_provider)
    
    # Get tracer
    tracer = trace.get_tracer("simple-phoenix-test")
    
    # Create test span
    print("Creating test span...")
    with tracer.start_as_current_span("simple_test_span") as span:
        span.set_attribute("test.attribute", "test_value")
        span.set_attribute("timestamp", time.time())
        
        # Add a nested span
        with tracer.start_as_current_span("nested_span") as nested:
            nested.set_attribute("nested", True)
            time.sleep(1)  # Simulate some work
    
    print("Test span created. Flushing...")
    
    # Force flush to ensure spans are exported
    tracer_provider.force_flush()
    
    print("Test completed. Check the Arize Phoenix UI for the 'SimplePhoenixTest' project.")
    print("Note: It might take a few minutes for the data to appear in the UI.")

if __name__ == "__main__":
    test_cloud_connection()
