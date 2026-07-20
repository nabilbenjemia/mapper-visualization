import duckdb
import time
import os

def aggregate_h3(dataset: str, res: int):
    base_url = f"/mnt/data/results/{dataset}"
    input_parquet = base_url + f"/cells_res10.parquet"
    t0 = time.time()

    con = duckdb.connect()

    try:
        print("Loading H3 extension...")
        con.execute("INSTALL h3 FROM community;")
        con.execute("LOAD h3;")

        print("Reading schema...")

        # get column names
        col_names = con.execute(f"""
        DESCRIBE SELECT *
        FROM read_parquet('{input_parquet}')
        """).fetchdf()["column_name"].tolist()

        # build aggregation (exclude H3 column)
        metric_cols = [c for c in col_names if c != "h3"]

        print(f"Aggregating {len(metric_cols)} metric columns...")

        agg_expr = ", ".join([f'AVG("{c}") AS "{c}"' for c in metric_cols])

        print("Running aggregation...")

        output_parquet = f"{base_url}/cells_res{res}.parquet"
        
        con.execute(f"""
        COPY (
            SELECT
                h3_cell_to_parent(h3, {res}) AS h3,
                {agg_expr}
            FROM read_parquet('{input_parquet}')
            GROUP BY 1
        )
        TO '{output_parquet}'
        (FORMAT PARQUET)
        """)

    
        print("\nPreview:")

        print(
            con.execute(f"""
            SELECT *
            FROM read_parquet('{output_parquet}')
            LIMIT 10
            """).fetchdf()
        )

        print("\nStats:")

        print(
            con.execute(f"""
            SELECT
                COUNT(*) AS rows,
                COUNT(*) * 1.0 AS rows_float
            FROM read_parquet('{output_parquet}')
            """).fetchdf()
        )

        print(f"\nFinished in {time.time() - t0:.2f} seconds")
        
    except Exception as e:
        print(f"Aggregation failed: {e}")
        raise
    finally:
        con.close()
    
    
def valid_parquet(path):
    return os.path.exists(path) and os.path.getsize(path) > 0


def create_resolution_parquets(dataset: str):
    base_url = f"/mnt/data/results/{dataset}"

    cells = os.path.join(base_url, "cells.parquet")
    cells_res10 = os.path.join(base_url, "cells_res10.parquet")

    if not os.path.exists(cells_res10):
        os.rename(cells, cells_res10)

    if not valid_parquet(os.path.join(base_url, "cells_res8.parquet")):
        aggregate_h3(dataset, 8)

    if not valid_parquet(os.path.join(base_url, "cells_res6.parquet")):
        aggregate_h3(dataset, 6)