package com.cinemamax.repository;

import com.cinemamax.model.Showtime;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;

public interface ShowtimeRepository extends JpaRepository<Showtime, Long> {

    @Query("""
        SELECT s FROM Showtime s
        LEFT JOIN FETCH s.bookedSeats
        WHERE s.movie.id = :movieId
        ORDER BY s.showTime
        """)
    List<Showtime> findByMovieIdWithBookings(@Param("movieId") Long movieId);
}
