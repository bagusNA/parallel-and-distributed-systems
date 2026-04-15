package com.bagusna.notification;

import com.bagusna.shared.OrderCreatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.RetryableTopic;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.kafka.retrytopic.TopicSuffixingStrategy;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.Map;
import java.util.Random;

@Slf4j
@Service
@RequiredArgsConstructor
public class NotificationService {

    private final NotificationWebSocketHandler webSocketHandler;
    private final ObjectMapper objectMapper;
    private final Random random = new Random();

    @Bean
    public NewTopic orderEventTopic() {
        return TopicBuilder.name("order-events")
                .partitions(1)
                .replicas(1)
                .build();
    }

    @RetryableTopic(
            attempts = "3",
            topicSuffixingStrategy = TopicSuffixingStrategy.SUFFIX_WITH_INDEX_VALUE)
    @KafkaListener(topics = "order-events", groupId = "notification-group")
    public void handleOrderCreated(OrderCreatedEvent event) throws Exception {
        log.info("Processing notification for order: {}", event.getOrderId());

        // Simulate 20% failure
        if (random.nextInt(100) < 20) {
            log.error("Simulated notification failure for order: {}", event.getOrderId());
            broadcastLog(event, "FAILURE", "Simulated email server delay/failure. Retrying...");
            throw new RuntimeException("Failed to send notification");
        }

        // Simulate "sending" email
        Thread.sleep(1000);
        log.info("Notification sent for order: {}", event.getOrderId());
        broadcastLog(event, "SUCCESS", "Email sent to user " + event.getUserId());
    }

    private void broadcastLog(OrderCreatedEvent event, String status, String detail) throws Exception {
        Map<String, Object> update = new HashMap<>();
        update.put("type", "NOTIFICATION_LOG");
        update.put("order_id", event.getOrderId());
        update.put("status", status);
        update.put("detail", detail);
        update.put("processed_timestamp", System.currentTimeMillis());
        update.put("event_timestamp", event.getTimestamp());

        webSocketHandler.broadcast(objectMapper.writeValueAsString(update));
    }
}
