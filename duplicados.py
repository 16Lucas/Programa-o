import fdb
from datetime import datetime, date
import openpyxl
from openpyxl import Workbook
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk


# Função para conectar ao banco de dados Firebird
def conectar_banco(caminho_banco):
    try:
        con = fdb.connect(
            dsn=caminho_banco,
            user='sysdba',
            password='masterkey'
        )
        return con
    except fdb.DatabaseError as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar ao banco de dados: {e}")
        return None

# Função para testar a conexão com o banco de dados
def testar_conexao():
    caminho_banco = entrada_banco.get()
    if not caminho_banco:
        messagebox.showwarning("Aviso", "Por favor, selecione o caminho do banco de dados.")
        return
    con = conectar_banco(caminho_banco)
    if con:
        messagebox.showinfo("Conexão", "Conexão com o banco de dados bem-sucedida!")
        con.close()

def atualizar_referencias(con, tabela, coluna, id_antigo, id_novo):
    cursor = con.cursor()
    try:
        # Verificar se já existe uma entrada com o id_novo que causaria duplicação
        cursor.execute(f"""
            SELECT COUNT(*) 
            FROM {tabela} 
            WHERE {coluna} = ? 
              AND EXISTS (
                  SELECT 1 
                  FROM {tabela} 
                  WHERE {coluna} = ? 
                    AND {coluna} = ?
              )
        """, (id_novo, id_antigo, id_novo))
        existe = cursor.fetchone()[0]
        
        if existe:
            print(f"Registro com {coluna} = {id_novo} já existe na tabela {tabela}. Atualização ignorada para evitar duplicação.")
            return

        # Atualizar as referências
        cursor.execute(f"""
            UPDATE {tabela} 
            SET {coluna} = ?
            WHERE {coluna} = ?
        """, (id_novo, id_antigo))
        con.commit()
        print(f"Referências atualizadas na tabela {tabela} de {id_antigo} para {id_novo}.")
    except fdb.DatabaseError as e:
        print(f"Erro ao atualizar referências na tabela {tabela}: {e}")

def atualizar_referencias_imovelparte(con, antigo_parteid, novo_parteid, imovelid, tipoparticipanteid):
    cursor = con.cursor()
    try:
        # Verificar se já existe um registro com a combinação de IMOVELID e TIPOPARTICIPANTEID para o novo PARTEID
        cursor.execute("""
            SELECT COUNT(*) 
            FROM IMOVELPARTE 
            WHERE IMOVELID = ? AND PARTEID = ? AND TIPOPARTICIPANTEID = ?
        """, (imovelid, novo_parteid, tipoparticipanteid))
        
        existe = cursor.fetchone()[0]

        if existe:
            # Atualizar os valores combinados, se necessário
            cursor.execute("""
                UPDATE IMOVELPARTE 
                SET VALORPATRIMONIAL = VALORPATRIMONIAL + COALESCE((
                    SELECT VALORPATRIMONIAL 
                    FROM IMOVELPARTE 
                    WHERE PARTEID = ? AND IMOVELID = ? AND TIPOPARTICIPANTEID = ?
                ), 0),
                PERCENTUALPATRIMONIAL = PERCENTUALPATRIMONIAL + COALESCE((
                    SELECT PERCENTUALPATRIMONIAL 
                    FROM IMOVELPARTE 
                    WHERE PARTEID = ? AND IMOVELID = ? AND TIPOPARTICIPANTEID = ?
                ), 0)
                WHERE PARTEID = ? AND IMOVELID = ? AND TIPOPARTICIPANTEID = ?;
            """, (antigo_parteid, imovelid, tipoparticipanteid, antigo_parteid, imovelid, tipoparticipanteid, novo_parteid, imovelid, tipoparticipanteid))
            
            # Verificar se o novo registro foi atualizado corretamente
            cursor.execute("""
                SELECT COUNT(*) 
                FROM IMOVELPARTE 
                WHERE PARTEID = ? AND IMOVELID = ? AND TIPOPARTICIPANTEID = ?
            """, (novo_parteid, imovelid, tipoparticipanteid))
            
            existe = cursor.fetchone()[0]
            if existe == 0:
                raise Exception(f"Erro ao atualizar registro na tabela IMOVELPARTE para PARTEID = {novo_parteid}")

            # Excluir o registro duplicado
            cursor.execute("""
                DELETE FROM IMOVELPARTE 
                WHERE PARTEID = ? AND IMOVELID = ? AND TIPOPARTICIPANTEID = ?;
            """, (antigo_parteid, imovelid, tipoparticipanteid))
        else:
            # Se não existir, simplesmente atualize
            cursor.execute("""
                UPDATE IMOVELPARTE 
                SET PARTEID = ? 
                WHERE PARTEID = ? AND IMOVELID = ? AND TIPOPARTICIPANTEID = ?;
            """, (novo_parteid, antigo_parteid, imovelid, tipoparticipanteid))
        
        con.commit()
        print(f"Referências atualizadas na tabela IMOVELPARTE de {antigo_parteid} para {novo_parteid}.")
    except fdb.DatabaseError as e:
        print(f"Erro ao atualizar referências na tabela IMOVELPARTE: {e}")

