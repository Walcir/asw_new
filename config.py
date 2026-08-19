# -*- coding: utf-8 -*-
"""
config.py - Configurações do sistema ASW
Mantém toda a lógica de negócio + GUI modal refatorada
"""
import os
import time
import platform
import configparser
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

# Módulos internos
try:
    from cryptoasw import encrypt_txt_n as ectxt
    from cryptoasw import desencrypt_n_txt as dctxt
except ImportError:
    ectxt = lambda x: x
    dctxt = lambda x: x

import tools
from ui_base import (ModalWindow, Colors, Icons, CardFrame, FormField,
                     show_info, show_warning, ask_yes_no)

# ============================================================
# 🌍 VARIÁVEIS GLOBAIS
# ============================================================
msg_all = ''
img_all = ''
doc_all = ''
each_key = ''
each_val = ''
each_section = ''
whatslogin = 0
contact_db = 0
clickId = 0
key_prs = ''
key_index = 0
dtvenclicense = ''
idcamp = 0
timereadQr = 390
saudaName = ''
saudatemp = ''
Eventos = ''
pxbtnsend = 0
pybtnsend = 0
timeupimg = 25
timesendmsg = 10
pathexebrowser = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
is_sendcamp = False
is_scrolling = False
scroll_speed = 100

# ============================================================
# 🛠️ FUNÇÕES UTILITÁRIAS (LÓGICA DE NEGÓCIO)
# ============================================================
def convertTuple(tup):
    s = ''
    if tup and tup != []:
        for item in tup:
            s = s + str(item)
    return s

def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

def isdatevalid(date):
    try:
        if int(date[0:2]) > 31 or int(date[0:2]) < 1:
            return False
        if int(date[2:4]) > 12 or int(date[2:4]) < 1:
            return False
        return True
    except (ValueError, IndexError):
        return False


def extract_number(string_text):
    return "".join([char for char in string_text if char.isdigit()])

def VerifyVencdate(dateNow, dateVenc)->bool:
    try:
        if not dateVenc:
           import config as cfg # pega a licença do arquivo de config
           key_lic  = cfg.readcfg('config.ini', 'active_license', 'key_license')
           dateVenc =getVenc_lic(key_lic)#extrai o vencimento pela licença

        from tools import update_log as uplog #guarda em um arquivo de log e imprime no console
        uplog(f"config.py->VerifyVencdate({dateNow.strftime('%y%m%d')},{dateVenc})")
        #Formata a data atual para string no formato correto '%y%m%d'
        str_now = dateNow.strftime('%y%m%d')
        #se hoje for maior ou iual ao vencimento
        if str_now >= dateVenc:
            return False
        else:
            return True
    except Exception as e:
        from tools import update_log as uplog
        uplog(f"Erro->config.py->VerifyVencdate{''.join(e.args)}")
        return False

def find_string_file(file, str_text):
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            return str_text in content
    except Exception:
        return False

def cleanFile(filetxt):
    try:
        with open(filetxt, "w", encoding='utf-8') as f:
            pass
    except Exception:
        pass

def write_new_line_f(file, newline_txt):
    with open(file, 'w', encoding='utf-8') as f:
        f.write('\n' + newline_txt + '\n')

def arqlog(pathlog, conteudo):
    try:
        mode = 'a' if os.path.exists(pathlog) else 'w'
        with open(pathlog, mode, encoding='utf-8') as f:
            f.write(conteudo + '\n')
        global Eventos
        Eventos += conteudo
    except Exception as e:
        print(f'Erro em arqlog: {e}')

def get_id_maq():
    try:
        name_maq = platform.node()
        version_maq = platform.version()
        id_maq = name_maq.replace("_", " ").replace("-", " ").replace("/", " ")
        id_maq = name_maq.replace(" ","")#remove espaços
        id_maq = (str(extract_number(id_maq)) + "-" + version_maq.replace(".", " ")).replace("-", " ")
        id_maq = id_maq.replace(".", " ").replace("~", " ").replace("^", " ").replace("  ", "0")
        return id_maq
    except Exception as e:
        print(f'(get_id_maq) Erro: {e}')
        return ""

def checkId_maqlic(licence):
    try:
        id_Product = str(get_id_maq())
        return (licence[0:2] == id_Product[0:2] and
                licence[len(licence)-2:len(licence)] == id_Product[len(id_Product)-2:len(id_Product)])
    except Exception:
        return False

def createParam(filepath, section, param, value):
    try:
        with open(filepath, 'a', encoding='utf-8') as cf:
            cf.write(f'[{section}]\n' if not find_string_file(filepath, f'[{section}]') else '')
            if not find_string_file(filepath, param):
                cf.write(f'{param} = {value}\n')
        return True
    except Exception as e:
        print(f'(createParam) Erro: {e}')
        return False

