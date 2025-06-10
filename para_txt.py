import pandas as pd
import numpy as np
import numpy_financial as npf
from pathlib import Path
import re
from collections import defaultdict

# Caminhos
pasta_planilhas = Path("./workspace")  # Coloque aqui sua pasta com planilhas
arquivo_txt = Path("./CB100601.TXT")  # Arquivo original .txt
saida_txt = arquivo_txt.with_name(arquivo_txt.stem + "_EDITADO.txt")

# Dicionário: (CPF, CONTRATO) → [lista de novos VPs formatados]
fluxos_por_pessoa = {}

# 📦 Etapa 1: Processa todas as planilhas
for planilha in pasta_planilhas.glob("*.*"):
    if not planilha.suffix.lower() in [".csv", ".xlsx"]:
        continue

    with open(planilha, "r", encoding="latin1") as f:
        linhas = f.readlines()

    if not linhas:
        continue

    dados = linhas[1:]  # Ignora cabeçalho

    pessoas = []
    parcelas_por_pessoa = []
    current_pessoa = None
    current_parcelas = []

    for linha in dados:
        partes = linha.strip().split(";")
        tipo = partes[12] if len(partes) > 12 and partes[12] in ["1", "11"] else (partes[6] if len(partes) > 6 and partes[6] in ["1", "11"] else "")

        if tipo == "1":
            if current_pessoa:
                pessoas.append(current_pessoa)
                parcelas_por_pessoa.append(current_parcelas)
                current_parcelas = []
            current_pessoa = partes
        elif tipo == "11":
            current_parcelas.append(partes)

    if current_pessoa:
        pessoas.append(current_pessoa)
        parcelas_por_pessoa.append(current_parcelas)

    for pessoa, parcelas in zip(pessoas, parcelas_por_pessoa):
        if not parcelas:
            continue

        df = pd.DataFrame(parcelas)

        try:
            df[16] = df[16].str.replace(",", ".").astype(float)
            df_abertas = df[df[16] > 0].copy()

            if df_abertas.empty:
                continue

            pmt = float(df_abertas[12].iloc[0].replace(",", "."))
            vp = df_abertas[16].sum()
            n = len(df_abertas)
            taxa = npf.rate(nper=n, pmt=-pmt, pv=vp, fv=0)

            # Novo fluxo de pagamento (PRICE invertido)
            novo_fluxo = [
                vp * (taxa * (1 + taxa) ** (n - i - 1)) / ((1 + taxa) ** n - 1)
                for i in range(n)
            ]

            # Extrai CPF e CONTRATO da linha da pessoa
            cpf = None
            contrato = None
            for campo in pessoa:
                if isinstance(campo, str):
                    cpf_match = re.search(r"\d{11}", campo)
                    contrato_match = re.search(r"\d{7}", campo)
                    if cpf_match:
                        cpf = cpf_match.group()
                    if contrato_match:
                        contrato = contrato_match.group()

            if cpf and contrato:
                chave = (cpf, contrato)
                fluxos_por_pessoa[chave] = [f"{int(round(valor * 100)):013d}" for valor in novo_fluxo]

        except Exception:
            continue

# 🛠 Etapa 2: Substitui os VPs no .TXT
contador_por_pessoa = defaultdict(int)
linhas_editadas = []

with open(arquivo_txt, "r", encoding="latin1") as f:
    for linha in f:
        linha_editada = linha
        cpf_match = re.search(r"\d{11}", linha)
        contrato_match = re.search(r"\d{7}", linha)

        if cpf_match and contrato_match:
            cpf = cpf_match.group()
            contrato = contrato_match.group()
            chave = (cpf, contrato)
            idx = contador_por_pessoa[chave]

            if chave in fluxos_por_pessoa and idx < len(fluxos_por_pessoa[chave]):
                novo_valor = fluxos_por_pessoa[chave][idx]
                linha_editada = linha[:192] + novo_valor + linha[205:]
                contador_por_pessoa[chave] += 1

        linhas_editadas.append(linha_editada)

# 💾 Etapa 3: Salva novo arquivo
with open(saida_txt, "w", encoding="latin1") as f:
    f.writelines(linhas_editadas)

print(f"✅ Novo arquivo salvo: {saida_txt.name}")
