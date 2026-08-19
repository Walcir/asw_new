# -*- coding: utf-8 -*-
"""
contacts.py - Gerenciamento de contatos (GUI modal refatorada)
"""
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox as msgbx
import ttkbootstrap as ttkb
from ttkbootstrap.constants import *

import databases as db
import config as cfg
import tools as tls
from ui_base import (ModalWindow, Colors, Icons, CardFrame,
                     show_info, show_warning, ask_yes_no)

# ============================================================
# 🌍 VARIÁVEIS GLOBAIS
# ============================================================
FrmShowcontact_w = None


# ============================================================
# 🗑️ EXCLUIR CONTATO
# ============================================================
def del_Contact(idcontact):
    try:
        if ask_yes_no(None, "Confirmar", "Tem certeza que deseja excluir este contato?"):
            db.deletetablesql(db.csqllite, 'contatos', '',
                            f' where idcontatos={idcontact}')
            db.csqllite.connection.commit()
            show_info(None, "Sucesso", "Contato excluído com sucesso!")
    except Exception as e:
        show_warning(None, "Erro", f"Erro ao excluir contato:\n{e}")


# ============================================================
# 📋 JANELA PRINCIPAL DE CONTATOS
# ============================================================
def menu_Showcontact(parent):
    """Abre a janela de visualização de contatos"""
    ContactsWindow(parent)


