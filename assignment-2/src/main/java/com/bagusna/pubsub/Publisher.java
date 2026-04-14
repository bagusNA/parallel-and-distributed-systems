package com.bagusna.pubsub;

import org.apache.kafka.clients.producer.*;
import org.apache.kafka.common.serialization.StringSerializer;

import java.time.LocalDateTime;
import java.util.Properties;
import java.util.concurrent.TimeUnit;

public class Publisher {
    static void main() throws InterruptedException {
        KafkaProducer<String, String> producer = getProducer();

        try (producer) {
            while (true) {
                LocalDateTime now = LocalDateTime.now();

                ProducerRecord<String, String> data = new ProducerRecord<>("demo", now.toString());
                producer.send(data);

                System.out.println("Sent: " + now);
                TimeUnit.SECONDS.sleep(2);
            }
        }
    }

    private static KafkaProducer<String, String> getProducer() {
        Properties properties = new Properties();
        properties.setProperty(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        properties.setProperty(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        properties.setProperty(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());

        return new KafkaProducer<>(properties);
    }
}
