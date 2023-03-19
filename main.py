import json
import re
import random_responses
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


bot = Client("my_account", api_id=api_id, api_hash=api_hash)

def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")   #JSON file loaded
        return json.load(bot_responses)


# Store JSON data
response_data = load_json("bot.json")


import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re

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
        return response_data[response_index]["bot_response"]

    return "Puoi ripetere?"


# {{{ creating connection
def create_connection(host_name, user_name, user_password):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,             #host values / *modify* if you not need to connect into a local host*
            passwd="root",

            database="test"  #database name / *modify*
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred when we try to connect into db")
    return connection
connection = create_connection("localhost", "root", "")
#}}} closing the connection function

cursor = connection.cursor() #cursor /Read-only attribute describing the result of a query.


tastiera=tastiera
tastiera2=tastiera2
tastiera3=tastiera3         #keyboards
tastiera4=tastiera4
allKeyboard=allKeyboard

def prof_info(msg,bot,orario,giorno): #function to get the info about the professor
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
        bot.send_message(msg.chat.id, text="Sei nel giorno sbagliato")
        return 0

    #ciaoo
    if(orario == -1):
        Ora = currentDateTime.hour  # actual hour
    else:
        Ora = orario

    Ora -= 7              #indent for the database
    if ((Giorno != "orarioproflunedì" and Ora > 6) or Ora <= 0 or Ora > 8):  # control if the hour is correct
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
    for c in str:

        #in words
        if (c == "prima"):
            return 8
        elif (c == "seconda"):
            return 9
        elif (c == "terza"):
            return 10
        elif (c == "quarta"):
            return 11
        elif (c == "quinta"):
            tot = 12
        elif (c == "sesta"):
            return 13
        elif (c == "settima"):
            return 14
        elif (c == "ottava"):
            return 15

        #in numbers
        elif (ord(c[0]) > 47 and ord(c[0]) < 58):

            string = re.split(':', c)

            for i in string:

                if (len(i) == 2 and ord(i[1]) > 47 and ord(i[1]) < 58):
                    nulla=False
                    tot = (ord(i[0]) - 48) * 10 + (ord(i[1]) - 48)
                    break
                elif("?" in i):
                    nulla = False
                    tot = ord(i[0]) - 48
                    break

                else:
                    nulla=False
                    tot = ord(i[0]) - 48
                    break
    if(nulla): #not found
        return -1
    else:
        return tot

#searching the name of the professor
def find2(str):
    str = re.split(' ', str.upper())
    for c in str:
        for i in allKeyboard:
            for z in i:
                if (len(c)>4 and c[0]+c[1]+c[2]+c[3]+c[4] in z):
                    return z
    return 0


#searching the day
def cerca_giorno(str):
    str = re.split(' ', str.lower())
    for c in str:
        if ("luned" in c):
            return 1
        elif ("marted" in c):
            return 2
        elif ("mercoled" in c):
            return 3
        elif ("gioved" in c):
            return 4
        elif ("venerd" in c):
            return 5
        elif ("sabato" in c):
            return 6
        elif ("domenica" in c):
            return 7
    return -1



MAIN_BUTTONS = [
  ["A-C","D"],
  ["E-O","P-Z"],
  ["/help"]
               ]



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
    global MAIN_BUTTONS
    global tastiera
    global tastiera2
    global tastiera3
    global tastiera4
    global allKeyboard

    response=get_response(message.text) #get the response from the type of message requested
    temp=message.text #save the message

    if(response=="trovato"): #asking for a professor
        message.text=find2(message.text) #modify the message text to the name of the professor (to work in some functions)

        if(message.text!=0): #if the professor is found

            ora=cerca_orario(temp) #search the time

            giorno=cerca_giorno(temp) #search the day
            info=prof_info(message,bot,ora,giorno) #get the info about the professor (ora and giorno can be '-1' if not found)
            if (info == 1):
                bot.send_message(message.chat.id, text=f"Il prof {message.text.title()} è libero") #if he is free
            elif (info == 2):
                bot.send_message(message.chat.id, text=f"Il prof oggi non c'è a scuola") #if he is not in school all time
            elif (info != 0):
                bot.send_message(message.chat.id,
                                 text=f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula: {info[2]}") #if he is in school
            else:
                message.text = temp #original message
        else:
            message.text = temp #original message


    elif(message.text==-1):
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
                if(info==1):
                    bot.send_message(message.chat.id, text=f"Il prof {message.text.title()} non è in una classe") #if he is free
                elif (info==2):
                    bot.send_message(message.chat.id, text=f"Il prof oggi non c'è a scuola") #if he is not in school all time
                elif(info!=0):
                    bot.send_message(message.chat.id ,text=f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula numero: {info[2]}") #if he is in school
            else:
                bot.send_message(message.chat.id, text="Prof non trovato, ricontrolla e manda un nuovo messaggio") #if the professor is not found
    else:
        bot.send_message(message.chat.id, text=response) #send the response of type of message requested
bot.run()