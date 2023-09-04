import re

from pyrogram import filters
from pyrogram.types import ReplyKeyboardMarkup
from pyrogram import Client
import mysql.connector
from stringworksfunction import *
from datafunction import *
from keyboardsfunction import *
from telegramoutputfunction import *


bot = Client("my_account", api_id=2002222, api_hash="347b5540bacc6fd007d605760f82a72f") #entering api info

MAIN_BUTTONS = [  #main menu keyboard
  ["A-C","D"],
  ["E-O","P-Z"],
  ["/help"]
               ]
MAIN_BUTTONS = ReplyKeyboardMarkup(MAIN_BUTTONS, one_time_keyboard=True, resize_keyboard=True) #make keyboard object

connection = create_connection("localhost", "root", "")
#}}} closing the connection function

cursor = connection.cursor(buffered=True) #cursor /Read-only attribute describing the result of a query.

keyboards=keyboardsgen(cursor)
tastiera1=keyboards[0]
tastiera2=keyboards[1]
tastiera3=keyboards[2]
tastiera4=keyboards[3]
allKeyboard=keyboards[4]

polliceInSu='\U0001F44D'
polliceInGiù='\U0001F44E'

response_data = load_json("bot.json")
@bot.on_message(filters.command(commands=['start']))  # start
def start(client, message):
    message.reply(
        text="Benvenuto! Usa questo bot per scoprire dove si trova un professore, per ogni aiuto usa /help, avrai anche una lista di comandi",
        reply_markup=MAIN_BUTTONS)


@bot.on_message(filters.command(commands=['help']))
def help(client, message):
    message.reply(
        text="Ehi, usa il bot per cercare l'aula in cui si trova un professore \n\n Comandi:\n \n/start - Il bot inizia, puoi usarlo per far apparire i pulsanti \n/find - cerca un professore \n/help - info e lista comandi \n\nChiedimi dove s trova un professore(Es. Dove si trova Acciavatti Cristiano alla quarta ora di venerdi?) \n \nPer aiuto o feedback scrivi al numero: \n +39 3924502802 \n ",
        reply_markup=MAIN_BUTTONS)


@bot.on_message(filters.command(commands=['find']))  # find a profesor from a part of a name
def find(client, message):
    newKeyboard = []  # prepere the keyboard where the user see the result
    for c in range(0, len(allKeyboard)):
        newKeyboard.append([])

    trovato = False
    cnt = 0
    message.text = re.sub("/find ", "", message.text)  # remove /find
    message.text = message.text.upper()

    for element in allKeyboard:  # for each name in the keyboard

        nomeseparato = re.split(" ",
                                element)  # split the name into a list of words (ex. "Cristiano Acciavatti" -> ["Cristiano","Acciavatti"])

        for nome in nomeseparato:  # for each word in the name
            if (similarity(message.text, nome) > 40 and len(
                    nome) > 2):  # if the similarity is >40 and the word is >2 characters(so no "DI" or "DE")
                trovato = True
                newKeyboard[cnt].append(element)  # add the name to the keyboard that will be shown to the user
                cnt += 1
    if trovato:  # if we found something
        reply_markup = ReplyKeyboardMarkup(newKeyboard, one_time_keyboard=True,
                                           resize_keyboard=True)  # create the keyboard object
        message.reply(text="Habbiamo trovato questi risultati, sceglierne uno per vedere dove si trova ora:",
                      reply_markup=reply_markup)  # send the keyboard
    else:
        message.reply(text="Non ho trovato nulla, prova a darci piu lettere :_( ",
                      reply_markup=MAIN_BUTTONS)  # if we don't found anything


@bot.on_message(filters.text)
def Main(client, message):
    global cursor
    global feedmessage
    global feedresponse
    global feedbot
    global connection

    if (message.text == polliceInSu or message.text == polliceInGiù):  # if the message is a thumbs up or down, so if the user give a feedback
        addLog(connection,cursor,message,feedmessage,feedresponse,feedbot)  # add the log
        bot.send_message(message.chat.id, text="Grazie per il feedback!")

    # if the user is using buttons and want to search a professor
    elif (message.text == "A-C"):
        message.reply(text="Button:", reply_markup=tastiera1)

    elif (message.text == "D"):
        message.reply(text="Button:", reply_markup=tastiera2)

    elif (message.text == "E-O"):
        message.reply(text="Button:", reply_markup=tastiera3)

    elif (message.text == "P-Z"):
        message.reply(text="Button:", reply_markup=tastiera4)

    elif (message.text == "<<<---------"):
        message.reply(text="Button:", reply_markup=MAIN_BUTTONS)

    # if is not a menu navigation and not a feedback
    else:
        response = get_response(message.text,
                                response_data)  # get the type of message and the response(usable if he isn't asking a professor)

        type = response[1]  # get the type of message
        response = response[0]  # get the response

        daibottoni = FindIfOnlyName(message.text, allKeyboard)
        if (response == "ricerca professore" or daibottoni):  # if is searching a professor
            output=sand(connection,cursor, message,type, daibottoni,bot)
            feedbot=output[0]
            feedresponse=output[1]
            feedmessage=output[2]
        else:  # if the message else
            output=sandOne(connection,cursor,message, type, response,bot)
            feedbot = output[0]
            feedresponse = output[1]
            feedmessage = output[2]


bot.run()  # run the bot