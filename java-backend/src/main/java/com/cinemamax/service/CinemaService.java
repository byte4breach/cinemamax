package com.cinemamax.service;

import com.cinemamax.model.BookedSeat;
import com.cinemamax.model.Movie;
import com.cinemamax.model.Showtime;
import com.cinemamax.repository.BookedSeatRepository;
import com.cinemamax.repository.MovieRepository;
import com.cinemamax.repository.ShowtimeRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * All business logic lives here.
 * Controllers call these methods and return the results as JSON.
 *
 * Key Java concepts used:
 *  - @Service   : marks this as a Spring-managed bean
 *  - @Transactional : wraps DB calls in a transaction (auto-rollback on error)
 *  - Stream API : Java's functional processing of collections
 *  - Record     : immutable data carrier (replaces DTO classes)
 */
@Service
@RequiredArgsConstructor  // Lombok: generates constructor for all final fields
public class CinemaService {

    // Constants — same as in your Python code
    private static final int STANDARD_ROWS = 8;
    private static final int STANDARD_COLS = 12;
    private static final int VIP_ROWS = 4;
    private static final int VIP_COLS = 6;
    private static final int STANDARD_PRICE = 20;
    private static final int VIP_PRICE = 50;

    private final MovieRepository movieRepo;
    private final ShowtimeRepository showtimeRepo;
    private final BookedSeatRepository bookedSeatRepo;

    // ── DTOs (Data Transfer Objects) ──────────────────────────────────────────
    // Records are immutable value objects — Java 16+. Perfect for API responses.

    public record MovieDTO(
        long id,
        String title,
        String genre,
        boolean blockbuster,
        int showCount
    ) {}

    public record ShowtimeDTO(
        long id,
        String hallName,
        String showTime,   // "HH:mm"
        boolean vip,
        int capacity,
        int bookedCount,
        int available,
        int pricePerSeat
    ) {}

    public record SeatDTO(int row, int col) {}

    public record BookingRequest(long showtimeId, List<String> seats) {
        // seats format: ["0-0", "0-1", "2-3"]  same as Python/frontend
    }

    public record BookingResult(boolean success, String message, int totalPrice) {}

    // ── Queries ───────────────────────────────────────────────────────────────

    /** Returns all movies with their showtime count. */
    public List<MovieDTO> getAllMovies() {
        return movieRepo.findAll().stream()
            .map(m -> new MovieDTO(
                m.getId(),
                m.getTitle(),
                m.getGenre(),
                m.isBlockbuster(),
                m.getShowtimes() != null ? m.getShowtimes().size() : 0
            ))
            .sorted(Comparator.comparing(MovieDTO::title))
            .toList();
    }

    /** Returns showtimes for a specific movie with availability info. */
    public List<ShowtimeDTO> getShowtimesForMovie(Long movieId) {
        return showtimeRepo.findByMovieIdWithBookings(movieId).stream()
            .map(s -> {
                int cap = capacity(s.isVip());
                int booked = s.getBookedSeats() != null ? s.getBookedSeats().size() : 0;
                return new ShowtimeDTO(
                    s.getId(),
                    s.getHallName(),
                    s.getShowTime().toString().substring(0, 5),   // "HH:mm"
                    s.isVip(),
                    cap,
                    booked,
                    cap - booked,
                    s.isVip() ? VIP_PRICE : STANDARD_PRICE
                );
            })
            .toList();
    }

    /** Returns booked seat positions for a showtime as "row-col" strings. */
    public List<String> getBookedSeats(Long showtimeId) {
        return bookedSeatRepo.findByShowtimeId(showtimeId).stream()
            .map(b -> b.getSeatRow() + "-" + b.getSeatCol())
            .toList();
    }

    /** Books seats. Returns error message if any seat is already taken. */
    @Transactional
    public BookingResult bookSeats(BookingRequest request) {
        Showtime showtime = showtimeRepo.findById(request.showtimeId())
            .orElseThrow(() -> new NoSuchElementException("Showtime not found"));

        // Check for conflicts first (all-or-nothing)
        for (String pos : request.seats()) {
            int[] rc = parsePos(pos);
            if (bookedSeatRepo.existsByShowtimeIdAndSeatRowAndSeatCol(
                    request.showtimeId(), rc[0], rc[1])) {
                return new BookingResult(false, "Seat " + pos + " is already booked.", 0);
            }
        }

        // Insert all seats
        int priceEach = showtime.isVip() ? VIP_PRICE : STANDARD_PRICE;
        for (String pos : request.seats()) {
            int[] rc = parsePos(pos);
            BookedSeat bs = new BookedSeat();
            bs.setShowtime(showtime);
            bs.setSeatRow(rc[0]);
            bs.setSeatCol(rc[1]);
            bookedSeatRepo.save(bs);
        }

        int total = request.seats().size() * priceEach;
        return new BookingResult(true, "Booking confirmed!", total);
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private int capacity(boolean isVip) {
        return isVip ? VIP_ROWS * VIP_COLS : STANDARD_ROWS * STANDARD_COLS;
    }

    private int[] parsePos(String pos) {
        String[] parts = pos.split("-");
        return new int[]{Integer.parseInt(parts[0]), Integer.parseInt(parts[1])};
    }
}
