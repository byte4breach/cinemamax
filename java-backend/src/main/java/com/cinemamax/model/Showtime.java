package com.cinemamax.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalTime;
import java.util.List;

/**
 * A specific screening of a movie (hall + time + VIP flag).
 */
@Entity
@Table(name = "showtimes")
@Data
@NoArgsConstructor
public class Showtime {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    // Many showtimes belong to one movie
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "movie_id", nullable = false)
    private Movie movie;

    @Column(name = "hall_name", nullable = false)
    private String hallName;

    @Column(name = "show_time", nullable = false)
    private LocalTime showTime;

    @Column(name = "is_vip", nullable = false)
    private boolean vip = false;

    // One showtime has many booked seats
    @OneToMany(mappedBy = "showtime", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<BookedSeat> bookedSeats;
}
