



"""

Info:
    When appare message, response and risposta they mean:
        - message: the message that the user send
        - response: the type of the message that the user sand
        - risposta: the response that the bot send to the user

Authors:
    - Ruffini Federico
    - De Amicis Andrea
Project:
    - NAO Challenge 2023
Place:
    - I.I.S. A. Volta Pescara
Repository:
    - https://github.com/freddyruf/VoltaBot

"""




from pyrogram import filters
import random
from pyrogram.types import ReplyKeyboardMarkup
from pyrogram import Client
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import re
import json
import editdistance




bot = Client("my_account", api_id=2002222, api_hash="347b5540bacc6fd007d605760f82a72f") #entering api info


feedmessage=""
feedresponse=""
feedbot=""

polliceInSu='\U0001F44D'
polliceInGiù='\U0001F44E'
risposta= ""



tastiera1=[["<<<---------"]]
tastiera=[["<<<---------"]]        #keyboards for the *from button input*
tastiera2=[["<<<---------"]]
tastiera3=[["<<<---------"]]       #with "<<<---------" the user will be able to go back to the main menu
tastiera4=[["<<<---------"]]
allKeyboard=[]

#keyboard with emoji for the feedback
emojiKey=[[polliceInSu,polliceInGiù]]
emojiKeyboard = ReplyKeyboardMarkup(emojiKey, one_time_keyboard=True, resize_keyboard=True) #make keyboard object


MAIN_BUTTONS = [  #main menu keyboard
  ["A-C","D"],
  ["E-O","P-Z"],
  ["/help"]
               ]
MAIN_BUTTONS = ReplyKeyboardMarkup(MAIN_BUTTONS, one_time_keyboard=True, resize_keyboard=True) #make keyboard object



#entering into jeson file for the fuction that search argument from a phrase
def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")
        return json.load(bot_responses)
# Store JSON data
response_data = load_json("bot.json")



# {{{ creating connection
connection = None
def create_connection(host_name, user_name, user_password):
    global connection
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,             #host values / *modify* if you not need to connect into a local host*

            database="docenti"  #database name / *modify*
        )
        print("Connection to MySQL DB successful")
    except Error as e:
        print(f"The error '{e}' occurred when we try to connect into db")
    return connection
connection = create_connection("localhost", "root", "")
#}}} closing the connection function

cursor = connection.cursor(buffered=True) #cursor /Read-only attribute describing the result of a query.
def keyboardsgen():
    global tastiera1
    global tastiera2
    global tastiera3
    global tastiera4
    global allKeyboard


    cursor.execute("SELECT Nome FROM professori")
    cnt=0
    allKeyboard0 = cursor.fetchall()
    allKeyboard1=[]
    for element in allKeyboard0:
        string=str(element)
        allKeyboard1.append(string.removeprefix("('").removesuffix("',)"))
    for element in allKeyboard1:
        allKeyboard.append(element)

    fineUno = allKeyboard.index("D`ALESSANDRO AURA")
    fineDue = allKeyboard.index("EVANGELISTA FILIPPO")
    fineTre = allKeyboard.index("PAGLIARA DANIELA")
    fineQuattro = allKeyboard.index("ZENONI CRISTINA")+1

    for i in range(0, fineUno):
        tastiera1.append([allKeyboard[i]]) # [ ] beacous it need to be a (1,len) matrix
    for i in range(fineUno, fineDue):
        tastiera2.append([allKeyboard[i]])
    for i in range(fineDue, fineTre):
        tastiera3.append([allKeyboard[i]])
    for i in range(fineTre, fineQuattro):
        tastiera4.append([allKeyboard[i]])

    tastiera1=ReplyKeyboardMarkup(tastiera1, one_time_keyboard=True, resize_keyboard=True) #make keyboard object
    tastiera2 = ReplyKeyboardMarkup(tastiera2, one_time_keyboard=True, resize_keyboard=True) #make keyboard object
    tastiera3 = ReplyKeyboardMarkup(tastiera3, one_time_keyboard=True, resize_keyboard=True) #make keyboard object
    tastiera4 = ReplyKeyboardMarkup(tastiera4, one_time_keyboard=True, resize_keyboard=True) #make keyboard object

