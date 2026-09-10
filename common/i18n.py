from __future__ import annotations

LANGS = ("ru", "uz", "en")

TEXT = {
    "ru": {
        "choose_lang": "🌐 Выберите язык AKBSHAV TOOLS:",
        "rules_title": "📜 Правила AKBSHAV TOOLS",
        "rules": (
            "1. Сервис предоставляет инструменты для Telegram.\n"
            "2. Пользователь отвечает за действия, выполненные с его аккаунта.\n"
            "3. Запрещены мошенничество, угрозы, преследование, вредоносные действия, доксинг и нежелательная массовая рассылка.\n"
            "4. Не используйте сервис для нарушения правил Telegram или применимого законодательства.\n"
            "5. При подключении автоматизации пользователь самостоятельно выбирает Telegram-разрешения.\n"
            "6. При отписке от обязательного канала доступ к функциям блокируется до повторной подписки.\n"
            "7. Разработчик не контролирует пользовательский контент и действия; ответственность за их последствия лежит на пользователе в пределах, допускаемых законом.\n"
            "8. Работа функций зависит от Telegram API, типа чата, выданных разрешений и технических ограничений.\n"
            "9. Администрация может ограничить доступ при нарушении правил.\n"
            "10. Использование сервиса означает согласие с правилами."
        ),
        "accept": "✅ Принимаю",
        "decline": "❌ Не принимаю",
        "sub_required": "📢 Для продолжения подпишитесь на обязательный канал, затем нажмите «Проверить».",
        "subscribe": "📢 Подписаться",
        "check": "🔄 Проверить",
        "access_denied": "⛔ Доступ ограничен. Проверьте правила и подписку на обязательный канал.",
        "main": "🏠 AKBSHAV TOOLS",
        "functions": "⚡ Функции",
        "automation": "🔗 Автоматизация",
        "library": "📚 Библиотека",
        "support": "💬 Поддержка",
        "settings": "⚙️ Настройки",
        "help": "ℹ️ Помощь",
        "back": "⬅️ Назад",
        "connected": "✅ Автоматизация подключена. Теперь вы можете воспользоваться функциями AKBSHAV TOOLS.",
        "disconnected": "⚠️ Автоматизация отключена. Функции, требующие подключения, недоступны.",
        "automation_help": (
            "🔗 <b>Автоматизация чатов</b>\n\n"
            "1. Откройте Telegram → Настройки.\n"
            "2. Откройте свой профиль и нажмите «Изменить».\n"
            "3. Выберите «Автоматизация чатов».\n"
            "4. Добавьте @AKBSHAVTOOLS_bot и выдайте только нужные разрешения.\n\n"
            "После подключения Telegram отправит подтверждение автоматически."
        ),
        "support_prompt": "💬 Опишите проблему одним или несколькими сообщениями. Я создам тикет и передам его администрации.\n\nДля отмены: /cancel",
        "ticket_created": "🎫 Тикет #{id} создан. Ответ администрации придёт сюда.",
        "ticket_closed": "🔒 Тикет закрыт.",
        "language_saved": "✅ Язык сохранён.",
        "settings_text": "⚙️ <b>Настройки</b>\n\nПрефикс команд: <code>.</code>\nЯзык можно изменить ниже.",
        "help_text": "ℹ️ <b>Помощь</b>\n\nОсновные команды автоматизации используют префикс <code>.</code>. Например: <code>.reverse текст</code> или <code>.coin</code>.",
        "automation_status_on": "✅ Подключена",
        "automation_status_off": "⚠️ Не подключена",
        "library_title": "📚 <b>Библиотека</b>",
        "library_empty": "Пока пусто.",
        "cancelled": "❌ Отменено.",
        "function_disabled": "⚠️ Эта функция временно отключена.",
        "rate_limited": "⏳ Слишком много запросов. Попробуйте немного позже.",
        "invalid_command": "⚠️ Неверный формат команды.",
        "server_error": "⚠️ Не удалось обработать запрос. Попробуйте ещё раз.",
    },
    "uz": {
        "choose_lang": "🌐 AKBSHAV TOOLS tilini tanlang:",
        "rules_title": "📜 AKBSHAV TOOLS qoidalari",
        "rules": (
            "1. Xizmat Telegram uchun vositalarni taqdim etadi.\n"
            "2. Foydalanuvchi o‘z akkaunti orqali bajarilgan harakatlar uchun javob beradi.\n"
            "3. Firibgarlik, tahdid, ta’qib, zararli harakatlar, doksing va istalmagan ommaviy tarqatish taqiqlanadi.\n"
            "4. Telegram qoidalari va amaldagi qonunchilikka rioya qiling.\n"
            "5. Avtomatlashtirishda Telegram ruxsatlarini foydalanuvchi o‘zi tanlaydi.\n"
            "6. Majburiy kanaldan chiqilsa, funksiyalar qayta obuna bo‘linguncha bloklanadi.\n"
            "7. Ishlab chiquvchi foydalanuvchi kontenti va harakatlarini nazorat qilmaydi; oqibatlar uchun javobgarlik foydalanuvchiga tegishli.\n"
            "8. Funksiyalar Telegram API, chat turi, ruxsatlar va texnik cheklovlarga bog‘liq.\n"
            "9. Qoidalar buzilsa, kirish cheklanishi mumkin.\n"
            "10. Xizmatdan foydalanish qoidalarni qabul qilishni anglatadi."
        ),
        "accept": "✅ Qabul qilaman",
        "decline": "❌ Qabul qilmayman",
        "sub_required": "📢 Davom etish uchun majburiy kanalga obuna bo‘ling va «Tekshirish»ni bosing.",
        "subscribe": "📢 Obuna bo‘lish",
        "check": "🔄 Tekshirish",
        "access_denied": "⛔ Kirish cheklangan. Qoidalar va kanal obunasini tekshiring.",
        "main": "🏠 AKBSHAV TOOLS",
        "functions": "⚡ Funksiyalar",
        "automation": "🔗 Avtomatlashtirish",
        "library": "📚 Kutubxona",
        "support": "💬 Yordam",
        "settings": "⚙️ Sozlamalar",
        "help": "ℹ️ Yordam",
        "back": "⬅️ Orqaga",
        "connected": "✅ Avtomatlashtirish ulandi. Endi AKBSHAV TOOLS funksiyalaridan foydalanishingiz mumkin.",
        "disconnected": "⚠️ Avtomatlashtirish uzildi.",
        "automation_help": "🔗 <b>Chat avtomatlashtirish</b>\n\n1. Telegram → Sozlamalar.\n2. Profilingizni oching va «Tahrirlash»ni bosing.\n3. «Chat avtomatlashtirish»ni tanlang.\n4. @AKBSHAVTOOLS_bot ni qo‘shing va kerakli ruxsatlarni bering.",
        "support_prompt": "💬 Muammoni yozing. Men murojaatni ticket sifatida yuboraman.\n\nBekor qilish: /cancel",
        "ticket_created": "🎫 #{id}-murojaat yaratildi. Javob shu yerga keladi.",
        "ticket_closed": "🔒 Murojaat yopildi.",
        "language_saved": "✅ Til saqlandi.",
        "settings_text": "⚙️ <b>Sozlamalar</b>\n\nBuyruq prefiksi: <code>.</code>",
        "help_text": "ℹ️ <b>Yordam</b>\n\nAsosiy buyruqlar <code>.</code> prefiksidan foydalanadi. Masalan: <code>.reverse matn</code> yoki <code>.coin</code>.",
        "automation_status_on": "✅ Ulangan",
        "automation_status_off": "⚠️ Ulanmagan",
        "library_title": "📚 <b>Kutubxona</b>",
        "library_empty": "Hozircha bo‘sh.",
        "cancelled": "❌ Bekor qilindi.",
        "function_disabled": "⚠️ Bu funksiya vaqtincha o‘chirilgan.",
        "rate_limited": "⏳ So‘rovlar juda ko‘p. Birozdan keyin urinib ko‘ring.",
        "invalid_command": "⚠️ Buyruq formati noto‘g‘ri.",
        "server_error": "⚠️ So‘rovni bajarib bo‘lmadi. Qayta urinib ko‘ring.",
    },
    "en": {
        "choose_lang": "🌐 Choose AKBSHAV TOOLS language:",
        "rules_title": "📜 AKBSHAV TOOLS Rules",
        "rules": (
            "1. The service provides tools for Telegram.\n"
            "2. Users are responsible for actions performed through their accounts.\n"
            "3. Fraud, threats, harassment, harmful actions, doxxing and unwanted mass distribution are prohibited.\n"
            "4. Follow Telegram rules and applicable law.\n"
            "5. Users choose Telegram permissions when connecting automation.\n"
            "6. Unsubscribing from the required channel blocks features until resubscription.\n"
            "7. The developer does not control user content or actions; responsibility for consequences rests with the user to the extent permitted by law.\n"
            "8. Functions depend on Telegram API, chat type, granted permissions and technical limits.\n"
            "9. Access may be restricted for violations.\n"
            "10. Using the service means accepting these rules."
        ),
        "accept": "✅ Accept",
        "decline": "❌ Decline",
        "sub_required": "📢 Subscribe to the required channel, then press “Check”.",
        "subscribe": "📢 Subscribe",
        "check": "🔄 Check",
        "access_denied": "⛔ Access is restricted. Check the rules and required channel subscription.",
        "main": "🏠 AKBSHAV TOOLS",
        "functions": "⚡ Functions",
        "automation": "🔗 Automation",
        "library": "📚 Library",
        "support": "💬 Support",
        "settings": "⚙️ Settings",
        "help": "ℹ️ Help",
        "back": "⬅️ Back",
        "connected": "✅ Automation connected. You can now use AKBSHAV TOOLS functions.",
        "disconnected": "⚠️ Automation disconnected.",
        "automation_help": "🔗 <b>Chat automation</b>\n\n1. Telegram → Settings.\n2. Open your profile and tap Edit.\n3. Select Chat Automation.\n4. Add @AKBSHAVTOOLS_bot and grant only the permissions you need.",
        "support_prompt": "💬 Describe the problem. I will create a ticket and send it to the administrators.\n\nCancel: /cancel",
        "ticket_created": "🎫 Ticket #{id} created. The administrator reply will arrive here.",
        "ticket_closed": "🔒 Ticket closed.",
        "language_saved": "✅ Language saved.",
        "settings_text": "⚙️ <b>Settings</b>\n\nCommand prefix: <code>.</code>",
        "help_text": "ℹ️ <b>Help</b>\n\nMain automation commands use the <code>.</code> prefix. Example: <code>.reverse text</code> or <code>.coin</code>.",
        "automation_status_on": "✅ Connected",
        "automation_status_off": "⚠️ Not connected",
        "library_title": "📚 <b>Library</b>",
        "library_empty": "Nothing saved yet.",
        "cancelled": "❌ Cancelled.",
        "function_disabled": "⚠️ This function is temporarily disabled.",
        "rate_limited": "⏳ Too many requests. Please try again shortly.",
        "invalid_command": "⚠️ Invalid command format.",
        "server_error": "⚠️ The request could not be processed. Please try again.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    lang = lang if lang in LANGS else "ru"
    return TEXT[lang][key].format(**kwargs)
