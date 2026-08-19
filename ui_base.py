# -*- coding: utf-8 -*-
"""
ui_base.py - Base compartilhada para toda a interface ASW
Contém: paleta de cores azul, classe ModalWindow, componentes reutilizáveis
"""
import os
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

# ============================================================
# 🎨 PALETA DE CORES - AZUL WHATSAPP-STYLE (Opção B)
# ============================================================
class Colors:
    # Azuis principais
    PRIMARY         = "#0088CC"      # Azul WhatsApp
    PRIMARY_DARK    = "#005C99"      # Azul mais escuro
    PRIMARY_DARKER  = "#003D66"      # Azul sidebar
    PRIMARY_HOVER   = "#004A7A"      # Hover sidebar
    PRIMARY_LIGHT   = "#E3F2FD"      # Fundo claro azul
    
    # Neutros (estilo WhatsApp Web)
    BG_MAIN         = "#F0F2F5"      # Fundo principal
    BG_WHITE        = "#FFFFFF"      # Fundo branco
    BG_SIDEBAR      = "#FFFFFF"      # Sidebar
    BG_CHAT         = "#EFEAE2"      # Fundo chat (bege WhatsApp)
    
    # Textos
    TEXT_PRIMARY    = "#111B21"      # Texto principal
    TEXT_SECONDARY  = "#667781"      # Texto secundário
    TEXT_LIGHT      = "#FFFFFF"      # Texto em fundo escuro
    TEXT_MUTED      = "#8696A0"      # Texto desativado
    
    # Bordas e divisores
    BORDER          = "#E9EDEF"      # Borda padrão
    BORDER_DARK     = "#D1D7DB"      # Borda escura
    DIVIDER         = "#F0F2F5"      # Divisor
    
    # Estados
    SUCCESS         = "#00A884"      # Verde WhatsApp (sucesso)
    DANGER          = "#E74C3C"      # Vermelho (erro/excluir)
    WARNING         = "#F39C12"      # Amarelo (alerta)
    INFO            = "#3498DB"      # Azul info
    
    # Botões
    BTN_SEND        = "#0088CC"      # Botão enviar
    BTN_CANCEL      = "#E74C3C"      # Botão cancelar
    BTN_SECONDARY   = "#F0F2F5"      # Botão secundário
    
    # Hover
    HOVER_LIGHT     = "#F5F6F6"      # Hover claro
    HOVER_SIDEBAR   = "#F0F2F5"      # Hover sidebar


# ============================================================
# 🔤 ICONES UNICODE (SVG embutido via emojis)
# ============================================================
class Icons:
    CONFIG      = "⚙️"
    CAMPAIGN    = "📋"
    CONTACT     = "👥"
    SEND        = "📤"
    FILE        = "📁"
    MESSAGE     = "💬"
    IMAGE       = "🖼️"
    DOCUMENT    = "📄"
    REPORT      = "📊"
    HELP        = "ℹ️"
    CLOSE       = "✕"
    BACK        = "←"
    ADD         = "➕"
    EDIT        = "✏️"
    DELETE      = "🗑️"
    FILTER      = "🔍"
    IMPORT      = "📥"
    CHECK       = "✓"
    WARNING     = "⚠️"
    CLOCK       = "🕐"
    CALENDAR    = "📅"
    GROUP       = "👨‍👩‍👧‍👦"
    PHONE       = "📱"
    EMAIL       = "📧"
    USER        = "👤"
    KEY         = "🔑"
    BROWSER     = "🌐"
    PLAY        = "▶️"
    PAUSE       = "⏸️"
    REFRESH     = "🔄"
    LOG         = "📝"
    WHATSAPP    = "💚"  # Coração verde representa WhatsApp


