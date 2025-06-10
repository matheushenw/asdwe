import pandas as pd
from pathlib import Path
from collections import defaultdict

# Caminhos
pasta_planilhas = Path('.')
arquivo_txt = Path('txtcnab.txt')
saida_txt = arquivo_txt.with_name(arquivo_txt.stem + '_EDITADO.txt')

# Dicionário (CPF, CONTRATO) -> lista de novos valores formatados
fluxos_por_pessoa = {}

# --- Etapa 1: Ler planilhas e extrair novo fluxo ---
for planilha in pasta_planilhas.glob('*'):
    if planilha.suffix.lower() not in {'.xlsx', '.csv'}:
        continue

    if planilha.suffix.lower() == '.xlsx':
        df = pd.read_excel(planilha, header=None)
    else:
        df = pd.read_csv(planilha, sep=';', header=None, encoding='latin1')

    current_key = None
    valores = []

    for _, row in df.iterrows():
        tipo = ''
        if not pd.isna(row[6]):
            tipo = str(int(row[6])).strip()

        if tipo == '1':
            if current_key:
                fluxos_por_pessoa[current_key] = valores
            cpf = None
            contrato = None
            if not pd.isna(row[16]):
                cpf = str(int(row[16])).zfill(11)
            if not pd.isna(row[7]):
                contrato = str(int(row[7])).zfill(7)
            current_key = (cpf, contrato)
            valores = []
        elif tipo == '11' and current_key:
            valor = row[1]
            if pd.notna(valor):
                valor = float(str(valor).replace(',', '.'))
                valores.append(f"{int(round(valor * 100)):013d}")

    if current_key:
        fluxos_por_pessoa[current_key] = valores

# --- Etapa 2: Editar arquivo TXT ---
contador = defaultdict(int)
linhas_editadas = []

with open(arquivo_txt, 'r', encoding='latin1') as f:
    for linha in f:
        cpf = linha[223:234]
        contrato = linha[53:60]
        chave = (cpf, contrato)
        idx = contador[chave]
        if chave in fluxos_por_pessoa and idx < len(fluxos_por_pessoa[chave]):
            novo_valor = fluxos_por_pessoa[chave][idx]
            linha = linha[:192] + novo_valor + linha[205:]
            contador[chave] += 1
        linhas_editadas.append(linha)

# --- Etapa 3: Salvar novo arquivo ---
with open(saida_txt, 'w', encoding='latin1') as f:
    f.writelines(linhas_editadas)

print(f'✅ Novo arquivo salvo: {saida_txt.name}')
