package com.bagusna.order;

import com.bagusna.order.PlaceOrderRequest;
import com.bagusna.order.PlaceOrderResponse;
import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import lombok.Data;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/orders")
@CrossOrigin(origins = "*")
public class OrderRestController {

    private final OrderGrpcServiceImpl grpcService;

    public OrderRestController(OrderGrpcServiceImpl grpcService) {
        this.grpcService = grpcService;
    }

    @PostMapping
    public OrderResponse placeOrder(@RequestBody OrderRequest request) {
        // We simulate the client side gRPC call here
        // In a real system, the frontend would use gRPC-Web or a Gateway
        // For this demo, this REST call is the "Sync Request" portal
        
        PlaceOrderRequest grpcRequest = PlaceOrderRequest.newBuilder()
                .setUserId(request.getUserId())
                .setItemId(request.getItemId())
                .setQuantity(request.getQuantity())
                .build();

        // Local call for simplicity, but behaves like a sync gRPC call
        final OrderResponse response = new OrderResponse();
        
        grpcService.placeOrder(grpcRequest, new io.grpc.stub.StreamObserver<PlaceOrderResponse>() {
            @Override
            public void onNext(PlaceOrderResponse value) {
                response.setOrderId(value.getOrderId());
                response.setStatus(value.getStatus());
            }

            @Override
            public void onError(Throwable t) {
                response.setStatus("ERROR");
            }

            @Override
            public void onCompleted() {}
        });

        return response;
    }

    @Data
    public static class OrderRequest {
        private String userId;
        private String itemId;
        private int quantity;
    }

    @Data
    public static class OrderResponse {
        private String orderId;
        private String status;
    }
}