def atualizar_referencias_movimentacaoimovelparte(con, antigo_parteid, novo_parteid, movimentacaoimovelid, tipoparticipanteid):
    cursor = con.cursor()
    try:
        # Verificar se o novo PARTEID já existe
        cursor.execute("""
            SELECT COUNT(*) 
            FROM MOVIMENTACAOIMOVELPARTE 
            WHERE MOVIMENTACAOIMOVELID = ? AND PARTEID = ? AND TIPOPARTICIPANTEID = ?
        """, (movimentacaoimovelid, novo_parteid, tipoparticipanteid))
        
        existe = cursor.fetchone()[0]

        if existe:
            # Se já existe, não precisa fazer nada
            print(f"O novo PARTEID {novo_parteid} já existe na tabela MOVIMENTACAOIMOVELPARTE.")
        else:
            # Se não existir, criar o novo registro com o novo PARTEID
            cursor.execute("""
                INSERT INTO MOVIMENTACAOIMOVELPARTE (MOVIMENTACAOIMOVELID, PARTEID, TIPOPARTICIPANTEID, PARTICIPACAO)
                SELECT MOVIMENTACAOIMOVELID, ?, TIPOPARTICIPANTEID, PARTICIPACAO
                FROM MOVIMENTACAOIMOVELPARTE
                WHERE PARTEID = ? AND MOVIMENTACAOIMOVELID = ? AND TIPOPARTICIPANTEID = ?;
            """, (novo_parteid, antigo_parteid, movimentacaoimovelid, tipoparticipanteid))
            
            # Excluir o registro antigo
            cursor.execute("""
                DELETE FROM MOVIMENTACAOIMOVELPARTE 
                WHERE PARTEID = ? AND MOVIMENTACAOIMOVELID = ? AND TIPOPARTICIPANTEID = ?;
            """, (antigo_parteid, movimentacaoimovelid, tipoparticipanteid))

        con.commit()
        print(f"Referências atualizadas na tabela MOVIMENTACAOIMOVELPARTE de {antigo_parteid} para {novo_parteid}.")
    except fdb.DatabaseError as e:
        print(f"Erro ao atualizar referências na tabela MOVIMENTACAOIMOVELPARTE: {e}")

def limpar_valores(dados):
    valores_tratados = []
    for valor in dados:
        if isinstance(valor, datetime):
            valor = valor.date()

        if isinstance(valor, date) and valor < date(1900, 1, 1):
            valores_tratados.append(date(1900, 1, 1))
        elif valor is None or valor == '':
            valores_tratados.append(None)
        else:
            valores_tratados.append(valor)
    
    return valores_tratados

def validar_tamanho_valores(dados, tamanhos):
    valores_tratados = []
    for valor, tamanho in zip(dados, tamanhos):
        if isinstance(valor, str):
            valores_tratados.append(valor[:tamanho])  # Truncar o valor para o tamanho máximo permitido
        else:
            valores_tratados.append(valor)
    return valores_tratados

def contar_campos_preenchidos(registro):
    return sum(1 for campo in registro if campo not in (None, '', datetime(1, 1, 1), date(1, 1, 1)))

def unificar_registros(registros):
    registro_base = list(registros[0])
    for registro in registros[1:]:
        for i, campo in enumerate(registro):
            if registro_base[i] in (None, '', datetime(1, 1, 1), date(1, 1, 1)):
                registro_base[i] = campo

    return tuple(registro_base)

