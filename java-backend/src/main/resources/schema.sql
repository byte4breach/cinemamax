-- CinemaMax – initial schema
-- Spring Boot runs this automatically via schema.sql when
-- spring.sql.init.mode=always  (set in application.properties for first deploy)

CREATE TABLE IF NOT EXISTS movies (
    id             SERIAL PRIMARY KEY,
    title          VARCHAR(255) NOT NULL,
    genre          VARCHAR(80)  NOT NULL DEFAULT 'CINEMA',
    is_blockbuster BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS showtimes (
    id         SERIAL PRIMARY KEY,
    movie_id   INTEGER      NOT NULL REFERENCES movies(id) ON DELETE CASCADE,
    hall_name  VARCHAR(100) NOT NULL,
    show_time  TIME         NOT NULL,
    is_vip     BOOLEAN      NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS booked_seats (
    id           SERIAL PRIMARY KEY,
    showtime_id  INTEGER NOT NULL REFERENCES showtimes(id) ON DELETE CASCADE,
    seat_row     INTEGER NOT NULL,
    seat_col     INTEGER NOT NULL,
    booked_at    TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (showtime_id, seat_row, seat_col)
);

-- ── Sample data (safe to re-run thanks to ON CONFLICT DO NOTHING) ──

INSERT INTO movies (title, genre, is_blockbuster) VALUES
  ('Avengers: Endgame',  'ACTION',  TRUE),
  ('Inception',          'SCI-FI',  TRUE),
  ('The Godfather',      'DRAMA',   FALSE),
  ('Interstellar',       'SCI-FI',  TRUE),
  ('Parasite',           'DRAMA',   FALSE),
  ('Top Gun: Maverick',  'ACTION',  TRUE),
  ('Dune: Part Two',     'SCI-FI',  TRUE),
  ('Oppenheimer',        'DRAMA',   TRUE)
ON CONFLICT DO NOTHING;

INSERT INTO showtimes (movie_id, hall_name, show_time, is_vip)
SELECT m.id, 'Hall A', '10:00', FALSE FROM movies m WHERE m.title = 'Avengers: Endgame'
ON CONFLICT DO NOTHING;
INSERT INTO showtimes (movie_id, hall_name, show_time, is_vip)
SELECT m.id, 'VIP Platinum', '14:30', TRUE FROM movies m WHERE m.title = 'Avengers: Endgame'
ON CONFLICT DO NOTHING;

INSERT INTO showtimes (movie_id, hall_name, show_time, is_vip)
SELECT m.id, 'Hall B', '12:00', FALSE FROM movies m WHERE m.title = 'Inception'
ON CONFLICT DO NOTHING;
INSERT INTO showtimes (movie_id, hall_name, show_time, is_vip)
SELECT m.id, 'Hall A', '18:00', FALSE FROM movies m WHERE m.title = 'Inception'
ON CONFLICT DO NOTHING;

INSERT INTO showtimes (movie_id, hall_name, show_time, is_vip)
SELECT m.id, 'Hall C', '15:00', FALSE FROM movies m WHERE m.title = 'Interstellar'
ON CONFLICT DO NOTHING;

INSERT INTO showtimes (movie_id, hall_name, show_time, is_vip)
SELECT m.id, 'VIP Platinum', '20:00', TRUE FROM movies m WHERE m.title = 'Dune: Part Two'
ON CONFLICT DO NOTHING;
INSERT INTO showtimes (movie_id, hall_name, show_time, is_vip)
SELECT m.id, 'Hall A', '11:30', FALSE FROM movies m WHERE m.title = 'Dune: Part Two'
ON CONFLICT DO NOTHING;
