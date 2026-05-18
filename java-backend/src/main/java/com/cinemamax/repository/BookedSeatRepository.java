package com.cinemamax.repository;

import com.cinemamax.model.BookedSeat;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface BookedSeatRepository extends JpaRepository<BookedSeat, Long> {

    List<BookedSeat> findByShowtimeId(Long showtimeId);

    boolean existsByShowtimeIdAndSeatRowAndSeatCol(Long showtimeId, int seatRow, int seatCol);
}
