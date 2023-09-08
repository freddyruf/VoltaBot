from datetime import datetime
import re

import mysql.connector
import editdistance

from datafunction import create_connection

connection = create_connection("localhost", "root", "")
#}}} closing the connection function

cursor = connection.cursor(buffered=True) #cursor /Read-only attribute describing the result of a query.

def similarity(string1, string2):  # function to calculate the similarity between two strings
    max_length = max(len(string1), len(string2))  # calculate the max length between the two strings

    if max_length == 0:  # if the max length is 0
        percent_distance = 0  # the distance is 0

    else:  # if the max length is not 0
        distance = editdistance.eval(string1, string2)  # calculate the distance between the two strings
        percent_distance = 100 * (max_length - distance) / max_length  # convert into %
    return percent_distance


def mostSimilarFromList(string, list):
    words = string.split()  # divide the string into a list of words
    n = len(words)
    closest = None
    min_distance = 0  # minimum distance that bot have found

    for i in range(n - 1):  # for each word in the list
        substring = words[i] + ' ' + words[i + 1]  # take the word and the next one

        for element in list:  # for each row in the list
            d = similarity(element, substring)
            if d > min_distance and d > 70:
                min_distance = d
                closest = element

    if closest is None:
        for c in words:  # for evry word in the list
            for element in list:  # for each element in the list
                if (len(c) > 4 and c[0] + c[1] + c[2] + c[3] + c[4] in element):
                    return element
    return closest


