# Guia de Formatação e Preparação de Datasets

Este documento descreve os requisitos de formato para datasets utilizados no Pangolin, incluindo estrutura esperada, mapeamento de colunas, formatos suportados e exemplos práticos.

---

## Índice

- [Formatos Suportados](#formatos-suportados)
- [Estrutura do Dataset](#estrutura-do-dataset)
- [Mapeamento de Colunas no config.yaml](#mapeamento-de-colunas-no-configyaml)
- [Exemplos de Datasets](#exemplos-de-datasets)
- [Preparação do Dataset](#preparação-do-dataset)
- [Boas Práticas](#boas-práticas)
- [Erros Comuns](#erros-comuns)

---

## Formatos Suportados

O Pangolin suporta três formatos de arquivo como entrada:

| Formato | Extensão | Observações |
|---|---|---|
| CSV | `.csv` | Separador vírgula padrão. Encoding recomendado: UTF-8 |
| JSON | `.json` | Array de objetos ou objeto com array. Ver exemplos |
| Excel | `.xlsx` | Lê a primeira planilha (sheet) do arquivo |

Coloque o(s) arquivo(s) de dados no diretório `data/` do projeto antes de executar `pg run`.

---

## Estrutura do Dataset

O dataset deve ser uma tabela onde **cada linha representa um item a ser classificado**. Não há restrição rígida de colunas além das mapeadas em `config.yaml`, mas alguns campos são recomendados para facilitar avaliação posterior.

### Colunas recomendadas

| Coluna | Papel | Obrigatório no Pangolin |
|---|---|---|
| Identificador (ex: `id`) | Chave única do registro | Não, mas fortemente recomendado |
| Texto de entrada (ex: `description`) | Texto que será enviado ao LLM | **Sim** (deve estar em `input_columns`) |
| Rótulo real (ex: `target`, `category`) | Classe correta para avaliação | Não (mas necessário para métricas de qualidade) |
| Campos auxiliares (ex: `timestamp`, `severity`) | Contexto adicional | Opcional |

### Dataset mínimo válido

```
id,description
1,"Servidor NTP mal configurado detectado"
2,"Tentativa de acesso não autorizado ao sistema"
3,"Atualização de firmware disponível para roteador"
```

### Dataset completo recomendado

```
id,description,target,source,timestamp
1,"Breve descrição: Alerta de servidor NTP mal configurado","DE-TE","CERT.br","2024-01-15"
2,"Tentativa de phishing detectada: e-mail solicitando credenciais","DE-FE","SOC Interno","2024-01-16"
3,"Ransomware identificado em endpoint Windows","PR-IP","EDR","2024-01-17"
```

---

## Mapeamento de Colunas no config.yaml

O mapeamento entre as colunas do dataset e o framework é feito via `config.yaml`:

```yaml
data:
  input_columns: [description]         # Colunas que compõem o texto enviado ao LLM
  required_columns: [id, target]       # Colunas que devem existir, mas não são input
```

### `input_columns` — Como o input é construído

Todas as colunas listadas são concatenadas em ordem para formar o texto de entrada:

**Exemplo com uma coluna:**
```yaml
data:
  input_columns: [description]
```
Input gerado: `"Servidor NTP mal configurado detectado"`

**Exemplo com múltiplas colunas:**
```yaml
data:
  input_columns: [assunto, corpo, remetente]
```
Input gerado:
```
assunto: Reunião de alinhamento amanhã
corpo: Confirmo presença para as 14h na sala 3
remetente: joao@empresa.com
```

### `required_columns` — Colunas de controle

Colunas em `required_columns` são verificadas na inicialização: o framework confirma que existem no dataset, mas **não as usa como input do prompt**. Use para identificadores e rótulos reais de avaliação.

---

## Exemplos de Datasets

### CSV — Classificação de e-mails

```csv
id,assunto,corpo,categoria_real
1,"Oferta imperdível!","Clique aqui e ganhe R$500 grátis hoje!","SPAM"
2,"Relatório Q3 2024","Segue em anexo o relatório trimestral conforme solicitado.","LEGIT"
3,"URGENTE: Confirme seus dados","Sua conta será bloqueada em 24h. Clique aqui.","SPAM"
4,"Convite: Reunião de equipe","Confirmo presença para amanhã às 14h na sala 3.","LEGIT"
```

Config correspondente:
```yaml
data:
  input_columns: [assunto, corpo]
  required_columns: [id, categoria_real]
```

### CSV — Classificação de incidentes de segurança

```csv
id,description,target,rouge
1,"Alerta: servidor NTP mal configurado. Data: Jun 2024","DE-TE",0.0
2,"Phishing detectado: e-mail solicitando credenciais bancárias","DE-FE",0.0
3,"Ransomware identificado em endpoint Windows 10","PR-IP",0.0
4,"Scan de portas detectado a partir de IP externo","DE-TE",0.0
5,"Credenciais comprometidas em serviço de terceiros","RS-AN",0.0
```

Config correspondente:
```yaml
data:
  input_columns: [description]
  required_columns: [id, target]
```

### JSON — Array de objetos

```json
[
  {
    "id": 1,
    "texto": "Servidor NTP mal configurado",
    "categoria": "DE-TE"
  },
  {
    "id": 2,
    "texto": "Tentativa de phishing por e-mail",
    "categoria": "DE-FE"
  }
]
```

Config correspondente:
```yaml
data:
  input_columns: [texto]
  required_columns: [id, categoria]
```

### JSON — Objeto com chave

```json
{
  "registros": [
    {"id": 1, "descricao": "...", "label": "..."},
    {"id": 2, "descricao": "...", "label": "..."}
  ]
}
```

### Excel (.xlsx)

A estrutura do Excel deve ter os cabeçalhos das colunas na **primeira linha** da primeira planilha. Cada linha subsequente representa um registro.

| id | description | target |
|---|---|---|
| 1 | Alerta de servidor NTP mal configurado | DE-TE |
| 2 | Phishing por e-mail detectado | DE-FE |

---

## Preparação do Dataset

### Passo 1 — Verificar encoding

Certifique-se de que o arquivo está em UTF-8 para evitar problemas com caracteres especiais:

```bash
# Converter para UTF-8 se necessário (Linux/macOS)
iconv -f latin1 -t utf-8 dados_originais.csv > dados_utf8.csv
```

### Passo 2 — Verificar cabeçalhos

Os nomes das colunas devem:
- Não conter espaços (use `_` ou `camelCase`)
- Ser consistentes com o que está em `config.yaml`
- Não ter caracteres especiais

```csv
# Ruim
id,Descrição do Incidente,Categoria Real
# Bom
id,description,target
```

### Passo 3 — Tratar valores ausentes

O framework não lida automaticamente com células vazias em `input_columns`. Preencha ou remova linhas com valores ausentes antes de executar:

```python
import pandas as pd

df = pd.read_csv("data/meus_dados.csv")
df = df.dropna(subset=["description"])   # Remove linhas sem texto de entrada
df.to_csv("data/meus_dados_limpos.csv", index=False)
```

### Passo 4 — Validar com script simples

```python
import pandas as pd

df = pd.read_csv("data/meus_dados.csv")

# Verificar colunas necessárias
required = ["id", "description", "target"]
missing = [c for c in required if c not in df.columns]
if missing:
    print(f"Colunas ausentes: {missing}")
else:
    print(f"Dataset válido: {len(df)} registros, {len(df.columns)} colunas")
    print(df.dtypes)
    print(df.head(3))
```

### Passo 5 — Colocar na pasta correta

```bash
cp meus_dados.csv meu_experimento/data/
```

O framework carrega automaticamente todos os arquivos CSV/JSON/XLSX encontrados em `data/`.

---

## Boas Práticas

**Usar subsets para testes iniciais**

Antes de executar o experimento completo, teste com um subset pequeno para validar a configuração:

```python
import pandas as pd

df = pd.read_csv("data/dataset_completo.csv")
df.head(10).to_csv("data/dataset_teste.csv", index=False)
```

**Manter o dataset original intacto**

Não modifique o arquivo original. Crie uma cópia preparada:

```
data/
├── dataset_original.csv      ← nunca modifique
└── dataset_preparado.csv     ← versão limpa e pronta para uso
```

**Incluir rótulos reais quando possível**

O campo `target` (ou equivalente) permite calcular métricas de qualidade como acurácia e ROUGE após a execução. Sem ele, você terá apenas as predições do modelo, sem como avaliar automaticamente.

**Balancear classes quando possível**

Para experimentos de classificação, tente usar datasets com distribuição equilibrada entre categorias para evitar viés nos resultados.

**Documentar o dataset**

Crie um arquivo `data/README.md` descrevendo a origem, versão e estrutura do dataset:

```markdown
# Dataset

- **Fonte:** CERT.br / SOC Interno
- **Período:** Janeiro–Junho 2024
- **Registros:** 1.247
- **Colunas:**
  - `id`: Identificador único do incidente
  - `description`: Descrição textual do incidente
  - `target`: Categoria NIST CSF real
```

---

## Erros Comuns

| Erro | Causa provável | Solução |
|---|---|---|
| `"Coluna não encontrada: description"` | Nome da coluna no CSV não corresponde ao `input_columns` | Alinhe os nomes no CSV e no `config.yaml` |
| `"Nenhum arquivo de dados encontrado"` | Pasta `data/` está vazia | Copie os arquivos de dados para `data/` |
| Caracteres corrompidos no output | Arquivo não está em UTF-8 | Converta o arquivo para UTF-8 |
| `ValueError: could not convert string to float` | Coluna numérica com valores de texto | Verifique e trate valores inesperados na coluna |
| Linhas ignoradas silenciosamente | Valores `NaN` em `input_columns` | Remova ou preencha linhas com valores ausentes |
