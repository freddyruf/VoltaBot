import json
import re
from pyrogram import filters
from dettails import api_hash 
from dettails import api_id

from keyboards import tastiera
from keyboards import tastiera2
from keyboards import tastiera3
from keyboards import tastiera4
from keyboards import allKeyboard

import tgcrypto
import random
import time
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from pyrogram import Client

import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re


bot = Client("my_account", api_id=api_id, api_hash=api_hash)

feedmessage=""
feedresponse=""
feedbot=""

polliceInSu='\U0001F44D'
polliceInGiù='\U0001F44E'
risposta= ""


tastiera=tastiera
tastiera2=tastiera2
tastiera3=tastiera3         #keyboards
tastiera4=tastiera4
allKeyboard=allKeyboard

from Levenshtein import distance

import editdistance




def similarity(string1, string2):
    max_length = max(len(string1), len(string2))
    if max_length == 0:
        percent_distance = 0
    else:
        distance = editdistance.eval(string1, string2)
        percent_distance = 100 * (max_length - distance) / max_length
    return percent_distance
def closest_substring(string, matrix):
    words = string.split()
    n = len(words)
    closest = None
    min_distance = 0
    for i in range(n-1):
        substring = words[i] + ' ' + words[i+1]
        for row in matrix:
            for element in row:
                d = similarity(element, substring)
                if d > min_distance and d > 70:
                    min_distance = d
                    closest = element
    if closest is None:
        for c in words: #entro nella lista di parole
            for i in matrix: #entro nella lista di liste di tasti
                for z in i: #entro nella lista di tasti
                    if (len(c)>4 and c[0]+c[1]+c[2]+c[3]+c[4] in z):
                        return z
    return closest

def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")   #JSON file loaded
        return json.load(bot_responses)
# Store JSON data
response_data = load_json("bot.json")


#function to find the type of message
def get_response(input_string):
    split_message = re.split(r'\s+|[,;?!.-]\s*', input_string.lower())
    score_list = []

    # Check all the responses
    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response["required_words"]

        # Check if there are any required words
        if required_words:
            for word in split_message:
                if word in required_words:
                    required_score += 1

        # Amount of required words should match the required score
        if required_score == len(required_words):
            # print(required_score == len(required_words))
            # Check each word the user has typed
            for word in split_message:
                # If the word is in the response, add to the score
                if word in response["user_input"]:
                    response_score += 1

        # Add score to list
        score_list.append(response_score)
        # Debugging: Find the best phrase
        # print(response_score, response["user_input"])

    # Find the best response and return it if they're not all 0
    best_response = max(score_list)
    response_index = score_list.index(best_response)

    # Check if input is empty
    if input_string == "":
        return -1

    # If there is no good response, return a random one.
    if best_response != 0:
        rt=["",""]
        rt[0] = response_data[response_index]["bot_response"]
        rt[1] = response_data[response_index]["response_type"]
        return rt

    return "Puoi ripetere?"


# {{{ creating connection
connection = None
def create_connection(host_name, user_name, user_password):
    global connection
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,             #host values / *modify* if you not need to connect into a local host*

            database="prova"  #database name / *modify*
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred when we try to connect into db")
    return connection
connection = create_connection("localhost", "root", "")
#}}} closing the connection function

cursor = connection.cursor(buffered=True) #cursor /Read-only attribute describing the result of a query.


def addLog(message):  # function to add the log into the database
    global cursor
    global connection
    global feedbot
    global feedresponse
    global feedmessage


    now = datetime.now()
    # Ottenere la data attuale come stringa nel formato 'YYYY-MM-DD'
    date_str = now.strftime('%Y-%m-%d')

    # Ottenere l'ora attuale come stringa nel formato 'HH:MM:SS'
    time_str = now.strftime('%H:%M:%S')

    timeinfo = date_str + " " + time_str # time info

    if (message.text == polliceInSu): # if the user give a feedback
        feed = 1
    elif (message.text == polliceInGiù): # if the user give a feedback
        feed = 0
    else: # if the user don't give a feedback
        feed = None

    if (feed!=None): # if the user give a feedback
        cursor.execute(
            f"INSERT INTO log (tempo, usertext, requestinfo, responsetext, feedback) VALUES ('{timeinfo}', '{feedmessage}','{feedresponse}', '{feedbot}', {feed});")

    else: # if the user don't give a feedback
        cursor.execute(
            f"INSERT INTO log (tempo, usertext, requestinfo, responsetext) VALUES ('{timeinfo}', '{feedmessage}','{feedresponse}', '{feedbot}');")

    connection.commit() # commit the changes

