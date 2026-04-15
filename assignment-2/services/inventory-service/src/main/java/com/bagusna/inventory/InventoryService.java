package com.bagusna.inventory;

import com.bagusna.shared.OrderCreatedEvent;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.kafka.clients.admin.NewTopic;
import org.springframework.context.annotation.Bean;
import org.springframework.kafka.annotation.KafkaListener;
import org.springframework.kafka.config.TopicBuilder;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;
import tools.jackson.databind.ObjectMapper;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Slf4j
@Service
@Component
@RequiredArgsConstructor
public class InventoryService {

    private final InventoryWebSocketHandler webSocketHandler;
    private final ObjectMapper objectMapper;
    
    // Initial stock
    private final Map<String, Integer> stock = new ConcurrentHashMap<>(Map.of(
            "item_1", 100,
            "item_2", 100,
            "item_3", 100
    ));

    @Bean
    public NewTopic orderEventTopic() {
        return TopicBuilder.name("order-events")
                .partitions(1)
                .replicas(1)
                .build();
    }

    @KafkaListener(topics = "order-events", groupId = "inventory-group")
    public void handleOrderCreated(OrderCreatedEvent event) throws Exception {
        log.info("Received order event in Inventory: {}", event);

        // Update stock
        stock.computeIfPresent(event.getItemId(), (id, current) -> Math.max(0, current - event.getQuantity()));

        // Push update to frontend
        Map<String, Object> update = new HashMap<>();
        update.put("type", "STOCK_UPDATE");
        update.put("stock", stock);
        update.put("processed_timestamp", System.currentTimeMillis());
        update.put("event_timestamp", event.getTimestamp());
        update.put("order_id", event.getOrderId());

        webSocketHandler.broadcast(objectMapper.writeValueAsString(update));
    }
}
