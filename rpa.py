# -*- coding: utf-8 -*-
import os
import platform
import random
import re
import subprocess
import time
from datetime import date, datetime

import pyautogui as pygui
import requests
from bs4 import BeautifulSoup
from genericpath import isfile

import config as cfg
import databases as db
from tools import showmessage
from tools import update_log as uplog  # methhod fo update log in db and file
from tools import deltxtarq as clean_logfile
from typing import List, Dict, Optional, Self
dtlocal = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
global Eventos
Eventos = ""
global url
url="https://web.whatsapp.com"
TPwebdriver=1
global dir_profile
dir_profile=""
Localwebdriver=""#limpa o local do webdriver
#mostra a plataforma so
plataform=platform.system()
print('SO',plataform)#'Linux'  # or 'Windows'/'Darwin'
#mostra o local da app
localapp=os.getcwd()

print('localApp: ',localapp) 
TPwebdriver = (cfg.readcfg('config.ini','action','browser'))  # 1-chrome(chromedriver) , 2-firefox 3,Edge
timeqrcode  =  cfg.readcfg('config.ini','action','timeqrcode')
px_btnadd   =cfg.readcfg('config.ini','action','px_btn+')
py_btnadd   =cfg.readcfg('config.ini','action','py_btn+')
px_btndoc   =cfg.readcfg('config.ini','action','px_btndoc')
py_btndoc   =cfg.readcfg('config.ini','action','py_btndoc')
px_btnimg   =cfg.readcfg('config.ini','action','px_btnimg')
py_btnimg   =cfg.readcfg('config.ini','action','py_btnimg')
px_fieldfind=cfg.readcfg('config.ini','action','px_fieldfind')
py_fieldfind=cfg.readcfg('config.ini','action','py_fieldfind')
px_fieldmsg =cfg.readcfg('config.ini','action','px_fieldmsg')
py_fieldmsg =cfg.readcfg('config.ini','action','py_fieldmsg')
pxbtnsend   =cfg.readcfg('config.ini','action','px_btnsend')
pybtnsend   =cfg.readcfg('config.ini','action','py_btnsend')

#**************************************************************
#dicionário lista de emoji para menssages
EMOJI = {
    "alerta":      "\u26A0\uFE0F",
    "erro":        "\u274C",
    "buscando":    "\U0001F50D",
    "ok":          "\u2705",
    "enviando":    "\U0001F4E4",
    "processando": "\u2699\uFE0F",
    "lendo":       "\U0001F4D6",
    "aguardando":  "\u231B",
}
#****************************************************************
#pega todo o conteudo da página para conferir (web Scrape)
def get_all_content_website(url):
  import requests
  from bs4 import BeautifulSoup
  from urllib.parse import urlparse
  from datetime import datetime
  import os
  import time
  try:
    website = requests.get(url)
    soup = BeautifulSoup(website.content, 'html.parser')
    html_content = ''
    if soup:
      html_content = soup.text
    print(html_content)
    # Salva o conteúdo em um arquivo de texto (recomendo usar extensão .html)
    # O encoding='utf-8' é vital para não quebrar acentos e emojis
    with open('webscrape.txt', 'w', encoding='utf-8') as file:
        file.write(html_content)
  except Exception as e:
      Evento_erro = f"Erro : {e}"
      uplog(Evento_erro)
      print(f"❌ {Evento_erro}")
  
  return html_content  
#**************************************************
def verificar_svg_icon(url, termo_busca):
    """
    Verifica se existe um ícone SVG (inline ou via <use>)
    """
    headers = {"User-Agent": "Mozilla/5.0"}


    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"\n🔍 Buscando SVGs relacionados a '{termo_busca}'...")   

    svg_encontrado = False
    
    # 1. Buscar SVGs inline
    svgs = soup.find_all('svg')
    print(f"   Total de <svg> encontrados: {len(svgs)}")
    
    if len(svgs)>0:
       svg_encontrado = True
       print(f"\n   ✅ Ícone encontrado")

   

    if not svg_encontrado:
        print(f"\n   ❌ Nenhum SVG/ícone de busca encontrado")
    
    #atualizando o arquivo de log e o bd 
    uplog(f"   Total de <svg> encontrados: {len(svgs)}")
    return svg_encontrado
#*************************************************** 
#  get eltement for xpath
def get_element_isvisible_by_xpath(url,xpath):
  """
  Raspa conteúdo usando XPath específico.

  Args:
    url: URL da página
    xpath: Expressão XPath para encontrar o elemento

  Returns:
    True ou False para Lista de elementos encontrados
    
    """
  import requests
  from lxml import html
  islocate=False

  headers = {
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
  }
  
  
  '''
  headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9"
  }
  '''
  
  print(f"🌐 Acessando  para xpath: {url}")
  response = requests.get(url, headers=headers, timeout=12)
  response.raise_for_status()
  
  # Parsear HTML com lxml (suporta XPath)
  tree = html.fromstring(response.content)
  
  print(f"🔍 Buscando com XPath: {xpath}")
 
  
  # Executar XPath
  elementos = tree.xpath(xpath)
  print(f"✅ Encontrados {len(elementos)} elemento(s) por xpath\n")
  if(len(elementos)>0):    
    islocate = True


  return islocate
#****************************************************** 
def check_element_isvisible_by_id(url,id_element):
  import requests
  from bs4 import BeautifulSoup as bs
  import time
  isvisible = False
  response = requests.get(url)
  soup = bs(response.content, 'html.parser')
  element = soup.find(id=id_element)
  if element:
    isvisible =  True
  return isvisible # return default
#**********************************************
def check_element_isvisible_by_class(url,eclass):
  import requests
  from bs4 import BeautifulSoup as bs
  import time
  response = requests.get(url)
  soup = bs(response.content, 'html.parser')
  element = soup.find(class_=eclass)
  return element is not None
