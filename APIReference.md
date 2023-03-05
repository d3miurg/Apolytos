**Любой ответ от сервера построен по следующей форме:**

	{
	"status": Может быть 0 (ошибка запроса) или 1 (успех)
	"reason": Всегда описывает результат запроса. При ошибке описывает её причину
	и дополнительная информация в зависимости от запроса
	}

*Далее standart_responce*

---

### /

Показывает статус API

>**Доступные методы:**
>
> - GET
>
>**Запрос:**
>
	{
	}
>
>**Ответ:** 
>
	{
	standart_responce
	}

---

### /login

Вход на сайт

>**Доступные методы:**
>
> - GET
>
>**Запрос:**
>
	?username=имя пользователя&password=пароль
>
>**Ответ:** 
>
	{
	standart_responce
	"auth_token": токен идентификации
	"refresh_token": токен обновления
	}

---

### /register

Регистрация на сайте

>**Доступные методы:**
>
> - POST
>
>**Запрос:**
>
	{
	"username": имя пользователя
	"password": пароль
	"slug": уникальная ссылка пользователя
	}
>
>**Ответ:** 
>
	{
	standart_responce
	}

---

### /chats

Базовая страница для чатов. Возвращает список всех чатов

>**Доступные методы:**
>
> - GET
>
>**Запрос:**
>
	{
	}
>
>**Ответ:**
> 
	{
	standart_responce,
	"chatlist": спикок уникальных ссылок чатов
	}

---

### /chats/%slug%

Страница чата с уникальной ссылкой *slug*

>**Доступные методы:**
>
> - GET
>
> - POST
>
>**Запрос:**
>
	?count=количество сообщений, которое необходимо вернуть
	или
	{
	"token": токен идентификации
	"content": содержание сообщения
	}
>
>**Ответ:**
>
	{
	standart_responce
	"last_messages": последние сообщения
	}
	или
	{
	standart_responce
	}