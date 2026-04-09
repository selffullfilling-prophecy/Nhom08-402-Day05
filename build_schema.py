from __future__ import annotations

import argparse
import os
import re
import sys
from textwrap import dedent

import psycopg2
from psycopg2 import sql


DEFAULT_HOST = os.getenv("PGHOST", "localhost")
DEFAULT_PORT = int(os.getenv("PGPORT", "5432"))
DEFAULT_DBNAME = os.getenv("PGDATABASE", "netflix_qa")
DEFAULT_USER = os.getenv("PGUSER", "netflix")
DEFAULT_PASSWORD = os.getenv("PGPASSWORD", "netflix")
DEFAULT_SCHEMA = os.getenv("NETFLIX_SCHEMA", "netflix")


DDL_TEMPLATE = dedent(
    """
    CREATE SCHEMA IF NOT EXISTS {schema};

    CREATE TABLE IF NOT EXISTS {schema}.movies (
        movie_row_id BIGSERIAL PRIMARY KEY,
        movie_id TEXT NOT NULL,
        title TEXT NOT NULL,
        content_type TEXT NOT NULL,
        genre_primary TEXT NOT NULL,
        genre_secondary TEXT,
        release_year INTEGER NOT NULL,
        duration_minutes NUMERIC(6,1) NOT NULL,
        rating TEXT NOT NULL,
        language TEXT NOT NULL,
        country_of_origin TEXT NOT NULL,
        imdb_rating NUMERIC(3,1),
        production_budget NUMERIC(15,1),
        box_office_revenue NUMERIC(15,1),
        number_of_seasons NUMERIC(6,1),
        number_of_episodes NUMERIC(6,1),
        is_netflix_original BOOLEAN NOT NULL,
        added_to_platform DATE NOT NULL,
        content_warning BOOLEAN NOT NULL,
        loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CHECK (imdb_rating IS NULL OR imdb_rating BETWEEN 0 AND 10)
    );

    CREATE TABLE IF NOT EXISTS {schema}.users (
        user_row_id BIGSERIAL PRIMARY KEY,
        user_id TEXT NOT NULL,
        email TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        age NUMERIC(5,1),
        gender TEXT,
        country TEXT NOT NULL,
        state_province TEXT NOT NULL,
        city TEXT NOT NULL,
        subscription_plan TEXT NOT NULL,
        subscription_start_date DATE NOT NULL,
        is_active BOOLEAN NOT NULL,
        monthly_spend NUMERIC(10,2),
        primary_device TEXT NOT NULL,
        household_size NUMERIC(4,1),
        created_at TIMESTAMP NOT NULL,
        loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CHECK (household_size IS NULL OR household_size >= 0)
    );

    CREATE TABLE IF NOT EXISTS {schema}.watch_history (
        watch_history_row_id BIGSERIAL PRIMARY KEY,
        session_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        movie_id TEXT NOT NULL,
        watch_date DATE NOT NULL,
        device_type TEXT NOT NULL,
        watch_duration_minutes NUMERIC(7,1),
        progress_percentage NUMERIC(5,1),
        action TEXT NOT NULL,
        quality TEXT NOT NULL,
        location_country TEXT NOT NULL,
        is_download BOOLEAN NOT NULL,
        user_rating SMALLINT,
        loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CHECK (progress_percentage IS NULL OR progress_percentage BETWEEN 0 AND 100),
        CHECK (user_rating IS NULL OR user_rating BETWEEN 1 AND 5)
    );

    CREATE TABLE IF NOT EXISTS {schema}.reviews (
        review_row_id BIGSERIAL PRIMARY KEY,
        review_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        movie_id TEXT NOT NULL,
        rating SMALLINT NOT NULL,
        review_date DATE NOT NULL,
        device_type TEXT NOT NULL,
        is_verified_watch BOOLEAN NOT NULL,
        helpful_votes NUMERIC(6,1),
        total_votes NUMERIC(6,1),
        review_text TEXT,
        sentiment TEXT NOT NULL,
        sentiment_score NUMERIC(4,3),
        loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CHECK (rating BETWEEN 1 AND 5),
        CHECK (sentiment_score IS NULL OR sentiment_score BETWEEN 0 AND 1)
    );

    CREATE TABLE IF NOT EXISTS {schema}.recommendation_logs (
        recommendation_log_row_id BIGSERIAL PRIMARY KEY,
        recommendation_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        movie_id TEXT NOT NULL,
        recommendation_date DATE NOT NULL,
        recommendation_type TEXT NOT NULL,
        recommendation_score NUMERIC(4,3),
        was_clicked BOOLEAN NOT NULL,
        position_in_list INTEGER NOT NULL,
        device_type TEXT NOT NULL,
        time_of_day TEXT NOT NULL,
        algorithm_version TEXT,
        loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CHECK (recommendation_score IS NULL OR recommendation_score BETWEEN 0 AND 1),
        CHECK (position_in_list >= 1)
    );

    CREATE TABLE IF NOT EXISTS {schema}.search_logs (
        search_log_row_id BIGSERIAL PRIMARY KEY,
        search_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        search_query TEXT NOT NULL,
        search_date DATE NOT NULL,
        results_returned INTEGER NOT NULL,
        clicked_result_position INTEGER,
        device_type TEXT NOT NULL,
        search_duration_seconds NUMERIC(6,1),
        had_typo BOOLEAN NOT NULL,
        used_filters BOOLEAN NOT NULL,
        location_country TEXT NOT NULL,
        loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CHECK (results_returned >= 0),
        CHECK (clicked_result_position IS NULL OR clicked_result_position >= 1),
        CHECK (search_duration_seconds IS NULL OR search_duration_seconds >= 0)
    );
    """
).strip()


