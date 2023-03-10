/ [GET](#mainget)
 /auth [GET](#authget) [POST](#authpost)
 /chats [GET](#chatsget) [POST](#chatspost) [PUT](#chatsput)
  /chats/{slug} [GET](#chatsslugget) [POST](#chatsslugpost)

**Любой ответ от сервера построен по следующей форме:**

	{
	"status": Может быть 0 (ошибка запроса) или 1 (успех)
	"reason": Всегда описывает результат запроса. При ошибке описывает её причину
	и дополнительная информация в зависимости от запроса
	}

*Далее standart_responce*

---

### /

Базовый ресурс

><a name="mainget"></a>**GET** - получить информацию об API
>
	{
	}
>
>**Ответ:** 
>
	{
	standart_responce
	"version": версия API
	"stack": технологический стек сервера
	}

---

### /auth

Ресурс входа

><a name="authget"></a>**GET** - войти
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
>
><a name="authpost"></a>**POST** - зарегистрироваться
>
	{
	"username": имя пользователя
	"password": пароль (желательно использовать SHA256)
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

Ресурс чатов

><a name="chatsget"></a>**GET** - получить список чатов
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
>
><a name="chatspost"></a>**POST** - создать чат
>
	{
	"token": токен идентификации
	"name": имя чата
	"slug": уникальная ссылка чата
	}
>
>**Ответ:**
> 
	{
	standart_responce,
	}
>
><a name="chatsput"></a>**PUT** - войти в чат
>
	{
	"token": токен идентификации
	"slug": уникальная ссылка чата
	}
>
>**Ответ:**
> 
	{
	standart_responce,
	}

---

### /chats/{slug}

Ресурс чата с уникальной ссылкой *slug*

><a name="chatsslugget"></a>**GET** - получить последние сообщения
>
	?count=количество сообщений, которое необходимо вернуть
>
>**Ответ:**
>
	{
	standart_responce
	"last_messages": последние сообщения
	}
>
><a name="chatsslugpost"></a>**POST** - отправить сообщение
>
	{
	"token": токен идентификации
	"content": содержание сообщения
	}
>
>**Ответ:**
>
	{
	standart_responce
	}
