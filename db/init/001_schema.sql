CREATE SCHEMA IF NOT EXISTS netflix;

CREATE TABLE IF NOT EXISTS netflix.movies (
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

CREATE TABLE IF NOT EXISTS netflix.users (
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

CREATE TABLE IF NOT EXISTS netflix.watch_history (
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

CREATE TABLE IF NOT EXISTS netflix.reviews (
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

CREATE TABLE IF NOT EXISTS netflix.recommendation_logs (
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

CREATE TABLE IF NOT EXISTS netflix.search_logs (
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

CREATE INDEX IF NOT EXISTS idx_movies_movie_id
    ON netflix.movies (movie_id);

CREATE INDEX IF NOT EXISTS idx_users_user_id
    ON netflix.users (user_id);

CREATE INDEX IF NOT EXISTS idx_users_email
    ON netflix.users (email);

CREATE INDEX IF NOT EXISTS idx_watch_history_session_id
    ON netflix.watch_history (session_id);

CREATE INDEX IF NOT EXISTS idx_watch_history_user_id
    ON netflix.watch_history (user_id);

CREATE INDEX IF NOT EXISTS idx_watch_history_movie_id
    ON netflix.watch_history (movie_id);

CREATE INDEX IF NOT EXISTS idx_watch_history_watch_date
    ON netflix.watch_history (watch_date);

CREATE INDEX IF NOT EXISTS idx_reviews_review_id
    ON netflix.reviews (review_id);

CREATE INDEX IF NOT EXISTS idx_reviews_user_id
    ON netflix.reviews (user_id);

CREATE INDEX IF NOT EXISTS idx_reviews_movie_id
    ON netflix.reviews (movie_id);

CREATE INDEX IF NOT EXISTS idx_recommendation_logs_recommendation_id
    ON netflix.recommendation_logs (recommendation_id);

CREATE INDEX IF NOT EXISTS idx_recommendation_logs_user_id
    ON netflix.recommendation_logs (user_id);

CREATE INDEX IF NOT EXISTS idx_recommendation_logs_movie_id
    ON netflix.recommendation_logs (movie_id);

CREATE INDEX IF NOT EXISTS idx_search_logs_search_id
    ON netflix.search_logs (search_id);

CREATE INDEX IF NOT EXISTS idx_search_logs_user_id
    ON netflix.search_logs (user_id);
