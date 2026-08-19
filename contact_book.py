import re
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets.tableview import Tableview


class ContactBook(ttk.Frame):
    def __init__(self, master):
        self.name = ttk.StringVar()
        self.email = ttk.StringVar()
        self.category = ttk.StringVar(value="Friend")
        self.search_var = ttk.StringVar()  # Variável para o campo de busca
        
        # Variável para rastrear qual linha estamos editando (None = Modo de Adição)
        self.linha_em_edicao = None
        
        # Lista para armazenar todos os contatos originais (para busca)
        self.todos_contatos = []
        
        super().__init__(master, padding=16)
        self.pack(fill=BOTH, expand=YES)

        ttk.Label(self, text="Contact Book", font="-size 16 -weight bold").pack()
   
        # --- FORMULÁRIO ---
        form = ttk.Labelframe(self, text="New contact", padding=12)
        form.pack(fill=X)
        form.columnconfigure(1, weight=1)

        ttk.Label(form, text="Name").grid(row=0, column=0, sticky=W, padx=(0, 8), pady=4)
        ttk.Entry(form, textvariable=self.name).grid(row=0, column=1, sticky=EW, pady=4)
 
        ttk.Label(form, text="Email").grid(row=1, column=0, sticky=W, padx=(0, 8), pady=4)
        email_entry = ttk.Entry(form, textvariable=self.email)
        email_entry.grid(row=1, column=1, sticky=EW, pady=4)

        def validar_email(*args):
            padrao = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
            if re.match(padrao, self.email.get()):
                email_entry.configure(bootstyle='success')
            else:
                email_entry.configure(bootstyle="danger")

        self.email.trace_add('write', validar_email)

        ttk.Label(form, text="Category").grid(row=2, column=0, sticky=W, padx=(0, 8), pady=4)
        category_combo = ttk.Combobox(form, textvariable=self.category, values=["Friend", "Family", "Work"], state="readonly")
        category_combo.grid(row=2, column=1, sticky=EW, pady=4)

        # Container para organizar os botões do formulário lado a lado
        btn_container = ttk.Frame(form)
        btn_container.grid(row=3, column=1, sticky=E, pady=(8, 0))

        # --- TABELA ---
        def _build_table():
            self.table = Tableview(
                self,
                coldata=["Name", "Email", "Category"],
                rowdata=[],
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
            self.status = ttk.Label(self, text="Nenhum contato na agenda", bootstyle="secondary")
            self.status.pack(fill=X, pady=(4, 0))

        _build_status()

        # --- FUNÇÃO DE BUSCA CUSTOMIZADA ---
        def buscar(*args):
            termo_busca = self.search_var.get().lower().strip()
            
            # Limpa a tabela atual
            if self.table.tablerows:
                self.table.delete_rows(list(range(len(self.table.tablerows))))
            
            if not termo_busca:
                # Se não houver termo de busca, mostra todos os contatos
                for contato in self.todos_contatos:
                    self.table.insert_row(values=contato)
                atualizar_contador()
                return
            
            # Filtra os contatos
            contatos_filtrados = []
            for contato in self.todos_contatos:
                nome, email, categoria = contato
                if (termo_busca in nome.lower() or 
                    termo_busca in email.lower() or 
                    termo_busca in categoria.lower()):
                    contatos_filtrados.append(contato)
            
            # Atualiza a tabela com os resultados filtrados
            for contato in contatos_filtrados:
                self.table.insert_row(values=contato)
            
            # Atualiza o status
            if contatos_filtrados:
                self.status.configure(
                    text=f"{len(contatos_filtrados)} contato(s) encontrado(s)", 
                    bootstyle="info"
                )
            else:
                self.status.configure(
                    text="Nenhum contato encontrado", 
                    bootstyle="warning"
                )

        # Bind para buscar enquanto digita
        self.search_var.trace_add('write', buscar)

        # --- MÉTODOS DE AÇÃO ---

        def add_contact():            
            name = self.name.get().strip()
            email = self.email.get().strip()
            categoria = self.category.get()
            
            if not name or not email:
                self.status.configure(text="Nome e email são obrigatórios!", bootstyle="danger")
                return
            
            if self.linha_em_edicao is None:
                # Modo de Inserção: Cria uma linha nova
                self.table.insert_row(values=[name, email, categoria])
                self.todos_contatos.append([name, email, categoria])  # Armazena para busca
                self.status.configure(text="Contato adicionado com sucesso!", bootstyle="success")
            else:
                # Modo de Edição: Atualiza os dados da linha selecionada anteriormente
                self.linha_em_edicao.values = [name, email, categoria]
                self.table.load_table_data()  # Recarrega a tabela visualmente
                
                # Atualiza na lista de todos os contatos
                try:
                    indice = int(self.linha_em_edicao.iid)
                    if indice < len(self.todos_contatos):
                        self.todos_contatos[indice] = [name, email, categoria]
                except (ValueError, IndexError):
                    pass
                
                cancel_edit_contact()         # Sai do modo de edição
                self.status.configure(text="Contato atualizado com sucesso!", bootstyle="success")
                return
            
            limpar_campos()
            atualizar_contador()

        def edit_contact():
            # Obtém a linha selecionada na tabela
            linha_selecionada = self.table.view.selection()

            if not linha_selecionada:
                self.status.configure(text="Selecione um contato na tabela para editar!", bootstyle="warning")
                return
            
            iid = linha_selecionada[0]
            indice_inteiro = self.table.view.index(iid)
            self.linha_em_edicao = self.table.get_row(indice_inteiro)
                       
            valores = self.linha_em_edicao.values
            self.name.set(valores[0])
            self.email.set(valores[1])
            self.category.set(valores[2])
            
            form.configure(text="Edit contact")
            self.add_button.configure(text="Save changes", bootstyle="info")
            self.cancel_button.grid(row=0, column=0, padx=(0, 4))

        def cancel_edit_contact():
            self.linha_em_edicao = None
            limpar_campos()
            form.configure(text="New contact")
            self.add_button.configure(text="Add contact", bootstyle="success")
            self.cancel_button.grid_remove()
            self.status.configure(text="Edição cancelada", bootstyle="secondary")

        def delete_contact():
            linha_selecionada = self.table.view.selection()

            if not linha_selecionada:
                self.status.configure(text="Selecione um contato na tabela para deletar!", bootstyle="warning")
                return

            iid = linha_selecionada[0]
            indice_inteiro = self.table.view.index(iid)
            
            if self.linha_em_edicao and self.table.view.selection()[0] == self.linha_em_edicao.iid:
                cancel_edit_contact()
            
            # Remove da lista de todos os contatos
            if indice_inteiro < len(self.todos_contatos):
                self.todos_contatos.pop(indice_inteiro)
            
            self.table.delete_rows([indice_inteiro])

            self.status.configure(text="Contato removido!", bootstyle="danger")
            atualizar_contador()

        def limpar_campos():
            self.name.set("")
            self.email.set("")
            self.category.set("Friend")
            email_entry.configure(bootstyle="")

        def atualizar_contador():
            count = len(self.table.tablerows)
            if count == 0:
                self.status.configure(text="Nenhum contato na agenda", bootstyle="secondary")
            else:
                self.status.configure(text=f"{count} contato(s) na agenda", bootstyle="secondary")

        # --- BOTÕES DO FORMULÁRIO ---
        self.cancel_button = ttk.Button(btn_container, text="Cancel", bootstyle="secondary", command=cancel_edit_contact)
        self.cancel_button.grid_remove() 

        self.add_button = ttk.Button(btn_container, text="Add contact", bootstyle="success", command=add_contact)
        self.add_button.grid(row=0, column=1)

        # --- BOTÕES DE GERENCIAMENTO (ABAIXO DA TABELA) ---
        acoes_container = ttk.Frame(self)
        acoes_container.pack(fill=X, pady=(0, 8))

        self.delete_button = ttk.Button(acoes_container, text="Delete contact", bootstyle="danger", command=delete_contact)
        self.delete_button.pack(side=RIGHT, padx=(4, 0))

        self.edit_button = ttk.Button(acoes_container, text="Edit contact", bootstyle="warning", command=edit_contact)
        self.edit_button.pack(side=RIGHT)


#=====================================================================================

# 🌙 APLICAÇÃO DO TEMA ESCURO
# Temas escuros disponíveis: darkly, cyborg, solar, vapor, superhero
app = ttk.Window(
    title="Contact Book", 
    size=(600, 800),
    themename="darkly"  # ← Tema escuro aplicado aqui!
)
ContactBook(app)
app.mainloop()