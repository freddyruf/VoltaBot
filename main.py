



"""

Info:
    Dictionary:
        - message: the message that the user send (pyrogram object)
        - response: one return of the get_response function, specify the message that would be sent
         to the user (exept in some case like searching a professor where the result for the user will be different)
        - type: one return of the get_response function, specify the type of the message
        - output: the response that the bot send to the user

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
output= ""



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
def create_connection(host_name, user_name, user_password):
    connection = None
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
def keyboardsgen(cursor):
    global tastiera1
    global tastiera2
    global tastiera3
    global tastiera4
    global allKeyboard


    cursor.execute("SELECT Nome FROM professori") #select all the name from the table
    cnt=0
    allKeyboard0 = cursor.fetchall()

    for element in allKeyboard0: #convert into a list and remove some suffix and prefix
        string=str(element)
        allKeyboard.append(string.removeprefix("('").removesuffix("',)"))

    """
        qui mi preparo a dividere la tastiera in 4 parti,
        ho trovato manualmente i nomi che mi dividono la tastiera,
        in 4 parti quasi uguali senza dover dividere i nomi con la stessa iniziale
    """
    fineUno = allKeyboard.index("D`ALESSANDRO AURA")
    fineDue = allKeyboard.index("EVANGELISTA FILIPPO")
    fineTre = allKeyboard.index("PAGLIARA DANIELA")
    fineQuattro = allKeyboard.index("ZENONI CRISTINA")+1

    for i in range(0, fineUno):
        tastiera1.append([allKeyboard[i]]) # [ ] because they need to be a matrix (1,len of initial list)
    for i in range(fineUno, fineDue):
        tastiera2.append([allKeyboard[i]])
    for i in range(fineDue, fineTre):
        tastiera3.append([allKeyboard[i]])
    for i in range(fineTre, fineQuattro):
        tastiera4.append([allKeyboard[i]])

    tastiera1 = ReplyKeyboardMarkup(tastiera1, one_time_keyboard=True, resize_keyboard=True) #make keyboard object
    tastiera2 = ReplyKeyboardMarkup(tastiera2, one_time_keyboard=True, resize_keyboard=True) #make keyboard object
    tastiera3 = ReplyKeyboardMarkup(tastiera3, one_time_keyboard=True, resize_keyboard=True) #make keyboard object
    tastiera4 = ReplyKeyboardMarkup(tastiera4, one_time_keyboard=True, resize_keyboard=True) #make keyboard object

keyboardsgen(cursor)

#function to find the type of message
def get_response(input_string,response_data):
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

def prepareLogInfo(message,response, output): # function to prepare the log element into the database (not sanding)
    global feedbot
    global feedresponse
    global feedmessage

    feedmessage = message.text
    feedresponse = response
    feedbot = output


def feedbacktry(message,response,output): # function to not always ask the user if he wants to give a feedback
    global feedmessage
    global feedresponse
    global feedbot


    if (random.randint(1, 5) == 1): # 1/5 chance to ask the user if he wants to give a feedback
        bot.send_message(message.chat.id, text="Potresti darci un feedback? " + polliceInSu + " o " + polliceInGiù,
                         reply_markup=emojiKeyboard)  # ask the user what he wants to do
        # save the message info
        feedmessage = message.text
        feedresponse = response
        feedbot = output
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

def mostSimilarFromList(string, list):
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
    global output

    cursor.execute(f"SELECT ID FROM professori WHERE Nome = '{msg.text}'") # obtain the id of the professor
    PROF_ID = cursor.fetchall()  # id prof
    PROF_ID = PROF_ID[0][0] # take the id from the tuple

    currentDateTime = datetime.now()  # actual date and time

    if(giorno == -1): # if the user don't specify the day
        Giorno = currentDateTime.isoweekday()  # actual day of the week
    else:
        Giorno = giorno

    # convert the day of the week into the name of the column in the database
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

    else: # if the day is not correct
        output= "Sei nel giorno sbagliato!"
        bot.send_message(msg.chat.id, text=output)
        return output


    if(orario == -1): # if the user don't specify the hour
        Ora = currentDateTime.hour  # actual hour
    else:
        Ora = orario -7 #-7 beacouse we use to talk about (frist, second, third...) hour and not about the actual hour for the clock


    if ((Giorno != "orarioproflunedì" and Ora > 6) or Ora <= 0 or Ora > 8):  # control if the hour is correct
        output='Ora sbagliata!'
        bot.send_message(msg.chat.id, text=output)
        return output

    # convert the hour into the name of the column in the database
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



    cursor.execute(f"SELECT {Ora} FROM {Giorno} WHERE IdProf = '{PROF_ID}'") # obtain the class where the professor is in that hour
    Classe = cursor.fetchall()  # class found
    Classe = Classe[0][0] # take the class from the tuple

    if(Classe=="libero" or Classe=="Libero"):   #control if the professor is free all hours
        cursor.execute(f"SELECT primaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'") #control frist hour
        prima = cursor.fetchall()

        cursor.execute(f"SELECT secondaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'") #control second hour
        seconda = cursor.fetchall()

        cursor.execute(f"SELECT terzaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'") #control third hour
        terza = cursor.fetchall()

        cursor.execute(f"SELECT quartaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'") #control fourth hour
        quarta = cursor.fetchall()

        cursor.execute(f"SELECT quintaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'") #control fifth hour
        quinta = cursor.fetchall()

        cursor.execute(f"SELECT sestaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  #control sixth hour
        sesta = cursor.fetchall()
        #control if the professor is free all hours
        if (prima[0][0]=="libero" and seconda[0][0]=="libero" and terza[0][0]=="libero" and quarta[0][0]=="libero" and quinta[0][0]=="libero" and sesta[0][0]=="libero"): return 2
        elif (prima[0][0]=="Libero" and seconda[0][0]=="Libero" and terza[0][0]=="Libero" and quarta[0][0]=="Libero" and quinta[0][0]=="Libero" and sesta[0][0]=="Libero"): return 2

        return "libero" #only the hour


    cursor.execute(f"SELECT IDaula FROM classi WHERE classe = '{Classe}'") # id aula
    IDAula = cursor.fetchall()
    IDAula = IDAula[0][0]

    cursor.execute(f"SELECT Palazzina,Piano,Aula FROM aule WHERE ID ='{IDAula}'") # info aula
    Aula = cursor.fetchall()  # catch the info about the class
    Palazzina = Aula[0][0]
    Piano = Aula[0][1]
    nAula = Aula[0][2]
    result = {
        "Classe": Classe,
        "Palazzina": Palazzina,
        "Piano": Piano,
        "Aula": nAula
    }
    return result



#searching the name of the professor

def FindIfOnlyName(str,lista):
    str = re.split(' ', str.upper())
    if len(str)>3:
        return False
    for c in str: #entro nella lista di parole
        
        for i in lista: #entro nella lista di liste di tasti
            if (len(c)>4 and c[0]+c[1]+c[2]+c[3]+c[4] in i):
                return True
    return False

def FindTime(str): #function to find the hour in the string
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

#searching the day
def findDay(str):
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
        elif ("domani" in c and not("dopo"in c) and not("dopo"in str)): #if the word is "domani" and there isn't "dopo" the day is the next day
            giorno= datetime.today().weekday()+2
            if(giorno>7): giorno-=7
            return giorno
        elif ("domani" in c and ("dopo"in c or "dopo"in str)): #if the word is "domani" and there is "dopo" the day is the next next day
            giorno= datetime.today().weekday()+3
            if(giorno>7): giorno-=7
            return giorno
        elif ("ieri" in c): #if the word is "ieri" the day is the last day
            giorno= datetime.today().weekday()
            if(giorno>7): giorno-=7
            return giorno

    return -1



def sand(message,type,inQuestoMomento):
    original_message= message.text
    message.text = mostSimilarFromList(
        message.text.upper(), allKeyboard)  # modify the message text to the name of the professor (to work in some functions)

    if (inQuestoMomento):
        ora=-1
        giorno=-1
    else:
        ora = FindTime(original_message)  # search the time
        giorno = findDay(original_message)  # search the day

    info = prof_info(message, ora,
                     giorno)  # get the info about the professor (ora and giorno can be '-1' if not found)

    if not type(info) is dict:  # if he is free
        output = f"Il prof {message.text.title()} è libero"
        bot.send_message(message.chat.id, text=output)  # if he is free

    else:  # if he is in school
        output = f"Il prof {message.text.title()} si trova nella classe {info['Classe']} in: \n-Palazzina: {info['Palazzina']} \n-Piano: {info['Piano']} \n-Aula: {info['Aula']}"
        bot.send_message(message.chat.id, text=output)  # if he is in school



    message.text = original_message  # original message
    feeding = feedbacktry(message, type, output)  # ask for feedback
    if (feeding):
        return 0  # if the user wants to give feedback, stop the function

    message.text = original_message  # original message
    prepareLogInfo(message, type, output)  # add the log
    addLog(message)  # add the log into db

def sandOne(message,type,response):
    global output
    bot.send_message(message.chat.id, text=response)  # send the response of type of message requested
    output = response  # save the response

    feeding = feedbacktry(message, type, output)  # ask for feedback
    if (feeding):
        return 0  # if the user wants to give feedback, stop the function
    prepareLogInfo(message, type, output)  # add the log
    addLog(message)  # add the log into db
    return 0  # stop the function


#telegram functions

@bot.on_message(filters.command(commands=['start']))   #start
def start(client,message):
    message.reply(text="Benvenuto! Usa questo bot per scoprire dove si trova un professore, per ogni aiuto usa /help, avrai anche una lista di comandi", reply_markup=MAIN_BUTTONS)

@bot.on_message(filters.command(commands=['help']))
def help(client,message):
    message.reply(text="Ehi, usa il bot per cercare l'aula in cui si trova un professore \n\n Comandi:\n \n/start - Il bot inizia, puoi usarlo per far apparire i pulsanti \n/find - cerca un professore \n/help - info e lista comandi \n\nChiedimi dove s trova un professore(Es. Dove si trova Acciavatti Cristiano alla quarta ora di venerdi?) \n \nPer aiuto o feedback scrivi al numero: \n +39 3924502802 \n ", reply_markup=MAIN_BUTTONS)


@bot.on_message(filters.command(commands=['find'])) #find a profesor from a part of a name
def find(client,message):

    newKeyboard=[] #prepere the keyboard where the user see the result
    for c in range(0,len(allKeyboard)):
         newKeyboard.append([])

    trovato=False
    cnt=0
    message.text=re.sub("/find ", "", message.text) #remove /find
    message.text=message.text.upper()
    
    
    for element in allKeyboard: #for each name in the keyboard
        
        nomeseparato=re.split(" ",element) #split the name into a list of words (ex. "Cristiano Acciavatti" -> ["Cristiano","Acciavatti"])
        
        for nome in nomeseparato: #for each word in the name
            if (similarity(message.text,nome)>40 and len(nome)>2): #if the similarity is >40 and the word is >2 characters(so no "DI" or "DE")
                trovato=True
                newKeyboard[cnt].append(element) #add the name to the keyboard that will be shown to the user
                cnt+=1
    if trovato: #if we found something
        reply_markup=ReplyKeyboardMarkup(newKeyboard,one_time_keyboard=True,resize_keyboard=True) #create the keyboard object
        message.reply(text="Habbiamo trovato questi risultati, sceglierne uno per vedere dove si trova ora:",reply_markup=reply_markup) #send the keyboard
    else:
        message.reply(text="Non ho trovato nulla, prova a darci piu lettere :_( ",reply_markup=MAIN_BUTTONS) #if we don't found anything
  
      

@bot.on_message(filters.text)

def Main(client,message):


    if(message.text==polliceInSu or message.text==polliceInGiù): #if the message is a thumbs up or down, so if the user give a feedback
        addLog(message) #add the log
        bot.send_message(message.chat.id, text="Grazie per il feedback!", reply_markup=MAIN_BUTTONS)

    #if the user is using buttons and want to search a professor
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

    #if is not a menu navigation and not a feedback
    else:
        response = get_response(message.text,response_data)  # get the type of message and the response(usable if he isn't asking a professor)

        type = response[1]  # get the type of message
        response = response[0]  # get the response

        daibottoni = FindIfOnlyName(message.text,allKeyboard)
        if(response=="ricerca professore" or daibottoni): #if is searching a professor
            sand(message,type,daibottoni)
        else: #if the message else
            sandOne(message,type, response)



bot.run() #run the bot