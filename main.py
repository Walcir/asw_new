# -*- coding: utf-8 -*-
"""
main.py - Tela principal ASW com sidebar estilo WhatsApp Web
"""
import os
import sys
from datetime import datetime
from time import sleep
import tkinter as tk
from tkinter import messagebox as msgbx
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

# Módulos do projeto
import config as cfg
import campaigns as camp
import contacts as ctc
import databases as db
from ui_base import (ModalWindow, Colors, Icons, SidebarButton, 
                     CardFrame, show_info, show_warning, ask_yes_no)

# ============================================================
# 🌍 VARIÁVEIS GLOBAIS
# ============================================================
Eventos = "Eventos "
filejson = "Enviar.json "
localapp = os.getcwd()

def obter_caminho_recurso(caminho_relativo):
    """ Retorna o caminho absoluto para o recurso, funcionando em desenvolvimento e no PyInstaller """
    try:
        # O PyInstaller cria uma pasta temporária e define a variável _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Se não estiver rodando pelo PyInstaller, usa o caminho normal do script
        base_path = os.path.abspath(".")
    return os.path.join(base_path, caminho_relativo)

# ============================================================
# 🚀 CLASSE PRINCIPAL: ASW APPLICATION
# ============================================================
class ASWApplication(ttkb.Window):
    """Janela principal com sidebar estilo WhatsApp Web"""
    
    def __init__(self):
        super().__init__(title="ASW - Auto Send WhatsApp",themename="cyborg")
        
        # Configuração da janela
        self.geometry("1100x700+150+50")
        self.minsize(900, 600)
        self.configure(bg=Colors.BG_MAIN)
        
        # Ícone
        try:
            icon_path = os.path.join(localapp, "icons", "ASW.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Estado
        self.current_section = "home"
        self.sidebar_buttons = {}
        
        # Monta a interface
        self._build_ui()
        
        # Verifica licença e campanhas pendentes
        self._check_license()
        
        # Protocolo de fechamento
        self.protocol("WM_DELETE_WINDOW", self._on_close)
    
    # ========================================================
    # 🔨 CONSTRUÇÃO DA INTERFACE
    # ========================================================
    def _build_ui(self):
        """Constrói a interface principal"""
        # Container principal (sidebar + content)
        main_container = ttkb.Frame(self, style="Main.TFrame")
        main_container.pack(fill="both", expand=True)
        
        # Sidebar esquerda
        self._build_sidebar(main_container)
        
        # Área de conteúdo
        self._build_content_area(main_container)
    
    def _build_sidebar(self, parent):
        """Constrói a sidebar estilo WhatsApp Web"""
        sidebar = tk.Frame(parent, bg=Colors.BG_SIDEBAR, width=280)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        
        # ===== HEADER: Logo e título =====
        header = tk.Frame(sidebar, bg=Colors.PRIMARY, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="💬  ASW Messenger",
            font=("Segoe UI", 14, "bold"),
            bg=Colors.PRIMARY,
            fg=Colors.TEXT_LIGHT
        ).pack(side="left", padx=20, pady=20)
        
        # ===== PERFIL DO USUÁRIO =====
        profile = tk.Frame(sidebar, bg=Colors.BG_SIDEBAR, height=80)
        profile.pack(fill="x")
        profile.pack_propagate(False)
        
        # Avatar circular
        avatar_canvas = tk.Canvas(profile, width=50, height=50,
                                  bg=Colors.BG_SIDEBAR, highlightthickness=0)
        avatar_canvas.pack(side="left", padx=15, pady=15)
        avatar_canvas.create_oval(2, 2, 48, 48, fill=Colors.PRIMARY, outline="")
        avatar_canvas.create_text(25, 25, text="👤", font=("Segoe UI Emoji", 20))
        
        # Info do perfil
        info_frame = tk.Frame(profile, bg=Colors.BG_SIDEBAR)
        info_frame.pack(side="left", fill="y", pady=15)
        
        tk.Label(
            info_frame, text="ASW System",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.BG_SIDEBAR, fg=Colors.TEXT_PRIMARY, anchor="w"
        ).pack(anchor="w")
        
        tk.Label(
            info_frame, text="Auto Send WhatsApp",
            font=("Segoe UI", 9),
            bg=Colors.BG_SIDEBAR, fg=Colors.TEXT_SECONDARY, anchor="w"
        ).pack(anchor="w")
        
        # Divisor
        tk.Frame(sidebar, height=1, bg=Colors.BORDER).pack(fill="x")
        
        # ===== MENU DE NAVEGAÇÃO =====
        menu_frame = tk.Frame(sidebar, bg=Colors.BG_SIDEBAR)
        menu_frame.pack(fill="both", expand=True, pady=10)
        
        tk.Label(
            menu_frame, text="MENU PRINCIPAL",
            font=("Segoe UI", 9, "bold"),
            bg=Colors.BG_SIDEBAR, fg=Colors.TEXT_MUTED, anchor="w"
        ).pack(fill="x", padx=20, pady=(10, 5))
        
        # Botões do menu
        menu_items = [
            ("home",     Icons.WHATSAPP, "Início",           self._show_home),
            ("config",   Icons.CONFIG,   "Configurações",    self._open_config),
            ("campaign", Icons.CAMPAIGN, "Campanhas",        self._open_campaigns),
            ("contact",  Icons.CONTACT,  "Contatos",         self._open_contacts),
            ("send",     Icons.SEND,     "Envio por Arquivo", self._open_send_file),
            ("msg",      Icons.MESSAGE,  "Mensagem p/ Todos", self._open_msg_all),
            ("report",   Icons.REPORT,   "Relatórios",       self._open_reports),
            ("help",     Icons.HELP,     "Ajuda e Suporte",  self._open_help),
        ]
        
        for key, icon, text, command in menu_items:
            btn = SidebarButton(menu_frame, icon, text, command,
                              active=(key == "home"))
            btn.pack(fill="x")
            self.sidebar_buttons[key] = btn
        
        # ===== FOOTER: Status da licença =====
        tk.Frame(sidebar, height=1, bg=Colors.BORDER).pack(fill="x", side="bottom")
        
        footer = tk.Frame(sidebar, bg=Colors.BG_SIDEBAR, height=70)
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)
        
        self.license_label = tk.Label(
            footer, text="🔑 Verificando licença...",
            font=("Segoe UI", 9),
            bg=Colors.BG_SIDEBAR, fg=Colors.TEXT_SECONDARY, anchor="w"
        )
        self.license_label.pack(fill="x", padx=20, pady=10)
        
        self._update_license_status()
    
    def _build_content_area(self, parent):
        """Constrói a área de conteúdo principal"""
        # Container direito
        content = tk.Frame(parent, bg=Colors.BG_MAIN)
        content.pack(side="left", fill="both", expand=True)
        
        # Header da área de conteúdo
        self.content_header = tk.Frame(content, bg=Colors.BG_WHITE, height=70)
        self.content_header.pack(fill="x")
        self.content_header.pack_propagate(False)
        
        self.title_label = tk.Label(
            self.content_header, text="🏠  Bem-vindo ao ASW",
            font=("Segoe UI", 14, "bold"),
            bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY
        )
        self.title_label.pack(side="left", padx=25, pady=20)
        
        # Status label (direita)
        self.status_label = tk.Label(
            self.content_header, text="● Online",
            font=("Segoe UI", 10),
            bg=Colors.BG_WHITE, fg=Colors.SUCCESS
        )
        self.status_label.pack(side="right", padx=25)
        
        # Divisor
        tk.Frame(content, height=1, bg=Colors.BORDER).pack(fill="x")
        
        # Área de conteúdo (scrollável)
        self.content_body = tk.Frame(content, bg=Colors.BG_MAIN)
        self.content_body.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Mostra a home inicialmente
        self._show_home()
    
    # ========================================================
    # 📄 SEÇÕES DE CONTEÚDO
    # ========================================================
    def _clear_content(self):
        """Limpa a área de conteúdo"""
        for widget in self.content_body.winfo_children():
            widget.destroy()
    
    def _set_active_menu(self, key):
        """Define o menu ativo"""
        for k, btn in self.sidebar_buttons.items():
            btn.set_active(k == key)
    
    def _show_home(self):
        """Mostra a tela inicial"""
        self._clear_content()
        self._set_active_menu("home")
        self.title_label.configure(text="🏠  Painel Principal")
        
        # Scroll frame
        canvas = tk.Canvas(self.content_body, bg=Colors.BG_MAIN,
                          highlightthickness=0)
        scrollbar = ttkb.Scrollbar(self.content_body, orient="vertical",
                                  command=canvas.yview)
        scroll_frame = ttkb.Frame(canvas, style="Main.TFrame")
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")
        
        # ===== Cards de boas-vindas =====
        welcome_card = CardFrame(scroll_frame, title="👋 Bem-vindo ao ASW Messenger")
        welcome_card.pack(fill="x", pady=(0, 15))
        
        welcome_text = tk.Frame(welcome_card, bg=Colors.BG_WHITE)
        welcome_text.pack(fill="x", padx=20, pady=15)
        
        
        tk.Label(
            welcome_text,
            text="Sistema de Automação de Envio para WhatsApp",
            font=("Segoe UI", 12, "bold"),
            bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x")
        
        tk.Label(
            welcome_text,
            text="Envie mensagens, imagens e documentos de forma automatizada "
                 "para seus contatos e grupos. Use o menu lateral para navegar.",
            font=("Segoe UI", 10),
            bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY,
            anchor="w", wraplength=600, justify="left"
        ).pack(fill="x", pady=(10, 0))
        
        # ===== Cards de ações rápidas =====
        tk.Label(
            scroll_frame, text="⚡ AÇÕES RÁPIDAS",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(10, 10))
        
        actions_grid = ttkb.Frame(scroll_frame, style="Main.TFrame")
        actions_grid.pack(fill="x")
        
        quick_actions = [
            (Icons.CONFIG,   "Configurações",     "Ajustar parâmetros",     self._open_config),
            (Icons.CAMPAIGN, "Campanhas",         "Gerenciar campanhas",    self._open_campaigns),
            (Icons.CONTACT,  "Contatos",          "Gerenciar contatos",     self._open_contacts),
            (Icons.SEND,     "Envio Rápido",      "Enviar por arquivo",     self._open_send_file),
            (Icons.MESSAGE,  "Mensagem Geral",    "Msg para todos",         self._open_msg_all),
            (Icons.REPORT,   "Relatórios",        "Ver logs e relatórios",  self._open_reports),
        ]
        
        for i, (icon, title, desc, cmd) in enumerate(quick_actions):
            row, col = divmod(i, 3)
            
            card = tk.Frame(actions_grid, bg=Colors.BG_WHITE,
                          relief="raised", bd=1, cursor="hand2")
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            actions_grid.grid_columnconfigure(col, weight=1)
            
            inner = tk.Frame(card, bg=Colors.BG_WHITE, padx=20, pady=20)
            inner.pack(fill="both", expand=True)
            
            tk.Label(inner, text=icon, font=("Segoe UI Emoji", 28),
                    bg=Colors.BG_WHITE).pack(pady=(0, 10))
            tk.Label(inner, text=title, font=("Segoe UI", 11, "bold"),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack()
            tk.Label(inner, text=desc, font=("Segoe UI", 9),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY).pack(pady=(5, 0))
            
            # Hover effects
            def on_enter(e, c=card):
                c.configure(bg=Colors.PRIMARY_LIGHT)
                for w in c.winfo_children():
                    if isinstance(w, tk.Frame):
                        w.configure(bg=Colors.PRIMARY_LIGHT)
                        for child in w.winfo_children():
                            if isinstance(child, tk.Label):
                                child.configure(bg=Colors.PRIMARY_LIGHT)
            
            def on_leave(e, c=card):
                c.configure(bg=Colors.BG_WHITE)
                for w in c.winfo_children():
                    if isinstance(w, tk.Frame):
                        w.configure(bg=Colors.BG_WHITE)
                        for child in w.winfo_children():
                            if isinstance(child, tk.Label):
                                if child.cget("font") == ("Segoe UI", 11, "bold"):
                                    child.configure(bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY)
                                else:
                                    child.configure(bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY)
            
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)
            for w in [inner] + inner.winfo_children():
                w.bind("<Button-1>", lambda e, c=cmd: c())
                w.bind("<Enter>", on_enter)
                w.bind("<Leave>", on_leave)
        
        # ===== Card de informações do sistema =====
        tk.Label(
            scroll_frame, text="ℹ️ INFORMAÇÕES DO SISTEMA",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(20, 10))
        
        info_card = CardFrame(scroll_frame)
        info_card.pack(fill="x", pady=(0, 20))
        
        info_frame = tk.Frame(info_card, bg=Colors.BG_WHITE)
        info_frame.pack(fill="x", padx=20, pady=15)
        
        # ID da máquina
        try:
            machine_id = cfg.get_id_maq()
            machine_id = cfg.extract_number(machine_id)
            short_id = machine_id[0:2] + machine_id[-2:] if len(machine_id) > 4 else machine_id
        except Exception:
            short_id = "N/A"
        
        info_items = [
            (Icons.USER,    "ID da Máquina", short_id),
            (Icons.CALENDAR, "Data/Hora",     datetime.now().strftime("%d/%m/%Y %H:%M")),
            (Icons.BROWSER, "Sistema",        f"{os.name} - {sys.platform}"),
            (Icons.FILE,    "Pasta",          localapp),
        ]
        
        for icon, label, value in info_items:
            row = tk.Frame(info_frame, bg=Colors.BG_WHITE)
            row.pack(fill="x", pady=5)
            
            tk.Label(row, text=icon, font=("Segoe UI Emoji", 14),
                    bg=Colors.BG_WHITE, width=3).pack(side="left")
            tk.Label(row, text=label, font=("Segoe UI", 10, "bold"),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                    width=15, anchor="w").pack(side="left")
            tk.Label(row, text=value, font=("Segoe UI", 10),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY,
                    anchor="w").pack(side="left", fill="x", expand=True)
    
    # ========================================================
    # 🚀 ABRIR JANELAS MODAIS
    # ========================================================
    def _open_config(self):
        """Abre janela de configurações"""
        self._set_active_menu("config")
        try:
            cfg.ciar_params(self)
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao abrir configurações:\n{e}")
    
    def _open_campaigns(self):
        """Abre janela de campanhas"""
        self._set_active_menu("campaign")
        try:
            camp.menu_Showcamp(self)
        except Exception as e:
            from tools import update_log as uplog
            uplog(f"Erro ao abrir campanhas:\n{e}")
            show_warning(self, "Erro", f"Erro ao abrir campanhas:\n{e}")
    
    def _open_contacts(self):
        """Abre janela de contatos"""
        self._set_active_menu("contact")
        try:
            ctc.menu_Showcontact(self)
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao abrir contatos:\n{e}")
    
    def _open_send_file(self):
        """Abre diálogo de envio por arquivo"""
        self._set_active_menu("send")
        try:
            self._click2_Json()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao abrir envio:\n{e}")
    
    def _open_msg_all(self):
        """Abre janela de mensagem para todos"""
        self._set_active_menu("msg")
        try:
            self._window_msg_all()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao abrir mensagem:\n{e}")
    
    def _open_reports(self):
        """Abre relatórios"""
        self._set_active_menu("report")
        try:
            # Tenta importar o módulo de relatórios
            try:
                import RpGraphics as rp
                rp.showreport_msg()
            except ImportError:
                self._show_log_viewer()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao abrir relatórios:\n{e}")
    
    def _open_help(self):
        """Abre ajuda e suporte"""
        self._set_active_menu("help")
        HelpWindow(self)
    
    # ========================================================
    # 📤 LÓGICA DE ENVIO POR ARQUIVO
    # ========================================================
    def _click2_Json(self):
        """Seleciona arquivo JSON e inicia envio"""
        from tkinter.filedialog import askopenfilename
        
        filejson = askopenfilename(
            parent=self,
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Selecione o arquivo JSON para envio"
        )
        
        if not filejson:
            return
        
        self.status_label.configure(text="● Processando...", fg=Colors.WARNING)
        
        try:
            # Lê configurações
            tpbrouser = cfg.readcfg('config.ini', 'action', 'browser')
            tpsend = cfg.readcfg('config.ini', 'action', 'tp')
            
            '''
            show_info(self, "Arquivo Selecionado",
                     f"Arquivo JSON selecionado:\n{filejson}\n\n"
                     f"Iniciando processo de envio...")
            '''
            self.status_label.configure(text=f"Arquivo Json selecionado:{filejson} Iniciando o processo de envio!",fg=Colors.PRIMARY_LIGHT)
            
            # Inicia envio
            cfg.cleanFile(localapp+'/ASW.log')#clean file log /limpa o
            import rpa
            rpa.sendSingleMessage(0, filejson)
            
            self.status_label.configure(text="● Online", fg=Colors.SUCCESS)
           #? show_info(self, "Sucesso", "Envio concluído com sucesso!")
            
        except Exception as e:
            self.status_label.configure(text="● Erro", fg=Colors.DANGER)
            '''show_warning(self, "Erro no Envio",
                        f"Erro ao processar envio:\n{e}")'''
    
    # ========================================================
    # 💬 JANELA DE MENSAGEM PARA TODOS
    # ========================================================
    def _window_msg_all(self):
        """Abre janela para editar mensagem para todos"""
        MsgAllWindow(self)
    
    # ========================================================
    # 📊 VISUALIZADOR DE LOG
    # ========================================================
    def _show_log_viewer(self):
        """Mostra visualizador de log"""
        LogViewerWindow(self)
    
    # ========================================================
    # 🔑 LICENÇA
    # ========================================================
    def _update_license_status(self):
        """Atualiza o status da licença no footer"""
        try:
            import config as cfg
            if os.path.exists('config.ini'):
                linc = cfg.readcfg('config.ini', 'active_license', 'key_license')
                cfg.dtvenclicense=cfg.getVenc_lic(licenca=linc)
                vencimento = cfg.dtvenclicense
                vencimento = vencimento[4:6]+"/"+vencimento[2:4]+"/"+vencimento[0:2]
                if linc and linc != 'None':
                    if (cfg.VerifyVencdate(datetime.now(),cfg.dtvenclicense)==True):
                        self.license_label.configure(                        
                            
                            text=f"🔑 Licença ativa vencimento:{vencimento} ",
                            fg=Colors.SUCCESS
                        )
                    else:
                        self.license_label.configure(
                        text=f"🔑 Licença: vencida em: {vencimento} ",
                        fg=Colors.WARNING
                    )

                else:
                    self.license_label.configure(
                        text="🔑 Licença: Demo",
                        fg=Colors.WARNING
                    )
            else:
                self.license_label.configure(
                    text="🔑 Configure a licença",
                    fg=Colors.WARNING
                )
        except Exception:
            self.license_label.configure(
                text="🔑 Status: Indefinido",
                fg=Colors.TEXT_SECONDARY
            )
    # ========================================================
    #  Check vencimento de licença e campanhas pendentes
    # ========================================================
    def _check_license(self):
        """Verifica se a licença é válida"""
        try:
            if not os.path.exists('config.ini'):
                return
            
            linc = cfg.readcfg('config.ini', 'active_license', 'key_license')
            if not linc or linc == 'None':
                return
            
            # Verifica vencimento
            cfg.dtvenclicense = cfg.getVenc_lic(linc)
            if hasattr(cfg, 'dtvenclicense') or cfg.dtvenclicense:
                if not cfg.VerifyVencdate(datetime.now(), cfg.dtvenclicense):
                    vencimento = cfg.dtvenclicense
                    vencimento = vencimento[0:2]+"/"+vencimento[2:4]+"/"+vencimento[4:6]
                    show_warning(self, "Licença Expirada",
                               f"Sua licença expirou em: {vencimento} !\n\n"
                               "Entre em contato: tecmax00@gmail.com\n"
                               "Ou acesse: 1-Configurações → Atualizar Chave")
                else:#senão se o vecimento for válido checa se existe campanha pendente para enviar
                    from campaigns import checkalertcamp as checkcamp
                    #"● Online",
                    self.status_label.configure(text="● Online, ...Aguarde verificando se existe campanha pendente à ser enviada!")
                    if checkcamp('N'):#se campanha pendente não é pelo click de enviar agora na janela de campanha, mas por data e hora menor ou igual a hoje
                        self.status_label.configure(text="● Online, Tudo ok. Última campanha pendente enviada com sucesso!")
                    else:
                        self.status_label.configure(text="● Online")
        except Exception as e:
            print(f"Erro ao verificar licença: {e}")
    
    # ========================================================
    # ❌ FECHAMENTO
    # ========================================================
    def _on_close(self):
        """Handler de fechamento da janela principal"""
        if ask_yes_no(self, "Sair", "Deseja realmente sair do sistema?"):
            self.destroy()
            sys.exit(0)


# ============================================================
# 💬 JANELA: MENSAGEM PARA TODOS
# ============================================================
class MsgAllWindow(ModalWindow):
    """Janela para editar mensagem que será enviada para todos"""
    
    def __init__(self, parent):
        super().__init__(parent, title="💬 Mensagem para Todos",
                        width=600, height=500)
        
        self._build_ui()
    
    def _build_ui(self):
        # Container
        container = tk.Frame(self, bg=Colors.BG_MAIN)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Card
        card = CardFrame(container, title="📝 Digite a mensagem")
        card.pack(fill="both", expand=True)
        
        # Text area
        text_frame = tk.Frame(card, bg=Colors.BG_WHITE)
        text_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        self.text_msg = tk.Text(
            text_frame,
            font=("Segoe UI", 11),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_PRIMARY,
            relief="solid", bd=1,
            wrap="word", padx=10, pady=10
        )
        self.text_msg.pack(fill="both", expand=True)
        
        # Carrega mensagem atual
        try:
            current_msg = cfg.readcfg('config.ini', 'repository', 'msg_all')
            if current_msg and current_msg != 'None':
                self.text_msg.insert("1.0", current_msg)
        except Exception:
            pass
        
        # Botões
        btn_frame = tk.Frame(card, bg=Colors.BG_WHITE)
        btn_frame.pack(fill="x", padx=15, pady=(0, 15))
        
        ttkb.Button(
            btn_frame, text="✕ Cancelar",
            style="secondary.TButton",
            command=self.on_close
        ).pack(side="left", padx=5)
        
        ttkb.Button(
            btn_frame, text="✓ Salvar Mensagem",
            style="primary.TButton",
            command=self._save_message
        ).pack(side="right", padx=5)
    
    def _save_message(self):
        """Salva a mensagem no config"""
        msg = self.text_msg.get("1.0", "end-1c").strip()
        
        if not msg:
            show_warning(self, "Atenção", "Digite uma mensagem antes de salvar!")
            return
        
        try:
            cfg.msg_all = msg
            # Atualiza no config.ini
            cfg.editcfg('config.ini', 'repository', 'msg_all', msg)
            show_info(self, "Sucesso", "Mensagem salva com sucesso!")
            self.on_close()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao salvar mensagem:\n{e}")


# ============================================================
# 📊 JANELA: VISUALIZADOR DE LOG
# ============================================================
class LogViewerWindow(ModalWindow):
    """Visualizador de log do sistema"""
    
    def __init__(self, parent):
        super().__init__(parent, title="📊 Visualizador de Log",
                        width=800, height=600)
        self._build_ui()
        self._load_log()
    
    def _build_ui(self):
        container = tk.Frame(self, bg=Colors.BG_MAIN)
        container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Toolbar
        toolbar = tk.Frame(container, bg=Colors.BG_WHITE, height=50)
        toolbar.pack(fill="x")
        toolbar.pack_propagate(False)
        
        ttkb.Button(
            toolbar, text="🔄 Atualizar",
            style="secondary.TButton",
            command=self._load_log
        ).pack(side="left", padx=5, pady=10)
        
        ttkb.Button(
            toolbar, text="🗑️ Limpar",
            style="secondary.TButton",
            command=self._clear_log
        ).pack(side="left", padx=5, pady=10)
        
        self.line_count = tk.Label(
            toolbar, text="0 linhas",
            font=("Segoe UI", 10),
            bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY
        )
        self.line_count.pack(side="right", padx=15)
        
        # Text area
        text_frame = tk.Frame(container, bg=Colors.BG_WHITE, relief="solid", bd=1)
        text_frame.pack(fill="both", expand=True, pady=(10, 0))
        
        self.text_log = tk.Text(
            text_frame,
            font=("Consolas", 10),
            bg="#1E1E1E",
            fg="#D4D4D4",
            relief="flat",
            wrap="none",
            padx=10, pady=10
        )
        self.text_log.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Scrollbars
        vsb = ttkb.Scrollbar(text_frame, orient="vertical",
                            command=self.text_log.yview)
        hsb = ttkb.Scrollbar(text_frame, orient="horizontal",
                            command=self.text_log.xview)
        self.text_log.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        vsb.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        hsb.place(relx=0.0, rely=1.0, relwidth=1.0, anchor="sw")
    
    def _load_log(self):
        """Carrega o arquivo de log"""
        log_path = os.path.join(localapp, 'ASW.log')
        
        self.text_log.delete("1.0", "end")
        
        if os.path.exists(log_path):
            try:
                with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self.text_log.insert("1.0", content)
                    lines = content.count('\n')
                    self.line_count.configure(text=f"{lines} linhas")
            except Exception as e:
                self.text_log.insert("1.0", f"Erro ao ler log: {e}")
        else:
            self.text_log.insert("1.0", "Arquivo de log não encontrado.")
            self.line_count.configure(text="0 linhas")
    
    def _clear_log(self):
        """Limpa o arquivo de log"""
        if ask_yes_no(self, "Confirmar", "Deseja realmente limpar o log?"):
            try:
                log_path = os.path.join(localapp, 'ASW.log')
                cfg.cleanFile(log_path)
                self._load_log()
                show_info(self, "Sucesso", "Log limpo com sucesso!")
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao limpar log:\n{e}")



# ============================================================
# ℹ️ JANELA: AJUDA E SUPORTE (Refatorada com Scroll e Centralização)
# ============================================================
class HelpWindow(ModalWindow):
    """Janela de ajuda e suporte com barra de rolagem"""
    
    def __init__(self, parent):
        # Alterado para resizable=True e altura maior para evitar cortes iniciais
        super().__init__(parent, title="ℹ️ Ajuda e Suporte",
                        width=550, height=600, resizable=True)
        self._build_ui()
    
    def _build_ui(self):
        # Container principal que ocupará toda a janela
        main_container = tk.Frame(self, bg=Colors.BG_MAIN)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 1. Criar o Canvas e a Scrollbar
        canvas = tk.Canvas(main_container, bg=Colors.BG_MAIN, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        
        # 2. Criar o Frame que conterá os widgets reais (dentro do canvas)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        # 3. Configurar o scrollregion dinamicamente quando o frame mudar de tamanho
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        # 4. Colocar o frame dentro do canvas
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=canvas.winfo_width())
        
        # 5. Vincular a scrollbar ao canvas
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 6. Empacotar canvas e scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 7. Adicionar suporte à roda do mouse (Mousewheel) para melhor UX
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind("<Enter>", lambda _: canvas.bind_all("<MouseWheel>", _on_mousewheel))
        canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))
        
        # Ajustar a largura do frame interno quando o canvas for redimensionado
        canvas.bind("<Configure>", lambda e: canvas.itemconfig("all", width=e.width))

        # ========================================================
        # CONTEÚDO REAL DA JANELA (Agora dentro do scrollable_frame)
        # ========================================================
        
        # Card principal
        card = CardFrame(scrollable_frame, title="💬 ASW Messenger")
        card.pack(fill="x", pady=(0, 15))
        
        info_frame = tk.Frame(card, bg=Colors.BG_WHITE)
        info_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(
            info_frame, text="Sistema de Automação de Envio WhatsApp",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY
        ).pack(anchor="w")
        
        tk.Label(
            info_frame, text="Versão 2.0 - Build 2026.07",
            font=("Segoe UI", 9),
            bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY
        ).pack(anchor="w", pady=(5, 0))
        
        # Opções de suporte
        tk.Label(
            scrollable_frame, text="🛠️ SUPORTE TÉCNICO",
            font=("Segoe UI", 10, "bold"),
            bg=Colors.BG_MAIN, fg=Colors.TEXT_PRIMARY, anchor="w"
        ).pack(fill="x", pady=(10, 10))
        
        support_options = [
            ("🌐", "Site Oficial", "Acessar site Tecmaxima", self._open_website),
            ("📧", "Email Suporte", "tecmax00@gmail.com", None),
            ("💻", "Suporte Remoto (Ammyy)somente windows", "Iniciar Ammyy Admin / informe o id do dispositivo ao suporte!", self._open_ammyy),
            ("🖥️", "Suporte Remoto (AnyDesk)", "Iniciar AnyDesk / informe o id do dispositivo ao suporte!", self._open_anydesk),
        ]
        
        for icon, title, desc, cmd in support_options:
            btn_card = tk.Frame(scrollable_frame, bg=Colors.BG_WHITE,
                              relief="solid", bd=1, cursor="hand2")
            btn_card.pack(fill="x", pady=5)
            
            inner = tk.Frame(btn_card, bg=Colors.BG_WHITE, padx=15, pady=12)
            inner.pack(fill="x")
            
            tk.Label(inner, text=icon, font=("Segoe UI Emoji", 18),
                    bg=Colors.BG_WHITE, width=2).pack(side="left")
            
            text_frame = tk.Frame(inner, bg=Colors.BG_WHITE)
            text_frame.pack(side="left", fill="x", expand=True, padx=10)
            
            tk.Label(text_frame, text=title, font=("Segoe UI", 10, "bold"),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                    anchor="w").pack(fill="x")
            tk.Label(text_frame, text=desc, font=("Segoe UI", 9),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY,
                    anchor="w").pack(fill="x")
            
            if cmd:
                # Aplica os eventos de hover em todos os widgets do card
                widgets_to_bind = [btn_card, inner, text_frame] + text_frame.winfo_children()
                for w in widgets_to_bind:
                    w.bind("<Button-1>", lambda e, c=cmd: c())
                    w.bind("<Enter>", lambda e, c=btn_card: c.configure(bg=Colors.PRIMARY_LIGHT))
                    w.bind("<Leave>", lambda e, c=btn_card: c.configure(bg=Colors.BG_WHITE))
                    
        # Espaço extra no final para garantir que o último item não fique colado na borda
        tk.Frame(scrollable_frame, bg=Colors.BG_MAIN, height=20).pack(fill="x")

    def _open_website(self):
        import webbrowser
        webbrowser.open("https://tmx.infinityfreeapp.com")
    
    def _open_ammyy(self):
        # Usando os.getcwd() para garantir que funcione mesmo se 'localapp' não estiver no escopo global
        exe_path = os.path.join(os.getcwd(), "AA_v3.exe")
        if os.path.exists(exe_path):
            os.startfile(exe_path)
            
        else:
            show_warning(self, "Não encontrado",
                        "Ammyy Admin (AA_v3.exe) não encontrado na pasta do sistema.")
    
    def _open_anydesk(self):
        exe_path = os.path.join(os.getcwd(), "AnyDesk.exe")
        if os.path.exists(exe_path):
            os.startfile(exe_path)
        else:
            import subprocess
            import platform
            try:
                if platform.system() == "Windows":
                    subprocess.Popen(["anydesk"])
                else:
                    subprocess.Popen(["/usr/bin/anydesk"])
            except Exception:
                show_warning(self, "Não encontrado",
                            "AnyDesk não encontrado no sistema.")

# 🚀 PONTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    try:
        app = ASWApplication()
        app.mainloop()
    except Exception as e:
        print(f"Erro crítico: {e}")
        import traceback
        traceback.print_exc()