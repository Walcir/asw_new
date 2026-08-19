# -*- coding: utf-8 -*-
"""
campanhas.py - Gerenciamento de campanhas (GUI Modal com tema azul WhatsApp Web)
Mantém toda a lógica de negócio original
"""
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import messagebox as msgbx
from tkinter import filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

import config as cfg
import databases as db
import tools as tls
from ui_base import (ModalWindow, Colors, Icons, CardFrame,
                     show_info, show_warning, ask_yes_no, safe_int, safe_float)

# ============================================================
# 🌍 VARIÁVEIS GLOBAIS (mantidas da versão original)
# ============================================================
dtini = ''
clickcontact = 0
namecontact = ''
fonecontact = ''
clickgroup = 0
namegrp_add = ''
filejson = ''
bodyemail = ''
saudatemp = 'N'
saudaName = 'N'
ckb_saudaname = None
pnlconscontact = None
is_sendcamp = False

EMOJI = {
    "alerta": "️", "erro": "❌", "buscando": "🔍",
    "ok": "✅", "enviando": "", "processando": "⚙️",
    "lendo": "📖", "aguardando": "⏳",
}


# ============================================================
# 🛠️ FUNÇÃO AUXILIAR: Cria Frame com Scroll (Padrão main.py)
# ============================================================
def create_scrollable_frame(parent, bg_color=Colors.BG_MAIN):
    """Cria container com Canvas e Scrollbar usando padrão robusto"""
    canvas = tk.Canvas(parent, bg=bg_color, highlightthickness=0)
    scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=bg_color)
    
    scroll_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=canvas.winfo_width())
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))
    
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind("<Enter>", lambda _: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))
    
    return scroll_frame


# ============================================================
# 📋 FUNÇÕES DE LÓGICA DE NEGÓCIO (mantidas do original)
# ============================================================

def showmessage(Title, message):
    """Exibe caixa de mensagem"""
    msgbx.showinfo(Title, message)


def format_date(strdate):
    """Formata data dd/mm/yyyy"""
    try:
        dtnow = datetime.now()
        datacad = str(datetime.strftime(dtnow, '%d/%m/%Y %H:%M'))
        if strdate == '':
            strdate = datacad
        else:
            strdate = strdate.replace('/', '')
            if len(strdate) >= 13:
                strdate = strdate[0:14]
            if len(strdate) >= 8:
                strdate = strdate[:2] + '/' + strdate[2:4] + '/' + strdate[4:len(strdate)]
        return strdate
    except Exception as e:
        print(e)
        return strdate


def choseFile():
    """Seleciona arquivo"""
    resultfpath = ''
    try:
        resultfpath = str(filedialog.askopenfilename())
    except Exception:
        resultfpath = str(filedialog.askopenfilename())
    print('filechose is:', resultfpath)
    return resultfpath


def checkalertcamp(isNow):
    """Verifica se existe campanha agendada e envia"""
    from tools import update_log as uplog
    dtnow = datetime.now()
    idcamp = 0
    Numero = ""
    navegador = None
    Eventos = ''
    localapp = os.getcwd()
    cfg.cleanFile(localapp + '/ASW.log')
    
    dtlocal = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
    Eventos = "...checando se existe campanha pendente "
    uplog(Eventos)
    
    con_camp = []
    
    if isNow == 's' or isNow == 'S':
        con_camp = db.consulttablesql(
            db.csqllite,
            "idcampanhas,nomecampanhas,dthcadastrocampanhas,msgcampanhas,imgcampanhas," +
            "doccampanhas,ativocampanhas,dthdispararcampanhas,enviada,saudatemp,saudaNome",
            "campanhas",
            f" where idcampanhas == {str(cfg.clickId)}" +
            " and ativocampanhas =  'S'  and (enviada =  'N') ","" )
    else:
        con_camp = db.consulttablesql(
            db.csqllite,
            "idcampanhas,nomecampanhas,dthcadastrocampanhas,msgcampanhas,imgcampanhas," +
            "doccampanhas,ativocampanhas,dthdispararcampanhas,enviada,saudatemp,saudaNome",
            "campanhas",
            f" where ativocampanhas =  'S'  and (enviada =  'N') ",
            f" order by dthdispararcampanhas ")
        '''
            f" where ativocampanhas =  'S'  and (enviada =  'N') "+
            f"and cast(substr(dthdispararcampanhas,7,4)as integer) <= cast(strftime('%Y', 'now')as integer)" +
            f"and cast(substr(dthdispararcampanhas,4,2)as integer) <=cast(strftime('%m', 'now')as integer)" +
            f"and cast(substr(dthdispararcampanhas,1,2)as integer)=cast(strftime('%d', 'now')as integer)" +
            f"and cast(substr(dthdispararcampanhas,12,2)as integer)==cast(strftime('%H', 'now')as integer)" +
            f"and cast(substr(dthdispararcampanhas,15,15)as integer)==cast(strftime('%M', 'now')as integer)", "")
        '''

    if (con_camp != [] and con_camp != None):
        for y in con_camp:
            for x in range(len(y)):
                dt = y[7]
                print("get date dispare-> ", dt)
        
        db.con_camp = con_camp
        #verifica se o vencimento do sistema  venceu
        if not (cfg.VerifyVencdate(datetime.now(), cfg.dtvenclicense) ):
            showmessage('Atencao!', 'Existe envio agendada de campanha pendente,mas não poderá ser enviada,Verifique sua licença!')
        else:
            idcamp = 0
            TPwebdriver = int(cfg.readcfg('config.ini', 'action', 'browser'))
            localapp = os.getcwd()

            localapp = localapp.replace('\\', '/')
            
            import rpa
            Eventos = "...buscando o tempo de leitura qrcode login!"
            uplog(Eventos)
            timeqrcode = cfg.readcfg('config.ini', 'action', 'timeqrcode')
            
            global bodyemail
            for cp in con_camp:
                idcamp = 0
                Msg = ''
                Doc = ''
                Img = ''
                saudatemp = 'N'
                saudaName = 'N'
                Namecamp = ''
                for i in range(len(cp)):
                    if (i == 0): idcamp = cp[i]
                    if (i == 1): Namecamp = cp[i]
                    if (i == 3): Msg = cp[i]
                    if (i == 4):
                        Img = str(cp[i])
                        Eventos = "Imagem da campanha->" + Img
                    uplog(Eventos)
                    if (i == 5):
                        Doc = str(cp[i])
                        Eventos = "Documento da campanha->" + Doc
                        uplog(Eventos)
                    if (i == 9): saudatemp = cp[i]
                    if (i == 10): saudaName = cp[i]
                
                Eventos = 'Consultando os dados dos contatos para a campanha'
                uplog(Eventos)
                global filejson
                filejson = localapp + '/' + Namecamp + '.json'
                
                rs_concontact = db.consulttablesql(
                    db.csqllite,
                    ' idcontatos,nomecontato,fonecontato,nomegrupocontato,datacad,emailcontato,ativocontato,eclientecontato ',
                    ' itenscamp,contatos ',
                    ' where idcoditcamp ="' + str(idcamp) + '" and iditcontcamp = idcontatos',
                    ' order by nomecontato;')
                
                if (rs_concontact != [] and rs_concontact != None):
                    db.con_contactCamp = rs_concontact
                    Id = ''
                    Numero = ''
                    Nome = ''
                    cont = 0
                    for c in rs_concontact:
                        try:
                            cont = cont + 1
                            for x in range(len(c)):
                                if (x == 0): Id = c[x]
                                if (x == 1): Nome = str(c[x])
                                if (x == 2): Numero = c[x]
                            
                            if saudaName == 'S': cfg.saudaName = saudaName
                            if saudatemp == 'S': cfg.saudatemp = saudatemp
                            # se o vencimento do está válido
                            if (cfg.VerifyVencdate(datetime.now(), cfg.dtvenclicense) == True):
                                cfg.idcamp = idcamp
                                Eventos = f"...{EMOJI['aguardando']} Fist send camp!/Iniciando o envio da campanha ao contato !"
                                uplog(Eventos)
                                
                                global saudatime
                                saudatime = ""
                                hora_atual = time.strftime('%H', time.localtime())
                                if saudaName == "S":
                                    hora_atual = time.strftime('%H', time.localtime())
                                    print('time is it? ', hora_atual)
                                if int(hora_atual) < 12:
                                    saudatime = ' Bom dia! '
                                elif int(hora_atual) >= 12 and int(hora_atual) <= 18:
                                    saudatime = ' Boa tarde! '
                                else:
                                    saudatime = ' Boa noite! '
                                
                                timeupload = cfg.readcfg('config.ini', 'action', 'timeqrcode')
                                Oksendmsg = False
                                
                                if Msg != None and Msg != "":
                                    from whatsappsender import WhatsAppSender as wsender
                                    sender_instance = wsender()
                                    Oksendmsg = wsender.send_message(self=sender_instance, phone=Numero, message=saudatime + Msg)
                                    
                                    if Oksendmsg == True:
                                        if Doc != "" and Doc != None:
                                            Eventos = f"{EMOJI['enviando']} Enviando documento/Send file doc"
                                            uplog(Eventos)
                                            wsender.send_document(self=sender_instance, phone=Numero, caminho_documento=Doc, nome_arquivo="", legenda="")
                                        if Img != "" and Img != None:
                                            Eventos = f"{EMOJI['enviando']} Enviando imagem/send image"
                                            uplog(Eventos)
                                            wsender.enviar_imagem(self=sender_instance, phone=Numero, caminho_imagem=Img, legenda="")
                                        Oksendmsg = False
                        except Exception as e:
                            Eventos = f"{EMOJI['erro']}Exceção ao enviar para ->" + str(Numero) + " \n" + "".join(e.args)
                            uplog(Eventos)
                            import pyautogui as pygui
                            pygui.hotkey('ctrl', 'f4')
                            continue
                    
                    setlistfields = " enviada = 'S' "
                    condition = ' idcampanhas = ' + str(idcamp)
                    db.updatetablesql(db.csqllite, "campanhas", setlistfields, condition)
                    
                    if cfg.is_sendcamp == True:
                        Eventos = f"{EMOJI['ok']} campanha processada com sucesso!"
                    uplog(Eventos)
        
        Eventos = ""
        if (Msg != None and Msg != "") or (Img != None and Img != "") or (Doc != None and Doc != ""):
            Eventos = f"{EMOJI['alerta']} Processo de envio da campanha finalizada,Verifique o log de processamento!"
            exite_grupo = False
            exite_grupo = checkalertgroupcamp(idcamp=idcamp)
            if exite_grupo:
                uplog("Ok exite grupo(s) para essa campanha!")
                from rpa import sendgroup
                from config import readcfg
                uplog("Pegando as posições do campo de busca")
                xfind = readcfg('config.ini','action','px_fieldfind')
                yfind = readcfg('config.ini','action','py_fieldfind')
                uplog('Buscando no bd o(s) grupo(s) para ser(em) enviado(s)!')

                con_group =[]
                con_group =db.consulttablesql(db.csqllite,' iditcampgp,idcampgp,itnamegp ','icampgp',f'WHERE idcampgp={idcamp}','ORDER BY iditcampgp')
                if (con_group != [] and con_group != None):
                    group=''#limpa o nome do grupo
                    for y in con_group:
                        for x in range(len(y)):
                            uplog(f"...pegando o(s) valor(es) do(s) grupo(s)")
                            uplog(f"Na posição {x} o valor e {y[x]}")
                            if(x==2):# se chegar na posição do nome do group, atribui a variavel
                                group=str(y[x])

                            uplog(f"...enviado para o grupo {group} !")    
                            sendgroup(xfind=int(xfind),yfind=int(yfind),
                                      Img=Img,Doc=Doc,
                                      Msg=Msg,
                                      idcamp=idcamp,group=group)
            else:
                uplog("Não existe grupo(s) para campanha!")
        else:
            Eventos = f"{EMOJI['alerta']} Não enviada.Dados da campanha incosistêntes,Favor revisar o log de processamento!"
            uplog(Eventos)
            showmessage("Alerta", Eventos)

        import pyautogui as pygui
        pygui.hotkey('alt', 'f4')
    else:
        Eventos = "Não Existe campanha pendente a ser enviada!"
        print(Eventos)
        uplog(Eventos=Eventos)


