import pandas as pd
from crewai.tools import BaseTool
from typing import Dict, Optional, Any, Type, List
from pydantic import BaseModel, Field

class DataFrameInput(BaseModel):
    """Input model for DataFrame operations"""
    file_path: str = Field(description="Path to the CSV file")
    
class FilterInput(BaseModel):
    """Input model for filter operations"""
    conditions: Dict[str, str] = Field(description="Dictionary of column:value pairs to filter by")
    data: Dict[str, Any] = Field(description="DataFrame data as dictionary")

class ValueInput(BaseModel):
    """Input model for value extraction"""
    column: str = Field(description="Column name to get value from")
    data: Dict[str, Any] = Field(description="DataFrame data as dictionary")

class ReadCSVTool(BaseTool):
    name: str = "Read CSV Data"
    description: str = "Read and process CSV data file"
    args_schema: Type[BaseModel] = DataFrameInput

    def _run(self, file_path: str) -> Dict[str, Any]:
        df = pd.read_csv(file_path)
        return df.to_dict()

class FilterDataTool(BaseTool):
    name: str = "Filter Data"
    description: str = "Filter data based on column conditions"
    args_schema: Type[BaseModel] = FilterInput

    def _run(self, conditions: Dict[str, str], data: Dict[str, Any]) -> Dict[str, Any]:
        df = pd.DataFrame.from_dict(data)
        query = ' & '.join([f"{k} == '{v}'" for k, v in conditions.items()])
        filtered_df = df.query(query)
        return filtered_df.to_dict()

class GetValueTool(BaseTool):
    name: str = "Get Value"
    description: str = "Get specific value from filtered data"
    args_schema: Type[BaseModel] = ValueInput

    def _run(self, column: str, data: Dict[str, Any]) -> Optional[Any]:
        df = pd.DataFrame.from_dict(data)
        return df[column].iloc[0] if not df.empty else None

class DataTools:
    read_csv_data = ReadCSVTool()
    filter_data = FilterDataTool()
    get_value = GetValueTool()

    @staticmethod
    def create_query_tool() -> BaseTool:
        def query_data(df: pd.DataFrame, query_str: str) -> pd.DataFrame:
            """
            Execute a pandas query string on the dataframe and return result
            Limited to 1 row for validation.
            """
            try:
                result = df.query(query_str).head(1)
                return result
            except Exception as e:
                return f"Query failed: {str(e)}"
                
        return BaseTool(
            name="query_data",
            description="Execute pandas query on dataframe",
            func=query_data
        )
