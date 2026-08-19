'''
try:
    from whatsappsender import WhatsAppSender as wsender
    import config as cfg
    timeqrcode =  round(float(cfg.readcfg('config.ini','action','timeqrcode')))
    sender_instance = wsender()#Crie uma instância da classe (com parênteses)
    #wsender.esperar_pagina(self=sender_instance,tempo=int(timeqrcode)) # type: ignore
    #?wsender.send_document(self=sender_instance,phone='5583988685395',caminho_documento="/media/wsm/wdc320g/Diversos/cursos/Linux no servidor.pdf")
    wsender.send_image(self=sender_instance,phone='5583988685395',caminho_imagem='/home/wsm/Downloads/VideoDownloader/Aula 1_Criando seu Primeiro Agente de IA com n8n.mp4',legenda='')
except Exception as e:
    print(f"❌ Erro ao enviar anexo: {' '.join(e.args)}")
'''

from datetime import date, datetime

'''
try:
  print('testando o vencimento da licença!')
  import config as cfg
  liense_key = cfg.readcfg('config.ini','active_license','key_license')
  print(f"licença = {liense_key}")  
  cfg.dtvenclicense=cfg.getVenc_lic(licenca=liense_key)
  vencimento = cfg.dtvenclicense
  vencimento = vencimento[0:2]+"/"+vencimento[2:4]+"/"+vencimento[4:6]
  print(f"retorno = {cfg.dtvenclicense}")
  print(f"vencimento = {vencimento}")
  
  if (cfg.VerifyVencdate(datetime.now(),cfg.dtvenclicense)==True):
    print('data vencida ou inválida!')
  else:
    print('data válida!')  
except Exception as e:
  print(f"erro no teste de vencimento pela licença:\n {''.join(e.args)}")
'''


#testando o envio por grupo
'''
exite_grupo = False
from campaigns import checkalertgroupcamp
idcamp = 1
Msg = 'Estou enviado a imagem para o grupo'
Doc=''
Img ='/media/wsm/wdc320g/Diversos/cursos/Desenvolvimento_web_com_PHP_e_MySQL_-_Ca.pdf'
exite_grupo = checkalertgroupcamp(idcamp=idcamp)
if exite_grupo:
    print("Ok exite grupo(s) para essa campanha!")
    from rpa import sendgroup
    from config import readcfg
    import databases as db
    print("Pegando as posições do campo de busca")
    xfind = readcfg('config.ini','action','px_fieldfind')
    yfind = readcfg('config.ini','action','py_fieldfind')
    print('Buscando no bd o(s) grupo(s) para ser(em) enviado(s)!')
    con_group =[]
    con_group =db.consulttablesql(db.csqllite,' iditcampgp,idcampgp,itnamegp ','icampgp',f'WHERE idcampgp={idcamp}','ORDER BY iditcampgp')
    if (con_group != [] and con_group != None):        
        for y in con_group:
          group=''  
          for x in range(len(y)):
            print(f"...pegando o(s) valor(es) do(s) grupo(s)")
            print(f"Na posição {x} o valor e {y[x]}")
            
            if(x==2):# se chegar na posição do nome do group, atribui a variavel
                group=str(y[x])
            print(f"...enviado para o grupo {group} !")    

          if(group!='') :
            sendgroup(xfind=int(xfind),yfind=int(yfind),
                    Img=Img,Doc=Doc,
                    Msg=Msg,
                    idcamp=idcamp,group=group)
'''
 #testando o try excepton com join e.args
try:
  i=0
  while i<10:
    i=i+1
    from tools import update_log as uplog
    uplog(f"o valor de i = {i}")
    if i==9:
      i=(i + "a")
except Exception as e:
  from tools import update_log as uplog
  uplog(f"error no teste de uplog com join e.args ".join(e.args))





