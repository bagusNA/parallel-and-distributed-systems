package com.bagusna.analytics;

import com.bagusna.shared.OrderCreatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.annotation.TopicPartition;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicLong;

@Slf4j
@Service
@RequiredArgsConstructor
public class AnalyticsService {

    private final AnalyticsWebSocketHandler webSocketHandler;
    private final ObjectMapper objectMapper;
    
    private final AtomicLong totalOrders = new AtomicLong(0);
    private final Map<String, Long> itemCounts = new ConcurrentHashMap<>();

    @Bean
    public NewTopic orderEventTopic() {
        return TopicBuilder.name("order-events")
                .partitions(1)
                .replicas(1)
                .build();
    }

    @KafkaListener(topicPartitions = { @TopicPartition(topic = "order-events", partitions = "0") })
    public void handleOrderCreated(OrderCreatedEvent event) throws Exception {
        log.info("Updating analytics for order: {}", event.getOrderId());

        totalOrders.incrementAndGet();
        itemCounts.merge(event.getItemId(), (long) event.getQuantity(), Long::sum);

        // Push update to frontend
        Map<String, Object> update = new HashMap<>();
        update.put("type", "ANALYTICS_UPDATE");
        update.put("total_orders", totalOrders.get());
        update.put("item_counts", itemCounts);
        update.put("order_id", event.getOrderId());
        update.put("processed_timestamp", System.currentTimeMillis());
        update.put("event_timestamp", event.getTimestamp());

        webSocketHandler.broadcast(objectMapper.writeValueAsString(update));
    }
}
