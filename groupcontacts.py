import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.tableview import Tableview
from ui_base import (ModalWindow, Colors, Icons, CardFrame,
                     show_info, show_warning, ask_yes_no, safe_int, safe_float)

class ContactBook(ttk.Frame):
    def __init__(self, master):
        self.namegrp = ttk.StringVar()
        self.email = ttk.StringVar()
        self.category = ttk.StringVar(value="Amigos")
        self.search_var = ttk.StringVar()  # Variável para o campo de busca
        self.RowData = []
        # estilo de cor
        #ttk.Style("cyborg")
        
        # Variável para rastrear qual linha estamos editando (None = Modo de Adição)
        self.linha_em_edicao = None
        
        # Lista para armazenar todos os contatos originais (para busca)
        self.todos_contatos = []
        
        super().__init__(master, padding=16)
        self.pack(fill=BOTH, expand=YES)

        ttk.Label(self, text=f"{Icons.GROUP}Grupo para campanha", font="-size 16 -weight bold").pack()
   
        # --- FORMULÁRIO ---
        form = ttk.Labelframe(self, text=f"{Icons.ADD}Novo Grupo", padding=12)
        form.pack(fill=X)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Nome").grid(row=0, column=0, sticky=W, padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.namegrp).grid(row=0, column=1, sticky=EW, pady=4)

        ttk.Label(form, text="Category").grid(row=2, column=0, sticky=W, padx=(0, 8), pady=4)
        category_combo = ttk.Combobox(form, textvariable=self.category, values=["Amigos", "Familia", "trabalho"], state="readonly")
        category_combo.grid(row=2, column=1, sticky=EW, pady=4)

        # Container para organizar os botões do formulário lado a lado
        btn_container = ttk.Frame(form)
        btn_container.grid(row=3, column=1, sticky=E, pady=(8, 0))

        # --- TABELA ---
        """
        Buscar os dados da tabela no banco de dados 
        e retorna o array de dados do resultset
        """
        import databases as db
        self.RowData = []
        self.RowData = db.consulttablesql(db.con," Namegrp, category ", " grp ", " where idgrp is not null ", " order by  namegrp ;")
        def _build_table():
            self.table = Tableview(
                self,
                #coldata=["Name", "Email", "Category"],
                coldata=["Name", "Category"],
                rowdata=self.RowData,
                searchable=False,  # Desativado porque vamos usar busca customizada
                bootstyle="primary",
                height=8,
            )
            self.table.pack(fill=BOTH, expand=YES, pady=(12, 8))
        
        _build_table()

        # --- CAMPO DE BUSCA ---
        search_frame = ttk.Frame(self)
        search_frame.pack(fill=X, pady=(12, 8))
        
        ttk.Label(search_frame, text="Buscar").pack(side=LEFT, padx=(0, 8))
        
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, bootstyle="primary")
        self.search_entry.pack(side=LEFT, fill=X, expand=YES)
        
        def limpar_busca():
            self.search_var.set("")
            self.search_entry.focus()
        
        # Botão de limpar busca
        self.clear_search_btn = ttk.Button(
            search_frame, 
            text="🔄",
            bootstyle="secondary",
            command=limpar_busca,
            width=3
        )
        self.clear_search_btn.pack(side=LEFT, padx=(8, 0))

        # --- STATUS BAR ---
        def _build_status():
            self.status = ttk.Label(self, text=f"{Icons.WARNING}Nenhum grupo na tabela", bootstyle="secondary")
            self.status.pack(fill=X, pady=(4, 0))
            #self.atualizar_contador()
            #força a contagem dos dados assim que iniciar a app
            count = len(self.table.tablerows)
            if count == 0:
                self.status.configure(text=f"{Icons.WARNING}Nenhum grupo na tabela", bootstyle="secondary")
            else:
                self.status.configure(text=f"{Icons.CHECK} {count} grupo(s) na tabela", bootstyle="secondary")
            

        _build_status()

        # --- FUNÇÃO DE BUSCA CUSTOMIZADA ---
        def buscar(*args):
            termo_busca = self.search_var.get().lower().strip()
            
            # Limpa a tabela atual
            if self.table.tablerows:
                #self.table.delete_rows(list(range(len(self.table.tablerows))))
                idx = list(range(len(self.table.tablerows)-1,-1,-1))
                self.table.delete_rows(idx)
                            
            if not termo_busca:
                # Se não houver termo de busca, mostra todos os contatos
                for contato in self.todos_contatos:
                    self.table.insert_row(values=contato)
                atualizar_contador()
                return
            
            # Filtra os contatos
            contatos_filtrados = []
            for contato in self.todos_contatos:
                #nome, email, categoria = contato
                nome, categoria = contato
                if (termo_busca in nome.lower() or                  
                    termo_busca in categoria.lower()):
                    contatos_filtrados.append(contato)
            
            # Atualiza a tabela com os resultados filtrados
            for contato in contatos_filtrados:
                self.table.insert_row(values=contato)
            
            # Atualiza o status
            if contatos_filtrados:
                self.status.configure(
                    text=f"{Icons.CHECK}{len(contatos_filtrados)} grupo(s) encontrado(s)", 
                    bootstyle="info"
                )
            else:
                self.status.configure(
                    text=f"{Icons.WARNING}Nenhum grupo encontrado", 
                    bootstyle="warning"
                )

        # Bind para buscar enquanto digita
        self.search_var.trace_add('write', buscar)

        # --- MÉTODOS DE AÇÃO ---

        def add_contact():            
            namegrp = self.namegrp.get().strip()
            #email = self.email.get().strip()
            categoria = self.category.get()
            
            if not namegrp or not categoria:
                self.status.configure(text=f"{Icons.WARNING}Nome e categoria são obrigatórios!", bootstyle="danger")
                return
            import databases as db # importa para base de dados
            if self.linha_em_edicao is None:
                # Modo de Inserção: Cria uma linha nova
                #self.table.insert_row(values=[namegrp, email, categoria])
                self.table.insert_row(values=[namegrp, categoria])
                #self.todos_contatos.append([namegrp, email, categoria])  # Armazena para busca
                self.todos_contatos.append([namegrp, categoria])  # Armazena para busca
                db.inserttablesql(db.csqllite," grp ", f" namegrp, dtgrp,category ", f" '{namegrp}', date('now'),'{categoria}' ",";")
                self.status.configure(text=f"{Icons.CHECK}Grupo adicionado com sucesso!", bootstyle="success")
            else:
                # Modo de Edição: Atualiza os dados da linha selecionada anteriormente
                #self.linha_em_edicao.values = [namegrp, email, categoria]
                self.linha_em_edicao.values = [namegrp, categoria]
                self.table.load_table_data()  # Recarrega a tabela visualmente
                
                # Atualiza na lista de todos os contatos
                try:
                    #indice = int(self.linha_em_edicao.iid)
                    # Obtém a linha selecionada na tabela
                    linha_selecionada = self.table.view.selection()
                    iid = linha_selecionada[0]
                    indice = self.table.view.index(iid)
                    # atualiza no banco de dados
                    idgrp=indice
                    try:
                      db.updatetablesql(cursor=db.csqllite,
                        tablename= " grp ",
                        setlistfields= f" namegrp='{namegrp}', category='{categoria}' ", 
                        condition=f" idgrp = '{idgrp}' ")
                    except Exception as e:
                        from tools import update_log as uplog
                        uplog("".join(e.arg()))
                    if indice < len(self.todos_contatos):
                        #self.todos_contatos[indice] = [namegrp, email, categoria]
                        self.todos_contatos[indice] = [namegrp,  categoria]                        
                except (ValueError, IndexError):
                    print("".join(ValueError.args()))
                    pass
                
                cancel_edit_contact()         # Sai do modo de edição
                self.status.configure(text=f"{Icons.CHECK}Grupo atualizado com sucesso!", bootstyle="success")
                return
            
            limpar_campos()
            atualizar_contador()

        def edit_contact():
            # Obtém a linha selecionada na tabela
            linha_selecionada = self.table.view.selection()

            if not linha_selecionada:
                self.status.configure(text=f"{Icons.WARNING}Selecione um grupo na tabela para editar!", bootstyle="warning")
                return
            
            iid = linha_selecionada[0]
            indice_inteiro = self.table.view.index(iid)
            self.linha_em_edicao = self.table.get_row(indice_inteiro)
                       
            valores = self.linha_em_edicao.values
            self.namegrp.set(valores[0])
            #?self.email.set(valores[1])
            #?self.category.set(valores[2])
            self.category.set(valores[1])
            
            form.configure(text="Edit group")
            self.add_button.configure(text=f"{Icons.CHECK}Save changes", bootstyle="info")
            self.cancel_button.grid(row=0, column=0, padx=(0, 4))

        def cancel_edit_contact():
            self.linha_em_edicao = None
            limpar_campos()
            form.configure(text="New group")
            self.add_button.configure(text=f"{Icons.GROUP}Add group", bootstyle="success")
            self.cancel_button.grid_remove()
            self.status.configure(text=f"{Icons.WARNING}Edição cancelada", bootstyle="secondary")

        def delete_contact():
            linha_selecionada = self.table.view.selection()          

            if not linha_selecionada:
                self.status.configure(text=f"{Icons.WARNING}Selecione um grupo na tabela para deletar!", bootstyle="warning")
                return

            iid = linha_selecionada[0]
            indice_inteiro = self.table.view.index(iid)
            
            if self.linha_em_edicao and self.table.view.selection()[0] == self.linha_em_edicao.iid:
                cancel_edit_contact()
            
            # Remove da lista de todos os contatos
            if indice_inteiro < len(self.todos_contatos):
                self.todos_contatos.pop(indice_inteiro)
            
            self.table.delete_rows([indice_inteiro])

            #Deleta a linha na tabela do bd
            import databases as db
            db.deletetablesql(db.sqlite3,' grp ', ' * ', f" where idgrp = '{indice_inteiro}';")

            self.status.configure(text="Grupo removido!", bootstyle="danger")
            atualizar_contador()

        def limpar_campos():
            self.namegrp.set("")
            #self.email.set("")
            self.category.set("Amigos")
            #email_entry.configure(bootstyle="")

        def atualizar_contador():
            count = len(self.table.tablerows)
            if count == 0:
                self.status.configure(text=f"{Icons.WARNING}Nenhum grupo na tabela", bootstyle="secondary")
            else:
                self.status.configure(text=f"{Icons.CHECK} {count} grupo(s) na tabela", bootstyle="secondary")

        # --- BOTÕES DO FORMULÁRIO ---
        self.cancel_button = ttk.Button(btn_container, text=f"{Icons.BACK}Cancelar", bootstyle="secondary", command=cancel_edit_contact)
        self.cancel_button.grid_remove() 

        self.add_button = ttk.Button(btn_container, text=f"{Icons.GROUP}Adicionar grupo", bootstyle="success", command=add_contact)
        self.add_button.grid(row=0, column=1)

        # --- BOTÕES DE GERENCIAMENTO (ABAIXO DA TABELA) ---
        acoes_container = ttk.Frame(self)
        acoes_container.pack(fill=X, pady=(0, 8))

        self.delete_button = ttk.Button(acoes_container, text=f"{Icons.DELETE}Delete grupo", bootstyle="danger", command=delete_contact)
        self.delete_button.pack(side=RIGHT, padx=(4, 0))

        self.edit_button = ttk.Button(acoes_container, text=f"{Icons.EDIT}Edite grupo", bootstyle="warning", command=edit_contact)
        self.edit_button.pack(side=RIGHT)


#=====================================================================================

# 🌙 APLICAÇÃO DO TEMA ESCURO
# Temas escuros disponíveis: darkly, cyborg, solar, vapor, superhero
'''
app = ttk.Window(
    title="Grupo de contatos para campanha", 
    size=(600, 800),
    themename="darkly"  # ← Tema escuro aplicado aqui!
)
'''


'''
ContactBook(app)
app.mainloop()
'''
