# PostgreSQL Dataset Setup

## Dataset check summary

The downloaded dataset contains 6 CSV files:

- `movies.csv`: 1,040 rows
- `users.csv`: 10,300 rows
- `watch_history.csv`: 105,000 rows
- `reviews.csv`: 15,450 rows
- `recommendation_logs.csv`: 52,000 rows
- `search_logs.csv`: 26,500 rows

The source intentionally contains duplicate business IDs and missing values, so the database schema keeps those source IDs as regular indexed columns instead of forcing them to be unique.

## Files added

- `docker-compose.yml`: PostgreSQL service for local development
- `db/init/001_schema.sql`: table definitions and indexes
- `db/init/002_load_dataset.sql`: initial CSV import

## Start the database

```bash
docker compose up -d
```

Database connection:

- Host: `localhost`
- Port: `5432`
- Database: `netflix_qa`
- User: `netflix`
- Password: `netflix`

## Verify loaded data

```bash
docker exec -it netflix-postgres psql -U netflix -d netflix_qa
```

```sql
SELECT COUNT(*) FROM netflix.users;
SELECT COUNT(*) FROM netflix.movies;
SELECT COUNT(*) FROM netflix.watch_history;
```

## Re-run initialization

PostgreSQL only runs `/docker-entrypoint-initdb.d` on first container creation. If you change the init SQL and want a clean rebuild:

```bash
docker compose down -v
docker compose up -d
```
