package com.cinemamax.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;

/**
 * Records a single booked seat for a showtime.
 * Unique constraint on (showtime, row, col) prevents double-booking.
 */
@Entity
@Table(
    name = "booked_seats",
    uniqueConstraints = @UniqueConstraint(columnNames = {"showtime_id", "seat_row", "seat_col"})
)
@Data
@NoArgsConstructor
public class BookedSeat {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "showtime_id", nullable = false)
    private Showtime showtime;

    @Column(name = "seat_row", nullable = false)
    private int seatRow;

    @Column(name = "seat_col", nullable = false)
    private int seatCol;

    @Column(name = "booked_at")
    private LocalDateTime bookedAt = LocalDateTime.now();
}
