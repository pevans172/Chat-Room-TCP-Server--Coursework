import socket
import sys


def TAKE_INPUT():
    while True:
        x = str(input(">>> "))
        if x != "":
            break
    return x
# returns a string for the input


def SEND_RECV(i):
    i = str(i)
    try:
        s.send(bytes(i, "utf-8"))
    except ConnectionResetError:
        return "ERROR: Server is not running/unavailable"

    # allows us to recieve data larger than the buffer size
    full_server_msg = ""
    # this variable will tell us whether a msg contains a HEADERSIZE portion we will need to remove
    new_msg = True
    # this gives us a 1,000,000,000 character limit for the data sent
    HEADERESIZE = 10
    # this allows for the server timeout if a response is too long
    s.settimeout(10)

    while True:
        # checks for socket timeout
        try:
            server_msg = s.recv(2048)
        except socket.timeout:
            return "SESSION ABANDONED: server took too long to reply"

        # this is the part we can check if we have a HEADERSIZE section in the msg
        if new_msg:
            server_msg_len = int(server_msg[:HEADERESIZE])
            new_msg = False

        full_server_msg += server_msg.decode("utf-8")
        # checker if we have recvd all parts of the message sent to us
        if len(full_server_msg)-HEADERESIZE == server_msg_len:
            full_server_msg += "\n"
            # return only the actual msg content
            return full_server_msg[HEADERESIZE:]
# send a string i to server then returns the string response


def CHECK_INPUT(x):
    # close down client
    if x == "QUIT":
        server_msg = SEND_RECV(x)
        print(server_msg)
        return 0

    # post a new mnessage and then recieves a confirmation
    elif x == "POST":
        # send board number
        print("Enter a message board number:")
        # Runs a loop until an integer is recieved
        while True:
            msg_bn = TAKE_INPUT()
            try:
                msg_bn = int(msg_bn)
                msg_bn = str(msg_bn)
                break
            except ValueError:
                print("Enter a message board number:")
                continue

        # put in a msg title
        print("Enter a message title:")
        msg_t = TAKE_INPUT()

        # put in a msg
        print("Enter a message:")
        msg_c = TAKE_INPUT()

        # send post request
        msg = SEND_RECV("POST_MESSAGE")
        print(msg)
        # once recieved all clear send data
        msg = f"{msg_bn},{msg_t},{msg_c}"
        server_msg = SEND_RECV(msg)
        print(server_msg)
        return server_msg

    # view the 100 recent posts of selected board
    try:
        i = int(x)
        msg = f"GET_MESSAGES,{i}"
        server_msg = SEND_RECV(msg)
        print(server_msg)
        return server_msg

    # takes whatever other possible input the client sent,
    # basically a server error will occur
    except ValueError:
        server_msg = SEND_RECV(x)
        print(server_msg)
        return server_msg

# does all the sending etc for the specific commands
# will only let us input POST, QUIT and a number


def main():
    er4 = 'SESSION ABANDONED: server took too long to reply'
    er5 = "ERROR: Server is not running/unavailable"
    er6 = 0
    while True:
        print("Enter any of the valid inputs:")
        print("- A message board number")
        print("- POST")
        print("- QUIT")
        msg = TAKE_INPUT()
        response = CHECK_INPUT(msg)
        # this checker is to check for the QUIT command to break this loop or a socket timeout
        if response in (er4, er5, er6):
            break


# The IP address and Port for the server
IP = sys.argv[1]
serverPort = int(sys.argv[2])
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((IP, serverPort))

    # get the GET as soon as connection is made
    get = SEND_RECV("GET_BOARDS")
    # if error then terminate client or if there is a timeout close the connection
    er1 = 'SESSION ABANDONED: server took too long to reply'
    er2 = "SERVER ERROR: no board folder defined\n"
    er3 = "SERVER ERROR: no message boards defined\n"
    if get in er1:
        print(get)
    elif get in (er2, er3):
        print(get)

    # or carry on
    else:
        print(get)
        main()
except ConnectionRefusedError:
    print("Server is not running/unavailable")
except ConnectionAbortedError:
    print("Server is not running/unavailable")
# catch any undefined error
except:
    print("SERVER ERROR: unknown cause of error")
