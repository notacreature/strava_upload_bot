TEXT = {
    "key_auth": "🔑 Открыть Strava",
    "key_chdesc": "✏ Описание",
    "key_chgear": "✏ Экипировка",
    "key_chname": "✏ Название",
    "key_chtype": "✏ Тип",
    "key_openstrava": "Посмотреть в Strava",
    "key_ride": "🚴‍♂️ Ride",
    "key_run": "👟 Run",
    "key_swim": "🏊‍♀️ Swim",
    "placeholder_chname": "Имя активности",
    "reply_activityupdated": "Активность обновлена 🏆\n```\nИмя: {}\nТип: {}\nЭкипировка: {}\nВремя: {}\nДистанция: {}\nОписание: {}```",
    "reply_activityuploaded": "Активность опубликована 🏆\n```\nИмя: {}\nТип: {}\nЭкипировка: {}\nВремя: {}\nДистанция: {}\nОписание: {}```",
    "reply_authorized": "🤖 Отлично! Я получил твое разрешение и готов работать. Просто пришли мне файл в формате `.fit`, `.tcx` или `.gpx`, и я его опубликую.",
    "reply_canceled": "Действие отменено ↩️",
    "reply_chdesc": "🤖 Введи новое описание.",
    "reply_chgear": "🤖 Выбери новую экипировку.",
    "reply_chname": "🤖 Введи новое название.",
    "reply_chtype": "🤖 Выбери новый вид спорта.",
    "reply_delete": "🤖 Ты точно хочешь чтобы я удалил все твои данные? Я больше не смогу работать с твоей Strava, пока ты снова не разрешить. Для подтверждения повтори /delete, для отмены /cancel.",
    "reply_done": "🤖 Готово!",
    "reply_error": "Не удалось загрузить активность 💢\n`{}`",
    "reply_favorites": "🤖 Введи до 3-х названий через запятую и я добавлю их в избранное.",
    "reply_help": "*Старт*\nДля начала работы с ботом введи команду /start, перейди по ссылке и разреши боту загружать твою активность в Strava. Для этого может потребоваться VPN.\n\n*Загрузка*\nОтправь в чат файл в формате `.fit`, `.tcx` или `.gpx` и бот его опубликует. После публикации ты получишь краткую информацию об активности и сможешь изменить её Имя, Описание, Тип и Экипировку.\nЕсли передумал, используй /cancel.\n\n*Избранные названия*\nТы можешь запомнить до трёх названий активности, которые часто используешь – введи команду /favorites и перечисли их через запятую.\n\n*Удаление данных*\nЕсли ты больше не хочешь, чтобы бот загружал файлы в твой аккаунт Strava – используй команду /delete и бот удалит все данные о тебе.",
    "reply_other": "🤖 К сожалению, я не понимаю, что ты имеешь ввиду.\nПопробуй ввести команду /help.",
    "reply_restart": "🤖 Мы уже знакомы. Но если ты хочешь переподключить меня к Strava, нажми кнопку ниже.",
    "reply_scope": "🤖 Кажется, я не получил от тебя все нужные разрешения. Попробуй выполнить команду /start еще раз и убедись, что все галочки в Strava установлены.",
    "reply_start": "🤖 Привет! Я бот, который поможет тебе публиковать твою активность в Strava. Для этого мне нужно получить твое разрешение на загрузку файлов в твой аккаунт. Нажми кнопку ниже, чтобы продолжить.",
    "reply_unknown": "🤖 Прости, но я тебя пока не знаю. Чтобы я мог тебе помочь, сначала введи команду /start и выполни пару шагов.",
}
URL = {
    "activity": "https://www.strava.com/activities/{}",
    "auth": "http://www.strava.com/oauth/authorize?client_id={}&response_type=code&scope={}&redirect_uri={}?user_id={}",
    "bot": "https://api.telegram.org/bot{}/sendMessage",
}
STATUS = {
    "deleted": "The created activity has been deleted.",
    "error": "There was an error processing your activity.",
    "ready": "Your activity is ready.",
    "wait": "Your activity is still being processed.",
}
