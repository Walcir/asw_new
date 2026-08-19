# -*- coding: utf-8 -*-
#import xlrd
#import urllib
#import time

import datetime
from re import X
#import matplotlib.pyplot as plt
from matplotlib import pyplot as plt
#try:
#    from Tkinter import* # Python 2.X
#except ImportError:
#from tkinter import * # Python 3+
#from tkinter import * # Python 3+
from tkinter import Tk,Frame,RAISED,LEFT,X,TRUE,SUNKEN,BOTTOM,Label,Entry,INSERT,RIGHT,Y
from tkinter import StringVar,TOP,Button,FLAT,IntVar,Radiobutton

import config as cfg 
from tkinter.ttk import Treeview
import tools as tls
import databases as db

#from reportlab.pdfgen import canvas
#from reportlab.pdfgen.canvas import Canvas
import os
import time
from fpdf import FPDF

#globals variables and object
#show local app
localapp=os.getcwd()
os.makedirs(os.path.join(localapp, "Docs"), exist_ok=True)

global con_msgs 
con_msgs=''
global cont
cont=0
pathapp=os.path.dirname(__file__)# local path app
global listdatacon
listx=[]
listy=[]  
lXtick=[]
global Showqtd 

#Create PDF
def createFpdf():       
  dtnow = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
  listHeader =['idmsg','idcampanhamsg','dtmsg','nomecontato','nomefone','msg','idimgmsg','iddocmsg']
  pdf=FPDF()
  pdf.add_page()
  pdf.set_font('Arial','B',9)  
  pdf.write(10,dtnow+'- Asw - Sistema / Relatorio de Menssages enviadas - Total de '+str(len(con_msgs))+' registros.')
  pdf.line(x1 = 10, y1 = 10, x2 = 185, y2 = 10)#draw line 30,813,550,813
  pdf.line(x1 = 10, y1 = 20, x2 = 185, y2 = 20)#draw line 30,813,550,813
  pdf.ln(8)
  #pdf.image("pyfpdf/tutorial/logo.png", 50, 50)
  #color and retang
  """"
  pdf.set_fill_color(128, 166, 197)
  pdf.set_draw_color(41, 53, 50)
  pdf.rect(80, 115, 50, 10, 'DF')

  pdf.set_text_color(183, 208, 232)
  pdf.ln(50)
  pdf.cell(70)
  pdf.cell(70, 0, 'We have a new line.', 0, 0, 'C')
  """
 
  pdf.set_draw_color(0, 0, 0)#pdf.set_draw_color(255, 255, 255)
  pdf.rect(0, 0, pdf.w, pdf.h, "D")
  pdf.set_line_width(0.2)
  pdf.rect(0.5, 0.5, pdf.w - 0.1, pdf.h - 0.1, "D")
  pdf.set_draw_color(0, 0, 0)
  pdf.write(10,'|codigo | Id camp|data e hora msg|nome de contato|numero fone|parte da mensagem texto|id imagem|id docum.')
  pdf.line(x1 = 10, y1 = 25, x2 = 185, y2 = 25)#draw line 30,813,550,813
  pdf.ln(4)
  if(len(con_msgs)>0):     
    # Set desired "resolution" of printed grid
    rows_per_page = len(con_msgs)-1#-5
    cols_per_page = 8#10
    # Calculate dimensions of print-able area
    print_h = pdf.h - pdf.t_margin - pdf.b_margin
    print_w = pdf.w - pdf.l_margin - pdf.r_margin

    # Actual size of grid cells on the page is available space divided by desired resolution, in each dimension
    c_h = print_h / rows_per_page +1.0
    c_w = print_w / cols_per_page
    #print("c_h = ",str(c_h))
    pdf.set_font('Arial','',8)
    pdf.ln(4)    
    for ln in con_msgs:#for in
      
      #if(len(str(ln))>10):
        #print('ln>10',ln)    
        #pdf.write(10,str(ln)[20])   
      #else:   
        #pdf.write(10,str(ln))   
      #print('y->',y)     

      for x in range(len(ln)):#for in Rowspdf.write(10,str(y))
        #print('x->',x,'=',str(ln[x]))
        if(x==0):#codigo
          cod = str(ln[x]) 
          while(len(cod) <6): cod = "0"+cod           
          #?pdf.write(10,cod+"| ")#pdf.write(10,str(ln[x]).rjust(14))
          pdf.cell(14, c_h,cod, border=0, ln=0, align="L")  
        elif(x==1):#idcamp
          idcamp = str(ln[x]) 
          while(len(idcamp) < 6): idcamp = "0"+idcamp 
          #?pdf.write(10,idcamp+"| ")#pdf.write(10,str(ln[x]).rjust(14))
          pdf.cell(14, c_h,idcamp, border=0, ln=0, align="C")
        elif(x==2):#data msg
          dtmsg = str(ln[x])
          while(len(dtmsg) < 17): dtmsg = " "+dtmsg
          #?pdf.write(10,dtmsg+"| ")#pdf.write(10,str(ln[x]).rjust(18))
          pdf.cell(25, c_h,dtmsg, border=0.1, ln=0, align="C") 
        elif(x==3):#name contact
          namectc = str(ln[x])
          while (len(namectc) < 20): namectc= namectc+" "
          #namectc = namectc[0:20]       
          #?pdf.write(10,namectc+"| ")#pdf.write(10,str(ln[x]).ljust(28))
          pdf.cell(24, c_h,namectc, border=0.1, ln=0, align="C")
        elif(x==4):#number phone
          Nphone = str(ln[x])
          while(len(Nphone) < 13): Nphone= " "+Nphone
          #?pdf.write(10,Nphone+"| ")#pdf.write(10,str(ln[x]).rjust(14))
          pdf.cell(25, c_h,Nphone, border=0.1, ln=0, align="C")
        elif(x==5):#partial msg 
          prtmsg = str(ln[x])
          #if(prtmsg==""): 
          # prtmsg="*"            
          #while len(prtmsg)<30: prtmsg = prtmsg+"_"  #pdf.write(10,' '.ljust(68))            
          #else:
          while len(prtmsg)<25: prtmsg = prtmsg+" "
          prtmsg = prtmsg[0:25]  
            #pdf.write(10,str(ln[x])[0:35].ljust(44))
          #?print('x5->',x,'=',prtmsg+"|")#str(ln[x])[0:44])
          #?pdf.write(10,prtmsg+"| ")
          pdf.cell(40, c_h,prtmsg, border=0.1, ln=0, align="C") 
        elif(x==6):#id img
          idimg= str(ln[x])
          while len(idimg)<6: idimg = "0"+idimg
          #?pdf.write(10,idimg+"| ")#pdf.write(10,str(ln[x]).ljust(18))#pdf.write(10,'%04d' % (ln[x]))        
          pdf.cell(18, c_h,idimg, border=0.1, ln=0, align="L") 
        else:# else 7 id doc
          iddoc = str(ln[x])
          while len(iddoc)<6: iddoc= "0"+iddoc
          #?pdf.write(10,iddoc+"|")#pdf.write(10,str(ln[x]).rjust(4))#pdf.write(10,'%04d' % (ln[x]))
          pdf.cell(18, c_h,iddoc, border=0.1, ln=0, align="L")
          #print('x->',x,y)            
          pdf.ln(3)
    pdf.ln(2)
    
    pdf.write(10,'Page ' + str(pdf.page_no())+'-Total de '+str(len(con_msgs))+' registros!')
      
    if os.path.exists("asw_rpt_msg"+time.strftime('%d%m%Y%H-%M', time.localtime())+".pdf"):
      os.remove("asw_rpt_msg"+time.strftime('%d%m%Y%H-%M')+".pdf")
      
    #pdf.output("asw_rpt_msg"+dtnow.strftime('%d%m%Y%H-%M')+".pdf", 'F')
    pdf.output("asw_rpt_msg"+time.strftime('%Y%m%d%H%M%S', time.localtime())+".pdf", 'F')
    
    tls.showmessage('Report count is ','Impressos '+str(len(con_msgs))+' registros em: '+
                  localapp+"/"+"asw_rpt_msg"+time.strftime('%Y%m%d%H%M%S', time.localtime())+".pdf"+'!')    
    return localapp+"/"+"asw_rpt_msg"+time.strftime('%Y%m%d%H%M%S', time.localtime())+".pdf"      
  else:
    tls.showmessage('Report count result: ','Não existe registros a serem impressos!') 
    return None  
  

