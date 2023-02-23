# aeza-assistant

Бот-ассистент для получения уведомлений о локациях в телеграм.

## Инструкция по запуску проекта через docker-compose

Для запуска проекта через docker-compose необходимо выполнить следующие шаги:

1. [Установить Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/), если они еще не установлены.
2. Склонировать репозиторий с проектом на свой локальный компьютер:

```bash
git clone https://github.com/cofob/aeza-assistant
```

3. Перейти в папку проекта:

```bash
cd aeza-assistant
```

4. Открыть файл *docker-compose.yml* в текстовом редакторе и изменить строчку с переменной TOKEN на токен вашего телеграм бота.

```
    environment:
      TOKEN: {telegram_bot_token}
```

5. Запустить проект командой:

```yml
docker-compose up
```

6. Если всё прошло успешно, то вы увидите в консоли сообщение о том, что бот запущен и готов к работе.

Готово! Вы успешно запустили проект через docker-compose.
