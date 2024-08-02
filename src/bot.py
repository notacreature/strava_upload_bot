import os, time, requests, configparser, strava
from tinydb import TinyDB, Query
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    constants,
)
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)
from dictionary import TEXT, URL, STATUS

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), "..", "settings.ini"))
TOKEN = CONFIG["Telegram"]["BOT_TOKEN"]
CLIENT_ID = CONFIG["Strava"]["CLIENT_ID"]
CLIENT_SECRET = CONFIG["Strava"]["CLIENT_SECRET"]
SCOPE = CONFIG["Strava"]["SCOPE"]
REDIRECT_URL = CONFIG["Server"]["URL"]
USER_DB = TinyDB(os.path.join(os.path.dirname(__file__), "..", "storage", "userdata.json"))
USER_QUERY = Query()


# /start; регистрация
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(TEXT["key_auth"], url=URL["auth"].format(CLIENT_ID, SCOPE, REDIRECT_URL, user_id)),
            ]
        ]
    )
    if not strava.user_exists(user_id, USER_DB, USER_QUERY):
        await update.message.reply_text(
            TEXT["reply_start"],
            constants.ParseMode.MARKDOWN,
            reply_markup=inline_keyboard,
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            TEXT["reply_restart"],
            constants.ParseMode.MARKDOWN,
            reply_markup=inline_keyboard,
        )
        return ConversationHandler.END


# /favorites; создание списка избранных названий
async def favorites_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not strava.user_exists(user_id, USER_DB, USER_QUERY):
        await update.message.reply_text(
            TEXT["reply_unknown"],
            constants.ParseMode.MARKDOWN,
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            TEXT["reply_favorites"],
            constants.ParseMode.MARKDOWN,
        )
        return "favorites_finish"


