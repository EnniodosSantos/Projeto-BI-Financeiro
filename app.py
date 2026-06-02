"""
app.py — Dashboard Financeiro Empresarial
KPIs: Rentabilidade · Crescimento · Liquidez · Fluxo de Caixa
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from generate_data import gerar_dados

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Financeiro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ─────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Syne', sans-serif;
    }

    .stApp {
        background: #0a0e1a;
        color: #e8eaf0;
    }

    section[data-testid="stSidebar"] {
        background: #0f1524;
        border-right: 1px solid #1e2740;
    }

    .kpi-card {
        background: linear-gradient(135deg, #111827 0%, #1a2235 100%);
        border: 1px solid #1e2d4a;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 12px;
        position: relative;
        overflow: hidden;
    }
    .kpi-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, #3b82f6, #06b6d4);
    }
    .kpi-label {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #64748b;
        margin-bottom: 6px;
    }
    .kpi-value {
        font-family: 'Space Mono', monospace;
        font-size: 28px;
        font-weight: 700;
        color: #e2e8f0;
        line-height: 1;
    }
    .kpi-delta {
        font-size: 12px;
        margin-top: 6px;
        font-weight: 600;
    }
    .kpi-delta.pos { color: #22c55e; }
    .kpi-delta.neg { color: #ef4444; }
    .kpi-delta.neu { color: #94a3b8; }

    .section-title {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        color: #3b82f6;
        margin: 32px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #1e2d4a;
    }

    .alert-box {
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        margin: 6px 0;
        font-weight: 500;
    }
    .alert-ok  { background: #052e16; border-left: 3px solid #22c55e; color: #86efac; }
    .alert-warn{ background: #2d1b00; border-left: 3px solid #f59e0b; color: #fcd34d; }
    .alert-bad { background: #1c0606; border-left: 3px solid #ef4444; color: #fca5a5; }

    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }
    .stSelectbox label, .stMultiSelect label { color: #94a3b8 !important; font-size: 12px !important; }
</style>
""", unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Syne, sans-serif", color="#94a3b8", size=12),
    margin=dict(l=20, r=20, t=40, b=20),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2d4a"),
)

AXIS_STYLE = dict(gridcolor="#1e2d4a", linecolor="#1e2d4a", tickcolor="#1e2d4a")

PALETTE = ["#3b82f6", "#06b6d4", "#8b5cf6", "#f59e0b", "#22c55e"]

# ── Carregar dados ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    return gerar_dados()

df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Filtros")
    st.markdown("---")

    empresas_disp = sorted(df["empresa"].unique())
    empresa_sel = st.selectbox("Empresa", empresas_disp)

    anos_disp = sorted(df["ano"].unique())
    ano_sel = st.selectbox("Ano de referência", anos_disp, index=len(anos_disp)-1)

    st.markdown("---")
    st.markdown("### Comparativo")
    empresas_comp = st.multiselect(
        "Comparar empresas",
        empresas_disp,
        default=empresas_disp[:3],
    )
    st.markdown("---")
    st.markdown(
        "<div style='color:#475569;font-size:11px;'>Dataset: 5 empresas fictícias · 2019–2023<br>Gerado com generate_data.py</div>",
        unsafe_allow_html=True
    )

# ── Filtros de dados ──────────────────────────────────────────────────────────
df_emp  = df[df["empresa"] == empresa_sel].sort_values("ano")
df_ano  = df[df["ano"] == ano_sel]
df_comp = df[df["empresa"].isin(empresas_comp)].sort_values(["empresa", "ano"])
row_atual = df_emp[df_emp["ano"] == ano_sel].iloc[0]

anos_anteriores = df_emp[df_emp["ano"] < ano_sel]
row_ant = anos_anteriores.iloc[-1] if not anos_anteriores.empty else None

def delta(atual, anterior, fmt="%"):
    if anterior is None or anterior == 0:
        return "", "neu"
    var = (atual - anterior) / abs(anterior)
    sinal = "▲" if var > 0 else "▼"
    cor = "pos" if var > 0 else "neg"
    if fmt == "%":
        return f"{sinal} {abs(var)*100:.1f}% vs ano anterior", cor
    return f"{sinal} {abs(var):.2f}x vs ano anterior", cor

def fmt_brl(v, div=1):
    v = v / div
    if abs(v) >= 1e3:
        return f"R$ {v/1e3:.1f} Bi"
    return f"R$ {v:.0f} M"

