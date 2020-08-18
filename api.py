import dialogflow
import os
from time import sleep
from google.api_core.exceptions import InvalidArgument
from modules.anekdot import Anekdot
from modules.chatapi import ChatApi
from modules.horoscope import Horoscope


class GGBot:
    """
    Класс бота для ГудГейма.
    """
    def __init__(self):
        # Креденшлы для логина в АПИ
        self.username = ''
        self.password = ''

        # Хрень нужная для инициализации АПИ говорилки от Гугла (чтобы бот был не максимально тупой).
        # В переменных окружения нужен путь (прямой или относительный) до ключа АПИ Dialogflow.
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'botfather-tcqy-1e34d2071dd8.json'
        self.DIALOGFLOW_PROJECT_ID = 'botfather-tcqy'
        self.DIALOGFLOW_LANGUAGE_CODE = 'ru'
        self.SESSION_ID = 'GoodGame'

        # Создание сессии к АПИ говорилки.
        self.session_client = dialogflow.SessionsClient()
        self.session = self.session_client.session_path(self.DIALOGFLOW_PROJECT_ID, self.SESSION_ID)

        # Инициализация класса для ГГ, анекдотов и гороскопов.
        self.t = ChatApi(self.username, self.password)
        self.anekdot = Anekdot()
        self.h = Horoscope()

        # Получаем полную историю чата, чтобы бот не отвечал на старые сообщения.
        # Приветствуем пацанов в чате.
        self.chat_history = {"type": ""}
        while "channel_history" != self.chat_history["type"]:
            self.chat_history = self.t.get_chat()
        self.timestamp = self.chat_history["data"]["messages"][-1]["timestamp"]
        self.t.send("Всем чмоке в етом чати! Ребята, я умею рассказывать анекдоты и запиливать гороскопы.")

    def run(self):
        """
        Бесконечный цикл парсинга новых сообщений, который лучше бы переписать на asyncio...
        """
        while True:
            # Печатаем три точки, чтобы в консоли палить итерации.
            print("...")
            # Получаем чат.
            chat = self.t.get_chat()
            # В любой момент АПИ чата может отправить ненужный нам ответ, потому смотрим, является ли ответ историей.
            if chat["type"] == "channel_history":
                # Выдергиваем сообщения
                msgs = chat["data"]["messages"]
                # Смотрим каждое сообщение...
                for msg in msgs:
                    # Тут захардкожено имя бота, чтобы понимать, что к нему обратились.
                    # Надо будет расхардкодить...
                    # Если обращаются к боту, сообщение не старое, и это не свое сообщение, то
                    if "bene4ka" in msg["text"] \
                            and int(self.timestamp) < int(msg["timestamp"]) \
                            and msg["user_name"] != "bene4ka":
                        # Создаем строку сообщения
                        msg_4me = msg["text"].replace("bene4ka, ", "")
                        # Если там есть слово анекдот - рассказываем анекдот.
                        if "анекдот" in msg_4me:
                            anekdot = self.anekdot.get_anekdot()
                            self.t.send(msg["user_name"] + ", " + anekdot)
                        # Если там гороскоп - то генерим и отправляем гороскоп.
                        elif "гороскоп" in msg_4me:
                            gen_h = self.h.get_horoscope()
                            self.t.send(msg["user_name"] + ", " + gen_h)
                        # Если не анекдот и гороскоп, то будем спрашивать у гугла, что ответить.
                        else:
                            text_input = dialogflow.types.TextInput(text=msg_4me,
                                                                    language_code=self.DIALOGFLOW_LANGUAGE_CODE)
                            query_input = dialogflow.types.QueryInput(text=text_input)
                            try:
                                response = self.session_client.detect_intent(
                                    session=self.session, query_input=query_input
                                )
                            except InvalidArgument:
                                raise
                            answer = response.query_result.fulfillment_text
                            self.t.send(msg["user_name"] + ", " + answer)
                    # Новые сообщения выводим в консоль.
                    if int(msg["timestamp"]) > int(self.timestamp):
                        print(msg["user_name"] + ": " + msg["text"])
                        self.timestamp = msg["timestamp"]
            # Спим 5 секунд до следующей итерации.
            sleep(5)


# Точка входа
if __name__ == '__main__':
    GGBot().run()