async def favorites_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    favorites = update.message.text.split(",")[:3]
    for fav in favorites:
        fav.strip()
    USER_DB.upsert({"favorites": favorites}, USER_QUERY["user_id"] == user_id)
    await update.message.reply_text(
        TEXT["reply_done"],
        constants.ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


# /delete; удаление данных пользователя из userdata.json
async def delete_user_data_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if not strava.user_exists(user_id, USER_DB, USER_QUERY):
        await update.message.reply_text(
            TEXT["reply_unknown"],
            constants.ParseMode.MARKDOWN,
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            TEXT["reply_delete"],
            constants.ParseMode.MARKDOWN,
        )
        return "user_data_delete"


async def delete_user_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    refresh_token = USER_DB.get(USER_QUERY["user_id"] == user_id)["refresh_token"]
    access_token = await strava.get_access_token(user_id, CLIENT_ID, CLIENT_SECRET, refresh_token, USER_DB, USER_QUERY)
    await strava.deauthorize(access_token)
    USER_DB.remove(USER_QUERY["user_id"] == user_id)
    await update.message.reply_text(
        TEXT["reply_done"],
        constants.ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


# Публикация тренировки
async def upload_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if not strava.user_exists(user_id, USER_DB, USER_QUERY):
        await update.message.reply_text(
            TEXT["reply_unknown"],
            constants.ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    name = update.message.caption
    file_id = update.message.document.file_id
    file_data = await context.bot.get_file(file_id)
    data_type = str.split(update.message.document.file_name, ".")[-1]
    file = requests.get(file_data.file_path).content
    refresh_token = USER_DB.get(USER_QUERY["user_id"] == user_id)["refresh_token"]
    access_token = await strava.get_access_token(user_id, CLIENT_ID, CLIENT_SECRET, refresh_token, USER_DB, USER_QUERY)
    context.user_data["access_token"] = access_token

    upload_id = await strava.post_activity(access_token, name, data_type, file)
    upload = await strava.get_upload(upload_id, access_token, STATUS)
    activity_id = str(upload["activity_id"])
    context.user_data["activity_id"] = activity_id
    status = str(upload["status"])

    if status == STATUS["ready"]:
        inline_keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(TEXT["key_chname"], callback_data="chname"),
                    InlineKeyboardButton(TEXT["key_chdesc"], callback_data="chdesc"),
                ],
                [
                    InlineKeyboardButton(TEXT["key_chtype"], callback_data="chtype"),
                    InlineKeyboardButton(TEXT["key_chgear"], callback_data="chgear"),
                ],
                [
                    InlineKeyboardButton(TEXT["key_openstrava"], url=URL["activity"].format(activity_id)),
                ],
            ]
        )
        activity = await strava.get_activity(access_token, activity_id)
        await update.message.reply_text(
            TEXT["reply_activityuploaded"].format(
                activity["name"], activity["sport_type"], activity["gear"], activity["moving_time"], activity["distance"], activity["description"]
            ),
            constants.ParseMode.MARKDOWN,
            reply_markup=inline_keyboard,
        )
        return "activity_view"
    else:
        await update.message.reply_text(
            TEXT["reply_error"].format(status),
            constants.ParseMode.MARKDOWN,
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END


# Список последних тренировок
async def view_activity_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)

    if not strava.user_exists(user_id, USER_DB, USER_QUERY):
        await update.message.reply_text(
            TEXT["reply_unknown"],
            constants.ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    refresh_token = USER_DB.get(USER_QUERY["user_id"] == user_id)["refresh_token"]
    access_token = await strava.get_access_token(user_id, CLIENT_ID, CLIENT_SECRET, refresh_token, USER_DB, USER_QUERY)
    context.user_data["access_token"] = access_token

    activity_list = await strava.get_activity_list(access_token, 3)
    inline_keys = []
    for activity in activity_list:
        date = time.strftime("%a %d.%m.%y %H:%M", (time.strptime(activity["start_date_local"], "%Y-%m-%dT%H:%M:%SZ")))
        inline_keys.append([InlineKeyboardButton(f"{date} 🔸 {activity['name']}", callback_data=activity["id"])])
    inline_keyboard = InlineKeyboardMarkup(inline_keys)
    await update.message.reply_text(
        "TODO ТЕКСТ ДЛЯ СПИСКА",
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "activity_list_view"


async def view_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    activity_id = update.callback_query.data
    context.user_data["activity_id"] = activity_id
    access_token = context.user_data["access_token"]
    await query.answer()

    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(TEXT["key_chname"], callback_data="chname"),
                InlineKeyboardButton(TEXT["key_chdesc"], callback_data="chdesc"),
            ],
            [
                InlineKeyboardButton(TEXT["key_chtype"], callback_data="chtype"),
                InlineKeyboardButton(TEXT["key_chgear"], callback_data="chgear"),
            ],
            [
                InlineKeyboardButton(TEXT["key_openstrava"], url=URL["activity"].format(activity_id)),
            ],
        ]
    )
    activity = await strava.get_activity(access_token, activity_id)
    await query.edit_message_text(
        TEXT["reply_activityupdated"].format(
            activity["name"], activity["sport_type"], activity["gear"], activity["moving_time"], activity["distance"], activity["description"]
        ),
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "activity_view"


# Редактирование тренировки
async def change_name_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = str(query.from_user.id)
    await query.answer()
    favorites = USER_DB.get(USER_QUERY["user_id"] == user_id)["favorites"]
    reply_keyboard = ReplyKeyboardMarkup(
        [favorites],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder=TEXT["placeholder_chname"],
    )
    await context.bot.send_message(
        user_id,
        TEXT["reply_chname"],
        constants.ParseMode.MARKDOWN,
        reply_markup=reply_keyboard,
    )
    return "name_change"


async def change_desc_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await context.bot.send_message(
        query.from_user.id,
        TEXT["reply_chdesc"],
        constants.ParseMode.MARKDOWN,
    )
    return "desc_change"


async def change_type_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(TEXT["key_swim"], callback_data="Swim"),
                InlineKeyboardButton(TEXT["key_ride"], callback_data="Ride"),
                InlineKeyboardButton(TEXT["key_run"], callback_data="Run"),
            ]
        ]
    )
    await query.edit_message_text(
        TEXT["reply_chtype"],
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "type_change"


async def change_gear_dialog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    access_token = context.user_data["access_token"]
    gear_list = await strava.get_gear(access_token)
    inline_keys = []
    for gear in gear_list:
        inline_keys.append([InlineKeyboardButton(f"{gear['type']} {gear['name']}", callback_data=gear["id"])])
    inline_keyboard = InlineKeyboardMarkup(inline_keys)
    await query.edit_message_text(
        TEXT["reply_chgear"],
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "gear_change"


async def change_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    access_token = context.user_data["access_token"]
    activity_id = context.user_data["activity_id"]
    activity = await strava.update_activity(access_token, activity_id, name=name)

    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(TEXT["key_chname"], callback_data="chname"),
                InlineKeyboardButton(TEXT["key_chdesc"], callback_data="chdesc"),
            ],
            [
                InlineKeyboardButton(TEXT["key_chtype"], callback_data="chtype"),
                InlineKeyboardButton(TEXT["key_chgear"], callback_data="chgear"),
            ],
            [
                InlineKeyboardButton(TEXT["key_openstrava"], url=URL["activity"].format(activity_id)),
            ],
        ]
    )
    await update.message.reply_text(
        TEXT["reply_activityupdated"].format(
            activity["name"], activity["sport_type"], activity["gear"], activity["moving_time"], activity["distance"], activity["description"]
        ),
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "activity_view"


async def change_desc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = update.message.text
    access_token = context.user_data["access_token"]
    activity_id = context.user_data["activity_id"]
    activity = await strava.update_activity(access_token, activity_id, description=description)

    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(TEXT["key_chname"], callback_data="chname"),
                InlineKeyboardButton(TEXT["key_chdesc"], callback_data="chdesc"),
            ],
            [
                InlineKeyboardButton(TEXT["key_chtype"], callback_data="chtype"),
                InlineKeyboardButton(TEXT["key_chgear"], callback_data="chgear"),
            ],
            [
                InlineKeyboardButton(TEXT["key_openstrava"], url=URL["activity"].format(activity_id)),
            ],
        ]
    )
    await update.message.reply_text(
        TEXT["reply_activityupdated"].format(
            activity["name"], activity["sport_type"], activity["gear"], activity["moving_time"], activity["distance"], activity["description"]
        ),
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "activity_view"


async def change_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    sport_type = update.callback_query.data
    access_token = context.user_data["access_token"]
    activity_id = context.user_data["activity_id"]
    activity = await strava.update_activity(access_token, activity_id, sport_type=sport_type)

    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(TEXT["key_chname"], callback_data="chname"),
                InlineKeyboardButton(TEXT["key_chdesc"], callback_data="chdesc"),
            ],
            [
                InlineKeyboardButton(TEXT["key_chtype"], callback_data="chtype"),
                InlineKeyboardButton(TEXT["key_chgear"], callback_data="chgear"),
            ],
            [
                InlineKeyboardButton(TEXT["key_openstrava"], url=URL["activity"].format(activity_id)),
            ],
        ]
    )
    await query.edit_message_text(
        TEXT["reply_activityupdated"].format(
            activity["name"], activity["sport_type"], activity["gear"], activity["moving_time"], activity["distance"], activity["description"]
        ),
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "activity_view"


async def change_gear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    gear_id = update.callback_query.data
    access_token = context.user_data["access_token"]
    activity_id = context.user_data["activity_id"]
    activity = await strava.update_activity(access_token, activity_id, gear_id=gear_id)

    inline_keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(TEXT["key_chname"], callback_data="chname"),
                InlineKeyboardButton(TEXT["key_chdesc"], callback_data="chdesc"),
            ],
            [
                InlineKeyboardButton(TEXT["key_chtype"], callback_data="chtype"),
                InlineKeyboardButton(TEXT["key_chgear"], callback_data="chgear"),
            ],
            [
                InlineKeyboardButton(TEXT["key_openstrava"], url=URL["activity"].format(activity_id)),
            ],
        ]
    )
    await query.edit_message_text(
        TEXT["reply_activityupdated"].format(
            activity["name"], activity["sport_type"], activity["gear"], activity["moving_time"], activity["distance"], activity["description"]
        ),
        constants.ParseMode.MARKDOWN,
        reply_markup=inline_keyboard,
    )
    return "activity_view"


