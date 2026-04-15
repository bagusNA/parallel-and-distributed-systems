package com.bagusna.shared;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class OrderCreatedEvent {
    private final String event = "order_created";
    private String orderId;
    private String userId;
    private String itemId;
    private int quantity;
    private long timestamp;
}
