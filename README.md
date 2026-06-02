# 📊 Dashboard Financeiro Empresarial

Dashboard interativo de KPIs financeiros construído com **Streamlit** e **Plotly**.  
Desenvolvido como projeto de portfólio em Business Intelligence e Análise de Dados.

---

## 🧠 O que esse dashboard analisa?

| Seção | KPIs |
|---|---|
| **Visão Executiva** | Receita, EBITDA, Lucro Líquido, Margem Líquida |
| **Rentabilidade** | Margem Bruta, Margem EBITDA, Margem Líquida, ROE, ROA |
| **Crescimento** | Crescimento YoY, CAGR 2019–2023 |
| **Liquidez & Solvência** | Liquidez Corrente, Dívida/EBITDA, Cobertura de Juros |
| **Fluxo de Caixa** | FCO, FCL, CAPEX, Conversão de Caixa |
| **Comparativo** | Radar de KPIs normalizados entre empresas |

---

## 🗂️ Estrutura do Projeto

```
financial_dashboard/
├── app.py              # Dashboard principal (Streamlit)
├── generate_data.py    # Gerador de dataset fictício realista
├── requirements.txt    # Dependências Python
└── README.md
```

---

## 🚀 Como rodar localmente

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/financial-dashboard.git
cd financial-dashboard
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Rode o dashboard
```bash
streamlit run app.py
```

Acesse em: `http://localhost:8501`

---

## ☁️ Deploy no Streamlit Cloud (gratuito)

1. Suba o projeto para um repositório público no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte sua conta GitHub
4. Selecione o repositório e o arquivo `app.py`
5. Clique em **Deploy** — o link público é gerado automaticamente

---

## 📦 Dados

Os dados são **gerados sinteticamente** pelo script `generate_data.py`:

- **5 empresas fictícias** em setores distintos (Tecnologia, Energia, Varejo, Saúde, Logística)
- **5 anos** de histórico (2019–2023), incluindo efeito COVID em 2020
- Todas as demonstrações financeiras: DRE, Balanço Patrimonial, Fluxo de Caixa
- KPIs calculados automaticamente

Para usar com dados reais, substitua a chamada `gerar_dados()` em `app.py` por:
```python
df = pd.read_csv("seus_dados.csv")
```

---

## 🛠️ Tecnologias

- [Streamlit](https://streamlit.io/) — interface web
- [Plotly](https://plotly.com/python/) — visualizações interativas
- [Pandas](https://pandas.pydata.org/) — manipulação de dados
- [NumPy](https://numpy.org/) — geração dos dados

---

## 👤 Autor

Projeto de portfólio — Ciência de Dados / Business Intelligence  
Desenvolvido para demonstrar competências em análise financeira, BI e visualização de dados.
# Projeto-BI-Financeiro
