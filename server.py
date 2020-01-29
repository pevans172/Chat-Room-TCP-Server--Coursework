import socket
from pathlib import Path
import sys
import datetime
import collections


def POST_MESSAGE(msgBoard, msgTitle, msg):
    p = Path(Path.cwd()) / "board"
    # serch through this folder and get the addresses of objects
    lst = []
    for i in p.iterdir():
        lst.append(i)
    # get this file always in alphabetical order
    lst.sort()
    # Get the message board address
    # this is where an error will happen
    messageBoard = lst[msgBoard-1]

    # writing and creating the file for the message
    messageTitle = str(msgTitle)
    # This is the message itself
    message = str(msg)

    # changing how to file title is written
    messageTitle = messageTitle.replace(" ", "_")
    x = datetime.datetime.now()
    # formatting the title
    fileName = "{:4d}{:02d}{:02d}".format(x.year, x.month, x.day)
    fileName = fileName + "-{:02d}{:02d}{:02d}-".format(x.hour, x.minute, x.second)
    fileName = fileName + messageTitle + ".txt"
    # making the destination for the file
    full_file_path = messageBoard / fileName

    # creating and editing the file
    f = open(full_file_path, "w+")
    f.write(f"{message}")
    f.close()
    return "Message posted"
# returns string confirmation


def GET_BOARDS():
    # get the address always for the board folder and make it a path object
    folder_path = Path(Path.cwd()) / "board"
    p = Path(folder_path)
    # make address a string
    folder_path = str(folder_path)
    # serch through this folder and get the names of objects
    lst = []
    for i in p.iterdir():
        lst.append(str(i))
    # get this file always in alphabetical order
    lst.sort()
    x = 1
    choices = "These are the message boards:\n"
    for i in lst:
        i = i.replace(folder_path, '')
        i = str(x) + ".  " + i[1:] + ";" + "\n"
        x += 1
        choices = choices + i
    return choices
# returns string of info


def GET_MESSAGES(brd):
    folder_path = Path(Path.cwd()) / "board"
    p = Path(folder_path)
    # clear this to use again later
    folder_path = ""
    # get all objects sorted in this list sorted
    lst = []
    for i in p.iterdir():
        lst.append(str(i))
    # get this list always in alphabetical order
    lst.sort()
    # serch through this folder and get the selected msg board
    count = 1
    for i in lst:
        if count == brd:
            folder_path = i
            break
        count += 1

    # continue on if it were a valid input
    # we store in a dictionary all filenames in the folder and then order them on creation date
    p = Path(folder_path)
    dct = {}
    for i in p.iterdir():
        name = str(i)
        name = name.replace(folder_path, '')
        name = name[1:]
        dct[i.stat().st_mtime] = name
    # get this list always in "most recent" order
    ordered_dct = collections.OrderedDict(sorted(dct.items(), reverse=True))

    count = 0
    file_names = []
    for key in ordered_dct:
        if count < 100:
            count += 1
            file_names.append(ordered_dct[key])
        else:
            break

    out = ""
    count = len(file_names)
    for f in file_names:
        cwp = Path(folder_path) / f
        o = Path(cwp).read_text()
        out = out + f"{count}: " + o + "\n"
        count -= 1
    return out
# returns string of info


def FORMAT_FOR_CLIENT(msg):
    # this gives us a 1,000,000,000 character limit for the data sent
    HEADERSIZE = 10
    # this is where we will make the header that contains the msg length
    # we append the msg content to the header
    msg_length = len(msg)
    msg = f"{msg_length:<{HEADERSIZE}}" + msg
    return msg
# formats the messages sent to client to contain a header describing the length of msg


def log(clAdr, msg, status):
    # get file address
    p = Path(Path.cwd()) / "server.log"

    # client info
    ip = str(clAdr[0])
    port = str(clAdr[1])

    # get date and time
    x = datetime.datetime.now()
    t = "{:02d}/{:02d}/{:4d}".format(x.day, x.month, x.year)
    t = t + "-{:02d}:{:02d}:{:02d}".format(x.hour, x.minute, x.second)

    # editing the file
    if Path('server.log').is_file():
        f = open(p, "a")
    # creating the log file if needed
    else:
        f = open(p, "w+")
    f.write(f"{ip}:{port:<10}\t{t}\t{msg:<17}\t{status}\n")
    f.close()