#***********************************************
def login_rpa(TPwebdriver, timeqrcode):
  try:
    import os
    global Eventos 
    #1-Abrir Browser
    global browser_path
    browser_path = ""
    #caminho do exe
    if(TPwebdriver==1):#se for chrome 
      if os.name =='nt':# se for windows
        #?browser_path = r'C:\Program Files\Google\Chrome\Application\chrome.exe';
        browser_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"    
        #2-Abrir url no webbrowser
        #?subprocess.run([browser_path]);
      else: #linux ou mac os/unix
        import shutil
        if(TPwebdriver==2):#se for firefox
          browser_path =  shutil.which("firefox")# pega o caminho do firefox no linux
          if not browser_path:
            caminhos_comuns = [
                "/usr/bin/firefox",
                "/snap/bin/firefox",
                "/var/lib/flatpak/app/org.mozilla.firefox/current/active/files/bin/firefox"
            ]

            encontrado = False
            for caminho in caminhos_comuns:
                if os.path.exists(caminho):
                    print(f"{EMOJI['ok']} Firefox encontrado em: {caminho}")
                    encontrado = True
                    browser_path = caminho
                    break

            if not encontrado:
                print(f"{EMOJI['alerta']} Nenhum executável padrão do Firefox foi encontrado.")
                exit()

    pygui.hotkey('ctrl','l')
    Eventos= f"...{EMOJI['aguardando']} rpa.py-login_rpa(TPwebdriver,timeqrcode)-->Write url"
    uplog(Eventos)    
    # Digitar a URL
    global url
    url="https://web.whatsapp.com"    
    import urllib.parse
    encoded_url = urllib.parse.quote(url, safe=':/?=&')
    # Abrir o navegador
    #os.startfile(browser_path)
    import webbrowser
    webbrowser.open(str(encoded_url))    
    pygui.typewrite(encoded_url)
    Eventos=f"...{EMOJI['aguardando']} rpa.py-login_rpa(TPwebdriver,timeqrcode)-Press enter!"
    uplog(Eventos)
    pygui.press('enter')
    #4_esperar carregar pagina p qrcode
    Eventos=f"...{EMOJI['processando']} rpa.py-login_rpa(TPwebdriver,timeqrcode)-wait time login qrcode->"+str(timeqrcode)
    uplog(Eventos)
    from whatsappsender import WhatsAppSender as wsender
    wsender.esperar_pagina(Self,int(timeqrcode)) # type: ignore
    #?time.sleep(float(timeqrcode))
    
    return url
  except Exception as e:
    Eventos=f"{EMOJI['erro']} Exceção ao fazer login no whatsapp/Exception in login whatsapp!->"+" ".join(e.args)
    uplog(Eventos)
    showmessage('Alert',Eventos)
#*******************************************************
def locate_search_field():#aguarda localizar o botão pesquisar na tela
  print(f"...{EMOJI['aguardando']} Localizando o botão pesquisar")
  timeqrcode =  str(cfg.readcfg('config.ini','action','timeqrcode'))
  run_time =float(timeqrcode)
  '''
  # força a busca pela classe
  run_time =  float(timeqrcode)      
  while  visible_field == False:        
    visible_field = check_element_isvisible_by_class(url,"html-input xdj266r x14z9mp xat24cr xllziwak xexx8yu xyri2b x18d9i69 xlcuobl xliyjqo2")
    run_time =  (run_time-01.0)
    Eventos=f"...Checando se o botão pesquisar foi carregado pela class em {run_time}\u231B"#ampulheta  
    print(Eventos)
    uplog(Eventos)
    time.sleep(1)

    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por classe não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)            
      
      break
  #********************************   

  # testa buscar a imagem do campo de pesquisa 'lupa' 'search' 'svg'
  visible_field  = verificar_svg_icon(url=url, termo_busca="search")
  #******************************** 
  '''
  visible_field = False    

  while check_element_isvisible_by_id(url,'app')==False:          
    run_time = run_time-01.0
    Eventos=f"...Wait time read qrcode/aguardando ler o qrcode!-> em {run_time} segundos.\u231B"#ampulheta
    print(Eventos)
    uplog(Eventos)
  
  #força a busca pelo id principal '_r_b_' do botão
  Eventos=f"...força a busca pelo id principal '_r_b_' da página\u231B"#ampulheta
  print(Eventos)
  uplog(Eventos)
  # testa a busca pelo id
  while  visible_field == False:
    visible_field = check_element_isvisible_by_id(url,"_r_b_")
    run_time = run_time-01.0
    Eventos=f"...Checando se o campo pesquisar foi carregado pelo id '_r_b_' em {run_time} segundos.\U0001F50D"#lupa      
    print(Eventos)
    uplog(Eventos)
    time.sleep(1)      

    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por id '_r_b_' não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)        

      break
  #******************************** 
  
  # testa buscar a imagem do campo de pesquisa 'lupa' 'search' 'svg'
  visible_field  = verificar_svg_icon(url=url, termo_busca="search")
  #******************************** 
  
  #testa a busca pelo xpath  # 1. Combinação de aria-label + role (MUITO específico)
  run_time =float(timeqrcode)#reinicia o contador
  while  visible_field == False:
    #visible_field =get_element_isvisible_by_xpath(url=url,xpath='//input[@role="textbox" and @aria-label="Pesquisar ou começar uma nova conversa"]')      
    visible_field =get_element_isvisible_by_xpath(url=url,xpath="//input[@id='_r_b_'")      
    run_time = run_time-01.0
    Eventos=f"...Checando se o campo pesquisar foi carregado pelo xpath  # 1. Combinação de aria-label + role (MUITO específico) em {run_time} segundos.\U0001F50D"#lupa      
    print(Eventos)
    uplog(Eventos)
    time.sleep(1) 
    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por xpah  # 1. Combinação de aria-label + role (MUITO específico) não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)        

      break
  #********************************

  #testa a busca pelo xpath  # 2. Placeholder exato
  run_time =float(timeqrcode)#reinicia o contador
  while  visible_field == False:
    visible_field =get_element_isvisible_by_xpath(url=url,xpath='//input[@placeholder="Pesquisar ou começar uma nova conversa"]')
    run_time = run_time-01.0
    Eventos=f"...Checando se o campo pesquisar foi carregado pelo xpath # 2. Placeholder exato em {run_time} segundos.\U0001F50D"#lupa      
    print(Eventos)
    uplog(Eventos)
    time.sleep(1) 
    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por xpah # 2. Placeholder exato não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)        

      break
  #********************************

  #testa a busca pelo xpath   # 3. aria-label contém texto (flexível)
  run_time =float(timeqrcode)#reinicia o contador
  while  visible_field == False:
    visible_field =get_element_isvisible_by_xpath(url=url,xpath='//input[@role="textbox" and contains(@aria-label, "Pesquisar")]')
    run_time = run_time-01.0
    Eventos=f"...Checando se o campo pesquisar foi carregado pelo xpath # 3. aria-label contém texto (flexível) em {run_time} segundos.\U0001F50D"#lupa      
    print(Eventos)
    uplog(Eventos)
    time.sleep(1) 
    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por xpah # 3. aria-label contém texto (flexível) não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)        

      break
  #********************************

  #testa a busca pelo xpath   # 4. ID dinâmico (começa com _r_)
  run_time =float(timeqrcode)#reinicia o contador
  while  visible_field == False:
    visible_field =get_element_isvisible_by_xpath(url=url,xpath='//input[starts-with(@id, "_r_") and @role="textbox"]')
    run_time = run_time-01.0
    Eventos=f"...Checando se o campo pesquisar foi carregado pelo xpath # 4. ID dinâmico (começa com _r_) em {run_time} segundos.\U0001F50D"#lupa      
    print(Eventos)
    uplog(Eventos)
    time.sleep(1) 
    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por xpah # 4. ID dinâmico (começa com _r_) não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)        

      break
  #********************************

  #testa a busca pelo xpath   # 5. Data-tab específico
  run_time =float(timeqrcode)#reinicia o contador
  while  visible_field == False:
    visible_field =get_element_isvisible_by_xpath(url=url,xpath='//input[@role="textbox" and @data-tab="3"]')
    run_time = run_time-01.0
    Eventos=f"...Checando se o campo pesquisar foi carregado pelo xpath # 5. Data-tab específico em {run_time} segundos.\U0001F50D"#lupa      
    print(Eventos)
    uplog(Eventos)
    time.sleep(1) 
    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por xpah # 5. Data-tab específico não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)        

      break
  #********************************

  # testa buscar a imagem do campo de pesquisa 'lupa' 'search' 'svg'
  visible_field  = verificar_svg_icon(url=url, termo_busca="search")
  #******************************** 

  #força a busca pelo id do campo pesquisa
  run_time = run_time-01.0
  while  visible_field == False:
    visible_field = check_element_isvisible_by_id(url,'input[id^="_r_"]')
    run_time = run_time-01.0
    Eventos=f"...Checando se o campo pesquisar foi carregado pelo id input[id^='_r_'] em {run_time} segundos.\U0001F50D"#lupa      
    print(Eventos)
    uplog(Eventos)
    time.sleep(1)

    if run_time < 01.0: # se chegou o final do tempo avisa
      Eventos = f"Timeout! Elemento por id '_r_b_' não apareceu em {run_time} segundos.\u274C"#X vermelho
      print(Eventos)
      uplog(Eventos)        

      break
  #********************************
  # testa buscar a imagem do campo de pesquisa 'lupa' 'search' 'svg'
  visible_field  = verificar_svg_icon(url=url, termo_busca="search")
  #******************************** 
  return visible_field
