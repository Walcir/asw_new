import urllib.parse
import webbrowser
import os
import time
import pyautogui
import platform
from typing import Optional, List, Dict
import re

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

class WhatsAppSender:
    """
    Classe para enviar mensagens, imagens e documentos pelo WhatsApp Web
    Sem Selenium ou Playwright - usa navegador nativo
    """
    
    def __init__(self):
        self.base_url = "https://web.whatsapp.com/send"
        self.sistema = platform.system()
        self.tempo_espera = 5  # Tempo para carregar a página

    #**************************************************
    def verificar_svg_icon(self,url, termo_busca):
        """
        Verifica se existe um ícone SVG (inline ou via <use>)
        """
        headers = {"User-Agent": "Mozilla/5.0"}
        import requests
        from bs4 import BeautifulSoup

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
        print(f"   Total de <svg> encontrados: {len(svgs)}")
        return svg_encontrado
    #*************************************************** 
    
    # ============================================
    # MÉTODOS DE ENVIO BÁSICOS
    # ============================================

    def fechar_prompt_firefox(self):
        imagem_botao = 'botao_sair.png' # Substitua pelo caminho da sua imagem
        
        print("Aguardando o prompt do Firefox aparecer...")
        time.sleep(1) # Pausa para garantir que o menu apareceu na tela
        
        try:
            # Busca o botão na tela
            # confidence=0.8 ajuda caso haja pequenas variações nas cores
            posicao = pyautogui.locateCenterOnScreen(imagem_botao, confidence=0.8)
            
            if posicao is not None:
                # Move o mouse para o centro do botão e clica
                pyautogui.click(posicao)
                print("Botão 'Sair' pressionado com sucesso!")
            else:
                print("Botão não encontrado na tela.")
                
        except pyautogui.ImageNotFoundException:
            print("A imagem do botão não foi reconhecida na tela.")

    # ============================================
    # MÉTODOS PARA ENVIAR MENSAGEM DE TEXTO
    # ============================================
    def send_message(self, phone: str, message: str) -> bool:
        """
        Envia mensagem de texto pelo WhatsApp
        
        Args:
            phone: Número do telefone
            message: Mensagem a ser enviada
        
        Returns:
            bool: True se enviado com sucesso
        """
        from tools import update_log as uplog
        try:
            #?phone = self._limpar_numero(phone)
            # Limpa o número (remove espaços, parênteses, etc)   
            uplog(f"{EMOJI['aguardando']} Limpa o número (remove espações, parênteses, etc)")

            
            phone = ''.join(filter(str.isdigit,str(phone)))
            import urllib.parse
            #?message_encoded = urllib.parse.quote(str(message))
            # Codifica a mensagem para URL
            message_encoded = urllib.parse.quote(message)

            #??url = f"{self.base_url}?phone={phone}&text={message_encoded}"
            # Monta a URL
            url = f"https://web.whatsapp.com/send?phone={phone}&text={message_encoded}"
            
            uplog(f"📱 Abrindo WhatsApp para: {phone}")
            # Aguarda carregar
            import config as cfg
            cont = 0
            #correção para evitar o erro de conversão de um valor float para interio- força float e depois converte para inteiro
            timelogin = float(cfg.readcfg('config.ini','action','timeqrcode')) # 1-chrome(chromedriver) , 2-firefox , 3-EDge
            timelogin = round(timelogin)#arrendonda para o enteriro mais proximo
            webbrowser.open(url)
            while cont < (timelogin) :  
                cont = cont +1              
                uplog(f"...{cont} de  {timelogin} aguardando carregar página!")  
                #?time.sleep(self.tempo_espera)
                time.sleep(1) # type: ignore
             

            uplog("📤 Enviando mensagem...")
            #aguarda o envio da menssagem
            pyautogui.press('enter')                     
            
            timesendmsg = int(cfg.readcfg('config.ini','action','timesendmsg'))
            Eventos = 'Pegando o tempo de carregar envio da messagem e aguardando '+str(timesendmsg)                   
            uplog(Eventos) 
            contador=0
                       
            """Aguardando para confirmar o envio"""
            
            while ( contador < (timesendmsg) ):  
                contador = contador + 1    
                Eventos = f"{EMOJI['aguardando']} ...Aguardando em {contador} de {timesendmsg} para confirmar o envio!"              
                uplog(Eventos)
                time.sleep(1) # type: ignore  

            uplog("✅ Mensagem de texto enviada!")
                        
            uplog(f"{EMOJI['alerta']} fechando a aba do navegaor!")
            pyautogui.hotkey("alt","f4")
            time.sleep(1) # Aguarda o prompt
            pyautogui.press('enter') # Tenta confirmar com Enter

            '''
            tipo_nav = cfg.readcfg('config.ini','action','browser')
            if tipo_nav == '2':#se for firefox "Enter no botao desseja sair dessa página"
            '''            
            
            return True
            
        except Exception as e:
            uplog(f"❌ Erro ao enviar mensagem: {e}")
            return False
    
    # ============================================
    # MÉTODOS PARA ENVIAR IMAGENS
    # ============================================
    
    def send_image(self, phone: str, caminho_imagem: str, legenda: str = "") -> bool:
        """
        Envia uma imagem pelo WhatsApp Web
        
        Args:
            phone: Número do telefone
            caminho_imagem: Caminho da imagem no computador
            legenda: Texto opcional para acompanhar a imagem
        
        Returns:
            bool: True se enviado com sucesso
        """
        from tools import update_log as uplog
        try:
            # Verifica se a imagem existe
            if not os.path.exists(caminho_imagem):
                uplog(f"❌ Imagem não encontrada: {caminho_imagem}")
                return False
            else:
                uplog(f"🖼️ Enviando imagem: {os.path.basename(caminho_imagem)}")
            
            """
            Se o telefone estiver prenchido monta a url para enviar para o número;
            Caso seja para enviar para um grupo não precisa montar a url e reabrir o navegador,
            pois sendo o envio por grupo isso já foi feito anteriormente e é necessário apenas anexar o arquivo
            e prosseguir com o processo de envio
            """   
            # Abre o WhatsApp
            #phone = self._limpar_numero(phone)
            # Limpa o número (remove espaços, parênteses, etc)   
            phone = ''.join(filter(str.isdigit,str(phone)))
            self.base_url = "https://web.whatsapp.com/send"
            url = f"{self.base_url}?phone={phone}"
            #webbrowser.open(url)
            
            # Aguarda carregar
            self.tempo_espera = 5  # Tempo para carregar a página
            #?time.sleep(self.tempo_espera)
            
            # Aguarda carregar
            import config as cfg
            cont = 0
            timelogin = int(cfg.readcfg('config.ini','action','timeqrcode')) # 1-chrome(chromedriver) , 2-firefox , 3-EDge
            
            # se Não for um envio para um grupo ou seja se for por numero abre a url com o número
            if phone and phone !="":
                webbrowser.open(url)
                while cont < (timelogin) :  
                    cont = cont +1              
                    uplog(f"...{cont} de  {timelogin} aguardando carregar página!")                  
                    time.sleep(1) # type: ignore
            # *************************************************************
            # Abre o anexo (clip)
            uplog("📎 Abrindo anexo...")
            import config as cfg
            uplog('...lendo as posições das coordenadas x,y para click no sinal de + no WhatsApp')                   
            px = cfg.readcfg('config.ini','action','px_btn+')
            py = cfg.readcfg('config.ini','action','py_btn+')
            pyautogui.click(int(px),int(py),duration=1.5) # type: ignore # Posição do clip no WhatsApp
            time.sleep(self.tempo_espera)
            
            # Clica em "Fotos e Vídeos"
            uplog("📸 Selecionando Fotos e Vídeos...")
            #pyautogui.click(400, 350)  # Posição do botão "Fotos e Vídeos"
            px = cfg.readcfg('config.ini','action','px_btnimg')
            py = cfg.readcfg('config.ini','action','py_btnimg')
            pyautogui.click(int(px),int(py),duration=1.5) # type: ignore # Posição do clip no WhatsApp
            time.sleep(self.tempo_espera)
            
            # Clica no campo de seleção de arquivo
            uplog("📂 Selecionando arquivo...")
            TPwebdriver = 0
            TPwebdriver = int(cfg.readcfg('config.ini','action','browser'))  # 1-chrome(chromedriver) , 2-firefox , 3-EDge.
            uplog(f"Tipo de navegador = {TPwebdriver}")
            if (self.sistema == 'Linux' or self.sistema == 'linux') and TPwebdriver == 2:# se for linux e firefox   
                uplog("...presionando ctrl + l para abrir o campo e digitar o caminho do arquivo!")             
                pyautogui.hotkey('ctrl','l')# para abrir o campo para digitar o caminho do arquivo

            
            #?pyautogui.click(400, 300)  # Posição do campo de arquivo           
            
            # Digita o caminho da imagem
            pyautogui.write(message=caminho_imagem,interval=0.05)
            import random
                        
            # Pressiona Enter para selecionar
            Eventos=f"{EMOJI['processando']} pressiona end para final da linha digitada e aguarda 3 segundos"
            uplog(Eventos)
            pyautogui.keyDown('end')
            time.sleep(3)

            Eventos=f"{EMOJI['processando']} Press enter p/ confirma a linha digitada e aguarda entre 6 e 9 segundos"
            pyautogui.keyDown('enter')
            uplog(Eventos)
            time.sleep(random.randint(6,9))

            #Pegando o tempo para download/upload da imagem ou video
            time_upload = int(cfg.readcfg('config.ini','action','timeupimg')) 

            cont = 0
            while cont < (self.tempo_espera) :
                cont = cont +1
                uplog(f"{EMOJI['aguardando']}...{cont} de  {self.tempo_espera} aguardando copiar arquivo da memória!")                  
                time.sleep(1) # type: ignore
            
            # Adiciona legenda se fornecida
            if legenda:
                uplog(f"✏️ Adicionando legenda: {legenda}")
                pyautogui.write(legenda)
                uplog(f"...{cont} de  {self.tempo_espera} aguardando digitar a legenda do caminho do arquivo!")   
                time.sleep(self.tempo_espera)

            uplog(f"{EMOJI['processando']} Pressionando enter para confirmar o envio do arquivo!")
            pyautogui.press('enter')
            time.sleep(3) # type: ignore

            # Envia
            uplog(f"{EMOJI['processando']} Pressionando enter para forçar o envio do arquivo!")
            pyautogui.press('enter')
            time.sleep(random.randint(6,9))
            uplog("📤 Enviando imagem...")
            cont = 0
            while cont < (time_upload) :  
                cont = cont +1              
                uplog(f"...{cont} de  {time_upload} aguardando subir arquivo!")                  
                time.sleep(1) # type: ignore            
            
            uplog("fechando a aba do navegador!")
            pyautogui.hotkey("alt","f4")

            time.sleep(random.randint(3,6))
            uplog(f"{EMOJI['processando']} Pressionando enter para confirmar sair da janela")
            pyautogui.press('enter') # Tenta confirmar com Enter
            time.sleep(random.randint(2,4))

            uplog(f"✅ Imagem enviada para {phone}")
            return True
            
        except Exception as e:
            uplog(f"❌ Erro ao enviar imagem: {e}")
            return False
    
    # ============================================
    # MÉTODOS PARA ENVIAR DOCUMENTOS
    # ============================================
    
    def send_document(self, phone: str, caminho_documento: str, nome_arquivo: str = "", legenda: str = "") -> bool:
        """
        Envia um documento pelo WhatsApp Web
        
        Args:
            phone: Número do telefone
            caminho_documento: Caminho do documento no computador
            nome_arquivo: Nome a ser exibido (opcional)
            legenda: Texto opcional
        
        Returns:
            bool: True se enviado com sucesso
        """
        from tools import update_log as uplog
        try:
            import random

            # Verifica se o documento existe
            if not os.path.exists(caminho_documento):
                uplog(f"❌ Documento não encontrado: {caminho_documento}")
                return False
            
            if not nome_arquivo:
                nome_arquivo = os.path.basename(caminho_documento)
            
            uplog(f"📄 Enviando documento: {nome_arquivo}")

            """
            Se o telefone estiver prenchido monta a url para enviar para o número;
            Caso seja para enviar para um grupo não precisa montar a url e reabrir o navegador,
            pois sendo o envio por grupo isso já foi feito anteriormente e é necessário apenas anexar o arquivo
            e prosseguir com o processo de envio
            """   
            
                        # Limpa o telefone
            phone = ''.join(filter(str.isdigit, str(phone)))
            
            # Abre o WhatsApp Web
            url = f"https://web.whatsapp.com/send?phone={phone}"

            # Aguarda carregar
            import config as cfg
            cont = 0
            # se Não for um envio para um grupo ou seja se for por numero abre a url com o número
            if phone and phone !="":
                uplog(f"📱 Abrindo WhatsApp para {phone}")           
                webbrowser.open(url)
                #??timelogin = int(round(cfg.readcfg('config.ini','action','timeqrcode')) )# 1-chrome(chromedriver) , 2-firefox , 3-EDge
                from whatsappsender import WhatsAppSender as wsender
                timeqrcode =  round(float(cfg.readcfg('config.ini','action','timeqrcode')))
                '''
                sender_instance = wsender()#Crie uma instância da classe (com parênteses)
                wsender.esperar_pagina(self=sender_instance,tempo=int(timeqrcode)) # type: ignore
                '''
                while cont < timeqrcode:                    
                    cont= cont+1
                    time.sleep(1)
                    uplog(f"{EMOJI['aguardando']} ...Aguardando {cont} de {timeqrcode} para atualizar a pagina (login qrcode) para enviar documento!")
            else:
                return False
            # *************************************************************
            
            # Abre o anexo (clip)
            uplog("📎 Abrindo anexo...")
            #??pyautogui.click(700, 600)  # Posição do clip            
            uplog('...lendo as posições das coordenadas x,y para click no sinal de + no WhatsApp')                   
            px = cfg.readcfg('config.ini','action','px_btn+')
            py = cfg.readcfg('config.ini','action','py_btn+')
            pyautogui.click(int(px),int(py),duration=1.5) # type: ignore # Posição do clip no WhatsApp
            #?time.sleep(self.tempo_espera)
            time.sleep(random.randint(2,6))  
            
            # Clica em "Documento"
            uplog("📄 Selecionando Documento...")
            #pyautogui.click(400, 400)  # Posição do botão "Documento"
            time.sleep(random.randint(6,9))  # Aguarda o prompt
            px = cfg.readcfg('config.ini','action','px_btndoc')
            py = cfg.readcfg('config.ini','action','py_btndoc')
            pyautogui.click(int(px),int(py),duration=2.6) # type: ignore # Posição do botão "Documento"
            time.sleep(random.randint(6,9))  
            
            # Clica no campo de seleção de arquivo
            uplog("📂 Selecionando arquivo...")
            #?pyautogui.click(400, 300)  # Posição do campo de arquivo
            time.sleep(random.randint(6,9))    
            TPwebdriver = 0
            TPwebdriver = int(cfg.readcfg('config.ini','action','browser'))  # 1-chrome(chromedriver) , 2-firefox , 3-EDge.
            sistema = platform.system()
            uplog(f"{EMOJI['alerta']} sistema operacional = {sistema} e navegador = {TPwebdriver}")
            if (sistema == 'Linux' or sistema =='linux') and TPwebdriver == 2:# se for linux e firefox            
                time.sleep(random.randint(2,6))   
                uplog("...presionando ctrl + l para abrir o campo e digitar o caminho do arquivo!")             
                pyautogui.hotkey('ctrl','l')# para abrir o campo para digitar o caminho do arquivo
            
            # Digita o caminho do documento
            uplog(f"{EMOJI['processando']} Escrevendo o caminho do arquivo!")
            pyautogui.write(caminho_documento,interval=0.05)
            time.sleep(3)

            # Pressiona Enter para selecionar
            Eventos=f"{EMOJI['processando']} pressiona end para final da linha digitada e aguarda 3 segundos"
            uplog(Eventos)
            pyautogui.keyDown('end')
            time.sleep(1)

            Eventos=f"{EMOJI['processando']} Press enter p/ confirma a url e aguarda entre 6 e 9 segundos"
            pyautogui.keyDown('enter')
            uplog(Eventos)
            time.sleep(random.randint(6,9))

            # Adiciona legenda se fornecida
            uplog(f"Lengenda fornecida = {legenda}")
            cont=0
            if legenda!="":
                time.sleep(random.randint(2,6)) 
                uplog(f"✏️ Adicionando legenda: {legenda}")
                pyautogui.write(legenda,interval=0.05)
                time.sleep(random.randint(2,6)) 
                uplog(f"...aguardando digitar a legenda do caminho do arquivo!")   
                time.sleep(random.randint(2,6))

            # Envia
            uplog("📤 Enviando documento...")
            pyautogui.press('enter')
            time.sleep(random.randint(2,6)) 
            #Pegando o tempo para upload do arquivo
            time_upload = int(cfg.readcfg('config.ini','action','timeupimg')) 
            cont = 0
            while cont < (time_upload) :  
                cont = cont +1              
                uplog(f"...{cont} de  {time_upload} aguardando subir arquivo!")                  
                time.sleep(1) # type: ignore            
            
            pyautogui.press('enter') # Tenta confirmar com Enter
            time.sleep(random.randint(2,5))  # Aguarda o prompt
            uplog(f"✅ Documento enviado para {phone}")
            uplog("fechando a aba do navegador!")
            pyautogui.hotkey("alt","f4")
            return True
            
        except Exception as e:
            uplog(f"❌ Erro ao enviar documento: {' '.join(e.args)}")
            return False
    
    # ============================================
    # MÉTODOS PARA ENVIAR MÚLTIPLOS ARQUIVOS
    # ============================================
    
    def send_multiple_images(self, phone: str, imagens: List[str], legenda: str = "") -> bool:
        """
        Envia múltiplas imagens de uma vez
        
        Args:
            phone: Número do telefone
            imagens: Lista de caminhos das imagens
            legenda: Legenda para todas as imagens
        
        Returns:
            bool: True se enviado com sucesso
        """
        print(f"🖼️ Enviando {len(imagens)} imagens...")
        
        for i, img in enumerate(imagens, 1):
            print(f"\n📸 [{i}/{len(imagens)}] Enviando: {os.path.basename(img)}")
            
            if not self.send_image(phone, img, legenda):
                print(f"⚠️ Falha ao enviar imagem {i}")
            
            time.sleep(2)  # Pausa entre envios
        
        print("\n✅ Todas as imagens enviadas!")
        return True
    
    def send_multiple_documents(self, phone: str, documentos: List[str], legenda: str = "") -> bool:
        """
        Envia múltiplos documentos de uma vez
        
        Args:
            phone: Número do telefone
            documentos: Lista de caminhos dos documentos
            legenda: Legenda para todos os documentos
        
        Returns:
            bool: True se enviado com sucesso
        """
        print(f"📄 Enviando {len(documentos)} documentos...")
        
        for i, doc in enumerate(documentos, 1):
            print(f"\n📄 [{i}/{len(documentos)}] Enviando: {os.path.basename(doc)}")
            
            if not self.send_document(phone, doc, legenda=legenda):
                print(f"⚠️ Falha ao enviar documento {i}")
            
            time.sleep(2)  # Pausa entre envios
        
        print("\n✅ Todos os documentos enviados!")
        return True
    
    # ============================================
    # MÉTODO PARA ENVIAR POR TIPO DE ARQUIVO
    # ============================================
    
    def send_file(self, phone: str, caminho_arquivo: str, legenda: str = "") -> bool:
        """
        Envia qualquer tipo de arquivo (detecta automaticamente o tipo)
        
        Args:
            phone: Número do telefone
            caminho_arquivo: Caminho do arquivo
            legenda: Legenda opcional
        
        Returns:
            bool: True se enviado com sucesso
        """
        if not os.path.exists(caminho_arquivo):
            print(f"❌ Arquivo não encontrado: {caminho_arquivo}")
            return False
        
        # Detecta o tipo de arquivo pela extensão
        extensao = os.path.splitext(caminho_arquivo)[1].lower()
        
        # Extensões de imagem
        if extensao in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']:
            return self.send_image(phone, caminho_arquivo, legenda)
        
        # Extensões de documento
        elif extensao in ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt', '.csv']:
            return self.send_document(phone, caminho_arquivo, legenda=legenda)
        
        # Outros arquivos (envia como documento)
        else:
            print(f"📄 Tipo não identificado, enviando como documento...")
            return self.send_document(phone, caminho_arquivo, legenda=legenda)
    
    # ============================================
    # MÉTODOS AUXILIARES
    # ============================================
    
    def _limpar_numero(self, phone: str) -> str:
        """Limpa e formata o número de telefone"""
        phone = re.sub(r'[^\d]', '', str(phone))
        
        if not phone.startswith('55') and len(phone) >= 10:
            phone = f"55{phone}"
        
        return phone
    
    #def _esperar_pagina(self, tempo: int = 0):
    def esperar_pagina(self, tempo):
        """Aguarda a página carregar"""
        from tools import update_log as uplog
        if tempo is None:
            #?tempo = self.tempo_espera
            import config as cfg            
            tempo = 0
            '''
            #correção converter para intero arrendodando o valor float
            #  com casas decimais para o inteiro mais próximo
            '''
            #tempo  = int(cfg.readcfg('config.ini','action','timeqrcode'))
            tempo  = int(round(cfg.readcfg('config.ini','action','timeqrcode')))

        print(f"{EMOJI['aguardando']} Temo de espera de: {tempo}")
        cont = 0        
        while cont < round(float(tempo)):# o round arredonda o valor float para o inteiro mais proximo
            cont = cont +1
            print(f'{EMOJI['aguardando']} Aguardando a página carregar em: {cont} de {tempo}')
            time.sleep(1)        

    # ============================================
    # FUNÇÕES SIMPLIFICADAS
    # ============================================

    def enviar_imagem(self,phone: str, caminho_imagem: str, legenda: str = ""):
        """
        Função simplificada para enviar imagem
        
        Exemplo:
            enviar_imagem("83999050093", "/home/usuario/foto.jpg", "Olá!")
        """
        sender = WhatsAppSender()
        return sender.send_image(phone, caminho_imagem, legenda)


    def enviar_documento(self,phone: str, caminho_documento: str, legenda: str = ""):
        """
        Função simplificada para enviar documento
        
        Exemplo:
            enviar_documento("83999050093", "/home/usuario/relatorio.pdf", "PDF anexo")
        """
        sender = WhatsAppSender()
        return sender.send_document(phone, caminho_documento, legenda)


    def enviar_arquivo(self,phone: str, caminho_arquivo: str, legenda: str = ""):
        """
        Função simplificada para enviar qualquer arquivo
        
        Exemplo:
            enviar_arquivo("83999050093", "/home/usuario/imagem.jpg")
        """
        sender = WhatsAppSender()
        return sender.send_file(phone, caminho_arquivo, legenda)


    # ============================================
    # FUNÇÃO COMPLETA COM AUTO-DETECÇÃO
    # ============================================

    def enviar_para_whatsapp(self,phone , arquivo, mensagem):
        """
        Função completa que envia mensagem e/ou arquivo
        
        Args:
            phone: Número do telefone
            arquivo: Caminho do arquivo (imagem, documento, etc)
            mensagem: Mensagem de texto
        """
        try:
            sender = WhatsAppSender()
        
            print("\n" + "="*50)
            print("📱 ENVIANDO PARA WHATSAPP")
            print("="*50)
            
            if mensagem and not arquivo:
                # Apenas mensagem
                return sender.send_message(phone, mensagem)
            
            elif arquivo and not mensagem:
                # Apenas arquivo
                return sender.send_file(phone, arquivo)
            
            elif arquivo and mensagem:
                # Mensagem + arquivo
                print("📤 Enviando mensagem e arquivo...")
                
                # Primeiro envia a mensagem
                sender.send_message(phone, mensagem)
                time.sleep(2)
                
                # Depois envia o arquivo
                return sender.send_file(phone, arquivo)
            
            else:        
                print("❌ Nada para enviar!")

            return False
        except Exception as e:
            print("whatsappsender.py->Exception->enviar_para_whatsapp:\n"+"".join(e.args))
        
    