keyboardsgen()

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
            # Check each word the user has typed
            for word in split_message:
                # If the word is in the response, add to the score
                if word in response["user_input"]:
                    response_score += 1
        # Add score to list
        score_list.append(response_score)
        # Debugging: Find the best phrase

    # Find the best response and return it if they're not all 0
    best_response = max(score_list)
    response_index = score_list.index(best_response)

    # Check if input is empty
    if input_string == "":
        return -1


    if best_response != 0:
        rt=["",""]
        rt[0] = response_data[response_index]["bot_response"] #return the response
        rt[1] = response_data[response_index]["response_type"] #return the type of response
        return rt
    else:
        # If there is no good response, return errore
        return ["Puoi ripetere?","errore"]
    #we need both the response and the type for some function when the message for the user is bot_response

def addLog(message):  # function to add the log element into the database
    global cursor
    global connection


    now = datetime.now()
    # Obtain actual date with format 'YYYY-MM-DD'
    date_str = now.strftime('%Y-%m-%d')

    # Obtain actual hours with format 'HH:MM:SS'
    time_str = now.strftime('%H:%M:%S')

    timeinfo = date_str + " " + time_str # setup time for SQL datetime syntax

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

def addLogInfo(message,response, risposta): # function to prepare the log element into the database (not sanding)
    global feedbot
    global feedresponse
    global feedmessage

    feedmessage = message.text
    feedresponse = response
    feedbot = risposta


def feedbacktry(message,response,risposta): # function to not always ask the user if he wants to give a feedback
    global feedmessage
    global feedresponse
    global feedbot


    if (random.randint(1, 5) == 1): # 1/5 chance to ask the user if he wants to give a feedback
        bot.send_message(message.chat.id, text="Potresti darci un feedback? " + polliceInSu + " o " + polliceInGiù,
                         reply_markup=emojiKeyboard)  # ask the user what he wants to do
        # save the message info
        feedmessage = message.text
        feedresponse = response
        feedbot = risposta
        return True
    else:
        return False

def similarity(string1, string2): # function to calculate the similarity between two strings
    max_length = max(len(string1), len(string2)) # calculate the max length between the two strings

    if max_length == 0: # if the max length is 0
        percent_distance = 0 # the distance is 0

    else: # if the max length is not 0
        distance = editdistance.eval(string1, string2) # calculate the distance between the two strings
        percent_distance = 100 * (max_length - distance) / max_length # convert into %
    return percent_distance

def closest_substring(string, list):
    words = string.split() #divide the string into a list of words
    n = len(words)
    closest = None
    min_distance = 0 #minimum distance that bot have found

    for i in range(n-1): #for each word in the list
        substring = words[i] + ' ' + words[i+1] #take the word and the next one

        for element in list: #for each row in the list
            d = similarity(element, substring)
            if d > min_distance and d > 70:
                min_distance = d
                closest = element

    if closest is None:
        for c in words: #for evry word in the list
            for element in list: #for each element in the list
                    if (len(c)>4 and c[0]+c[1]+c[2]+c[3]+c[4] in element):
                        return element
    return closest


def prof_info(msg,orario,giorno): #function to get the info about the professor
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
        return risposta


    if(orario == -1):
        Ora = currentDateTime.hour  # actual hour
    else:
        Ora = orario

    Ora -= 7              #indent for the database
    if ((Giorno != "orarioproflunedì" and Ora > 6) or Ora <= 0 or Ora > 8):  # control if the hour is correct
        risposta='Ora sbagliata!'
        bot.send_message(msg.chat.id, text="Ora sbagliata!")
        return risposta
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
    if (name == None):
        return 0
    else: return name

def findsolonome(str):
    str = re.split(' ', str.upper())
    if len(str)>3:
        return False
    for c in str: #entro nella lista di parole
        for i in allKeyboard: #entro nella lista di liste di tasti
            if (len(c)>4 and c[0]+c[1]+c[2]+c[3]+c[4] in i):
                return i
    return False

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