#******************************************************
def sendmsg(Num,Msg):
  """
  Envia mensagem pelo WhatsApp Web sem Selenium/Playwright

  Args:
    numero (str): Número do telefone com DDD (ex: '558399050093')
    mensagem (str): Mensagem a ser enviada
  """
  enviada =False
  try:
    #?Num="+"+str(Num) 
    # Limpa o número (remove espaços, parênteses, etc)   
    numero_limpo = ''.join(filter(str.isdigit,str(Num)))
    import urllib.parse
    #??pygui.hotkey('win','d')
    Eventos="rpa.py->sendmsg-> get url/pegando a url"
    time.sleep(random.randint(3,5))#espera entre 3 e cinco segundos
    uplog(Eventos)
    print(Eventos)
    #?Msg = urllib.parse.quote('{Msg}')    
    # Codifica a mensagem para URL
    mensagem_codificada = urllib.parse.quote(Msg)
    '''
    url="https://web.whatsapp.com/send?phone="+Num+"&text="+Msg      
    encoded_url = urllib.parse.quote(url, safe=':/?=&')    
    #??showmessage('',str(encoded_url))    
    '''    
    # Monta a URL
    url = f"https://web.whatsapp.com/send?phone={numero_limpo}&text={mensagem_codificada}"
    Eventos="Montando a url"+url
    uplog(Eventos)
    print(Eventos)
    import webbrowser    

    # Abre no navegador padrão
    #webbrowser.open(str(encoded_url))     
    webbrowser.open(url)
    Eventos="Abre a url solicitada no navegador"
    uplog(Eventos)
    print(Eventos)

    time.sleep(random.randint(3,5))
    timeqrcode =  str(cfg.readcfg('config.ini','action','timeqrcode'))

    Eventos="Aguarda ente 6 e 13 segundos para iniciar a conversa"
    uplog(Eventos)
    print(Eventos)
    time.sleep(random.randint(9,13))

    Eventos="press end e aguarda 3 segundos"
    uplog(Eventos)
    print(Eventos)    
    pygui.keyDown('end') 
    time.sleep(3)   

    Eventos="Press enter p/ confirma a url e aguarda entre 6 e 9 segundos"
    pygui.keyDown('enter')
    uplog(Eventos)
    print(Eventos)
    time.sleep(random.randint(6,9))
    Eventos="Aguardando o carregamento da tela principal ou o tempo para ler o qrcode de login"
    uplog(Eventos)
    print(Eventos)

    from whatsappsender import WhatsAppSender as wsender
    wsender.esperar_pagina(Self,int(timeqrcode)) # type: ignore
    
    #*****************************************************
    #testa buscar a imagem do campo de pesquisa 'lupa' 'search' 'svg'
    visible_icon = verificar_svg_icon(url=url, termo_busca="search")
    while not visible_icon:
      time.sleep(float(timeqrcode))  
      print(f'...Aguardando {str(int(timeqrcode)-1)} s para o icone da lupa de pesquisa da pagina principal aparecer!')
      visible_icon = verificar_svg_icon(url=url, termo_busca="search")

    """
     #<p class="selectable-text copyable-text x15bjb6t x1n2onr6" dir="ltr" style="text-indent: 0px; margin-top: 0px; margin-bottom: 0px;"><span class="selectable-text copyable-text" data-lexical-text="true">Boa noite!</span></p>
    """
    
    """
    while check_element_isvisible_by_class(url,"selectable-text copyable-text x15bjb6t x1n2onr6")==None:
      Eventos="...aguardando o campo de mensagem aparecer!"
      uplog(Eventos)
      print(Eventos)
      time.sleep(5)
    #?if isfile==False:
    
    """

    """      
    else: 
    px_btnsend =  str(cfg.readcfg('config.ini','action','px_btnsend'))
    py_btnsend =  str(cfg.readcfg('config.ini','action','py_btnsend'))
    Eventos="Pegando as posições e clicando no botão enviar x,y-> "+str(px_btnsend)+", "+str(py_btnsend)        
    uplog(Eventos)
    print(Eventos)
    
    Eventos = "movendo o cursor e clicando on  botão enviar"
    uplog(Eventos)
    pygui.moveTo(int(px_btnsend),int(py_btnsend),duration=1.5)
    pygui.click()
    time.sleep(random.randint(4,7))#aguarda o envio
    """

    timesendmsg = str(cfg.readcfg('config.ini','action','timesendmsg'))
    Eventos = f"{EMOJI['lendo']} Pegando o tempo de carregar envio da messagem e aguardando "+timesendmsg
    uplog(Eventos)
    
    contador = 0 
    while contador < round(float(timesendmsg)):# o round arredonda o valor float para o inteiro mais proximo
      contador = contador +1
      time.sleep(1)
      Eventos = f"{EMOJI['aguardando']}  ...aguardando {contador} de "+timesendmsg+" para enviar a menssagem!"
      uplog(Eventos)
    
    
    while verificar_svg_icon(url=url,termo_busca='sticker')==False:  
      contador = contador - 1    
      Eventos = f"{EMOJI['aguardando']}...Aguardando em {contador} não aparecer o icone svg do botao stick principal para exibir o campo de menssagem na tela aguarda!"  
      uplog(Eventos)
      Eventos =f" {EMOJI['buscando']}...buscando aparecer o botão  sticker para confirmar o envio!"
      uplog(Eventos)
      time.sleep(1)
    else:  
      #time.sleep(float(timeqrcode))
      Eventos=f"{EMOJI['alerta']} Menssagem de texto enviada com sucesso para o numero:"+Num
      uplog(Eventos)      
      time.sleep(random.randint(5,7))
      enviada=True
      pygui.hotkey('ctrl','f4')#fecha a tab do navegador se enviada
  except Exception as e:
    Eventos=f"{EMOJI['erro']} Exceção ao enviar mensagem/Exception in send message!->"+" ".join(e.args)
    uplog(Eventos)
    #?showmessage('Alert',Eventos)
    pygui.hotkey('ctrl','f4')#fecha a tab do navegador se error
  return enviada  