# /help; справка
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TEXT["reply_help"],
        constants.ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


# /cancel; отмена диалога ConversationHandler
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TEXT["reply_canceled"],
        constants.ParseMode.MARKDOWN,
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


# Обработка прочих сообщений
async def other(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        TEXT["reply_other"],
        constants.ParseMode.MARKDOWN,
    )
    return ConversationHandler.END


def main():
    application = ApplicationBuilder().token(TOKEN).build()

    list_entry = CommandHandler("list", view_activity_list)
    file_entry = MessageHandler(
        filters.Document.FileExtension("fit") | filters.Document.FileExtension("tcx") | filters.Document.FileExtension("gpx"), upload_activity
    )
    favorites_entry = CommandHandler("favorites", favorites_start)
    delete_entry = CommandHandler("delete", delete_user_data_dialog)

    cancel_fallback = CommandHandler("cancel", cancel)

    start_reply = CommandHandler("start", start)
    help_reply = CommandHandler("help", help)
    other_reply = MessageHandler(
        ~filters.COMMAND & ~filters.Document.FileExtension("fit") & ~filters.Document.FileExtension("tcx") & ~filters.Document.FileExtension("gpx"), other
    )

    activity_dialog = ConversationHandler(
        entry_points=[
            list_entry,
            file_entry,
        ],
        states={
            "activity_list_view": [CallbackQueryHandler(view_activity, pattern="^\d+$")],
            "activity_view": [
                # Еще один обработчик для возвращения к списку
                CallbackQueryHandler(change_name_dialog, pattern="chname"),
                CallbackQueryHandler(change_desc_dialog, pattern="chdesc"),
                CallbackQueryHandler(change_type_dialog, pattern="chtype"),
                CallbackQueryHandler(change_gear_dialog, pattern="chgear"),
            ],
            "name_change": [MessageHandler(~filters.COMMAND & filters.TEXT, change_name)],
            "desc_change": [MessageHandler(~filters.COMMAND & filters.TEXT, change_desc)],
            "type_change": [CallbackQueryHandler(change_type, pattern="Swim|Ride|Run")],
            "gear_change": [CallbackQueryHandler(change_gear, pattern="^\w\d+$")],
        },
        fallbacks=[
            cancel_fallback,
            list_entry,
            file_entry,
            favorites_entry,
            delete_entry,
        ],
    )

    favorites_dialog = ConversationHandler(
        entry_points=[favorites_entry],
        states={"favorites_finish": [MessageHandler(~filters.COMMAND & filters.TEXT, favorites_finish)]},
        fallbacks=[
            cancel_fallback,
            list_entry,
            file_entry,
            favorites_entry,
            delete_entry,
        ],
    )
    delete_dialog = ConversationHandler(
        entry_points=[delete_entry],
        states={"user_data_delete": [CommandHandler("delete", delete_user_data)]},
        fallbacks=[
            cancel_fallback,
            list_entry,
            file_entry,
            favorites_entry,
            delete_entry,
        ],
    )

    application.add_handlers(
        [
            activity_dialog,
            favorites_dialog,
            delete_dialog,
            start_reply,
            help_reply,
            other_reply,
        ]
    )

    application.run_polling()


if __name__ == "__main__":
    main()
