package software.amazon.awssdk.services.dynamodb;

public interface DynamoDbClient {
    static DynamoDbClient create() {
        return null;
    }

    String getItem(String table, String key);

    void putItem(String table, String item);
}