def fmt_pct(v):
    return f"{v*100:.1f}%"

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="display:flex;align-items:baseline;gap:16px;margin-bottom:4px;">
  <span style="font-size:28px;font-weight:800;color:#e2e8f0;">{empresa_sel}</span>
  <span style="font-size:14px;color:#3b82f6;font-weight:700;letter-spacing:.1em;">
    {row_atual['setor'].upper()} · {ano_sel}
  </span>
</div>
<div style="color:#475569;font-size:13px;margin-bottom:24px;">
  Dashboard de KPIs Financeiros — Rentabilidade · Liquidez · Fluxo de Caixa
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — VISÃO EXECUTIVA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">01 · Visão Executiva</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

def kpi_card(col, label, value, delta_txt, delta_cor):
    col.markdown(f"""
    <div class="kpi-card">
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-delta {delta_cor}">{delta_txt}</div>
    </div>""", unsafe_allow_html=True)

d_txt, d_cor = delta(row_atual["receita_liquida"], row_ant["receita_liquida"] if row_ant is not None else None)
kpi_card(c1, "Receita Líquida", fmt_brl(row_atual["receita_liquida"]), d_txt, d_cor)

d_txt, d_cor = delta(row_atual["ebitda"], row_ant["ebitda"] if row_ant is not None else None)
kpi_card(c2, "EBITDA", fmt_brl(row_atual["ebitda"]), d_txt, d_cor)

d_txt, d_cor = delta(row_atual["lucro_liquido"], row_ant["lucro_liquido"] if row_ant is not None else None)
kpi_card(c3, "Lucro Líquido", fmt_brl(row_atual["lucro_liquido"]), d_txt, d_cor)

d_txt, d_cor = delta(row_atual["margem_liquida"], row_ant["margem_liquida"] if row_ant is not None else None)
kpi_card(c4, "Margem Líquida", fmt_pct(row_atual["margem_liquida"]), d_txt, d_cor)

# Gráfico de evolução — DRE
fig_dre = go.Figure()
metricas_dre = {
    "Receita Líquida": ("receita_liquida", PALETTE[0]),
    "EBITDA":          ("ebitda",          PALETTE[1]),
    "Lucro Líquido":   ("lucro_liquido",   PALETTE[2]),
}
for nome, (col, cor) in metricas_dre.items():
    fig_dre.add_trace(go.Scatter(
        x=df_emp["ano"], y=df_emp[col],
        name=nome, line=dict(color=cor, width=2.5),
        mode="lines+markers",
        marker=dict(size=6, color=cor),
        hovertemplate=f"<b>{nome}</b><br>R$ %{{y:,.0f}} M<extra></extra>",
    ))
