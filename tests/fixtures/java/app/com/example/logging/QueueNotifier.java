package com.example.logging;

import software.amazon.awssdk.services.sqs.SqsClient;

public class QueueNotifier {
    private final SqsClient sqs = SqsClient.create();

    public void notify(String body) {
        sqs.sendMessage("https://sqs.example/queue", body);
    }
}
