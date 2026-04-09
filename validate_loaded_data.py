from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import psycopg2
from psycopg2 import sql

from build_schema import (
    DEFAULT_DBNAME,
    DEFAULT_HOST,
    DEFAULT_PASSWORD,
    DEFAULT_PORT,
    DEFAULT_SCHEMA,
    DEFAULT_USER,
    validate_schema_name,
)


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DATASET_DIR = PROJECT_ROOT / "dataset"

TABLE_SPECS = (
    ("movies", "movies.csv", "movie_id"),
    ("users", "users.csv", "user_id"),
    ("watch_history", "watch_history.csv", "session_id"),
    ("reviews", "reviews.csv", "review_id"),
    ("recommendation_logs", "recommendation_logs.csv", "recommendation_id"),
    ("search_logs", "search_logs.csv", "search_id"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that the CSV dataset was loaded into PostgreSQL correctly."
    )
    parser.add_argument("--host", default=DEFAULT_HOST, help="PostgreSQL host.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="PostgreSQL port.")
    parser.add_argument("--dbname", default=DEFAULT_DBNAME, help="Database name.")
    parser.add_argument("--user", default=DEFAULT_USER, help="Database user.")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help="Database password.")
    parser.add_argument(
        "--schema",
        default=DEFAULT_SCHEMA,
        help="Target schema name. Defaults to NETFLIX_SCHEMA or 'netflix'.",
    )
    parser.add_argument(
        "--dataset-dir",
        default=str(DEFAULT_DATASET_DIR),
        help="Folder containing the CSV files.",
    )
    return parser.parse_args()


def validate_dataset_dir(dataset_dir: Path) -> None:
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {dataset_dir}")

    missing_files = [filename for _, filename, _ in TABLE_SPECS if not (dataset_dir / filename).exists()]
    if missing_files:
        raise FileNotFoundError(
            "Missing CSV files in dataset directory: " + ", ".join(missing_files)
        )


def csv_stats(file_path: Path, key_column: str) -> tuple[int, int]:
    row_count = 0
    distinct_keys: set[str] = set()
    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            row_count += 1
            distinct_keys.add(row[key_column])
    return row_count, len(distinct_keys)


def table_exists(cursor: psycopg2.extensions.cursor, schema_name: str, table_name: str) -> bool:
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
        )
        """,
        (schema_name, table_name),
    )
    return bool(cursor.fetchone()[0])


def db_stats(
    cursor: psycopg2.extensions.cursor,
    schema_name: str,
    table_name: str,
    key_column: str,
) -> tuple[int, int]:
    cursor.execute(
        sql.SQL("SELECT COUNT(*), COUNT(DISTINCT {}) FROM {}").format(
            sql.Identifier(key_column),
            sql.Identifier(schema_name, table_name),
        )
    )
    total_rows, distinct_keys = cursor.fetchone()
    return int(total_rows), int(distinct_keys)


def main() -> int:
    args = parse_args()

    try:
        schema_name = validate_schema_name(args.schema)
        dataset_dir = Path(args.dataset_dir).resolve()
        validate_dataset_dir(dataset_dir)
    except (ValueError, FileNotFoundError) as exc:
        print(exc, file=sys.stderr)
        return 1

    print(
        f"Validating PostgreSQL load at {args.host}:{args.port}, "
        f"database='{args.dbname}', schema='{schema_name}'..."
    )
    print(f"Dataset directory: {dataset_dir}")

    connection_kwargs = {
        "host": args.host,
        "port": args.port,
        "dbname": args.dbname,
        "user": args.user,
        "password": args.password,
    }

    failures: list[str] = []

    try:
        with psycopg2.connect(**connection_kwargs) as conn:
            with conn.cursor() as cursor:
                for table_name, filename, key_column in TABLE_SPECS:
                    file_path = dataset_dir / filename
                    csv_rows, csv_distinct_keys = csv_stats(file_path, key_column)

                    if not table_exists(cursor, schema_name, table_name):
                        failures.append(f"{table_name}: table does not exist in schema '{schema_name}'")
                        print(f"[FAIL] {table_name}: table is missing")
                        continue

                    db_rows, db_distinct_keys = db_stats(cursor, schema_name, table_name, key_column)
                    status = "OK"
                    if db_rows != csv_rows or db_distinct_keys != csv_distinct_keys:
                        status = "FAIL"
                        failures.append(
                            f"{table_name}: csv_rows={csv_rows}, db_rows={db_rows}, "
                            f"csv_distinct_{key_column}={csv_distinct_keys}, "
                            f"db_distinct_{key_column}={db_distinct_keys}"
                        )

                    print(
                        f"[{status}] {table_name}: "
                        f"csv_rows={csv_rows}, db_rows={db_rows}, "
                        f"csv_distinct_{key_column}={csv_distinct_keys}, "
                        f"db_distinct_{key_column}={db_distinct_keys}"
                    )
    except psycopg2.Error as exc:
        print(f"Failed to validate dataset load: {exc}", file=sys.stderr)
        return 1

    if failures:
        print("\nValidation failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print("\nValidation passed: PostgreSQL row counts and distinct business keys match the CSV files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
