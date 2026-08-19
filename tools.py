# -*- coding: utf-8 -*-
#try:
#    from Tkinter import* # Python 2.X
#except ImportError:
#from tkinter import * # Python 3+
#from tkinter import * # Python 3+
#from tkinter import Tk,Frame,RAISED,LEFT,X,TRUE,SUNKEN,BOTTOM,Label,Entry,INSERT,RIGHT,Y
#from tkinter import StringVar,TOP,Button,FLAT,IntVar,Radiobutton
import os
#?from matplotlib.pyplot import title
from tkcalendar import Calendar
#?from tkcalendar import *
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders 
import config as cfg 
import unicodedata
import re

#try: 
#    import tkMessageBox as msgbx # Python 2.X
#except ImportError: # Python 3+
#    from tkinter import messagebox as msgbx#tkinter.tkMessageBox 
from tkinter import messagebox as msgbx
import databases as db

Eventos =''
procancel=False
inprocess=False

#exibe uma caixa de Messagem
def showmessage(Title,message):    
   #tkMessageBox.showinfo(Title, message)
   msgbx.showinfo(Title, message)  
   
   
def getlogdb():
  #Select * from log where descrilog is not null order by 1    
  rslog=db.consulttablesql(db.csqllite,'*','log',' where descrilog is not null',' order by 1')
  return rslog

#delete content file log 
def  deltxtarq(pathlog):
    if(os.path.isfile(pathlog)): #se arquivo existe
        open(pathlog, 'w').close() # 'w' apaga conteudo

#writing content file log
def arqlog(pathlog,conteudo):
   try:   
      #print('conteudo',conteudo) 
      #global Eventos
      #Eventos+=conteudo
      mode= 'a' if os.path.exists(pathlog)else 'w'
      with open(pathlog,mode,encoding="utf8")as f:
        #f.write(conteudo+'\n')#f.write('Hello, world!\n')
        #f.writelines(Eventos)
        f.close()   
       
       
   except ImportError as ie: #Return execption
       print('mportError arqlog ',ie)    
       #global Eventos
       #Eventos+=conteudo

#globals variables
#global root
#root= Tk()  #create Frame
seldate =''
def center(win):
    # :param win: the main window or Toplevel window to center

    # Apparently a common hack to get the window size. Temporarily hide the
    # window to avoid update_idletasks() drawing the window in the wrong
    # position.
    win.update_idletasks()  # Update "requested size" from geometry manager

    # define window dimensions width and height
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width

    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width

    # Get the window position from the top dynamically as well as position from left or right as follows
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2

    # this is the line that will center your window
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    # This seems to draw the window frame immediately, so only call deiconify()
    # after setting correct window position
    win.deiconify()
#***************************************************************************
def get_key(key):
  import keyboard
  if keyboard.is_pressed(key):
    key_pressed = keyboard.read_key()    
    print(f"get key: {key} pressed key: {key_pressed}")
    return True
  else:
    key_pressed = keyboard.read_key() 
    print(f"get key: {key} pressed key: {key_pressed}")
    return False
#****************************************************************************
"""
A remoção de acentos foi baseada em uma resposta no Stack Overflow.
http://stackoverflow.com/a/517974/3464573
"""
  
def removerAcentosECaracteresEspeciais(palavra):

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    nfkd = unicodedata.normalize('NFKD', palavra)
    palavraSemAcento = "".join([c for c in nfkd if not unicodedata.combining(c)])

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    return re.sub('[^a-zA-Z0-9]', '', palavraSemAcento)    

def createcalendar():
  #global root  
  root=Tk()
  root.title("Calendário-Escolha a data!")
  root.geometry("300x250")
  root.wm_iconbitmap("icons/ASW.ico")
  root['bg']='#008000'#green 
  center(root)
  #add calendar
  dtNow = datetime.now()
  #dt = str(datetime.strptime(asw_Now,'%y%m%d'))
  #print(dt)
  cal=Calendar(root,selectmode='day',year=dtNow.year,month=dtNow.month,day=dtNow.day)
  cal.pack(padx=20)
  
  def grad_date():
        #date.config(text = "Selected Date is: " + cal.get_date())
    # return date on string
    global seldate #atualization variable of value chose date
    seldate = str(cal.get_date())
    print("T chose date is ",seldate)    
    if(root!=None):
      root.destroy()

  Button(root, text = "OK DATA",
  command = grad_date).pack(pady = 20)
  
 
  # Add Button and Label
  #date = Label(root, text = "")
  #date.pack(pady = 20)

  # Execute Tkinter
  root.mainloop()
#testing
#createcalendar()
#print( "Selected Date is: ",seldate)#
#print("dia",seldate[3:5])
#print("Mes",seldate[0:2])
#print('ano',seldate[6:8])
def listEmails():
  strlistemail=[cfg.readcfg('config.ini','repository','emailrel')]                            
  listemailsend = []
  if not listemailsend:# list empty
    print('List emails empty!')
  else:  
    for y in strlistemail:
    #print('i',y)
      achou = False
      email=''
      for i in y:
        if(i!=';'and i!=','):
          email=email+i
          achou = False
          #print("emailf",email)
        else:
          achou=True
          #print("emailt",email)
          listemailsend.append(email)
          email=''    
  return listemailsend

