import pandas as pd
import yaml
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any
from prototype3.utils.path_utils import get_data_file
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.core import PromptTemplate

class QueryInput(BaseModel):
    """Schema for the query input"""
    query: str = Field(description="Natural language question about the data")
    schema: dict = Field(description="Metadata about the dataset structure")

class PandasQueryTool(BaseTool):
    """Tool for querying data using natural language.
    Uses LlamaIndex's PandasQueryEngine for converting natural language to pandas operations.
    """
    
    name: str = "Query Data"
    description: str = """
        Ask questions about data in natural language.
        The tool will convert your question into appropriate pandas operations.
    """
    
    args_schema: type[BaseModel] = QueryInput
    df: pd.DataFrame = Field(default=None)
    schema: dict = Field(default=None)
    _query_engine: Any = None

    model_config = {
        "arbitrary_types_allowed": True
    }
    
    def __init__(self, **data):
        """Initialize with data and setup LlamaIndex query engine with custom prompt"""
        super().__init__(**data)
        csv_path = get_data_file('OBY01PDT01.csv')
        self.df = pd.read_csv(csv_path)
        
        # Create generic prompt template with dataset-specific rules
        pandas_prompt = PromptTemplate("""\
You are working with a dataframe in Python. The dataframe 'df' has the following structure:

Columns and their descriptions:
{schema_str}

Important data rules:
{rules_str}

This is the result of df.head():
{df_str}

Follow these instructions:
1. Convert the natural language query to executable Python code using Pandas
2. Handle any special characters in column names or values
3. Return only the final expression that can be evaluated
4. Consider data rules when aggregating or filtering

Query: {query_str}

Expression:""")

        # Initialize query engine with custom prompt
        self._query_engine = PandasQueryEngine(
            df=self.df,
            verbose=True,
            synthesize_response=True,
            prompt_template=pandas_prompt,
            metadata={
                "schema_str": self._format_schema(data.get("schema", {})),
                "rules_str": self._extract_rules(data.get("schema", {}))
            }
        )

    def _format_schema(self, schema: dict) -> str:
        """Format schema into human-readable description"""
        if not schema:
            return "\n".join(f"- {col}: {self.df[col].dtype}" 
                           for col in self.df.columns)
        
        # If schema provided, use it to create detailed description
        descriptions = []
        for dim_name, dim_info in schema.get("dimensions", {}).items():
            dim_type = dim_info.get("type", "unknown")
            values = dim_info.get("values", [])
            desc = f"- {dim_name}: {dim_type} dimension with {len(values)} unique values"
            if len(values) < 10:  # Only show values if there aren't too many
                desc += f"\n  Values: {', '.join(str(v) for v in values)}"
            descriptions.append(desc)
        
        return "\n".join(descriptions)

    def _extract_rules(self, schema: dict) -> str:
        """Extract data rules from schema"""
        if not schema:
            return "No specific data rules provided"
        
        rules = []
        # Extract rules based on schema structure
        for dim_name, dim_info in schema.get("dimensions", {}).items():
            if dim_info.get("is_temporal"):
                rules.append(f"- {dim_name} contains temporal information")
            if dim_info.get("is_geographical"):
                rules.append(f"- {dim_name} contains geographical information")
        
        return "\n".join(rules) if rules else "No specific data rules provided"

    def _run(self, query: str) -> str:
        """Execute natural language query using LlamaIndex
        
        Args:
            query: Natural language question about the data
            
        Returns:
            Response in YAML format
        """
        try:
            # Execute query through LlamaIndex
            response = self._query_engine.query(query)
            print(f"[DEBUG] Generated pandas code: {response.metadata.get('pandas_instruction_str', 'No code generated')}")
            
            # Extract pandas result
            pandas_result = response.metadata.get("pandas_output")
            
            # Handle different result types
            if pandas_result is not None:
                if isinstance(pandas_result, (pd.DataFrame, pd.Series)):
                    result_dict = (pandas_result.to_dict('records') 
                                 if isinstance(pandas_result, pd.DataFrame)
                                 else pandas_result.to_dict())
                    return yaml.dump(result_dict, allow_unicode=True)
                return str(pandas_result)
            
            return str(response)
            
        except Exception as e:
            return f"Query error: {str(e)}"
