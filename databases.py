# -*- coding: utf-8 -*-
import csv
#from msilib import schema
import sqlite3
#from statistics import mode
#from fdb import Cursor # para o sqllite local
#import MySQLdb # para o MySQL
import os

#from types import NoneType
from tkinter import messagebox as msgbx#tkinter.tkMessageBox
#conexao  com os banco
#sqllite local
#mostra o local da app
from datetime import datetime
#globals
localapp=os.getcwd()

localapp=localapp.replace('\\','/')
print('localApp: ',localapp) 
con =None
sqlitedb=localapp+'/sqlite.db'# campinho do banco de dados
print (sqlitedb)
#method decod charcset database
atual_encoding = 'UTF-8'
def decode(s):
  s.decode(atual_encoding)
  return s

if os.path.isfile(sqlitedb)==False:# is not exists db file
  con = sqlite3.connect(sqlitedb)
  con.text_factory=decode
  if con is None:
    print("conection erro !")
else:#force create file db
  con = sqlite3.connect(sqlitedb)      
  con.text_factory = lambda b: b.decode(errors = 'ignore')
  #obtendo uma transação(cusor)
csqllite = con.cursor()
#Result Set array db camp
con_camp =[]
#Result Set array db contact of camp
con_contactCamp=[]
#exibe uma caixa de Messagem
def showmessage(Title,message):    
   #tkMessageBox.showinfo(Title, message)
   msgbx.showinfo(Title, message)

def iftableexists(cusor,nametable):
    listOfTables = cusor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='"+nametable+"'; ").fetchall()
    # commit changes
    #cusor.commit()
    
    if listOfTables == []:
       # print('Table not found!')
        return False
    else:
       # print('Table found!')
        return True  
    # terminate the connection
    #cusor.close()
def inserttablesql(cusor,tablename,listfields,valuesfields,where):
    #cursor.execute('INSERT INTO TABELA (CAMPO1, CAMPO2, CAMPO3) VALUES (?,?,?)', (valor1, valor2, valor3))
    sql="insert into "+tablename+" ("+listfields+") values("+valuesfields+")"+where
    print(sql)
    try:
        #?cusor.execute(sql)
        csqllite.execute(sql)
        # commit changes
        csqllite.connection.commit()#?cusor.connection.commit()        
        #cusor.close()
    except Exception as e:        
        print("Error occurred: ", e)
        print("sql->",sql)
        showmessage("Exception->inserttablesql=",".join(e.args)+"+sql)
        
def updatetablesql(cusor,tablename,setlistfields,condition):
    sql="Update "+tablename+" set "+setlistfields+" where "+condition+" ;" 
    try:
      if cusor :
        cusor.execute("Update "+tablename+" set "+setlistfields+" where "+condition+" ;")
        # commit changes
        cusor.connection.commit()#cusor.connection.commit() 
      else:  
        csqllite.execute("Update "+tablename+" set "+setlistfields+" where "+condition+" ;")
        # commit changes
        csqllite.connection.commit()#cusor.connection.commit() 
        
      sqlite3.Cursor.fetchall
      # terminate the connection
      #cusor.close()
    except Exception as e:
       print("Error occurred: ", e)
       print('Tipo: ',type(e))
       print('Arqgumentos: ',e.args)
       Eventos='Excection in databses.py->updatetablesql->'"".join(e.args)
       print(Eventos)
def deletetablesql(cusor,tablename,listfields,where):
    #?cursor.execute('INSERT INTO TABELA (CAMPO1, CAMPO2, CAMPO3) VALUES (?,?,?)', (valor1, valor2, valor3))
    sql="delete "+listfields+" from "+tablename+"  "+where
    try:
        print("sql->",sql)
        csqllite.execute(sql)#?cusor.execute(sql)
        # commit changes
        #?cusor.connection.commit() 
        csqllite.connection.commit()
        sqlite3.Cursor.fetchall    
        # terminate the connection
        #cusor.close()
    except Exception as e:     
        print("Exc-> in database.py on deletetablesql:\n ")
        print("\nsql->",sql)
        print("Exc->->",u''.join(e.args))