def VerifyParamsExists(filepath, section, params):
    try:
        conf = configparser.ConfigParser()
        conf.read(filepath)
        for each_section in conf.sections():
            if section == each_section:
                for each_key, _ in conf.items(each_section):
                    if params in each_key:
                        return True
        return False
    except Exception:
        return False

def getVenc_lic(licenca):
    try:
        id_Product = str(get_id_maq())
        id_Product = extract_number(id_Product)#extrai apenas os numeros da string
        id_Product = id_Product.replace(' ','')#remove os espaços da string
        id_Product = id_Product[0:2] + id_Product[len(id_Product)-2:len(id_Product)]
        asw_Now = datetime.now()
        ''' 
            Se a licença não estiver definida atribui os 2 primeiros digitos do id do equipamento
            + a data atual no formato y(ano)m(mês)d(dia)[230511] + os ultimos 2 digítos do equipamento
        '''
        if not licenca:
            licenca = id_Product[0:2]+datetime.strftime(asw_Now, '%y%m%d')+id_Product[len(id_Product)-2:len(id_Product)]
        '''
           o método consiste em subtrair o id do equipamento com 4 digitos 
           - (a licença / pela constante 2 )
           e resultado - a constante 12
        ''' 
        #Limpa a licença para o tamanho 6 digitos ymd 240501
        licenca = licenca[2:8]# da segunda posição até a oitava
        r_lic = str(((int(licenca) - (int(id_Product)) )// 2) - 12)
        return r_lic
    except Exception as e:
        print(f"Exceção ao buscar o vencimento da licença, será atribuido o valor padrão de controle 230111")
        print(f"config.py->getVenc_lic->{''.join(e.args())}")
        return '230111'

def keylicence_toNow():
    asw_Now = datetime.today().strftime('%y%m%d').replace(".", "")
    id_Product = str(get_id_maq())
    id_Product = id_Product.replace(" ","")#remove espaços
    id_Product = extract_number(id_Product)#retorna apenas numeros para concatenar e somar valores abaixo
    id_Product = id_Product[0:2] + id_Product[len(id_Product)-2:len(id_Product)]
    calckey = (int(asw_Now) + 12) * 2 + int(id_Product)
    calckey = int(id_Product[0:2]) + calckey + int(id_Product[len(id_Product)-2:len(id_Product)])
    return calckey

def createcfg(host, dbname, port, user, password, type_, url, filejson,
              msg_all_, doc_all_, img_all_, emailrel, tp, browser,
              time_, day, id_Product, key_license, dtat, timeqrcode,
              pflogin, pxbtnsend_, pybtnsend_, timeupimg_, pathexebrowser_,
              px_btnadd, py_btnadd, px_btndoc, py_btndoc, px_btnimg,
              py_btnimg, px_fieldfind, py_fieldfind, px_fieldmsg,
              py_fieldmsg, tmsendmsg):
    try:
        if not id_Product or id_Product == "None":
            id_Product = get_id_maq()
        if not key_license or key_license in ("None", "0"):
            key_license = str(keylicence_toNow())
        if not filejson or filejson == " ":
            filejson = os.getcwd() + '/file.json'
        
        config = configparser.ConfigParser()
        config.add_section('database')
        config.set('database', 'host', host)
        config.set('database', 'dbname', dbname)
        config.set('database', 'port', port)
        config.set('database', 'user', user)
        config.set('database', 'password', password)
        
        config.add_section('repository')
        config.set('repository', 'type', type_)
        config.set('repository', 'url', url)
        config.set('repository', 'filejson', filejson)
        config.set('repository', 'msg_all', msg_all_)
        config.set('repository', 'doc_all', doc_all_)
        config.set('repository', 'img_all', img_all_)
        config.set('repository', 'emailrel', emailrel)
        
        config.add_section('action')
        config.set('action', 'browser', browser)
        config.set('action', 'tp', tp)
        config.set('action', 'time', time_)
        config.set('action', 'day', day)
        config.set('action', 'timeqrcode', str(timeqrcode))
        config.set('action', 'pflogin', str(pflogin))
        config.set('action', 'px_btnsend', pxbtnsend_)
        config.set('action', 'py_btnsend', pybtnsend_)
        config.set('action', 'timeupimg', str(timeupimg_))
        config.set('action', 'pathexebrowser', pathexebrowser_)
        config.set('action', 'px_btn+', str(px_btnadd))
        config.set('action', 'py_btn+', str(py_btnadd))
        config.set('action', 'px_btndoc', str(px_btndoc))
        config.set('action', 'py_btndoc', str(py_btndoc))
        config.set('action', 'px_btnimg', str(px_btnimg))
        config.set('action', 'py_btnimg', str(py_btnimg))
        config.set('action', 'px_fieldfind', str(px_fieldfind))
        config.set('action', 'py_fieldfind', str(py_fieldfind))
        config.set('action', 'px_fieldmsg', str(px_fieldmsg))
        config.set('action', 'py_fieldmsg', str(py_fieldmsg))
        config.set('action', 'timesendmsg', str(tmsendmsg))
        
        config.add_section('active_license')
        config.set('active_license', 'id_Product', str(id_Product))
        config.set('active_license', 'key_license', str(key_license))
        
        with open('config.ini', 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        
        return 'Configurações atualizadas com sucesso!'
    except Exception as e:
        return f'Erro ao criar config: {e}'

def readcfg(filepath, section, param):
    try:
        cfg = configparser.ConfigParser()
        cfg.read(filepath)
        return str(cfg.get(section, param))
    except Exception as e:
        print(f'(readcfg) Erro: {e}')
        return None

def setValue(pathfileCfg, keyparam, value):
    global pxbtnsend, pybtnsend, timeupimg
    tpbrouser = readcfg(pathfileCfg, 'action', 'browser')
    tpsend = readcfg(pathfileCfg, 'action', 'tp')
    time_ = readcfg(pathfileCfg, 'action', 'time')
    days = readcfg(pathfileCfg, 'action', 'day')
    filejson = readcfg(pathfileCfg, 'repository', 'filejson')
    key_license = readcfg(pathfileCfg, 'active_license', 'key_license')
    pxbtnsend = int(readcfg('config.ini', 'action', 'px_btnsend') or 0)
    pybtnsend = int(readcfg('config.ini', 'action', 'py_btnsend') or 0)
    
    if VerifyParamsExists(pathfileCfg, 'action', 'timeupimg'):
        timeupimg = readcfg('config.ini', 'action', 'timeupimg')
    else:
        timeupimg = 26
    
    msg_all = readcfg(pathfileCfg, 'repository', 'msg_all')
    doc_all = readcfg(pathfileCfg, 'repository', 'doc_all')
    img_all = readcfg(pathfileCfg, 'repository', 'img_all')
    return 'Configuração atualizada com sucesso!'

def editcfg(filepath, section, keyparam, value):
    try:
        config = configparser.ConfigParser()
        config.read(filepath)
        if not config.has_section(section):
            config.add_section(section)
        config.set(section, keyparam, str(value))
        with open(filepath, 'w', encoding='utf-8') as configfile:
            config.write(configfile)
        return True
    except Exception as e:
        print(f'(editcfg) Erro: {e}')
        return False

def createfilejson(filepath):
    try:
        with open(filepath, 'w+', encoding='utf-8') as f:
            f.write('[\n\t{\n')
    except Exception as e:
        print(f'(createfilejson) Erro: {e}')

def writefileJson(filepath, text):
    try:
        mode = 'a' if os.path.exists(filepath) else 'w'
        with open(filepath, mode, encoding='utf-8') as f:
            f.write(text + '\n')
    except Exception as e:
        print(f'(writefileJson) Erro: {e}')

def saudahora():
    hora_atual = int(time.strftime('%H', time.localtime()))
    if hora_atual < 12:
        return 'Bom dia!'
    elif hora_atual <= 18:
        return 'Boa tarde!'
    return 'Boa noite!'

# ============================================================
# 🪟 JANELA DE CONFIGURAÇÕES (GUI MODAL)
# ============================================================
def ciar_params(parent):
    """Abre a janela de configurações (modal)"""
    ConfigWindow(parent)


class ConfigWindow(ModalWindow):
    """Janela de configurações com abas"""
    
    def __init__(self, parent):
        # Tamanho mínimo para garantir visualização completa
        super().__init__(parent, title="⚙️ Configurações do Sistema",
                    width=750, height=700)  # Aumentei a altura
        
        self.localapp = os.getcwd()

        self._load_initial_values()
        self._build_ui()
    
    def _load_initial_values(self):
        """Carrega valores iniciais do config.ini com tratamento seguro"""
        from ui_base import safe_int, safe_float
        
        self.id_Product = get_id_maq()
        self.asw_Now = datetime.today().strftime('%y%m%d').replace(".", "")
        
        # Valores padrão
        self.tpbrouser = '1'
        self.tpsend = '1'
        self.time_ = '00:00'
        self.days = '1234567'
        self.msg_all = ''
        self.img_all = ''
        self.doc_all = ''
        self.pxbtnsend = 1588
        self.pybtnsend = 934
        self.pathexebrowser = pathexebrowser
        self.px_btnadd = '560'
        self.py_btnadd = '700'
        self.px_btndoc = '558'
        self.py_btndoc = '440'
        self.px_btnimg = '558'
        self.py_btnimg = '492'
        self.px_fieldfind = '147'
        self.py_fieldfind = '205'
        self.px_fieldmsg = '641'
        self.py_fieldmsg = '700'
        self.emailrel = ''
        self.pflogin = ''
        
        if os.name == 'nt':
            try:
                osUser = os.getlogin()
                self.pflogin = f'C:\\Users\\{osUser}\\AppData\\Local\\Google\\Chrome\\User Data'
            except Exception:
                self.pflogin = r'C:\Users\youuser\AppData\Local\Google\Chrome\User Data'
        
        # Lê do arquivo se existir
        if os.path.isfile('config.ini'):
            try:
                # ===== LEITURA SEGURA COM TRATAMENTO =====
                
                # Browser e tipo de envio (strings)
                self.tpbrouser = readcfg('config.ini', 'action', 'browser') or '1'
                self.tpsend = readcfg('config.ini', 'action', 'tp') or '1'
                self.time_ = readcfg('config.ini', 'action', 'time') or '00:00'
                self.days = readcfg('config.ini', 'action', 'day') or '1234567'
                self.pflogin = readcfg('config.ini', 'action', 'pflogin') or self.pflogin
                
                # ===== POSIÇÕES X/Y (conversão segura para int) =====
                self.pxbtnsend = safe_int(readcfg('config.ini', 'action', 'px_btnsend'), 1316)
                self.pybtnsend = safe_int(readcfg('config.ini', 'action', 'py_btnsend'), 677)
                self.pathexebrowser = readcfg('config.ini', 'action', 'pathexebrowser') or pathexebrowser
                
                # ===== TEMPOS (conversão segura) =====
                global timereadQr, timeupimg
                
                timeqrcode_val = readcfg('config.ini', 'action', 'timeqrcode')
                timereadQr = safe_float(timeqrcode_val, 390.0)
                
                timeupimg_val = readcfg('config.ini', 'action', 'timeupimg')
                timeupimg = safe_int(timeupimg_val, 26)
                
                # ===== EMAIL E MENSAGENS =====
                self.emailrel = readcfg('config.ini', 'repository', 'emailrel') or ''
                self.msg_all = readcfg('config.ini', 'repository', 'msg_all') or ''
                self.img_all = readcfg('config.ini', 'repository', 'img_all') or ''
                self.doc_all = readcfg('config.ini', 'repository', 'doc_all') or ''
                
                # ===== POSIÇÕES DOS BOTÕES (conversão segura) =====
                self.px_btnadd = str(safe_int(readcfg('config.ini', 'action', 'px_btn+'), 560))
                self.py_btnadd = str(safe_int(readcfg('config.ini', 'action', 'py_btn+'), 700))
                self.px_btndoc = str(safe_int(readcfg('config.ini', 'action', 'px_btndoc'), 558))
                self.py_btndoc = str(safe_int(readcfg('config.ini', 'action', 'py_btndoc'), 440))
                self.px_btnimg = str(safe_int(readcfg('config.ini', 'action', 'px_btnimg'), 558))
                self.py_btnimg = str(safe_int(readcfg('config.ini', 'action', 'py_btnimg'), 492))
                self.px_fieldfind = str(safe_int(readcfg('config.ini', 'action', 'px_fieldfind'), 147))
                self.py_fieldfind = str(safe_int(readcfg('config.ini', 'action', 'py_fieldfind'), 205))
                self.px_fieldmsg = str(safe_int(readcfg('config.ini', 'action', 'px_fieldmsg'), 641))
                self.py_fieldmsg = str(safe_int(readcfg('config.ini', 'action', 'py_fieldmsg'), 700))
                
                print("✅ Configurações carregadas com sucesso!")
                
            except Exception as e:
                print(f'⚠️ Erro ao ler config.ini: {e}')
                print('Usando valores padrão...')
                # Mantém os valores padrão já definidos acima


    def _build_ui(self):
        """Constrói a interface com abas"""
        # Notebook (abas)
        notebook = ttkb.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Aba 1: Dados Gerais
        tab1 = tk.Frame(notebook, bg=Colors.BG_MAIN)
        notebook.add(tab1, text=f" {Icons.CONFIG} Dados Gerais ")
        self._build_tab_dados(tab1)
        
        # Aba 2: Movimento (Posições)
        tab2 = tk.Frame(notebook, bg=Colors.BG_MAIN)
        notebook.add(tab2, text=f" {Icons.BROWSER} Movimento ")
        self._build_tab_movimento(tab2)
        
        # Aba 3: Tempos
        tab3 = tk.Frame(notebook, bg=Colors.BG_MAIN)
        notebook.add(tab3, text=f" {Icons.CLOCK} Tempos ")
        self._build_tab_tempos(tab3)
        
        # Botões inferiores
        btn_frame = tk.Frame(self, bg=Colors.BG_MAIN, height=60)
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        btn_frame.pack_propagate(False)
        
        ttkb.Button(
            btn_frame, text="✕ Cancelar",
            style="secondary.TButton",
            command=self.on_close
        ).pack(side="left", padx=5)
        
        ttkb.Button(
            btn_frame, text="💾 Salvar Configurações",
            style="primary.TButton",
            command=self._save_config
        ).pack(side="right", padx=5)
    
    def _build_tab_dados(self, parent):
        """Aba de dados gerais - Layout totalmente responsivo"""
        # Container principal com scroll
        canvas = tk.Canvas(parent, bg=Colors.BG_MAIN, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw", width=canvas.winfo_width())
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Bind para ajustar largura do frame interno quando o canvas redimensiona
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # ===== CARD 1: NAVEGADOR =====
        card1 = CardFrame(scroll_frame, title=f"{Icons.BROWSER} Navegador")
        card1.pack(fill="x", padx=15, pady=(15, 10))
        
        inner1 = tk.Frame(card1, bg=Colors.BG_WHITE)
        inner1.pack(fill="x", padx=15, pady=15)
        
        # Tipo de navegador - usando grid para responsividade
        tk.Label(inner1, text="Tipo de navegador:",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.cb_browser = ttkb.Combobox(inner1, values=['1 - Chrome', '2 - Firefox'],
                                    state="readonly")
        self.cb_browser.set(f"{self.tpbrouser} - {'Chrome' if self.tpbrouser == '1' else 'Firefox'}")
        self.cb_browser.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        # Caminho do executável
        tk.Label(inner1, text="Caminho do executável:",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        path_frame = tk.Frame(inner1, bg=Colors.BG_WHITE)
        path_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        path_frame.columnconfigure(0, weight=1)  # Entry expande
        
        self.entry_browser_path = ttkb.Entry(path_frame)
        self.entry_browser_path.insert(0, self.pathexebrowser)
        self.entry_browser_path.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ttkb.Button(
            path_frame, text="📁", style="secondary.TButton", width=3,
            command=lambda: self._browse_file(self.entry_browser_path)
        ).grid(row=0, column=1)
        
        # Configurar coluna para expandir
        inner1.columnconfigure(0, weight=1)
        
        # ===== CARD 2: PERFIL WHATSAPP =====
        card2 = CardFrame(scroll_frame, title=f"{Icons.WHATSAPP} Perfil WhatsApp")
        card2.pack(fill="x", padx=15, pady=10)
        
        inner2 = tk.Frame(card2, bg=Colors.BG_WHITE)
        inner2.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner2, text="Local do perfil de login:",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        path_frame2 = tk.Frame(inner2, bg=Colors.BG_WHITE)
        path_frame2.grid(row=1, column=0, sticky="ew")
        path_frame2.columnconfigure(0, weight=1)
        
        self.entry_pflogin = ttkb.Entry(path_frame2)
        self.entry_pflogin.insert(0, self.pflogin)
        self.entry_pflogin.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        ttkb.Button(
            path_frame2, text="📁", style="secondary.TButton", width=3,
            command=lambda: self._browse_dir(self.entry_pflogin)
        ).grid(row=0, column=1)
        
        inner2.columnconfigure(0, weight=1)
        
        # ===== CARD 3: EMAIL =====
        card3 = CardFrame(scroll_frame, title=f"{Icons.EMAIL} Email para Relatórios")
        card3.pack(fill="x", padx=15, pady=10)
        
        inner3 = tk.Frame(card3, bg=Colors.BG_WHITE)
        inner3.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner3, text="Endereço de email:",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.entry_email = ttkb.Entry(inner3)
        self.entry_email.insert(0, self.emailrel or "seuemail@email.com")
        self.entry_email.grid(row=1, column=0, sticky="ew")
        
        inner3.columnconfigure(0, weight=1)
        
        # ===== CARD 4: LICENÇA (COM BOTÃO ATUALIZAR ONLINE VISÍVEL) =====
        card4 = CardFrame(scroll_frame, title=f"{Icons.KEY} Licença e Ativação")
        card4.pack(fill="x", padx=15, pady=(10, 15))
        
        inner4 = tk.Frame(card4, bg=Colors.BG_WHITE)
        inner4.pack(fill="x", padx=15, pady=15)
        
        # ID da Máquina
        tk.Label(inner4, text="🖥️ ID da Máquina:",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        #id_Product = get_id_maq()
        id_Product = extract_number(str(self.id_Product))
        id_display = id_Product[0:2] + id_Product[-2:] if len(id_Product) > 4 else id_Product
        
        id_frame = tk.Frame(inner4, bg=Colors.PRIMARY_LIGHT, relief="solid", bd=1)
        id_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        tk.Label(id_frame, text=f"  {id_Product}  ",
                font=("Segoe UI", 12, "bold"),
                bg=Colors.PRIMARY_LIGHT, fg=Colors.PRIMARY,
                padx=15, pady=8).pack()
        
        # Chave de Licença
        tk.Label(inner4, text="🔑 Chave de Licença:",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        # Frame para Entry + Botão - usando grid para garantir visibilidade
        key_frame = tk.Frame(inner4, bg=Colors.BG_WHITE)
        key_frame.grid(row=3, column=0, sticky="ew", pady=(0, 10))
        key_frame.columnconfigure(0, weight=1)  # Entry expande
        
        self.entry_key = ttkb.Entry(key_frame, font=("Consolas", 10))
        self.entry_key.insert(0, id_display[0:2]+str(keylicence_toNow())+id_display[2:4])
        self.entry_key.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=3)
        
        # ⭐ BOTÃO ATUALIZAR ONLINE - AGORA VISÍVEL E DESTACADO
        self.btn_update_key = ttkb.Button(
            key_frame, 
            text=f"{Icons.REFRESH} Atualizar Online",
            style="warning.TButton",
            command=self._update_key_online
        )
        self.btn_update_key.grid(row=0, column=1, sticky="e")
        
        # Dica informativa
        tk.Label(inner4, 
                text="💡 Clique em 'Atualizar Online' para abrir o navegador e gerar/renovar sua chave de licença.",
                font=("Segoe UI", 9, "italic"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY,
                anchor="w", wraplength=600, justify="left").grid(row=4, column=0, sticky="w", pady=(5, 0))
        
        inner4.columnconfigure(0, weight=1)
        
        # ===== CARD 5: ENVIO E OPERAÇÃO =====
        card5 = CardFrame(scroll_frame, title=f"{Icons.SEND} Modo de Envio")
        card5.pack(fill="x", padx=15, pady=(0, 15))
        
        inner5 = tk.Frame(card5, bg=Colors.BG_WHITE)
        inner5.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner5, text="Tipo de envio:",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.cb_send_type = ttkb.Combobox(inner5, 
                                        values=['1 - Manual', '2 - Automático'],
                                        state="readonly")
        self.cb_send_type.set(f"{self.tpsend} - {'Manual' if self.tpsend == '1' else 'Automático'}")
        self.cb_send_type.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        
        tk.Label(inner5, text="Dias da semana para envio (1=Dom, 2=Seg, ... 7=Sáb):",
                font=("Segoe UI", 10, "bold"), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").grid(row=2, column=0, sticky="w", pady=(0, 5))
        
        self.entry_days = ttkb.Entry(inner5)
        self.entry_days.insert(0, self.days)
        self.entry_days.grid(row=3, column=0, sticky="ew")
        
        tk.Label(inner5, 
                text="💡 Exemplo: '1234567' = todos os dias, '23456' = segunda a sexta",
                font=("Segoe UI", 9, "italic"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY,
                anchor="w").grid(row=4, column=0, sticky="w", pady=(5, 0))
        
        inner5.columnconfigure(0, weight=1)

    def _build_tab_movimento(self, parent):
        """Aba de posições de movimento"""
        canvas = tk.Canvas(parent, bg=Colors.BG_MAIN, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Card: Posições dos campos
        card = CardFrame(scroll_frame, title=f"{Icons.FILTER} Posições dos Elementos")
        card.pack(fill="x", padx=15, pady=15)
        
        inner = tk.Frame(card, bg=Colors.BG_WHITE)
        inner.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner, text="Configure as coordenadas X,Y dos elementos do WhatsApp Web.\n"
                           "Use o botão 'Capturar Mouse' para obter as posições da sua tela.",
                font=("Segoe UI", 9, "italic"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY,
                anchor="w", justify="left").pack(fill="x", pady=(0, 15))
        
        # Grid de posições
        positions = [
            ("Campo Pesquisar", "px_fieldfind", "py_fieldfind"),
            ("Botão + (Anexar)", "px_btnadd", "py_btnadd"),
            ("Botão Documento", "px_btndoc", "py_btndoc"),
            ("Botão Imagem", "px_btnimg", "py_btnimg"),
            ("Campo Mensagem", "px_fieldmsg", "py_fieldmsg"),
            ("Botão Enviar", "pxbtnsend", "pybtnsend"),
        ]
        
        self.pos_entries = {}
        
        for label, px_key, py_key in positions:
            row = tk.Frame(inner, bg=Colors.BG_WHITE)
            row.pack(fill="x", pady=5)
            
            tk.Label(row, text=label, font=("Segoe UI", 10),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                    width=20, anchor="w").pack(side="left")
            
            tk.Label(row, text="X:", font=("Segoe UI", 10, "bold"),
                    bg=Colors.BG_WHITE, fg=Colors.PRIMARY, width=2).pack(side="left")
            
            px_entry = ttkb.Entry(row, width=8)
            px_entry.insert(0, str(getattr(self, px_key)))
            px_entry.pack(side="left", padx=(0, 10))
            
            tk.Label(row, text="Y:", font=("Segoe UI", 10, "bold"),
                    bg=Colors.BG_WHITE, fg=Colors.PRIMARY, width=2).pack(side="left")
            
            py_entry = ttkb.Entry(row, width=8)
            py_entry.insert(0, str(getattr(self, py_key)))
            py_entry.pack(side="left")
            
            self.pos_entries[px_key] = px_entry
            self.pos_entries[py_key] = py_entry
        
        # Botão capturar mouse
        ttkb.Button(
            inner, text="🖱️ Capturar Posição do Mouse",
            style="info.TButton",
            command=self._capture_mouse_position
        ).pack(fill="x", pady=(20, 0))
    
    def _build_tab_tempos(self, parent):
        """Aba de tempos de espera"""
        canvas = tk.Canvas(parent, bg=Colors.BG_MAIN, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Tempo QR Code
        card1 = CardFrame(scroll_frame, title=f"{Icons.CLOCK} Tempo de Leitura do QR Code")
        card1.pack(fill="x", padx=15, pady=(15, 10))
        
        inner1 = tk.Frame(card1, bg=Colors.BG_WHITE)
        inner1.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner1, text="Tempo para aguardar leitura do QR Code (segundos):",
                font=("Segoe UI", 10), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        
        self.scale_qrcode = ttkb.Scale(inner1, from_=0, to=1000,
                                       value=timereadQr, orient="horizontal")
        self.scale_qrcode.pack(fill="x", pady=10)
        
        self.lbl_qrcode_val = tk.Label(inner1, text=f"{int(timereadQr)}s",
                                       font=("Segoe UI", 11, "bold"),
                                       bg=Colors.PRIMARY_LIGHT, fg=Colors.PRIMARY,
                                       padx=10, pady=5)
        self.lbl_qrcode_val.pack()
        
        self.scale_qrcode.configure(command=lambda v: self.lbl_qrcode_val.configure(
            text=f"{int(float(v))}s"))
        
        # Tempo envio mensagem
        card2 = CardFrame(scroll_frame, title=f"{Icons.SEND} Tempo de Envio da Mensagem")
        card2.pack(fill="x", padx=15, pady=10)
        
        inner2 = tk.Frame(card2, bg=Colors.BG_WHITE)
        inner2.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner2, text="Tempo para aguardar envio da mensagem (segundos):",
                font=("Segoe UI", 10), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        
        self.scale_sendmsg = ttkb.Scale(inner2, from_=0, to=1000,
                                       value=timesendmsg, orient="horizontal")
        self.scale_sendmsg.pack(fill="x", pady=10)
        
        self.lbl_sendmsg_val = tk.Label(inner2, text=f"{int(timesendmsg)}s",
                                        font=("Segoe UI", 11, "bold"),
                                        bg=Colors.PRIMARY_LIGHT, fg=Colors.PRIMARY,
                                        padx=10, pady=5)
        self.lbl_sendmsg_val.pack()
        
        self.scale_sendmsg.configure(command=lambda v: self.lbl_sendmsg_val.configure(
            text=f"{int(float(v))}s"))
        
        # Tempo upload imagem
        card3 = CardFrame(scroll_frame, title=f"{Icons.IMAGE} Tempo de Upload de Imagem")
        card3.pack(fill="x", padx=15, pady=(10, 15))
        
        inner3 = tk.Frame(card3, bg=Colors.BG_WHITE)
        inner3.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner3, text="Tempo para aguardar upload de imagem (segundos):",
                font=("Segoe UI", 10), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        
        self.scale_upimg = ttkb.Scale(inner3, from_=0, to=1000,
                                     value=timeupimg, orient="horizontal")
        self.scale_upimg.pack(fill="x", pady=10)
        
        self.lbl_upimg_val = tk.Label(inner3, text=f"{int(timeupimg)}s",
                                      font=("Segoe UI", 11, "bold"),
                                      bg=Colors.PRIMARY_LIGHT, fg=Colors.PRIMARY,
                                      padx=10, pady=5)
        self.lbl_upimg_val.pack()
        
        self.scale_upimg.configure(command=lambda v: self.lbl_upimg_val.configure(
            text=f"{int(float(v))}s"))
    
    def _browse_file(self, entry):
        """Abre diálogo para selecionar arquivo"""
        path = filedialog.askopenfilename(parent=self)
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)
    
    def _browse_dir(self, entry):
        """Abre diálogo para selecionar pasta"""
        path = filedialog.askdirectory(parent=self)
        if path:
            entry.delete(0, "end")
            entry.insert(0, path)
    
    def _update_key_online(self):
        """Abre navegador para atualizar chave"""
        import webbrowser
        id_maq = get_id_maq()
        id_short = extract_number(id_maq)#extrai apenas os numeros da string
        id_short = id_maq[0:2] + id_maq[-2:] if len(id_maq) > 4 else id_maq        
        id_short = id_short.replace(' ','')#remove os espaços da string
        id_short = id_short[0:2] + id_short[len(id_short)-2:len(id_short)]
        url = f'https://tmx.infinityfreeapp.com/gkey.php?i={id_short}&k={self.entry_key.get()}'
        webbrowser.open(url)
    
    def _capture_mouse_position(self):
        """Captura posição do mouse"""
        try:
            import pyautogui
            self.show_message("Captura", 
                            "Posicione o mouse sobre o elemento e aguarde 3 segundos...")
            self.after(3000, lambda: self._show_mouse_pos(pyautogui.position()))
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao capturar mouse:\n{e}")
    
    def _show_mouse_pos(self, pos):
        """Mostra posição capturada"""
        show_info(self, "Posição Capturada",
                 f"Mouse em: X={pos.x}, Y={pos.y}\n\n"
                 f"Copie esses valores para os campos desejados.")
    
    def _save_config(self):
        """Salva as configurações"""
        if not ask_yes_no(self, "Confirmar", "Deseja realmente salvar as configurações?"):
            return
        
        try:
            # Coleta valores
            browser_val = self.cb_browser.get().split(' - ')[0]
            pflogin = self.entry_pflogin.get()
            email = self.entry_email.get()
            key = self.entry_key.get()
            browser_path = self.entry_browser_path.get()
            
            # Posições
            px_fieldfind = self.pos_entries['px_fieldfind'].get()
            py_fieldfind = self.pos_entries['py_fieldfind'].get()
            px_btnadd = self.pos_entries['px_btnadd'].get()
            py_btnadd = self.pos_entries['py_btnadd'].get()
            px_btndoc = self.pos_entries['px_btndoc'].get()
            py_btndoc = self.pos_entries['py_btndoc'].get()
            px_btnimg = self.pos_entries['px_btnimg'].get()
            py_btnimg = self.pos_entries['py_btnimg'].get()
            px_fieldmsg = self.pos_entries['px_fieldmsg'].get()
            py_fieldmsg = self.pos_entries['py_fieldmsg'].get()
            px_btnsend = self.pos_entries['pxbtnsend'].get()
            py_btnsend = self.pos_entries['pybtnsend'].get()
            
            # Tempos
            timeqrcode = int(float(self.scale_qrcode.get()))
            timesendmsg_ = int(float(self.scale_sendmsg.get()))
            timeupimg_ = int(float(self.scale_upimg.get()))
            
            # Salva
            createcfg(
                'localhost', 'example', '1234', 'admin', 'secret',
                'git', 'git@github.com:user/project.git',
                '', self.msg_all, self.doc_all, self.img_all, email,
                self.tpsend, browser_val, self.time_, self.days,
                self.id_Product, key, self.asw_Now,
                str(timeqrcode), pflogin,
                px_btnsend, py_btnsend, str(timeupimg_), browser_path,
                px_btnadd, py_btnadd, px_btndoc, py_btndoc,
                px_btnimg, py_btnimg, px_fieldfind, py_fieldfind,
                px_fieldmsg, py_fieldmsg, str(timesendmsg_)
            )
            
            # Atualiza variáveis globais
            global timereadQr, timesendmsg, timeupimg, pathexebrowser
            timereadQr = timeqrcode
            timesendmsg = timesendmsg_
            timeupimg = timeupimg_
            pathexebrowser = browser_path
            
            show_info(self, "Sucesso", "Configurações salvas com sucesso!")
            self.on_close()
            
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao salvar configurações:\n{e}")
