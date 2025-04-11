"""
Phoenix Quickstart Example
Following https://docs.arize.com/phoenix/tracing/llm-traces-1/quickstart-tracing-python
"""
import os
import time
from dotenv import load_dotenv
import openai
from phoenix.otel import register

# Load environment variables
load_dotenv()

def main():
    print("Starting Phoenix Quickstart test")
    
    # 1. Set up API key
    api_key = os.getenv("PHOENIX_API_KEY", "8a4c8e6b440bc9c98e5:d67db08")
    print(f"Using Phoenix API key: {api_key[:10]}...")
    
    # Set OpenAI API key
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("OpenAI API key not found. Exiting.")
        return
        
    os.environ["OPENAI_API_KEY"] = openai_api_key
    
    # 2. Configure the Phoenix tracer exactly as in the docs
    print("Configuring Phoenix tracer...")
    tracer_provider = register(
        project_name="phoenix-quickstart",  # Simple, unique project name
        auto_instrument=True                # Enable auto-instrumentation
    )
    tracer = tracer_provider.get_tracer(__name__)
    
    print("Phoenix tracer configured.")
    
    # 3. Create decorator for function tracing
    @tracer.chain
    def generate_haiku(prompt: str) -> str:
        """Generate a haiku using OpenAI"""
        print(f"Generating haiku for prompt: {prompt}")
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": f"Write a haiku about {prompt}"}],
        )
        return response.choices[0].message.content
    
    # 4. Call the traced function
    print("Calling traced function...")
    haiku = generate_haiku("mountains")
    print(f"Generated haiku:\n{haiku}")
    
    # 5. Additional tracked operation
    with tracer.start_as_current_span("additional_operation") as span:
        span.set_attribute("custom.attribute", "test_value")
        print("Performing additional operation...")
        time.sleep(2)  # Simulate work
    
    print("\nTest completed. Check the Phoenix UI for the 'phoenix-quickstart' project.")
    print("Note: It might take a few minutes for the data to appear.")
    time.sleep(5)  # Give some time for traces to be sent

if __name__ == "__main__":
    main()
