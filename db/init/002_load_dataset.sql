COPY netflix.movies (
    movie_id,
    title,
    content_type,
    genre_primary,
    genre_secondary,
    release_year,
    duration_minutes,
    rating,
    language,
    country_of_origin,
    imdb_rating,
    production_budget,
    box_office_revenue,
    number_of_seasons,
    number_of_episodes,
    is_netflix_original,
    added_to_platform,
    content_warning
)
FROM '/dataset/movies.csv'
WITH (FORMAT csv, HEADER true);

COPY netflix.users (
    user_id,
    email,
    first_name,
    last_name,
    age,
    gender,
    country,
    state_province,
    city,
    subscription_plan,
    subscription_start_date,
    is_active,
    monthly_spend,
    primary_device,
    household_size,
    created_at
)
FROM '/dataset/users.csv'
WITH (FORMAT csv, HEADER true);

COPY netflix.watch_history (
    session_id,
    user_id,
    movie_id,
    watch_date,
    device_type,
    watch_duration_minutes,
    progress_percentage,
    action,
    quality,
    location_country,
    is_download,
    user_rating
)
FROM '/dataset/watch_history.csv'
WITH (FORMAT csv, HEADER true);

COPY netflix.reviews (
    review_id,
    user_id,
    movie_id,
    rating,
    review_date,
    device_type,
    is_verified_watch,
    helpful_votes,
    total_votes,
    review_text,
    sentiment,
    sentiment_score
)
FROM '/dataset/reviews.csv'
WITH (FORMAT csv, HEADER true);

COPY netflix.recommendation_logs (
    recommendation_id,
    user_id,
    movie_id,
    recommendation_date,
    recommendation_type,
    recommendation_score,
    was_clicked,
    position_in_list,
    device_type,
    time_of_day,
    algorithm_version
)
FROM '/dataset/recommendation_logs.csv'
WITH (FORMAT csv, HEADER true);

COPY netflix.search_logs (
    search_id,
    user_id,
    search_query,
    search_date,
    results_returned,
    clicked_result_position,
    device_type,
    search_duration_seconds,
    had_typo,
    used_filters,
    location_country
)
FROM '/dataset/search_logs.csv'
WITH (FORMAT csv, HEADER true);
