# Aeza Assistant

Aeza Assistant is a Telegram bot that notifies about changes in location sales in the Aeza hosting service. The bot can be run using a Docker Compose file, which is located in the root folder of the repository.

## Prerequisites

Before running Aeza Assistant, you need to have Docker and Docker Compose installed on your system. If you don't have them installed, please follow the instructions at <https://docs.docker.com/get-docker/> and <https://docs.docker.com/compose/install/> to install them.

## Getting Started

1. Clone the repository using the following command:

  ```bash
  git clone https://github.com/cofob/aeza-assistant.git
  ```

2. Go to the root folder of the repository:

  ```bash
  cd aeza-assistant
  ```

3. Open the docker-compose.yml file in a text editor.
4. Replace the value of the TOKEN environment variable with your Telegram bot token. You can get a bot token by talking to the [BotFather](https://t.me/BotFather).
5. If you want to receive push notifications on Uptime Kuma, you can set the PUSH_ADDRESSES environment variable to a comma-separated list of push addresses. The format is as follows:

  ```text
  PUSH_ADDRESSES='EPs | https://uptime-kuma/api/push/1234 , VIEs | https://uptime-kuma/api/push/5678'
  ```

  The above example adds two push addresses: `https://uptime-kuma/api/push/1234` with the label EPs and `https://uptime-kuma/api/push/5678` with the label VIEs. If you don't want to receive push notifications, you can skip this step.

6. Save and close the docker-compose.yml file.
7. Run the following command to start Aeza Assistant:

  ```bash
  docker-compose up -d
  ```

  This will start the Docker container in detached mode, which means it will run in the background.

8. You can now interact with Aeza Assistant by sending messages to your Telegram bot.

## Using the Tor network

If you want to use Aeza Assistant through the Tor network, you can use the `ghcr.io/cofob/aeza-assistant:torsocks` Docker image instead of the default image. To use this image, follow the same steps as above, but replace the image field in the docker-compose.yml file with the following:

```yaml
image: ghcr.io/cofob/aeza-assistant:torsocks
```

**Why do we need the Tor version?** The reason is that Aeza blocks connections to its API from its own servers, so you need to use a different IP, such as the one from Tor.

## Conclusion

Congratulations! You have successfully set up Aeza Assistant and can now receive notifications about changes in location sales in the Aeza hosting service. If you have any questions or feedback, please feel free to reach out to the developers at [issues](https://github.com/cofob/aeza-assistant/issues).
