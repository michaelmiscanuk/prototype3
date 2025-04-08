import pandas as pd
import yaml
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any
from prototype3.utils.path_utils import get_data_file
from langchain_experimental.tools.python.tool import PythonAstREPLTool

class QueryInput(BaseModel):
    """Schema for the query input"""
    query: str = Field(description="Pandas query string to execute")

class PandasQueryTool(BaseTool):
    """Tool for executing pandas queries on Czech population data.
    
    Uses Langchain's PythonAstREPLTool for secure query execution.
    The tool provides access to a dataframe containing Czech population statistics.
    """
    
    name: str = "Execute Pandas Query"
    description: str = """
        Execute pandas queries on Czech population data with columns:
        - 'Kumulace čtvrtletí': Time period (e.g., 'Q1-Q3 2024')
        - 'ČR, kraje': Region names
        - 'Ukazatel': Metric types (population indicators)
        - 'value': Numeric values

        Example queries:
        1. Basic filtering:
           df[df['ČR, kraje'] == 'Plzeňský kraj']
        
        2. Value aggregation:
           df[df['Ukazatel'].str.contains('ženy')]['value'].sum()
        
        3. Complex query:
           df[
             (df['Kumulace čtvrtletí'] == 'Q1-Q3 2024') & 
             (df['ČR, kraje'].isin(['Plzeňský kraj', 'Hlavní město Praha'])) &
             (df['Ukazatel'].str.contains('ženy'))
           ]['value'].sum()
    """
    
    # Model configuration
    args_schema: type[BaseModel] = QueryInput
    df: pd.DataFrame = Field(default=None, description="Population data DataFrame")
    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, **data):
        """Initialize the tool with data from CSV and setup Langchain REPL"""
        super().__init__(**data)
        # Load population data
        csv_path = get_data_file('OBY01PDT01.csv')
        self.df = pd.read_csv(csv_path)
        # Setup secure Python REPL with access to pandas and our dataframe
        self._langchain_tool = PythonAstREPLTool(locals={"df": self.df, "pd": pd})

    def _run(self, query: str) -> str:
        """Execute a pandas query and return results in YAML format
        
        Args:
            query: A pandas query string to execute
            
        Returns:
            YAML formatted string containing query results
            
        Raises:
            Returns error message if query execution fails
        """
        try:
            # Execute query using Langchain's secure REPL
            result = self._langchain_tool.run(query)
            
            # Format results based on type
            if isinstance(result, (pd.DataFrame, pd.Series)):
                return yaml.dump(
                    result.to_dict('records') if isinstance(result, pd.DataFrame)
                    else result.to_dict(),
                    allow_unicode=True
                )
            return str(result)
            
        except Exception as e:
            return f"Query error: {str(e)}"
