#entering into jeson file for the fuction that search argument from a phrase
import datetime
from datetime import datetime
import json

import mysql
from mysql.connector import Error
import re

import random
def load_json(file):
    with open(file) as bot_responses:
        print(f"Loaded '{file}' successfully!")
        return json.load(bot_responses)

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

#function to find the type of message
def get_response(input_string, response_data):
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


polliceInSu='\U0001F44D'
polliceInGiù='\U0001F44E'

def addLog(connection,cursor,message,feedmessage,feedresponse,feedbot):  # function to add the log element into the database


    now = datetime.now()
    # Obtain actual date with format 'YYYY-MM-DD'
    date_str = now.strftime('%Y-%m-%d')

    # Obtain actual hours with format 'HH:MM:SS'
    time_str = now.strftime('%H:%M:%S')

    timeinfo = date_str + " " + time_str # setup time for SQL datetime syntax

    if (message.text == polliceInSu): # if the user give a feedback
        feed = 1
    elif (message.text == polliceInGiù): # if the user give a feedback
        feed = -1
    else: # if the user don't give a feedback
        feed = 0

    cursor.execute(
                f"INSERT INTO log (tempo, usertext, requestinfo, responsetext, feedback) VALUES ('{timeinfo}', '{feedmessage}','{feedresponse}', '{feedbot}', {feed});")

    # if (feed!=None): # if the user give a feedback
    #     cursor.execute(
    #         f"INSERT INTO log (tempo, usertext, requestinfo, responsetext, feedback) VALUES ('{timeinfo}', '{feedmessage}','{feedresponse}', '{feedbot}', {feed});")
    #
    # else: # if the user don't give a feedback
    #     cursor.execute(
    #         f"INSERT INTO log (tempo, usertext, requestinfo, responsetext) VALUES ('{timeinfo}', '{feedmessage}','{feedresponse}', '{feedbot}');")

    connection.commit() # commit the changes

def prepareLogInfo(message,response, output): # function to prepare the log element into the database (not sanding)

    feedmessage = message.text
    feedresponse = response
    feedbot = output
    return [feedmessage,feedresponse,feedbot]


def feedbacktry(message,response,output): # function to not always ask the user if he wants to give a feedback

    feedmessage = message.text
    feedresponse = response
    feedbot = output

    if (random.randint(1, 5) == 1): # 1/5 chance to ask the user if he wants to give a feedback
        # save the message info

        return [True,feedmessage,feedresponse,feedbot]
    else:
        return [False,feedmessage,feedresponse,feedbot]