#*******************************************************
def send_file(Img,Doc,codigo,Nome,Numero,idcamp,timeupload):
  #send message to open field and butons file /Envia menssagem para abrir a tela e mostrar os botoes e o campo para arquivo
  #?sendmsg(Numero,"arquivo->",True)
  #?time.sleep(random.randint(13,15))
  #####sending documents or image or video
  px_btnadd=cfg.readcfg('config.ini','action','px_btn+')
  py_btnadd=cfg.readcfg('config.ini','action','py_btn+')
  px_btndoc=cfg.readcfg('config.ini','action','px_btndoc')
  py_btndoc=cfg.readcfg('config.ini','action','py_btndoc')
  px_btnimg=cfg.readcfg('config.ini','action','px_btnimg')
  py_btnimg=cfg.readcfg('config.ini','action','py_btnimg')
  pxbtnsend=cfg.readcfg('config.ini','action','px_btnsend')
  pybtnsend=cfg.readcfg('config.ini','action','py_btnsend')
  if(Doc!="" and Doc!=None):#exist Docments attachment
    #?Doc=Doc.replace('\\','/')#remove carcater clean or update
    Eventos = f' {EMOJI["enviando"]} --Enviando doc '+Doc+' anexo para = '+Nome
    uplog(Eventos)
    if os.path.exists(Doc):
      '''
      Eventos="clicar no sinal de +"
      uplog(Eventos)
      pygui.click(int(px_btnadd),int(py_btnadd),duration=1.5)
      Eventos="clicar no botao documento"
      uplog(Eventos)
      pygui.click(int(px_btndoc),int(py_btndoc),duration=1.5)
      time.sleep(random.randint(5,7))
      Eventos="preecher o caminho do arquivo"
      uplog(Eventos)
      pygui.typewrite(Doc)
      time.sleep(random.randint(3,6))
      Eventos="pressionar tab 2x e enter em abrir"
      pygui.press(['tab', 'tab', 'enter'],interval=2.0)
      time.sleep(random.randint(10,11))
      Eventos="clicando no botão enviar "
      pygui.click(int(pxbtnsend),int(pybtnsend),duration=1.0)
      time.sleep(float(timeupload))
      time.sleep(random.randint(5,8))
      Eventos="file exist "+Doc+"-Send sucess/Arquivo existente enviado com sucesso!"
      uplog(Eventos)
      '''
      from whatsappsender import WhatsAppSender as wsender
      wsender.send_document(self=Self,phone=str(Numero),caminho_documento=Doc,nome_arquivo="",legenda="") # type: ignore
      tablename="doc"
      listfields="iddoc, namedoc"
      where= "where namedoc ='"+Doc+"'"
      order =";"
      sql="Select "+listfields+" from "+tablename+" "+where+" "+order
      rs = db.consulttablesql(db.csqllite,listfields,tablename,where,";")
      #if(len(rs)==0):#if no  result con doc
      if(rs!=[] and rs!=None):
        try:
          dtnow=datetime.now()
          #datacad = str(datetime.strftime(dtnow,'%d/%m/%Y %H:%M'))
          dtimg = str(datetime.strftime(dtnow,'%d/%m/%Y'))
          db.insertupdateimgf(Doc,idcamp,dtimg,2)
          Eventos=f"{EMOJI['ok']} Documento "+Doc+" salvo na tabela doc com sucesso!"          
          Eventos=Eventos+(sql)                 
          uplog(Eventos)
          
        except Exception as e:
          Eventos=f"{EMOJI['erro']}"+" ".join(e.args)
          uplog(Eventos)
          showmessage('Excecao ao inserir doc!',Eventos)

    else:
      Eventos = f'{EMOJI["alerta"]} 1--Documento negado ou inexistente para = '+str(codigo)+'-'+Nome+'-'+str(Numero)
      uplog(Eventos)
    #*************end send doc in mensagem/fim do envio do documento*************
    
  if(Img!="" and Img!=None):#exist Image or video attachment
   
    if platform.system() == 'Windows':
      Img=Img.replace('/','\\')#remove carcater clean or update
    Eventos = f'{EMOJI["enviando"]}1-...Enviando imagem '+Img+' anexa para = '+Nome+'-'+str(Numero)
    uplog(Eventos)    
    if os.path.exists(Img):

      '''
      Eventos="clicar no sinal de +"
      uplog(Eventos)
      pygui.click(int(px_btnadd),int(py_btnadd),duration=1.5) # type: ignore

      Eventos="clicar no botao imagem cam"
      uplog(Eventos)
      pygui.click(int(px_btnimg),int(py_btnimg),duration=1.5) # type: ignore
      time.sleep(random.randint(4,8))

      Eventos="preecher o caminho do arquivo"
      uplog(Eventos)    
      pygui.typewrite(Img)
      time.sleep(random.randint(9,11))

      Eventos="pressionar tab 2x e enter em abrir"
      pygui.press('tab',interval=2.0)
      time.sleep(2.0)
      pygui.press('tab',interval=2.0)
      time.sleep(2.0)

      pygui.press('enter')
      time.sleep(random.randint(10,11))

      Eventos="clicando no botão enviar "
      pygui.click(int(pxbtnsend),int(pybtnsend),duration=1.0) # type: ignore
      time.sleep(float(timeupload))
      time.sleep(random.randint(10,11))
      Eventos = 'imagem enviada com sucesso para = '+Nome
      uplog(Eventos)

      '''
      from whatsappsender import WhatsAppSender as wsender
      wsender.enviar_imagem(self=Self,phone=str(Numero),caminho_imagem=Img,legenda="") # type: ignore
      tablename="img"
      listfields="idimg, nameimg"
      where= " where nameimg ='"+Img+"'"
      order =";"
      sql="Select "+listfields+" from "+tablename+" "+where+" "+order
      rs = db.consulttablesql(db.csqllite,listfields,tablename,where,";")
      #if(len(rs)==0):#if no  result con img in database
      if(rs==[] or rs==None):
        try:
          dtnow=datetime.now()
          dtimg = str(datetime.strftime(dtnow,'%d/%m/%Y'))
          Eventos =f'{EMOJI["processando"]} Salvando imagem no banco de dados '
          uplog(Eventos)
          #?db.insertupdateimgf(Img,idcamp,str(dtimg),1)
        except Exception as e:
          Eventos=f"{EMOJI['erro']} Error occurred: ao inserir img "
          Eventos=Eventos+(sql)
          Eventos=Eventos+" ".join(e.args)
          uplog(Eventos)
    else:
      Eventos = f'{EMOJI['alerta']} --imagem negado para = '+str(codigo)+'-'+Nome+'-'+str(Numero)+'-img-'+Img
      uplog(Eventos)
