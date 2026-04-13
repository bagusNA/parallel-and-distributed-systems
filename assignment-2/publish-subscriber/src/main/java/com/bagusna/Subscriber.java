package com.bagusna;

import org.apache.kafka.clients.consumer.ConsumerConfig;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.common.serialization.StringDeserializer;

import java.time.Duration;
import java.util.List;
import java.util.Properties;

public class Subscriber {
    private static final String topic = "demo";

    static void main() {
        KafkaConsumer<String, String> consumer = getConsumer();

        try (consumer) {
            consumer.subscribe(List.of(topic));

            while (true) {
                ConsumerRecords<String, String> messages = consumer.poll(Duration.ofMillis(200));

                for (ConsumerRecord<String, String> record : messages) {
                    System.out.printf("[%s] %s\n", record.topic(), record.value());
                }
            }
        }
    }

    private static KafkaConsumer<String, String> getConsumer() {
        Properties props = new Properties();
        props.setProperty(ConsumerConfig.BOOTSTRAP_SERVERS_CONFIG, "localhost:9092");
        props.setProperty(ConsumerConfig.KEY_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.setProperty(ConsumerConfig.VALUE_DESERIALIZER_CLASS_CONFIG, StringDeserializer.class.getName());
        props.setProperty(ConsumerConfig.GROUP_ID_CONFIG, "consumer_group");
        props.setProperty(ConsumerConfig.AUTO_OFFSET_RESET_CONFIG, "earliest");

        return new KafkaConsumer<>(props);
    }
}
