import duckdb
from config.layers import layer_name
from config.categories import get_available_categories
from config.modes import get_available_modes
from utils.logger import get_logger

con = duckdb.connect()


def load_layer(dataset: str, parquet_path: str):
    logger = get_logger(__name__, dataset)

    print(f"Loading layer {parquet_path}")
    query = f"""
        SELECT h3, value
        FROM read_parquet('{parquet_path}')
        WHERE value IS NOT NULL AND value > 0
    """
    try:
        return con.execute(query).fetchall()
    except Exception as e:
        logger.error(f"Error occurred at while loading layer: {e}")
        raise ValueError(f"Error occurred at while loading layer: {e}") from e