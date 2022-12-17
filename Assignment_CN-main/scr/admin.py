# It creates a GUI for the admin to see the list of online users and the list of offline users
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import socket
import threading
import json

#ADMIN_ADDR = "192.168.1.12"
ADMIN_ADDR = socket.gethostbyname(socket.gethostname())
#Port
ADMIN_PORT = 5505 

print(ADMIN_ADDR)

FORMAT = "utf8"
MAX_CILENT = 10

COLOR_1 = "#040073"
COLOR_2 = "#1337ac"
COLOR_3 = "#617dd7"
COLOR_4 = "#ffffff"

#MODE_LOGIN = 1
#MODE_SIGNIN = 2

#Success_message = "SUCCESS"
#Fail_message = "FAILED"

user_list = {} # list of user
class Admin:
    def __init__(self):
        """
        It creates a GUI for the admin to see the list of online users and the list of offline users.
        """
        #Back End
        
        # Creating a socket object and binding it to the host and port.
        self.host_server = socket.gethostbyname(ADMIN_ADDR)
        self.port_server = ADMIN_PORT
        self.curr_client = 0

        # Creating a socket object.
        self.server_process = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Binding the server to the host and port.
        self.server_process.bind((self.host_server, self.port_server))
        # The above code is listening for 10 connections.
        self.server_process.listen(10)
        
        #Front End
        
        # Creating a GUI window with a title, size, and color.
        # Creating a GUI for the admin to see the online users.
        self.gui = Tk()
        
        self.gui.title("ADMIN GUI")
        
        self.gui.geometry("600x600")
        
        self.gui.protocol("WM_DELETE_WINDOW", self.Close)
        
  
        self.Frame = Frame(self.gui) # The frame for the IP address of the server
        
        self.Id_Room = Label(self.Frame, text="ID ROOM") # The ID of the room
        
        self.idLabel = Label(self.Frame, text="WELCOME TO ADMIN GUI") # Welcome message
        
        self.Input = Label(self.Frame, text=self.host_server) # The IP address of the server
        
        self.idLabel.config(font=("Arial", 25), bg=COLOR_1, fg=COLOR_4) # The font, color, and size of the welcome message.
        
        self.idLabel.pack() # The welcome message is packed.
        

        self.Frame.config(bg=COLOR_2)    # The  color of the frame.
        
        self.Id_Room.config(bg=COLOR_1, fg=COLOR_4) # The font, color, and size of the ID of the room.
        
        self.Input.config(bg="#ffffff", fg=COLOR_1) # The font, color, and size of the IP address of the server.

        self.Frame.place(relheight=0.34, relwidth=1) # The size of the frame.
        
        self.Id_Room.place(relheight=0.15, relwidth=0.3, relx=0.35, rely=0.32) # The size of the ID of the room.
        
        self.Input.place(relheight=0.15, relwidth=0.3, relx=0.35, rely=0.52) # The size of the IP address of the server.


        self.Act_Frame = Frame(self.gui) # The frame for the list of online users.
        
        self.Online_Frame = Frame(self.Act_Frame)        # The frame for the list of online users. 
        
        self.onlIntro = Label(self.Online_Frame, text="LIST OF ONLINE USER")  # The list of online users.

        self.Online_Frame.config(bg = COLOR_4)  # The color of the frame for the list of online users.
        
        self.Act_Frame.config(bg = COLOR_2) # The color of the frame for the list of online users.
        
        self.onlIntro.config(bg = COLOR_1, fg = COLOR_4)  # The font, color, and size of the list of online users.  

        self.Online_Frame.place(relheight=0.55, relwidth=0.7, relx=0.15, rely=0.11)  # The  size of the frame for the list of online users.
        
        self.Act_Frame.place(relheight=0.9, relwidth=1, relx=0,rely=0.3) # The size of the frame for the list of online users.
        
        self.onlIntro.place(relheight=0.1, relwidth=0.6, relx=0.2,rely=0.02) # The  size of the list of online users.
        
        self.Online_User = [] #if user is online, add to this list


