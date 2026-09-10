from __future__ import annotations

import random
import re
import unicodedata

from common.config import MAX_REPEATS, MAX_WORDS, MAX_MESSAGE_LENGTH

BUBBLE = str.maketrans({
    **{chr(ord('a')+i): c for i,c in enumerate('ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ')},
    **{chr(ord('A')+i): c for i,c in enumerate('ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ')},
})
LEET = str.maketrans({"a":"4","e":"3","i":"1","o":"0","s":"5","t":"7","A":"4","E":"3","I":"1","O":"0","S":"5","T":"7"})


FUNCTIONS = {
    "help", "помощь", "reverse", "nospace", "bubble", "leet", "dumb",
    "glitch", "spoiler", "words", "heart", "print", "matrix", "coin",
    "монета", "repeat", "quote", "autoreply", "autoreplyoff", "timer",
    "save", "unsave",
}


def clean_arg(text: str) -> str:
    return text.strip()[:MAX_MESSAGE_LENGTH]


def reverse(text: str) -> str:
    return text[::-1]


def nospace(text: str) -> str:
    return re.sub(r"\s+", "", text)


def bubble(text: str) -> str:
    return text.translate(BUBBLE)


def leet(text: str) -> str:
    return text.translate(LEET)


def dumb(text: str) -> str:
    chars = []
    for i, ch in enumerate(text):
        chars.append(ch.lower() if i % 2 else ch.upper())
    return "".join(chars)


def glitch(text: str) -> str:
    marks = "̷̸̶̴̵"
    return "".join(ch + random.choice(marks) for ch in text[:500])


def spoiler(text: str) -> str:
    return f"||{text}||"


def words(text: str) -> str:
    parts = text.split()
    if len(parts) > MAX_WORDS:
        parts = parts[:MAX_WORDS]
    return "\n".join(parts)


def heart(text: str) -> str:
    return "♥ " + text + " ♥"


def print_effect(text: str) -> str:
    return "\n".join(text[:120])


def matrix(text: str) -> str:
    alphabet = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out = []
    for ch in text[:500]:
        if ch.isspace():
            out.append(ch)
        else:
            out.append(random.choice(alphabet))
    return "".join(out)


def limited_repeat(text: str, count: int) -> str:
    count = max(1, min(count, MAX_REPEATS))
    return "\n".join([text] * count)


def coin() -> str:
    return random.choice(("🪙 Орёл", "🪙 Решка"))


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def command_help() -> str:
    return (
        "<b>Безопасные команды</b>\n\n"
        ".reverse текст — реверс\n"
        ".nospace текст — убрать пробелы\n"
        ".bubble текст — буквы в кружках\n"
        ".leet текст — 1337-стиль\n"
        ".dumb текст — чередование регистра\n"
        ".glitch текст — глитч-эффект\n"
        ".spoiler текст — спойлер\n"
        ".words текст — каждое слово отдельной строкой\n"
        ".heart текст — декоративная рамка\n"
        ".print текст — эффект печати\n"
        ".matrix текст — визуальный Matrix-эффект\n"
        ".repeat N текст — ограниченный повтор\n"
        ".coin — монетка\n"
        ".quote — цитата из сообщения, на которое вы ответили\n"
        ".autoreply текст — включить автоответ\n.autoreplyoff — выключить автоответ\n.timer N текст — отложить сообщение (1–3600 сек.)\n.save shortcut текст — сохранить быстрый ответ\n.unsave shortcut — удалить быстрый ответ\n\nМассовая рассылка, доксинг, снос аккаунтов и обход ограничений Telegram в этот релиз не входят."
    )