#*********************************************************       
def consulttablesql(cusor,listfields,Fromtablename,where,order):
    try:
      global sql
      sql="Select "+listfields+" from "+Fromtablename+" "+where+" "+order  
      print(sql)
      #?showmessage('consulttablesql',sql)
      #resultsql=cusor.execute("Select "+listfields+" from "+Fromtablename+" "+where+" "+order) 
      resultsql=csqllite.execute("Select "+listfields+" from "+Fromtablename+" "+where+" "+order)   
      return resultsql.fetchall()   
    except Exception as e:    
        print("Error occurred: ", u''.join(e.args))
        print("sql->",sql)
#*******************************************************        
def addColumn(cursor,table,column,type,len):
    try:
        #?cursor.execute(' Alter table '+table+' add column '+column+' '+type+' '+len)
        csqllite.execute(' Alter table '+table+' add column '+column+' '+type+' '+len)
        print("Field "+column+" in table "+table+" add sucess!/campo adicionado com sucesso!")
        return True
    except sqlite3.OperationalError:
        print("Excec. Aviso: O Campo "+column+" 'Bloqueado' ja existe.")
        return False
def updateTypeCol(cursor,table,column_name,new_type,len):
    #cursor.execute(' Alter table '+table+' alter column '+column_name+' '+new_type+'('+len+').')
    csqllite.execute(' Alter table '+table+' alter column '+column_name+' '+new_type+'('+len+').')
    #ALTER TABLE Tabela ALTER COLUMN Coluna VARCHAR(100).
#count colums in table/conta a quantidade de colunas em uma tabela
def countcoltable(nametable):
  rsc=[]
  sql = 'PRAGMA table_info('+nametable+'); '
  rsc=csqllite.execute(sql)
  qtdcol = rsc.fetchall()
  print('qtd fields in table '+nametable+'-> ',len(qtdcol))
  return qtdcol
#cria a tabela contatos
if iftableexists(csqllite,'log')==False: 
  csqllite.execute("create table if not exists log(descrilog varchar(100),dttimelog text)")
  print("tabela log criada com suceso!")
else:
    print("tabela log ja existe!")    
#cria a tabela contatos
if iftableexists(csqllite,'contatos')==False: 
  csqllite.execute("create table if not exists contatos(idcontatos integer not null primary key autoincrement,nomecontato varchar(100),"+
  "fonecontato varchar(20),emailcontato varchar(70), nomegrupocontato varchar(50), ativocontato varchar(1), eclientecontato varchar(1),datacad text)")
  print("tabela contatos criada com suceso!")
else:
    print("tabela contatos ja existe!")
#exemplo sqlite
#INSERT INTO conta(datahora, descricao) values(datetime('now'),'Exemplo de texto');
#cursor.execute('CREATE TABLE fotos (codigo INTEGER NOT NULL, foto BLOB
#NOT NULL)')
#codigo = 123
#dados_binarios_da_foto = open('foto.jpg').read()
#cursor.execute('INSERT INTO digitais VALUES (?, ?)', (codigo,
#sqlite3.Binary(dados_binarios_da_foto)))

#cria campanhas publicitaria e market  
if iftableexists(csqllite,'campanhas')==False:     
  csqllite.execute("create table if not exists campanhas(idcampanhas integer not null primary key autoincrement, nomecampanhas varchar(100),"+
  "dthcadastrocampanhas text, msgcampanhas varchar(1000), imgcampanhas blob, doccampanhas blob, ativocampanhas varchar(1),"+
  " dthdispararcampanhas text, enviada varchar(1),saudatemp varchar (1),saudaNome varchar(1) )")
  print("tabela campanhas criada com suceso!")
#else:
    #print("tabela campanhas ja existe!")
#cria itens campanhas, contacts data   
if iftableexists(csqllite,'itenscamp')==False:
    csqllite.execute("create table if not exists itenscamp(iditcamp integer not null primary key autoincrement,"+
    "idcoditcamp integer not null,iditcontcamp integer not null,itnamecontcamp varchar(100),"+
    "itfonecontcamp varchar(13),status varchar(1) default('N') )")
    print("tabela itenscamp criada com sucesso!")
#confere os campos e atualiza a tabela itenscamp
if len(countcoltable('itenscamp'))== 5 :
  addColumn(csqllite,'itenscamp','status','varchar','(1) defaut("N")')