#BASIC FUNCTION
    #server-process listen to client
    def listen(self):                           
        """
        The function listens for new clients and creates a new thread for each client
        """
        while self.curr_client<MAX_CILENT: # no more than 10 clients
            # accept new client and create a new thread for it
            channel,client = self.server_process.accept() 
            
            print(f"Client: {client}") # print client address
            
            try: # try to create a new thread
                self.curr_client += 1 # get new client
                
                thr = threading.Thread(target=self.userHandle, args=(channel,client)) # create new thread
                
                thr.TF = False # set TF to False
                
                thr.start() # start thread
                
            except: 
                
                print("error") # print error
                
                
    def Send_mess(self, channel, client, message): # Send_mess message to client    
        """
        It sends a message to a client
        
        :param channel: the socket
        :param client: the client that the message is being sent to
        :param message: the message to Send_mess
        """
        channel.sendall(str(message).encode(FORMAT)) # Send_mess message
        
    #server-process recieve message from other
    def receive_message(self, channel, client):        
        """
        It receives a message from the client and returns it
        
        :param channel: the channel that the message is being received from
        :param client: the client object
        :return: The message that was received.
        """
        mess = channel.recv(1024).decode(FORMAT) # receive message
        return mess
    #server-process Send_mess message to other
       
    #fucntion support for close the connection
    def Close(self): 
        self.server_process.close() # close server
        
        self.gui.destroy() # close gui
    #function support for update user list
    
    #function support for Authentification    
    def processAccount(self, Acc, Adr):
        """
        It takes a string of the form "name:password" and "address:port" and returns a dictionary with
        the keys "name", "password", "address", "port", and "isAct" with the values being the
        corresponding values from the input strings
        
        :param Acc: {'name': 'password'}
        :param Adr: {'127.0.0.1': '8080'}
        :return: A dictionary with the keys "name", "password", "address", "port", and "isAct".
        """
        Information = {}
        
        accInfor=Acc.replace("{","").replace("}","").replace("'","").replace(" ","").split(":") # remove all the characters that are not needed
        
        adrInfor=Adr.replace("{","").replace("}","").replace("'","").replace(" ","").split(":") # remove all the characters that are not needed
        # Creating a dictionary called Information and adding the values of the accInfor and adrInfor
        # lists to it.
        Information["name"] = accInfor[0]   
        
        Information["password"] = accInfor[1]    
        
        Information["address"] = adrInfor[0]
        
        Information["port"] = adrInfor[1]
        
        Information["isAct"] = 1
        
        return Information
    
    
       
    def updateUserList(self):
        """
        It reads a json file, creates a dictionary, loops through the json file, creates a label for
        each account, places the label in a frame, and then writes the json file.
        """
        with open("account.json", "rb") as f: 
            jsonFile = json.load(f) # read json file
        self.Online_User = {} # create new dictionary
        
        for account in jsonFile["account"]: # loop through all account
            # Creating a new label with the name of the account.
            self.Online_User[account["name"]] = Label(self.Online_Frame, text=account['name']) 
            self.Online_User[account["name"]].config(bg=COLOR_1, fg=COLOR_4) 

        # A variable to keep track of the index of the label.
        onlIndex = 0
        
        # Placing all the widgets in the Online_Frame to the top left corner of the frame.
        for widget in self.Online_Frame.winfo_children():
            widget.place(relheight=0, relwidth=0)

        self.onlIntro.place(relheight=0.1, relwidth=0.3, relx=0.2)
        # This is a loop that goes through all the accounts in the json file and checks if the account
        # is active. If it is, it will add 1 to the index and place the label in the frame.
        for account in jsonFile["account"]:
            if account["isAct"] == 1:
                onlIndex+=1
                self.Online_User[account["name"]].place(relheight=0.1, relwidth = 0.8, relx=0.1, rely =  onlIndex*0.15)

        with open('account.json','w') as f:
            json.dump(jsonFile,f) 
        pass
    
    
        def createAccount(self, jsonFile, jsonObject):
            """
            It takes a json file, and a json object, and appends the json object to the json file
        
            :param jsonFile: The json file that is being read from
            :param jsonObject: {"name": "John", "age": 30, "city": "New York"}
            :return: The jsonFile and the Success_message
            """
            jsonFile["account"].append(jsonObject)
            return jsonFile, "SUCCESS"
       
    
    def checkAccount(self, jsonFile, jsonObject):
        """
        If the name and password in the jsonObject match the name and password in the jsonFile, then
        update the address, port, and isAct fields in the jsonFile
        
        :param jsonFile: the json file that contains all the accounts
        :param jsonObject: {"name": "name", "password": "password", "address": "address", "port":
        "port"}
        :return: The jsonFile and the message
        """
        for account in jsonFile["account"]:
            
            # Checking if the name and password in the jsonObject are the same as the name and
            # password in the account.
            if account["name"] == jsonObject["name"] and account["password"]==jsonObject["password"]: 
                # Updating the address, port, and isAct fields in the jsonFile.
                account["address"] = jsonObject["address"]    
                account["port"] = jsonObject["port"]
                account["isAct"] = 1
                return jsonFile, "SUCCESS"
        return jsonFile, "FAILED"
    

    def Deactive_acc(self, userName):
        """
        It opens the json file, finds the account with the name that matches the userName parameter,
        sets the isAct value to 0, and then dumps the json file
        
        :param userName: The name of the user to be deactivated
        """
        with open("account.json", "rb") as f: # open json file
            jsonFile = json.load(f)
        
        # Looping through the json file and if the name is equal to the userName, it will set the
        # isAct to 0.
        for account in jsonFile["account"]: 
            if account["name"] == userName:
                account["isAct"] = 0
        with open('account.json','w') as f:
            json.dump(jsonFile,f)   

        self.updateUserList()
        
        
