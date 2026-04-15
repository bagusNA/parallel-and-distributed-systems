FROM gradle:9.4-jdk25 AS build
WORKDIR /app
COPY . .
RUN gradle :services:order-service:bootJar :services:inventory-service:bootJar :services:notification-service:bootJar :services:analytics-service:bootJar --no-daemon --info --build-cache

FROM eclipse-temurin:25-jre
WORKDIR /app
COPY --from=build /app/services/order-service/build/libs/*.jar services/order-service/build/libs/
COPY --from=build /app/services/inventory-service/build/libs/*.jar services/inventory-service/build/libs/
COPY --from=build /app/services/notification-service/build/libs/*.jar services/notification-service/build/libs/
COPY --from=build /app/services/analytics-service/build/libs/*.jar services/analytics-service/build/libs/
# This will be overridden by the specific service
ENTRYPOINT ["java", "-jar", "app.jar"]
