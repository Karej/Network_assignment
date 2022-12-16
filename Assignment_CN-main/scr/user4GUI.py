from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import socket
import threading
import json
import os
from tkinter.font import BOLD, ITALIC

# HOST_ADDR = "192.168.1.12"
HOST_ADDR = socket.gethostbyname(socket.gethostname())
HOST_PORT = 5507


# ADMIN_ADDR = "192.168.1.12"
ADMIN_ADDR = socket.gethostbyname(socket.gethostname())
ADMIN_PORT = 5505

MODE_LOGIN = 1
MODE_SIGNIN = 2

MESS_SUCCESS = "SUCCESS"
MESS_FAILURE = "FAILED"

FORMAT = "utf-8"
MAX_CILENT = 10

outFlag = 0

COLOR_1 = "#005073"
COLOR_2 = "#107dac"
COLOR_3 = "#1ebbd7"
COLOR_4 = "#71c7ec"

friendList = None
connect_friend = ""


class User:
    def __init__(self):
        self.curr_client = 0
        self.host_server = socket.gethostbyname(HOST_ADDR)
        self.port_server = HOST_PORT

        self.host_client = socket.gethostbyname(HOST_ADDR)
        self.port_client = ADMIN_PORT

        self.server_process = socket.socket()
        self.client_process = socket.socket()

        self.server_process.bind((self.host_server, 0))
        self.server_process.listen(10)

    def serverConnect(self, serverAdress):
        self.host_client = serverAdress
        try:
            self.client_process.connect((self.host_client, self.port_client))
            messagebox.showinfo("Information", "Welcome to the Chat Room!!!")
            idFrame.place(relheight=0, relwidth=0)
            loginFrame.place(relheight=1, relwidth=1)
        except:
            messagebox.showerror("ERROR", "You entered invalid ID")

    def signUpPage(self):
        loginFrame.place(relheight=0, relwidth=0)
        signUpFrame.place(relheight=1, relwidth=1)

    def LoginPage(self):
        signUpFrame.place(relheight=0, relwidth=0)
        loginFrame.place(relheight=1, relwidth=1)
# ------------------------ BASIC FUNCTION ---------------------
    # server-process listen to client

    def listen(self):
        while self.curr_client < MAX_CILENT:
            channel, client = self.server_process.accept()
            print(f"\nClient: {client}")
            try:
                self.curr_client += 1
                thr = threading.Thread(
                    target=self.userHandle, args=(channel, client))
                thr.daemon = False
                thr.start()
            except:
                print("error")
    # server-process recieve message from other

    def recv(self, channel, client):
        mess = channel.recv(1024).decode(FORMAT)
        return mess
    # server-process send message to other

    def send(self, channel, client, message):
        channel.sendall(str(message).encode(FORMAT))
    # client-process send account information to admin went wakeup

    def changeFriendHandle(self, name):
        choose = messagebox.askyesno(
            "Warning", "You will leave the current chat, are you sure")
        if (choose):
            messBox.config(state=NORMAL)
            messBox.delete("1.0", END)
            messBox.config(state=DISABLED)
            messInput.delete("0", END)
            self.serverChat(name)
        else:
            pass

    def refreshHandle(self):
        choose = messagebox.askyesno(
            "Warning", "You will leave all the conversation, are you sure")
        if (choose):
            friendLabel.config(text="NULL")
            messBox.config(state=NORMAL)
            messBox.delete("1.0", END)
            messBox.config(state=DISABLED)
            messInput.delete("0", END)
            self.refreshFriendList()
        else:
            pass

    def process(self, strList):
        return json.loads(strList)

    def updateFriendlist(self):
        global friendList
        print("UpdateList")
        index = 0
        friendList = self.process(
            self.client_process.recv(1024).decode(FORMAT))["account"]
        self.client_process.sendall(('Received').encode(FORMAT))
        print("endCheck")
        count = 0
        for friend in friendList:
            if friend["name"] != self.userName and friend["isAct"] == 1:
                print(f"{friend['name']} is here, enter {index} to chat")
                butt = Button(friendsFrame, text=friend["name"])
                butt.config(bg=COLOR_4, fg=COLOR_1, command=lambda name=butt.cget(
                    'text'):  self.changeFriendHandle(name))
                butt.place(relheight=0.05, relwidth=0.9,
                           relx=0.05, rely=0.2+count*0.1)
                count += 1
            elif friend["name"] == self.userName:
                userID = index
            index += 1
        return userID

    def refreshFriendList(self):
        self.client_process.sendall("-1".encode(FORMAT))
        self.client_process.recv(1024).decode(FORMAT)
        self.client_process.sendall(self.userName.encode(FORMAT))
        self.client_process.recv(1024).decode(FORMAT)

        self.client_process.close()
        self.client_process = socket.socket()
        self.client_process.connect((self.host_client, self.port_client))
        self.serverLogin(1, self.userName, self.password)
