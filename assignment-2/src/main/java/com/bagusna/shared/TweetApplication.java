package com.bagusna.shared;

import com.bagusna.shared.components.TweetCellBuilder;
import com.bagusna.shared.dto.Tweet;
import javafx.application.Application;
import javafx.beans.property.Property;
import javafx.beans.property.SimpleStringProperty;
import javafx.geometry.Insets;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.VBox;

abstract public class TweetApplication extends Application {
    protected ListView<Tweet> tweetListView;

    protected Property<String> author = new SimpleStringProperty("");
    protected TextField authorTextField;
    protected Property<String> messageDraft = new SimpleStringProperty("");
    protected TextArea messageDraftTextArea;
    protected Button sendButton;

    protected Scene buildUI() {
        tweetListView = new ListView<>();
        tweetListView.setPadding(new Insets(10));
        tweetListView.setCellFactory(param -> new TweetCellBuilder());

        ScrollPane scrollPane = new ScrollPane(tweetListView);
        scrollPane.setFitToWidth(true);
        scrollPane.setFitToHeight(true);

        authorTextField = new TextField();
        authorTextField.textProperty().bindBidirectional(author);
        messageDraftTextArea = new TextArea();
        messageDraftTextArea.textProperty().bindBidirectional(messageDraft);
        sendButton = new Button("Send");
        sendButton.setOnAction(event -> {
            onSend(messageDraft.getValue(), author.getValue());
        });

        VBox messageContainer = new VBox();
        messageContainer.setPadding(new Insets(10));
        messageContainer.setSpacing(8);
        messageContainer.getChildren().addAll(authorTextField, messageDraftTextArea, sendButton);

        BorderPane root = new BorderPane();
        root.setCenter(scrollPane);
        root.setBottom(messageContainer);

        return new Scene(root, 800, 600);
    }

    abstract protected void onSend(String message, String author);
}
