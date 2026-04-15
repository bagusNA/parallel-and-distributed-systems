package com.bagusna.pubsub;

import com.bagusna.pubsub.service.PubSubService;
import com.bagusna.shared.dto.Tweet;
import com.bagusna.shared.service.TweetService;
import org.apache.kafka.clients.producer.*;

import java.util.concurrent.TimeUnit;

public class Publisher {
    private static final String topic = "tweets";

    static void main() throws InterruptedException {
        TweetService tweetService = new TweetService();
        PubSubService<Tweet> pubSubService = new PubSubService<>();

        KafkaProducer<String, Tweet> producer = pubSubService.getProducer();

        try (producer) {
            while (true) {
                Tweet tweet = tweetService.createRandomTweet();

                ProducerRecord<String, Tweet> data = new ProducerRecord<>(topic, tweet);
                producer.send(data);

                System.out.println("Sent: " + tweet.text());
                TimeUnit.SECONDS.sleep(2);
            }
        }
    }
}