fig_dre.update_layout(**PLOTLY_LAYOUT, title="Evolução DRE (R$ Milhões)", height=320)
fig_dre.update_xaxes(**AXIS_STYLE)
fig_dre.update_yaxes(**AXIS_STYLE)
st.plotly_chart(fig_dre, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — RENTABILIDADE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">02 · Rentabilidade</div>', unsafe_allow_html=True)

col_a, col_b = st.columns(2)

with col_a:
    # Margens ao longo do tempo
    fig_mg = go.Figure()
    margens = {
        "Margem Bruta":   ("margem_bruta",   PALETTE[0]),
        "Margem EBITDA":  ("margem_ebitda",  PALETTE[1]),
        "Margem Líquida": ("margem_liquida", PALETTE[2]),
    }
    for nome, (col, cor) in margens.items():
        fig_mg.add_trace(go.Scatter(
            x=df_emp["ano"], y=df_emp[col]*100,
            name=nome, line=dict(color=cor, width=2.5),
            mode="lines+markers", marker=dict(size=6),
            hovertemplate=f"<b>{nome}</b>: %{{y:.1f}}%<extra></extra>",
        ))
    fig_mg.update_layout(**PLOTLY_LAYOUT, title="Evolução das Margens (%)", height=300)
    fig_mg.update_xaxes(**AXIS_STYLE)
    fig_mg.update_yaxes(**AXIS_STYLE, ticksuffix="%")
    st.plotly_chart(fig_mg, use_container_width=True)

with col_b:
    # ROE e ROA comparativo entre empresas no ano selecionado
    df_roe = df_ano[df_ano["empresa"].isin(empresas_comp)].sort_values("roe", ascending=True)
    fig_roe = go.Figure()
    fig_roe.add_trace(go.Bar(
        y=df_roe["empresa"], x=df_roe["roe"]*100,
        name="ROE", orientation="h",
        marker_color=PALETTE[0], opacity=0.9,
        hovertemplate="ROE: %{x:.1f}%<extra></extra>",
    ))
    fig_roe.add_trace(go.Bar(
        y=df_roe["empresa"], x=df_roe["roa"]*100,
        name="ROA", orientation="h",
        marker_color=PALETTE[1], opacity=0.9,
        hovertemplate="ROA: %{x:.1f}%<extra></extra>",
    ))
    fig_roe.update_layout(
        **PLOTLY_LAYOUT, title=f"ROE vs ROA por Empresa ({ano_sel})",
        barmode="group", height=300,
    )
    fig_roe.update_xaxes(**AXIS_STYLE, ticksuffix="%")
    fig_roe.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_roe, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — CRESCIMENTO
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">03 · Crescimento</div>', unsafe_allow_html=True)

col_c, col_d = st.columns(2)

with col_c:
    fig_cresc = go.Figure()
    for i, emp in enumerate(empresas_comp):
        d = df_comp[df_comp["empresa"] == emp].dropna(subset=["cresc_receita_yoy"])
        fig_cresc.add_trace(go.Bar(
            x=d["ano"], y=d["cresc_receita_yoy"]*100,
            name=emp.split()[0], marker_color=PALETTE[i % len(PALETTE)],
            opacity=0.85,
            hovertemplate=f"<b>{emp.split()[0]}</b>: %{{y:.1f}}%<extra></extra>",
        ))
    fig_cresc.update_layout(
        **PLOTLY_LAYOUT, title="Crescimento de Receita YoY (%)",
        barmode="group", height=300,
    )
    fig_cresc.update_xaxes(**AXIS_STYLE)
    fig_cresc.update_yaxes(**AXIS_STYLE, ticksuffix="%")
    st.plotly_chart(fig_cresc, use_container_width=True)

with col_d:
    # CAGR de receita por empresa
    cagr_rows = []
    for emp in empresas_comp:
        d = df[df["empresa"] == emp].sort_values("ano")
        r0, r1 = d["receita_liquida"].iloc[0], d["receita_liquida"].iloc[-1]
        n = len(d) - 1
        cagr = (r1 / r0) ** (1/n) - 1 if n > 0 else 0
        cagr_rows.append({"Empresa": emp.split()[0], "CAGR": cagr * 100})
    df_cagr = pd.DataFrame(cagr_rows).sort_values("CAGR")

    fig_cagr = go.Figure(go.Bar(
        x=df_cagr["CAGR"], y=df_cagr["Empresa"],
        orientation="h",
        marker=dict(
            color=df_cagr["CAGR"],
            colorscale=[[0, "#1e3a5f"], [1, "#3b82f6"]],
        ),
        hovertemplate="CAGR: %{x:.1f}%<extra></extra>",
    ))
    fig_cagr.update_layout(
        **PLOTLY_LAYOUT, title="CAGR Receita 2019–2023 (%)",
        height=300,
    )
    fig_cagr.update_xaxes(**AXIS_STYLE, ticksuffix="%")
    fig_cagr.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_cagr, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — LIQUIDEZ & SOLVÊNCIA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">04 · Liquidez & Solvência</div>', unsafe_allow_html=True)

col_e, col_f, col_g = st.columns(3)

liq = row_atual["liquidez_corrente"]
div_ebitda = row_atual["divida_liq_ebitda"]
cob_juros = row_atual["cobertura_juros"]

def gauge(value, title, min_v, max_v, thresholds, suffix="x"):
    steps = [
        {"range": [min_v, thresholds[0]], "color": "#1c0606"},
        {"range": [thresholds[0], thresholds[1]], "color": "#2d1b00"},
        {"range": [thresholds[1], max_v], "color": "#052e16"},
    ]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix, "font": {"family": "Space Mono", "color": "#e2e8f0", "size": 28}},
        title={"text": title, "font": {"family": "Syne", "color": "#94a3b8", "size": 13}},
        gauge={
            "axis": {"range": [min_v, max_v], "tickcolor": "#475569", "tickfont": {"color": "#475569"}},
            "bar": {"color": "#3b82f6", "thickness": 0.25},
            "bgcolor": "#0f1524",
            "bordercolor": "#1e2d4a",
            "steps": steps,
            "threshold": {
                "line": {"color": "#06b6d4", "width": 3},
                "thickness": 0.8,
                "value": thresholds[1],
            },
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", height=220,
                      margin=dict(l=20, r=20, t=50, b=10),
                      font=dict(family="Syne"))
    return fig

