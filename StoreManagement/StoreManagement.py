from tkinter import *
import sqlite3
from tkinter import ttk
import tkinter.messagebox as tkMessageBox
from tkinter.filedialog import askopenfile 
from PollyReports import *
from reportlab.pdfgen.canvas import Canvas
import os
from datetime import date,datetime

Home = Tk()
Home.title("Store Management System")
width = Home.winfo_screenwidth()/2
height = Home.winfo_screenheight()/2
screen_width = Home.winfo_screenwidth()
screen_height = Home.winfo_screenheight()
x = (screen_width/2) - (width/2)
y = (screen_height/2) - (height/2)
Home.geometry("%dx%d+%d+%d" % (width, height, x, y))
Home.resizable(0, 0)

#========================================VARIABLES========================================
NAME = StringVar()
ALMIRAHNUMBER = StringVar()
RACKNUMBER = StringVar()
BOXNUMBER = StringVar()
QUANTITY = IntVar()
SEARCH = StringVar()
FIRSTNAME = StringVar()
LASTNAME = StringVar()
DESIGNATION = StringVar()
ITEMNAME = StringVar()
BALANCE = IntVar()
RESULT = StringVar()
NAMEFILTER = StringVar()
ITEMFILTER = StringVar()
ITEMTYPE = StringVar()
DATE = StringVar()
#========================================METHODS==========================================


def ResetAllEntries():
    #Reset user details
    FIRSTNAME.set("")
    LASTNAME.set("")
    DESIGNATION.set("")

    #Reset new item details
    NAME.set("")
    ALMIRAHNUMBER.set("")
    RACKNUMBER.set("")
    BOXNUMBER.set("")
    ITEMNAME.set("")
    QUANTITY.set(0)
    DATE.set(datetime.strftime(date.today(),"%d/%m/%Y"))
    BALANCE.set(0)
    ITEMTYPE.set("")
    #Reset extra details
    NAMEFILTER.set("")
    ITEMFILTER.set("")
    SEARCH.set("")
    RESULT.set("")