def checkalertgroupcamp(idcamp):
    """Checa se existe grupo(s) para essa campanha"""
    rs = []
    rs = db.consulttablesql(db.csqllite, "i.iditgrupogp,i.itnamegp,g.dtgrp",
                            f" icampgp as i left join grp as g on(g.idgrp=i.iditgrupogp)",
                            f"where i.idcampgp = {str(idcamp)}", "")
    if rs != [] and rs != None:
        return True
    else:
        return False


def ifexistcontactincamp(itidcamp, idcontact):
    """Consulta se contato existe na campanha"""
    rs = []
    rs = db.consulttablesql(db.csqllite, '  iditcontcamp,idcoditcamp,idcampanhas,nomecampanhas ',
                            ' itenscamp,campanhas ',
                            ' where iditcontcamp = "' + str(idcontact) + '" and idcampanhas =' + str(itidcamp) + ' and idcoditcamp =idcampanhas ', ' ;')
    if rs != [] and rs != None:
        return True
    else:
        return False


def importmsg():
    """Importa mensagem de arquivo txt"""
    localapp = os.getcwd()

    texto = ''
    filetxt = str(filedialog.askopenfilename(filetypes=[("text files", "*.txt")]))
    global text_msgcamp
    text_msgcamp.delete(1.0, END)
    with open(filetxt, 'r', errors='ignore', encoding="utf-8") as f:
        datacfg = f.readlines()
        for line in datacfg:
            print(line)
            text_msgcamp.insert(END, line + '\n')


def del_camp(idcamp):
    """Exclui campanha"""
    try:
        result = msgbx.askquestion('Alerta ', 'Tem certeza que realmente quer deletar essa campanha?')
        if result == 'yes':
            db.deletetablesql(db.csqllite, 'campanhas', '', ' where idcampanhas=' + str(idcamp))
            showmessage('Confirmado ', "Campanha excluido com sucesso,para atualizar feche e abra essa tela novamente!")
            db.csqllite.connection.commit()
    except Exception as e:
        print("Error occurred: in def del_camp", e)
        print('Tipo: ', type(e))
        print('Arqgumentos: ', e.args)


# ============================================================
# 📋 PONTO DE ENTRADA
# ============================================================
def menu_Showcamp(parent=None):
    """Abre a janela principal de campanhas"""
    CampaignsWindow(parent)


