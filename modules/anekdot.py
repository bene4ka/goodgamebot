import requests
from bs4 import BeautifulSoup
import html2text


class Anekdot:
    """
    Класс, который генерирует случайный анекдот.
    """
    def __init__(self):
        """
        Инициализируется только УРЛ ресурса с анекдотами.
        """
        self.url = "https://anekdot-z.ru/random-anekdot"

    def get_anekdot(self):
        """
        Выдергиваем анекдот со страницы и убираем HTML теги.
        :return: Текст анекдота в формате string.
        """
        page = requests.get(self.url).text
        soap = BeautifulSoup(page, "lxml")
        anekdot_div = soap.findAll("div", {"class": "anekdot-content"})[0]

        return html2text.html2text(str(anekdot_div))