# ------------------------ SERVER PROCESS ---------------------
    # FOR NORMAL USER
    # Compare to admin user, normal user just have to talk with other

    def userHandle(self, channel, client):
        self.userChat(channel, client)
    # Communication with other normal user

    def userChat(self, channel, client):
        global outFlag

        mess = None
        current_friend = self.recv(channel, client)
        self.send(channel, client, "Received")

        messagebox.showinfo(f"{current_friend} is here",
                            "if you are not connect, refresh friendList")
        while mess != "out":
            mess = self.recv(channel, client)
            self.send(channel, client, "Received")
            if (mess == "sendmess"):
                mess = self.recv(channel, client)
                self.send(channel, client, "Received")
            elif (mess == "sendfile"):
                filename = self.recv(channel, client)
                self.send(channel, client, "Received")

                agree = messagebox.askyesno(
                    f"{current_friend} sends a file", "A file is sent to you, saved file ?")

                if agree:
                    file = filedialog.asksaveasfile(
                        mode='w', defaultextension=".txt")
                    datacome = ""
                    filedata = ""
                    while (datacome != "endsend"):
                        print("begin receive")
                        datacome = self.recv(channel, client)
                        # print(datacome ," ", type(datacome))

                        if ("endsend" in datacome):
                            print("end receive")
                            self.send(channel, client, "Received")
                            break
                        if ("endsend" not in datacome):
                            filedata = filedata + datacome
                            self.send(channel, client, "Received")
                    file.write(filedata)
                    file.close()
                mess = "A file is sent to you"

            if (mess != "out"):
                if current_friend == connect_friend:
                    messBox.config(state=NORMAL)
                    messBox.insert(END, f"{connect_friend}: {mess}\n")
                    messBox.config(state=DISABLED)
                else:
                    print(f"{current_friend}: {mess}")
                    waitBox.config(state=NORMAL)
                    waitBox.insert(END, f"{current_friend}: {mess}\n")
                    waitBox.config(state=DISABLED)
        if (outFlag == 0):
            print("\nYour friend left the conversation")
            print("Enter 'out' for chat with other friend")
        else:
            outFlag = 0