# ============================================================
# 📋 JANELA PRINCIPAL DE CAMPANHAS
# ============================================================
class CampaignsWindow(ModalWindow):
    """Janela principal de campanhas com abas - Tema Azul WhatsApp Web"""
    
    def __init__(self, parent=None):
        super().__init__(parent, title="📋 Gerenciar Campanhas", width=1200, height=750)
        self.selected_campaign_id = None
        self._build_ui()
        self._load_campaigns()
        
    def _build_ui(self):
        """Constrói interface com abas"""
        notebook = ttkb.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Aba 1: Campanha Única
        tab1 = tk.Frame(notebook, bg=Colors.BG_MAIN)
        notebook.add(tab1, text=f" {Icons.CAMPAIGN} Campanha Única ")
        self._build_tab_unica(tab1)
        
        # Aba 2: Campanha Diversificada
        tab2 = tk.Frame(notebook, bg=Colors.BG_MAIN)
        notebook.add(tab2, text=f" {Icons.MESSAGE} Diversificada ")
        self._build_tab_diversificada(tab2)
        
        # Aba 3: Log
        tab3 = tk.Frame(notebook, bg=Colors.BG_MAIN)
        notebook.add(tab3, text=f" {Icons.LOG} Log ")
        self._build_tab_log(tab3)

    
    def _build_tab_unica(self, parent):
        """Aba de campanha única com layout grid e painel direito scrollável"""
        # Container principal com grid
        split = tk.Frame(parent, bg=Colors.BG_MAIN)
        split.pack(fill="both", expand=True)
        split.grid_columnconfigure(0, weight=3)  # Lista ocupa mais espaço
        split.grid_columnconfigure(1, weight=1)  # Painel direito
        split.grid_rowconfigure(0, weight=1)
        
        # ===== LADO ESQUERDO: Lista de Campanhas =====
        list_frame = tk.Frame(split, bg=Colors.BG_WHITE, relief="solid", bd=1)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        list_header = tk.Frame(list_frame, bg=Colors.BG_WHITE, height=50)
        list_header.grid(row=0, column=0, sticky="ew")
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text=f"{Icons.CAMPAIGN} Campanhas",
                font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left", padx=15, pady=12)
        
        ttkb.Button(list_header, text=f"{Icons.ADD} Nova campanha", style="success.TButton",
                   command=self._add_campaign).pack(side="right", padx=10, pady=8)

        #evento para o botão novo grupo
        def _show_config_group():
            import ttkbootstrap as ttk
            import groupcontacts as grp
            app = ttk.Window(
                title="Grupo de contatos para campanha",
                size=(400, 600)              
            )            
          
            grp.ContactBook(app).pack(fill="x")


            #app.mainloop()

        ttkb.Button(list_header, text=f"{Icons.CONFIG} configurar grupos", style="success.TButton",
                           command=_show_config_group).pack(side="right", padx=10, pady=8)

        # Treeview
        tree_frame = tk.Frame(list_frame, bg=Colors.BG_WHITE)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        columns = ("id", "nome", "cadastro", "msg", "ativo", "disparo", "enviada")
        self.tree_camp = ttkb.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree_camp.heading("id", text="ID"); self.tree_camp.column("id", width=40, anchor="center")
        self.tree_camp.heading("nome", text="Nome"); self.tree_camp.column("nome", width=150)
        self.tree_camp.heading("cadastro", text="Cadastro"); self.tree_camp.column("cadastro", width=100)
        self.tree_camp.heading("msg", text="Mensagem"); self.tree_camp.column("msg", width=200)
        self.tree_camp.heading("ativo", text="Ativo"); self.tree_camp.column("ativo", width=50, anchor="center")
        self.tree_camp.heading("disparo", text="Disparo"); self.tree_camp.column("disparo", width=100)
        self.tree_camp.heading("enviada", text="Enviada"); self.tree_camp.column("enviada", width=60, anchor="center")
        
        scrollbar_y = ttkb.Scrollbar(tree_frame, orient="vertical", command=self.tree_camp.yview)
        self.tree_camp.configure(yscrollcommand=scrollbar_y.set)
        self.tree_camp.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree_camp.bind("<<TreeviewSelect>>", self._on_select_campaign)
        
        # ===== LADO DIREITO: Painel com Scroll (botões + contatos + grupos) =====
        right_panel_outer = tk.Frame(split, bg=Colors.BG_MAIN, width=380)
        right_panel_outer.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel_outer.pack_propagate(False)
        
        # Usa a função auxiliar robusta para scroll no painel direito INTEIRO
        scroll_frame = create_scrollable_frame(right_panel_outer, bg_color=Colors.BG_MAIN)
        
        # Card: Ações
        btn_card = CardFrame(scroll_frame, title=f"{Icons.PLAY} Ações")
        btn_card.pack(fill="x", padx=10, pady=(10, 5))
        
        btn_frame = tk.Frame(btn_card, bg=Colors.BG_WHITE)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        buttons = [
            (f"{Icons.EDIT} Editar", "info.TButton", self._edit_campaign),
            (f"{Icons.DELETE} Excluir", "danger.TButton", self._delete_campaign),
            #(f"{Icons.ADD} Add 1 Contato", "success.TButton", self._add_contact_to_campaign),
            #(f"{Icons.ADD} Add Todos", "success.TButton", self._add_all_contacts),
            #(f"{Icons.DELETE} Remover Contato", "warning.TButton", self._remove_contact),
            (f"{Icons.IMPORT} Importar CSV", "warning.TButton", self._import_csv),
            #(f"{Icons.GROUP} Add Grupo", "info.TButton", self._add_group),
            (f"{Icons.PLAY} Enviar Agora", "success.TButton", self._send_now),
        ]
        
        for text, style, cmd in buttons:
            ttkb.Button(btn_frame, text=text, style=style, command=cmd).pack(fill="x", pady=3)
        
        # Card: Contatos
        contacts_card = CardFrame(scroll_frame, title=f"{Icons.CONTACT} Contatos")
        contacts_card.pack(fill="x", padx=10, pady=5)
        
        contacts_frame = tk.Frame(contacts_card, bg=Colors.BG_WHITE)
        contacts_frame.pack(fill="x", padx=10, pady=10)
        
        self.tree_contacts = ttkb.Treeview(contacts_frame, columns=("id", "nome", "fone"), show="headings", height=6)
        self.tree_contacts.heading("id", text="ID"); self.tree_contacts.column("id", width=40, anchor="center")
        self.tree_contacts.heading("nome", text="Nome"); self.tree_contacts.column("nome", width=140)
        self.tree_contacts.heading("fone", text="Fone"); self.tree_contacts.column("fone", width=120)
        self.tree_contacts.pack(fill="x")
        
        self.lbl_contact_count = tk.Label(contacts_card, text="0 contatos", font=("Segoe UI", 9),
                                          bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY)
        self.lbl_contact_count.pack(pady=(0, 10))

        #Botoes para ações dos contatos:
        ttkb.Button(contacts_card, text=f"{Icons.ADD} Add 1 Contato", style="primary.TButton",
        command=self._add_contact_to_campaign).pack(fill="x", padx=10, pady=8)
        
        ttkb.Button(contacts_card, text=f"{Icons.DELETE} Remover 1 Contato",
        bootstyle="danger",
        command=self._remove_contact).pack(fill="x", padx=10, pady=8)
        
        ttkb.Button(contacts_card, text=f"{Icons.ADD} Add Todos",
        bootstyle="success",
        command=self._add_all_contacts).pack(fill="x", padx=10, pady=8)

        #(f"{Icons.IMPORT} Importar CSV", "warning.TButton", self._import_csv),
        ttkb.Button(contacts_card, text=f"{Icons.ADD} Importar de CSV",
        bootstyle="warning",
        command=self._import_csv).pack(fill="x", padx=10, pady=8)
        
        # Card: Grupos (SEPARADO abaixo de Contatos)
        groups_card = CardFrame(scroll_frame, title=f"{Icons.GROUP} Grupos")
        groups_card.pack(fill="x", padx=10, pady=5)
        
        groups_frame = tk.Frame(groups_card, bg=Colors.BG_WHITE)
        groups_frame.pack(fill="x", padx=10, pady=10)
        
        self.tree_groups = ttkb.Treeview(groups_frame, columns=("id", "nome", "data"), show="headings", height=5)
        self.tree_groups.heading("id", text="ID"); self.tree_groups.column("id", width=40, anchor="center")
        self.tree_groups.heading("nome", text="Nome"); self.tree_groups.column("nome", width=160)
        self.tree_groups.heading("data", text="Data"); self.tree_groups.column("data", width=100)
        self.tree_groups.pack(fill="x")
        
        self.lbl_group_count = tk.Label(groups_card, text="0 grupos", font=("Segoe UI", 9),
                                        bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY)
        self.lbl_group_count.pack(pady=(0, 10))

        #botoes para  grupo(s) da lista
        #(f"{Icons.GROUP} Add Grupo", "info.TButton", self._add_group),
        ttkb.Button(groups_card, text=f"{Icons.ADD} Add Grupo", style="primary.TButton",
                                    command=self._add_group).pack(fill="x", padx=10, pady=8)

        ttkb.Button(groups_card, text=f"{Icons.DELETE} Remover Grupo",
            bootstyle="danger",
            command=self._remove_group).pack(fill="x", padx=10, pady=8)
        
        # Espaço extra no final
        tk.Frame(scroll_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")
    
    def _build_tab_diversificada(self, parent):
        """Aba de campanha diversificada"""
        split = tk.Frame(parent, bg=Colors.BG_MAIN)
        split.pack(fill="both", expand=True, padx=5, pady=5)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=1)
        split.grid_rowconfigure(0, weight=1)
        
        # Lista
        list_frame = tk.Frame(split, bg=Colors.BG_WHITE, relief="solid", bd=1)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        list_header = tk.Frame(list_frame, bg=Colors.BG_WHITE, height=50)
        list_header.grid(row=0, column=0, sticky="ew")
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text=f"{Icons.MESSAGE} Campanhas Diversificadas",
                font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left", padx=15, pady=12)
        
        ttkb.Button(list_header, text=f"{Icons.ADD} Nova", style="success.TButton",
                   command=self._add_campaign_dv).pack(side="right", padx=10, pady=8)
        
        tree_frame = tk.Frame(list_frame, bg=Colors.BG_WHITE)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("id", "nome", "ativo", "dt_envio", "hr_envio", "min")
        self.tree_dv = ttkb.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree_dv.heading("id", text="ID"); self.tree_dv.column("id", width=40, anchor="center")
        self.tree_dv.heading("nome", text="Nome"); self.tree_dv.column("nome", width=150)
        self.tree_dv.heading("ativo", text="Ativo"); self.tree_dv.column("ativo", width=60, anchor="center")
        self.tree_dv.heading("dt_envio", text="Data Envio"); self.tree_dv.column("dt_envio", width=100)
        self.tree_dv.heading("hr_envio", text="Hora"); self.tree_dv.column("hr_envio", width=60, anchor="center")
        self.tree_dv.heading("min", text="Minuto"); self.tree_dv.column("min", width=60, anchor="center")
        
        scrollbar_y = ttkb.Scrollbar(tree_frame, orient="vertical", command=self.tree_dv.yview)
        self.tree_dv.configure(yscrollcommand=scrollbar_y.set)
        self.tree_dv.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree_dv.bind("<<TreeviewSelect>>", self._on_select_campaign_dv)
        
        # Painel direito com scroll
        right_panel_outer = tk.Frame(split, bg=Colors.BG_MAIN, width=300)
        right_panel_outer.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel_outer.pack_propagate(False)
        
        scroll_frame = create_scrollable_frame(right_panel_outer, bg_color=Colors.BG_MAIN)
        
        btn_card = CardFrame(scroll_frame, title=f"{Icons.PLAY} Ações")
        btn_card.pack(fill="x", padx=10, pady=10)
        
        btn_frame = tk.Frame(btn_card, bg=Colors.BG_WHITE)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        buttons = [
            (f"{Icons.EDIT} Editar", "info.TButton", self._edit_campaign_dv),
            (f"{Icons.DELETE} Excluir", "danger.TButton", self._delete_campaign_dv),
            (f"{Icons.IMPORT} Importar CSV", "warning.TButton", self._import_csv_dv),
            (f"{Icons.DELETE} Remover Todos", "warning.TButton", self._remove_all_contacts_dv),
            (f"{Icons.PLAY} Enviar Agora", "success.TButton", self._send_now_dv),
        ]
        for text, style, cmd in buttons:
            ttkb.Button(btn_frame, text=text, style=style, command=cmd).pack(fill="x", pady=3)
        
        tk.Frame(scroll_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")
    

    def _build_tab_config_group(self, parent):
        """Aba de configuração de grupo de market para campanha """
        split = tk.Frame(parent, bg=Colors.BG_MAIN)
        split.pack(fill="both", expand=True, padx=5, pady=5)
        split.grid_columnconfigure(0, weight=3)
        split.grid_columnconfigure(1, weight=1)
        split.grid_rowconfigure(0, weight=1)
        
        # Lista
        list_frame = tk.Frame(split, bg=Colors.BG_WHITE, relief="solid", bd=1)
        list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        
        list_header = tk.Frame(list_frame, bg=Colors.BG_WHITE, height=50)
        list_header.grid(row=0, column=0, sticky="ew")
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text=f"{Icons.MESSAGE} Configurar grupo de marketing para campanhas",
                font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left", padx=15, pady=12)
        
        ttkb.Button(list_header, text=f"{Icons.ADD} Nova", style="success.TButton",
                   command=self._add_campaign_dv).pack(side="right", padx=10, pady=8)
        
        tree_frame = tk.Frame(list_frame, bg=Colors.BG_WHITE)
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        columns = ("id", "nome", "ativo", "dt_envio", "hr_envio", "min")
        self.tree_dv = ttkb.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree_dv.heading("id", text="ID"); self.tree_dv.column("id", width=40, anchor="center")
        self.tree_dv.heading("nome", text="Nome"); self.tree_dv.column("nome", width=150)
        self.tree_dv.heading("ativo", text="Ativo"); self.tree_dv.column("ativo", width=60, anchor="center")
        self.tree_dv.heading("dt_envio", text="Data Envio"); self.tree_dv.column("dt_envio", width=100)
        self.tree_dv.heading("hr_envio", text="Hora"); self.tree_dv.column("hr_envio", width=60, anchor="center")
        self.tree_dv.heading("min", text="Minuto"); self.tree_dv.column("min", width=60, anchor="center")
        
        scrollbar_y = ttkb.Scrollbar(tree_frame, orient="vertical", command=self.tree_dv.yview)
        self.tree_dv.configure(yscrollcommand=scrollbar_y.set)
        self.tree_dv.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        self.tree_dv.bind("<<TreeviewSelect>>", self._on_select_campaign_dv)
        
        # Painel direito com scroll
        right_panel_outer = tk.Frame(split, bg=Colors.BG_MAIN, width=300)
        right_panel_outer.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        right_panel_outer.pack_propagate(False)
        
        scroll_frame = create_scrollable_frame(right_panel_outer, bg_color=Colors.BG_MAIN)
        
        btn_card = CardFrame(scroll_frame, title=f"{Icons.PLAY} Ações")
        btn_card.pack(fill="x", padx=10, pady=10)
        
        btn_frame = tk.Frame(btn_card, bg=Colors.BG_WHITE)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        buttons = [
            (f"{Icons.EDIT} Editar", "info.TButton", self._edit_campaign_dv),
            (f"{Icons.DELETE} Excluir", "danger.TButton", self._delete_campaign_dv),
            (f"{Icons.IMPORT} Importar CSV", "warning.TButton", self._import_csv_dv),
            (f"{Icons.DELETE} Remover Todos", "warning.TButton", self._remove_all_contacts_dv),
            (f"{Icons.PLAY} Enviar Agora", "success.TButton", self._send_now_dv),
        ]
        for text, style, cmd in buttons:
            ttkb.Button(btn_frame, text=text, style=style, command=cmd).pack(fill="x", pady=3)
        
        tk.Frame(scroll_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")
    
    def _build_tab_log(self, parent):
        """Aba de log"""
        toolbar = tk.Frame(parent, bg=Colors.BG_WHITE, height=50)
        toolbar.pack(fill="x", pady=(0, 5))
        toolbar.pack_propagate(False)
        
        ttkb.Button(toolbar, text=f"{Icons.REFRESH} Atualizar Log", style="primary.TButton",
                   command=self._load_log).pack(side="left", padx=10, pady=8)
        ttkb.Button(toolbar, text=f"{Icons.DELETE} Limpar", style="danger.TButton",
                   command=self._clear_log).pack(side="left", padx=5, pady=8)
        
        self.lbl_log_count = tk.Label(toolbar, text="0 linhas", font=("Segoe UI", 10),
                                      bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY)
        self.lbl_log_count.pack(side="right", padx=15)
        
        text_frame = tk.Frame(parent, bg=Colors.BG_WHITE, relief="solid", bd=1)
        text_frame.pack(fill="both", expand=True)
        
        self.text_log = tk.Text(text_frame, font=("Consolas", 10), bg="#1E1E1E", fg="#D4D4D4",
                                relief="flat", wrap="none", padx=10, pady=10)
        self.text_log.pack(fill="both", expand=True, padx=1, pady=1)
        
        vsb = ttkb.Scrollbar(text_frame, orient="vertical", command=self.text_log.yview)
        hsb = ttkb.Scrollbar(text_frame, orient="horizontal", command=self.text_log.xview)
        self.text_log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        vsb.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        hsb.place(relx=0.0, rely=1.0, relwidth=1.0, anchor="sw")
        self._load_log()

    # ============================================================
    # 📊 MÉTODOS DE CARREGAMENTO
    # ============================================================
    def _load_campaigns(self):
        """Carrega campanhas"""
        self.tree_camp.delete(*self.tree_camp.get_children())
        try:
            campaigns = db.consulttablesql(
                db.csqllite,
                'idcampanhas,nomecampanhas,dthcadastrocampanhas,msgcampanhas,ativocampanhas,dthdispararcampanhas,enviada',
                'campanhas', ' ', ' ')
            if campaigns:
                for c in campaigns:
                    self.tree_camp.insert("", "end", values=c)
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao carregar campanhas:\n{e}")
    
    def _on_select_campaign(self, event):
        """Handler de seleção de campanha"""
        selection = self.tree_camp.selection()
        if not selection:
            return
        values = self.tree_camp.item(selection[0], "values")
        self.selected_campaign_id = values[0]
        cfg.clickId = self.selected_campaign_id
        self._load_campaign_contacts(values[0])
        self._load_campaign_groups(values[0])
    
    def _load_campaign_contacts(self, campaign_id):
        """Carrega contatos da campanha"""
        self.tree_contacts.delete(*self.tree_contacts.get_children())
        try:
            contacts = db.consulttablesql(
                db.csqllite,
                'idcontatos,nomecontato,fonecontato',
                'itenscamp,contatos',
                f' where idcoditcamp="{campaign_id}" and iditcontcamp = idcontatos ',
                ' order by nomecontato ')
            if contacts:
                for c in contacts:
                    self.tree_contacts.insert("", "end", values=(c[0], c[1], c[2]))
                self.lbl_contact_count.configure(text=f"{len(contacts)} contatos")
            else:
                self.lbl_contact_count.configure(text="0 contatos")
        except Exception as e:
            print(f"Erro ao carregar contatos: {e}")
    
    def _load_campaign_groups(self, campaign_id):
        """Carrega grupos da campanha"""
        self.tree_groups.delete(*self.tree_groups.get_children())
        try:
            groups = db.consulttablesql(
                db.csqllite,
                'i.iditgrupogp,i.itnamegp,g.dtgrp',
                'icampgp as i left join grp as g on(g.idgrp=i.iditgrupogp)',
                f' where i.idcampgp = {campaign_id} ',
                '')
            if groups:
                for g in groups:
                    self.tree_groups.insert("", "end", values=g)
                self.lbl_group_count.configure(text=f"{len(groups)} grupos")
            else:
                self.lbl_group_count.configure(text="0 grupos")
        except Exception as e:
            print(f"Erro ao carregar grupos: {e}")
            from tools import update_log as uplog
            uplog(f" ".join(e.args))
    
    # ============================================================
    # 🎯 AÇÕES DE CAMPANHA
    # ============================================================
    def _add_campaign(self):
        """Abre formulário para nova campanha"""
        CampaignFormWindow(self, mode="add")
    
    def _edit_campaign(self):
        """Edita campanha selecionada"""
        if not self.selected_campaign_id:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        CampaignFormWindow(self, mode="edit", campaign_id=self.selected_campaign_id)
    
    def _delete_campaign(self):
        """Exclui campanha selecionada"""
        if not self.selected_campaign_id:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        if ask_yes_no(self, "Confirmar", "Deseja realmente excluir esta campanha?"):
            try:
                db.deletetablesql(db.csqllite, 'campanhas', '',
                                f' where idcampanhas={self.selected_campaign_id}')
                db.csqllite.connection.commit()
                show_info(self, "Sucesso", "Campanha excluída!")
                self._load_campaigns()
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao excluir:\n{e}")
    
    def _add_contact_to_campaign(self):
        """Adiciona contato à campanha"""
        if not self.selected_campaign_id:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        AddContactToCampaignWindow(self, self.selected_campaign_id)
    
    def _add_all_contacts(self):
        """Adiciona todos os contatos à campanha"""
        if not self.selected_campaign_id:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        try:
            contacts = db.consulttablesql(
                db.csqllite, 'idcontatos,nomecontato,fonecontato',
                'contatos', ' where idcontatos is not null ',
                ' order by nomecontato ')
            if contacts:
                count = 0
                for c in contacts:
                    existing = db.consulttablesql(
                        db.csqllite, 'iditcontcamp', 'itenscamp',
                        f' where iditcontcamp="{c[0]}" and idcoditcamp={self.selected_campaign_id} ', '')
                    if not existing:
                        db.inserttablesql(
                            db.csqllite, 'itenscamp',
                            'idcoditcamp,iditcontcamp,itnamecontcamp,itfonecontcamp',
                            f'{self.selected_campaign_id},{c[0]},"{c[1]}","{c[2]}"', '')
                        count += 1
                show_info(self, "Sucesso", f"{count} contato(s) adicionado(s)!")
                self._load_campaign_contacts(self.selected_campaign_id)
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao adicionar contatos:\n{e}")
    
    def _remove_contact(self):
        """Remove contato da campanha"""
        selection = self.tree_contacts.selection()
        if not selection:
            show_warning(self, "Atenção", "Selecione um contato!")
            return
        values = self.tree_contacts.item(selection[0], "values")
        if ask_yes_no(self, "Confirmar", f"Remover {values[1]} da campanha?"):
            try:
                db.deletetablesql(
                    db.csqllite, 'itenscamp', '',
                    f' where iditcontcamp="{values[0]}" and idcoditcamp={self.selected_campaign_id}')
                show_info(self, "Sucesso", "Contato removido!")
                self._load_campaign_contacts(self.selected_campaign_id)
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao remover:\n{e}")
    
    def _import_csv(self):
        """Importa contatos de CSV para a campanha"""
        if not self.selected_campaign_id:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        filecsv = filedialog.askopenfilename(
            parent=self,
            filetypes=[("CSV files", "*.csv")],
            title="Selecione o arquivo CSV")
        if not filecsv:
            return
        try:
            cfg.idcamp = self.selected_campaign_id
            qtd = db.importcontacts_csv(filecsv, cfg.idcamp) - 1
            if qtd > 0:
                show_info(self, "Sucesso", f"{qtd} contato(s) importado(s)!")
                self._load_campaign_contacts(self.selected_campaign_id)
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao importar:\n{e}")
    
    def _add_group(self):
        """Adiciona grupo à campanha"""
        if not self.selected_campaign_id:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        AddGroupToCampaignWindow(self, self.selected_campaign_id)

    def _remove_group(self):
            """Remove grupo da campanha"""
            selection = self.tree_groups.selection()#pega o grupo selecionado na grid
            if not selection:#se não selcionou nehum grupo avisa
                show_warning(self, "Atenção", "Selecione um Grupo!")
                return
            
            values = self.tree_groups.item(selection[0], "values")#pega os valores selecionados
            if ask_yes_no(self, "Confirmar", f"Remover {values[1]} da campanha?"):
                try:# se confirmar a operação deleta no banco de dados
                    db.deletetablesql(
                        db.csqllite, 'icampgp', '',
                        f' where iditgrupogp="{values[0]}" and idcampgp={self.selected_campaign_id}')
                    show_info(self, "Sucesso", "Grupo removido!")#exibe menssagem confirmado a remoção
                    self._load_campaign_groups(self.selected_campaign_id)#(atualiza a lista e chama o método para reixibir os grupos
                except Exception as e:
                    show_warning(self, "Erro", f"Erro ao remover:\n{e}")

    def _send_now(self):
        """Envia campanha agora"""
        if not self.selected_campaign_id:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        if ask_yes_no(self, "Confirmar", "Iniciar envio da campanha agora?"):
            try:
                cfg.clickId = self.selected_campaign_id
                checkalertcamp('s')
                show_info(self, "Sucesso", "Envio iniciado!")
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao enviar:\n{e}")
    
    # ============================================================
    # 🎯 AÇÕES DE CAMPANHA DIVERSIFICADA
    # ============================================================
    def _add_campaign_dv(self):
        """Adiciona campanha diversificada"""
        CampaignDVFormWindow(self, mode="add")
    
    def _edit_campaign_dv(self):
        """Edita campanha diversificada"""
        selection = self.tree_dv.selection()
        if not selection:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        values = self.tree_dv.item(selection[0], "values")
        cfg.clickId = values[0]
        CampaignDVFormWindow(self, mode="edit", campaign_id=values[0])
    
    def _delete_campaign_dv(self):
        """Exclui campanha diversificada"""
        selection = self.tree_dv.selection()
        if not selection:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        values = self.tree_dv.item(selection[0], "values")
        if ask_yes_no(self, "Confirmar", "Excluir esta campanha diversificada?"):
            try:
                db.deletetablesql(db.csqllite, 'campdv', '',
                                f' where idcampdv={values[0]}')
                db.csqllite.connection.commit()
                show_info(self, "Sucesso", "Campanha excluída!")
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao excluir:\n{e}")
    
    def _on_select_campaign_dv(self, event):
        """Handler de seleção de campanha DV"""
        selection = self.tree_dv.selection()
        if selection:
            cfg.clickId = self.tree_dv.item(selection[0], "values")[0]
    
    def _import_csv_dv(self):
        """Importa CSV para campanha DV"""
        if not cfg.clickId:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        filecsv = filedialog.askopenfilename(
            parent=self,
            filetypes=[("CSV files", "*.csv")],
            title="Selecione o arquivo CSV")
        if not filecsv:
            return
        try:
            lblwait = tk.Label(self, text="Importando...")
            qtd = db.importmsgdatacampdv_csv(filecsv, cfg.clickId) - 1
            if qtd > 0:
                show_info(self, "Sucesso", f"{qtd} contato(s) importado(s)!")
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao importar:\n{e}")
    
    def _remove_all_contacts_dv(self):
        """Remove todos contatos da campanha DV"""
        if not cfg.clickId:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        if ask_yes_no(self, "Confirmar", "Remover todos os contatos?"):
            try:
                db.deletetablesql(db.csqllite, 'itcampdv', '',
                                f' where iditcampdv={cfg.clickId}')
                show_info(self, "Sucesso", "Contatos removidos!")
            except Exception as e:
                show_warning(self, "Erro", f"Erro:\n{e}")
    
    def _send_now_dv(self):
        """Envia campanha DV agora"""
        if not cfg.clickId:
            show_warning(self, "Atenção", "Selecione uma campanha!")
            return
        if ask_yes_no(self, "Confirmar", "Iniciar envio da campanha diversificada?"):
            try:
                sendnow_cd()
                show_info(self, "Sucesso", "Envio iniciado!")
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao enviar:\n{e}")
    
    def _load_log(self):
        """Carrega log"""
        log_path = os.path.join(os.getcwd(), 'ASW.log')
        self.text_log.delete("1.0", "end")
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self.text_log.insert("1.0", content)
                    self.lbl_log_count.configure(text=f"{content.count(chr(10))} linhas")
            except Exception as e:
                self.text_log.insert("1.0", f"Erro: {e}")
        else:
            self.text_log.insert("1.0", "Log não encontrado.")
    
    def _clear_log(self):
        """Limpa log"""
        if ask_yes_no(self, "Confirmar", "Limpar o log?"):
            try:
                cfg.cleanFile(os.path.join(os.getcwd(), 'ASW.log'))
                self._load_log()
                show_info(self, "Sucesso", "Log limpo!")
            except Exception as e:
                show_warning(self, "Erro", f"Erro:\n{e}")


# ============================================================
# 📝 FORMULÁRIO DE CAMPANHA
# ============================================================
class CampaignFormWindow(ModalWindow):
    """Formulário de campanha"""
    
    def __init__(self, parent, mode="add", campaign_id=None):
        title = f"{Icons.ADD} Nova Campanha" if mode == "add" else f"{Icons.EDIT} Editar Campanha"
        super().__init__(parent, title=title, width=650, height=700)
        self.mode = mode
        self.campaign_id = campaign_id
        self._build_ui()
        if mode == "edit" and campaign_id:
            self._load_campaign_data()
    
    def _build_ui(self):
        """Constrói formulário"""
        scroll_frame = create_scrollable_frame(self, bg_color=Colors.BG_MAIN)
        
        card1 = CardFrame(scroll_frame, title=f"{Icons.CAMPAIGN} Dados da Campanha")
        card1.pack(fill="x", pady=(0, 10), padx=15)
        inner1 = tk.Frame(card1, bg=Colors.BG_WHITE)
        inner1.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner1, text="Nome *", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        self.entry_name = ttkb.Entry(inner1)
        self.entry_name.pack(fill="x", pady=(5, 15))
        
        tk.Label(inner1, text="Mensagem", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        msg_frame = tk.Frame(inner1, bg=Colors.BG_WHITE)
        msg_frame.pack(fill="x", pady=(5, 5))
        self.text_msg = tk.Text(msg_frame, height=5, font=("Segoe UI", 10),
                               bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                               relief="solid", bd=1, wrap="word")
        self.text_msg.pack(side="left", fill="x", expand=True)
        ttkb.Button(msg_frame, text="📁 Importar", style="secondary.TButton",
                   command=self._import_message).pack(side="right", padx=(5, 0))
        
        card2 = CardFrame(scroll_frame, title=f"{Icons.FILE} Anexos (Opcionais)")
        card2.pack(fill="x", pady=(0, 10), padx=15)
        inner2 = tk.Frame(card2, bg=Colors.BG_WHITE)
        inner2.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner2, text="Imagem", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        img_frame = tk.Frame(inner2, bg=Colors.BG_WHITE)
        img_frame.pack(fill="x", pady=(5, 15))
        self.entry_img = ttkb.Entry(img_frame)
        self.entry_img.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttkb.Button(img_frame, text="📁", style="secondary.TButton",
                   command=lambda: self._browse_file(self.entry_img)).pack(side="right")
        
        tk.Label(inner2, text="Documento", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        doc_frame = tk.Frame(inner2, bg=Colors.BG_WHITE)
        doc_frame.pack(fill="x", pady=(5, 0))
        self.entry_doc = ttkb.Entry(doc_frame)
        self.entry_doc.pack(side="left", fill="x", expand=True, padx=(0, 5))
        ttkb.Button(doc_frame, text="📁", style="secondary.TButton",
                   command=lambda: self._browse_file(self.entry_doc)).pack(side="right")
        
        card3 = CardFrame(scroll_frame, title=f"{Icons.CALENDAR} Agendamento")
        card3.pack(fill="x", pady=(0, 10), padx=15)
        inner3 = tk.Frame(card3, bg=Colors.BG_WHITE)
        inner3.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner3, text="Data de Disparo (DD/MM/YYYY HH:MM)",
                font=("Segoe UI", 10), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        self.entry_date = ttkb.Entry(inner3)
        self.entry_date.insert(0, datetime.now().strftime('%d/%m/%Y %H:%M'))
        self.entry_date.pack(fill="x", pady=(5, 15))
        
        tk.Label(inner3, text="Status", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        self.var_active = tk.StringVar(value="S")
        status_frame = tk.Frame(inner3, bg=Colors.BG_WHITE)
        status_frame.pack(fill="x", pady=(5, 15))
        ttkb.Radiobutton(status_frame, text="✅ Ativo",
                        variable=self.var_active, value="S",
                        bootstyle="success").pack(side="left", padx=5)
        ttkb.Radiobutton(status_frame, text=" Inativo",
                        variable=self.var_active, value="N",
                        bootstyle="danger").pack(side="left", padx=5)
        
        tk.Label(inner3, text="Saudações", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        self.var_saudaname = tk.BooleanVar(value=False)
        self.var_saudatime = tk.BooleanVar(value=False)
        ttkb.Checkbutton(inner3, text="Saudar pelo nome",
                        variable=self.var_saudaname,
                        bootstyle="success-round-toggle").pack(anchor="w", pady=2)
        ttkb.Checkbutton(inner3, text="Saudar por período (Bom dia/tarde/noite)",
                        variable=self.var_saudatime,
                        bootstyle="success-round-toggle").pack(anchor="w")
        
        btn_frame = tk.Frame(scroll_frame, bg=Colors.BG_MAIN)
        btn_frame.pack(fill="x", pady=(10, 0), padx=15)
        ttkb.Button(btn_frame, text="✕ Cancelar", style="secondary.TButton",
                   command=self.on_close).pack(side="left", padx=5)
        save_text = "💾 Salvar" if self.mode == "add" else "💾 Atualizar"
        ttkb.Button(btn_frame, text=save_text, style="primary.TButton",
                   command=self._save_campaign).pack(side="right", padx=5)
        
        tk.Frame(scroll_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")
    
    def _load_campaign_data(self):
        """Carrega dados da campanha"""
        try:
            campaigns = db.consulttablesql(
                db.csqllite, '*', 'campanhas',
                f' where idcampanhas={self.campaign_id}', ';')
            if campaigns and len(campaigns) > 0:
                c = campaigns[0]
                self.entry_name.insert(0, c[1])
                self.text_msg.insert("1.0", c[3] or "")
                self.entry_img.insert(0, c[4] or "")
                self.entry_doc.insert(0, c[5] or "")
                self.var_active.set(c[6])
                self.entry_date.delete(0, "end")
                self.entry_date.insert(0, c[7] or "")
                self.var_saudaname.set(c[9] == 'S')
                self.var_saudatime.set(c[10] == 'S')
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao carregar:\n{e}")
    
    def _browse_file(self, entry):
        """Seleciona arquivo"""
        path = filedialog.askopenfilename(parent=self)
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)
    
    def _import_message(self):
        """Importa mensagem de arquivo"""
        filetxt = filedialog.askopenfilename(
            parent=self,
            filetypes=[("Text files", "*.txt")],
            title="Selecione o arquivo de mensagem")
        if filetxt:
            try:
                with open(filetxt, 'r', encoding='utf-8', errors='ignore') as f:
                    self.text_msg.delete("1.0", "end")
                    self.text_msg.insert("1.0", f.read())
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao importar:\n{e}")
    
    def _save_campaign(self):
        """Salva campanha"""
        name = self.entry_name.get().strip()
        if not name:
            show_warning(self, "Atenção", "O nome é obrigatório!")
            return
        msg = self.text_msg.get("1.0", "end-1c").strip()
        img = self.entry_img.get().strip()
        doc = self.entry_doc.get().strip()
        date = self.entry_date.get().strip()
        active = self.var_active.get()
        saudan = 'S' if self.var_saudaname.get() else 'N'
        saudat = 'S' if self.var_saudatime.get() else 'N'
        datacad = datetime.now().strftime('%d/%m/%Y %H:%M')
        
        try:
            if self.mode == "add":
                sql = (f'insert into campanhas '
                      f'(nomecampanhas,dthcadastrocampanhas,msgcampanhas,'
                      f'imgcampanhas,doccampanhas,ativocampanhas,'
                      f'dthdispararcampanhas,enviada,saudaNome,saudatemp) '
                      f'values("{name}","{datacad}","{msg}","{img}","{doc}",'
                      f'"{active}","{date}","N","{saudan}","{saudat}")')
                if ask_yes_no(self, "Confirmar", "Inserir nova campanha?"):
                    db.csqllite.execute(sql)
                    db.csqllite.connection.commit()
                    show_info(self, "Sucesso", "Campanha criada!")
                    self.on_close()
            else:
                set_fields = (f"nomecampanhas='{name}',msgcampanhas='{msg}',"
                             f"imgcampanhas='{img}',doccampanhas='{doc}',"
                             f"ativocampanhas='{active}',dthdispararcampanhas='{date}',"
                             f"saudatemp='{saudat}',saudaNome='{saudan}'")
                if ask_yes_no(self, "Confirmar", "Atualizar campanha?"):
                    db.updatetablesql(db.csqllite, 'campanhas', set_fields,
                                    f" idcampanhas={self.campaign_id}")
                    show_info(self, "Sucesso", "Campanha atualizada!")
                    self.on_close()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao salvar:\n{e}")


# ============================================================
# 📝 FORMULÁRIO CAMPANHA DIVERSIFICADA
# ============================================================
class CampaignDVFormWindow(ModalWindow):
    """Formulário de campanha diversificada"""
    
    def __init__(self, parent, mode="add", campaign_id=None):
        title = f"{Icons.ADD} Nova Campanha Diversificada" if mode == "add" else f"{Icons.EDIT} Editar"
        super().__init__(parent, title=title, width=500, height=550)
        self.mode = mode
        self.campaign_id = campaign_id
        self._build_ui()
        if mode == "edit" and campaign_id:
            self._load_data()
    
    def _build_ui(self):
        """Constrói formulário"""
        scroll_frame = create_scrollable_frame(self, bg_color=Colors.BG_MAIN)
        
        card = CardFrame(scroll_frame, title=f"{Icons.MESSAGE} Dados da Campanha")
        card.pack(fill="x", pady=(0, 10), padx=15)
        inner = tk.Frame(card, bg=Colors.BG_WHITE)
        inner.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner, text="Nome *", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        self.entry_name = ttkb.Entry(inner)
        self.entry_name.pack(fill="x", pady=(5, 15))
        
        tk.Label(inner, text="Data de Envio (DD/MM/YYYY)",
                font=("Segoe UI", 10), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        self.entry_date = ttkb.Entry(inner)
        self.entry_date.insert(0, datetime.now().strftime('%d/%m/%Y'))
        self.entry_date.pack(fill="x", pady=(5, 15))
        
        time_frame = tk.Frame(inner, bg=Colors.BG_WHITE)
        time_frame.pack(fill="x")
        tk.Label(time_frame, text="Hora:", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left")
        self.cb_hour = ttkb.Combobox(time_frame, values=[f"{h:02d}" for h in range(24)],
                                    width=5, state="readonly")
        self.cb_hour.set("00")
        self.cb_hour.pack(side="left", padx=5)
        
        tk.Label(time_frame, text="Minuto:", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left", padx=(15, 0))
        self.cb_min = ttkb.Combobox(time_frame, values=[f"{m:02d}" for m in range(60)],
                                   width=5, state="readonly")
        self.cb_min.set("00")
        self.cb_min.pack(side="left", padx=5)
        
        tk.Label(inner, text="Status", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x", pady=(15, 0))
        self.var_active = tk.StringVar(value="N")
        status_frame = tk.Frame(inner, bg=Colors.BG_WHITE)
        status_frame.pack(fill="x", pady=(5, 0))
        ttkb.Radiobutton(status_frame, text="✅ Ativo",
                        variable=self.var_active, value="S",
                        bootstyle="success").pack(side="left", padx=5)
        ttkb.Radiobutton(status_frame, text="❌ Inativo",
                        variable=self.var_active, value="N",
                        bootstyle="danger").pack(side="left", padx=5)
        
        btn_frame = tk.Frame(scroll_frame, bg=Colors.BG_MAIN)
        btn_frame.pack(fill="x", pady=(15, 0), padx=15)
        ttkb.Button(btn_frame, text="✕ Cancelar", style="secondary.TButton",
                   command=self.on_close).pack(side="left", padx=5)
        save_text = "💾 Salvar" if self.mode == "add" else "💾 Atualizar"
        ttkb.Button(btn_frame, text=save_text, style="primary.TButton",
                   command=self._save).pack(side="right", padx=5)
        tk.Frame(scroll_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")
    
    def _load_data(self):
        """Carrega dados"""
        try:
            campaigns = db.consulttablesql(
                db.csqllite,
                'descricampdv,ativocampdv,dtsendcampdv,hrsendcampdv,mincampdv',
                'campdv', f' where idcampdv={self.campaign_id}', ';')
            if campaigns and len(campaigns) > 0:
                c = campaigns[0]
                self.entry_name.insert(0, c[0])
                self.var_active.set(c[1])
                self.entry_date.delete(0, "end")
                self.entry_date.insert(0, c[2])
                self.cb_hour.set(c[3])
                self.cb_min.set(c[4])
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao carregar:\n{e}")
    
    def _save(self):
        """Salva"""
        name = self.entry_name.get().strip()
        if not name:
            show_warning(self, "Atenção", "Nome obrigatório!")
            return
        date = self.entry_date.get().strip()
        hour = self.cb_hour.get()
        minute = self.cb_min.get()
        active = self.var_active.get()
        try:
            if self.mode == "add":
                sql = (f'insert into campdv '
                      f'(descricampdv,dtsendcampdv,hrsendcampdv,mincampdv,ativocampdv) '
                      f'values("{name}","{date}","{hour}","{minute}","{active}")')
                if ask_yes_no(self, "Confirmar", "Inserir campanha?"):
                    db.csqllite.execute(sql)
                    db.csqllite.connection.commit()
                    show_info(self, "Sucesso", "Campanha criada!")
                    self.on_close()
            else:
                set_fields = (f'descricampdv="{name}",dtsendcampdv="{date}",'
                             f'hrsendcampdv="{hour}",mincampdv="{minute}",'
                             f'ativocampdv="{active}"')
                if ask_yes_no(self, "Confirmar", "Atualizar campanha?"):
                    db.updatetablesql(db.csqllite, 'campdv', set_fields,
                                    f" idcampdv={self.campaign_id}")
                    show_info(self, "Sucesso", "Campanha atualizada!")
                    self.on_close()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao salvar:\n{e}")


# ============================================================
#  ADICIONAR CONTATO À CAMPANHA
# ============================================================
class AddContactToCampaignWindow(ModalWindow):
    """Janela para adicionar contato à campanha"""
    
    def __init__(self, parent, campaign_id):
        super().__init__(parent, title=f"{Icons.ADD} Adicionar Contato",
                        width=600, height=500)
        self.campaign_id = campaign_id
        self.selected_contact = None
        self._build_ui()
        self._load_contacts()
    
    def _build_ui(self):
        """Constrói interface"""
        scroll_frame = create_scrollable_frame(self, bg_color=Colors.BG_MAIN)
        
        filter_card = CardFrame(scroll_frame, title=f"{Icons.FILTER} Filtrar Contatos")
        filter_card.pack(fill="x", pady=(0, 10), padx=15)
        filter_inner = tk.Frame(filter_card, bg=Colors.BG_WHITE)
        filter_inner.pack(fill="x", padx=15, pady=15)
        filter_frame = tk.Frame(filter_inner, bg=Colors.BG_WHITE)
        filter_frame.pack(fill="x")
        
        tk.Label(filter_frame, text="Nome:", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left")
        self.entry_filter = ttkb.Entry(filter_frame)
        self.entry_filter.pack(side="left", fill="x", expand=True, padx=10)
        ttkb.Button(filter_frame, text=" Filtrar", style="primary.TButton",
                   command=self._apply_filter).pack(side="right")
        
        list_card = CardFrame(scroll_frame, title=f"{Icons.CONTACT} Contatos Disponíveis")
        list_card.pack(fill="both", expand=True, pady=(0, 10), padx=15)
        list_frame = tk.Frame(list_card, bg=Colors.BG_WHITE)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tree = ttkb.Treeview(
            list_frame,
            columns=("id", "nome", "fone"),
            show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID"); self.tree.column("id", width=50, anchor="center")
        self.tree.heading("nome", text="Nome"); self.tree.column("nome", width=250)
        self.tree.heading("fone", text="Telefone"); self.tree.column("fone", width=150)
        
        tree_scroll = ttkb.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        
        btn_frame = tk.Frame(scroll_frame, bg=Colors.BG_MAIN)
        btn_frame.pack(fill="x", padx=15)
        ttkb.Button(btn_frame, text="✕ Cancelar", style="secondary.TButton",
                   command=self.on_close).pack(side="left", padx=5)
        ttkb.Button(btn_frame, text=f"{Icons.ADD} Adicionar à Campanha",
                   style="success.TButton", command=self._add_contact).pack(side="right", padx=5)
        tk.Frame(scroll_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")
    
    def _load_contacts(self, filter_text=""):
        """Carrega contatos disponíveis"""
        self.tree.delete(*self.tree.get_children())
        try:
            where = ' where idcontatos is not null '
            if filter_text:
                where += f' and nomecontato like "%{filter_text}%" '
            contacts = db.consulttablesql(
                db.csqllite,
                'idcontatos,nomecontato,fonecontato',
                'contatos', where, ' order by nomecontato ')
            if contacts:
                for c in contacts:
                    self.tree.insert("", "end", values=(c[0], c[1], c[2]))
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao carregar:\n{e}")
    
    def _apply_filter(self):
        """Aplica filtro"""
        self._load_contacts(self.entry_filter.get().strip())
    
    def _on_select(self, event):
        """Handler de seleção"""
        selection = self.tree.selection()
        if selection:
            self.selected_contact = self.tree.item(selection[0], "values")
    
    def _add_contact(self):
        """Adiciona contato à campanha"""
        if not self.selected_contact:
            show_warning(self, "Atenção", "Selecione um contato!")
            return
        try:
            existing = db.consulttablesql(
                db.csqllite, 'iditcontcamp', 'itenscamp',
                f' where iditcontcamp="{self.selected_contact[0]}" and idcoditcamp={self.campaign_id} ', '')
            if existing:
                show_warning(self, "Atenção", "Contato já está na campanha!")
                return
            db.inserttablesql(
                db.csqllite, 'itenscamp',
                'idcoditcamp,iditcontcamp,itnamecontcamp,itfonecontcamp',
                f'{self.campaign_id},{self.selected_contact[0]},"{self.selected_contact[1]}","{self.selected_contact[2]}"', '')
            show_info(self, "Sucesso", f"{self.selected_contact[1]} adicionado à campanha!")
            self.on_close()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao adicionar:\n{e}")


# ============================================================
# 👥 ADICIONAR GRUPO À CAMPANHA
# ============================================================
class AddGroupToCampaignWindow(ModalWindow):
    """Janela para adicionar grupo à campanha"""
    
    def __init__(self, parent, campaign_id):
        super().__init__(parent, title=f"{Icons.GROUP} Adicionar Grupo",
                        width=600, height=500)
        self.campaign_id = campaign_id
        self.selected_group = None
        self._build_ui()
        self._load_groups()
    
    def _build_ui(self):
        """Constrói interface"""
        scroll_frame = create_scrollable_frame(self, bg_color=Colors.BG_MAIN)
        
        filter_card = CardFrame(scroll_frame, title=f"{Icons.FILTER} Filtrar Grupos")
        filter_card.pack(fill="x", pady=(0, 10), padx=15)
        filter_inner = tk.Frame(filter_card, bg=Colors.BG_WHITE)
        filter_inner.pack(fill="x", padx=15, pady=15)
        filter_frame = tk.Frame(filter_inner, bg=Colors.BG_WHITE)
        filter_frame.pack(fill="x")
        
        tk.Label(filter_frame, text="Nome:", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left")
        self.entry_filter = ttkb.Entry(filter_frame)
        self.entry_filter.pack(side="left", fill="x", expand=True, padx=10)
        ttkb.Button(filter_frame, text=" Filtrar", style="primary.TButton",
                   command=self._apply_filter).pack(side="right")
        
        list_card = CardFrame(scroll_frame, title=f"{Icons.GROUP} Grupos Disponíveis")
        list_card.pack(fill="both", expand=True, pady=(0, 10), padx=15)
        list_frame = tk.Frame(list_card, bg=Colors.BG_WHITE)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tree = ttkb.Treeview(
            list_frame,
            columns=("id", "nome", "data"),
            show="headings", selectmode="browse")
        
        self.tree.heading("id", text="ID"); self.tree.column("id", width=50, anchor="center")
        self.tree.heading("nome", text="Nome"); self.tree.column("nome", width=300)
        self.tree.heading("data", text="Data"); self.tree.column("data", width=150)
        
        tree_scroll = ttkb.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll.grid(row=0, column=1, sticky="ns")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)
        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        
        btn_frame = tk.Frame(scroll_frame, bg=Colors.BG_MAIN)
        btn_frame.pack(fill="x", padx=15)
        ttkb.Button(btn_frame, text="✕ Cancelar", style="secondary.TButton",
                   command=self.on_close).pack(side="left", padx=5)
        ttkb.Button(btn_frame, text=f"{Icons.ADD} Adicionar à Campanha",
                   style="success.TButton", command=self._add_group).pack(side="right", padx=5)
        tk.Frame(scroll_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")
    
    def _load_groups(self, filter_text=""):
        """Carrega grupos"""
        self.tree.delete(*self.tree.get_children())
        try:
            where = ' where idgrp is not null '
            if filter_text:
                where += f' and namegrp like "%{filter_text}%" '

            groups = db.consulttablesql(
                db.csqllite, 'idgrp,namegrp,dtgrp',
                'grp', where, ' order by namegrp ')
            if groups:
                for g in groups:
                    self.tree.insert("", "end", values=g)
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao carregar:\n{e}")


    def _apply_filter(self):
        """Aplica filtro"""
        self._load_groups(self.entry_filter.get().strip())
    
    def _on_select(self, event):
        """Handler de seleção"""
        selection = self.tree.selection()
        if selection:
            self.selected_group = self.tree.item(selection[0], "values")
    
    def _add_group(self):
        """Adiciona grupo à campanha"""
        if not self.selected_group:
            show_warning(self, "Atenção", "Selecione um grupo!")
            return
        try:
            existing = db.consulttablesql(
                db.csqllite, 'iditgrupogp', 'icampgp',
                f' where idcampgp={self.campaign_id} and iditgrupogp={self.selected_group[0]} ', '')
            if existing:
                show_warning(self, "Atenção", "Grupo já está na campanha!")
                return
            db.inserttablesql(
                db.csqllite, 'icampgp',
                'idcampgp,iditgrupogp,itnamegp',
                f'{self.campaign_id},{self.selected_group[0]},"{self.selected_group[1]}"', '')

            #(atualiza a lista e chama o método para reixibir os grupos
            self.selected_campaign_id = cfg.clickId
            AddGroupToCampaignWindow(self, self.selected_campaign_id)            
            #self._load_groups(self,filter_text="")#(atualiza a lista e chama o método para reixibir os grupos
            show_info(self, "Sucesso", f"Grupo {self.selected_group[1]} adicionado,Clique na campanha novamente para atualizar!!")
            self.on_close
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao adicionar:\n{e}")


# ============================================================
# 📤 FUNÇÃO DE ENVIO CAMPANHA DIVERSIFICADA (mantida do original)
# ============================================================
def sendnow_cd():
    """Envia campanha diversificada"""
    label = tk.Label()
    label['fg'] = 'red'
    label.config(text='Eventos->Processo lendo o arquivo json para envio!')
    import time
    dtlocal = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
    import os
    import rpa
    from tools import update_log as uplog
    Namecamp = ''
    localapp = ''
    localapp = os.getcwd()

    localapp = localapp.replace('\\', '/')
    global filejson
    filejson = ''
    Eventos = '...Percorrendo a os contatos e montando o arquivo json para envio/1'
    label.config(text='Eventos->' + Eventos)
    uplog(Eventos)
    rscampdv = []
    Eventos = 'Consultando se a campanha está ativa!'
    label.config(text='Eventos->' + Eventos)
    rscampdv = db.consulttablesql(db.csqllite, 'idcampdv,descricampdv,ativocampdv',
                                  ' campdv ', 'where idcampdv=' + str(cfg.clickId) + ' and ativocampdv="S"', '')
    if rscampdv == [] or rscampdv == None:
        showmessage('Alerta', 'Você não escolheu uma campanha, ou está desativada!\nFavor corrigir!')
    else:
        Eventos = 'Pegando o Nome da campanha  para criar o arquivo'
        uplog(Eventos)
        for y in rscampdv:
            for x in range(len(y)):
                if x == 0: idcampdv = y[x]
                elif x == 1: Namecamp = y[x]

        Eventos = 'Criando o arquivo json da campanha diversa'
        uplog(Eventos)
        docs_dir = os.path.join(localapp, 'Docs')
        os.makedirs(docs_dir, exist_ok=True)
        filejson = os.path.join(docs_dir, Namecamp + '.json')

        cfg.createfilejson(filejson)
        Eventos = "Consultando se o contato já foi cadastrado no sistema e importado na campanha!"
        uplog(Eventos)
        rs_concontact = []
        rs_concontact = db.consulttablesql(
            db.csqllite,
            ' idcontatos,nomecontato,fonecontato,nomegrupocontato,datacad,emailcontato,ativocontato,eclientecontato, ' +
            'i.msgitcampdv,i.imgitcampdv,i.docitcampdv',
            ' contatos c left join itcampdv i on(i.numitcampdv = c.fonecontato) ',
            ' where i.iditcampdv="' + str(cfg.clickId) + '"', ' order by nomecontato;')
        if (rs_concontact != [] and rs_concontact != None):
            db.con_contactCamp = rs_concontact
            Id = ''
            Numero = ''
            Nome = ''
            Mensagem = ''
            Doc = ''
            Img = ''
            cont = 0
            for c in rs_concontact:
                cont = cont + 1
                for x in range(len(c)):
                    if (x == 0): Id = c[x]
                    elif (x == 1): Nome = str(c[x])
                    elif (x == 2): Numero = c[x]
                    elif (x == 8): Mensagem = c[x]
                    elif (x == 9): Img = c[x]
                    elif (x == 10): Doc = c[x]
                Eventos = "Inserindo os dados:id=" + str(Id) + ",Nome=" + str(Nome) + ",Numero=" + str(Numero) + ",Messagem=" + str(Mensagem)
                Eventos = Eventos + ",Img=" + Img + ",Doc=" + Doc + " no arquivo !"
                print(Eventos)
                uplog(Eventos)
                Doc = Doc.replace('\\', '/')
                Img = Img.replace('\\', '/')
                cfg.writefileJson(filejson, '		"Id":"' + str(Id) + '",')
                cfg.writefileJson(filejson, '		"Numero":' + str(Numero) + ',')
                cfg.writefileJson(filejson, '		"Nome":"' + Nome + '",')
                cfg.writefileJson(filejson, '		"Mensagem":"' + Mensagem + '",')
                cfg.writefileJson(filejson, '		"Doc":"' + Doc + '",')
                cfg.writefileJson(filejson, '		"Img":"' + Img + '"')
                print('qtd of contact ->' + str(cont), '-len c->' + str(len(rs_concontact)))
                if cont < len(rs_concontact):
                    cfg.writefileJson(filejson, '	},')
                    cfg.writefileJson(filejson, '	{\n')
                elif cont == len(rs_concontact):
                    cfg.writefileJson(filejson, '	}')
                    cfg.writefileJson(filejson, '\n')
                    cfg.writefileJson(filejson, ']')

        Eventos = '...Chamando o método de envio camp dv por arquivo'
        uplog(Eventos)

        docs_dir = os.path.join(localapp, 'Docs')
        os.makedirs(docs_dir, exist_ok=True)
        filejson = os.path.join(docs_dir, Namecamp + '.json')
        
        if os.path.exists(filejson) == False:
            Eventos = "File " + filejson + " not found,chosen file json to send"
            uplog(Eventos)
        getsetfile_Json(filejson)
        try:
            import os
            Eventos = 'check if file exists json to send msg'
            uplog(Eventos)
            if (os.path.isfile(filejson)):
                Eventos = '...Encontrou o arquivo!'
                uplog(Eventos)
                TPwebdriver = int(cfg.readcfg('config.ini', 'action', 'browser'))
                print('TPwebdriver ', str(TPwebdriver))
                Eventos = '...sending campaing diversity!/ Enviando a campanha diversa!'
                uplog(Eventos)
                rpa.sendSingleMessage(cfg.clickId, filejson)
        except Exception as e:
            Eventos = f"4-Exceção in sendnow_cd(->" + "".join(e.args)
            uplog(Eventos)


def getsetfile_Json(filejson):
    """Lê arquivo config e atribui json"""
    global Eventos
    global tpbrouser
    global tpsend
    global time
    global days
    global msg_all
    global pxbtnsend
    global pybtnsend
    import time
    dtlocal = time.strftime('%d/%m/%Y %H:%M:%S', time.localtime())
    from tools import update_log as uplog
    Eventos = 'read file config '
    print(Eventos)
    tpbrouser = cfg.readcfg('config.ini', 'action', 'browser')
    tpsend = cfg.readcfg('config.ini', 'action', 'tp')
    time = cfg.readcfg('config.ini', 'action', 'time')
    days = cfg.readcfg('config.ini', 'action', 'day')
    timeqrcode = cfg.readcfg('config.ini', 'action', 'timeqrcode')
    pflogin = cfg.readcfg('config.ini', 'action', 'pflogin')
    msg_all = cfg.readcfg('config.ini', 'repository', 'msg_all')
    doc_all = cfg.readcfg('config.ini', 'repository', 'doc_all')
    img_all = cfg.readcfg('config.ini', 'repository', 'img_all')
    emailrel = cfg.readcfg('config.ini', 'repository', 'emailrel')
    id_Product = cfg.get_id_maq()
    if (id_Product == '' or id_Product == "None"):
        print('read id_Product of file config =', id_Product)
    key_license = cfg.readcfg('config.ini', 'active_license', 'key_license')
    print('read key_license of file config =', key_license)
    asw_Now = datetime.today().strftime('%y%m%d')
    asw_Now = asw_Now.replace(".", "")
    dtat = asw_Now
    if (key_license == '' or key_license == "None"):
        key_license = str(cfg.keylicence_toNow())
    if cfg.find_string_file('config.ini', 'px_btnsend') != False:
        pxbtnsend = int(cfg.readcfg('config.ini', 'action', 'px_btnsend'))
    if cfg.find_string_file('config.ini', 'py_btnsend') != False:
        pybtnsend = int(cfg.readcfg('config.ini', 'action', 'py_btnsend'))
    if cfg.readcfg('config.ini', 'action', 'px_btnsend') == None:
        pxbtnsend = 1316
    else:
        pxbtnsend = int(cfg.readcfg('config.ini', 'action', 'px_btnsend'))
    if cfg.readcfg('config.ini', 'action', 'py_btnsend') == None:
        pybtnsend = 677
    else:
        pybtnsend = int(cfg.readcfg('config.ini', 'action', 'py_btnsend'))
    if cfg.find_string_file('config.ini', 'pathexebrowser') == True:
        cfg.pathexebrowser = (cfg.readcfg('config.ini', 'action', 'pathexebrowser'))
    cfg.timereadQr = cfg.readcfg('config.ini', 'action', 'timeqrcode')
    if cfg.find_string_file('config.ini', 'timeupimg') == True:
        if (cfg.readcfg('config.ini', 'action', 'timeupimg') != None):
            cfg.timeupimg = int(cfg.readcfg('config.ini', 'action', 'timeupimg'))
    msg_all = cfg.readcfg('config.ini', 'repository', 'msg_all')
    img_all = cfg.readcfg('config.ini', 'repository', 'img_all')
    doc_all = cfg.readcfg('config.ini', 'repository', 'doc_all')
    emailrel = cfg.readcfg('config.ini', 'repository', 'emailrel')
    key_license = cfg.readcfg('config.ini', 'active_license', 'key_license')
    Eventos = 'Save local file json and our params'
    print(Eventos)
    uplog(Eventos)
    Eventos = cfg.createcfg('localhost', 'example', '1234', 'admin', 'secret', 'git',
                           'git@github.com:user/project.git',
                           filejson, msg_all, doc_all, img_all, emailrel, tpsend, tpbrouser, time, days,
                           id_Product, key_license, dtat,
                           timeqrcode, pflogin, str(pxbtnsend), str(pybtnsend), str(cfg.timeupimg),
                           cfg.pathexebrowser)
    uplog(Eventos)