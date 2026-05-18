package com.cinemamax.repository;

import com.cinemamax.model.Movie;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;

import java.util.List;

/**
 * Spring Data automatically implements all basic CRUD methods.
 * We just add one custom query to get movies with their showtime count.
 */
public interface MovieRepository extends JpaRepository<Movie, Long> {

    @Query("""
        SELECT m FROM Movie m
        LEFT JOIN FETCH m.showtimes
        ORDER BY m.title
        """)
    List<Movie> findAllWithShowtimes();
}
