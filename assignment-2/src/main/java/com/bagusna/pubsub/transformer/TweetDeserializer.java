package com.bagusna.pubsub.transformer;

import com.bagusna.shared.dto.Tweet;
import org.apache.kafka.common.serialization.Deserializer;
import tools.jackson.databind.ObjectMapper;

public class TweetDeserializer implements Deserializer<Tweet> {
    private final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public Tweet deserialize(String topic, byte[] data) {
        if (data == null) {
            return null;
        }

        try {
            return objectMapper.readValue(data, Tweet.class);
        } catch (Exception e) {
            throw new RuntimeException("Error deserializing JSON", e);
        }
    }
}