# ============================================================
# 🪟 CLASSE BASE: JANELA MODAL (Pai → Filha)
# ============================================================
class ModalWindow(ttkb.Toplevel):
    """
    Janela modal que:
    - Bloqueia a janela pai (grab_set)
    - Centraliza na tela
    - Tem botão fechar estilo WhatsApp
    - Aplica tema azul consistente
    """
    #*****************************************
    def __init__(self, parent, title="ASW", width=800, height=600, 
             show_close_btn=True, resizable=True):
        super().__init__(parent)
        
        self.parent_window = parent
        self.title(title)
        self.configure(bg=Colors.BG_MAIN)
        
        # Tamanho e centralização
        self.geometry(f"{width}x{height}")
        self.minsize(400, 300)
        
        if not resizable:
            self.resizable(False, False)
        
        # Torna modal (bloqueia pai) - CORREÇÃO AQUI
        self.transient(parent)
        self.update_idletasks()  # Força renderização imediata
        self.after(50, self._apply_modal_grab)  # Aplica grab após 50ms
        
        # Ícone (se existir)
        try:
            icon_path = os.path.join(os.getcwd(), "icons", "ASW.ico")
            if os.path.exists(icon_path):
                self.iconbitmap(icon_path)
        except Exception:
            pass
        
        # Aplica estilo
        self._apply_styles()
        
        # Header customizado com botão fechar
        if show_close_btn:
            self._create_header(title)
        
        # Centraliza na tela
        self._center_on_screen(width, height)
        
        # Protocolo de fechamento
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    #*****************************************
    def _apply_modal_grab(self):
        """Aplica o grab modal após a janela estar totalmente visível"""
    try:
        if self.winfo_exists() and self.winfo_viewable():
            self.grab_set()
    except Exception as e:
        print(f"Aviso: Não foi possível aplicar grab modal: {e}")
    #******************************************
    def _apply_styles(self):
        """Aplica estilos ttk personalizados"""
        style = ttkb.Style()
        
        # Frame principal
        style.configure("Main.TFrame", background=Colors.BG_MAIN)
        style.configure("Card.TFrame", background=Colors.BG_WHITE)
        style.configure("Sidebar.TFrame", background=Colors.BG_SIDEBAR)
        
        # Labels
        style.configure("Title.TLabel", 
                       background=Colors.BG_WHITE,
                       foreground=Colors.TEXT_PRIMARY,
                       font=("Segoe UI", 14, "bold"))
        style.configure("Header.TLabel",
                       background=Colors.BG_WHITE,
                       foreground=Colors.TEXT_PRIMARY,
                       font=("Segoe UI", 12, "bold"))
        style.configure("Body.TLabel",
                       background=Colors.BG_WHITE,
                       foreground=Colors.TEXT_PRIMARY,
                       font=("Segoe UI", 10))
        style.configure("Muted.TLabel",
                       background=Colors.BG_WHITE,
                       foreground=Colors.TEXT_SECONDARY,
                       font=("Segoe UI", 9))
        
        # Botões
        style.configure("Primary.TButton",
                       font=("Segoe UI", 10, "bold"))
        style.configure("Secondary.TButton",
                       font=("Segoe UI", 10))
    
    def _create_header(self, title):
        """Cria header com título e botão fechar estilo WhatsApp"""
        header = ttkb.Frame(self, style="Card.TFrame", height=60)
        header.pack(fill="x", side="top")
        header.pack_propagate(False)
        
        # Título
        title_lbl = ttkb.Label(header, text=title, style="Header.TLabel")
        title_lbl.pack(side="left", padx=20, pady=15)
        
        # Botão fechar estilo WhatsApp (círculo com X)
        close_btn = tk.Button(
            header,
            text="✕",
            font=("Segoe UI", 11, "bold"),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_SECONDARY,
            activebackground=Colors.DANGER,
            activeforeground=Colors.TEXT_LIGHT,
            relief="flat",
            bd=0,
            width=2,
            height=1,
            cursor="hand2",
            command=self.on_close
        )
        close_btn.pack(side="right", padx=15, pady=10)
        
        # Efeito hover
        def on_enter(e):
            close_btn.configure(bg=Colors.DANGER, fg=Colors.TEXT_LIGHT)
        def on_leave(e):
            close_btn.configure(bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY)
        
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)
        
        # Linha divisória
        divider = tk.Frame(header, height=1, bg=Colors.BORDER)
        divider.pack(fill="x", side="bottom")
    
    def _center_on_screen(self, width, height):
        """Centraliza a janela na tela"""
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def on_close(self):
        """Handler de fechamento (pode ser sobrescrito)"""
        self.grab_release()
        self.destroy()
    
    def show_message(self, title, message, icon="info"):
        """Exibe mensagem usando messagebox estilizado"""
        from tkinter import messagebox as mb
        if icon == "info":
            mb.showinfo(title, message, parent=self)
        elif icon == "warning":
            mb.showwarning(title, message, parent=self)
        elif icon == "error":
            mb.showerror(title, message, parent=self)
        elif icon == "question":
            return mb.askquestion(title, message, parent=self)
    
    def ask_confirmation(self, title, message):
        """Pede confirmação ao usuário"""
        from tkinter import messagebox as mb
        return mb.askyesno(title, message, parent=self)