# ------------------------ CLIENT PROCESS ---------------------
    # FOR NORMAL USER
    # Before given ability to communication with other, normal user has to send information to admin user
    # this step i called login/signin

    def serverHandle(self, mode, name, password):
        self.serverLogin(mode, name, password)
    # Execute Authentication follow the server instruction

    def serverLogin(self, mode, name, password):
        mess = None
        # send mode to server
        self.client_process.sendall(str(mode).encode(FORMAT))
        self.client_process.recv(1024).decode(FORMAT)

        self.userName = name
        self.password = password
        # execute login/signin mode
        self.client_process.sendall(str({name: password}).encode(FORMAT))
        # Ensure server receive inorder
        print(self.client_process.recv(1024).decode(FORMAT))
        self.client_process.sendall(
            str({self.host_server: self.server_process.getsockname()[1]}).encode(FORMAT))
        # Ensure server receive inorder
        print(self.client_process.recv(1024).decode(FORMAT))

        self.client_process.sendall(str("Received").encode(FORMAT))
        mess = self.client_process.recv(1024).decode(FORMAT)
        self.client_process.sendall(str("Received").encode(FORMAT))

        print(f"Authen: {mess}")
        if (mess == MESS_FAILURE):
            messagebox.showinfo(
                "ATTENTION", "Failed, try to Log in/Sign in again")
        else:
            messagebox.showinfo("ATTENTION", "Login/Sign in success")
            loginFrame.place(relheight=0, relwidth=0)
            chatFrame.place(relheight=1, relwidth=1)
            self.userName = name
            self.updateFriendlist()
    # Start to communication

    def sendMess(self):
        mess = messInput.get()

        messBox.config(state=NORMAL)
        messBox.insert(END, f"You: {mess}\n")
        messBox.config(state=DISABLED)

        messInput.delete("0", END)

        self.chat_process.sendall("sendmess".encode(FORMAT))
        self.chat_process.recv(1024).decode(FORMAT)
        self.chat_process.sendall(mess.encode(FORMAT))
        self.chat_process.recv(1024).decode(FORMAT)

    def sendFile(self):
        filename = filedialog.askopenfilename(
            initialdir="d:/", title="Select a File", filetypes=(("text file", "*.txt"), ("all files", "*.*")))
        file = open(filename, "r")
        filedata = file.read()
        file.close()

        self.chat_process.sendall("sendfile".encode(FORMAT))
        self.chat_process.recv(1024).decode(FORMAT)
        self.chat_process.sendall(filename.encode(FORMAT))
        self.chat_process.recv(1024).decode(FORMAT)
        self.chat_process.sendall(filedata.encode(FORMAT))
        self.chat_process.recv(1024).decode(FORMAT)
        self.chat_process.sendall("endsend".encode(FORMAT))
        self.chat_process.recv(1024).decode(FORMAT)
        print("done")
        pass

    def onClosing(self):
        try:
            self.client_process.sendall(str(-1).encode(FORMAT))
            self.client_process.recv(1024).decode(FORMAT)

            self.client_process.sendall(str(self.userName).encode(FORMAT))
            self.client_process.recv(1024).decode(FORMAT)
            self.chat_process.sendall("out".encode(FORMAT))
            self.chat_process.recv(1024).decode(FORMAT)
        except:
            pass
        self.client_process.close()
        root.destroy()

    def serverChat(self, name):
        global outFlag
        global connect_friend

        connect_friend = name
        for index, friend in enumerate(friendList):
            if friend["name"] == name:
                friendID = index

        self.client_process.sendall(str(friendID).encode(FORMAT))
        self.client_process.recv(1024)

        userID = self.updateFriendlist()
        try:
            self.chat_process.sendall("out".encode(FORMAT))
            self.chat_process.close()
        except:
            pass

        if (friendID > -1 and friendID != userID):
            self.chat_process = socket.socket()
            self.chat_process.connect(
                (friendList[friendID]["address"], int(friendList[friendID]["port"])))
            self.chat_process.sendall(self.userName.encode(FORMAT))
            self.chat_process.recv(1024).decode(FORMAT)

            connect_friend = friendList[friendID]["name"]
            friendLabel.config(text=connect_friend)
            sendMessBut.config(state=NORMAL)
            sendFileButton.config(state=NORMAL)


