"""
Test script to verify Phoenix connectivity
"""
import os
import time
import json
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

# Load environment variables
load_dotenv()

def test_phoenix_connection():
    """Simple test to verify Phoenix connectivity"""
    # Get API key
    api_key = os.getenv("PHOENIX_API_KEY", "8a4c8e6b440bc9c98e5:d67db08")
    print(f"Testing Phoenix connection with API key: {api_key[:10]}...")
    
    # Set up resource - add more attributes for better identification
    resource = Resource.create({
        "service.name": "CrewAI_Test",
        "service.namespace": "prototype",
        "service.version": "1.0.0",
        "deployment.environment": "development",
        "service.instance.id": "test-instance-1"
    })
    
    # Try using just the first part of the API key (before the colon)
    api_key_first_part = api_key.split(':')[0] if ':' in api_key else api_key
    
    # Try all possible header combinations
    headers = {
        "api_key": api_key,  # Standard with underscore
    }
    
    print(f"Attempting with headers: {json.dumps(headers, indent=2)}")
    
    # Set up exporter with explicit content type
    otlp_exporter = OTLPSpanExporter(
        endpoint="https://app.phoenix.arize.com/v1/traces",
        headers=headers,
    )
    
    # Set up tracer with batch processor
    tracer_provider = TracerProvider(resource=resource)
    span_processor = BatchSpanProcessor(otlp_exporter)
    tracer_provider.add_span_processor(span_processor)
    trace.set_tracer_provider(tracer_provider)
    
    # Create tracer
    tracer = trace.get_tracer("phoenix-test")
    
    # Create and export a test span with more attributes
    with tracer.start_as_current_span("phoenix_test_span") as span:
        span.set_attribute("test.attribute", "test_value")
        span.set_attribute("test.number", 42)
        span.set_attribute("test.boolean", True)
        span.add_event("test_event", {"event.detail": "This is a test"})
        print("Created test span")
        time.sleep(1)  # Give some time for the span to be processed
    
    # Force the span processor to export any batched spans
    span_processor.force_flush()
    
    print("Test span completed and exported")
    print("Check the Phoenix UI for the 'CrewAI_Test' project in a few minutes")
    
    # Try alternate header format if the first attempt failed
    print("\nTrying alternate header format...")
    
    headers_alt = {
        "api-key": api_key,  # With hyphen
    }
    
    print(f"Attempting with headers: {json.dumps(headers_alt, indent=2)}")
    
    # Set up alternate exporter
    otlp_alt_exporter = OTLPSpanExporter(
        endpoint="https://app.phoenix.arize.com/v1/traces",
        headers=headers_alt,
    )
    
    # Set up alternate tracer
    alt_tracer_provider = TracerProvider(resource=resource)
    alt_span_processor = BatchSpanProcessor(otlp_alt_exporter)
    alt_tracer_provider.add_span_processor(alt_span_processor)
    
    # Create alternate tracer
    alt_tracer = trace.get_tracer_provider().get_tracer("phoenix-test-alt")
    
    # Create and export another test span
    with alt_tracer.start_as_current_span("phoenix_test_span_alt") as span:
        span.set_attribute("test.attempt", "alternate")
        span.add_event("test_event_alt", {"event.detail": "This is an alternate test"})
        print("Created alternate test span")
        time.sleep(1)
    
    # Force flush
    alt_span_processor.force_flush()
    
    print("Alternate test span completed and exported")
    print("Check the Phoenix UI for the 'CrewAI_Test' project in a few minutes")

if __name__ == "__main__":
    test_phoenix_connection()