def Database():
    global conn, cursor
    conn = sqlite3.connect("Store.db")
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS LogTableInfo (IndexId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                      Name TEXT, AlmirahNumber TEXT, RackNumber TEXT, BoxNumber TEXT, ItemName TEXT, QuantityIssued INTEGER, DateOfIssue TEXT,
                     QuantityReturned TEXT, DateOfReturn TEXT, Type TEXT, Balance INTEGER)""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS InventTable (AlmirahNumber TEXT, RackNumber TEXT,
                      BoxNumber TEXT, ItemName TEXT, Quantity INTEGER, Balance INTEGER, ItemType TEXT, PRIMARY KEY (AlmirahNumber, RackNumber, BoxNumber))""")
    cursor.execute("CREATE TABLE IF NOT EXISTS UserInfo (IndexId INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, FirstName TEXT, LastName TEXT, Designation TEXT)")
    conn.commit()
        
def PrintItemDetails():
    ResetAllEntries()
    printitemdetails = Toplevel()
    printitemdetails.title("Store Management System / Print item details")
    width = 500
    height = 500
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    printitemdetails.geometry("%dx%d+%d+%d" % (width, height, x, y))
    printitemdetails.resizable(0, 0)
    TopPrintingDetails = Frame(printitemdetails, width=600, height=100, bd=1, relief=SOLID)
    TopPrintingDetails.pack(side=TOP, pady=20)
    MidPrintingDetails = Frame(printitemdetails, width=600)
    MidPrintingDetails.pack(side=TOP, pady=20)
    lbl_text = Label(TopPrintingDetails, text="Print item details", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    lbl_result = Label(MidPrintingDetails, textvariable=RESULT, font=('arial', 10), bd=10, fg="red")
    lbl_result.grid(row=3, columnspan=2)
    lbl_itemname = Label(MidPrintingDetails, text="Item name:", font=('arial', 16), bd=10)
    lbl_itemname.grid(row=0, sticky=W)
    itemname = ttk.Combobox(MidPrintingDetails, values=Items(),textvariable=ITEMNAME, font=('arial', 16), width=15)
    itemname.grid(row=0, column=1)
    btn_add = Button(MidPrintingDetails, text="Print", font=('arial', 16), width=30, bg="#009ACD", command=PrintItem)
    btn_add.grid(row=2, columnspan=2, pady=20)

def PrintItem(): 
    if(ITEMNAME.get()!=""):
        Database()
        cursor.execute(f"SELECT * FROM LogTableInfo WHERE ItemName = '{ITEMNAME.get().split('/')[0]}'")
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        if(len(rows) == 0): rows = [{"Name":"-","DateOfIssue":"-","QuantityIssued":"-","DateOfReturn":"-","QuantityReturned":"-"}]
        cursor.execute(f"SELECT Balance, Quantity FROM InventTable WHERE ItemName = '{ITEMNAME.get().split('/')[0]}'")
        fetch = cursor.fetchone()
        rpt = Report(datasource = rows, detailband = Band([
        Element((0, 10), ("Helvetica", 9), key = "Name"),
        Element((100, 10), ("Helvetica", 9), key = "DateOfIssue"),
        Element((200, 10), ("Helvetica", 9), key = "QuantityIssued"),
        Element((300, 10), ("Helvetica", 9), key = "DateOfReturn"),
        Element((400, 10), ("Helvetica", 9), key = "QuantityReturned")]))
        rpt.pageheader = Band([
        Element((0, 0), ("Times-Bold", 14), text = "Item name:"),
        Element((100, 0), ("Helvetica", 12), text = "{}".format(ITEMNAME.get().split('/')[0])),
        Element((0, 17), ("Times-Bold", 14), text = "Balance:"),
        Element((100, 17), ("Helvetica", 12), text = "{}".format(fetch[0])),
        Element((0, 34), ("Times-Bold", 14), text = "Quantity:"), 
        Element((100, 34), ("Helvetica", 12), text = "{}".format(fetch[1])),
        Element((0, 60), ("Helvetica", 10), text = "Name:"),
        Element((100, 60), ("Helvetica", 10), text = "Issued on:"),
        Element((200, 60), ("Helvetica", 10), text = "Quantity issued:"),
        Element((300, 60), ("Helvetica", 10), text = "Returned on:"),
        Element((400, 60), ("Helvetica", 10), text = "Quantity returned:"),
        Rule((0, 72), 7.5*72, thickness = 1)])
        canvas = Canvas("{}.pdf".format(ITEMNAME.get().split('/')[0]))
        rpt.generate(canvas)
        canvas.save()
        cursor.close()
        conn.close()
        RESULT.set("Success")
    else:
        RESULT.set("Select item name.")

def PrintUserDetails():
    ResetAllEntries()
    printuserdetails = Toplevel()
    printuserdetails.title("Store Management System / Print user details")
    width = 500
    height = 500
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    printuserdetails.geometry("%dx%d+%d+%d" % (width, height, x, y))
    printuserdetails.resizable(0, 0)
    TopPrintingDetails = Frame(printuserdetails, width=600, height=100, bd=1, relief=SOLID)
    TopPrintingDetails.pack(side=TOP, pady=20)
    MidPrintingDetails = Frame(printuserdetails, width=600)
    MidPrintingDetails.pack(side=TOP, pady=20)
    lbl_text = Label(TopPrintingDetails, text="Print user details", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    lbl_result = Label(MidPrintingDetails, textvariable=RESULT, font=('arial', 10), bd=10, fg="red")
    lbl_result.grid(row=3, columnspan=2)
    lbl_user = Label(MidPrintingDetails, text="User:", font=('arial', 16), bd=10)
    lbl_user.grid(row=0, sticky=W)
    user = ttk.Combobox(MidPrintingDetails, values=Names(),textvariable=NAME, font=('arial', 16), width=15)
    user.grid(row=0, column=1)
    btn_add = Button(MidPrintingDetails, text="Print", font=('arial', 16), width=30, bg="#009ACD", command=PrintUser)
    btn_add.grid(row=2, columnspan=2, pady=20)

def PrintUser(): 
    if(NAME.get()!=""):
        Database()
        cursor.execute(f"SELECT * FROM LogTableInfo WHERE Name = '{NAME.get()}'")
        columns = [col[0] for col in cursor.description]
        rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
        if(len(rows) == 0): rows = [{"ItemName":"-","DateOfIssue":"-","QuantityIssued":"-","DateOfReturn":"-","QuantityReturned":"-"}]
        rpt = Report(datasource = rows, detailband = Band([
        Element((0, 10), ("Helvetica", 9), key = "ItemName"),
        Element((100, 10), ("Helvetica", 9), key = "DateOfIssue"),
        Element((200, 10), ("Helvetica", 9), key = "QuantityIssued"),
        Element((300, 10), ("Helvetica", 9), key = "DateOfReturn"),
        Element((400, 10), ("Helvetica", 9), key = "QuantityReturned")]))
        rpt.pageheader = Band([
        Element((0, 0), ("Times-Bold", 14), text = "User:"),
        Element((100, 0), ("Helvetica", 12), text = "{}".format(NAME.get())),
        Element((0, 25), ("Helvetica", 10), text = "Item name:"),
        Element((100, 25), ("Helvetica", 10), text = "Issued on:"),
        Element((200, 25), ("Helvetica", 10), text = "Quantity issued:"),
        Element((300, 25), ("Helvetica", 10), text = "Returned on:"),
        Element((400, 25), ("Helvetica", 10), text = "Quantity returned:"),
        Rule((0, 38), 7.5*72, thickness = 1)])
        canvas = Canvas("{}.pdf".format(NAME.get().split('/')[0]))
        rpt.generate(canvas)
        canvas.save()
        cursor.close()
        conn.close()
        RESULT.set("Success")
    else:
        RESULT.set("Select user.")

#========================================INVENTORY FORM===================================

def ShowItemNew():
    global itemnewform
    itemnewform = Toplevel()
    itemnewform.title("Inventory Management System / New item")
    width =Home.winfo_screenwidth()*0.3
    height = Home.winfo_screenheight()*0.6
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    itemnewform.geometry("%dx%d+%d+%d" % (width, height, x, y))
    itemnewform.resizable(0, 0)
    ItemNewForm()

def ItemNewForm():
    ResetAllEntries()
    TopItemNew = Frame(itemnewform, width=600, height=100, bd=1, relief=SOLID)
    TopItemNew.pack(side=TOP, pady=10)
    MidItemNew = Frame(itemnewform, width=600)
    MidItemNew.pack(side=TOP, pady=10)
    lbl_text = Label(TopItemNew, text="New item", font=('arial', 14), width=600)
    lbl_text.pack(fill=X)
    lbl_almirahnumber = Label(MidItemNew, text="Almirah number:", font=('arial', 12), bd=10)
    lbl_almirahnumber.grid(row=0, sticky=W)
    lbl_racknumber = Label(MidItemNew, text="Rack number:", font=('arial', 12), bd=10)
    lbl_racknumber.grid(row=1, sticky=W)
    lbl_boxnumber = Label(MidItemNew, text="Box number:", font=('arial', 12), bd=10)
    lbl_boxnumber.grid(row=2, sticky=W)
    lbl_itemname = Label(MidItemNew, text="Item name:", font=('arial', 12), bd=10)
    lbl_itemname.grid(row=3, sticky=W)
    lbl_quantity = Label(MidItemNew, text="Quantity:", font=('arial', 12), bd=10)
    lbl_quantity.grid(row=4, sticky=W)
    lbl_itemtype = Label(MidItemNew, text="Item Type:", font=('arial', 12), bd=10)
    lbl_itemtype.grid(row=5, sticky=W)
    lbl_result = Label(MidItemNew, textvariable=RESULT, font=('arial', 8), bd=10, fg="red")
    lbl_result.grid(row=7, columnspan = 2)

    almirahnumber = Entry(MidItemNew, textvariable = ALMIRAHNUMBER, font=('arial', 12), width=15)
    almirahnumber.grid(row=0, column=1)
    racknumber = Entry(MidItemNew, textvariable = RACKNUMBER, font=('arial', 12), width=15)
    racknumber.grid(row=1, column=1)
    boxnumber = Entry(MidItemNew, textvariable = BOXNUMBER, font=('arial', 12), width=15)
    boxnumber.grid(row=2, column=1)
    itemname = Entry(MidItemNew, textvariable = ITEMNAME, font=('arial', 12), width=15)
    itemname.grid(row=3, column=1)
    quantity = Entry(MidItemNew, textvariable = QUANTITY, font=('arial', 12), width=15)
    quantity.grid(row=4, column=1)
    itemtype = ttk.Combobox(MidItemNew, textvariable = ITEMTYPE, values = ["Consumable", "Non-Consumable", "NCF"], font=('arial', 12), width=15)
    itemtype.grid(row=5, column=1)
    btn_add = Button(MidItemNew, text="Save", font=('arial', 10), width=30, bg="#009ACD", command=ItemNew)
    btn_add.grid(row=6, columnspan=2, pady=10)

def ItemNew():
    Database()
    if(ALMIRAHNUMBER.get()!="" and RACKNUMBER.get()!="" and BOXNUMBER.get()!="" and ITEMNAME.get()!="" 
      and QUANTITY.get()!=None and QUANTITY.get()>0 and ITEMTYPE.get()!=""):
        cursor.execute(f"SELECT * FROM InventTable WHERE AlmirahNumber = '{ALMIRAHNUMBER.get()}' and RackNumber = '{RACKNUMBER.get()}' and BoxNumber = '{BOXNUMBER.get()}'")
        fetch = cursor.fetchone()
        if fetch is not None:
            RESULT.set("Item exists")
            return
        cursor.execute("INSERT INTO InventTable (AlmirahNumber, RackNumber, BoxNumber, ItemName, Quantity, Balance, ItemType) VALUES(?, ?, ?, ?, ?, ?, ?)",
                      (ALMIRAHNUMBER.get(), RACKNUMBER.get(), BOXNUMBER.get(), ITEMNAME.get(), QUANTITY.get(), QUANTITY.get(), ITEMTYPE.get()))
        conn.commit()
        ResetAllEntries()
        RESULT.set("Success")
    else: 
        RESULT.set("Please enter all details")
    cursor.close()
    conn.close()

#========================================USER FORM===================================

def ShowUserNew():
    global usernewform
    usernewform = Toplevel()
    usernewform.title("Store Management System / Create new user")
    width = 500
    height = 400
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    usernewform.geometry("%dx%d+%d+%d" % (width, height, x, y))
    usernewform.resizable(0, 0)
    UserNewForm()

def UserNewForm():
    ResetAllEntries()
    TopUserNew = Frame(usernewform, width=600, height=100, bd=1, relief=SOLID)
    TopUserNew.pack(side=TOP, pady=20)
    MidUserNew = Frame(usernewform, width=600)
    MidUserNew.pack(side=TOP, pady=20)
    lbl_text = Label(TopUserNew, text="New user", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    lbl_firstname = Label(MidUserNew, text="First Name:", font=('arial', 16), bd=10)
    lbl_firstname.grid(row=0, sticky=W)
    lbl_lastname = Label(MidUserNew, text="Last Name:", font=('arial', 16), bd=10)
    lbl_lastname.grid(row=1, sticky=W)
    lbl_designation = Label(MidUserNew, text="Designation:", font=('arial', 16), bd=10)
    lbl_designation.grid(row=2, sticky=W)
    lbl_result = Label(MidUserNew, textvariable=RESULT, font=('arial', 10), bd=10,fg="red")
    lbl_result.grid(row=4, columnspan=2)
    firstname = Entry(MidUserNew, textvariable = FIRSTNAME, font=('arial', 16), width=15)
    firstname.grid(row=0, column=1)
    lastname = Entry(MidUserNew, textvariable = LASTNAME, font=('arial', 16), width=15)
    lastname.grid(row=1, column=1)
    designation = Entry(MidUserNew, textvariable = DESIGNATION, font=('arial', 16), width=15)
    designation.grid(row=2, column=1)
    btn_add = Button(MidUserNew, text="Save", font=('arial', 16), width=30, bg="#009ACD", command=UserNew)
    btn_add.grid(row=3, columnspan=2, pady=20)

def UserNew():
    if(FIRSTNAME.get()!="" and LASTNAME.get()!="" and DESIGNATION.get()!=""):
        Database()
        cursor.execute("INSERT INTO UserInfo (FirstName, LastName, Designation) VALUES(?, ?, ?)", (FIRSTNAME.get(), LASTNAME.get(), DESIGNATION.get()))
        conn.commit()
        cursor.close()
        conn.close()
        ResetAllEntries()
    else:
       RESULT.set("Please enter all details")

#========================================ISSUE FORM===================================

def ShowIssueItem():
    global issuenewform
    issuenewform = Toplevel()
    issuenewform.title("Store Management System / Issue item")
    width = 500
    height = 500
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    issuenewform.geometry("%dx%d+%d+%d" % (width, height, x, y))
    issuenewform.resizable(0, 0)
    IssueNewForm()

def IssueNewForm():
    global name, itemname 
    ResetAllEntries()
    TopIssueNew = Frame(issuenewform, width=600, height=100, bd=1, relief=SOLID)
    TopIssueNew.pack(side=TOP, pady=20)
    lbl_text = Label(TopIssueNew, text="Issue item", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    MidIssueNew = Frame(issuenewform, width=600)
    MidIssueNew.pack(side=TOP, pady=20)
    lbl_name = Label(MidIssueNew, text="Name:", font=('arial', 16), bd=10)
    lbl_name.grid(row=0, sticky=W)
    lbl_date = Label(MidIssueNew, text="Date of issue:", font=('arial', 16), bd=10)
    lbl_date.grid(row=1, sticky=W)
    lbl_itemname = Label(MidIssueNew, text="Item name:", font=('arial', 16), bd=10)
    lbl_itemname.grid(row=2, sticky=W)
    lbl_balance = Label(MidIssueNew, text="Balance:", font=('arial', 16), bd=10)
    lbl_balance.grid(row=3, sticky=W)
    lbl_quantity = Label(MidIssueNew, text="Quantity issued:", font=('arial', 16), bd=10)
    lbl_quantity.grid(row=4, sticky=W)
    lbl_result = Label(MidIssueNew, textvariable = RESULT, font=('arial', 10), bd=10, fg="red")
    lbl_result.grid(row=6, columnspan = 2)
    name = ttk.Combobox(MidIssueNew, values = Names(), textvariable = NAME, font=('arial', 16), width=15)
    name.grid(row=0, column=1)
    namefilter = Entry(MidIssueNew, textvariable=NAMEFILTER, font=('arial', 8), width=8)
    namefilter.grid(row=0, column=2)
    btn_namefilter = Button(MidIssueNew, text="Search", font=('arial', 8), width=5, bg="#009ACD", command = FilterName)
    btn_namefilter.grid(row=0, column=3)
    issueDate = Entry(MidIssueNew, textvariable=DATE, font=('arial', 16), width=15)
    issueDate.grid(row=1, column=1)
    itemname = ttk.Combobox(MidIssueNew, values = Items(), textvariable=ITEMNAME, font=('arial', 16), width=15)
    itemname.bind("<<ComboboxSelected>>", SetBalance)
    itemname.grid(row=2, column=1)
    itemfilter = Entry(MidIssueNew, textvariable=ITEMFILTER, font=('arial', 8), width=8)
    itemfilter.grid(row=2, column=2)
    btn_itemfilter = Button(MidIssueNew, text="Search", font=('arial', 8), width=5, bg="#009ACD", command = FilterItemName)
    btn_itemfilter.grid(row=2, column=3)
    balance = Label(MidIssueNew, textvariable=BALANCE, font=('arial', 16), bd=10)
    balance.grid(row=3, column=1)
    quantity = Entry(MidIssueNew, textvariable=QUANTITY, font=('arial', 16), width=15)
    quantity.grid(row=4, column=1)
    btn_add = Button(MidIssueNew, text="Save", font=('arial', 16), width=30, bg="#009ACD", command=IssueNew)
    btn_add.grid(row=5, columnspan=2, pady=20)

def FilterItemName():
    itemname['values'] = Items()

def Items():
    Database()
    cursor.execute(f"SELECT ItemName, Balance FROM InventTable WHERE ItemName LIKE '{ITEMFILTER.get()}%'")
    fetch = cursor.fetchall()
    list = ["{}/Balance:{}".format(data[0], data[1]) for data in fetch]
    cursor.close()
    conn.close()
    return list

def FilterName():
    name['values'] = Names()

def Names():
    Database()
    cursor.execute(f"SELECT FirstName, LastName, Designation FROM userInfo WHERE FirstName LIKE '{NAMEFILTER.get()}%'")
    fetch = cursor.fetchall()
    list = ["{} {}/{}".format(data[0], data[1], data[2]) for data in fetch]
    cursor.close()
    conn.close()
    return list

def SetBalance(event = None):
    if(ITEMNAME.get()!=""):
        BALANCE.set(int(ITEMNAME.get().split('/Balance:')[1]))
        ITEMNAME.set(ITEMNAME.get().split('/Balance:')[0])

def IssueNew():
    format = "%d/%m/%Y"
    Delta = datetime.strptime(DATE.get(),format) - datetime.strptime(date.today().strftime(format),format)
    if(ITEMNAME.get()!="" and NAME.get()!="" and QUANTITY.get()!=None and QUANTITY.get()>0):
        if(Delta.days <= 0):
            newbalance = BALANCE.get() - QUANTITY.get()
            if(newbalance >= 0):
                Database()
                cursor.execute(f"SELECT AlmirahNumber, RackNumber, BoxNumber FROM InventTable WHERE ItemName = '{ITEMNAME.get()}' and Balance = {BALANCE.get()}")
                data = cursor.fetchone()
                cursor.execute("UPDATE InventTable SET Balance = {} WHERE AlmirahNumber = '{}' and RackNumber = '{}' and BoxNumber = '{}'".format(newbalance, data[0], data[1], data[2]))
                cursor.execute("INSERT INTO LogTableInfo (Name, ItemName, AlmirahNumber, RackNumber, BoxNumber, DateOfIssue, QuantityIssued, Balance) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                          (NAME.get(), ITEMNAME.get(), data[0], data[1], data[2], DATE.get(), QUANTITY.get(), newbalance))
                conn.commit()
                cursor.close()
                conn.close()
                ResetAllEntries()
            else: 
                RESULT.set("Insufficient balance")
        else: 
            RESULT.set("Cannot be issued for future dates")
    else: 
        RESULT.set("Please enter all details")

#========================================RETURN FORM===================================

def ShowReturnItem():
    global returnnewform
    returnnewform = Toplevel()
    returnnewform.title("Store Management System / Return item")
    width = 500
    height = 500
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    returnnewform.geometry("%dx%d+%d+%d" % (width, height, x, y))
    returnnewform.resizable(0, 0)
    ReturnNewForm()

def ReturnNewForm():
    global name, itemname 
    ResetAllEntries()
    TopReturnNew = Frame(returnnewform, width=600, height=100, bd=1, relief=SOLID)
    TopReturnNew.pack(side=TOP, pady=20)
    lbl_text = Label(TopReturnNew, text="Return item", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    MidReturnNew = Frame(returnnewform, width=600)
    MidReturnNew.pack(side=TOP, pady=20)
    lbl_name = Label(MidReturnNew, text="Name:", font=('arial', 16), bd=10)
    lbl_name.grid(row=0, sticky=W)
    lbl_date = Label(MidReturnNew, text="Date of issue:", font=('arial', 16), bd=10)
    lbl_date.grid(row=1, sticky=W)
    lbl_itemname = Label(MidReturnNew, text="Item name:", font=('arial', 16), bd=10)
    lbl_itemname.grid(row=2, sticky=W)
    lbl_quantity = Label(MidReturnNew, text="Quantity issued:", font=('arial', 16), bd=10)
    lbl_quantity.grid(row=3, sticky=W)
    lbl_result = Label(MidReturnNew, textvariable = RESULT, font=('arial', 10), bd=10, fg="red")
    lbl_result.grid(row=5, columnspan = 2)
    name = ttk.Combobox(MidReturnNew, values = Names(), textvariable = NAME, font=('arial', 16), width=15)
    name.grid(row=0, column=1)
    namefilter = Entry(MidReturnNew, textvariable=NAMEFILTER, font=('arial', 8), width=8)
    namefilter.grid(row=0, column=2)
    btn_namefilter = Button(MidReturnNew, text="Search", font=('arial', 8), width=5, bg="#009ACD", command = FilterName)
    btn_namefilter.grid(row=0, column=3)
    returnDate = Entry(MidReturnNew, textvariable=DATE, font=('arial', 16), width=15)
    returnDate.grid(row=1, column=1)
    itemname = ttk.Combobox(MidReturnNew, values = Items(), textvariable=ITEMNAME, font=('arial', 16), width=15)
    itemname.bind("<<ComboboxSelected>>", SetBalance)
    itemname.grid(row=2, column=1)
    itemfilter = Entry(MidReturnNew, textvariable=ITEMFILTER, font=('arial', 8), width=8)
    itemfilter.grid(row=2, column=2)
    btn_itemfilter = Button(MidReturnNew, text="Search", font=('arial', 8), width=5, bg="#009ACD", command = FilterItemName)
    btn_itemfilter.grid(row=2, column=3)
    quantity = Entry(MidReturnNew, textvariable=QUANTITY, font=('arial', 16), width=15)
    quantity.grid(row=3, column=1)
    btn_add = Button(MidReturnNew, text="Save", font=('arial', 16), width=30, bg="#009ACD", command=ReturnNew)
    btn_add.grid(row=4, columnspan=2, pady=20)

def ReturnNew():
    format = "%d/%m/%Y"
    Delta = datetime.strptime(DATE.get(),format) - datetime.strptime(date.today().strftime(format),format)
    if(ITEMNAME.get()!="" and NAME.get()!="" and QUANTITY.get()!=None and QUANTITY.get()>0):
        if(Delta.days <= 0):
            newbalance = BALANCE.get() + QUANTITY.get()
            if(newbalance >= 0):
                Database()
                cursor.execute(f"SELECT AlmirahNumber, RackNumber, BoxNumber FROM InventTable WHERE ItemName = '{ITEMNAME.get()}' and Balance = {BALANCE.get()}")
                data = cursor.fetchone()
                cursor.execute("UPDATE InventTable SET Balance = {} WHERE AlmirahNumber = '{}' and RackNumber = '{}' and BoxNumber = '{}'".format(newbalance, data[0], data[1], data[2]))
                cursor.execute("INSERT INTO LogTableInfo (Name, ItemName, AlmirahNumber, RackNumber, BoxNumber, DateOfReturn, QuantityReturned, Balance) VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
                            (NAME.get(), ITEMNAME.get(), data[0], data[1], data[2], DATE.get(), QUANTITY.get(), newbalance))
                conn.commit()
                cursor.close()
                conn.close()
                ResetAllEntries()
            else: 
                RESULT.set("Insufficient balance")
        else: 
            RESULT.set("Cannot be issued for future dates")
    else: 
        RESULT.set("Please enter all details")

#========================================LOG VIEW FORM===================================

def LogForm():
    global tree
    ResetAllEntries()
    TopLogForm = Frame(logform, width=600, bd=1, relief=SOLID)
    TopLogForm.pack(side=TOP, fill=X)
    LeftLogForm = Frame(logform, width=100)
    LeftLogForm.pack(side=LEFT, fill=Y)
    MidLogForm = Frame(logform, width=1100)
    MidLogForm.pack(side=RIGHT)
    lbl_text = Label(TopLogForm, text="Logs", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    lbl_txtsearch = Label(LeftLogForm, text="Search by name", font=('arial', 16))
    lbl_txtsearch.pack(side=TOP, anchor=W)
    search = Entry(LeftLogForm, textvariable=SEARCH, font=('arial', 16), width=10)
    search.pack(side=TOP,  padx=10, fill=X)
    btn_search = Button(LeftLogForm, text="Search", command=Search)
    btn_search.pack(side=TOP, padx=10, pady=10, fill=X)
    btn_reset = Button(LeftLogForm, text="Reset", command=Reset)
    btn_reset.pack(side=TOP, padx=10, pady=10, fill=X)
    scrollbarx = Scrollbar(MidLogForm, orient=HORIZONTAL)
    scrollbary = Scrollbar(MidLogForm, orient=VERTICAL)
    tree = ttk.Treeview(MidLogForm, columns=("Index","Name", "Item name", "Date of issue", "Quantity issued", "Date of return", "Quantity returned", "Item balance"), selectmode="extended", height=100, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
    scrollbary.config(command=tree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)
    scrollbarx.config(command=tree.xview)
    scrollbarx.pack(side=BOTTOM, fill=X)
    tree.heading('Index', text="Index",anchor=W)
    tree.heading('Name', text="Name",anchor=W)
    tree.heading('Item name', text="Item name",anchor=W)
    tree.heading('Date of issue', text="Date of issue",anchor=W)
    tree.heading('Quantity issued', text="Quantity issued",anchor=W)
    tree.heading('Date of return', text="Date of return",anchor=W)
    tree.heading('Quantity returned', text="Quantity returned",anchor=W)
    tree.heading('Item balance', text="Item balance",anchor=W)
    tree.column('#0', stretch=NO, minwidth=0, width=0)
    tree.column('#1', stretch=NO, minwidth=0, width=120)
    tree.column('#2', stretch=NO, minwidth=0, width=120)
    tree.column('#3', stretch=NO, minwidth=0, width=120)
    tree.column('#4', stretch=NO, minwidth=0, width=120)
    tree.column('#5', stretch=NO, minwidth=0, width=120)
    tree.column('#6', stretch=NO, minwidth=0, width=120)
    tree.column('#7', stretch=NO, minwidth=0, width=120)
    tree.column('#8', stretch=NO, minwidth=0, width=120)
    tree.pack()
    DisplayData()

def DisplayData(event = None):
    Database()
    tree.delete(*tree.get_children())
    cursor.execute("SELECT IndexId, Name, ItemName, DateOfIssue, QuantityIssued, DateOfReturn, QuantityReturned, Balance FROM LogTableInfo")
    fetch = cursor.fetchall()
    for data in fetch:
        tree.insert('', 'end', values=(data))
    cursor.close()
    conn.close()


#========================================USER VIEW FORM===================================

def UserForm():
    global usertree
    ResetAllEntries()
    TopUserForm = Frame(userform, width=600, bd=1, relief=SOLID)
    TopUserForm.pack(side=TOP, fill=X)
    LeftUserForm = Frame(userform, width=600)
    LeftUserForm.pack(side=LEFT, fill=Y)
    MidUserForm = Frame(userform, width=600)
    MidUserForm.pack(side=RIGHT)
    lbl_text = Label(TopUserForm, text="Users", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    lbl_txtsearch = Label(LeftUserForm, text="Search by first name", font=('arial', 16))
    lbl_txtsearch.pack(side=TOP, anchor=W)
    search = Entry(LeftUserForm, textvariable=SEARCH, font=('arial', 16), width=10)
    search.pack(side=TOP,  padx=10, fill=X)
    btn_search = Button(LeftUserForm, text="Search", command=UserSearch)
    btn_search.pack(side=TOP, padx=10, pady=10, fill=X)
    btn_reset = Button(LeftUserForm, text="Reset", command=UserReset)
    btn_reset.pack(side=TOP, padx=10, pady=10, fill=X)
    btn_delete = Button(LeftUserForm, text="Delete", command=UserDelete)
    btn_delete.pack(side=TOP, padx=10, pady=10, fill=X)
    scrollbarx = Scrollbar(MidUserForm, orient=HORIZONTAL)
    scrollbary = Scrollbar(MidUserForm, orient=VERTICAL)
    usertree = ttk.Treeview(MidUserForm, columns=("Index", "First name", "Last name", "Designation"), selectmode="extended", height=100, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
    scrollbary.config(command=usertree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)
    scrollbarx.config(command=usertree.xview)
    scrollbarx.pack(side=BOTTOM, fill=X)
    usertree.heading('Index', text="Index",anchor=W)
    usertree.heading('First name', text="First name",anchor=W)
    usertree.heading('Last name', text="Last name",anchor=W)
    usertree.heading('Designation', text="Designation",anchor=W)
    usertree.column('#0', stretch=NO, minwidth=0, width=0)
    usertree.column('#1', stretch=NO, minwidth=0, width=0)
    usertree.column('#2', stretch=NO, minwidth=0, width=100)
    usertree.column('#3', stretch=NO, minwidth=0, width=100)
    usertree.pack()
    UserDisplayData()

def UserDisplayData(event = None):
    Database()
    usertree.delete(*usertree.get_children())
    cursor.execute("SELECT * FROM UserInfo")
    fetch = cursor.fetchall()
    for data in fetch:
        usertree.insert('', 'end', values=(data))
    cursor.close()
    conn.close()


#========================================INVENTORY VIEW FORM===================================

def InventoryForm():
    global inventorytree
    ResetAllEntries()
    TopInventoryForm = Frame(inventoryform, width=600, bd=1, relief=SOLID)
    TopInventoryForm.pack(side=TOP, fill=X)
    LeftInventoryForm = Frame(inventoryform, width=100)
    LeftInventoryForm.pack(side=LEFT, fill=Y)
    MidInventoryForm = Frame(inventoryform, width=1100)
    MidInventoryForm.pack(side=RIGHT)
    lbl_text = Label(TopInventoryForm, text="Inventory", font=('arial', 18), width=600)
    lbl_text.pack(fill=X)
    lbl_txtsearch = Label(LeftInventoryForm, text="Search by item name", font=('arial', 16))
    lbl_txtsearch.pack(side=TOP, anchor=W)
    search = Entry(LeftInventoryForm, textvariable=SEARCH, font=('arial', 16), width=10)
    search.pack(side=TOP,  padx=10, fill=X)
    btn_search = Button(LeftInventoryForm, text="Search", command=InventorySearch)
    btn_search.pack(side=TOP, padx=10, pady=10, fill=X)
    btn_reset = Button(LeftInventoryForm, text="Reset", command=InventoryReset)
    btn_reset.pack(side=TOP, padx=10, pady=10, fill=X)
    btn_delete = Button(LeftInventoryForm, text="Delete", command=InventoryDelete)
    btn_delete.pack(side=TOP, padx=10, pady=10, fill=X)
    btn_edit = Button(LeftInventoryForm, text="Edit", command=InventoryEdit)
    btn_edit.pack(side=TOP, padx=10, pady=10, fill=X)
    scrollbarx = Scrollbar(MidInventoryForm, orient=HORIZONTAL)
    scrollbary = Scrollbar(MidInventoryForm, orient=VERTICAL)
    inventorytree = ttk.Treeview(MidInventoryForm, columns=("Almirah number", "Rack number", "Box number", "Item name", "Quantity", "Balance", "Item type"), selectmode="extended", height=100, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)
    scrollbary.config(command=inventorytree.yview)
    scrollbary.pack(side=RIGHT, fill=Y)
    scrollbarx.config(command=inventorytree.xview)
    scrollbarx.pack(side=BOTTOM, fill=X)
    inventorytree.heading('Almirah number', text="Almirah number",anchor=W)
    inventorytree.heading('Rack number', text="Rack number",anchor=W)
    inventorytree.heading('Box number', text="Box number",anchor=W)
    inventorytree.heading('Item name', text="Item name",anchor=W)
    inventorytree.heading('Quantity', text="Quantity",anchor=W)
    inventorytree.heading('Balance', text="Balance",anchor=W)
    inventorytree.heading('Item type', text="Item type",anchor=W)
    inventorytree.column('#0', stretch=NO, minwidth=0, width=0)
    inventorytree.column('#1', stretch=NO, minwidth=0, width=100)
    inventorytree.column('#2', stretch=NO, minwidth=0, width=100)
    inventorytree.column('#3', stretch=NO, minwidth=0, width=100)
    inventorytree.column('#4', stretch=NO, minwidth=0, width=100)
    inventorytree.column('#5', stretch=NO, minwidth=0, width=100)
    inventorytree.column('#6', stretch=NO, minwidth=0, width=100)
    inventorytree.column('#7', stretch=NO, minwidth=0, width=100)
    inventorytree.pack()
    InventoryDisplayData()

def InventoryDisplayData(event = None):
    Database()
    inventorytree.delete(*inventorytree.get_children())
    cursor.execute("SELECT * FROM InventTable")
    fetch = cursor.fetchall()
    for data in fetch:
        inventorytree.insert('', 'end', values=(data))
    cursor.close()
    conn.close()

#========================================BUTTONS FOR INVENTORY VIEW===================================

def InventorySearch():
    if SEARCH.get() != "":
        inventorytree.delete(*inventorytree.get_children())
        Database()
        cursor.execute(f"SELECT * FROM InventTable WHERE ItemName LIKE '%{SEARCH.get()}%'")
        fetch = cursor.fetchall()
        for data in fetch:
            inventorytree.insert('', 'end', values=(data))
        cursor.close()
        conn.close()

def InventoryReset():
    inventorytree.delete(*inventorytree.get_children())
    InventoryDisplayData()
    SEARCH.set("")

def InventoryDelete():
    if not inventorytree.selection():
       print("ERROR")
    else:
        result = tkMessageBox.askquestion('Inventory Management System', 'Are you sure you want to delete this record?', icon="warning")
        if result == 'yes':
            curItem = inventorytree.focus()
            contents =(inventorytree.item(curItem))
            selecteditem = contents['values']
            inventorytree.delete(curItem)
            Database()
            cursor.execute(f"DELETE FROM InventTable WHERE AlmirahNumber = '{selecteditem[0]}' and RackNumber = '{selecteditem[1]}' and BoxNumber = '{selecteditem[2]}'")
            conn.commit()
            cursor.close()
            conn.close()

def setValues(selecteditem):
    ALMIRAHNUMBER.set(selecteditem[0])
    RACKNUMBER.set(selecteditem[1])
    BOXNUMBER.set(selecteditem[2])
    ITEMNAME.set(selecteditem[3])
    ITEMTYPE.set(selecteditem[6])

def InventoryEdit():
    if not inventorytree.selection():
       print("ERROR")
    else:
        global itemnewform
        ResetAllEntries()
        curItem = inventorytree.focus()
        contents =(inventorytree.item(curItem))
        selecteditem = contents['values']
        setValues(selecteditem)
        itemnewform = Toplevel()
        itemnewform.title("Store Management System / Edit item")
        width =Home.winfo_screenwidth()*0.4
        height = Home.winfo_screenheight()*0.8
        screen_width = Home.winfo_screenwidth()
        screen_height = Home.winfo_screenheight()
        x = (screen_width/2) - (width/2)
        y = (screen_height/2) - (height/2)
        itemnewform.geometry("%dx%d+%d+%d" % (width, height, x, y))
        itemnewform.resizable(0, 0)
        TopItemNew = Frame(itemnewform, width=600, height=100, bd=1, relief=SOLID)
        TopItemNew.pack(side=TOP, pady=10)
        MidItemNew = Frame(itemnewform, width=600)
        MidItemNew.pack(side=TOP, pady=10)
        lbl_text = Label(TopItemNew, text="Edit item", font=('arial', 14), width=600)
        lbl_text.pack(fill=X)
        lbl_almirahnumber = Label(MidItemNew, text="Almirah number:", font=('arial', 12), bd=10)
        lbl_almirahnumber.grid(row=0, sticky=W)
        lbl_racknumber = Label(MidItemNew, text="Rack number:", font=('arial', 12), bd=10)
        lbl_racknumber.grid(row=1, sticky=W)
        lbl_boxnumber = Label(MidItemNew, text="Box number:", font=('arial', 12), bd=10)
        lbl_boxnumber.grid(row=2, sticky=W)
        lbl_itemname = Label(MidItemNew, text="Item name:", font=('arial', 12), bd=10)
        lbl_itemname.grid(row=3, sticky=W)
        lbl_itemtype = Label(MidItemNew, text="Item Type:", font=('arial', 12), bd=10)
        lbl_itemtype.grid(row=4, sticky=W)
        lbl_result = Label(MidItemNew, textvariable=RESULT, font=('arial', 8), bd=10, fg="red")
        lbl_result.grid(row=6, columnspan = 2)
        almirahnumber = Label(MidItemNew, textvariable = ALMIRAHNUMBER, font=('arial', 12))
        almirahnumber.grid(row=0, column=1)
        racknumber = Label(MidItemNew, textvariable = RACKNUMBER, font=('arial', 12))
        racknumber.grid(row=1, column=1)
        boxnumber = Label(MidItemNew, textvariable = BOXNUMBER, font=('arial', 12))
        boxnumber.grid(row=2, column=1)
        itemname = Entry(MidItemNew, textvariable = ITEMNAME, font=('arial', 12), width=15)
        itemname.grid(row=3, column=1)
        itemtype = ttk.Combobox(MidItemNew, textvariable = ITEMTYPE, values = ["Consumable", "Non-Consumable", "NCF"], font=('arial', 12), width=15)
        itemtype.grid(row=4, column=1)
        btn_add = Button(MidItemNew, text="Update", font=('arial', 10), width=30, bg="#009ACD", command=ItemEdit)
        btn_add.grid(row=5, columnspan=2, pady=10)


def ItemEdit():
    if ITEMNAME.get()!="" and ITEMTYPE.get()!="" and ALMIRAHNUMBER.get()!="" and RACKNUMBER.get()!="" and BOXNUMBER.get()!="":
        Database()
        cursor.execute("UPDATE InventTable SET ItemName = '{}', ItemType = '{}' WHERE AlmirahNumber = '{}'and RackNumber = '{}' and BoxNumber = '{}'"
                       .format(ITEMNAME.get(), ITEMTYPE.get(), ALMIRAHNUMBER.get(), RACKNUMBER.get(), BOXNUMBER.get()))
        conn.commit()
        cursor.close()
        conn.close()
        itemnewform.destroy()
        ResetAllEntries()
        InventoryReset()
    else:
        RESULT.set("Enter details")
    
    

#========================================BUTTONS FOR USER VIEW===================================

def UserSearch():
    if SEARCH.get() != "":
        usertree.delete(*usertree.get_children())
        Database()
        cursor.execute(f"SELECT * FROM UserInfo WHERE FirstName LIKE '%{SEARCH.get()}%'")
        fetch = cursor.fetchall()
        for data in fetch:
            usertree.insert('', 'end', values=(data))
        cursor.close()
        conn.close()

def UserReset():
    usertree.delete(*usertree.get_children())
    UserDisplayData()
    SEARCH.set("")

def UserDelete():
    if not usertree.selection():
       print("ERROR")
    else:
        result = tkMessageBox.askquestion('Store Management System', 'Are you sure you want to delete this record?', icon="warning")
        if result == 'yes':
            curItem = usertree.focus()
            contents =(usertree.item(curItem))
            selecteditem = contents['values']
            usertree.delete(curItem)
            Database()
            cursor.execute(f"DELETE FROM UserInfo WHERE IndexId = {selecteditem[0]}")
            conn.commit()
            cursor.close()
            conn.close()


#========================================BUTTONS FOR LOG VIEW===================================

def Search():
    if SEARCH.get() != "":
        tree.delete(*tree.get_children())
        Database()
        cursor.execute(f"SELECT IndexId, Name, ItemName, DateOfIssue, QuantityIssued, DateOfReturn, QuantityReturned, Balance FROM LogTableInfo WHERE Name LIKE '%{SEARCH.get()}%'")
        fetch = cursor.fetchall()
        for data in fetch:
            tree.insert('', 'end', values=(data))
        cursor.close()
        conn.close()

def Reset():
    tree.delete(*tree.get_children())
    DisplayData()
    SEARCH.set("")


def ShowLogView():
    global logform
    logform = Toplevel()
    logform.title("Store Management System / View Logs")
    width = 1024
    height = 520
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    logform.geometry("%dx%d+%d+%d" % (width, height, x, y))
    logform.resizable(True, True)
    LogForm()


def ShowUserView():
    global userform
    userform = Toplevel()
    userform.title("Store Management System / View users")
    width = 600
    height = 500
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    userform.geometry("%dx%d+%d+%d" % (width, height, x, y))
    userform.resizable(True, True)
    UserForm()


def ShowInventoryView():
    global inventoryform
    inventoryform = Toplevel()
    inventoryform.title("Store Management System / View items")
    width = 1024
    height = 520
    screen_width = Home.winfo_screenwidth()
    screen_height = Home.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    inventoryform.geometry("%dx%d+%d+%d" % (width, height, x, y))
    inventoryform.resizable(True, True)
    InventoryForm()


#Home page details
Title = Frame(Home, bd=1, relief=SOLID)
Title.pack(pady=10)
lbl_display = Label(Title, text="Store Management System", font=('arial', 20))
lbl_display.pack()
menubar = Menu(Home)
filemenu1 = Menu(menubar, tearoff=0)
filemenu2 = Menu(menubar, tearoff=0)
filemenu3 = Menu(menubar, tearoff=0)
filemenu4 = Menu(menubar, tearoff=0)
filemenu5 = Menu(menubar, tearoff=0)
filemenu6 = Menu(menubar, tearoff=0)
filemenu1.add_command(label="Issue", command=ShowIssueItem)
filemenu1.add_command(label="Return", command=ShowReturnItem)
filemenu1.add_command(label="Log", command=ShowLogView)
filemenu2.add_command(label="New user", command=ShowUserNew)
filemenu2.add_command(label="Users", command=ShowUserView)
filemenu3.add_command(label="New item", command=ShowItemNew)
filemenu3.add_command(label="Item", command=ShowInventoryView)
filemenu4.add_command(label="Print item details", command=PrintItemDetails)
filemenu4.add_command(label="Print user details", command=PrintUserDetails)
menubar.add_cascade(label="Log", menu=filemenu1)
menubar.add_cascade(label="Users", menu=filemenu2)
menubar.add_cascade(label="Items", menu=filemenu3)
menubar.add_cascade(label="Print", menu=filemenu4)
Home.config(menu=menubar)
Home.config(bg="#6666ff")


#========================================INITIALIZATION===================================
if __name__ == '__main__':
    Home.mainloop()