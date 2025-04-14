module_description = r"""Parallel DataFrame Processing with Azure OpenAI

This module provides functionality to process pandas DataFrames in parallel using Azure OpenAI.

Key Features:
-------------
1. Fully Dynamic Column Handling: All DataFrame columns are passed as parameters to the prompt template.
2. Parallel Processing: Uses ThreadPoolExecutor for concurrent API calls.
3. Rate Limiting: Implements request rate limiting to respect API constraints.
4. Error Handling: Retries failed requests and captures errors.
5. Metrics Collection: Tracks processing time and success/failure rates.
6. External Template Loading: Loads prompt templates from external text files with UTF-8 support.

How it works:
------------
1. Input: Takes a DataFrame where column names match placeholders in the prompt template.
2. Configuration: Uses environment variables for Azure OpenAI setup.
3. Processing:
   - Each row is processed as a separate API call.
   - All columns are passed dynamically to the prompt template.
   - Results are collected and merged back into the DataFrame.
4. Output: Returns original DataFrame with new response column.

Usage Example:
-------------
# Create a template file with placeholders
# File: PROMPT_TEMPLATE.txt
# Content:
# You are a helpful assistant.
# Topic: {topic}
# Task: {task}
# Style: {style}
# Additional Context: {context}

# Create DataFrame with matching column names
test_df = pd.DataFrame({
    'topic': ['Quantum Computing', 'AI'],
    'task': ['Explain basics', 'Compare with humans'],
    'style': ['beginner-friendly', 'technical'],
    'context': ['high school', 'graduates']
})

# Process the DataFrame
result_df = process_dataframe_parallel(
    test_df,
    output_column='response',
    max_workers=3,
    requests_per_minute=30
)"""

#===============================================================================
# IMPORTS
#===============================================================================
import pandas as pd
import os
from dotenv import load_dotenv
import litellm
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt, wait_exponential
import time
import logging
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime
from functools import wraps
import tqdm as tqdm_module
import sys
import csv

#===============================================================================
# CUSTOM EXCEPTIONS
#===============================================================================
class ConfigurationError(Exception):
    """Raised when there's a configuration error."""
    pass

class ProcessingError(Exception):
    """Raised when processing fails."""
    pass

#===============================================================================
# CONFIGURATION AND SETUP
#===============================================================================
# Simplified logging setup
logging.basicConfig(level=logging.CRITICAL, format='%(message)s')
logger = logging.getLogger(__name__)

# Load and validate environment in one step
load_dotenv()
for var in ['AZURE_OPENAI_ENDPOINT', 'AZURE_OPENAI_API_KEY']:
    if not os.getenv(var):
        raise EnvironmentError(f"Missing required environment variable: {var}")

# Configure litellm for Azure OpenAI
litellm.drop_params = True
litellm.api_type = "azure"
litellm.api_version = "2024-05-01-preview"
litellm.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
litellm.api_key = os.getenv('AZURE_OPENAI_API_KEY')
litellm.model_alias_map = {
    "gpt-4o": "azure/gpt-4o__test1"
}

# Consolidated constants
CONFIG = {
    'MODEL': "gpt-4o",
    'TEMPERATURE': 0.7,
    'MAX_WORKERS': 5,
    'REQUESTS_PER_MINUTE': {
        'DEFAULT': 60,
        'MIN': 1,
        'MAX': 100
    }
}

# Initialize prompt template
PROMPT_TEMPLATE = ""

#===============================================================================
# HELPER FUNCTIONS
#===============================================================================
def get_script_directory() -> str:
    """Get the absolute path of the directory containing this script."""
    return os.path.dirname(os.path.abspath(__file__))

def get_absolute_path(relative_path: str) -> str:
    """Convert relative path to absolute path based on script location."""
    return os.path.join(get_script_directory(), relative_path)

def load_prompt_template_from_txt(txt_path: str = "PROMPT_TEMPLATE.txt") -> str:
    """Load prompt template from a text file.

    Args:
        txt_path (str): Path to the text file containing the prompt template.

    Returns:
        str: The prompt template loaded from the file.

    Raises:
        ConfigurationError: If the file cannot be loaded or is empty.
    """
    try:
        absolute_path = get_absolute_path(txt_path)
        with open(absolute_path, 'r', encoding='utf-8') as file:
            template = file.read()
            if not template:
                raise ConfigurationError("Template file is empty")
            return template
    except Exception as e:
        raise ConfigurationError(f"Failed to load prompt template from file: {e}")