def addLogInfo(message,response, risposta): # function to prepare the log into the database
    global feedbot
    global feedresponse
    global feedmessage

    feedmessage = message.text
    feedresponse = response
    feedbot = risposta


def feedbacktry(message,response,risposta,emojiKeyboard,bot): # function to not always ask the user if he wants to give a feedback
    global feedmessage
    global feedresponse
    global feedbot

    global polliceInSu
    global polliceInGiù


    if (random.randint(1, 5) == 1): # 1/5 chance to ask the user if he wants to give a feedback
        bot.send_message(message.chat.id, text="Potresti darci un feedback? " + polliceInSu + " o " + polliceInGiù,
                         reply_markup=emojiKeyboard)  # ask the user what he wants to do
        feedmessage = message.text # save the message
        feedresponse = response
        feedbot = risposta
        return True
    else:
        return False




def prof_info(msg,bot,orario,giorno): #function to get the info about the professor
    global risposta
    global cursor
    cursor.execute(f"SELECT ID FROM professori WHERE Nome = '{msg.text}'")
    PROF_ID = cursor.fetchall()  # id prof

    PROF_ID = PROF_ID[0][0]
    currentDateTime = datetime.now()  # actual date and time


    if(giorno == -1):
        Giorno = currentDateTime.isoweekday()  # day of the week
    else:
        Giorno = giorno
    if (Giorno == 1):
        Giorno = "orarioproflunedì"
    elif (Giorno == 2):
        Giorno = "orarioprofmartedì"
    elif (Giorno == 3):
        Giorno = "orarioprofmercoledì"
    elif (Giorno == 4):
        Giorno = "orarioprofgiovedì"
    elif (Giorno == 5):
        Giorno = "orarioprofvenerdì"
    else:
        risposta= "Sei nel giorno sbagliato"
        bot.send_message(msg.chat.id, text="Sei nel giorno sbagliato")
        return 0

    #ciaoo
    if(orario == -1):
        Ora = currentDateTime.hour  # actual hour
    else:
        Ora = orario

    Ora -= 7              #indent for the database
    if ((Giorno != "orarioproflunedì" and Ora > 6) or Ora <= 0 or Ora > 8):  # control if the hour is correct
        risposta='Ora sbagliata!'
        bot.send_message(msg.chat.id, text="Ora sbagliata!")
        return 0
    if (Ora == 1):
        Ora = "primaOra"
    elif (Ora == 2):
        Ora = "secondaOra"
    elif (Ora == 3):
        Ora = "terzaOra"
    elif (Ora == 4):
        Ora = "quartaOra"
    elif (Ora == 5):
        Ora = "quintaOra"
    elif (Ora == 6):
        Ora = "sestaOra"
    elif (Ora == 7):
        Ora = "settimaOra"
    elif (Ora == 8):
        Ora = "ottavaOra"



    cursor.execute(f"SELECT {Ora} FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
    Classe = cursor.fetchall()  # class found
    Classe = Classe[0][0]
    if(Classe=="libero" or Classe=="Libero"):   #control if the professor is free all hours
        cursor.execute(f"SELECT primaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        prima = cursor.fetchall()

        cursor.execute(f"SELECT secondaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        seconda = cursor.fetchall()

        cursor.execute(f"SELECT terzaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        terza = cursor.fetchall()

        cursor.execute(f"SELECT quartaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        quarta = cursor.fetchall()

        cursor.execute(f"SELECT quintaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        quinta = cursor.fetchall()

        cursor.execute(f"SELECT sestaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")
        sesta = cursor.fetchall()
        #control if the professor is free all hours
        if (prima[0][0]=="libero" and seconda[0][0]=="libero" and terza[0][0]=="libero" and quarta[0][0]=="libero" and quinta[0][0]=="libero" and sesta[0][0]=="libero"): return 2
        elif (prima[0][0]=="Libero" and seconda[0][0]=="Libero" and terza[0][0]=="Libero" and quarta[0][0]=="Libero" and quinta[0][0]=="Libero" and sesta[0][0]=="Libero"): return 2

        return 1 #only the hour


    cursor.execute(f"SELECT IDaula FROM classi WHERE classe = '{Classe}'") # id aula
    IDAula = cursor.fetchall()
    IDAula = IDAula[0][0]

    cursor.execute(f"SELECT Palazzina,Piano,Aula FROM aule WHERE ID ='{IDAula}'") # info aula
    Aula = cursor.fetchall()  # catch the info about the class
    Palazzina = Aula[0][0]
    Piano = Aula[0][1]
    nAula = Aula[0][2]
    result = [Palazzina,Piano,nAula]
    return result

def cerca_orario(str): #function to find the hour in the string
    str = re.split(' ', str.lower())
    tot = 0
    nulla=True
    for c in str: #for each word in the string in

        # words
        if (c == "prima"): #if the word is "prima" the hour is 1
            return 8
        elif (c == "seconda"): #if the word is "seconda" the hour is 2
            return 9
        elif (c == "terza"): #if the word is "terza" the hour is 3
            return 10
        elif (c == "quarta"): #if the word is "quarta" the hour is 4
            return 11
        elif (c == "quinta"): #if the word is "quinta" the hour is 5
            return 12
        elif (c == "sesta"): #if the word is "sesta" the hour is 6
            return 13
        elif (c == "settima"): #if the word is "settima" the hour is 7
            return 14
        elif (c == "ottava"): #if the word is "ottava" the hour is 8
            return 15

        #in numbers
        elif (ord(c[0]) > 47 and ord(c[0]) < 58): #if the first char is a number

            string = re.split(':', c) #split the string in the char ":"

            for i in string: #for each element in the list
                if (len(i) == 2 and ord(i[1]) > 47 and ord(i[1]) < 58):  #if the element is a number
                    nulla=False
                    tot = (ord(i[0]) - 48) * 10 + (ord(i[1]) - 48) #convert the string in a number
                    break
                elif("?" in i): #if the element is a "?" the hour is the frist number
                    nulla = False
                    tot = ord(i[0]) - 48
                    break
                else:
                    nulla=False
                    tot = ord(i[0]) - 48
                    break

    if(nulla): #not found
        return -1
    else: #found
        return tot

#searching the name of the professor
def find2(str):
    name=closest_substring(str.upper(), allKeyboard)
    # str = re.split(' ', str.upper())
    # for c in str: #entro nella lista di parole
    #     for i in allKeyboard: #entro nella lista di liste di tasti
    #         for z in i: #entro nella lista di tasti
    #             if (len(c)>4 and c[0]+c[1]+c[2]+c[3]+c[4] in z):
    #                 return z
    if (name == None):
        return 0
    else: return name


#searching the day
def cerca_giorno(str):
    str = re.split(' ', str.lower()) #split the string in the char " "
    for c in str:
        if ("luned" in c): #if the word is "lunedì" the day is 1
            return 1
        elif ("marted" in c): #if the word is "martedì" the day is 2
            return 2
        elif ("mercoled" in c): #if the word is "mercoledì" the day is 3
            return 3
        elif ("gioved" in c): #if the word is "giovedì" the day is 4
            return 4
        elif ("venerd" in c):   #if the word is "venerdì" the day is 5
            return 5
        elif ("sabato" in c): #if the word is "sabato" the day is 6
            return 6
        elif ("domenica" in c): #if the word is "domenica" the day is 7
            return 7
    return -1



MAIN_BUTTONS = [
  ["A-C","D"],
  ["E-O","P-Z"],
  ["/help"]
               ]


#telegram functions

@bot.on_message(filters.command(commands=['start']))   #start
def start(client,message):
    global MAIN_BUTTONS
    reply_markup=ReplyKeyboardMarkup(MAIN_BUTTONS,one_time_keyboard=True,resize_keyboard=True)
    message.reply(text="Benvenuto! Usa questo bot per scoprire dove si trova un professore, per ogni aiuto usa /help, avrai anche una lista di comandi", reply_markup=reply_markup)

@bot.on_message(filters.command(commands=['help']))
def help(client,message):
    global MAIN_BUTTONS
    reply_markup=ReplyKeyboardMarkup(MAIN_BUTTONS,one_time_keyboard=True,resize_keyboard=True)
    message.reply(text="Comandi:\n \n/start - Il bot inizia, puoi usarlo per far apparire i pulsanti \n/find - cerca un professore \n/help - info e lista comandi \n/clear - per resettare la chat \n \nPer aiuto o feedback scrivi al numero: \n +39 3924502802 \n ", reply_markup=reply_markup)


@bot.on_message(filters.command(commands=['clear'])) #???
def easteregg(client,message):
    bot.send_message(message.chat.id, text="Federico Ruffini")

@bot.on_message(filters.command(commands=['find'])) #find a proffesor
def find(client,message):
  global allKeyboard
  newKeyboard=[]
  for c in range(0,len(allKeyboard)):
    newKeyboard.append([""])

  trovato=False
  cnt=0
  text=message.text
  text=re.sub("/find ", "", text) #remove /find
  text=text.upper()
  for i in range(0,len(allKeyboard)):
    if (text in allKeyboard[i][0]):
      trovato=True
      newKeyboard[cnt][0]=allKeyboard[i][0]
      cnt+=1
  if trovato:
    reply_markup=ReplyKeyboardMarkup(newKeyboard,one_time_keyboard=True,resize_keyboard=True)
    message.reply(text="Habbiamo trovato questi risultati, sceglierne uno:",reply_markup=reply_markup)
  else:
    global MAIN_BUTTONS
    reply_markup=ReplyKeyboardMarkup(MAIN_BUTTONS,one_time_keyboard=True,resize_keyboard=True)
    message.reply(text="Non ho trovato nulla :_( ",reply_markup=reply_markup)
  
      

@bot.on_message(filters.text)

def Main(client,message):
    #thumbs up and down unicode
    global polliceInSu
    global polliceInGiù
    emojiKey=[[polliceInSu,polliceInGiù]]
    emojiKeyboard = ReplyKeyboardMarkup(emojiKey, one_time_keyboard=True, resize_keyboard=True)

    global MAIN_BUTTONS
    global tastiera
    global tastiera2
    global tastiera3
    global tastiera4
    global allKeyboard

    global feedbot
    global feedresponse
    global feedmessage

    global risposta

    continuaricerca=True

    if(message.text==polliceInSu or message.text==polliceInGiù): #if the message is a thumbs up or down
        addLog(message) #add the log
        bot.send_message(message.chat.id, text="Grazie per il feedback!", reply_markup=ReplyKeyboardMarkup(MAIN_BUTTONS,one_time_keyboard=True,resize_keyboard=True))
        return 0


    response=get_response(message.text) #get the response from the type of message requested
    type=response[1] #get the type of message
    response=response[0] #get the response

    temp=message.text #save the message


    if(response=="trovato" and continuaricerca): #asking for a professor
        message.text=find2(message.text) #modify the message text to the name of the professor (to work in some functions)

        if(message.text!=0): #if the professor is found

            ora=cerca_orario(temp) #search the time

            giorno=cerca_giorno(temp) #search the day

            info=prof_info(message,bot,ora,giorno) #get the info about the professor (ora and giorno can be '-1' if not found)

            if (info == 1): #if he is free
                bot.send_message(message.chat.id, text=f"Il prof {message.text.title()} è libero") #if he is free
                risposta=f"Il prof {message.text.title()} è libero"

            elif (info == 2): #if he is not in school
                bot.send_message(message.chat.id, text=f"Il prof oggi non c'è a scuola") #if he is not in school all time
                risposta=f"Il prof oggi non c'è a scuola"

            elif (info != 0): #if he is in school
                bot.send_message(message.chat.id,
                                 text=f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula: {info[2]}") #if he is in school
                risposta=f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula: {info[2]}"

            message.text=temp #original message
            feeding=feedbacktry(message, type, risposta, emojiKeyboard, bot) #ask for feedback
            if (feeding):
                return 0 #if the user wants to give feedback, stop the function

        message.text = temp #original message
        addLogInfo(message, type, risposta) #add the log
        addLog(message) #add the log into db
        return 0 #stop the function



    elif(response=="Puoi ripetere?" and continuaricerca):
        tastieraPrima=ReplyKeyboardMarkup(tastiera,one_time_keyboard=True,resize_keyboard=True)
        tastieraSeconda=ReplyKeyboardMarkup(tastiera2,one_time_keyboard=True,resize_keyboard=True) #set the keyboards
        tastieraTerza=ReplyKeyboardMarkup(tastiera3,one_time_keyboard=True,resize_keyboard=True)
        tastieraQuarta=ReplyKeyboardMarkup(tastiera4,one_time_keyboard=True,resize_keyboard=True)
        reply_markup=ReplyKeyboardMarkup(MAIN_BUTTONS,one_time_keyboard=True,resize_keyboard=True)


        if(message.text=="A-C"): #if the user choose a keyboard
          message.reply(text="Dimmi un nome:",reply_markup=tastieraPrima)
        elif(message.text=="D"):
          message.reply(text="Dimmi un nome:",reply_markup=tastieraSeconda)
        elif(message.text=="E-O"):
          message.reply(text="Dimmi un nome:",reply_markup=tastieraTerza)
        elif(message.text=="P-Z"):
          message.reply(text="Dimmi un nome:",reply_markup=tastieraQuarta)
        elif(message.text=="<<<---------"):
          message.reply(text="Indietro:",reply_markup=reply_markup)

        else:
            cercare=False
            for i in allKeyboard: #search the professor
                if(message.text in i[0]): cercare=True

            if(cercare): #if the professor is found
                info=prof_info(message,bot,-1,-1) #get the info about the professor for today in this moment

                if(info==1): #if he is free
                    bot.send_message(message.chat.id, text=f"Il prof {message.text.title()} non è in una classe") #if he is free
                    risposta=f"Il prof {message.text.title()} non è in una classe"

                elif (info==2): #if he is not in school
                    bot.send_message(message.chat.id, text=f"Il prof oggi non c'è a scuola") #if he is not in school all time
                    risposta=f"Il prof oggi non c'è a scuola"

                elif(info!=0): #if he is in school
                    bot.send_message(message.chat.id ,text=f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula numero: {info[2]}") #if he is in school
                    risposta=f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula numero: {info[2]}"

            else: #if the professor is not found
                bot.send_message(message.chat.id, text="Prof non trovato, ricontrolla e manda un nuovo messaggio") #if the professor is not found
                risposta="Prof non trovato, ricontrolla e manda un nuovo messaggio"

            feeding = feedbacktry(message, type, risposta, emojiKeyboard, bot) #ask for feedback
            if (feeding):
                return 0 #if the user wants to give feedback, stop the function
            addLogInfo(message, type, risposta) #add the log
            addLog(message) #add the log into db
            return 0 #stop the function

    else:
        if (continuaricerca): #if the user isn't asking for a professor
            bot.send_message(message.chat.id, text=response) #send the response of type of message requested
            risposta = response #save the response
            feeding = feedbacktry(message, type, risposta, emojiKeyboard, bot) #ask for feedback
            if (feeding):
                return 0 #if the user wants to give feedback, stop the function

            addLogInfo(message, type, risposta) #add the log
            addLog(message) #add the log into db
            return 0 #stop the function



bot.run() #run the bot