def mover_e_excluir_duplicados(con, caminho_arquivo, progress_var, root, label_status):
    cursor = con.cursor()

    wb = Workbook()
    ws = wb.active
    ws.title = "Duplicados"
    
    headers = [
        "PARTEID", "NOME", "DOCUMENTO", "TIPOPESSOA", "NOMECONJUGE", "IDENTIDADE", "INSCRICAOMUNICIPAL", 
        "INSCRICAOESTADUAL", "NASCIMENTO", "FUNDACAO", "TELEFONECOMERCIAL", "TELEFONECELULAR", 
        "TELEFONERESIDENCIAL", "PROFISSAO", "ESTADOCIVIL", "EMAIL", "CONTATO", "NOMEUPPER", "OBSERVACAO", 
        "USUARIOID", "NACIONALIDADE", "ORGEMISSOR", "REGIMECASAMENTO", "SITUACAODOCUMENTO", 
        "CONJUGEPARTEID", "SEXO", "STATUSVERIFICADO", "DATACADASTRO", "RETERISS", "RNE", 
        "VALIDADOSINTER", "TIPODOCUMENTOPARTEID", "TIPOSERVIDORPUBLICO", "PESSOAOBRIGADACOAF", 
        "NOMEFANTASIA", "EMAILPROFISSIONAL", "PAI", "MAE", "DOCUMENTOUF", "DATACASAMENTO", "NUMEROPACTO", 
        "DATAPACTO", "LOCALREGISTROPACTO", "CAPACIDADECIVIL", "DATAEMISSAODOCUMENTO", 
        "MATRICULACASAMENTO", "CARTORIOCASAMENTO", "ORIGEMPARTEID", "CONVPARTEID"
    ]
    
    try:
        # Buscar nomes duplicados onde DOCUMENTO está vazio
        cursor.execute("""
            SELECT NOME
            FROM PARTE
            WHERE DOCUMENTO = ''
            GROUP BY NOME
            HAVING COUNT(*) > 1
        """)
        nomes_duplicados = cursor.fetchall()
        
        if not nomes_duplicados:
            print("Nenhum nome duplicado encontrado com DOCUMENTO vazio.")
            return
        
        total_nomes = len(nomes_duplicados)
        
        for idx, (nome,) in enumerate(nomes_duplicados):
            cursor.execute("""
                SELECT * FROM PARTE 
                WHERE NOME = ? AND DOCUMENTO = ''
                ORDER BY PARTEID
            """, (nome,))
            partes = cursor.fetchall()

            if len(partes) < 2:
                continue

            partes_ordenadas = sorted(partes, key=contar_campos_preenchidos, reverse=True)
            registro_unificado = unificar_registros(partes_ordenadas)
            
            for parte in partes_ordenadas[1:]:
                ws.append(limpar_valores(parte))
                try:
                    atualizar_referencias(con, 'IMOVELPARTE', 'PARTEID', parte[0], partes_ordenadas[0][0])
                    atualizar_referencias(con, 'MOVIMENTACAOIMOVELPARTE', 'PARTEID', parte[0], partes_ordenadas[0][0])
                    atualizar_referencias(con, 'AVISO', 'PARTEID', parte[0], partes_ordenadas[0][0])
                    atualizar_referencias(con, 'ENDERECOPARTE', 'PARTEID', parte[0], partes_ordenadas[0][0])
                    atualizar_referencias(con, 'INDICADORPESSOAL', 'PROPRIETARIOID', parte[0], partes_ordenadas[0][0])
                    atualizar_referencias(con, 'REPRESENTACAOPARTE', 'REPRESENTADOPARTEID', parte[0], partes_ordenadas[0][0])
                    atualizar_referencias(con, 'REPRESENTACAOPARTE', 'REPRESENTANTEPARTEID', parte[0], partes_ordenadas[0][0])
                    
                    cursor.execute("""
                        DELETE FROM PARTE WHERE PARTEID = ?
                    """, (parte[0],))
                    con.commit()
                    print(f"Registro com PARTEID {parte[0]} excluído da tabela PARTE.")
                except fdb.DatabaseError as e:
                    print(f"Erro ao excluir registro com PARTEID {parte[0]}: {e}")
            
            placeholders = ', '.join([f"{coluna} = ?" for coluna in headers])
            valores_atualizacao = tuple(validar_tamanho_valores(registro_unificado, [250] * len(headers))) + (registro_unificado[0],)
            cursor.execute(f"UPDATE PARTE SET {placeholders} WHERE PARTEID = ?", valores_atualizacao)
            con.commit()

            progress = int((idx + 1) / total_nomes * 100)
            progress_var.set(progress)
            label_status.config(text=f"Processando {idx + 1}/{total_nomes} registros")
            root.update_idletasks()

        caminho_completo = f"{caminho_arquivo}/registros_duplicados.xlsx"
        wb.save(caminho_completo)
        messagebox.showinfo("Processo Concluído", f"Arquivo Excel salvo com sucesso em {caminho_completo}.")
    
    except fdb.DatabaseError as e:
        messagebox.showerror("Erro", f"Erro ao processar registros duplicados: {e}")

