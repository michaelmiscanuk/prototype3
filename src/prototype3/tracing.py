import os
import json
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource

def setup_tracing():
    """Set up OpenTelemetry tracing with Arize Phoenix"""
    try:
        # Get API key from environment
        api_key = os.getenv("PHOENIX_API_KEY", "8a4c8e6b440bc9c98e5:d67db08")
        
        # Configure resource with proper service attributes
        resource = Resource.create({
            "service.name": "CrewAI_Prototype3",
            "service.namespace": "prototype",
            "service.version": "1.0.0",
            "deployment.environment": "development",
            "service.instance.id": "crewai-instance-1"
        })
        
        # Only use the first part of the API key (before the colon)
        api_key_first_part = api_key.split(':')[0] if ':' in api_key else api_key
        
        # Use the standard header format expected by Arize Phoenix
        headers = {
            "api_key": api_key
        }
        
        print(f"Setting up tracing with headers: {json.dumps(headers, indent=2)}")
        
        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint="https://app.phoenix.arize.com/v1/traces",
            headers=headers
        )
        
        # Create and configure tracer provider with batch processor
        tracer_provider = TracerProvider(resource=resource)
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(tracer_provider)
        
        # Instrument libraries with explicit tracer provider
        from openinference.instrumentation.crewai import CrewAIInstrumentor
        from openinference.instrumentation.litellm import LiteLLMInstrumentor
        from openinference.instrumentation.openai import OpenAIInstrumentor
        
        CrewAIInstrumentor().instrument(skip_dep_check=True, tracer_provider=tracer_provider)
        LiteLLMInstrumentor().instrument(tracer_provider=tracer_provider)
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        
        print("✅ Tracing initialized successfully")
        print(f"✅ Using endpoint: https://app.phoenix.arize.com/v1/traces")
        print(f"✅ Using API key: {api_key[:10]}...")
        return True
    except Exception as e:
        print(f"⚠️ Tracing initialization failed: {str(e)}")
        return False
