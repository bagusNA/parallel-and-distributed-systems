package com.bagusna.pubsub.transformer;

import org.apache.kafka.common.serialization.Serializer;
import tools.jackson.databind.ObjectMapper;

public class JsonSerializer<T> implements Serializer<T> {
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public byte[] serialize(String topic, T data) {
        try {
            return objectMapper.writeValueAsBytes(data);
        } catch (Exception e) {
            throw new RuntimeException("Error serializing JSON", e);
        }
    }
}