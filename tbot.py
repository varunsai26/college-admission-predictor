from telegram import Update
from telegram.ext import (
    Updater, 
    CommandHandler, 
    CallbackContext, 
    ConversationHandler,
    Filters,
    MessageHandler
)
import pickle, json
import pandas as pd

filename = 'eamcet_model.sav'
model = pickle.load(open(filename, 'rb'))

df = pd.read_csv('tseamcet.csv')

feature_map = json.loads(open('feature_encoder.json', 'r').read())
# target_map = json.loads(open('target_encoder.json', 'r').read())



RANK, GENDER, CASTE, REGION = range(4)

def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Hi i am eamcet bot i can predict your college for your details'
        'enter your rank here'
    )
    
    return RANK

def rank(update: Update, context: CallbackContext) -> int:
    r = int(update.message.text)
    context.user_data['rank'] = r
    
    update.message.reply_text(
        'I see! now tell me your gender type M (male) / F (female)'
    )
    return GENDER

def gender(update: Update, context: CallbackContext) -> int:
    g = update.message.text
    context.user_data['gender'] = g
    
    update.message.reply_text(
        'Now enter your caste'
    )
    return CASTE

def caste(update: Update, context: CallbackContext) -> int:
    c = update.message.text
    context.user_data['caste'] = c
    
    update.message.reply_text(
        'Now enter your region'
    )
    return REGION

def region(update: Update, context: CallbackContext) -> int:
    r = update.message.text
    context.user_data['region'] = r
    
    testcase = [
        [
         context.user_data['rank'], 
         feature_map['gender'][context.user_data['gender']],
         feature_map['caste'][context.user_data['caste']],
         feature_map['region'][context.user_data['region']]
        ]
    ]
    
    distances, indices = model.kneighbors(testcase)
    
    result = ""
    
    
    for college in df.values[indices][0]:
        result += str(college[6]) + " " + str(college[9]) + "\n"
        
    
    update.message.reply_text(
        result
    )
    return ConversationHandler.END

def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Bye! I hope we can talk again some day.'
    )

    return ConversationHandler.END

updater = Updater('2035395431:AAGrJhHIeSo5m07CdVJw1Q3Iyy2BMjb-Fik')
dispatcher = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        RANK: [MessageHandler(Filters.text, rank)],
        GENDER: [MessageHandler(Filters.text, gender)],
        CASTE: [MessageHandler(Filters.text, caste)],
        REGION: [MessageHandler(Filters.text, region)]
    },
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(conv_handler)
updater.start_polling()
updater.idle()