# cria a tabela fotos
if iftableexists(csqllite,'img')==False:
    csqllite.execute("create table if not exists img(idimg integer not null primary key autoincrement,nameimg varchar(100),"+
    "idcampanhaimg integer, dtimg text, pictureimg blob not null)")
    print("tabela img criada com sucesso!")
#else:
    #print("tabela img ja existe!")
# cria a tabela docs
if iftableexists(csqllite,'doc')==False:
    csqllite.execute("create table if not exists doc(iddoc integer not null primary key autoincrement,namedoc varchar(100),"+
    "idcampanhadoc integer, dtdoc text, picturedoc blob not null)")
    print("tabela doc criada com sucesso!")
else:
    print("tabela doc ja existe!")
    
if iftableexists(csqllite,'msg')==False:
    csqllite.execute("create table if not exists msg(idmsg integer not null primary key autoincrement,msg varchar(200),"+
    "idimgmsg integer,iddocmsg integer,idcampanhamsg integer,dtmsg text,Nfone varchar(100),Nomecontato varchar(15))")
    print("tabela msg criada com sucesso!")
else:
    print("tabela msg ja existe!")
    
if iftableexists(csqllite,'grp')==False:
    csqllite.execute("create table if not exists grp(idgrp integer not null primary key autoincrement,namegrp varchar(100),"+
    "dtgrp text)")
    print("tabela group criada com sucesso!") 
else:
  print('tabela grp já existe!')
  
 #cria itens camp  grupo em anexo
if iftableexists(csqllite,'icampgp')==False:
  csqllite.execute("create table if not exists icampgp(iditcampgp integer not null primary key autoincrement,"+
  "idcampgp integer not null,iditgrupogp integer not null,itnamegp varchar(100))")
  print("tabela (icampgp) de grupo na campanha criada com sucesso!")  
else:
  print('tabela item grupo na campanha criada com sucesso!')
#********tabela  campanha diversa************
if iftableexists(csqllite,'campdv')==False:
  csqllite.execute("create table if not exists campdv(idcampdv integer not null primary key autoincrement,"+
  "dtsendcampdv text,hrsendcampdv text,mincampdv text,descricampdv varchar(100),ativocampdv varchar(1))")
  print("tabela (campdv) campanha diversa criada com sucesso!")  
else:
  print('tabela campdv(campanha diversa) já existe!')
#*********************************************
#***********create table items camp dv********
if iftableexists(csqllite,'itcampdv')==False:
  csqllite.execute("create table if not exists itcampdv(iditcampdv integer ,"+
  "msgitcampdv varchar(500),idcontitcampdv integer, nomeitcampdv varchar(80),numitcampdv varchar(20),"+
  "imgitcampdv blob,docitcampdv blob, status varchar(1) default('N') )")
  print("tabela (itcampdv)  criada com sucesso!")  
else:
  print('tabela itcampdv já existe!')
#*********************************************
#confere os campos e atualiza a tabela itcampdv
if len(countcoltable('itcampdv'))==7:
  addColumn(csqllite,'itcampdv','status','varchar','(1) defaut("N")')
#cria a tabela config
if iftableexists(csqllite,'config')==False: 
  csqllite.execute("create table if not exists config(idcfg integer not null primary key autoincrement,nfantcfg varchar(100),"+
  "cpfcnjcfg varchar(20),emailcfg varchar(170), razscfg varchar(50), ativocfg varchar(1), whatapp varchar(20),datacad text,"+
  "filejsoncfg varchar(50),msg_allcfg varchar(1000),doc_all blob,img_allcfg blob, tpbrowsercfg varchar(1),timeqrcodecfg float,"+
  "pflogincfg varchar (200),px_bnsendcfg integer,pybtnsendcfg integer,pathexebrowsercfg varchar(200), id_procuctcfg integer, keylicensecfg integer,"+
  "check_sendcfg integer,sendingrpcfg integer)")
  print("tabela config criada com suceso!")
else:
    print("tabela config ja existe!") 
     
