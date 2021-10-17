import logging
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove,Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)
import pickle, json

import html
import pdfkit
#from datetime import datetime


import pandas as pd
# from telegram.files.document import Document
#loading model
filename = 'eamcet_model.sav'
model = pickle.load(open(filename, 'rb'))

df = pd.read_csv('tseamcet.csv')

feature_map = json.loads(open('feature_encoder.json', 'r').read())




RANK, GENDER, CASTE,REGION= range(4)


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Hi i am eamcet bot i can predict your college from your details\nenter your rank here'
    )
    
    return RANK

def rank(update: Update, context: CallbackContext) -> int:
    r = int(update.message.text)
    context.user_data['rank'] = r
    user = update.message.from_user
    logger.info("User %s : %d rank  .",user.first_name,r)
    reply_keyboard=[['M','F']]
    update.message.reply_text(
        'Are you a Male Or Female?',
    reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='Male or Female?'
        ),
    )
   
    return GENDER

def gender(update: Update, context: CallbackContext) -> int:
    g = update.message.text
    context.user_data['gender'] = g
    user = update.message.from_user
    logger.info("User %s : %s gender  .",user.first_name, g)
    
    update.message.reply_text(
    'Now enter your caste\n ',
     reply_markup=ReplyKeyboardRemove(),
     )
     
    return CASTE


def caste(update: Update, context: CallbackContext) -> int:
    c=update.message.text.upper()
    context.user_data['caste'] = c
    user = update.message.from_user
    logger.info("User %s : %s caste .",user.first_name, c)
    reply_keyboard=[['OU','SVU','AU']]
    update.message.reply_text(
        'Are you a Male Or Female?',
    reply_markup=ReplyKeyboardMarkup(
        reply_keyboard, one_time_keyboard=True, input_field_placeholder='OU, SVU AU?'
        ),
    )
    return REGION

def region(update: Update, context: CallbackContext) -> int:
    r=update.message.text
    context.user_data['region'] = r
    user = update.message.from_user
    logger.info("User %s : %s region .",user.first_name, r)
    testcase = [
        [
         context.user_data['rank'], 
         feature_map['gender'][context.user_data['gender']],
         feature_map['caste'][context.user_data['caste']],
         feature_map['region'][context.user_data['region']],
        ]
     ]
    #k-nn
    distances, indices = model.kneighbors(testcase)
    
    
    

    indices = list(indices).pop()
    print(indices)
    #filename = str(datetime.now())

    df1=df.iloc[indices, [6,9]]

    def html_(txt):

        res = f'''
            <html>
                <head><title>colleges</title></title>
                <body>
                    {txt}
                </body>
            </html>
        '''
        return html.unescape(res)
    #dataframe to html
    text_file = open("index1.html", "w")
    text_file.write(html_(df1.to_html(index=False,justify='center')))
    text_file.close()
   #html to pdf
    path_wkhtmltopdf = r'C:/Users/*****/Desktop/mypr/Lib/site-packages/wkhtmltopdf/bin/wkhtmltopdf.exe'#enter your package location
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
    pdfkit.from_file('index1.html', '**********colleges.pdf', configuration=config)#ENTER THE pdf location
    update.message.reply_text('wait sending a file ...!'),
    context.bot.sendDocument(update.effective_chat.id,document=open('./colleges.pdf','rb')),
    
    update.message.reply_text('Thank you! for using College Admission Predictor.')
    return ConversationHandler.END

    
    
    



def cancel(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

updater = Updater('2037942965:AAFoVN74XTF2ohX4REvtgFXPoCxs-KIPxuM')
dispatcher = updater.dispatcher

conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start)],
    states={
        RANK: [MessageHandler(Filters.text, rank)],
        GENDER: [MessageHandler(Filters.text, gender)],
        CASTE: [MessageHandler(Filters.text, caste)],
        REGION:[MessageHandler(Filters.text,region),]
        
    },
    
    fallbacks=[CommandHandler('cancel', cancel)]
)

dispatcher.add_handler(conv_handler)
# updater.dispatcher.add_handler(CallbackQueryHandler(button))
updater.start_polling()
updater.idle()
