package com.cinemamax.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;

/**
 * Represents a movie in the cinema.
 * Lombok @Data auto-generates getters, setters, equals, hashCode, toString.
 */
@Entity
@Table(name = "movies")
@Data
@NoArgsConstructor
public class Movie {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false)
    private String genre = "CINEMA";

    @Column(name = "is_blockbuster", nullable = false)
    private boolean blockbuster = false;

    // One movie has many showtimes
    @OneToMany(mappedBy = "movie", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<Showtime> showtimes;
}
