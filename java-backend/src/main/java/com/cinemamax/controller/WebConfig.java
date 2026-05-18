package com.cinemamax.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.*;

/**
 * CORS + Static file configuration.
 *
 * CORS (Cross-Origin Resource Sharing) allows the browser on GitHub Pages
 * and Telegram WebApp to call our Java API on Render.com.
 *
 * Static files: We tell Spring to serve everything in /static/ as-is,
 * so you can drop index.html (and any CSS/JS) into
 * src/main/resources/static/ and it will be served at /.
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${cinemamax.cors.allowed-origins}")
    private String allowedOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/api/**")
            .allowedOriginPatterns("*")   // allow all for Telegram WebApp
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("*")
            .allowCredentials(false);
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        // Serve static files (index.html etc.) from /static/
        registry.addResourceHandler("/**")
            .addResourceLocations("classpath:/static/");
    }
}