# ============================================
# EXEMPLO DE USO
# ============================================
'''
if __name__ == "__main__":
    
    print("="*60)
    print("📱 ENVIADOR DE MENSAGENS, IMAGENS E DOCUMENTOS")
    print("="*60)
    
    # Configurações
    phone = "83999050093"  # Substitua pelo número desejado
    
    # ============================================
    # EXEMPLO 1: Enviar imagem
    # ============================================
    print("\n🔹 EXEMPLO 1: Enviar imagem")
    
    caminho_imagem = "/home/usuario/foto.jpg"  # Substitua pelo caminho real
    
    # Verifica se a imagem existe
    if os.path.exists(caminho_imagem):
        enviar_imagem(phone, caminho_imagem, "Olá! Esta é uma imagem de teste.")
    else:
        print(f"⚠️ Imagem não encontrada: {caminho_imagem}")
        print("💡 Crie um arquivo de teste ou use um caminho existente")
    
    # ============================================
    # EXEMPLO 2: Enviar documento PDF
    # ============================================
    print("\n🔹 EXEMPLO 2: Enviar documento PDF")
    
    caminho_pdf = "/home/usuario/documento.pdf"  # Substitua pelo caminho real
    
    if os.path.exists(caminho_pdf):
        enviar_documento(phone, caminho_pdf, "Documento em PDF anexo")
    else:
        print(f"⚠️ PDF não encontrado: {caminho_pdf}")
    
    # ============================================
    # EXEMPLO 3: Enviar múltiplas imagens
    # ============================================
    print("\n🔹 EXEMPLO 3: Enviar múltiplas imagens")
    
    imagens = [
        "/home/usuario/foto1.jpg",
        "/home/usuario/foto2.jpg",
        "/home/usuario/foto3.jpg"
    ]
    
    # Filtra apenas imagens que existem
    imagens_existentes = [img for img in imagens if os.path.exists(img)]
    
    if imagens_existentes:
        sender = WhatsAppSender()
        sender.send_multiple_images(phone, imagens_existentes, "Fotos do evento")
    else:
        print("⚠️ Nenhuma imagem encontrada")
    
    # ============================================
    # EXEMPLO 4: Enviar arquivo por tipo
    # ============================================
    print("\n🔹 EXEMPLO 4: Enviar arquivo (detecta automaticamente)")
    
    arquivo = "/home/usuario/planilha.xlsx"  # Substitua pelo caminho real
    
    if os.path.exists(arquivo):
        enviar_arquivo(phone, arquivo, "Planilha com dados atualizados")
    else:
        print(f"⚠️ Arquivo não encontrado: {arquivo}")
    
    # ============================================
    # EXEMPLO 5: Enviar tudo (mensagem + arquivo)
    # ============================================
    print("\n🔹 EXEMPLO 5: Enviar mensagem + arquivo")
    
    mensagem = "Olá! Segue o arquivo solicitado."
    arquivo = "/home/usuario/relatorio.docx"  # Substitua
    
    if os.path.exists(arquivo):
        enviar_para_whatsapp(phone, arquivo, mensagem)
    else:
        print(f"⚠️ Arquivo não encontrado: {arquivo}")
    
    # ============================================
    # EXEMPLO 6: Criar arquivo de teste
    # ============================================
    print("\n🔹 EXEMPLO 6: Criando arquivos de teste")
    
    # Cria um arquivo de texto de teste
    with open("teste_whatsapp.txt", "w") as f:
        f.write("Este é um arquivo de teste para o WhatsApp\n")
        f.write("Data: " + time.strftime("%d/%m/%Y %H:%M:%S"))
    
    print("✅ Arquivo de teste criado: teste_whatsapp.txt")
    
    # Tenta enviar o arquivo de teste

    enviar_documento(phone, "teste_whatsapp.txt", "Arquivo de teste")
'''
