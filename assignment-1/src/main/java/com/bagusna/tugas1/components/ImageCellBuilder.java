package com.bagusna.tugas1.components;

import javafx.geometry.Pos;
import javafx.scene.control.Label;
import javafx.scene.control.ListCell;
import javafx.scene.image.ImageView;
import javafx.scene.layout.HBox;
import javafx.scene.layout.VBox;

import static com.bagusna.shared.utils.StringHelper.humanReadableByteCountSI;

public class ImageCellBuilder extends ListCell<ImageEntry> {
    private final HBox container = new HBox();
    private final VBox labelContainer = new VBox();
    private final ImageView imageView = new ImageView();
    private final Label nameLabel = new Label();
    private final Label sizeLabel = new Label();

    @Override
    public void updateItem(ImageEntry image, boolean empty) {
        super.updateItem(image, empty);

        if (empty || image == null) {
            setText(null);
            setGraphic(null);
        }
        else {
            imageView.setImage(image.image);
            nameLabel.setText(image.fileName);
            sizeLabel.setText(humanReadableByteCountSI(image.size));

            labelContainer.setAlignment(Pos.CENTER_LEFT);
            labelContainer.setSpacing(5);
            labelContainer.getChildren().setAll(nameLabel, sizeLabel);

            container.setAlignment(Pos.CENTER_LEFT);
            container.setSpacing(10);
            container.getChildren().setAll(imageView, labelContainer);

            setGraphic(container);
        }

    }
}
