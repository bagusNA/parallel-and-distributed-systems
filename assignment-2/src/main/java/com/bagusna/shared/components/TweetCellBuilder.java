package com.bagusna.shared.components;

import com.bagusna.shared.dto.Tweet;
import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.control.ListCell;
import javafx.scene.layout.VBox;
import javafx.scene.text.Font;
import javafx.scene.text.FontWeight;

public class TweetCellBuilder extends ListCell<Tweet> {
    private final VBox container = new VBox();
    private final Label usernameLabel = new Label();
    private final Label contentLabel = new Label();

    @Override
    public void updateItem(Tweet tweet, boolean empty) {
        super.updateItem(tweet, empty);

        if (empty || tweet == null) {
            setText(null);
            setGraphic(null);
        }
        else {
            usernameLabel.setFont(Font.font("System",  FontWeight.BOLD, 14));
            usernameLabel.setText(tweet.author());
            contentLabel.setText(tweet.text());

            container.setAlignment(Pos.CENTER_LEFT);
            container.setSpacing(8);
            container.getChildren().setAll(usernameLabel, contentLabel);

            setGraphic(container);
        }

    }
}
