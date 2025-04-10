import pandas as pd
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from prototype3.utils.path_utils import get_data_file

class QueryInput(BaseModel):
    query: str = Field(description="Pandas query string to execute")

class PandasQueryTool(BaseTool):
    name: str = "Execute Pandas Query"
    description: str = "Execute pandas query on the dataframe named 'df'"
    args_schema: type[BaseModel] = QueryInput
    df: pd.DataFrame = Field(default=None)

    model_config = {"arbitrary_types_allowed": True}
    
    def __init__(self, **data):
        super().__init__(**data)
        self.df = pd.read_csv(get_data_file('OBY01PDT01.csv'))

    def _run(self, query: str) -> str:
        try:
            result = eval(query, {'df': self.df, 'pd': pd}, {})
            return str(result)
        except Exception as e:
            return f"Query error: {str(e)}"