col_e.plotly_chart(gauge(liq, "Liquidez Corrente", 0, 4, [1.0, 1.5], "x"), use_container_width=True)
col_f.plotly_chart(gauge(max(div_ebitda, 0), "Dívida Líq. / EBITDA", 0, 6, [3.0, 2.0], "x"), use_container_width=True)
col_g.plotly_chart(gauge(min(cob_juros, 15), "Cobertura de Juros", 0, 15, [2.0, 3.0], "x"), use_container_width=True)

# Alertas de saúde financeira
st.markdown("**Semáforo de Saúde Financeira**")
ac1, ac2, ac3 = st.columns(3)

def alerta(col, label, valor, ok_min=None, warn_min=None, reverso=False, fmt="x"):
    v_fmt = f"{valor:.2f}{fmt}"
    if reverso:
        cls = "alert-ok" if valor <= (warn_min or 2) else ("alert-warn" if valor <= (ok_min or 4) else "alert-bad")
        icon = "✅" if valor <= (warn_min or 2) else ("⚠️" if valor <= (ok_min or 4) else "🔴")
    else:
        cls = "alert-ok" if valor >= (ok_min or 1.5) else ("alert-warn" if valor >= (warn_min or 1.0) else "alert-bad")
        icon = "✅" if valor >= (ok_min or 1.5) else ("⚠️" if valor >= (warn_min or 1.0) else "🔴")
    col.markdown(f'<div class="alert-box {cls}">{icon} {label}: <b>{v_fmt}</b></div>', unsafe_allow_html=True)

alerta(ac1, "Liquidez Corrente", liq, ok_min=1.5, warn_min=1.0)
alerta(ac2, "Dívida/EBITDA", div_ebitda, ok_min=4.0, warn_min=3.0, reverso=True)
alerta(ac3, "Cobertura de Juros", cob_juros, ok_min=3.0, warn_min=2.0)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — FLUXO DE CAIXA
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">05 · Fluxo de Caixa</div>', unsafe_allow_html=True)

col_h, col_i = st.columns(2)

with col_h:
    fig_fc = go.Figure()
    for nome, col_fc, cor in [
        ("FCO", "fco", PALETTE[0]),
        ("FCL", "fcl", PALETTE[2]),
        ("Lucro Líquido", "lucro_liquido", PALETTE[3]),
    ]:
        fig_fc.add_trace(go.Bar(
            x=df_emp["ano"], y=df_emp[col_fc],
            name=nome, marker_color=cor, opacity=0.85,
            hovertemplate=f"<b>{nome}</b>: R$ %{{y:,.0f}} M<extra></extra>",
        ))
    fig_fc.update_layout(
        **PLOTLY_LAYOUT, title="FCO vs FCL vs Lucro Líquido (R$ M)",
        barmode="group", height=320,
    )
    fig_fc.update_xaxes(**AXIS_STYLE)
    fig_fc.update_yaxes(**AXIS_STYLE)
    st.plotly_chart(fig_fc, use_container_width=True)