#*******************************************************
def sendgroup(xfind,yfind,Img,Doc,Msg,idcamp,group):
  try:
    import webbrowser
    cfg.cleanFile(localapp+'/ASW.log')#clean file log 
    Eventos=f"...{EMOJI['processando']} abrindo a url e pegando o tempo de espera para login"
    webbrowser.open("https://web.whatsapp.com")
    timeqrcode =  str(cfg.readcfg('config.ini','action','timeqrcode'))
    uplog(Eventos)
    
    cont = 0
    while cont < (float(timeqrcode)) :
      cont = cont +1
      Eventos=f"....{EMOJI['aguardando']} aguardando carregar a página {cont} de {(float(timeqrcode))}"
      uplog(Eventos)
      time.sleep(1)
    
    Eventos=f"...{EMOJI['processando']} Iniciando o envio para um grupo!/Begin send group"
    uplog(Eventos)    
    
    Eventos=f"...{EMOJI['aguardando']} Buscando o campo pesquisar"
    uplog(Eventos=Eventos)    

    Eventos=f"...{EMOJI['processando']} Simular o clique no elemento (ajustar as coordenadas:x {xfind}, y {yfind} conforme necessário)!"
    uplog(Eventos)    
    # Simular o clique no elemento (ajustar as coordenadas conforme necessário)
    pygui.click(xfind, yfind,duration=3.5)#click no campo pescquisar

    time.sleep(random.randint(15,16))#espera o campo pesquisar
    Eventos=f"{EMOJI['processando']} Escreve o nome do grupo"
    uplog(Eventos)
    #?pygui.typewrite(group,interval=1.5)#escreve o nome do grupo no campo pesquisar
    '''
    # importando a biblioteca keyboard que possui suporte para teclas em português (acentuação)
    '''
    import platform      
    import keyboard as key 
    tpsystem = platform.system()
    from typing import List, Dict, Optional
    if tpsystem == 'nt':# se for windows
      key.write(group)#escreve o nome do grupo no campo pesquisar
    else:
      time.sleep(3)#Espera 3 segundos 
      
      pygui.hotkey('ctrl', 'a')
      Eventos = 'Seleciona todo o texto no campo atual'
      uplog(Eventos)
      print(Eventos)

      # Apaga o texto selecionado
      pygui.press('delete')
      Eventos = 'Apaga o texto selecionado com delete'
      uplog(Eventos)
      print(Eventos)

      import pyperclip
      
      pyperclip.copy(group)
      Eventos="# Copia para a memória do sistema (não exige sudo e funciona no Wayland)"
      uplog(Eventos)
      print(Eventos)

      # Cola dentro do Firefox usando o atalho universal
      time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos 
      pygui.hotkey("ctrl", "v")
      time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos 
      Eventos= "Cola dentro do Firefox usando o atalho universal"
      uplog(Eventos)
      print(Eventos)
      time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos 

    Eventos=f"{EMOJI['processando']} pressiona enter"
    uplog(Eventos)
    pygui.press('enter')
    time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos após o enter

    if Msg and Msg != "": # se estiver mennssagem conigurada
      Eventos="click no campo menssagem!/click in field mesnsage!"    
      uplog(Eventos)
      px_fieldmsg= str(cfg.readcfg('config.ini','action','px_fieldmsg'))
      py_fieldmsg= str(cfg.readcfg('config.ini','action','py_fieldmsg'))
      pygui.click(int(px_fieldmsg),int(py_fieldmsg),duration=3.0)
      Eventos="escreve a menssagem/write messagem!"    
      uplog(Eventos)
      pygui.typewrite(Msg,interval=0.1)
      Eventos="pressiona enter"
      pygui.press('enter')
      Eventos="espera envia a menssagem/wait send mensage!"
      time.sleep(random.randint(5,6));
      uplog(Eventos)
    
    #*****************************************************
    from whatsappsender import WhatsAppSender as wsender  
    # 1. Crie uma instância da classe (com parênteses)
    sender_instance = wsender()   
    #*****************************************************       
    Eventos="envia o arquivo/send file"
    uplog(Eventos)
    timeupload=15
    timeupload= cfg.readcfg('config.ini','action','timeupimg')
    Eventos=f"{EMOJI['lendo']} pegando o tempo para envio do arquivo de->"+str(timeupload)
    uplog(Eventos)
    # se tiver documento em anexo configurado envia
    if (Doc!=None and Doc!=""):
      Eventos=f"...{EMOJI['enviando']} Enviando documento em anexo"
      uplog(Eventos)
      print(Eventos)
      #?send_file("",Doc,1,group,0,idcamp,timeupload)#comentado por walcir pois usárá a classe nova para envio
      wsender.send_document(self=sender_instance,phone="",caminho_documento=Doc,nome_arquivo="",legenda="") # type: ignore
    
    # se tiver video/imagem em anexo configurado envia
    if (Img!=None and Img!=""):
      Eventos=f"...{EMOJI['enviando']} Enviando video/imagem em anexo"
      uplog(Eventos)
      print(Eventos)
      #send_file(Img,"",1,group,0,idcamp,timeupload)#comentado por walcir pois usará a rotina da classe whataappsender
      wsender.send_image(self=sender_instance,phone="",caminho_imagem=Img,legenda="") # type: ignore 
    #espera envia a menssagem
    time.sleep(random.randint(5,6));
    pygui.hotkey('ctrl','f4')

    if (idcamp != None) or (group != None):
      print(f"Enviado dados para o grupo {group} da campanha {idcamp} com sucesso!")

    return True
  except Exception as e:
    Eventos="Exceção ao enviar para grupo/Exception in send group!->"+" ".join(e.args)
    uplog(Eventos)
    showmessage('Alert',Eventos)
    pygui.hotkey('ctrl','f4')

    return False
