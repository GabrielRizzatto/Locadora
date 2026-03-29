import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.veiculo import VeiculoFactory, Categoria, Carro, Motorhome
from models.ExcecoesPersonalizadas import PlacaInvalidaError

class VeiculoListView:
    def __init__(self, root):
        self.root = root
        self.root.title("Locadora de Veículos - Menu Principal")
        self.root.geometry("650x400")
        
        self.veiculos_cadastrados = []

        lbl_titulo = tk.Label(self.root, text="Veículos Cadastrados", font=("Arial", 16), pady=10)
        lbl_titulo.pack()

        colunas = ("Placa", "Tipo", "Categoria", "Taxa Diária")
        self.tree = ttk.Treeview(self.root, columns=colunas, show="headings", height=10)
        self.tree.heading("Placa", text="Placa")
        self.tree.heading("Tipo", text="Tipo do Veículo")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Taxa Diária", text="Taxa Diária (R$)")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        frame_botoes = tk.Frame(self.root, pady=10)
        frame_botoes.pack()

        btn_novo = tk.Button(frame_botoes, text="Novo", width=15, command=self.abrir_tela_cadastro)
        btn_novo.grid(row=0, column=0, padx=10)

        btn_info = tk.Button(frame_botoes, text="Ver Informações", width=15, command=self.exibir_dados)
        btn_info.grid(row=0, column=1, padx=10)

        btn_remover = tk.Button(frame_botoes, text="Remover", width=15, command=self.remover_veiculo)
        btn_remover.grid(row=0, column=2, padx=10)

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for veiculo in self.veiculos_cadastrados:
            tipo_veiculo = "Carro" if isinstance(veiculo, Carro) else "Motorhome"
            self.tree.insert("", tk.END, values=(
                veiculo.placa, 
                tipo_veiculo, 
                veiculo.categoria.value, 
                f"{veiculo.taxa_diaria:.2f}"
            ))

    def exibir_dados(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo na listagem primeiro.")
            return
        
        item = self.tree.item(selecionado[0])
        placa_alvo = item['values'][0]
        
        veiculo = next((v for v in self.veiculos_cadastrados if v.placa == placa_alvo), None)
        
        if veiculo:
            tipo = "Carro" if isinstance(veiculo, Carro) else "Motorhome"
            info = (f"=== Informações do Veículo ===\n"
                    f"Placa: {veiculo.placa}\n"
                    f"Tipo: {tipo}\n"
                    f"Categoria: {veiculo.categoria.value}\n"
                    f"Taxa Diária: R$ {veiculo.taxa_diaria:.2f}\n"
                    f"Estado Atual: {veiculo.estado_atual.__class__.__name__}\n"
                    f"Valor do Seguro: R$ {veiculo.valor_seguro:.2f}")
            
            messagebox.showinfo("Dados do Veículo", info)

    def remover_veiculo(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Selecione um veículo na listagem para remover.")
            return
        
        item = self.tree.item(selecionado[0])
        placa_alvo = item['values'][0]
        
        self.veiculos_cadastrados = [v for v in self.veiculos_cadastrados if v.placa != placa_alvo]
        self.atualizar_lista()
        messagebox.showinfo("Remoção", f"Veículo placa {placa_alvo} removido com sucesso!")

    def abrir_tela_cadastro(self):
        top = tk.Toplevel(self.root)
        top.title("Cadastro de Veículo")
        top.geometry("350x400")
        
        tk.Label(top, text="Placa:").pack(pady=5)
        txt_placa = tk.Entry(top)
        txt_placa.pack()
        
        tk.Label(top, text="Tipo do Veículo:").pack(pady=5)
        cb_tipo = ttk.Combobox(top, values=["Carro", "Motorhome"], state="readonly")
        cb_tipo.pack()
        
        tk.Label(top, text="Categoria:").pack(pady=5)
        cb_categoria = ttk.Combobox(top, values=["ECONOMICO", "EXECUTIVO"], state="readonly")
        cb_categoria.pack()
        
        tk.Label(top, text="Taxa Diária (R$):").pack(pady=5)
        txt_taxa = tk.Entry(top)
        txt_taxa.pack()
        
        def salvar():
            placa = txt_placa.get().strip()
            tipo = cb_tipo.get().strip()
            categoria_str = cb_categoria.get().strip()
            taxa_str = txt_taxa.get().strip()
            
            if not placa or not tipo or not categoria_str or not taxa_str:
                messagebox.showerror("Atenção", "Todos os campos são obrigatórios!")
                return
            
            try:
                taxa = float(taxa_str)
            except ValueError:
                messagebox.showerror("Atenção", "A taxa diária deve ser um número válido!")
                return
                
            categoria_enum = Categoria.ECONOMICO if categoria_str == "ECONOMICO" else Categoria.EXECUTIVO
            
            try:
                novo_veiculo = VeiculoFactory.criar_veiculo(tipo, placa, categoria_enum, taxa)
                
                self.veiculos_cadastrados.append(novo_veiculo)
                
                self.atualizar_lista()
                
                messagebox.showinfo("Sucesso", "Veículo cadastrado com sucesso!")
                
                top.destroy()
                
            except (ValueError, PlacaInvalidaError, Exception) as error:
                messagebox.showerror("Erro nas Regras de Negócio", str(error))
        
        btn_salvar = tk.Button(top, text="Salvar", width=20, command=salvar)
        btn_salvar.pack(pady=20)

if __name__ == "__main__":
    janela_raiz = tk.Tk()
    app = VeiculoListView(janela_raiz)
    janela_raiz.mainloop()