with col_i:
    # Conversão de caixa e CAPEX
    fig_conv = make_subplots(specs=[[{"secondary_y": True}]])
    fig_conv.add_trace(go.Bar(
        x=df_emp["ano"], y=df_emp["capex"],
        name="CAPEX", marker_color="#f59e0b", opacity=0.7,
        hovertemplate="CAPEX: R$ %{y:,.0f} M<extra></extra>",
    ), secondary_y=False)
    fig_conv.add_trace(go.Scatter(
        x=df_emp["ano"], y=df_emp["conversao_caixa"],
        name="Conversão de Caixa", line=dict(color="#06b6d4", width=2.5),
        mode="lines+markers", marker=dict(size=7),
        hovertemplate="Conv. Caixa: %{y:.2f}x<extra></extra>",
    ), secondary_y=True)
    fig_conv.update_layout(**PLOTLY_LAYOUT, title="CAPEX e Conversão de Caixa", height=320)
    fig_conv.update_xaxes(**AXIS_STYLE)
    fig_conv.update_yaxes(title_text="CAPEX (R$ M)", secondary_y=False, gridcolor="#1e2d4a")
    fig_conv.update_yaxes(title_text="Conversão (x)", secondary_y=True, gridcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_conv, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6 — COMPARATIVO ENTRE EMPRESAS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">06 · Comparativo entre Empresas</div>', unsafe_allow_html=True)

kpis_comp = {
    "Margem Líquida (%)": "margem_liquida",
    "ROE (%)": "roe",
    "Liquidez Corrente (x)": "liquidez_corrente",
    "Dívida/EBITDA (x)": "divida_liq_ebitda",
    "Margem EBITDA (%)": "margem_ebitda",
}

df_radar = df_ano[df_ano["empresa"].isin(empresas_comp)].copy()

fig_radar = go.Figure()
categorias = list(kpis_comp.keys())

for i, (_, row) in enumerate(df_radar.iterrows()):
    vals = []
    for kpi, col in kpis_comp.items():
        v = row[col]
        if "%" in kpi:
            v = v * 100
        vals.append(v)
    vals_norm = []
    for j, (kpi, col) in enumerate(kpis_comp.items()):
        all_vals = df_radar[col].values
        rng = all_vals.max() - all_vals.min()
        if rng == 0:
            vals_norm.append(0.5)
        else:
            vals_norm.append((vals[j] - all_vals.min()) / rng)

    fig_radar.add_trace(go.Scatterpolar(
        r=vals_norm + [vals_norm[0]],
        theta=categorias + [categorias[0]],
        name=row["empresa"].split()[0],
        line=dict(color=PALETTE[i % len(PALETTE)], width=2),
        fill="toself",
        fillcolor=f"rgba{tuple(list(px.colors.hex_to_rgb(PALETTE[i % len(PALETTE)])) + [0.08])}",
    ))

fig_radar.update_layout(
    paper_bgcolor="rgba(0,0,0,0)",
    polar=dict(
        bgcolor="#0f1524",
        radialaxis=dict(visible=True, range=[0, 1], color="#475569", gridcolor="#1e2d4a"),
        angularaxis=dict(color="#94a3b8", gridcolor="#1e2d4a"),
    ),
    font=dict(family="Syne", color="#94a3b8"),
    title=dict(text=f"Radar de KPIs — {ano_sel} (normalizado)", font=dict(color="#e2e8f0")),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    height=420,
    margin=dict(l=60, r=60, t=60, b=40),
)
st.plotly_chart(fig_radar, use_container_width=True)

# ── Tabela resumo ─────────────────────────────────────────────────────────────
st.markdown("**Tabela Resumo de KPIs**")
tabela_cols = {
    "Empresa": "empresa",
    "Setor": "setor",
    "Receita (R$M)": "receita_liquida",
    "Mg. Bruta": "margem_bruta",
    "Mg. EBITDA": "margem_ebitda",
    "Mg. Líquida": "margem_liquida",
    "ROE": "roe",
    "ROA": "roa",
    "Liq. Corrente": "liquidez_corrente",
    "Dívi./EBITDA": "divida_liq_ebitda",
}
df_tab = df_ano[df_ano["empresa"].isin(empresas_comp)][list(tabela_cols.values())].copy()
df_tab.columns = list(tabela_cols.keys())
df_tab["Receita (R$M)"] = df_tab["Receita (R$M)"].map(lambda x: f"R$ {x:,.0f}")
for col in ["Mg. Bruta", "Mg. EBITDA", "Mg. Líquida", "ROE", "ROA"]:
    df_tab[col] = df_tab[col].map(lambda x: f"{x*100:.1f}%")
for col in ["Liq. Corrente", "Dívi./EBITDA"]:
    df_tab[col] = df_tab[col].map(lambda x: f"{x:.2f}x")

st.dataframe(
    df_tab.set_index("Empresa"),
    use_container_width=True,
    height=220,
)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:40px;padding-top:20px;border-top:1px solid #1e2d4a;
     color:#334155;font-size:11px;text-align:center;">
  Dashboard Financeiro · Dados fictícios para fins de portfólio · Construído com Streamlit + Plotly
</div>
""", unsafe_allow_html=True)
