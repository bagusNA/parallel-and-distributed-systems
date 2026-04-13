package com.bagusna.tugas1;

import com.bagusna.shared.utils.BenchmarkTime;
import com.bagusna.tugas1.components.ImageCellBuilder;
import com.bagusna.tugas1.components.ImageEntry;
import javafx.application.Application;
import javafx.application.Platform;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Scene;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.HBox;
import javafx.stage.DirectoryChooser;
import javafx.stage.Stage;

import java.io.File;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class ImageDatasetViewer extends Application {

    private ListView<ImageEntry> imageGrid;

//    private final int threadCount = 1;
     private final int threadCount = 8;

    private final ExecutorService executor = Executors.newFixedThreadPool(threadCount);

    private void queryImageFolder(Stage stage, Label elapsedTime, BenchmarkTime benchmarkTime) {
        DirectoryChooser dc = new DirectoryChooser();
        File selectedFolder = dc.showDialog(stage);

        if (selectedFolder == null) {
            return;
        }

        imageGrid.getItems().clear(); // Reset view

        File[] files = selectedFolder.listFiles((dir, name) ->
            name.toLowerCase().endsWith(".png") ||
            name.toLowerCase().endsWith(".jpg") ||
            name.toLowerCase().endsWith(".jpeg")
        );

        if (files == null || files.length == 0) {
            return;
        }

        benchmarkTime.startTime = System.currentTimeMillis();

        for (File file : files) {
            // Loader thread
            executor.submit(() -> {
                ImageEntry entry = new ImageEntry(
                        new Image(file.toURI().toString(), 200, 0, true, true),
                        file.getName(),
                        file.length()
                );

                // UI Thread
                Platform.runLater(() -> {
                    imageGrid.getItems().add(entry);

                    benchmarkTime.endTime = System.currentTimeMillis();
                    elapsedTime.setText(String.format("Elapsed time: %d ms", benchmarkTime.getDuration()));
                });
            });
        }

    }

    @Override
    public void start(Stage primaryStage) {
        BenchmarkTime benchmarkTime = new BenchmarkTime();

        // Init UI
        imageGrid = new ListView<ImageEntry>();
        imageGrid.setPadding(new Insets(15));
        imageGrid.setCellFactory(param -> new ImageCellBuilder());

        ScrollPane scrollPane = new ScrollPane(imageGrid);
        scrollPane.setFitToWidth(true); // Makes the grid resize with the window
        scrollPane.setFitToHeight(true);

        Label elapsedTime = new Label();
        Label threadCountLabel = new Label("Threads: " + threadCount);
        Button openBtn = new Button("Select Folder");
        openBtn.setOnAction(e -> queryImageFolder(primaryStage, elapsedTime, benchmarkTime));

        HBox hBox = new HBox(openBtn, threadCountLabel, elapsedTime);
        hBox.setSpacing(10);
        hBox.setPadding(new Insets(10));
        hBox.setAlignment(Pos.CENTER_LEFT);

        BorderPane root = new BorderPane();
        root.setTop(hBox);

        BorderPane.setMargin(openBtn, new Insets(10));
        root.setCenter(scrollPane);

        Scene scene = new Scene(root, 800, 600);
        primaryStage.setTitle("Image Dataset Viewer");
        primaryStage.setScene(scene);
        primaryStage.show();
    }

    public static void main(String[] args) {
        launch(args);
    }
}