# Função para iniciar o processamento
def iniciar_processamento():
    caminho_banco = entrada_banco.get()
    caminho_arquivo = entrada_pasta.get()

    if not caminho_banco:
        messagebox.showwarning("Aviso", "Por favor, selecione o caminho do banco de dados.")
        return

    if not caminho_arquivo:
        messagebox.showwarning("Aviso", "Por favor, selecione o caminho para salvar o arquivo Excel.")
        return

    con = conectar_banco(caminho_banco)
    if con:
        mover_e_excluir_duplicados(con, caminho_arquivo, progress_var, root, label_status)
        con.close()

# Funções de seleção de arquivos
def selecionar_banco():
    caminho_banco = filedialog.askopenfilename(filetypes=[("Banco de Dados Firebird", "*.fdb")])
    if caminho_banco:
        entrada_banco.delete(0, tk.END)
        entrada_banco.insert(0, caminho_banco)

def selecionar_pasta():
    caminho_pasta = filedialog.askdirectory()
    if caminho_pasta:
        entrada_pasta.delete(0, tk.END)
        entrada_pasta.insert(0, caminho_pasta)

# Criação da interface gráfica
root = tk.Tk()
root.title("Processador de Duplicados")
root.geometry("600x400")
root.configure(bg="#f0f0f0")

# Frame para seleção de banco de dados
frame_banco = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
frame_banco.pack(fill="x")

tk.Label(frame_banco, text="Caminho do Banco de Dados:", bg="#f0f0f0").pack(anchor="w")
entrada_banco = tk.Entry(frame_banco, width=60)
entrada_banco.pack(side="left", padx=5)
btn_banco = tk.Button(frame_banco, text="Selecionar", command=selecionar_banco)
btn_banco.pack(side="left", padx=5)

# Frame para seleção da pasta de salvamento
frame_pasta = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
frame_pasta.pack(fill="x")

tk.Label(frame_pasta, text="Caminho para Salvar o Arquivo Excel:", bg="#f0f0f0").pack(anchor="w")
entrada_pasta = tk.Entry(frame_pasta, width=60)
entrada_pasta.pack(side="left", padx=5)
btn_pasta = tk.Button(frame_pasta, text="Selecionar", command=selecionar_pasta)
btn_pasta.pack(side="left", padx=5)

# Frame para ações
frame_acoes = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
frame_acoes.pack(fill="x")

btn_teste_conexao = tk.Button(frame_acoes, text="Testar Conexão", command=testar_conexao, width=15)
btn_teste_conexao.pack(side="left", padx=5)

btn_iniciar = tk.Button(frame_acoes, text="Iniciar Processamento", command=iniciar_processamento, width=20)
btn_iniciar.pack(side="left", padx=5)

# Barra de progresso e status
frame_progresso = tk.Frame(root, bg="#f0f0f0", padx=10, pady=10)
frame_progresso.pack(fill="x")

progress_var = tk.IntVar()
progress_bar = ttk.Progressbar(frame_progresso, orient="horizontal", length=400, mode="determinate", variable=progress_var)
progress_bar.pack(pady=10)

label_status = tk.Label(frame_progresso, text="Aguardando...", bg="#f0f0f0", fg="green")
label_status.pack()

root.mainloop()