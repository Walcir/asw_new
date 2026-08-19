# -*- coding: utf-8 -*-
import string
import unidecode
import unicodedata
import re

def readcodnum(x):
    #caract of number
    crt_x = x
    #print("crt_x ",str(crt_x))
    crt_x = str(crt_x)
    
    if(crt_x == "01"):
        crt_x = "A"        
    elif(crt_x == "02"):
        crt_x = "B"
    elif(crt_x == "03"):
        crt_x = "C"
    elif(crt_x == "04"):
        crt_x = "D"
    elif(crt_x == "05"):
        crt_x = "E"
    elif(crt_x == "06"):
        crt_x = "F"
    elif(crt_x == "07"):
        crt_x = "G"
    elif(crt_x == "08"):
        crt_x = "H"
    elif(crt_x == "09"):
        crt_x = "I"
    elif(crt_x == "10"):
        crt_x = "J"
    elif(crt_x == "11"):
        crt_x = "K"
    elif(crt_x == "12"):
        crt_x = "L"
    elif(crt_x == "13"):
        crt_x = "M"
    elif(crt_x == "14"):
        crt_x = "N"
    elif(crt_x == "15"):
        crt_x = "O"
    elif(crt_x == "16"):
        crt_x = "P"
    elif(crt_x == "17"):
        crt_x = "Q"
    elif(crt_x == "18"):
        crt_x = "R"
    elif(crt_x == "19"):
        crt_x = "S"
    elif(crt_x == "20"):
        crt_x = "T"
    elif(crt_x == "21"):
        crt_x = "U"
    elif(crt_x == "22"):
        crt_x = "V"
    elif(crt_x == "23"):
        crt_x = "W"
    elif(crt_x == "24"):
        crt_x = "X"
    elif(crt_x == "25"):
        crt_x = "Y"
    elif(crt_x == "26"):
        crt_x = "Z"      
    else:
        crt_x = crt_x 
        
    #print("caracter ",crt_x)
    
    return crt_x 
    
def readcaracter(crt_x):
    crt_x = str(crt_x)
    #print('crt_x ',crt_x)
    #caract of number      

    #remove Acent equal 2 ziro 00
    if(crt_x == "A")or(crt_x =="?")or(crt_x =="?")or(crt_x =="?")or(crt_x == "?")or(crt_x =="?")or(crt_x =="?")or(crt_x =="?"): #?, ?, ?
        crt_x = crt_x.replace(crt_x,'a')
    elif(crt_x == "?")or(crt_x =="?")or(crt_x =="?")or(crt_x == "?")or(crt_x =="?")or(crt_x =="?"):#e, ?, ?
        crt_x = crt_x.replace(crt_x,'e')
    elif(crt_x == "?")or(crt_x =="?")or(crt_x == "?")or(crt_x =="?"): #?,?
        crt_x = crt_x.replace(crt_x,'i')
    elif(crt_x == "?")or(crt_x =="?")or(crt_x =="?")or(crt_x =="?")or(crt_x == "?")or(crt_x =="?")or(crt_x =="?")or(crt_x =="?"): #o, ?, ?
        crt_x = crt_x.replace(crt_x,'o')
    elif(crt_x == "?")or(crt_x =="?")or(crt_x =="?")or(crt_x =="?"):#u, ?, ?
        crt_x = crt_x.replace(crt_x,'u')
    elif(crt_x == "?")or(crt_x == "?"):
        crt_x = crt_x.replace(crt_x,'c')
    else: 
        crt_x = crt_x
    
    crt_x = crt_x.upper()#Upper letter
    
    if(crt_x == "A"):
        crt_x = "01"        
    elif(crt_x == "B"):
        crt_x = "02"
    elif(crt_x == "C"):
        crt_x = "03"
    elif(crt_x == "D"):
        crt_x = "04"
    elif(crt_x == "E"):
        crt_x = "05"
    elif(crt_x == "F"):
        crt_x = "06"
    elif(crt_x == "G"):
        crt_x = "07"
    elif(crt_x == "H"):
        crt_x = "08"
    elif(crt_x == "I"):
        crt_x = "09"
    elif(crt_x == "J"):
        crt_x = "10"
    elif(crt_x == "K"):
        crt_x = "11"
    elif(crt_x == "L"):
        crt_x = "12"
    elif(crt_x == "M"):
        crt_x = "13"
    elif(crt_x == "N"):
        crt_x = "14"
    elif(crt_x == "O"):
        crt_x = "15"
    elif(crt_x == "P"):
        crt_x = "16"
    elif(crt_x == "Q"):
        crt_x = "17"
    elif(crt_x == "R"):
        crt_x = "18"
    elif(crt_x == "S"):
        crt_x = "19"
    elif(crt_x == "T"):
        crt_x = "20"
    elif(crt_x == "U"):
        crt_x = "21"
    elif(crt_x == "V"):
        crt_x = "22"
    elif(crt_x == "W"):
        crt_x = "23"
    elif(crt_x == "X"):
        crt_x = "24"
    elif(crt_x == "Y"):
        crt_x = "25"
    elif(crt_x == "Z"):
        crt_x = "26"      
    else:
        crt_x = crt_x    
        
    #print("caracter ",crt_x)
    
    return crt_x 

def encrypt_txt_n(content_txt):
  y="" 
  if(content_txt!=None):  
    print("Encripty",content_txt)       
    for x in content_txt:
      y=y+readcaracter(x)+"."
      #print("Retorno lido ",y)     
  
  else:
    print("content_txt=none")
  
  y = y.replace(",","")
  return y

#r="19.05.18.22.09.04.15.18"

def desencrypt_n_txt(content_n):
    s=""
    lst=content_n.split(".")
    for x in lst:
        s=s+readcodnum(x)
        
    #print("retorno escrito: ",s) 
    return s
'''   
content_txt="EHTU"
content_n=encrypt_txt_n(content_txt)
desencrypt_n_txt(content_n)
'''

'''
def keylincence(k):
   for x in k:
    print(x)
    
    
chv = "05082021"
keylincence(chv)
'''