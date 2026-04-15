package com.bagusna.order;

import com.bagusna.shared.OrderCreatedEvent;
import io.grpc.stub.StreamObserver;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import net.devh.boot.grpc.server.service.GrpcService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.kafka.core.KafkaTemplate;

import java.util.UUID;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

@Slf4j
@GrpcService
@RequiredArgsConstructor
public class OrderGrpcServiceImpl extends OrderServiceGrpc.OrderServiceImplBase {

    @Autowired
    private final KafkaTemplate<String, Object> kafkaTemplate;
    private static final String TOPIC = "order-events";

    @Override
    public void placeOrder(PlaceOrderRequest request, StreamObserver<PlaceOrderResponse> responseObserver) {
        log.info("Received gRPC request build: {}", request);

        // Simulate logic: quantity > 100 fails
        String status = "SUCCESS";
        String orderId = UUID.randomUUID().toString();

        if (request.getQuantity() > 100) {
            status = "FAILED";
            orderId = "";
        }

        PlaceOrderResponse response = PlaceOrderResponse.newBuilder()
                .setOrderId(orderId)
                .setStatus(status)
                .build();

        // 1. Return response immediately (Sync)
        responseObserver.onNext(response);
        responseObserver.onCompleted();

        // 2. Publish event if success (Async)
        if ("SUCCESS".equals(status)) {
            OrderCreatedEvent event = OrderCreatedEvent.builder()
                    .orderId(orderId)
                    .userId(request.getUserId())
                    .itemId(request.getItemId())
                    .quantity(request.getQuantity())
                    .timestamp(System.currentTimeMillis())
                    .build();

            log.info("Publishing async event to Kafka: {}", event);

            try {
                kafkaTemplate.send(TOPIC, orderId, event).get(5, TimeUnit.SECONDS);
                log.info("SENT");
            } catch (ExecutionException | InterruptedException | TimeoutException e) {
                throw new RuntimeException(e);
            }
        }
    }
}