if __name__ == "__main__":
    print("Messenger Clone: User")
    user = User()

    server_process = threading.Thread(target=user.listen)
    server_process.daemon = True
    server_process.start()

    root = Tk()

    root.title("GUI for User")
    root.geometry("500x500")
    root.protocol("WM_DELETE_WINDOW", user.onClosing)

    # -------------------ENTER ID FRAME---------------------

    idFrame = Frame(root)
    idFrame.config(bg=COLOR_4)
    idFrame.place(relheight=1, relwidth=1)

    # --------------Print Welcome line----------------------

    idWelcome = Label(idFrame, text="WELCOME TO CHAT ROOM")
    idWelcome.config(bg=COLOR_1, fg=COLOR_4,
                     font=('Calibri', 16, BOLD, ITALIC))
    idWelcome.place(relheight=0.12, relwidth=0.8, relx=0.1, rely=0.1)

    # --------------Print Instruction----------------------

    idIns = Label(idFrame, text='Please input your ID to connect the room')
    idIns.config(bg=COLOR_1, fg=COLOR_4, font=('Calibri', 13))
    idIns.place(relheight=0.07, relwidth=0.8, relx=0.1, rely=0.27)

    # --------------Print Label ID----------------------

    idLabel = Label(idFrame, text="ID Room")
    idLabel.place(relheight=0.05, relwidth=0.15, relx=0.15, rely=0.42)
    idLabel.config(bg=COLOR_3, fg=COLOR_1, font=('Calibri', 11, BOLD))

    # --------------Input bar for entering ID----------------------

    idInputBar = Entry(idFrame)
    idInputBar.config(bg="#ffffff", fg=COLOR_1, relief=SUNKEN, borderwidth=1,
                      font=('Calibri', 11, BOLD))
    idInputBar.place(relheight=0.05, relwidth=0.5, relx=0.35, rely=0.42)

    # --------------Button to connect the room----------------------

    idButton = Button(idFrame, text="Connect")
    idButton.place(relheight=0.05, relwidth=0.15, relx=0.7, rely=0.62)
    idButton.config(bg=COLOR_1, fg=COLOR_4, relief=RAISED, borderwidth=1, font=('Calibri', 11, BOLD),
                    command=lambda: user.serverConnect(idInputBar.get()))

    # --------------------LOGIN FRAME-----------------------

    loginFrame = Frame(root)
    loginFrame.config(bg=COLOR_4)

    # --------------Login Auth Welcome----------------------

    loginAuth = Label(loginFrame, text="LOGIN")
    loginAuth.config(bg=COLOR_1, fg=COLOR_4,
                     font=('Calibri', 16, BOLD, ITALIC))
    loginAuth.place(relheight=0.05, relwidth=0.8, relx=0.1, rely=0.15)

    # --------------Login Instruction----------------------

    loginIns = Label(loginFrame, text="Enter your username and password")
    loginIns.config(bg=COLOR_1, fg=COLOR_4, font=('Calibri', 13, BOLD))
    loginIns.place(relheight=0.05, relwidth=0.8, relx=0.1, rely=0.25)

    # --------------Login Username----------------------

    L_nameLabel = Label(loginFrame, text="Username")
    L_nameLabel.config(bg=COLOR_3, fg=COLOR_1, font=('Calibri', 11, BOLD))
    L_nameLabel.place(relheight=0.05, relwidth=0.15, relx=0.15, rely=0.42)

    L_passLabel = Label(loginFrame, text="Password")
    L_passLabel.config(bg=COLOR_3, fg=COLOR_1, font=('Calibri', 11, BOLD))
    L_passLabel.place(relheight=0.05, relwidth=0.15, relx=0.15, rely=0.52)

    # --------------Login Password----------------------

    L_nameInput = Entry(loginFrame)
    L_nameInput.config(bg="#ffffff", fg=COLOR_1, relief=SUNKEN)
    L_nameInput.place(relheight=0.05, relwidth=0.5, relx=0.35, rely=0.42)

    L_passInput = Entry(loginFrame)
    L_passInput.config(bg="#ffffff", fg=COLOR_1, relief=SUNKEN)
    L_passInput.place(relheight=0.05, relwidth=0.5, relx=0.35, rely=0.52)

    # --------------Login Button to enter the chat room----------------------

    loginButton = Button(loginFrame, text="Log In")
    loginButton.config(bg=COLOR_1, fg=COLOR_4, relief=RAISED, borderwidth=1, font=('Calibri', 11), command=lambda: user.serverHandle(
        1, L_nameInput.get(), L_passInput.get()))
    loginButton.place(relheight=0.05, relwidth=0.2, relx=0.4, rely=0.62)

    # --------------Change to signup page if you don't have an account----------------------

    signUpLabel = Label(loginFrame, text="Don't have an account ?")
    signUpLabel.config(fg=COLOR_1,  bg=COLOR_4, font=(
        'Calibri', 11, BOLD))
    signUpLabel.place(relheight=0.05, relwidth=0.3, relx=0.2, rely=0.72)

    signUpButton = Button(loginFrame, text="Sign Up")
    signUpButton.config(bg=COLOR_1, fg=COLOR_4, relief=RAISED, borderwidth=1, font=(
        'Calibri', 11), command=lambda: user.signUpPage())
    signUpButton.place(relheight=0.05, relwidth=0.15, relx=0.60, rely=0.72)

    # --------------------Sign up FRAME-----------------------

    signUpFrame = Frame(root)
    signUpFrame.config(bg=COLOR_4)

    # --------------Signup Auth Welcome----------------------

    signUpAuth = Label(signUpFrame, text="SIGN UP")
    signUpAuth.config(bg=COLOR_1, fg=COLOR_4,
                      font=('Calibri', 16, BOLD, ITALIC))
    signUpAuth.place(relheight=0.05, relwidth=0.8, relx=0.1, rely=0.15)

    # --------------Signup Instruction----------------------

    signUpIns = Label(
        signUpFrame, text="Enter your username and password")
    signUpIns.config(bg=COLOR_1, fg=COLOR_4, font=('Calibri', 13, BOLD))
    signUpIns.place(relheight=0.05, relwidth=0.8, relx=0.1, rely=0.25)

    # --------------Sign up username----------------------

    S_nameLabel = Label(signUpFrame, text="Username")
    S_nameLabel.config(bg=COLOR_3, fg=COLOR_1, font=('Calibri', 11, BOLD))
    S_nameLabel.place(relheight=0.05, relwidth=0.15, relx=0.15, rely=0.42)

    S_nameInput = Entry(signUpFrame)
    S_nameInput.config(bg="#ffffff", fg=COLOR_1, relief=SUNKEN)
    S_nameInput.place(relheight=0.05, relwidth=0.5, relx=0.35, rely=0.42)

    # --------------Sign up password----------------------

    S_passLabel = Label(signUpFrame, text="Password")
    S_passLabel.config(bg=COLOR_3, fg=COLOR_1, font=('Calibri', 11, BOLD))
    S_passLabel.place(relheight=0.05, relwidth=0.15, relx=0.15, rely=0.52)

    S_passInput = Entry(signUpFrame)
    S_passInput.config(bg="#ffffff", fg=COLOR_1, relief=SUNKEN)
    S_passInput.place(relheight=0.05, relwidth=0.5, relx=0.35, rely=0.52)

    # --------------Sign up button to create account & enter chat room----------------------

    SignUpButton = Button(signUpFrame, text="Sign Up")
    SignUpButton.config(bg=COLOR_1, fg=COLOR_4, relief=RAISED, borderwidth=1, font=('Calibri', 11), command=lambda: user.serverHandle(
        2, S_nameInput.get(), S_passInput.get()))
    SignUpButton.place(relheight=0.05, relwidth=0.2, relx=0.4, rely=0.62)

    # --------------If you have an account then go to Log in page----------------------

    signUpLabel = Label(signUpFrame, text="Have an account ?")
    signUpLabel.config(fg=COLOR_1,  bg=COLOR_4, font=(
        'Calibri', 11, BOLD))
    signUpLabel.place(relheight=0.05, relwidth=0.3, relx=0.2, rely=0.72)

    LogInButton = Button(signUpFrame, text="Log In")
    LogInButton.config(bg=COLOR_1, fg=COLOR_4, relief=RAISED, borderwidth=1, font=(
        'Calibri', 11), command=lambda: user.LoginPage())
    LogInButton.place(relheight=0.05, relwidth=0.15, relx=0.60, rely=0.72)

    # --------------------CHAT FRAME-----------------------

    chatFrame = Frame(root)

    # -------------------- FRIENDS FRAME-----------------------

    friendsFrame = Frame(chatFrame)
    friendsFrame.config(bg=COLOR_3)
    friendsFrame.place(relheight=1, relwidth=0.2, relx=0, rely=0)

    friendsIntro = Label(friendsFrame, text="Friends")
    friendsIntro.config(bg=COLOR_4, fg=COLOR_1)
    friendsIntro.place(relwidth=0.9, relx=0.05, rely=0.05)

    refreshButton = Button(friendsFrame, text="Refresh")
    refreshButton.config(bg=COLOR_4, fg=COLOR_1,
                         command=lambda: user.refreshHandle())
    refreshButton.place(relwidth=0.9, relx=0.05, rely=0.9)

    # --------------------DISPLAY FRAME-----------------------

    displayFrame = Frame(chatFrame)
    displayFrame.config(bg=COLOR_4)
    displayFrame.place(relheight=0.9, relwidth=0.8, relx=0.2, rely=0)

    waitBox = Text(displayFrame)
    waitBox.config(bg=COLOR_4, fg=COLOR_1, state=DISABLED)
    waitBox.place(relwidth=1, relheight=0.5, rely=0)

    messBox = Text(displayFrame)
    messBox.config(bg=COLOR_4, fg=COLOR_1, state=DISABLED)
    messBox.place(relwidth=1, relheight=0.5, rely=0.5)

    notifyLabel = Label(displayFrame,  text="Notification")
    notifyLabel.config(bg=COLOR_1, fg=COLOR_4)
    notifyLabel.place(relwidth=0.2, relheight=0.05, relx=0.8)

    friendLabel = Label(displayFrame, text="NULL")
    friendLabel.config(bg=COLOR_1, fg=COLOR_4)
    friendLabel.place(relwidth=0.2, relheight=0.05, relx=0.8, rely=0.5)

    # --------------------MESSAGE FRAME-----------------------

    messageFrame = Frame(chatFrame)
    messageFrame.config(bg="#ffffff")
    messageFrame.place(relheight=0.1, relwidth=0.8, relx=0.2, rely=0.9)

    sendFileButton = Button(messageFrame, text="FILE")
    sendFileButton.config(bg=COLOR_4, fg=COLOR_1, relief=FLAT,
                          state=DISABLED, command=lambda: user.sendFile())
    sendFileButton.place(relheight=1, relwidth=0.1, relx=0, rely=0)

    sendMessBut = Button(messageFrame, text="CHAT")
    sendMessBut.config(bg=COLOR_3, fg=COLOR_1, relief=FLAT,
                       state=DISABLED, command=lambda: user.sendMess())
    sendMessBut.place(relheight=1, relwidth=0.1, relx=0.9, rely=0)

    messInput = Entry(messageFrame)
    messInput.config(bg="#ffffff", fg=COLOR_1)
    messInput.place(relheight=1, relwidth=0.8, relx=0.1, rely=0)

    root.mainloop()
