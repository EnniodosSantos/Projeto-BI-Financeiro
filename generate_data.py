"""
generate_data.py
Gera dataset financeiro fictício realista para 5 empresas brasileiras (2019–2023).
Executa automaticamente ao ser importado pelo app.py.
"""

import pandas as pd
import numpy as np

SEED = 42
np.random.seed(SEED)

COMPANIES = {
    "AlphaTech S.A.":    {"setor": "Tecnologia",    "receita_base": 1_200, "margem_bruta": 0.62, "crescimento": 0.18},
    "BetaEnergy S.A.":   {"setor": "Energia",       "receita_base": 3_800, "margem_bruta": 0.38, "crescimento": 0.07},
    "GammaRetail S.A.":  {"setor": "Varejo",        "receita_base": 2_100, "margem_bruta": 0.28, "crescimento": 0.12},
    "DeltaFarma S.A.":   {"setor": "Saúde",         "receita_base":   950, "margem_bruta": 0.55, "crescimento": 0.14},
    "EpsilonLog S.A.":   {"setor": "Logística",     "receita_base": 1_650, "margem_bruta": 0.32, "crescimento": 0.09},
}

ANOS = [2019, 2020, 2021, 2022, 2023]


def gerar_dados():
    rows = []

    for empresa, cfg in COMPANIES.items():
        receita = cfg["receita_base"]

        for i, ano in enumerate(ANOS):
            # Choque COVID 2020
            choque = -0.10 if ano == 2020 else 0.0
            noise = np.random.uniform(-0.03, 0.03)
            crescimento_efetivo = cfg["crescimento"] + choque + noise

            if i > 0:
                receita = receita * (1 + crescimento_efetivo)

            receita_liq = receita * np.random.uniform(0.97, 1.00)
            lucro_bruto = receita_liq * cfg["margem_bruta"] * np.random.uniform(0.96, 1.04)

            # Despesas operacionais (SG&A)
            sgae = receita_liq * np.random.uniform(0.12, 0.18)
            depreciacao = receita_liq * np.random.uniform(0.03, 0.06)

            ebit = lucro_bruto - sgae - depreciacao
            ebitda = ebit + depreciacao

            despesas_fin = receita_liq * np.random.uniform(0.02, 0.05)
            lair = ebit - despesas_fin
            ir = max(lair * 0.34, 0)
            lucro_liq = lair - ir

            # Balanço
            ativo_total = receita_liq * np.random.uniform(1.2, 1.8)
            ativo_circ = ativo_total * np.random.uniform(0.35, 0.50)
            passivo_circ = ativo_circ * np.random.uniform(0.55, 0.80)
            divida_total = ativo_total * np.random.uniform(0.25, 0.45)
            caixa = ativo_circ * np.random.uniform(0.20, 0.35)
            pl = ativo_total - divida_total - passivo_circ * 0.4

            # Fluxo de Caixa
            fco = lucro_liq + depreciacao + receita_liq * np.random.uniform(-0.03, 0.05)
            capex = receita_liq * np.random.uniform(0.04, 0.09)
            fcl = fco - capex

            rows.append({
                "empresa": empresa,
                "setor": cfg["setor"],
                "ano": ano,
                # DRE
                "receita_liquida": round(receita_liq, 2),
                "lucro_bruto": round(lucro_bruto, 2),
                "ebitda": round(ebitda, 2),
                "ebit": round(ebit, 2),
                "despesas_financeiras": round(despesas_fin, 2),
                "lucro_liquido": round(lucro_liq, 2),
                "depreciacao": round(depreciacao, 2),
                # Balanço
                "ativo_total": round(ativo_total, 2),
                "ativo_circulante": round(ativo_circ, 2),
                "passivo_circulante": round(passivo_circ, 2),
                "divida_total": round(divida_total, 2),
                "caixa": round(caixa, 2),
                "patrimonio_liquido": round(pl, 2),
                # Fluxo de Caixa
                "fco": round(fco, 2),
                "capex": round(capex, 2),
                "fcl": round(fcl, 2),
            })

    df = pd.DataFrame(rows)

    # ── KPIs calculados ──────────────────────────────────────────────
    df["margem_bruta"]       = df["lucro_bruto"]    / df["receita_liquida"]
    df["margem_ebitda"]      = df["ebitda"]          / df["receita_liquida"]
    df["margem_liquida"]     = df["lucro_liquido"]   / df["receita_liquida"]
    df["roe"]                = df["lucro_liquido"]   / df["patrimonio_liquido"]
    df["roa"]                = df["lucro_liquido"]   / df["ativo_total"]
    df["liquidez_corrente"]  = df["ativo_circulante"]/ df["passivo_circulante"]
    df["divida_liq_ebitda"]  = (df["divida_total"] - df["caixa"]) / df["ebitda"]
    df["cobertura_juros"]    = df["ebit"]            / df["despesas_financeiras"]
    df["conversao_caixa"]    = df["fco"]             / df["lucro_liquido"].replace(0, np.nan)

    # Crescimento YoY de receita
    df = df.sort_values(["empresa", "ano"])
    df["cresc_receita_yoy"] = df.groupby("empresa")["receita_liquida"].pct_change()

    return df


if __name__ == "__main__":
    df = gerar_dados()
    df.to_csv("dados_financeiros.csv", index=False)
    print(f"Dataset gerado: {df.shape[0]} linhas x {df.shape[1]} colunas")
    print(df.head())
