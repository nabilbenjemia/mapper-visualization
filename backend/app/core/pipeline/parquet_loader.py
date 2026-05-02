import duckdb
from config.layers import layer_name
from config.categories import get_available_categories
from config.modes import get_available_modes
from utils.logger import get_logger

logger = get_logger(__name__)
con = duckdb.connect()

def load_layer(parquet_path: str, category: str, mode: str):
    if category not in get_available_categories():
        raise ValueError(f"Category {category} not found in dataset")
    if mode not in get_available_modes():
        raise ValueError(f"Mode {mode} not found in dataset")
    
    column = layer_name(category, mode)
    query = f"""
        SELECT h3, {column}
        FROM read_parquet('{parquet_path}')
    """
    try:
        return con.execute(query).fetchall()
    except Exception as e:
        logger.error(f"Error occurred at while loading layer: {e}")
        raise ValueError(f"Column {column} not found in dataset") from e