#*******************************************************
def sendSingleMessage(idcamp,filejson):
  import pyautogui as pygui  
  import json
  try:
    #Arq_dados  = cfg.readcfg('config.ini','repository','filejson')
    timeupload = cfg.readcfg('config.ini','action','timeupimg')
    TPwebdriver=None
    TPwebdriver = (cfg.readcfg('config.ini','action','browser'))  # 1-chrome(chromedriver) , 2-firefox 3,Edge
    filejson=filejson.replace('/','//')
    Eventos ='...Lendo json: '+filejson 
    uplog(Eventos) 
    print(Eventos)
    data = json.load(open(filejson)) #ler_json(Arq_dados)
    #time_u=0#zera o contador de tempo usado 
    #list Saudation or congralutation
    lsauda=["OI,","Tudo bom? ","olá,","Tudo bem?","Como vai?"]
    cont_lin=0
    global saudatime   
    saudatime=cfg.saudahora  
    #percorre as linhas de cima pra baixo
    for y in data:
      cfg.arqlog(localapp+'/ASW.log','Linha lida :'+str(y)) 
      print("...Testando a posição de linha do elemento dentro do for = ",str(cont_lin))
      #time_u += time_u #incrementa contador
      cont_lin = cont_lin+1 #incrementa contador de linha de conteudo
      if cont_lin ==1:           
        print(f"...{EMOJI['aguardando']} Fazendo login inicial para aguardar o login qrcode e carregar a pagina pela primeira vez")
        login_rpa(TPwebdriver=TPwebdriver,timeqrcode=timeqrcode)
        pygui.hotkey('ctrl','f4')# fecha para evitar abas duplicadas do whatsappweb e travar com pegunta qual aba usar
      
      Id=y['Id']
      Nome=""
      Nome=str(y['Nome'])
      Numero=""
      Numero=str(y['Numero'])
      Msg=""
      Msg=str(y['Mensagem'])
      Doc=y['Doc']
      Img=y['Img']
      print("pegando os dados para serem enviados")
      if Msg!=None and Msg!="":  
        Oksendmsg=sendmsg(Numero,Msg)

        while Oksendmsg==True:
          #Enviando os arquivos de imagem e documentos************
          if Doc!="" and Doc!=None:
            Eventos="Enviando documento/Send file doc"
            print(Eventos)
            uplog(Eventos)
            send_file(Img,Doc,Id,Nome,Numero,idcamp,timeupload)

          if Img!="" and Img!=None:
            Eventos="Enviando imagem/send image"
            uplog(Eventos)
            print(Eventos)
            send_file(Img,Doc,Id,Nome,Numero,idcamp,timeupload)
          #*******************************************************

          #*******************************************************

          #pygui.hotkey('alt','f4')#close tag browser after send/fecha tag do browser apos enviar
          Oksendmsg=False#return status /retorna o status
        else:
           Eventos = "Mensagem não enviada para "+str(Nome)+" numero "+str(Numero)+" !"  
           uplog(Eventos)
           print(Eventos)
    #fecha apos percorrer todo o 'for' com o laço da lista de numeros para enviar
    Eventos = f"{EMOJI['ok']} Toda a lista de {cont_lin} numeros foi percorida e processada o envio das menssagems"
    uplog(Eventos)
    print(Eventos)
    #??pygui.hotkey('alt','f4')#close app after send /fecha app apos enviar
  except Exception as e:
    Eventos="exception in rpa->sendSingleMessage->"+"".join(e.args)
    #Eventos=Eventos.join(e.args)
    uplog(Eventos)
    print(Eventos)
    #?showmessage('Alert',Eventos)
    pygui.hotkey('ctrl','f4')
