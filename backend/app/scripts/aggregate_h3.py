import duckdb
import time
import os

TEMP_DIR = "/mnt/data/duckdb_tmp"

def create_category_mode_parquet(
    dataset: str,
    input_parquet: str,
    category: str,
    mode: str,
    input_resolution: int,
):
    """
    Create a temporary parquet containing only:

        h3
        category_mode_metric

    The parquet is created at the input resolution.
    """

    base_url = f"/mnt/data/results/{dataset}"
    os.makedirs(TEMP_DIR, exist_ok=True)

    metric_column = f"poi_{category}_{mode}"

    output_dir = os.path.join(base_url, "tmp")
    os.makedirs(output_dir, exist_ok=True)

    output_parquet = os.path.join(
        output_dir,
        f"{category}_{mode}_res{input_resolution}.parquet"
    )

    t0 = time.time()

    con = duckdb.connect()

    try:
        con.execute("SET memory_limit='8GB'")
        con.execute("SET threads=1")
        con.execute("SET preserve_insertion_order=false")

        con.execute(f"SET temp_directory='{TEMP_DIR}'")
        con.execute("SET max_temp_directory_size='80GB'")

        print("Loading H3 extension...")
        con.execute("INSTALL h3 FROM community;")
        con.execute("LOAD h3;")

        print(f"Creating temporary parquet for {category} × {mode}")
        print(f"Metric column: {metric_column}")

        # Check that the requested column exists.
        columns = con.execute(
            f"""
            DESCRIBE SELECT *
            FROM read_parquet('{input_parquet}')
            """
        ).fetchdf()["column_name"].tolist()

        if metric_column not in columns:
            raise ValueError(
                f"Column '{metric_column}' not found in {input_parquet}"
            )

        con.execute(
            f"""
            COPY (
                SELECT
                    h3,
                    "{metric_column}" AS value
                FROM read_parquet('{input_parquet}')
            )
            TO '{output_parquet}'
            (FORMAT PARQUET)
            """
        )

        print(
            f"Created {output_parquet} "
            f"in {time.time() - t0:.2f}s"
        )

        return output_parquet

    except Exception as e:
        print(
            f"Failed to create temporary parquet "
            f"for {category} × {mode}: {e}"
        )
        raise

    finally:
        con.close()


def aggregate_h3(
    input_parquet: str,
    output_parquet: str,
    res: int,
):
    """
    Aggregate a single category×mode parquet to a lower H3 resolution.

    Input:
        h3, value

    Output:
        h3, value
    """

    t0 = time.time()

    con = duckdb.connect()

    try:
        con.execute("SET memory_limit='8GB'")
        con.execute("SET threads=1")
        con.execute("SET preserve_insertion_order=false")

        con.execute(f"SET temp_directory='{TEMP_DIR}'")
        con.execute("SET max_temp_directory_size='80GB'")

        con.execute("LOAD h3;")

        print(
            f"Aggregating {input_parquet} → res{res}"
        )

        con.execute(
            f"""
            COPY (
                SELECT
                    h3_cell_to_parent(h3, {res}) AS h3,
                    AVG(value) AS value
                FROM read_parquet('{input_parquet}')
                GROUP BY 1
            )
            TO '{output_parquet}'
            (FORMAT PARQUET)
            """
        )

        print(
            f"Created {output_parquet} "
            f"in {time.time() - t0:.2f}s"
        )

    except Exception as e:
        print(f"H3 aggregation failed: {e}")
        raise

    finally:
        con.close()
        
def create_category_mode_resolutions(
    dataset: str,
    input_parquet: str,
    category: str,
    mode: str,
    input_resolution: int,
    resolutions: list[int],
):
    """
    Create temporary parquet files for one category×mode
    at all required H3 resolutions.

    The files contain only:

        h3
        value

    Resolutions are generated progressively:

        source → res10 → res8 → res6

    The returned dictionary maps resolution to parquet path.
    """

    base_url = f"/mnt/data/results/{dataset}"

    output_dir = os.path.join(base_url, "tmp")
    os.makedirs(output_dir, exist_ok=True)

    # First create the category×mode parquet at the original resolution.
    current_parquet = create_category_mode_parquet(
        dataset=dataset,
        input_parquet=input_parquet,
        category=category,
        mode=mode,
        input_resolution=input_resolution,
    )

    paths = {
        input_resolution: current_parquet
    }

    # Generate lower resolutions progressively.
    for res in sorted(resolutions, reverse=True):

        # Don't recreate the input resolution.
        if res >= input_resolution:
            continue

        output_parquet = os.path.join(
            output_dir,
            f"{category}_{mode}_res{res}.parquet"
        )

        aggregate_h3(
            input_parquet=current_parquet,
            output_parquet=output_parquet,
            res=res,
        )

        paths[res] = output_parquet

        # Next aggregation starts from this lower resolution.
        current_parquet = output_parquet

    return paths