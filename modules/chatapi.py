import websocket
import requests
import json


class ChatApi:
    """
    Реализует работу с АПИ ГудГейма. Пока привязан к одному каналу без выбора.
    """
    def __init__(self, uname, passwd):
        """
        Инициализируем класс, создаем соединение с АПИ ГудГейма.
        :param uname: логин в формате string.
        :param passwd: пароль в формате string.
        """
        # Логин, пароль и токен(пока пустой)
        self.username = uname
        self.password = passwd
        self.token = ""

        # Получаем токен и ИД юзера, они нужны для авторизации в АПИ
        self.reg_url = 'https://goodgame.ru/ajax/chatlogin'
        self.token_req = requests.post(url=self.reg_url, data={
            'login': self.username,
            'password': self.password
        })
        self.token = self.token_req.json()["token"]
        self.user_id = self.token_req.json()["user_id"]

        # Соединияемся с АПИ, сразу же получаем ответ, который нам не нужен
        self.ws = websocket.WebSocket()
        self.ws.connect("wss://chat.goodgame.ru/chat/websocket")
        self.r = self.ws.recv()

        # Проходим аутентификацию
        self.ws.send(json.dumps({
            "type": "auth",
            "data": {
                "user_id": self.user_id,
                "token": self.token
            }
        }))
        self.r = self.ws.recv()

        # Получаем список топ50 каналов
        self.ws.send(json.dumps({
            "type": "get_channels_list",
            "data": {
                "start": 0,
                "count": 50
            }
        }))
        self.r = self.ws.recv()

        # Канал мне заранее известен, потому тут я его захардкодил
        self.ws.send(json.dumps(
            {
                "type": "join",
                "data": {
                    "channel_id": "55600",
                    "hidden": "false",
                }
            }
        ))
        self.r = self.ws.recv()

    def send(self, message):
        """
        Функция отправляющая сообщение в чат.
        :param message: Текст отправляемого сообщения в string.
        :return: Ответ от АПИ сервера.
        """
        self.ws.send(json.dumps({
            "type": "send_message",
            "data": {
                "channel_id": "55600",
                "text": message,
                "hideIcon": "false",
                "mobile": "false"
            }
        }))
        return self.recv()

    def recv(self):
        """
        Функция получения ответа от АПИ сервера.
        :return: Ответ от АПИ сервера.
        """
        self.r = self.ws.recv()
        return self.r

    def get_chat(self):
        """
        Получение истории сообщений чата.
        :return: JSON с сообщениями чата.
        """
        self.ws.send(json.dumps({
            "type": "get_channel_history",
            "data": {
                "channel_id": "55600"
            }
        }))
        self.r = json.loads(self.ws.recv())
        return self.r