# ============================================================
# 🎨 COMPONENTES REUTILIZÁVEIS
# ============================================================
class SidebarButton(ttkb.Frame):
    """Botão da sidebar estilo WhatsApp Web"""
    
    def __init__(self, parent, icon, text, command=None, active=False):
        super().__init__(parent, style="Sidebar.TFrame")
        
        self.command = command
        self.is_active = active
        
        # Container clicável
        self.container = tk.Frame(
            self,
            bg=Colors.PRIMARY_LIGHT if active else Colors.BG_SIDEBAR,
            cursor="hand2"
        )
        self.container.pack(fill="x", padx=8, pady=2)
        
        # Ícone
        self.icon_lbl = tk.Label(
            self.container,
            text=icon,
            font=("Segoe UI Emoji", 16),
            bg=self.container["bg"],
            fg=Colors.PRIMARY if active else Colors.TEXT_SECONDARY,
            width=2
        )
        self.icon_lbl.pack(side="left", padx=(10, 5), pady=10)
        
        # Texto
        self.text_lbl = tk.Label(
            self.container,
            text=text,
            font=("Segoe UI", 11),
            bg=self.container["bg"],
            fg=Colors.PRIMARY if active else Colors.TEXT_PRIMARY,
            anchor="w"
        )
        self.text_lbl.pack(side="left", fill="x", expand=True, pady=10)
        
        # Bindings
        for widget in (self.container, self.icon_lbl, self.text_lbl):
            widget.bind("<Button-1>", lambda e: self._on_click())
            widget.bind("<Enter>", lambda e: self._on_enter())
            widget.bind("<Leave>", lambda e: self._on_leave())
    
    def _on_click(self):
        if self.command:
            self.command()
    
    def _on_enter(self):
        if not self.is_active:
            self.container.configure(bg=Colors.HOVER_SIDEBAR)
            self.icon_lbl.configure(bg=Colors.HOVER_SIDEBAR)
            self.text_lbl.configure(bg=Colors.HOVER_SIDEBAR)
    
    def _on_leave(self):
        if not self.is_active:
            self.container.configure(bg=Colors.BG_SIDEBAR)
            self.icon_lbl.configure(bg=Colors.BG_SIDEBAR)
            self.text_lbl.configure(bg=Colors.BG_SIDEBAR)
    
    def set_active(self, active):
        self.is_active = active
        bg = Colors.PRIMARY_LIGHT if active else Colors.BG_SIDEBAR
        fg_icon = Colors.PRIMARY if active else Colors.TEXT_SECONDARY
        fg_text = Colors.PRIMARY if active else Colors.TEXT_PRIMARY
        
        self.container.configure(bg=bg)
        self.icon_lbl.configure(bg=bg, fg=fg_icon)
        self.text_lbl.configure(bg=bg, fg=fg_text)


