function orderSystem() {
    return {
        processing: false,
        orderForm: {
            userId: 'user_' + Math.floor(Math.random() * 1000),
            itemId: 'item_1',
            quantity: 1
        },
        lastResponse: null,
        wsStatus: {
            inventory: false,
            notification: false,
            analytics: false
        },
        stock: {
            item_1: 100,
            item_2: 100,
            item_3: 100
        },
        notificationLogs: [],
        stats: {
            total: 0,
            items: {}
        },
        events: [],
        timeline: [],
        
        init() {
            this.connectWebSockets();
        },

        connectWebSockets() {
            const connect = (service, port, path, statusKey) => {
                const ws = new WebSocket(`ws://localhost:${port}${path}`);
                ws.onopen = () => this.wsStatus[statusKey] = true;
                ws.onclose = () => {
                    this.wsStatus[statusKey] = false;
                    setTimeout(() => connect(service, port, path, statusKey), 5000);
                };
                ws.onmessage = (msg) => this.handleMessage(statusKey, JSON.parse(msg.data));
            };

            connect('Inventory', 8081, '/ws/inventory', 'inventory');
            connect('Notification', 8082, '/ws/notifications', 'notification');
            connect('Analytics', 8083, '/ws/analytics', 'analytics');
        },

        handleMessage(source, data) {
            console.log(`Msg from ${source}:`, data);
            
            if (data.type === 'STOCK_UPDATE') {
                this.stock = data.stock;
                this.recordTimeline(data.order_id, data.event_timestamp, data.processed_timestamp, 'inventory');
            } else if (data.type === 'NOTIFICATION_LOG') {
                this.notificationLogs.unshift({
                    id: Date.now() + Math.random(),
                    status: data.status,
                    detail: data.detail,
                    time: new Date().toLocaleTimeString()
                });
                if (this.notificationLogs.length > 20) this.notificationLogs.pop();
                this.recordTimeline(data.order_id, data.event_timestamp, data.processed_timestamp, 'notification');
            } else if (data.type === 'ANALYTICS_UPDATE') {
                this.stats.total = data.total_orders;
                this.stats.items = data.item_counts;
                this.recordTimeline(data.order_id, data.event_timestamp, data.processed_timestamp, 'analytics');
            }
        },

        async placeOrder() {
            this.processing = true;
            const startTime = Date.now();
            
            try {
                const response = await fetch('http://localhost:8084/api/orders', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.orderForm)
                });
                
                const result = await response.json();
                const endTime = Date.now();
                
                this.lastResponse = {
                    orderId: result.orderId,
                    status: result.status,
                    latency: endTime - startTime
                };
                
                if (result.status === 'SUCCESS') {
                    // Create visual event
                    this.triggerEventAnimation(result.orderId);
                    
                    // Add initial timeline entry
                    this.timeline.push({
                        orderId: result.orderId,
                        grpcDuration: Math.min(this.lastResponse.latency * 2, 100), // Scaled for vis
                        asyncStart: 120, // Offset for broker delay
                        asyncDuration: 0
                    });
                }
            } catch (err) {
                console.error(err);
                this.lastResponse = { status: 'FAILED', orderId: 'SERVER ERROR', latency: 0 };
            } finally {
                this.processing = false;
            }
        },

        async placeOrderBlocking() {
            this.processing = true;
            const startTime = Date.now();
            
            try {
                const response = await fetch('http://localhost:8084/api/orders/blocking', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(this.orderForm)
                });
                
                const result = await response.json();
                const endTime = Date.now();
                
                this.lastResponse = {
                    orderId: result.orderId,
                    status: result.status,
                    latency: endTime - startTime
                };
                
                if (result.status === 'SUCCESS') {
                    // In blocking, we don't trigger the "flow" animation until response returns
                    // to emphasize that the client was waiting
                    this.triggerEventAnimation(result.orderId);
                    
                    // Add single long blocking bar to timeline
                    this.timeline.push({
                        orderId: result.orderId,
                        grpcDuration: 0, 
                        isBlocking: true,
                        blockingDuration: (endTime - startTime) / 10 // Scaled
                    });
                }
            } catch (err) {
                console.error(err);
                this.lastResponse = { status: 'FAILED', orderId: 'SERVER ERROR', latency: 0 };
            } finally {
                this.processing = false;
            }
        },

        triggerEventAnimation(orderId) {
            const id = Date.now();
            this.events.push({
                id: id,
                orderId: orderId,
                speed: 3 + Math.random() * 2
            });
        },

        removeEvent(id) {
            this.events = this.events.filter(e => e.id !== id);
        },

        recordTimeline(orderId, startTs, endTs, type) {
            const entry = this.timeline.find(t => t.orderId === orderId);
            if (entry) {
                const duration = (endTs - startTs) / 10; // Scaled
                entry.asyncDuration = Math.max(entry.asyncDuration, duration);
            }
        }
    };
}