def prof_info(msg, orario, giorno):  # function to get the info about the professor
    global output

    cursor.execute(f"SELECT ID FROM professori WHERE Nome = '{msg}'")  # obtain the id of the professor
    PROF_ID = cursor.fetchall()  # id prof
    print(PROF_ID)
    PROF_ID = PROF_ID[0][0]  # take the id from the tuple

    currentDateTime = datetime.now()  # actual date and time

    if (giorno == -1):  # if the user don't specify the day
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

    else:  # if the day is not correct
        output = "Sei nel giorno sbagliato!"
        return output

    if (orario == -1):  # if the user don't specify the hour
        Ora = currentDateTime.hour  # actual hour
    else:
        Ora = orario - 7  # -7 beacouse we use to talk about (frist, second, third...) hour and not about the actual hour for the clock

    if ((Giorno != "orarioproflunedì" and Ora > 6) or Ora <= 0 or Ora > 8):  # control if the hour is correct
        output = 'Ora sbagliata!'
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

    cursor.execute(
        f"SELECT {Ora} FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  # obtain the class where the professor is in that hour
    Classe = cursor.fetchall()  # class found
    Classe = Classe[0][0]  # take the class from the tuple

    if (Classe == "libero" or Classe == "Libero"):  # control if the professor is free all hours
        cursor.execute(f"SELECT primaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  # control frist hour
        prima = cursor.fetchall()

        cursor.execute(f"SELECT secondaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  # control second hour
        seconda = cursor.fetchall()

        cursor.execute(f"SELECT terzaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  # control third hour
        terza = cursor.fetchall()

        cursor.execute(f"SELECT quartaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  # control fourth hour
        quarta = cursor.fetchall()

        cursor.execute(f"SELECT quintaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  # control fifth hour
        quinta = cursor.fetchall()

        cursor.execute(f"SELECT sestaOra FROM {Giorno} WHERE IdProf = '{PROF_ID}'")  # control sixth hour
        sesta = cursor.fetchall()
        # control if the professor is free all hours
        if (prima[0][0] == "libero" and seconda[0][0] == "libero" and terza[0][0] == "libero" and quarta[0][
            0] == "libero" and quinta[0][0] == "libero" and sesta[0][0] == "libero"):
            return "Ha il giorno libero"
        elif (prima[0][0] == "Libero" and seconda[0][0] == "Libero" and terza[0][0] == "Libero" and quarta[0][
            0] == "Libero" and quinta[0][0] == "Libero" and sesta[0][0] == "Libero"):
            return "Ha il giorno libero"

        return "è libero quest ora"  # only the hour

    cursor.execute(f"SELECT IDaula FROM classi WHERE classe = '{Classe}'")  # id aula
    IDAula = cursor.fetchall()
    IDAula = IDAula[0][0]

    cursor.execute(f"SELECT Palazzina,Piano,Aula FROM aule WHERE ID ='{IDAula}'")  # info aula
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


# searching the name of the professor

def FindIfOnlyName(str, lista):
    str = re.split(' ', str.upper())
    if len(str) > 3:
        return False
    for c in str:  # entro nella lista di parole

        for i in lista:  # entro nella lista di liste di tasti
            if (len(c) > 4 and c[0] + c[1] + c[2] + c[3] + c[4] in i):
                return True
    return False


def FindTime(str):  # function to find the hour in the string
    str = re.split(' ', str.lower())
    tot = 0
    nulla = True
    for c in str:  # for each word in the string in

        # words
        if (c == "prima"):  # if the word is "prima" the hour is 1
            return 8
        elif (c == "seconda"):  # if the word is "seconda" the hour is 2
            return 9
        elif (c == "terza"):  # if the word is "terza" the hour is 3
            return 10
        elif (c == "quarta"):  # if the word is "quarta" the hour is 4
            return 11
        elif (c == "quinta"):  # if the word is "quinta" the hour is 5
            return 12
        elif (c == "sesta"):  # if the word is "sesta" the hour is 6
            return 13
        elif (c == "settima"):  # if the word is "settima" the hour is 7
            return 14
        elif (c == "ottava"):  # if the word is "ottava" the hour is 8
            return 15

        # in numbers
        elif (ord(c[0]) > 47 and ord(c[0]) < 58):  # if the first char is a number

            string = re.split(':', c)  # split the string in the char ":"

            for i in string:  # for each element in the list
                if (len(i) == 2 and ord(i[1]) > 47 and ord(i[1]) < 58):  # if the element is a number
                    nulla = False
                    tot = (ord(i[0]) - 48) * 10 + (ord(i[1]) - 48)  # convert the string in a number
                    break
                elif ("?" in i):  # if the element is a "?" the hour is the frist number
                    nulla = False
                    tot = ord(i[0]) - 48
                    break
                else:
                    nulla = False
                    tot = ord(i[0]) - 48
                    break

    if (nulla):  # not found
        return -1
    else:  # found
        return tot


# searching the day
def findDay(str):
    str = re.split(' ', str.lower())  # split the string in the char " "
    for c in str:
        if ("luned" in c):  # if the word is "lunedì" the day is 1
            return 1
        elif ("marted" in c):  # if the word is "martedì" the day is 2
            return 2
        elif ("mercoled" in c):  # if the word is "mercoledì" the day is 3
            return 3
        elif ("gioved" in c):  # if the word is "giovedì" the day is 4
            return 4
        elif ("venerd" in c):  # if the word is "venerdì" the day is 5
            return 5
        elif ("sabato" in c):  # if the word is "sabato" the day is 6
            return 6
        elif ("domenica" in c):  # if the word is "domenica" the day is 7
            return 7
        elif ("domani" in c and not ("dopo" in c) and not (
                "dopo" in str)):  # if the word is "domani" and there isn't "dopo" the day is the next day
            giorno = datetime.today().weekday() + 2
            if (giorno > 7): giorno -= 7
            return giorno
        elif ("domani" in c and (
                "dopo" in c or "dopo" in str)):  # if the word is "domani" and there is "dopo" the day is the next next day
            giorno = datetime.today().weekday() + 3
            if (giorno > 7): giorno -= 7
            return giorno
        elif ("ieri" in c):  # if the word is "ieri" the day is the last day
            giorno = datetime.today().weekday()
            if (giorno > 7): giorno -= 7
            return giorno

    return -1