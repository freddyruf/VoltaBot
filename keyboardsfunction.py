
from pyrogram.types import ReplyKeyboardMarkup
import mysql.connector
def keyboardsgen(cursor):

    allKeyboard = []
    tastiera1 = [["<<<---------"]]
    tastiera2 = [["<<<---------"]]
    tastiera3 = [["<<<---------"]]  # with "<<<---------" the user will be able to go back to the main menu
    tastiera4 = [["<<<---------"]]
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
    return [tastiera1,tastiera2,tastiera3,tastiera4,allKeyboard]