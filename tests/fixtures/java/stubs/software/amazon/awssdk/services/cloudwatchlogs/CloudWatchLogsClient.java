package software.amazon.awssdk.services.cloudwatchlogs;

public interface CloudWatchLogsClient {
    static CloudWatchLogsClient create() {
        return null;
    }

    void putLogEvents(String group, String stream, String message);
}
