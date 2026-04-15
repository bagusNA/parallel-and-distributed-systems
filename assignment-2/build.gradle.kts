plugins {
    id("java")
    id("io.freefair.lombok") version "9.2.0"
}

group = "com.bagusna"
version = "1.0-SNAPSHOT"

repositories {
    mavenCentral()
}

dependencies {
    implementation("org.apache.kafka:kafka-streams:4.2.0")
    implementation("tools.jackson.core:jackson-databind:3.1.2")
    implementation("net.datafaker:datafaker:2.5.4")
    testImplementation(platform("org.junit:junit-bom:6.0.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

tasks.test {
    useJUnitPlatform()
}