class ContactsWindow(ModalWindow):
    """Janela principal de contatos"""
    
    def __init__(self, parent):
        super().__init__(parent, title="👥 Gerenciar Contatos",
                        width=1100, height=730)
        
        self.selected_contact_id = None
        self._build_ui()
        self._load_contacts()
    
    def _build_ui(self):
        """Constrói a interface"""
        # Container principal
        main = tk.Frame(self, bg=Colors.BG_MAIN)
        main.pack(fill="both", expand=True, padx=15, pady=15)        

        # ===== Toolbar superior =====
        toolbar = tk.Frame(main, bg=Colors.BG_WHITE, relief="solid", bd=1)
        toolbar.pack(fill="x", pady=(0, 10))
        
        tk.Label(toolbar, text=f"{Icons.FILTER} Filtros",
                font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left", padx=15, pady=10)
        
        ttkb.Button(
            toolbar, text="🔍 Aplicar Filtros",
            style="primary.TButton",
            command=self._apply_filters
        ).pack(side="right", padx=10, pady=8)
        
        # ===== Área de filtros =====
        filter_card = CardFrame(main)
        filter_card.pack(fill="x", pady=(0, 10))
        
        filter_inner = tk.Frame(filter_card, bg=Colors.BG_WHITE)
        filter_inner.pack(fill="x", padx=5, pady=5)
        
        # Grid de filtros
        filters = [
            ("Nome inicial:", "text_nameini"),
            ("Nome final:", "text_namefin"),
            ("Fone inicial:", "text_foneini"),
            ("Fone final:", "text_fonefin"),
            ("Categoria inicial:", "text_groupini"),
            ("Categoria final:", "text_groupfin"),
        ]
        
        self.filter_entries = {}
        
        for i, (label, key) in enumerate(filters):
            row, col = divmod(i, 3)
            cell = tk.Frame(filter_inner, bg=Colors.BG_WHITE)
            cell.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
            filter_inner.grid_columnconfigure(col, weight=1)
            
            tk.Label(cell, text=label, font=("Segoe UI", 9),
                    bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY,
                    anchor="w").pack(fill="x")
            
            entry = ttkb.Entry(cell)
            entry.pack(fill="x", pady=(2, 0))
            self.filter_entries[key] = entry
        
        # ===== Split: Lista + Detalhes =====
        split = tk.Frame(main, bg=Colors.BG_MAIN)
        split.pack(fill="both", expand=True)
        
        # Lista de contatos (esquerda)
        list_frame = tk.Frame(split, bg=Colors.BG_WHITE , relief="solid", bd=1)
        list_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Header da lista
        list_header = tk.Frame(list_frame, bg=Colors.BG_WHITE, height=40)
        list_header.pack(fill="x")
        list_header.pack_propagate(False)
        
        tk.Label(list_header, text=f"{Icons.CONTACT} Contatos",
                font=("Segoe UI", 11, "bold"),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY).pack(side="left", padx=15, pady=10)
        
        self.lbl_count = tk.Label(list_header, text="0 contatos",
                                 font=("Segoe UI", 10),
                                 bg=Colors.BG_WHITE, fg=Colors.TEXT_SECONDARY)
        self.lbl_count.pack(side="right", padx=15)

        
        self.lbl_details = tk.Label(
            list_header,
            text="Selecione um contato\nna lista ao lado",
            font=("Segoe UI", 8),
            bg=Colors.BG_WHITE,
            fg=Colors.TEXT_SECONDARY,
            justify="center"
        )
        self.lbl_details.pack(fill="x",padx=5, pady=1)
        
        # Treeview
        tree_frame = tk.Frame(list_frame, bg=Colors.BG_WHITE)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        columns = ("id", "nome", "fone", "categoria", "email", "ativo")
        self.tree = ttkb.Treeview(tree_frame, columns=columns, show="headings",
                                 selectmode="browse")
        
        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Nome")
        self.tree.heading("fone", text="Telefone")
        self.tree.heading("categoria", text="Categoria")
        self.tree.heading("email", text="Email")
        self.tree.heading("ativo", text="Ativo")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("nome", width=180)
        self.tree.column("fone", width=130)
        self.tree.column("categoria", width=120)
        self.tree.column("email", width=180)
        self.tree.column("ativo", width=60, anchor="center")
        
        scrollbar_y = ttkb.Scrollbar(tree_frame, orient="vertical",
                                    command=self.tree.yview)
        scrollbar_x = ttkb.Scrollbar(tree_frame, orient="horizontal",
                                    command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set,
                           xscrollcommand=scrollbar_x.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self._on_select_contact)
        
        # Painel direito (detalhes + botões)
        right_panel = tk.Frame(split, bg=Colors.BG_MAIN, width=280)
        right_panel.pack(side="right", fill="y", padx=(5, 0))
        right_panel.pack_propagate(False)

        # Scroll ==========================================================
        canvas = tk.Canvas(split, bg=Colors.BG_MAIN, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(right_panel, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y")
        #===================================================================

        
        # Card de detalhes
        details_card = CardFrame(right_panel, title=f"{Icons.USER} Detalhes")
        details_card.pack(fill="x", pady=(0, 5))

        
        self.details_frame = tk.Frame(details_card, bg=Colors.BG_WHITE)
        self.details_frame.pack(fill="x", padx=10, pady=1)       
        
        # Card de campanhas do contato
        camp_card = CardFrame(right_panel, title=f"{Icons.CAMPAIGN} Campanhas")
        camp_card.pack(fill="both", expand=True,padx=5,pady=5)
        
        camp_frame = tk.Frame(camp_card, bg=Colors.BG_WHITE)
        camp_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.tree_camp = ttkb.Treeview(
            camp_frame,
            columns=("id", "nome", "ativo", "enviada"),
            show="headings", height=5
        )
        
        self.tree_camp.heading("id", text="ID")
        self.tree_camp.heading("nome", text="Nome")
        self.tree_camp.heading("ativo", text="Ativo")
        self.tree_camp.heading("enviada", text="Enviada")
        
        self.tree_camp.column("id", width=30, anchor="center")
        self.tree_camp.column("nome", width=110)
        self.tree_camp.column("ativo", width=50, anchor="center")
        self.tree_camp.column("enviada", width=60, anchor="center")
        
        self.tree_camp.pack(fill="both", expand=True)

        # Botões de ação
        #btn_card = CardFrame(right_panel)
        btn_card = CardFrame(self.details_frame)
        btn_card.pack(fill="x")
        
        btn_frame = tk.Frame(btn_card, bg=Colors.BG_WHITE)
        btn_frame.pack(fill="x", padx=5,pady=1)
        
        buttons = [
            (f"{Icons.ADD} Novo Contato", "success.TButton", self._add_contact),
            (f"{Icons.EDIT} Editar", "info.TButton", self._edit_contact),
            (f"{Icons.DELETE} Excluir", "danger.TButton", self._delete_contact),
            (f"{Icons.IMPORT} Importar CSV", "warning.TButton", self._import_csv),
            (f"{Icons.IMPORT} Importar VCF", "warning.TButton", self._import_vcf),
        ]
        
        for text, style, cmd in buttons:
            ttkb.Button(
                btn_frame, text=text, style=style,
                command=cmd
            ).pack(fill="x", pady=1)    
        
       
    
    def _load_contacts(self):
        """Carrega todos os contatos"""
        self.tree.delete(*self.tree.get_children())
        
        try:
            contacts = db.consulttablesql(
                db.csqllite,
                'idcontatos,nomecontato,fonecontato,nomegrupocontato,emailcontato,ativocontato',
                'contatos',
                ' where idcontatos is not null ',
                ' order by nomecontato '
            )
            
            if contacts:
                for c in contacts:
                    self.tree.insert("", "end", values=(
                        c[0], c[1], c[2], c[3], c[4], c[5]
                    ))
                self.lbl_count.configure(text=f"{len(contacts)} contatos")
            else:
                self.lbl_count.configure(text="0 contatos")
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao carregar contatos:\n{e}")
    
    def _apply_filters(self):
        """Aplica os filtros e recarrega"""
        where = ' where idcontatos is not null '
        
        name_ini = self.filter_entries['text_nameini'].get().strip()
        name_fin = self.filter_entries['text_namefin'].get().strip()
        fone_ini = self.filter_entries['text_foneini'].get().strip()
        fone_fin = self.filter_entries['text_fonefin'].get().strip()
        group_ini = self.filter_entries['text_groupini'].get().strip()
        group_fin = self.filter_entries['text_groupfin'].get().strip()
        
        if name_ini:
            where += f" and nomecontato >= '{name_ini}'"
        if name_fin:
            where += f" and nomecontato <= '{name_fin}'"
        if fone_ini:
            where += f" and fonecontato >= '{fone_ini}'"
        if fone_fin:
            where += f" and fonecontato <= '{fone_fin}'"
        if group_ini:
            where += f" and nomegrupocontato >= '{group_ini}'"
        if group_fin:
            where += f" and nomegrupocontato <= '{group_fin}'"
        
        self.tree.delete(*self.tree.get_children())
        
        try:
            contacts = db.consulttablesql(
                db.csqllite,
                'idcontatos,nomecontato,fonecontato,nomegrupocontato,emailcontato,ativocontato',
                'contatos', where, ' order by nomecontato '
            )
            
            if contacts:
                for c in contacts:
                    self.tree.insert("", "end", values=(
                        c[0], c[1], c[2], c[3], c[4], c[5]
                    ))
                self.lbl_count.configure(text=f"{len(contacts)} contatos")
            else:
                self.lbl_count.configure(text="0 contatos")
                show_info(self, "Busca", "Nenhum contato encontrado com os filtros aplicados.")
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao aplicar filtros:\n{e}")
    
    def _on_select_contact(self, event):
        """Handler de seleção de contato"""
        selection = self.tree.selection()
        if not selection:
            return
        
        values = self.tree.item(selection[0], "values")
        self.selected_contact_id = values[0]
        cfg.clickId = self.selected_contact_id
        
        # Atualiza detalhes
        details = (
            f"👤 {values[1]}\n\n"
            f"📱 {values[2]}\n"
            f"📧 {values[4]}\n"
            f"📋 {values[3]}\n"
            f"{'✅' if values[5] == 'S' else '❌'} {'Ativo' if values[5] == 'S' else 'Inativo'}"
        )
        self.lbl_details.configure(text=details, justify="left", anchor="w")
        
        # Carrega campanhas do contato
        self._load_contact_campaigns(values[0])
    
    def _load_contact_campaigns(self, contact_id):
        """Carrega campanhas do contato selecionado"""
        self.tree_camp.delete(*self.tree_camp.get_children())
        
        try:
            campaigns = db.consulttablesql(
                db.csqllite,
                'idcampanhas,nomecampanhas,ativocampanhas,enviada',
                'campanhas left join itenscamp on(idcoditcamp = idcampanhas)',
                f' where iditcontcamp = "{contact_id}" ',
                ' ;'
            )
            
            if campaigns:
                for c in campaigns:
                    self.tree_camp.insert("", "end", values=c)
        except Exception as e:
            print(f"Erro ao carregar campanhas: {e}")
    
    def _add_contact(self):
        """Abre janela para adicionar contato"""
        ContactFormWindow(self, mode="add")
    
    def _edit_contact(self):
        """Abre janela para editar contato"""
        if not self.selected_contact_id:
            show_warning(self, "Atenção", "Selecione um contato para editar!")
            return
        ContactFormWindow(self, mode="edit", contact_id=self.selected_contact_id)
    
    def _delete_contact(self):
        """Exclui contato selecionado"""
        if not self.selected_contact_id:
            show_warning(self, "Atenção", "Selecione um contato para excluir!")
            return
        
        if ask_yes_no(self, "Confirmar", "Deseja realmente excluir este contato?"):
            try:
                db.deletetablesql(db.csqllite, 'contatos', '',
                                f' where idcontatos={self.selected_contact_id}')
                db.csqllite.connection.commit()
                show_info(self, "Sucesso", "Contato excluído com sucesso!")
                self._load_contacts()
            except Exception as e:
                show_warning(self, "Erro", f"Erro ao excluir:\n{e}")
    
    def _import_csv(self):
        """Importa contatos de CSV"""
        from tkinter.filedialog import askopenfilename
        
        filecsv = askopenfilename(
            parent=self,
            filetypes=[("CSV files", "*.csv")],
            title="Selecione o arquivo CSV"
        )
        
        if not filecsv:
            return
        
        try:
            qtd = db.importcontacts_csv(filecsv, 0)
            if qtd > 0:
                show_info(self, "Sucesso",
                         f"{qtd-1} contato(s) importado(s) com sucesso!")
                self._load_contacts()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao importar CSV:\n{e}")
    
    def _import_vcf(self):
        """Importa contatos de VCF"""
        from tkinter.filedialog import askopenfilename
        
        filevcf = askopenfilename(
            parent=self,
            filetypes=[("VCF files", "*.vcf")],
            title="Selecione o arquivo VCF"
        )
        
        if not filevcf:
            return
        
        try:
            qtd = db.importcontacts_vcf(filevcf, 0)
            if qtd and qtd > 0:
                show_info(self, "Sucesso",
                         f"{qtd} contato(s) importado(s) com sucesso!")
                self._load_contacts()
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao importar VCF:\n{e}")


# ============================================================
# 📝 FORMULÁRIO DE CONTATO (ADD/EDIT)
# ============================================================
class ContactFormWindow(ModalWindow):
    """Formulário para adicionar/editar contato"""
    
    def __init__(self, parent, mode="add", contact_id=None):
        title = f"{Icons.ADD} Novo Contato" if mode == "add" else f"{Icons.EDIT} Editar Contato"
        super().__init__(parent, title=title, width=550, height=550)
        
        self.mode = mode
        self.contact_id = contact_id
        self.contact_data = {}
        
        self._build_ui()
        
        if mode == "edit" and contact_id:
            self._load_contact_data()
    
    def _build_ui(self):
        """Constrói o formulário"""
        # Scroll
        canvas = tk.Canvas(self, bg=Colors.BG_MAIN, highlightthickness=0)
        scrollbar = ttkb.Scrollbar(self, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg=Colors.BG_MAIN)
        
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True, padx=15, pady=15)
        scrollbar.pack(side="right", fill="y")
        
        # Card: Dados básicos
        card1 = CardFrame(scroll_frame, title=f"{Icons.USER} Dados Básicos")
        card1.pack(fill="x", pady=(0, 10))
        
        inner1 = tk.Frame(card1, bg=Colors.BG_WHITE)
        inner1.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner1, text="Nome *", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                anchor="w").pack(fill="x")
        self.entry_name = ttkb.Entry(inner1)
        self.entry_name.pack(fill="x", pady=(5, 15))
        
        tk.Label(inner1, text="Telefone * (Ex: 5583988009900)",
                font=("Segoe UI", 10), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        self.entry_phone = ttkb.Entry(inner1)
        self.entry_phone.pack(fill="x", pady=(5, 15))
        
        tk.Label(inner1, text="Email", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                anchor="w").pack(fill="x")
        self.entry_email = ttkb.Entry(inner1)
        self.entry_email.pack(fill="x", pady=(5, 15))
        
        tk.Label(inner1, text="Categoria/Grupo", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                anchor="w").pack(fill="x")
        self.entry_group = ttkb.Entry(inner1)
        self.entry_group.pack(fill="x", pady=(5, 0))
        
        # Card: Status
        card2 = CardFrame(scroll_frame, title=f"{Icons.CHECK} Status")
        card2.pack(fill="x", pady=(0, 10))
        
        inner2 = tk.Frame(card2, bg=Colors.BG_WHITE)
        inner2.pack(fill="x", padx=15, pady=15)
        
        tk.Label(inner2, text="Status do contato:",
                font=("Segoe UI", 10), bg=Colors.BG_WHITE,
                fg=Colors.TEXT_PRIMARY, anchor="w").pack(fill="x")
        
        self.var_active = tk.StringVar(value="S")
        active_frame = tk.Frame(inner2, bg=Colors.BG_WHITE)
        active_frame.pack(fill="x", pady=(5, 15))
        
        ttkb.Radiobutton(active_frame, text="✅ Ativo",
                        variable=self.var_active, value="S",
                        bootstyle="success").pack(side="left", padx=5)
        ttkb.Radiobutton(active_frame, text="❌ Inativo",
                        variable=self.var_active, value="N",
                        bootstyle="danger").pack(side="left", padx=5)
        
        tk.Label(inner2, text="É cliente?", font=("Segoe UI", 10),
                bg=Colors.BG_WHITE, fg=Colors.TEXT_PRIMARY,
                anchor="w").pack(fill="x")
        
        self.var_client = tk.StringVar(value="N")
        client_frame = tk.Frame(inner2, bg=Colors.BG_WHITE)
        client_frame.pack(fill="x", pady=(5, 0))
        
        ttkb.Radiobutton(client_frame, text="✅ Sim",
                        variable=self.var_client, value="S",
                        bootstyle="success").pack(side="left", padx=5)
        ttkb.Radiobutton(client_frame, text="❌ Não",
                        variable=self.var_client, value="N",
                        bootstyle="danger").pack(side="left", padx=5)
        
        # Botões
        btn_frame = tk.Frame(scroll_frame, bg=Colors.BG_MAIN)
        btn_frame.pack(fill="x", pady=(10, 0))
        
        ttkb.Button(
            btn_frame, text="✕ Cancelar",
            style="secondary.TButton",
            command=self.on_close
        ).pack(side="left", padx=5)
        
        save_text = "💾 Salvar" if self.mode == "add" else "💾 Atualizar"
        ttkb.Button(
            btn_frame, text=save_text,
            style="primary.TButton",
            command=self._save_contact
        ).pack(side="right", padx=5)
    
    def _load_contact_data(self):
        """Carrega dados do contato para edição"""
        try:
            contacts = db.consulttablesql(
                db.csqllite, '*', 'contatos',
                f' where idcontatos={self.contact_id}', ';'
            )
            
            if contacts and len(contacts) > 0:
                c = contacts[0]
                self.entry_name.insert(0, c[1])
                self.entry_phone.insert(0, c[2])
                self.entry_email.insert(0, c[3])
                self.entry_group.insert(0, c[4])
                self.var_active.set(c[5])
                self.var_client.set(c[6])
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao carregar contato:\n{e}")
    
    def _save_contact(self):
        """Salva o contato"""
        name = self.entry_name.get().strip()
        phone = self.entry_phone.get().strip()
        email = self.entry_email.get().strip()
        group = self.entry_group.get().strip()
        active = self.var_active.get()
        client = self.var_client.get()
        
        # Validações
        if not name:
            show_warning(self, "Atenção", "O nome é obrigatório!")
            self.entry_name.focus()
            return
        
        # Limpa telefone
        phone = ''.join(filter(str.isdigit, phone))
        if len(phone) < 12 or len(phone) > 13:
            show_warning(self, "Atenção",
                        "Telefone inválido! Use formato: 5583988009900")
            self.entry_phone.focus()
            return
        
        datacad = datetime.now().strftime('%d%m%Y')
        
        try:
            if self.mode == "add":
                sql = (f'insert into contatos '
                      f'(nomecontato,fonecontato,emailcontato,nomegrupocontato,'
                      f'ativocontato,eclientecontato,datacad) '
                      f'values("{name}","{phone}","{email}","{group}",'
                      f'"{active}","{client}","{datacad}")')
                
                if ask_yes_no(self, "Confirmar", "Deseja realmente inserir este contato?"):
                    db.csqllite.execute(sql)
                    db.csqllite.connection.commit()
                    show_info(self, "Sucesso", "Contato inserido com sucesso!")
                    self.on_close()
            
            else:  # edit
                set_fields = (f"nomecontato='{name}',fonecontato='{phone}',"
                             f"emailcontato='{email}',nomegrupocontato='{group}',"
                             f"ativocontato='{active}',eclientecontato='{client}',"
                             f"datacad='{datacad}'")
                
                if ask_yes_no(self, "Confirmar", "Deseja realmente alterar este contato?"):
                    db.updatetablesql(db.csqllite, 'contatos', set_fields,
                                    f" idcontatos='{self.contact_id}'")
                    show_info(self, "Sucesso", "Contato alterado com sucesso!")
                    self.on_close()
        
        except Exception as e:
            show_warning(self, "Erro", f"Erro ao salvar contato:\n{e}")