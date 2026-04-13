package com.bagusna.tugas1.components;

import javafx.scene.image.Image;

public class ImageEntry {
    public Image image;
    public String fileName;
    public long size;

    public ImageEntry(Image image, String fileName, long size) {
        this.image = image;
        this.fileName = fileName;
        this.size = size;
    }
}
