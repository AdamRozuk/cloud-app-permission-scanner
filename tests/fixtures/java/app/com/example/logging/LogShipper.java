package com.example.logging;

import software.amazon.awssdk.services.cloudwatchlogs.CloudWatchLogsClient;

public class LogShipper {
    private final CloudWatchLogsClient logs = CloudWatchLogsClient.create();

    public void ship(String message) {
        logs.putLogEvents("app", "main", message);
    }
}
