// THIS IS JUST AN INTUITION CODE ON HOW TO SEND THE REQUESTS..... ACTUAL TESTS USING MICROCONTROLLERS HAS NOT BEEN DONE

#include <WiFi.h>
#include <HTTPClient.h>
#include <driver/i2s.h>

// ====== Wi-Fi Credentials ======
const char *ssid = "YOUR_SSID";
const char *password = "YOUR_PASSWORD";

// ====== Server URL ======
const char *serverURL = "http://localhost:8000/convert";

// ====== I2S Configuration ======
#define I2S_SAMPLE_RATE 16000
#define I2S_BUFFER_SIZE 16000 // 1 second buffer
#define I2S_MIC_CHANNEL I2S_CHANNEL_FMT_ONLY_RIGHT
#define I2S_PORT I2S_NUM_0

// ====== I2S Pin Config (adjust to your wiring) ======
const i2s_config_t i2s_config = {
    .mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX | I2S_MODE_TX),
    .sample_rate = I2S_SAMPLE_RATE,
    .bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT,
    .channel_format = I2S_MIC_CHANNEL,
    .communication_format = I2S_COMM_FORMAT_I2S,
    .intr_alloc_flags = ESP_INTR_FLAG_LEVEL1,
    .dma_buf_count = 8,
    .dma_buf_len = 512,
    .use_apll = false};

const i2s_pin_config_t pin_config = {
    .bck_io_num = 26,   // Bit Clock
    .ws_io_num = 25,    // Word Select / LRCK
    .data_out_num = 22, // For speaker (DAC)
    .data_in_num = 23   // For mic input
};

void setup()
{
    Serial.begin(115200);

    // Connect to Wi-Fi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\nWiFi connected!");

    // Setup I2S
    i2s_driver_install(I2S_PORT, &i2s_config, 0, NULL);
    i2s_set_pin(I2S_PORT, &pin_config);
    i2s_zero_dma_buffer(I2S_PORT);
}

void loop()
{
    // 1. Record audio from mic
    uint8_t audioData[I2S_BUFFER_SIZE];
    size_t bytesRead;
    i2s_read(I2S_PORT, audioData, I2S_BUFFER_SIZE, &bytesRead, portMAX_DELAY);

    Serial.println("Sending audio to server...");

    // 2. Send POST request
    HTTPClient http;
    http.begin(serverURL);
    http.addHeader("Content-Type", "application/octet-stream");

    int httpResponseCode = http.POST(audioData, bytesRead);

    if (httpResponseCode == 200)
    {
        Serial.println("Response received! Playing audio...");

        WiFiClient *stream = http.getStreamPtr();
        uint8_t buf[512];
        while (stream->available())
        {
            int len = stream->read(buf, sizeof(buf));
            i2s_write_bytes(I2S_PORT, (const char *)buf, len, portMAX_DELAY);
        }
    }
    else
    {
        Serial.print("Failed, HTTP code: ");
        Serial.println(httpResponseCode);
    }

    http.end();

    delay(5000); // Wait before next interaction
}