#*********criate or write file  ***************
def fileaw(pathfile,content,tp,ext):
  try:
    print('content file ->'+ content)   
    mode= 'a' if os.path.exists(pathfile)else 'w'
    with open(pathfile,mode)as f:
      if mode =='w' and tp=='contatos' and ext=='.csv':
        f.write('nomecontato,fonecontato,emailcontato'+'\n')
        f.write(content+'\n')
      else:  
        f.write(content+'\n')#f.write('Hello, world!\n')
      f.close()    
  except ImportError as ierr: #Return execption
    print('error file ', ierr)
#************************************************

def importcontacts_csv(pathfile,idcamp):
  import config as cfg  
  import time
  from tools import update_log as uplog
  #mostra o local da app
  localapp=os.getcwd()  

  linhas = 0  
  Eventos='...Importando contatos via csv'
  dtlocal = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
  uplog(Eventos)
  if (iftableexists(csqllite,'contatos')==True)and(pathfile!='' or pathfile!=None):
    with open (pathfile,mode='r',encoding='utf-8',errors='ignore')as arq: #with open (pathfile,mode='r')as arq:     
      leitor = csv.reader(arq,delimiter=';')      
      for coluna in leitor:
        if linhas ==0:
          Eventos='Coluna->'+str(coluna)
          uplog(Eventos)
          linhas +=1
        else:
          dtnow=datetime.now()
          datacad = str(datetime.strftime(dtnow,'%d/%m/%Y'))
          print('date now/data atual cadastro: '+datacad)          
          nomecontato=coluna[1]
          fonecontato=""
          fonecontato=str(coluna[2])
          fonecontato=fonecontato.replace(" ", "")
          emailcontato=coluna[3]          
          groupcategoria=coluna[4]
          status='S'
          iclie=status        
          #print("sql->",sql) 
          try:
            tablename ='contatos'
            Eventos='consultado se o contato já está cadastrado?'
            uplog(Eventos)
            csqllite.connection.commit()
            conctc=consulttablesql(csqllite,' nomecontato,fonecontato ',tablename,' where fonecontato = "'+fonecontato+'"',' ;')
            #result = msgbx.askquestion('Confirmação ','Quer realmente inserir um novo?')
            #if result == 'yes': 
            if conctc==[] or conctc==None: # if not exist contact result, then insert new
              Eventos='cadastrando o contato->'+nomecontato
              print(Eventos)#print(f'Colunas:{" ".join(coluna)}.')
              uplog(Eventos)              
              listfields='nomecontato,fonecontato,emailcontato,nomegrupocontato,ativocontato,eclientecontato,datacad'
              valuesfields='"'+nomecontato+'","'+fonecontato+'","'+emailcontato+'","'+groupcategoria+'","'+status+'","'+iclie+'","'+datacad+'"'
              where=";"
              sql="insert into "+tablename+" ("+listfields+") values("+valuesfields+")"+where                   
              csqllite.execute(sql)                
              csqllite.connection.commit()
            #insert contact in camp
            if idcamp!=0 and idcamp!=None:
              #get id last contact insert in db
              Eventos='pegando o codigo  do contato->'+nomecontato
              print(Eventos)#print(f'Colunas:{" ".join(coluna)}.')
              inserttablesql(csqllite,'log','descrilog,dttimelog','"'+Eventos+'","'+str(dtlocal)+'"','')#insert log db                   
              csqllite.connection.commit()
              uplog(Eventos)           
              rscons_idcontact=consulttablesql(csqllite,' idcontatos ',' contatos ',' where fonecontato = "'+fonecontato+'"',' ;')
              idcontact=0#get id contact
              if rscons_idcontact!=None:
                for y in rscons_idcontact:                    
                  for x in y:#:len(range(y)):
                    idcontact=y[0]
                if idcontact>0:#insert conctact in camp    
                  Eventos='importando o contato->'+nomecontato+', na campaha->'+str(idcamp)
                  uplog(Eventos)
                  csqllite.connection.commit()                  
                  inserttablesql(csqllite,'itenscamp','idcoditcamp,iditcontcamp,itnamecontcamp,itfonecontcamp',
                  ''+str(idcamp)+','+str(idcontact)+',"'+nomecontato+'","'+fonecontato+'"',' ;')
                  csqllite.connection.commit()                  
          except Exception as e:
            print("Error occurred import contact in csv: ", e)
            print('Tipo: ',type(e))
            print('Arqgumentos: ',e.args) 
            Eventos='Exception import contact in csv:'+"".join(e.args)
            uplog(Eventos)
            csqllite.connection.commit()            
            #print('numero: ',coluna[0],' nome: ',coluna[1])#print(f'\tNumero{coluna[0]} e o nome é {coluna[1]}.') 
            continue  # Continua para a próxima iteração do loop   
        linhas +=1#continua contando as linhas do laco for
    print('Lidas ',linhas)#print(f'lidas{linhas} lidas.')    
    return linhas