def invia(message,type,inQuestoMomento):
    original_message= message.text
    message.text = find2(
        message.text)  # modify the message text to the name of the professor (to work in some functions)

    if (inQuestoMomento):
        ora=-1
        giorno=-1
    else:
        ora = cerca_orario(original_message)  # search the time
        giorno = cerca_giorno(original_message)  # search the day

    info = prof_info(message, ora,
                     giorno)  # get the info about the professor (ora and giorno can be '-1' if not found)

    if (info == 1):  # if he is free
        bot.send_message(message.chat.id, text=f"Il prof {message.text.title()} è libero")  # if he is free
        risposta = f"Il prof {message.text.title()} è libero"

    elif (info == 2):  # if he is not in school
        bot.send_message(message.chat.id,
                         text=f"Il prof oggi non c'è a scuola")  # if he is not in school all time
        risposta = f"Il prof oggi non c'è a scuola"
    elif (info == "Sei nel giorno sbagliato!" or info=="Ora sbagliata!"):  # if the name is not correct
        risposta=info
    else:  # if he is in school
        bot.send_message(message.chat.id,
                         text=f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula: {info[2]}")  # if he is in school
        risposta = f"Il prof {message.text.title()} si trova in: \nPalazzina: {info[0]} \nPiano: {info[1]} \nAula: {info[2]}"


    message.text = original_message  # original message
    feeding = feedbacktry(message, type, risposta)  # ask for feedback
    if (feeding):
        return 0  # if the user wants to give feedback, stop the function

    message.text = original_message  # original message
    addLogInfo(message, type, risposta)  # add the log
    addLog(message)  # add the log into db

def inviasingolo(message,type,response):
    global risposta
    bot.send_message(message.chat.id, text=response)  # send the response of type of message requested
    risposta = response  # save the response

    feeding = feedbacktry(message, type, risposta)  # ask for feedback
    if (feeding):
        return 0  # if the user wants to give feedback, stop the function
    addLogInfo(message, type, risposta)  # add the log
    addLog(message)  # add the log into db
    return 0  # stop the function


#telegram functions

@bot.on_message(filters.command(commands=['start']))   #start
def start(client,message):
    message.reply(text="Benvenuto! Usa questo bot per scoprire dove si trova un professore, per ogni aiuto usa /help, avrai anche una lista di comandi", reply_markup=MAIN_BUTTONS)

@bot.on_message(filters.command(commands=['help']))
def help(client,message):
    message.reply(text="Comandi:\n \n/start - Il bot inizia, puoi usarlo per far apparire i pulsanti \n/find - cerca un professore \n/help - info e lista comandi \n/clear - per resettare la chat \n \nPer aiuto o feedback scrivi al numero: \n +39 3924502802 \n ", reply_markup=MAIN_BUTTONS)


@bot.on_message(filters.command(commands=['clear'])) #???
def easteregg(client,message):
    bot.send_message(message.chat.id, text="Federico Ruffini")

@bot.on_message(filters.command(commands=['find'])) #find a proffesor
def find(client,message):
    newKeyboard=[]
    for c in range(0,len(allKeyboard)):
        newKeyboard.append([""])

    trovato=False
    cnt=0
    text=message.text
    text=re.sub("/find ", "", text) #remove /find
    text=text.upper()
    for i in range(0,len(allKeyboard)):
        if (text in allKeyboard[i]):
            trovato=True
            newKeyboard[cnt][0]=allKeyboard[i]
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


    if(message.text==polliceInSu or message.text==polliceInGiù): #if the message is a thumbs up or down, so if the user give a feedback
        addLog(message) #add the log
        bot.send_message(message.chat.id, text="Grazie per il feedback!", reply_markup=MAIN_BUTTONS)

    elif(message.text=="A-C"):
        message.reply(text="Button:",reply_markup=tastiera1)

    elif(message.text=="D"):
        message.reply(text="Button:",reply_markup=tastiera2)

    elif(message.text=="E-O"):
        message.reply(text="Button:",reply_markup=tastiera3)

    elif(message.text=="P-Z"):
        message.reply(text="Button:",reply_markup=tastiera4)

    elif(message.text=="<<<---------"):
        message.reply(text="Button:", reply_markup=MAIN_BUTTONS)

    else:
        response = get_response(message.text)  # get the response from the type of message requested

        type = response[1]  # get the type of message
        response = response[0]  # get the response

        daibottoni = findsolonome(message.text)
        if(daibottoni): #if the message is only a name (True means that the date and time is when message is sent)
            invia(message,type, True)
        elif(response=="ricerca professore"): #if the message is for searching a professor (False means that the date and time is specified in the message)
            invia(message,type, False)
        else: #if the message else
            inviasingolo(message,type, response)



bot.run() #run the bot