# appends information to the log file


def CHECK_BOARDS():
    # check to see if there is a board folder / board folders
    try:
        x = GET_BOARDS()
        if x == "These are the message boards:\n":
            msg = "SERVER ERROR: no message boards defined"
            return msg
    except:
        msg = "SERVER ERROR: no board folder defined"
        return msg


def main():
    try:
        clientSocket, clientAddress = s.accept()
        print(f"Connection from client at: {clientAddress} \n")

        while True:

            # input from the client
            inpt = clientSocket.recv(1024).decode("utf-8")

            if inpt == "QUIT":
                try:
                    msg = "\nCLIENT CONNECTION SHUTTING DOWN"
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    clientSocket.close()
                    print(f"Connection from client at {clientAddress} has closed.")
                    log(clientAddress, "QUIT", "OK")
                    return 1

                except:
                    msg = "SERVER ERROR: command wasn't able to run"
                    print(msg)
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    log(clientAddress, "QUIT", "ERROR")

            if inpt == "GET_BOARDS":
                try:
                    x = GET_BOARDS()
                    if x == "These are the message boards:\n":
                        msg = "SERVER ERROR: no message boards defined"
                        print(msg)
                        clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                        log(clientAddress, "GET_BOARDS", "ERROR")
                        return 0

                    msg = f"\nConnected to server at IP: {IP} , and Port: {serverPort}\n" + x
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    print("GET_BOARDS request completed")
                    log(clientAddress, "GET_BOARDS", "OK")
                except:
                    # server must shutdown from this error
                    msg = "SERVER ERROR: no board folder defined"
                    print(msg)
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    log(clientAddress, "GET_BOARDS", "ERROR")
                    return 0
                continue

            if inpt == "POST_MESSAGE":
                msg = "POST_MESSAGE request recieved"
                clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                try:
                    data = clientSocket.recv(1024).decode("utf-8")
                    data = data.split(",")
                    msg = POST_MESSAGE(int(data[0]), data[1], data[2])
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    print("POST_MESSAGE request completed")
                    log(clientAddress, "POST_MESSAGE", "OK")
                except:
                    msg = "SERVER ERROR: invalid board number chosen for POST_MESSAGE"
                    print(msg)
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    log(clientAddress, "POST_MESSAGE", "ERROR")
                continue

            data = inpt.split(",")
            if data[0] == "GET_MESSAGES":
                try:
                    msg = GET_MESSAGES(int(data[1]))
                    if msg == "":
                        msg = "There are no messages in this message board."
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    print("GET_MESSAGES request completed")
                    log(clientAddress, "GET_MESSAGES", "OK")
                # except:
                except:
                    msg = "SERVER ERROR: invalid board number chosen for GET_MESSAGES"
                    print(msg)
                    clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
                    log(clientAddress, "GET_MESSAGES", "ERROR")
                continue

            # CATCH ALL POSSIBLE INPUTS AND JUST RETURN AN ERROR FOR UNDEFINED
            msg = "SERVER ERROR: unable to understand command"
            print(msg)
            clientSocket.send(bytes(FORMAT_FOR_CLIENT(msg), "utf-8"))
            log(clientAddress, "UNDEFINED_COMMAND", "ERROR")

    except ConnectionAbortedError:
        print("SERVER ERROR: taking too long to send responses")

    except ConnectionResetError:
        print("CLIENT ERROR: connection with client abruptly lost")


# The IP address and Port for the server
IP = sys.argv[1]
serverPort = int(sys.argv[2])

# try and set up the server
try:
    # check there is a board or message folder
    er1 = "SERVER ERROR: no board folder defined"
    er2 = "SERVER ERROR: no message boards defined"
    c = CHECK_BOARDS()
    if c in (er1, er2):
        print(c)

    else:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((IP, serverPort))
        s.listen(2)
        print(f"Server listening at: ('{IP}', {serverPort})...")
        # keep the serevr running even if clients quit
        while True:
            # quit and shut down server only when no boards are defined or no board folder
            if main() == 0:
                break

except socket.error:
    print("SERVER ERROR: could not bind server to specified address")
    s.close()

# catch any exception thats left over
except:
    print("SERVER ERROR: unknown cause of error")
    s.close()