#**********************************************************  
def importcontacts_vcf(pathfile,idcamp): 
  #from pandas import read_csv as pdrdcsv  
  from tools import update_log as uplog
  from io import StringIO as strio     
  Eventos="...abrindo o arquivo para importação!"   
  uplog(Eventos)
  with open(pathfile, 'r') as f:
    listlines=[]
    listlines=f.readlines()
    count=0
    counterror=0
    global lenf
    lenf=0
    global getname    
    global getfone  
    global getemail 
    getname=''
    getfone='' 
    getemail=''
    global ext
    ext=''
    Eventos='Percorrendo as linhas do arquivo vcf e pegando os dados'
    uplog(Eventos)
    for ln in listlines:      
      lini= ln.strip()[0:12]   
      #getname=ln.strip()[0:3]
      if ln.strip()[0:3]=='FN:' and getname=='':
        getname=ln.strip()[3:len(ln)]           
      
      #getfone=ln.strip()[9:len(ln)]    
      if ln.strip()[0:9] =='TEL;CELL:':
        getfone=ln.strip()[9:len(ln)] 
        getfone=getfone.replace('+','') #remove sinal pus/remove sinal mais
        getfone=getfone.replace('-','') #remove sinal pus/remove sinal minus
        getfone=getfone.replace('(','')#remove caracter/remove caracter
        getfone=getfone.replace(')','')#remove caracter/remove caracter
        getfone=getfone.replace('.','')#remove caracter/remove caracter
        getfone=getfone.replace(' ','')#remove espace/remove espaco       
      elif ln.strip()[0:14] =='TEL;X-Celular:': 
        getfone=ln.strip()[14:len(ln)]
        getfone=getfone.replace('+','') #remove sinal pus/remove sinal mais
        getfone=getfone.replace('-','') #remove sinal pus/remove sinal minus
        getfone=getfone.replace('(','')#remove caracter/remove caracter
        getfone=getfone.replace(')','')#remove caracter/remove caracter
        getfone=getfone.replace('.','')#remove caracter/remove caracter
        getfone=getfone.replace(' ','')#remove espace/remove espaco
      
      if ln.split()[0:6] =='EMAIL:':
        getemail=ln.strip()[7:len(ln)]
        getemail=getemail.replace(' ','')#remove space/remove espaco
        getemail=getemail.lower()#letter minus/letra minuscula
      Eventos="Line{}: {}".format(count, ln.strip())
      uplog(Eventos)
      #if exist name and fone then write in csv 
      if getfone!='' and getname!='':              
        prefix='55'
        if getfone[0:2]!=prefix:#if not contains prefix/se não contem o prefixo
          getfone=prefix+getfone#Add prefix/adiciona o prefixo
        if len(getfone)==13:#prefix+number
          count +=1 
          print('write in csv file->',getname+','+getfone+','+getemail+',')
          lenf=(len(pathfile)-4)
          ext='.csv'  
          fileaw(pathfile[0:lenf]+ext,getname+','+getfone+','+getemail,'contatos',ext)#new file ou update content
          #return value from get name and get fone and email
          getname=''
          getfone=''
          getemail=''
        else:
          Eventos='Error number phpne minus 11 length!'+getname+','+getfone+','+getemail
          uplog(Eventos)
          lenf=(len(pathfile)-4)
          ext='.csv' 
          counterror+=1
          fileaw(pathfile[0:lenf]+'Error'+ext,getname+','+getfone+','+getemail,'contatos',ext)#new file ou update content
          #return value from get name and get fone
          getname=''
          getfone=''
          getemail=''
  importcontacts_csv(pathfile[0:lenf]+ext,0)          
  showmessage('Informação','Foram validos '+str(count)+' contados e rejeitados '+str(counterror)+',Salvo em arquivo para correção!')    
  return count
