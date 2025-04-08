import pandas as pd
import yaml
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Any
from prototype3.utils.path_utils import get_data_file

class QueryInput(BaseModel):
    query: str = Field(description="Pandas query string to execute")

class PandasQueryTool(BaseTool):
    name: str = "Execute Pandas Query"
    description: str = """Execute pandas query on the dataframe named 'df'.
        The dataframe contains Czech population data.
        Examples:
        - Filtering: df[df['Column'] == 'Value']
        - Aggregating: df.groupby('Column')['value'].sum()
        - Complex example: df[
            (df['Kumulace čtvrtletí'] == 'Q1-Q3 2024') & 
            (df['ČR, kraje'].isin(['Plzeňský kraj', 'Hlavní město Praha']))
          ]['value'].sum()
        """
    args_schema: type[BaseModel] = QueryInput
    df: pd.DataFrame = Field(default=None)

    model_config = {
        "arbitrary_types_allowed": True
    }
    
    def __init__(self, **data):
        super().__init__(**data)
        csv_path = get_data_file('OBY01PDT01.csv')
        self.df = pd.read_csv(csv_path)

    def _run(self, query: str) -> str:
        try:
            # Create a local scope with df variable
            local_scope = {'df': self.df}
            
            print(f"[DEBUG] Executing query: {query}")
            result = eval(query, globals(), local_scope)
            
            if isinstance(result, (int, float)):
                return str(result)
            
            if isinstance(result, pd.Series):
                result = result.to_frame() if not result.empty else pd.DataFrame()
            
            return yaml.dump(
                result.to_dict('records') if isinstance(result, pd.DataFrame) 
                else {'result': result}, 
                allow_unicode=True
            )
            
        except Exception as e:
            return f"Query error: {str(e)}\nPlease use 'df' to reference the dataframe."
