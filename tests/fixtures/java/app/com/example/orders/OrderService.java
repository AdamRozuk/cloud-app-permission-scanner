package com.example.orders;

import software.amazon.awssdk.services.dynamodb.DynamoDbClient;
import software.amazon.awssdk.services.s3.S3Client;

public class OrderService {
    private final S3Client s3 = S3Client.create();
    private final DynamoDbClient dynamo = DynamoDbClient.create();

    public String load(String id) {
        String order = dynamo.getItem("orders", id);
        String invoice = s3.getObject("invoices", id);
        return order + invoice;
    }

    public void save(String id, String body) {
        dynamo.putItem("orders", body);
        s3.putObject("invoices", id, body);
    }

    public String listInvoices() {
        return s3.listObjectsV2("invoices");
    }

    public void shutdown() {
        s3.close();
    }
}
