from __future__ import annotations

import argparse
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
    {
        "table": "movies",
        "file": "movies.csv",
        "columns": (
            "movie_id",
            "title",
            "content_type",
            "genre_primary",
            "genre_secondary",
            "release_year",
            "duration_minutes",
            "rating",
            "language",
            "country_of_origin",
            "imdb_rating",
            "production_budget",
            "box_office_revenue",
            "number_of_seasons",
            "number_of_episodes",
            "is_netflix_original",
            "added_to_platform",
            "content_warning",
        ),
    },
    {
        "table": "users",
        "file": "users.csv",
        "columns": (
            "user_id",
            "email",
            "first_name",
            "last_name",
            "age",
            "gender",
            "country",
            "state_province",
            "city",
            "subscription_plan",
            "subscription_start_date",
            "is_active",
            "monthly_spend",
            "primary_device",
            "household_size",
            "created_at",
        ),
    },
    {
        "table": "watch_history",
        "file": "watch_history.csv",
        "columns": (
            "session_id",
            "user_id",
            "movie_id",
            "watch_date",
            "device_type",
            "watch_duration_minutes",
            "progress_percentage",
            "action",
            "quality",
            "location_country",
            "is_download",
            "user_rating",
        ),
    },
    {
        "table": "reviews",
        "file": "reviews.csv",
        "columns": (
            "review_id",
            "user_id",
            "movie_id",
            "rating",
            "review_date",
            "device_type",
            "is_verified_watch",
            "helpful_votes",
            "total_votes",
            "review_text",
            "sentiment",
            "sentiment_score",
        ),
    },
    {
        "table": "recommendation_logs",
        "file": "recommendation_logs.csv",
        "columns": (
            "recommendation_id",
            "user_id",
            "movie_id",
            "recommendation_date",
            "recommendation_type",
            "recommendation_score",
            "was_clicked",
            "position_in_list",
            "device_type",
            "time_of_day",
            "algorithm_version",
        ),
    },
    {
        "table": "search_logs",
        "file": "search_logs.csv",
        "columns": (
            "search_id",
            "user_id",
            "search_query",
            "search_date",
            "results_returned",
            "clicked_result_position",
            "device_type",
            "search_duration_seconds",
            "had_typo",
            "used_filters",
            "location_country",
        ),
    },
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load the Netflix synthetic CSV dataset into PostgreSQL tables."
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
    parser.add_argument(
        "--truncate",
        action="store_true",
        help="Truncate target tables before loading. Recommended for a clean reload.",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="Append rows even if target tables already contain data.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate files and show what would be loaded without modifying the database.",
    )
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> str:
    if args.truncate and args.append:
        raise ValueError("Choose only one of --truncate or --append.")
    return validate_schema_name(args.schema)


def validate_dataset_dir(dataset_dir: Path) -> None:
    if not dataset_dir.exists():
        raise FileNotFoundError(f"Dataset directory does not exist: {dataset_dir}")

    missing_files = [spec["file"] for spec in TABLE_SPECS if not (dataset_dir / spec["file"]).exists()]
    if missing_files:
        raise FileNotFoundError(
            "Missing CSV files in dataset directory: " + ", ".join(missing_files)
        )


def fetch_table_counts(
    cursor: psycopg2.extensions.cursor,
    schema_name: str,
) -> dict[str, int]:
    counts: dict[str, int] = {}
    for spec in TABLE_SPECS:
        table_name = spec["table"]
        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM {}").format(
                sql.Identifier(schema_name, table_name)
            )
        )
        counts[table_name] = cursor.fetchone()[0]
    return counts


def ensure_load_is_safe(counts: dict[str, int], append: bool, truncate: bool) -> None:
    non_empty = {table: count for table, count in counts.items() if count > 0}
    if non_empty and not append and not truncate:
        joined = ", ".join(f"{table}={count}" for table, count in non_empty.items())
        raise RuntimeError(
            "Target tables already contain data. "
            f"Current row counts: {joined}. "
            "Use --truncate for a clean reload or --append to load on top of existing rows."
        )


def truncate_tables(cursor: psycopg2.extensions.cursor, schema_name: str) -> None:
    identifiers = [
        sql.Identifier(schema_name, spec["table"])
        for spec in TABLE_SPECS
    ]
    cursor.execute(
        sql.SQL("TRUNCATE TABLE {} RESTART IDENTITY").format(
            sql.SQL(", ").join(identifiers)
        )
    )


def load_table(
    conn: psycopg2.extensions.connection,
    cursor: psycopg2.extensions.cursor,
    schema_name: str,
    dataset_dir: Path,
    spec: dict[str, object],
) -> None:
    table_name = spec["table"]
    file_path = dataset_dir / str(spec["file"])
    columns = spec["columns"]

    copy_sql = sql.SQL(
        "COPY {} ({}) FROM STDIN WITH (FORMAT CSV, HEADER TRUE, NULL '')"
    ).format(
        sql.Identifier(schema_name, str(table_name)),
        sql.SQL(", ").join(sql.Identifier(column) for column in columns),
    )

    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        cursor.copy_expert(copy_sql.as_string(conn), handle)


def print_counts(title: str, counts: dict[str, int]) -> None:
    print(title)
    for spec in TABLE_SPECS:
        table_name = spec["table"]
        print(f"  - {table_name}: {counts[table_name]}")


def main() -> int:
    args = parse_args()

    try:
        schema_name = validate_args(args)
        dataset_dir = Path(args.dataset_dir).resolve()
        validate_dataset_dir(dataset_dir)
    except (ValueError, FileNotFoundError) as exc:
        print(exc, file=sys.stderr)
        return 1

    connection_kwargs = {
        "host": args.host,
        "port": args.port,
        "dbname": args.dbname,
        "user": args.user,
        "password": args.password,
    }

    print(
        f"Connecting to PostgreSQL at {args.host}:{args.port}, "
        f"database='{args.dbname}', schema='{schema_name}'..."
    )
    print(f"Dataset directory: {dataset_dir}")

    try:
        with psycopg2.connect(**connection_kwargs) as conn:
            with conn.cursor() as cursor:
                before_counts = fetch_table_counts(cursor, schema_name)
                print_counts("Current row counts:", before_counts)

                if args.dry_run:
                    non_empty = {table: count for table, count in before_counts.items() if count > 0}
                    if non_empty:
                        print(
                            "Note: target tables are not empty. "
                            "Use --truncate for a clean reload or --append to add more rows."
                        )
                    print("Dry run completed. No data was loaded.")
                    return 0

                ensure_load_is_safe(before_counts, args.append, args.truncate)

                if args.truncate:
                    print("Truncating target tables before load...")
                    truncate_tables(cursor, schema_name)

                for spec in TABLE_SPECS:
                    print(f"Loading {spec['file']} into {schema_name}.{spec['table']}...")
                    load_table(conn, cursor, schema_name, dataset_dir, spec)

                after_counts = fetch_table_counts(cursor, schema_name)
                print_counts("Row counts after load:", after_counts)

            conn.commit()
    except (psycopg2.Error, RuntimeError) as exc:
        print(f"Failed to load dataset: {exc}", file=sys.stderr)
        return 1

    print("Dataset loaded successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