def load_dataframe_from_csv(csv_path: str) -> pd.DataFrame:
    """Load DataFrame from CSV file, handling commas in cells.

    Args:
        csv_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame: The DataFrame loaded from the CSV file.

    Raises:
        ConfigurationError: If the file cannot be loaded or is empty.
    """
    try:
        absolute_path = get_absolute_path(csv_path)
        with open(absolute_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            data = list(reader)
        
        df = pd.DataFrame(data, columns=header)
        if df.empty:
            raise ConfigurationError("DataFrame is empty")
        return df
    except Exception as e:
        raise ConfigurationError(f"Failed to load DataFrame from CSV: {e}")

def validate_model_config():
    """Validate model configuration at startup.

    Raises:
        ValueError: If the model alias map is empty or the default model is not configured.
    """
    if not litellm.model_alias_map:
        raise ValueError("Model alias map is empty")
    if CONFIG['MODEL'] not in litellm.model_alias_map:
        raise ValueError(f"Default model {CONFIG['MODEL']} not configured in model_alias_map")

def format_system_prompt(**kwargs: Dict[str, Any]) -> str:
    """Format the prompt template using DataFrame column values.

    Args:
        **kwargs: Keyword arguments representing DataFrame column values.

    Returns:
        str: The formatted prompt.

    Raises:
        ValueError: If there is an error formatting the prompt template.
    """
    try:
        return PROMPT_TEMPLATE.format(**kwargs)
    except Exception as e:
        raise ValueError(f"Error formatting prompt template: {e}")

def get_progress_bar(iterable, total: int, desc: str):
    """Get a simple progress bar suitable for CLI.

    Args:
        iterable: The iterable to track progress on.
        total (int): The total number of items in the iterable.
        desc (str): Description of the progress.

    Returns:
        tqdm_module.tqdm: A tqdm progress bar instance.
    """
    return tqdm_module.tqdm(
        iterable, 
        total=total, 
        desc=desc,
        leave=True,  # Keep the progress bar
        ncols=100,   # Fixed width
        bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]',
        file=sys.stdout
    )

def save_to_csv(df: pd.DataFrame, filename: str):
    """Save DataFrame to CSV file.

    Args:
        df (pd.DataFrame): The DataFrame to save.
        filename (str): The filename to save the DataFrame to.
    """
    try:
        absolute_path = get_absolute_path(filename)
        df.to_csv(absolute_path, index=False)
        logger.info(f"DataFrame successfully saved to {absolute_path}")
    except Exception as e:
        logger.error(f"Error saving DataFrame to CSV: {e}")
        raise

#===============================================================================
# CONFIGURATION
#===============================================================================
@dataclass
class Config:
    """Configuration class for processing."""
    model: str
    temperature: float
    max_workers: int
    requests_per_minute: int
    
    def __post_init__(self):
        """Validate configuration parameters after initialization."""
        if not CONFIG['REQUESTS_PER_MINUTE']['MIN'] <= self.requests_per_minute <= CONFIG['REQUESTS_PER_MINUTE']['MAX']:
            raise ConfigurationError(f"Invalid requests_per_minute: {self.requests_per_minute}")
        if self.max_workers < 1:
            raise ConfigurationError(f"Invalid max_workers: {self.max_workers}")
        if not 0 <= self.temperature <= 1:
            raise ConfigurationError(f"Invalid temperature: {self.temperature}")

# Create global config with new CONFIG dictionary
CONFIG_INSTANCE = Config(
    model=CONFIG['MODEL'],
    temperature=CONFIG['TEMPERATURE'],
    max_workers=CONFIG['MAX_WORKERS'],
    requests_per_minute=CONFIG['REQUESTS_PER_MINUTE']['DEFAULT']
)

#===============================================================================
# MONITORING AND METRICS
#===============================================================================
class Metrics:
    """Simple metrics collection."""
    def __init__(self):
        """Initialize metrics."""
        self.start_time = time.time()
        self.processed_rows = 0
        self.failed_rows = 0
        self.total_processing_time = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to a dictionary.

        Returns:
            Dict[str, Any]: A dictionary containing the metrics.
        """
        return {
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "processed_rows": self.processed_rows,
            "failed_rows": self.failed_rows,
            "total_processing_time": self.total_processing_time,
            "average_time_per_row": self.total_processing_time / max(1, self.processed_rows)
        }

def log_execution_time(func):
    """Decorator to log execution time of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.2f} seconds")
            return result
        except Exception as e: 
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f} seconds: {e}")
            raise
    return wrapper

