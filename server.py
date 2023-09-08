import socket
import time
from datafunction import *
from serveroutput import sand,sandOne
#i messaggi arriveranno sottoforma di IDinput;nome;timestring

#ID: 1 = richiestaa prof


connection = create_connection("localhost", "root", "")
#}}} closing the connection function

cursor = connection.cursor(buffered=True) #cursor /Read-only attribute describing the result of a query.


print ('avvio server');
HOST = '192.168.1.16'
PORT = 60004
s = socket.socket() #senza parametri protocollo tcp-ip

s.bind((HOST, PORT))
s.listen()

while True:
    conn, addr = s.accept()
    print('Connesso ad IP: ', addr)
    print(conn)
    dati = conn.recv(1024)
    dati=dati.decode('utf-8')
    #controlla ID
    if dati[0]=="1": #ricerca professore
        #divide i dati e rendo il timestring un object time da formato "anno-mese-giorno ora:minuti:secondi". convertendo byte in stringa
        dati=dati.split(';')
        nome=dati[1].upper()
        timeinfo=time.strptime(dati[2],'%Y-%m-%d %H:%M:%S')
        output = sand(conn,connection,nome,timeinfo)
        feedbot = output[0]
        feedresponse = output[1]
        feedmessage = output[2]

    print('dati ricevuti: ',dati)
s.close()
print('Fine programma')