def grp_line(listx,listy,titlex,titley,title):
  plt.plot(listx,listy,'-',color='#008000',lw=5)        
  plt.ylabel(titley)
  plt.xlabel(titlex)#plt.xlabel(labelx)
  plt.title(title,fontdict={'family':'monospace','color':'red','weight':'bold','size':16},loc='center')
  #plt.xticks(lXtick,1.0)
  #plt.yticks(listdata)
  #plt.full_screen_toggle()
  plt.legend()
  plt.show()

def grp_multline():
  x=['Jan','Fev','Mar','Abri','Mai','jun']#np.arange(8)
  y1=[15,85,46,97,28,39]#*x+5
  y2=[25,65,49,82,35,15]#3*x+5
  y3=[19,27,90,76,25,37]#2*x+5
  y4=[5,35,45,97,30,20]#x+5
  y5=[25,45,35,87,70,30]#x+5
  y6=[35,25,45,77,60,92]#x+5

  colors=['orange', 'purple', 'green','red','gray','yellow']

  plt.gca().set_prop_cycle(color=colors)
  plt.plot(x,y1,label="joao")#plt.plot(x,y1,label="4x+5")
  plt.plot(x,y2,label="Maria")#plt.plot(x,y2,label="3x+5")
  plt.plot(x,y3,label="Pedro")#plt.plot(x,y3,label="2x+5")
  plt.plot(x,y4,label="Madalena")#plt.plot(x,y4,label="x+5")
  plt.plot(x,y5,label="Lucas")
  plt.plot(x,y6,label="Marta")

  plt.title("Plot Multiple lines in Matplotlib",fontsize=15)
  plt.xlabel("semestre",fontsize=13)#plt.xlabel("X",fontsize=13)
  plt.ylabel("Valores",fontsize=13)#plt.ylabel("Y",fontsize=13)
  plt.legend()
  plt.show()
  