#===============================================================================
# CORE PROCESSING FUNCTIONS
#===============================================================================
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_azure_llm_response(**kwargs: Dict[str, Any]) -> str:
    """Get response from Azure OpenAI using litellm.

    Args:
        **kwargs: Keyword arguments to pass to the prompt template.

    Returns:
        str: The content of the response from Azure OpenAI.

    Raises:
        ValueError: If the model is not found in the model alias map.
        Exception: If there is an error during the API call.
    """
    if CONFIG['MODEL'] not in litellm.model_alias_map:
        raise ValueError(f"Model {CONFIG['MODEL']} not found in model_alias_map")
    try:
        formatted_prompt = format_system_prompt(**kwargs)
        request_id = f"req_{int(time.time()*1000)}"  # Unique request ID
        
        response = litellm.completion(
            model=CONFIG['MODEL'],
            messages=[{"role": "user", "content": formatted_prompt}],
            temperature=CONFIG['TEMPERATURE'],
            metadata={"request_id": request_id}
        )
        return response.choices[0].message.content
    except Exception as e:
        # Silent error handling, just re-raise
        raise

def process_dataframe_parallel(
    df: pd.DataFrame, 
    output_column: str, 
    max_workers: int = CONFIG_INSTANCE.max_workers, 
    requests_per_minute: int = CONFIG_INSTANCE.requests_per_minute
) -> pd.DataFrame:
    """Process a DataFrame in parallel using Azure OpenAI.

    Args:
        df (pd.DataFrame): The DataFrame to process.
        output_column (str): The name of the column to store the results in.
        max_workers (int): The maximum number of workers to use for parallel processing.
        requests_per_minute (int): The maximum number of requests to make per minute.

    Returns:
        pd.DataFrame: The DataFrame with the results added to the specified output column.
    """
    metrics = Metrics()
    start_time = time.time()
    
    try:
        results = [None] * len(df)
        delay_between_requests = 60 / requests_per_minute
        
        def process_row(index: int, row: pd.Series):
            """Process a single row of the DataFrame.

            Args:
                index (int): The index of the row.
                row (pd.Series): The row to process.

            Returns:
                Tuple[int, Optional[str]]: The index of the row and the result, or None if an error occurred.
            """
            time.sleep(index * delay_between_requests)
            try:
                row_dict = row.to_dict()
                if output_column in row_dict:
                    del row_dict[output_column]
                return index, get_azure_llm_response(**row_dict)
            except Exception:
                return index, None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(process_row, index, row): index
                for index, row in df.iterrows()
            }
            
            with get_progress_bar(total=len(df), desc="Processing", iterable=as_completed(futures)) as pbar:
                for future in pbar:
                    index, result = future.result()
                    results[index] = result
                    metrics.processed_rows += 1
                    if result is None:
                        metrics.failed_rows += 1
        
        df[output_column] = results
        end_time = time.time()
        metrics.total_processing_time = end_time - start_time
        
        print(f"\nProcessing completed in {metrics.total_processing_time:.2f} seconds:")
        print(f"- Rows processed: {metrics.processed_rows}")
        print(f"- Rows failed: {metrics.failed_rows}")
        print(f"- Average time per row: {metrics.total_processing_time/max(1,metrics.processed_rows):.2f} seconds")
        
        return df
        
    except Exception as e:
        print(f"\nError: {e}")
        raise

#===============================================================================
# EXECUTION BLOCK
#===============================================================================
if __name__ == "__main__":
    try:
        validate_model_config()
        
        # Load prompt template from CSV
        PROMPT_TEMPLATE = load_prompt_template_from_txt()
        print(f"Loaded prompt template: {PROMPT_TEMPLATE[:1000]}...")
        
        # Load DataFrame from CSV
        input_csv_path = "input.csv"
        test_df = load_dataframe_from_csv(input_csv_path)
        
        print("Starting parallel DataFrame processing...")
        processed_df = process_dataframe_parallel(
            test_df,
            output_column="ai_response",
            max_workers=3,
            requests_per_minute=30
        )
        
        # Save results to CSV
        csv_path = "output.csv"
        save_to_csv(processed_df, csv_path)
        
        print("\nResults saved to:", get_absolute_path(csv_path))
        
    except Exception as e:
        print(f"Application error: {e}")
        raise