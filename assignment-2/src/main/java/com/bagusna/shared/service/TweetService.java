package com.bagusna.shared.service;

import com.bagusna.shared.dto.Tweet;
import net.datafaker.Faker;

public class TweetService {
    private final Faker faker;

    public TweetService() {
        this.faker = new Faker();
    }

    public Tweet createRandomTweet() {
        return new Tweet(faker.bigBangTheory().quote(), faker.credentials().username());
    }
}
