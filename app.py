from telegram import ReplyKeyboardMarkup, Update, \
    InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)
import logging
from typing import Dict
from src.recommendation_engine.inference import predict_cuisine, get_similar_recipes
from src.recognition_engine.inference import classify_images


logging.basicConfig(

    format='%(asctime)s - %(name)s - %(levelname)s - %(messages)s',
    lwvel=logging.INFO
)

logger = logging.getLogger(__name__)


CHOOSING, GET_TEXT, GET_IMAGE = range(3)

CALLBACK1, CALLBACK2 = range(3,5)

reply_keyboard = [
    ['Show ingredients', 'Get recipes'],
    ['Remove item', 'Done'],
]
marckup = ReplyKeyboardMarckup(reply_keyboard,
                               one_time_keyboard=False)

def start(update: Update, context: CallbackContex) -> int:
    user = update.message.from_user
    logger.info(f"{user.first_name}: Start")

    context.user_data['chat_id'] = update.maeeage.chat_id

    update.message.reply_text(
        "Hi! I am you recipe bot. What ingredients do you currently have?"
        "You cam send an image or add ingredients by typing it in one or two words"
        reply_markup=markup,
    )
return CHOOSING

def get_basket_txt(list_ingredients):
    txt = 'Here are your current ingredients:\n'
    for ingredient in list_ingredients:
        txt += f'   - {ingredient}\n'
    return txt

def recived_image_information(update: Update, context: CallbackContex) -> int:
    user = update.message.from_user
    photo_phile = update.message.photo[-1].get_file()
    photo_phile.download('infer_image.png')
    logger.info("Photo of %s: %s", user.first_name, 'infer_image.png')
    update.message,reply_text(
        'Thanks the photo is being processed'
    )
    user_data = context.user_data

    ingredient = classify_image('infer_image.png')

    keyboard = [
        [
            InlineKeyboardButton(ingredient[0], callback_data=ingredient[0]),
            InlineKeyboardButton(ingredient[1], callback_data=ingredient[1]),
            InlineKeyboardButton(ingredient[2], callback_data=ingredient[2])],
        [
            InlineKeyboardButton(ingredient[3], callback_data=ingredient[3]),
            InlineKeyboardButton(ingredient[4], callback_data=ingredient[4]),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Chose the ingredients you have on your image!",
                              reply_markup=reply_markup)
    return CALLBACK1

def button1(update: Update, context: CallbackContex) -> int:
    logger.info(f":button1")
    query = update.callback_query
    query.answer()
    user_data = context.user_data
    if 'inredients_list' not in user_data:
        user_data['ingredients_list'] = [query.data]
    else:
        user_data['ingredients_list'].append(query.data)
    query.edit_message_text(text=f"Ok you selected: {query.data}")

    txt = get_basket_txt(user_data['ingredients_list'])
    context.bot.send_message(chat_id=context.user_data['chat_id'], text=txt)
    return CHOOSING

def recipes_query(update: Update, contrxt: CallBackContext) -> int:

    user = update.message.from_user
    logger.info(f"{user.first_name}: recipes_query")

    user_data = context.user_data

    input_text = ' '.join(user_data['ingredients_list'])


    cuisine = predict_ciusine(input_text)

    keyboard = [
        [
            InlineKeyboardButton(ingredient[0], callback_data=ingredient[0]),
            InlineKeyboardButton(ingredient[1], callback_data=ingredient[1]),
            InlineKeyboardButton(ingredient[2], callback_data=ingredient[2])],
        [
            InlineKeyboardButton(ingredient[3], callback_data=ingredient[3]),
            InlineKeyboardButton(ingredient[4], callback_data=ingredient[4]),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text("Chose the ingredients you have on your image!",
                              reply_markup=reply_markup)
    return CALLBACK2

def button2(update: Update, context: CallbackContex) -> int:

    logger.info(f":button2")
    query = update.callback_query
    query.answer()

    recipes = get_similar_recipes(context.user_data['ingredients_list'],
                                   query.data)
    sep = '\n\n'
    for index, row in recipes.iterrows():
        title = 'Title: ' + row['title']
        ingredients=''
        list_ing = row['ingredients'].replace('ADVERTISMENT', '').strip('][').split(', ')
        for ingredient in list_ing:
            ingredients+= ingredient.replace("'", "") + '\n'
        ingredients = 'Ingredients: ' + '\n' + ingredients
        instructions = 'Instruction: '+ '\n' + row['instructions']
        txt = title + sep + ingredients + sep + instructions
        context.bot.send_message(chat_id=context.user_data['chat_id'], text=txt)
    return CHOOSING