def grp_dot(x,y,labelx,labely,title):
  #plt.plot(x,y, label='Pontos percentual')
  plt.scatter(x,y,label='pontos progresso')
  plt.ylabel(labely)
  plt.xlabel(labelx)
  plt.title(title)
  plt.xticks(x)
  plt.yticks(y)
  plt.legend()
  plt.show()
    
def grp_bar(x,y,labelx,labely,title,titlebar):
  plt.bar(x,y,label=titlebar)
  plt.ylabel(labely)
  plt.xlabel(labelx)
  plt.title(title)
  plt.xticks(x)
  plt.yticks(y)
  plt.legend() 
  plt.get_current_fig_manager().full_screen_toggle()#mazimize
  plt.show()
  
 ########################create window show message#################
def showreport_msg():    
    Frmshowmsg_rp = Tk()##create object window
    Frmshowmsg_rp['bg']='#008000'#green
    #Frmshowmsg_rp.wm_iconbitmap("icons/Asw.ico")
    op='Visualizar'
    #width, heigth, incWidth,incheigth    
    Frmshowmsg_rp.geometry("850x410+250+350")
    cfg.center(Frmshowmsg_rp)  
    #?Frmshowmsg_rp.state("zoomed")#maximized
    #Contanier text
    contentcamps = Frame(Frmshowmsg_rp, bd=1, relief=RAISED)   
    contentcamps['bg']='#000000'  #black   
    contentcamps.pack(side=LEFT, fill=X,expand=TRUE)    
    separador = Frame(contentcamps,height=2, bd=1, relief=SUNKEN)
    separador.pack(side=BOTTOM)
    
    Frmshowmsg_rp.title("Relatório de Mensagens")    
    label = Label(Frmshowmsg_rp, text='Mensagens->'+op)
    label['bg']='#90EE90'
    label.pack()       
    
    
    lbl_idini = Label(contentcamps,text="Id inicial",fg='#FFFAFA')
    lbl_idini['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_idini.pack(padx=20, pady=5)    
    
    global text_idini
    text_idini = Entry(contentcamps, width = 20,name="text_idini")
    text_idini.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_idini.pack()    
    #focus inicialized in 
    text_idini.focus()
    #text_name.bind("<Return>",focus())
        
    lbl_idfin = Label(contentcamps,text="id final",fg='#FFFAFA')
    lbl_idfin['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_idfin.pack(padx=20, pady=5)    
    
    global text_idfin
    text_idfin = Entry(contentcamps, width = 20,name="text_idfin")
    text_idfin.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_idfin.pack()    
    
    lbl_nameini = Label(contentcamps,text="Nome contato inicial",fg='#FFFAFA')
    lbl_nameini['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_nameini.pack(padx=20, pady=5)    
    
    global text_nameini
    text_nameini = Entry(contentcamps, width = 20,name="text_nameini")
    text_nameini.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_nameini.pack()    
    #text_name.bind("<Return>",focus())
    
    lbl_namefin = Label(contentcamps,text="Nome contato final",fg='#FFFAFA')
    lbl_namefin['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_namefin.pack(padx=20, pady=5)    
    
    global text_namefin
    text_namefin = Entry(contentcamps, width = 20,name="text_namefin")
    text_namefin.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_namefin.pack()    
    #focus inicialized in     
    
    lbl_foneini = Label(contentcamps,text="fone inicial(Ex: 5583988009900)",fg='#FFFAFA')
    lbl_foneini['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_foneini.pack(padx=20, pady=5)
    
    global text_foneini
    text_foneini = Entry(contentcamps,  width = 20,name='text_foneini')
    text_foneini.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_foneini.pack()
    #text_fone.bind("<Return>",focus())
    
    lbl_fonefin = Label(contentcamps,text="fone final(Ex: 5583988009900)",fg='#FFFAFA')
    lbl_fonefin['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_fonefin.pack(padx=20, pady=5)
    
    global text_fonefin
    text_fonefin = Entry(contentcamps,  width = 20,name='text_fonefin')
    text_fonefin.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_fonefin.pack()
    '''
    lbl_namecampini = Label(contentcamps,text="Nome campanha inicial",fg='#FFFAFA')
    lbl_namecampini['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_namecampini.pack(padx=20, pady=5)
    
    global text_namecampini
    text_namecampini = Entry(contentcamps,  width = 30)
    text_namecampini.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_namecampini.pack()
    
    lbl_namecampfin = Label(contentcamps,text="Nome campanha final",fg='#FFFAFA')
    lbl_namecampfin['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_namecampfin.pack(padx=20, pady=5)
    
    global text_namecampfin
    text_namecampfin = Entry(contentcamps,  width = 30)
    text_namecampfin.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_namecampfin.pack()
    '''    
    lbl_dateini = Label(contentcamps,text="data Inicial Ex:01/06/2020",fg='#FFFAFA')
    lbl_dateini['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_dateini.pack(padx=20, pady=5)
    
    global text_dateini
    #text_dateini = Calendar(contentcamps,selectmode ="day",year=2020,mont=5,day=22)
    text_dateini = Entry(contentcamps,  width = 10)
    text_dateini.insert(INSERT,'') #insere o valor da variavel do arquivo config
    text_dateini.pack()
    
    lbl_datefin = Label(contentcamps,text="data final Ex:01/06/2020",fg='#FFFAFA')
    lbl_datefin['bg']='#000000'  #black  #'#90EE90'  #LigthGreen   
    lbl_datefin.pack(padx=20, pady=5)
        
    global text_datefin
    text_datefin = Entry(contentcamps,  width = 10)
    asw_Now = datetime.date.today()
    strdate=asw_Now.strftime('%d/%m/%Y')
    text_datefin.insert(INSERT,strdate) #insere o valor da variavel do arquivo config
    text_datefin.pack()
    
    contentdata = Frame(Frmshowmsg_rp, bd=1, relief=RAISED)   
    contentdata['bg']='#229A00'  #green   
    contentdata.pack(side=RIGHT, fill=Y,expand=TRUE)      
    
    global T_idct 
    T_idct=StringVar()   
        
    #consulting in db the all contacts
    global con_contacts
    global tv
    tv = None
    #create table view     
    #tv = Treeview(Frmshowmsg_rp,columns=(1,2,3,4,5,6,7,8),show='headings')    
    tv = Treeview(contentdata,columns=("idmsg","idcampanhamsg","dtmsg","Nomecontato","Nfone","msg","idimgmsg","iddocmsg"),show='headings')
    #length of colums     
    tv.column('idmsg',minwidth=0,width=35)
    tv.column('idcampanhamsg',minwidth=0,width=40)
    tv.column('dtmsg',minwidth=0,width=100)
    tv.column('Nomecontato',minwidth=0,width=85)
    tv.column('Nfone',minwidth=0,width=90)
    tv.column('msg',minwidth=0,width=120)
    tv.column('idimgmsg',minwidth=0,width=50)
    tv.column('iddocmsg',minwidth=0,width=30)
    #label of colums
    tv.heading('idmsg',text='codigo')
    tv.heading('idcampanhamsg',text='id campanha')
    tv.heading('dtmsg',text='data envio')
    tv.heading('Nomecontato',text='nome contato')
    tv.heading('Nfone',text='fone')
    tv.heading('msg',text='mensagem')    
    tv.heading('idimgmsg',text='id imagem')
    tv.heading('iddocmsg',text='id doc')

    tv.pack()
    #defined count of camp label
    #title
    lbltotalmsg = Label(contentdata,text="total de mensagens: ",fg='#FFFAFA')
    lbltotalmsg['bg']='#000000'  #black
    lbltotalmsg['fg']='#FFFAFA'#white
    lbltotalmsg.pack(padx=5, pady=5)
    
    lblqtdmsg = Label(contentdata,text='0')
    lblqtdmsg['bg']='#000000' #back
    lblqtdmsg['fg']='#FFFAFA'#white
    lblqtdmsg.pack(padx=5,pady=5)
    
    lblqtdcampt = Label(contentdata,text="Quant. campanhas/contato: ",fg='#FFFAFA')
    lblqtdcampt['bg']='#000000'  #black
    lblqtdcampt.pack(padx=20, pady=5)
    #result quant of camp
    global qtdcamp
    global con_msgs  
    if con_msgs==None:
      con_msgs=0
    global Showqtd    
    Showqtd = StringVar()
    Showqtd.set('0')# get value count on rs

    #lblqtdcamp = Label(contentdata,fg='#FFFAFA',textvariable=Showqtd,text=str(Showqtd))
    lblqtdcamp = Label(contentdata,fg='#FFFAFA',text='0')
    lblqtdcamp['bg']='#000000'  #black
    lblqtdcamp.pack(padx=20, pady=5)
    
    #********* if click in grid**********************************************
    def selectItem(a): 
      lblqtdcamp.config(text='0')
      fonecont=''
      namecont=''
      curItem = tv.focus()        
      print("curItem = ",curItem)
      #get line clicking/ pega a linha clicada
      print(tv.item(curItem))
      listln=[]
      listln=tv.item(curItem)
      #run line collums/ percorre as colunas da linha      
      for y in listln:
        print('-col->'+str(y)+'=rs->',str(listln[y]))   
        if str(y)=='values':#get values list/ pega a lista de valores
          listcol=[]
          listcol= listln[y]
          i=0
          for x in listcol:
            if i == 3:
              namecont = str(x)
            elif i == 4:
              fonecont = str(x)  
            print(str(i),'-values col->',x)
            i=i+1
      for y in curItem:
        if y!="0" and y!="I":
          #print("Cod value ",y) 
          cfg.clickId = y
          print("Code clicked ",str(cfg.clickId) )    
          getidcont ='(Select idcontatos from contatos where fonecontato= "'+fonecont+'" or nomecontato="'+namecont+'")'
          rscamp=db.consulttablesql(db.csqllite,' count(iditcamp)as qtd ','itenscamp',' where iditcontcamp = '+str(getidcont)+' ',' ;')
          qtd=0
          if rscamp !=[] and rscamp!=None:
            for i in rscamp:
              qtd = i[0]
            print('quant.camp is->',str(qtd) ) 
            global Showqtd
            Showqtd=str(qtd)
            print("var Shouqtd is->",Showqtd)
            lblqtdcamp.config(text=str(Showqtd))              
              
    #************************************************************************
    tv.bind('<ButtonRelease-1>', selectItem)
    #Contanier butons        
    pnlbutons = Frame(contentdata,height=150, bd=1, relief=RAISED)   
    pnlbutons['bg']='#90EE90'  #LigthGreen   
    pnlbutons.pack(side=BOTTOM, fill=X,expand=TRUE)
    #*******clink in button edit contact ********************
    def click_editContact():       
      if cfg.clickId >0:
        print("Code chose ",str(cfg.clickId))
        #menu_editContact()        
      else:          
        #print('NO id chose = '+str(cfg.clickId ))
        tls.showmessage('Informação','è preciso escolher um contanto na lista!')
              
    #****************************************************************   

    #**********************************************************************************************************  
    btn_voltar = Button(pnlbutons, text='Voltar/sair',image ='',bg='#FF0000', fg="white",compound = LEFT,command=Frmshowmsg_rp.destroy)
    btn_voltar.pack(side=LEFT, padx=20, pady=2)    
    #btn_voltar.pack(side=LEFT) 
    ##idmsg,msg,idimgmsg,iddocmsg,idcampanhamsg,dtmsg,Nfone,Nomecontato
    def listgrid():#linting grind after consult filter    
      lblqtdmsg.configure(text='0')      
      global where
      where =' where idmsg is not null '    
      idmsgini      ="'"+text_idini.get()+"'"      
      idmsgfin      ="'"+text_idfin.get()+"'"
      nomecontatoini     ="'"+text_nameini.get()+"'"
      nomecontatofin     ="'"+text_namefin.get()+"'"
      fonecontatoini     ="'"+text_foneini.get()+"'"
      fonecontatofin     ="'"+text_fonefin.get()+"'"
      '''
      nomecampini="'"+text_namecampini.get()+"'"
      nomecampfin="'"+text_namecampfin.get()+"'"
      '''
      datacadini=text_dateini.get()
      datacadini=datacadini[6:10]+datacadini[3:5]+datacadini[0:2]
      
      datacadfin=text_datefin.get()
      datacadfin=datacadfin[6:10]+datacadfin[3:5]+datacadfin[0:2]
      
      if(idmsgini!="''"): 
        print('idmsgini=',idmsgini)
        where=where+' and  idmsg >='+idmsgini      
      if(idmsgfin!="''"): 
        where=where+' and  idmsg <='+idmsgfin
      if(nomecontatoini!="''"): 
        where=where+' and  nomecontato >='+nomecontatoini
      if(nomecontatofin!="''"): 
        where=where+' and  nomecontato <='+nomecontatofin
      if(fonecontatoini!="''"): 
        where=where+' and  Nfone >='+fonecontatoini
      if(fonecontatofin!="''"): 
        where=where+' and  Nfone <='+fonecontatofin  
      '''
      if(nomecampini!="''"): 
        where=where+' and idcampanhamsg >=(Select idcampanhas from campanhas where nomecampanhas like "%'+nomecampini+'%") '
      if(nomecampfin!="''"): 
        where=where+' and idcampanhamsg <=(Select idcampanhas from campanhas where nomecampanhas like "%'+nomecampini+'%") '
      '''  
      
      if(datacadini!=''): 
        where=where+' and  dt >='+"'"+datacadini+"'"#where=where+' and  dtmsg >='+"'"+datacadini+"'"
      if(datacadfin!=''): 
        where=where+' and  dt <='+"'"+datacadfin+"'"#where=where+' and  dtmsg <='+"'"+datacadfin+"'"
      #if(ativocontato!="''"): 
        #where=where+' and ativocontato in('+ativocontato+')'
      #if(eclientecontato!="''"): 
        #where=where+' and eclientecontato in('+eclientecontato+')'          
      tv.delete(*tv.get_children())# delete all contents children
      global con_msgs   
      con_msgs=0      
      con_msgs=db.consulttablesql(db.csqllite,' idmsg,idcampanhamsg,dtmsg,Nomecontato,Nfone,msg,idimgmsg,iddocmsg,substr(dtmsg,7,4)||substr(dtmsg,4,2)||substr(dtmsg,1,2) as dt',' msg ',where,' order by 3 ;')
      if(len(con_msgs)>0):
        global cont
        cont = 0#id = 0
        for y in con_msgs:
          tv.insert('','end',values=y)
          cont=cont+1
        global Showqtd
        print('valor con_msgs->',str(len(con_msgs)))
        lblqtdmsg.configure(text=str(len(con_msgs)))
        #listmsg.clear;
        global listx
        global listy
        listx.clear;
        listy.clear;
        '''
        select count(*)as qtd ,Nomecontato,dtmsg
        from msg where nomecontato is not null
        and dtmsg between '01/01/2024' and '05/04/2024'
        group by Nomecontato
        order by dtmsg
        '''    
        rs_count=None
        where =' where nomecontato is not null'
        if(text_dateini.get()!=''): 
          where=where+' and  dtmsg >='+"'"+text_dateini.get()+"'"#where=where+' and  dtmsg >='+"'"+datacadini+"'"
          
        if(text_datefin.get()!=''): 
          where=where+' and  dtmsg <='+"'"+text_datefin.get()+"'"#where=where+' and  dtmsg <='+"'"+datacadfin+"'"
          
        where = where + 'group by nomecontato'  
        sql=' select count(*)as qtd, nomecontato, dtmsg from msg '+where+' order by dtmsg '
        print(sql)
        rs_count= db.consulttablesql(db.csqllite,' count(*)as qtd ,Nomecontato,dtmsg',' msg ',where,'  order by dtmsg;')
        for y in rs_count:
          for x in range(len(y)): 
              if (y[0]==None or y[0]==''):#name
                listy.append('0')
              else:  
                listy.append(y[0])#qtd #name
              #listy.append(x)
              #listx.append(str(y[2])[0:9])#dtmsg
              listx.append(str(y[2])[0:10])
      else:
        tls.showmessage('resultado de busca','menssagem não encontrada!')
         
           
    def printgraphic():
      #global listx
      #global listy
      #listx.clear;      
      #listy.clear;    
      
      if (con_msgs!=0 ):#if(len(con_msgs)>0):  
        global cont      
        cont = 0#id = 0        
        #listmsg.clear;         
        for y in con_msgs: # run coluns         
          for x in range(len(y)): # run lines
        #    if( y[3]==None or y[3]==''):#name
        #      listy.append('sem nome')
        #    else:  
        #      listy.append(y[3])#name
        #    #listxdtcon.append(x)
        #    listx.append(str(y[2])[0:9])#dtmsg
        #    #lXtick.append(str(y[0]))#codigo
            cont=cont+1
        #  print('len x',str(len(listx)))
        #  print('len y',str(len(listy)))
        #?grp_line(listx,listy,'progresso','contatos','Análise grafica messagens/contatos')
        grp_bar(listx,listy,'progresso/período','contatos','Análise de mensagens enviadas (fechar tela: alt+f4)','´progresão')
        
        
    btn_filter= Button(pnlbutons,text='filtrar', image='' , bg='#F57F17', fg="white",
    compound = BOTTOM, relief=FLAT, command=listgrid)
    btn_filter.pack(side=LEFT, padx=20, pady=2)
    
    #global listdatacon
    #Crud -> 0-Default, 1-incluir, 2-alterar, 3-excluir, 4-consulta
    btn_graphic = Button(pnlbutons, text='+Relatorio grafico',image ='',bg='#008000', fg="white",compound = LEFT,command=printgraphic)
    #btn_ins.pack(side=LEFT, padx=40, pady=2) 
    btn_graphic.pack(side=LEFT, padx=20, pady=2) 
    
    btn_print= Button(pnlbutons,text='?imprimir/enviar', image='' , bg='#0000FF', fg="white", compound = BOTTOM, relief=FLAT, command=createFpdf)     
    btn_print.pack(side=LEFT, padx=20, pady=2)     
    
    Frmshowmsg_rp.mainloop()

#********************************************************************** 
#grp_default() #tests 
#grp_dot()
 #title='Niveis de crescimento'#'ponto grafico'
 #f=['18-25','26,35','36-45','55+']
 #r1=[1805.45,2458.12,4120.89,3486.22]
 #r2=[1705.25,2158.10,3110.89,2486.12]
 #r=[r1,r2]
 #labelx='Eixo x - progresso faixa etaria'
 #labely='Eixo y - media salarial'
#grp_bar(f,r,labelx,labely,title)
#grp_dot(f,r,labelx,labely,title)
#grp_line(f,r,labelx,labely,title)
#grp_multline()

#Teste listar dados
  #yt=[[15,85,46,97,28,39],[25,65,49,82,35,15],[19,27,90,76,25,37],
    #[5,35,45,97,30,20],[25,45,35,87,70,30],[35,25,45,77,60,92]]
#print(len(yt))  
  #i=1
  #z=1
  #y=1
  #for i in range(len(yt)):
    #print(y) #show index of list ready #mostra o indice da lista lida  
    #y=y+1 #increment index # incrimenta indece da lista
    #print(yt[i])#show complety list # mostra a lista complete
    #for z in (yt[i]):#go thouugth the list # percorre a lista
    #print(z)#show each item in the list # mostra cada item da lista
   
