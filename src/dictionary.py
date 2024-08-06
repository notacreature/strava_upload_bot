TEXT = {
    "key_activity": "{} 🔸 {}",
    "key_auth": "🔑 Открыть Strava",
    "key_chdesc": "✏ Описание",
    "key_chgear": "✏ Экипировка",
    "key_chname": "✏ Название",
    "key_chtype": "✏ Тип",
    "key_list": "📃 Последние тренировки",
    "key_ride": "🚴‍♂️ Ride",
    "key_run": "👟 Run",
    "key_swim": "🏊‍♀️ Swim",
    "reply_activity_updated": "✅ *Тренировка обновлена!*\n\n*Имя:* `{}`\n*Тип:* `{}`\n*Время:* `{}`\n*Дистанция:* `{}`\n*Экипировка:* `{}`\n*Описание:* `{}`\n\n[Посмотреть в Strava]({})",
    "reply_activity_uploaded": "✅ *Тренировка опубликована!*\n\n*Имя:* `{}`\n*Тип:* `{}`\n*Время:* `{}`\n*Дистанция:* `{}`\n*Экипировка:* `{}`\n*Описание:* `{}`\n\n[Посмотреть в Strava]({})",
    "reply_activity_view": "*Имя:* `{}`\n*Тип:* `{}`\n*Время:* `{}`\n*Дистанция:* `{}`\n*Экипировка:* `{}`\n*Описание:* `{}`\n\n[Посмотреть в Strava]({})",
    "reply_authorized": "🤖 Отлично! Я получил твое разрешение и готов работать. Теперь введи команду /list, чтобы изменить тренировку в Strava или пришли мне файл в формате `.fit`, `.tcx` или `.gpx`, чтобы опубликовать новую.",
    "reply_canceled": "⏮️ Действие отменено.",
    "reply_chdesc": "Введи новое описание:",
    "reply_chgear": "Выбери новую экипировку:",
    "reply_chname": "Введи новое название:",
    "reply_chtype": "Выбери новый вид спорта:",
    "reply_delete_dialog": "🤖 Ты точно хочешь чтобы я удалил все твои данные? Я больше не смогу работать с твоей Strava, пока ты снова не разрешить. Для подтверждения повтори /delete, для отмены /cancel.",
    "reply_deleted": "✅ Готово, данные удалены!",
    "reply_error": "💢 Не удалось загрузить тренировку.\n`{}`",
    "reply_help": "*Начало*\nДля начала работы с ботом введи команду /start, перейди по ссылке и разреши боту доступ к твоим тренировкам в Strava. Для этого может потребоваться VPN.\n\n*Редактирование*\nДля редактирования тренировок в Strava введи команду /list – ты получишь список последних записей в твоём аккаунте. Нажми на одну из них, и в открывшейся карточке ты сможешь изменить имя, описание, тип и экипировку.\nЕсли передумал, используй /cancel.\n\n*Загрузка*\nОтправь в чат файл в формате '.fit', '.tcx' или '.gpx', и бот его опубликует. После публикации ты получишь краткую информацию о тренировке и сможешь её изменить.\n\n*Удаление данных*\nЕсли ты больше не хочешь, чтобы бот имел доступ к твоим тренировкам в Strava, используй команду /delete, и бот удалит все данные о тебе.",
    "reply_list_view": "📃 Твои последние тренировки:",
    "reply_other": "🤖 К сожалению, я не понимаю, что ты имеешь ввиду.\nПопробуй ввести команду /help.",
    "reply_restart": "🤖 Мы уже знакомы. Но если ты хочешь переподключить меня к Strava, нажми кнопку ниже.",
    "reply_scope": "🤖 Кажется, я не получил от тебя все необходимые разрешения. Попробуй выполнить команду /start еще раз и убедись, что все галочки в Strava установлены.",
    "reply_start": "🤖 Привет! Я бот, который поможет тебе управлять тренировками в Strava. Чтобы начать, мне нужно разрешение на доступ к твоим данным активности. Нажми кнопку ниже, чтобы продолжить.",
    "reply_unknown": "🤖 Прости, но я тебя пока не знаю. Чтобы я мог тебе помочь, сначала введи команду /start и выполни пару шагов.",
}
URL = {
    "activity": "https://www.strava.com/activities/{}",
    "auth": "http://www.strava.com/oauth/authorize?client_id={}&response_type=code&scope={}&redirect_uri={}?user_id={}",
    "bot": "https://api.telegram.org/bot{}/sendMessage",
}