#**********************************************************  
def importmsgdatacampdv_csv(pathfile,idcampdv):
  import config as cfg  
  import time
  #mostra o local da app
  localapp=os.getcwd()  

  linhas = 0  
  Eventos='...Importando contatos e dados msg camp. diversa via csv'
  dtlocal = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
  inserttablesql(csqllite,'log','descrilog,dttimelog','"'+Eventos+'","'+str(dtlocal)+'"','')#insert log db         
  cfg.arqlog(localapp+'/ASW.log',Eventos)
  linhas = 0  
  if (iftableexists(csqllite,'itcampdv')==True)and(pathfile!='' or pathfile!=None):
    #idcontato,numerocontato,nomecontato,menssagemcontato,doccontato,imgcontato    
    with open (pathfile,mode='r')as arq:     
      leitor = csv.reader(arq,delimiter=',')      
      for coluna in leitor:
        if linhas ==0:
          print('colunas',coluna)#print(f'Colunas:{" ".join(coluna)}.')
          linhas +=1
        else:          
          #get values in file csv
          nomecontato=coluna[0]
          fonecontato=coluna[1]          
          emailcontato=coluna[2]
          group=''
          status='S'
          iclie=status   
          msgitcampdv=coluna[3]
          imgitcampdv=coluna[4]
          docitcampdv=coluna[5]
          #print("sql->",sql) 
          Eventos="..pegando os valores das colunas!"
          inserttablesql(csqllite,'log','descrilog,dttimelog','"'+Eventos+'","'+str(dtlocal)+'"','')#insert log db         
          cfg.arqlog(localapp+'/ASW.log',Eventos)
          try:
            Eventos='...Consultando o contato-> '+nomecontato+' no db!'
            inserttablesql(csqllite,'log','descrilog,dttimelog','"'+Eventos+'","'+str(dtlocal)+'"','')#insert log db         
            cfg.arqlog(localapp+'/ASW.log',Eventos)
            dtnow=datetime.now()
            datacad = str(datetime.strftime(dtnow,'%d/%m/%Y'))
            print('date now/data atual cadastro: '+datacad)
            tablename ='contatos'
            listfields='nomecontato,fonecontato,emailcontato,'
            listfields=listfields+'nomegrupocontato,ativocontato,eclientecontato,datacad'
            conctc=consulttablesql(csqllite,' nomecontato,fonecontato ',tablename,' where fonecontato = "'+fonecontato+'"',' ;')
            #result = msgbx.askquestion('Confirmação ','Quer realmente inserir um novo?')
            #if result == 'yes': 
            if conctc==[] or conctc==None: # if not exist contact result, then insert new
              Eventos='...Inserindo o contato-> '+nomecontato+' no db!'
              inserttablesql(csqllite,'log','descrilog,dttimelog','"'+Eventos+'","'+str(dtlocal)+'"','')#insert log db         
              cfg.arqlog(localapp+'/ASW.log',Eventos)
              valuesfields='"'+nomecontato+'","'+fonecontato+'","'+emailcontato+'","'+group+'","'+status+'","'+iclie+'","'+datacad+'"'
              where=";"
              sql="insert into "+tablename+" ("+listfields+") values("+valuesfields+")"+where                   
              csqllite.execute(sql)                
              csqllite.connection.commit()
              
            #insert contact in camp
            if idcampdv!=0 and idcampdv!=None:
              #get id contact insert in db
              Eventos='...pegando o id do contato-> '+nomecontato+' no db para inserir na camp.!'
              inserttablesql(csqllite,'log','descrilog,dttimelog','"'+Eventos+'","'+str(dtlocal)+'"','')#insert log db         
              cfg.arqlog(localapp+'/ASW.log',Eventos)
              rscons_idcontact=consulttablesql(csqllite,' idcontatos ',' contatos ',' where fonecontato = "'+fonecontato+'"',' ;')
              idcontact=0#get id contact
              if rscons_idcontact!=None:
                for y in rscons_idcontact:                    
                  for x in y:#:len(range(y)):
                    idcontact=y[0]
                if idcontact>0:#insert conctact in camp dv
                  Eventos='...Inserido os dados do contato-> '+nomecontato+' na campanha!'
                  inserttablesql(csqllite,'log','descrilog,dttimelog','"'+Eventos+'","'+str(dtlocal)+'"','')#insert log db         
                  cfg.arqlog(localapp+'/ASW.log',Eventos)
                  listfields="iditcampdv,msgitcampdv,idcontitcampdv,nomeitcampdv,numitcampdv,imgitcampdv,docitcampdv"
                  valuesfields=''+str(idcampdv)+',"'+msgitcampdv+'",'+str(idcontact)+',"'+nomecontato+'","'+fonecontato+'",'
                  valuesfields=valuesfields+'"'+imgitcampdv+'","'+docitcampdv+'"'
                  inserttablesql(csqllite,'itcampdv',listfields,valuesfields,';')
          except Exception as e:
            print("Error occurred import contact in csv: ", e)
            print('Tipo: ',type(e))
            print('Arqgumentos: ',e.args)   
            Eventos='Exception in methodo->importmsgdatacampdv_csv->'+"".join(e.args)
            cfg.arqlog(localapp+'/ASW.log',Eventos)
         #print('numero: ',coluna[0],' nome: ',coluna[1])#print(f'\tNumero{coluna[0]} e o nome é {coluna[1]}.')    
          linhas +=1
    print('Lidas ',linhas)#print(f'lidas{linhas} lidas.')    
    return linhas
