"""
===========================================================
📄 SCRIPT: Gerador de Novo Fluxo de Valor Presente (CNAB444)
===========================================================

📌 DESCRIÇÃO:
-------------
Este script lê planilhas de parcelas de contratos consignados,
recalcula os valores de cada parcela com base no valor presente 
e uma nova taxa implícita, e substitui esses valores em um 
arquivo CNAB `.TXT` (posição 193 a 205), conforme o layout 444.

✔️ Corrige PMTs (parcelas) com base no fluxo de pagamento PRICE.
✔️ Garante formatação correta de 13 dígitos no arquivo `.TXT`.
✔️ Evita sobrescrever registros de cabeçalho.
✔️ Trata valores inconsistentes ou inválidos automaticamente.


🔍 FUNCIONAMENTO:
-----------------
1. As planilhas possuem:
   - Linha tipo "1": identificação da pessoa (contém CPF e contrato)
   - Linhas tipo "11": parcelas com valores
2. Para cada grupo de parcelas:
   - Calcula a taxa de juros implícita usando numpy_financial
   - Recalcula o novo fluxo (PRICE invertido)
3. No `.TXT`:
   - Encontra todas as linhas que possuem CPF e contrato
   - Substitui o campo valor presente (posição 193–205) pelas novas PMTs
   - Ignora linhas sem vencimento (evita cabeçalhos)

📦 DEPENDÊNCIAS:
----------------
- pandas
- numpy
- numpy_financial
- pathlib
- re
