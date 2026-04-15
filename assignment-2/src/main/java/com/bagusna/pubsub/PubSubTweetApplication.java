package com.bagusna.pubsub;

import com.bagusna.pubsub.service.PubSubService;
import com.bagusna.shared.TweetApplication;
import com.bagusna.shared.dto.Tweet;
import javafx.application.Platform;
import javafx.scene.Scene;
import javafx.stage.Stage;
import net.datafaker.Faker;
import org.apache.kafka.clients.consumer.ConsumerRecord;
import org.apache.kafka.clients.consumer.ConsumerRecords;
import org.apache.kafka.clients.consumer.KafkaConsumer;
import org.apache.kafka.clients.producer.KafkaProducer;
import org.apache.kafka.clients.producer.ProducerRecord;

import java.time.Duration;
import java.util.List;

public class PubSubTweetApplication extends TweetApplication {
    private final Thread consumerThread;
    private final PubSubService<Tweet> pubSubService;
    private final KafkaConsumer<String, Tweet> consumer;
    private final KafkaProducer<String, Tweet> producer;

    public PubSubTweetApplication() {
        this.pubSubService = new PubSubService<>();
        this.consumer = pubSubService.getConsumer(new Faker().mountain().name().toLowerCase());
        this.producer = pubSubService.getProducer();

        this.consumerThread = new Thread(() -> {
            try (this.consumer) {
                consumer.subscribe(List.of(pubSubService.topic));

                while (true) {
                    ConsumerRecords<String, Tweet> tweets = consumer.poll(Duration.ofMillis(500));

                    Platform.runLater(() -> {
                        for (ConsumerRecord<String, Tweet> record : tweets) {
                            if (record.value() == null) continue;

                            tweetListView.getItems().add(record.value());
                            tweetListView.scrollTo(tweetListView.getItems().size() - 1);
                        }
                    });
                }
            }
        });

        this.consumerThread.start();
    }

    @Override
    public void start(Stage primaryStage) throws Exception {
        Scene ui = buildUI();

        primaryStage.setTitle("Pub-Sub Tweet");
        primaryStage.setScene(ui);
        primaryStage.show();
    }

    @Override
    protected void onSend(String message, String author) {
        Tweet tweet = new Tweet(message, author);
        ProducerRecord<String, Tweet> record = new ProducerRecord<>(pubSubService.topic, tweet);
        producer.send(record);
    }

    public static void main(String[] args) {
        launch(args);
    }
}
