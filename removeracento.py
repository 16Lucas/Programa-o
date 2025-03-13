import unicodedata
import fdb
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def normalizar_texto(texto):
    """
    Remove acentos e converte para maiúsculas.
    """
    if not texto:
        return ""
    texto = texto.strip().upper()
    return ''.join(c for c in unicodedata.normalize('NFKD', texto) if not unicodedata.combining(c))

def conectar_banco(caminho_banco):
    try:
        con = fdb.connect(dsn=caminho_banco, user='sysdba', password='masterkey')
        return con
    except fdb.DatabaseError as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {e}")
        return None

def normalizar_nomes(con, progress_var, log_text):
    cursor = con.cursor()
    try:
        cursor.execute("""
            SELECT PARTEID, NOME FROM PARTE WHERE DOCUMENTO = ''
        """)
        registros = cursor.fetchall()
        
        total = len(registros)
        if total == 0:
            messagebox.showinfo("Informação", "Nenhum nome para normalizar encontrado.")
            return
        
        for idx, (parteid, nome) in enumerate(registros):
            nome_normalizado = normalizar_texto(nome)
            cursor.execute("UPDATE PARTE SET NOME = ? WHERE PARTEID = ?", (nome_normalizado, parteid))
            
            # Atualizar barra de progresso
            progress = int((idx + 1) / total * 100)
            progress_var.set(progress)
            root.update_idletasks()
            
            # Atualizar log
            log_text.insert(tk.END, f"PARTEID {parteid}: '{nome}' -> '{nome_normalizado}'\n")
            log_text.yview(tk.END)
        
        con.commit()
        messagebox.showinfo("Sucesso", "Nomes normalizados com sucesso!")
    except fdb.DatabaseError as e:
        messagebox.showerror("Erro", f"Erro ao normalizar nomes: {e}")

def selecionar_banco():
    caminho_banco = filedialog.askopenfilename(filetypes=[("Banco de Dados Firebird", "*.fdb")])
    if caminho_banco:
        entrada_banco.delete(0, tk.END)
        entrada_banco.insert(0, caminho_banco)

def iniciar_normalizacao():
    caminho_banco = entrada_banco.get()
    if not caminho_banco:
        messagebox.showwarning("Aviso", "Por favor, selecione o banco de dados.")
        return
    con = conectar_banco(caminho_banco)
    if con:
        normalizar_nomes(con, progress_var, log_text)
        con.close()

root = tk.Tk()
root.title("Normalizador de Nomes")
root.geometry("500x300")
root.configure(bg="#f0f0f0")

tk.Label(root, text="Banco de Dados Firebird:", bg="#f0f0f0").pack(anchor="w", padx=10, pady=5)
entrada_banco = tk.Entry(root, width=50)
entrada_banco.pack(padx=10, pady=5)
btn_banco = tk.Button(root, text="Selecionar", command=selecionar_banco)
btn_banco.pack(pady=5)

btn_iniciar = tk.Button(root, text="Normalizar Nomes", command=iniciar_normalizacao, width=20)
btn_iniciar.pack(pady=5)

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=5)

log_text = tk.Text(root, height=8, width=60)
log_text.pack(pady=5)

root.mainloop()