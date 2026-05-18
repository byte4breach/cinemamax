package com.cinemamax.controller;

import com.cinemamax.service.CinemaService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST API controller.
 *
 * All endpoints are under /api/ so the Java backend can also serve
 * the static index.html at / without path conflicts.
 *
 * The Python Telegram bot calls these same endpoints via HTTP.
 * The Web App (index.html) also calls them from the browser.
 *
 * Endpoints:
 *   GET  /api/movies                      → list of movies
 *   GET  /api/movies/{id}/showtimes        → showtimes for a movie
 *   GET  /api/showtimes/{id}/seats         → booked seats for a showtime
 *   POST /api/bookings                     → book seats
 */
@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class CinemaController {

    private final CinemaService service;

    /** List all movies with showtime count */
    @GetMapping("/movies")
    public List<CinemaService.MovieDTO> getMovies() {
        return service.getAllMovies();
    }

    /** Showtimes for a specific movie */
    @GetMapping("/movies/{id}/showtimes")
    public List<CinemaService.ShowtimeDTO> getShowtimes(@PathVariable Long id) {
        return service.getShowtimesForMovie(id);
    }

    /** Booked seat positions for a showtime */
    @GetMapping("/showtimes/{id}/seats")
    public List<String> getBookedSeats(@PathVariable Long id) {
        return service.getBookedSeats(id);
    }

    /** Book seats — called from both the web app and the Telegram bot */
    @PostMapping("/bookings")
    public ResponseEntity<CinemaService.BookingResult> bookSeats(
            @RequestBody CinemaService.BookingRequest request) {

        CinemaService.BookingResult result = service.bookSeats(request);
        if (result.success()) {
            return ResponseEntity.ok(result);
        } else {
            return ResponseEntity.badRequest().body(result);
        }
    }
}
