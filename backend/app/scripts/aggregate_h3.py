import duckdb
import time

BASE_URL = "/mnt/data/results/2026-03-18T14-34-36Z_europe-germany_b9dada"

INPUT_PARQUET = f"{BASE_URL}/cells.parquet"

def aggregate_h3(input_parquet: str, res: int):
    t0 = time.time()

    con = duckdb.connect()

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

    output_parquet = f"{BASE_URL}/cells_res{res}.parquet"
    
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
    
    
aggregate_h3(INPUT_PARQUET, 8)
aggregate_h3(INPUT_PARQUET, 6)