#"https://web.whatsapp.com/send?phone=+5583986737243&text=Estou Fazendo alguns testes na app e não terminei aida isso é testes!
#pygui.hotkey('ctrl','f4')

#?#sendgroup(147,205,Img,"","Estamos avaliando nossa aplicação",2,'Tecmaxima IA')
#*****************************************************************************************
def _obter_clipboard() -> str:
  """
  Obtém o conteúdo do clipboard de forma nativa
  """
  import platform
  sistema  = platform.system()
  if sistema == "Linux":
      try:
          # Usa xclip
          resultado = subprocess.run(
              ['xclip', '-selection', 'clipboard', '-o'],
              capture_output=True,
              text=True,
              timeout=2
          )
          return resultado.stdout
      except:
          try:
              # Fallback para xsel
              resultado = subprocess.run(
                  ['xsel', '--clipboard', '--output'],
                  capture_output=True,
                  text=True,
                  timeout=2
              )
              return resultado.stdout
          except:
              return ""
              
  elif sistema == "Darwin":  # macOS
      try:
          resultado = subprocess.run(
              ['pbpaste'],
              capture_output=True,
              text=True,
              timeout=2
          )
          return resultado.stdout
      except:
          return ""
          
  elif sistema == "Windows":
      try:
          import pyperclip
          return pyperclip.paste()
      except:
          return ""
  
  return ""
#**********************************
def capturar_tela_html() -> str:
  """
  Captura o HTML da página atual usando métodos nativos
  """
  print("📸 Capturando HTML da página...")
  
  # Método 1: Usar atalho para salvar página (mais confiável)
  # Ctrl+S para salvar, Ctrl+A para selecionar tudo, Ctrl+C para copiar
  
  # Seleciona tudo
  pygui.hotkey('ctrl', 'a')
  time.sleep(0.3)
  
  # Copia
  pygui.hotkey('ctrl', 'c')
  time.sleep(0.5)
  
  # Tenta obter do clipboard
  html = _obter_clipboard()
  
  if html:
      print(f"✅ HTML capturado: {len(html)} caracteres")
      return html
  
  # Método 2: Usar DevTools via atalho (F12)
  print("🔄 Tentando método alternativo...")
  pygui.press('f12')
  time.sleep(1)
  
  # Seleciona elemento <html> no console
  # Nota: Este método é mais complexo e pode não funcionar em todos os casos
  
  return ""   
#**************************************
def _capturar_manual() -> List[Dict]:
    """
    Método manual de captura (fallback)
    """
    print("\n🔄 MODO MANUAL")
    print("Por favor, selecione o texto com os telefones e copie (Ctrl+C)")
    input("Pressione Enter quando tiver copiado os telefones...")
    
    texto = _obter_clipboard()
    
    if texto:
        # Extrai telefones do texto
        padrao = re.compile(r'(?:\+55|55)?\s*\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}')
        matches = padrao.findall(texto)
        
        telefones = []
        for match in matches:
            telefone_limpo = re.sub(r'[^\d+]', '', match)
            if len(telefone_limpo) >= 10:
                telefones.append({
                    'telefone': telefone_limpo,
                    'telefone_formatado': match,
                    'contexto': 'captura manual'
                })
        
        return telefones
    
    return []
#**************************************
def extrair_telefones_html(html: str) -> List[Dict]:
  """
  Extrai números de telefone do HTML
  """
  print("🔍 Extraindo telefones do HTML...")
  
  soup = BeautifulSoup(html, 'html.parser')
  
  # Padrões para encontrar telefones
  padrao_telefone = re.compile(
      r'(?:\+55|55)?\s*\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}',
      re.IGNORECASE
  )
  
  padrao_telefone_whatsapp = re.compile(
      r'(?:\+55|55)?\s*\(?\d{2}\)?\s*\d{4,5}[-\s]?\d{4}',
      re.IGNORECASE
  )
  
  telefones_encontrados = []
  
  # Busca em todo o texto
  textos = soup.find_all(string=True)
  
  for texto in textos:
      if texto.parent.name not in ['script', 'style', 'meta', 'title']:
          # Procura telefones no texto
          matches = padrao_telefone.findall(texto)
          for match in matches:
              telefone_limpo = re.sub(r'[^\d+]', '', match)
              if len(telefone_limpo) >= 10:
                  telefones_encontrados.append({
                      'telefone': telefone_limpo,
                      'telefone_formatado': match,
                      'contexto': texto.strip()[:100],
                      'fonte': 'texto'
                  })
  
  # Busca específica em elementos de mensagem
  mensagens = soup.find_all('div', class_=re.compile(r'message|text|copyable'))
  for msg in mensagens:
      texto_msg = msg.get_text(strip=True)
      matches = padrao_telefone.findall(texto_msg)
      for match in matches:
          telefone_limpo = re.sub(r'[^\d+]', '', match)
          if len(telefone_limpo) >= 10:
              telefones_encontrados.append({
                  'telefone': telefone_limpo,
                  'telefone_formatado': match,
                  'contexto': texto_msg[:100],
                  'fonte': 'mensagem'
              })
  
  # Busca em spans com números
  spans = soup.find_all('span', string=padrao_telefone)
  for span in spans:
      texto = span.get_text(strip=True)
      matches = padrao_telefone.findall(texto)
      for match in matches:
          telefone_limpo = re.sub(r'[^\d+]', '', match)
          if len(telefone_limpo) >= 10:
              telefones_encontrados.append({
                  'telefone': telefone_limpo,
                  'telefone_formatado': match,
                  'contexto': texto[:100],
                  'fonte': 'span'
              })
  
  # Remove duplicatas mantendo a ordem
  telefones_unicos = []
  seen = set()
  for tel in telefones_encontrados:
      if tel['telefone'] not in seen:
          seen.add(tel['telefone'])
          telefones_unicos.append(tel)
  
  telefones = telefones_unicos
  
  print(f"✅ Encontrados {len(telefones_unicos)} telefones únicos")
  return telefones_unicos
