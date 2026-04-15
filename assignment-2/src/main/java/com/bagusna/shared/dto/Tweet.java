package com.bagusna.shared.dto;

import java.time.LocalDateTime;

public record Tweet(String text, String author, LocalDateTime timestamp) {
    public Tweet(String text, String author) {
        this(text, author, LocalDateTime.now());
    }
}
