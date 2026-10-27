package software.amazon.awssdk.services.sqs;

public interface SqsClient {
    static SqsClient create() {
        return null;
    }

    void sendMessage(String queueUrl, String body);
}