#**********************************************************  
#insert image or doc in db
def insertupdateimgf(imagef,idcamp,dtimg,tpFile):
  global tablename
  tablename=''
  import base64
  from PIL import Image
  import io 
  #open file image in binare mode
  file = open(imagef,'rb').read()
  # We must encode the file to get base64 string
  imgfile = base64.b64encode(file)
  
  #?valuesfields='"'+imagef+'","'+idcamp+'","'+dtimg+'","'+imgfile+'"'
  #args=(imagef,idcamp,dtimg,imgfile)
  if tpFile == 1:#img
    tablename='img'
    sql='insert into '+tablename+' values((select count(idimg)+1 as count from '+tablename+'),"'+imagef+'","'+str(idcamp)+'","'+dtimg+'","'+imgfile.decode()+'")'
  if tpFile == 2:#doc
    tablename='doc'
  sql='insert into '+tablename+' values((select count(iddoc)+1 as count from '+tablename+'),"'+imagef+'","'+str(idcamp)+'","'+dtimg+'","'+imgfile.decode()+'")'  
  csqllite.execute(sql)
  csqllite.connection.commit()
  print("imagem salva no bd com sucesso!")
  #?showmessage('Alerta',"imagem inserida com sucesso!")
  #?insertupdateimgdoc("C:/Users/wsm/Pictures/ASW-Tecnica auto Zap.png",'5','02/03/2023',1)
  #?insertupdateimgdoc("C:/wsm/ASW/Imgs/Tecmaxima_FelizNatal.mp4",'2','10/12/2023',1)
#get image or doc from db
def getimgfdata(fileimg,idcamp,tpFile):# tpFile = 1 to (image-video) 2= to (doc)
  import base64
  from PIL import Image
  import io   
  try:
    rs=[]
    if tpFile == 1 :#img
      rs=consulttablesql(csqllite,' pictureimg ',' img ',' where idcampanhaimg = "'+str(idcamp)+'"','')    
    if tpFile == 2 :#doc
      rs=consulttablesql(csqllite,' picturedoc ',' doc ',' where idcampanhadoc = "'+str(idcamp)+'"','')      
      
    csqllite.fetchall()
      
    if rs!=None and rs!=0:
      img= rs[0][0]
      binary_data = base64.b64decode(img)
      
      ext_f=fileimg[(len(fileimg)-4):len(fileimg)]
      if ext_f =='.mp4' or tpFile==1 :#check if extension file is mp4 /Checa a extensão do arquivo mp4
        with open(fileimg,'wb')as fb:#escreve o arquivo no "fileimg"
          fb.write(binary_data)#write video file in local "fileimg"
      elif ext_f == '.jpg' or ext_f == '.jpeg' or ext_f == '.png' or ext_f == '.bmp' or ext_f  == '.gif':
        image=Image.open(io.BytesIO(binary_data))
        image.show('img_camp_'+str(idcamp))
            
  except Exception as e :
    print("Error occurred: ", e) 
