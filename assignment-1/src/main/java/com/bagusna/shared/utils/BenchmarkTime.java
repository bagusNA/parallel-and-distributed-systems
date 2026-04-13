package com.bagusna.shared.utils;

public class BenchmarkTime {
    public long startTime;
    public long endTime;

    public BenchmarkTime() {
        this.startTime = 0;
        this.endTime = 0;
    }

    public long getDuration() {
        return this.endTime - this.startTime;
    }
}