class CardFrame(tk.Frame):
    """Card com borda sutil estilo Material - usa tk.Frame para suportar relief/bd"""
    
    def __init__(self, parent, title=None, **kwargs):
        # tk.Frame aceita relief e bd nativamente
        super().__init__(parent, bg=Colors.BG_WHITE,
                        relief="solid", bd=1, **kwargs)
        
        if title:
            header = tk.Frame(self, bg=Colors.BG_WHITE, height=40)
            header.pack(fill="x")
            header.pack_propagate(False)
            
            tk.Label(
                header, text=title,
                font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY
            ).pack(side="left", padx=15, pady=8)
            
            # Linha divisória
            tk.Frame(self, height=1, bg=Colors.BORDER).pack(fill="x")


class FormField(ttkb.Frame):
    """Campo de formulário com label"""
    
    def __init__(self, parent, label_text, field_type="entry", **kwargs):
        super().__init__(parent, style="Card.TFrame")
        
        # Label
        lbl = tk.Label(
            self, text=label_text,
            font=("Segoe UI", 10),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_PRIMARY,
            anchor="w"
        )
        lbl.pack(fill="x", padx=10, pady=(10, 2))
        
        # Campo
        if field_type == "entry":
            self.field = ttkb.Entry(self, **kwargs)
        elif field_type == "text":
            self.field = tk.Text(self, height=5, font=("Segoe UI", 10),
                                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                                relief="solid", bd=1)
        elif field_type == "combobox":
            self.field = ttkb.Combobox(self, **kwargs)
        elif field_type == "password":
            self.field = ttkb.Entry(self, show="*", **kwargs)
        
        self.field.pack(fill="x", padx=10, pady=(0, 10))
    
    def get(self):
        if isinstance(self.field, tk.Text):
            return self.field.get("1.0", "end-1c")
        return self.field.get()
    
    def set(self, value):
        if isinstance(self.field, tk.Text):
            self.field.delete("1.0", "end")
            self.field.insert("1.0", value)
        elif isinstance(self.field, ttkb.Combobox):
            self.field.set(value)
        else:
            self.field.delete(0, "end")
            self.field.insert(0, value)


# ============================================================
# 🛠️ FUNÇÕES UTILITÁRIAS
# ============================================================
def show_info(parent, title, message):
    from tkinter import messagebox as mb
    mb.showinfo(title, message, parent=parent)

def show_warning(parent, title, message):
    from tkinter import messagebox as mb
    mb.showwarning(title, message, parent=parent)

def show_error(parent, title, message):
    from tkinter import messagebox as mb
    mb.showerror(title, message, parent=parent)

def ask_yes_no(parent, title, message):
    from tkinter import messagebox as mb
    return mb.askyesno(title, message, parent=parent)

# ============================================================
# 🛡️ CONVERSÃO SEGURA DE VALORES
# ============================================================
def safe_int(value, default=0):
    """Converte valor para int de forma segura"""
    try:
        if value is None or value == '' or value == 'None':
            return default
        # Remove espaços e caracteres não numéricos (exceto sinal)
        clean_value = str(value).strip()
        return int(clean_value)
    except (ValueError, TypeError):
        # Tenta extrair apenas números da string
        try:
            import re
            numbers = re.findall(r'-?\d+', str(value))
            if numbers:
                return int(numbers[0])
        except Exception:
            pass
        return default


def safe_float(value, default=0.0):
    """Converte valor para float de forma segura"""
    try:
        if value is None or value == '' or value == 'None':
            return default
        clean_value = str(value).strip()
        return float(clean_value)
    except (ValueError, TypeError):
        try:
            import re
            numbers = re.findall(r'-?\d+\.?\d*', str(value))
            if numbers:
                return float(numbers[0])
        except Exception:
            pass
        return default