#*************************************
def extract_contacts_group(xfind,yfind,group):  
  import webbrowser
  try:
    cfg.cleanFile(localapp+'/ASW.log')#clean file log/Limpa o arquivo de log     
    url="https://web.whatsapp.com"
    webbrowser.open(url)    
  
    Eventos="...Iniciando a busca do grupo:"+group+"!/Begin get group"
    print(Eventos)
    uplog(Eventos) 
    visible_field = False
    #chama o metodo que localiza o campo pesquisar ou a lupa pesquisar
    visible_field = locate_search_field()
    #se o campo pesquisa foi encontrado ou o elemento de imagem svg (figura da lupa)    
    if visible_field:   
      # Simular o clique no elemento (ajustar as coordenadas conforme necessário)
      pygui.click(xfind, yfind,duration=3.5)#click no campo pescquisar
      Eventos="...click campo pesquisar!"
      uplog(Eventos)
      print(Eventos) 

      Eventos="Escrever o nome do grupo: "+group
      uplog(Eventos)
      print(Eventos)

      #time.sleep(random.randint(15,16))#espera o campo pesquisar
      #pygui.typewrite(group,interval=1.5)#escreve o nome do grupo no campo pesquisar
      '''
      # importando a biblioteca keyboard que possui suporte para teclas em português (acentuação)
      '''
      import platform      
      import keyboard as key 
      tpsystem = platform.system()
      from typing import List, Dict, Optional
      if tpsystem == 'nt':# se for windows
        key.write(group)#escreve o nome do grupo no campo pesquisar
      else:
        time.sleep(3)#Espera 3 segundos 
        
        pygui.hotkey('ctrl', 'a')
        Eventos = 'Seleciona todo o texto no campo atual'
        uplog(Eventos)
        print(Eventos)

        # Apaga o texto selecionado
        pygui.press('delete')
        Eventos = 'Apaga o texto selecionado com delete'
        uplog(Eventos)
        print(Eventos)

        import pyperclip
        
        pyperclip.copy(group)
        Eventos="# Copia para a memória do sistema (não exige sudo e funciona no Wayland)"
        uplog(Eventos)
        print(Eventos)

        # Cola dentro do Firefox usando o atalho universal
        time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos 
        pygui.hotkey("ctrl", "v")
        time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos 
        Eventos= "Cola dentro do Firefox usando o atalho universal"
        uplog(Eventos)
        print(Eventos)
        time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos 

      # Pressiona enter idependente do sistema operacional
      pygui.press('enter')
      time.sleep(random.randint(3,5))#Espera entre 3 a 5 segundos após o enter      
      Eventos="pressiona enter apoś o nome do grupo"
      uplog(Eventos)
      print(Eventos)

      #teste pegar o conteudo da página
      #?Eventos="...testando pegar o conteudo da página\u231B"#ampulheta
      #?print(Eventos)
      #?uplog(Eventos) 
      # pegar o conteudo da página para análise
      #?get_all_content_website(url)# não funciona mais descontinuido pois o whatsapp web ultiliza redenrizzação por javascript
      Eventos="Posicionando e clicando na barra abaixo do titulo do grupo para capturar lista de dados!"
      print(Eventos)
      uplog(Eventos) 
      pygui.click(x=620,y=157,duration=2)
       # Passo 4: Scroll para ver todos os participantes
      print("📜 Rolando para ver todos os participantes...")
      #**********************************
      '''
      for _ in range(5):
          pygui.scroll(-500)  # Scroll para baixo
          time.sleep(0.5)
      '''
 #******************************************
      def _salvar_resultados(telefones: List[Dict], nome_grupo: str):
        """
        Salva os telefones em arquivo
        """
        import json
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"telefones_{nome_grupo.replace(' ', '_')}_{timestamp}.json"
        
        # Salva como JSON
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            json.dump(telefones, f, ensure_ascii=False, indent=2)
        
        # Salva como TXT (apenas números)
        nome_txt = f"telefones_{nome_grupo.replace(' ', '_')}_{timestamp}.txt"
        with open(nome_txt, 'w', encoding='utf-8') as f:
            for tel in telefones:
                f.write(f"{tel['telefone']}\n")
        
        print(f"\n💾 Telefones salvos em:")
        print(f"  📄 {nome_arquivo} (JSON)")
        print(f"  📄 {nome_txt} (TXT)")
        
        # Mostra resumo
        print("\n📊 RESUMO:")
        print(f"  Total de telefones: {len(telefones)}")
        print("\n📋 Primeiros 10 telefones:")
        for i, tel in enumerate(telefones[:10], 1):
            print(f"  {i}. {tel['telefone_formatado']}")
        
        if len(telefones) > 10:
            print(f"  ... e mais {len(telefones) - 10} telefones")
      #******************************************
      # Passo 5: Capturar HTML
      html = capturar_tela_html()        
      if not html:
          print("❌ Falha ao capturar HTML")
          print("🔄 Tentando método alternativo...")
          return _capturar_manual() 
      
      # Passo 6: Extrair telefones
      telefones = extrair_telefones_html(html)   

      # Passo 7: Salvar resultados
      _salvar_resultados(telefones, group)

      pygui.press('esc')
      Eventos = "finalizado a extração de participantes com sucesso e precionando a tecla esc para limpar a seleção da tela !"
      uplog(Eventos)
      print(Eventos)
    else:
      Eventos = f"Timeout! Elemento (botão pesquisar) não foi encontrado nem pelo id nem pela classe em {run_time} segundos.\u26A0)"#Tringulo amarelo Alerta
      print(Eventos)
      uplog(Eventos)            
      pygui.hotkey('ctrl','f4')
      showmessage('Alert',Eventos)

  except Exception as e:
    # pegar o conteudo da página para análise
    get_all_content_website(url)

    Eventos="Exceção ao extrair dados  do grupo/Exception in extract data group!->"
    Eventos=Eventos+" ".join(e.args)
    uplog(Eventos)
    print(Eventos)    
    pygui.hotkey('ctrl','f4')
    showmessage('Alert',Eventos)
#*************************************