# SERVER PROCESS 
    #FOR ADMIN USER
        
    # Authentification for normal user
       
    def user_Authentication(self, channel, client):
        """
        It receives a message from the client, then sends a message back to the client to ensure that
        the client receives the message in order
        
        :param channel: the channel that the client is connected to
        :param client: the client socket
        """
        Acc = None
        mess = None
        while mess!="SUCCESS":

            type = self.receive_message(channel,client)
            #self.Send_mess(channel, client, "Received")      # ensure client receive inorder
            Acc = self.receive_message(channel, client)
            #self.Send_mess(channel, client, "Received")      # ensure client receive inorder
            Adr = self.receive_message(channel , client)
            #self.Send_mess(channel, client, "Received") 
            
            # Update 
            jsonObject = self.processAccount(Acc, Adr)
            print(jsonObject)
            with open("account.json", "rb") as f:
                jsonFile = json.load(f)

            # Receiving a message from the client and then checking the type of message. If the type
            # is 1, it will check the account. If the type is 2, it will create an account.
            print(self.receive_message(channel , client))
            if int(type)==1: 
                jsonFile, mess = self.checkAccount(jsonFile, jsonObject)
                self.Send_mess(channel, client, mess)
            elif int(type)==2:
                jsonFile, mess = self.createAccount(jsonFile, jsonObject)
                self.Send_mess(channel, client, mess)
            print(self.receive_message(channel, client))

            # Open a json file and writing the jsonFile variable to it.
            with open('account.json','w') as f:
                json.dump(jsonFile,f)


            
            
    # Communication with Normal User
    def userChat(self, channel, client):
        """
        The function receives a message from the client, then sends a message to the client, then
        deactivates the account, then decrements the current client count
        
        :param channel: the channel that the client is connected to
        :param client: The client that is currently connected to the server
        """

        friendID = 0
        # Sending the json file to the client.
        while friendID != -1:
            print("check")
            # Sending a json file to the client.
            if friendID>=-1 or friendID==-2:
                with open("account.json", "rb") as f:
                    jsonFile = json.load(f)                   # load json filefA
                    self.Send_mess(channel, client, json.dumps(jsonFile))    # Send_mess json file
                    self.receive_message(channel, client)           # receive message
            
            # Receiving a friendID from the client and sending a message back to the client.
            friendID = int(self.receive_message(channel, client)) # receive friendID
            self.Send_mess(channel, client, "Received") # Send_mess


       # Receiving a message from the client, then sending a message to the client, then deactivating
       # the account, then decrementing the current client count.
        userName = self.receive_message(channel, client) 
        self.Send_mess(channel, client, "Diconnected")
        self.Deactive_acc(userName)
        self.curr_client -= 1
        
    # Enforce normal user to  login before allow them to chat with other    
    def userHandle(self,channel, client):
        """
        The function userHandle() is called when a user connects to the server. It calls the
        userAuthen() function to authenticate the user, then calls the updateUserList() function to
        update the user list, and finally calls the userChat() function to allow the user to chat
        
        :param channel: The channel that the user is in
        :param client: The client object that is connected to the server
        """
        # Calling the user_Authentication function and passing the channel and client as parameters.
        self.user_Authentication(channel, client)
        
        # Updating the user list.
        self.updateUserList()
        
        # Calling the userChat function and passing the channel and client as parameters.
        self.userChat(channel, client)
        
        
    
    # Admin user just have server-process, which keeps track on database, normal user Informationmation

if __name__=="__main__":
    print("You are Admin")
    admin = Admin()
    
    # Creating a thread that will run the admin.listen() function.
    thread = threading.Thread(target = admin.listen)
    thread.TF= True
    thread.start()

    admin.gui.mainloop()
   