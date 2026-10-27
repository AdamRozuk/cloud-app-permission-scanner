package software.amazon.awssdk.services.s3;

public interface S3Client extends AutoCloseable {
    static S3Client create() {
        return null;
    }

    String getObject(String bucket, String key);

    void putObject(String bucket, String key, String body);

    void deleteObject(String bucket, String key);

    String listObjectsV2(String bucket);

    @Override
    void close();
}
