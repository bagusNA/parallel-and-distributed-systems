package com.bagusna.pubsub;

import com.bagusna.pubsub.service.PubSubService;
import com.bagusna.shared.dto.Tweet;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;

import java.time.Duration;
import java.util.List;


public class Subscriber {
    private static final String topic = "tweets";

    static void main() {
        PubSubService<Tweet> pubSubService = new PubSubService<>();

        KafkaConsumer<String, Tweet> consumer = pubSubService.getConsumer();

        try (consumer) {
            consumer.subscribe(List.of(topic));

            while (true) {
                ConsumerRecords<String, Tweet> messages = consumer.poll(Duration.ofMillis(200));

                for (ConsumerRecord<String, Tweet> tweet : messages) {
                    System.out.printf("[%s] %s (%s)\n", tweet.value().author(), tweet.value().text(), tweet.value().timestamp());
                }
            }
        }
    }

}
