package com.cinemamax;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * CinemaMax – Java Spring Boot backend
 *
 * This server:
 *  1. Exposes a REST API at /api/** (used by the web app AND the Python Telegram bot)
 *  2. Serves static files (index.html) at /
 *  3. Connects to PostgreSQL (URL comes from the DATABASE_URL env variable on Render)
 */
@SpringBootApplication
public class CinemaMaxApplication {
    public static void main(String[] args) {
        SpringApplication.run(CinemaMaxApplication.class, args);
    }
}