INDEX_DEFINITIONS = (
    ("idx_movies_movie_id", "movies", ("movie_id",)),
    ("idx_users_user_id", "users", ("user_id",)),
    ("idx_users_email", "users", ("email",)),
    ("idx_watch_history_session_id", "watch_history", ("session_id",)),
    ("idx_watch_history_user_id", "watch_history", ("user_id",)),
    ("idx_watch_history_movie_id", "watch_history", ("movie_id",)),
    ("idx_watch_history_watch_date", "watch_history", ("watch_date",)),
    ("idx_reviews_review_id", "reviews", ("review_id",)),
    ("idx_reviews_user_id", "reviews", ("user_id",)),
    ("idx_reviews_movie_id", "reviews", ("movie_id",)),
    ("idx_reviews_review_date", "reviews", ("review_date",)),
    ("idx_recommendation_logs_recommendation_id", "recommendation_logs", ("recommendation_id",)),
    ("idx_recommendation_logs_user_id", "recommendation_logs", ("user_id",)),
    ("idx_recommendation_logs_movie_id", "recommendation_logs", ("movie_id",)),
    ("idx_recommendation_logs_recommendation_date", "recommendation_logs", ("recommendation_date",)),
    ("idx_search_logs_search_id", "search_logs", ("search_id",)),
    ("idx_search_logs_user_id", "search_logs", ("user_id",)),
    ("idx_search_logs_search_date", "search_logs", ("search_date",)),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the PostgreSQL schema for the Netflix synthetic dataset."
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
        "--print-sql",
        action="store_true",
        help="Print the CREATE statements without executing them.",
    )
    return parser.parse_args()


def validate_schema_name(schema_name: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", schema_name):
        raise ValueError(
            f"Invalid schema name '{schema_name}'. Use letters, digits, and underscores only."
        )
    return schema_name


def build_ddl(schema_name: str) -> str:
    return DDL_TEMPLATE.format(schema=schema_name)


def create_indexes(cursor: psycopg2.extensions.cursor, schema_name: str) -> None:
    for index_name, table_name, columns in INDEX_DEFINITIONS:
        cursor.execute(
            sql.SQL("CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns})").format(
                index_name=sql.Identifier(index_name),
                table_name=sql.Identifier(schema_name, table_name),
                columns=sql.SQL(", ").join(sql.Identifier(column) for column in columns),
            )
        )


def main() -> int:
    args = parse_args()

    try:
        schema_name = validate_schema_name(args.schema)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1

    ddl = build_ddl(schema_name)

    if args.print_sql:
        print(ddl)
        print("-- Index statements are created programmatically after the tables.")
        return 0

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

    try:
        with psycopg2.connect(**connection_kwargs) as conn:
            with conn.cursor() as cursor:
                cursor.execute(ddl)
                create_indexes(cursor, schema_name)
            conn.commit()
    except psycopg2.Error as exc:
        print(f"Failed to build schema: {exc}", file=sys.stderr)
        return 1

    print("Schema created successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