def send_email(sender_email_id,sender_email_id_password,listemailsender,f_Attachment,bodytxt):
  try:
    dtnow = datetime.today()
    msg = MIMEMultipart() 
    msg['From'] = sender_email_id
    msg['Subject'] = "Relatorio do sistema ASW_WahatsApp "+dtnow.strftime('%d/%m/%Y %H:%M')
    body = "Relatorio do sistema ASW-WhatsApp"+dtnow.strftime('%d/%m/%Y %H:%M')
    msg.attach(MIMEText(body, 'plain'))
    filename = f_Attachment
    if filename != '' and filename!=None:      
      attachment = open(f_Attachment, "rb")
      p = MIMEBase('application', 'octet-stream')
      p.set_payload((attachment).read())
      encoders.encode_base64(p) 
      p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
      msg.attach(p)  
    if listemailsender!=[] and listemailsender!=None:
      for dest in listemailsender:
        msg['To'] = dest  
        s = smtplib.SMTP('smtp-mail.outlook.com', 587)
        s.starttls() 
        s.login(sender_email_id,sender_email_id_password)
        #message = "voce recebeu um teste de envio da aplicacao ASW"
        text=msg.as_string()
        if bodytxt!=None:
          text = text+bodytxt
        s.sendmail(sender_email_id, dest, text)
        s.quit() 
        print("email enviado com sucesso!")
  except Exception as e:
    print('Excecao ao envia Email',e)
#**********************************************************************
#create class thread auto
class auto():
  istart=0
  getkey=""
  chk_key = False
  def __init__(self,num):
    #?Thread.__init__(self)
    self.num =num
  #create method run auto get start
  def run(self):
    import sys    
    if auto.istart>0:                  
      print('...auto process start')     
    else:
      print('auto process stop!')
  #starting thread
  def start_auto(self):
    #https://medium.com/@habbema/threads-em-python-9a3a7b3c776d
    import threading
    # Criação de uma instância de Thread
    global thread
    thread = threading.Thread(target=auto.run(self))
    # Inicia a thread
    print("iniciando a thread ")
    from scripts.main import rotulo
    rotulo.config(text="inicianco a thread")
    thread.start()    
    auto.istart=1
  #************************************************************  
  def stop_auto(self):
    # Espera pela thread terminar
    global thread 
    print("Thread principal finalizada")
    from scripts.main import rotulo
    rotulo.config(text="Parada a Thread!")
    thread.join()
    auto.istart=0
#*************************************
#**************************************
#class teleprompter to run 
import tkinter as tk
#from tkinter.scrolledtext import ScrolledTextclass
class Teleprompter(tk.Tk):  
  def __init__(self,text_area):
    super().__init__()
    # Create a ScrolledText widget
    #TextArea = ScrolledText(background="black",foreground='white')
   # Variables to control scrolling
    self.is_scrolling = False
    self.scroll_speed = 100  # Adjust the delay to control the scroll speed  
    self.text_area = text_area
    # Withdraw the window (make it invisible)
    self.withdraw()     
  def add_text(self,text):
    self.text_area.insert(tk.END,text)
    self.text_area.see(tk.END)
     
  def start_scrolling(self):
      if not self.is_scrolling:
          self.is_scrolling = True
          self.scroll_text()
          
  def pause_scrolling(self):
      self.is_scrolling = False
      
  def restart_scrolling(self):
      self.pause_scrolling()
      self.text_area.yview_moveto(0)  # Move to the first line
      if not self.is_scrolling:
          self.is_scrolling = True
          self.scroll_text()
      
  def scroll_text(self):
      if self.is_scrolling:
        if self.text_area!=None:
          self.text_area.configure(state=tk.NORMAL)# Temporarily make it editable for scrolling
          self.text_area.yview_scroll(1, "unit")
        #?  self.text_area.configure(state=tk.DISABLED)  # Make the text read-only again
          # Schedule the next scroll
          self.after(self.scroll_speed, self.scroll_text)# Temporarily make it editable for scrolling
          
          
  def scrool_one_line_dow(self):
    self.text_area.configure(state=tk.NORMAL)#Temporarily make it editable for scrolling
    self.text_area.yview_scrooll(1,"unit")
    #?self.text_area.configure(state=tk.DISABLED)#make the text read-only again
#***************************************
# ********update log***************** 
def update_log(Eventos):
  cfg.is_scrolling =True#Ativa a rolagem da tela principal de log
  import time
  dtlocal = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime()) 
  localapp=os.getcwd()

  localapp=localapp.replace('\\','/')
  cfg.arqlog(localapp+"/ASW.log",Eventos)
  db.inserttablesql(db.csqllite,'log','descrilog,dttimelog','"'+str(Eventos)+'","'+str(dtlocal)+'"','')#insert log db    
  print(Eventos) 
  