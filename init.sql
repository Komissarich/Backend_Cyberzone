ALTER DATABASE task SET timezone TO 'Europe/Moscow';
CREATE TABLE IF NOT EXISTS users(
    id SERIAL PRIMARY KEY,
    username TEXT,
    password TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ);



CREATE TABLE IF NOT EXISTS posts(
    id TEXT PRIMARY KEY,
    text TEXT,
    user_id TEXT,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ);


CREATE TABLE IF NOT EXISTS user_to_posts(
    post_id TEXT,
    user_login TEXT);