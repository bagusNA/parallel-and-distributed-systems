plugins {
    id("org.springframework.boot") version "4.0.4"
    id("io.spring.dependency-management") version "1.1.7"
}

dependencies {
    implementation(project(":shared"))

    implementation("org.springframework.boot:spring-boot-starter-web:4.0.4")
    implementation("org.springframework.kafka:spring-kafka:4.0.4")

    implementation("net.devh:grpc-server-spring-boot-starter:3.1.0.RELEASE")
    implementation("tools.jackson.core:jackson-databind:3.1.2")
}

tasks.bootJar {
    enabled = true
}

tasks.jar {
    enabled = true
}
