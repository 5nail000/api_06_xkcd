# Скрипт для публикации комиксов XKCD во ВКОНТАКТЕ
Скрипт отправляет на стену в ВК, случайный комикс от **xkdc.com**

![jpg](https://telegra.ph/file/2dfaa36a1b91b1f1eedb9.jpg)

## УСТАНОВКА

Для запуска скрипта у вас уже должен быть установлен Python 3.

- Скачайте код
- Установите зависимости командой:
```
pip install -r requirements.txt
```

## НАСТРОЙКА 
.ENV (Переменные Окружения)
 - VK_ACCESS_TOKEN - Токен доступа https://vk.com/dev/implicit_flow_user
 - VK_WALL_ID - Номер стены, для публикаций(должен быть доступ) https://regvk.com/id/

## ЗАПУСК

- Запустите скрипт командой: 
```
py xkdc2vk.py
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
