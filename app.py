import streamlit as st
import pandas as pd
from io import BytesIO
import base64
import re

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Estadísticas de Talleres",
    page_icon="escudotalleres.png",
    layout="wide"
)

# --- Estilos CSS ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0A192F; color: #E0E0E0; }
    h1, h2, h3, h4, h5 { font-weight: 700; color: #F0F8FF; }
    h1 {
        border-bottom: 2px solid #0056B3;
        padding-bottom: 10px;
        padding-top: 15px;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 2px solid #334B68; }
    .stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent; border: none; color: #B0C4DE; font-size: 16px; font-weight: 600; }
    .stTabs [data-baseweb="tab--selected"] { color: #FFFFFF; border-bottom: 2px solid #FFFFFF; }
    .custom-table { border-collapse: collapse; width: 100%; font-size: 14px; text-align: left; color: #E0E0E0; }
    .custom-table thead tr { background-color: #1A2E4B; color: #FFFFFF; text-transform: uppercase; font-size: 12px; }
    .custom-table th, .custom-table td { padding: 10px 12px; }
    .custom-table tbody tr { border-bottom: 1px solid #334B68; }
    .custom-table tbody tr:last-of-type { border-bottom: none; }
    .custom-table tbody tr:hover { background-color: #2D4C72; }
    .tooltip { position: relative; display: inline-block; cursor: help; }
    .tooltip .tooltiptext { visibility: hidden; width: 140px; background-color: #334B68; color: #fff; text-align: center; border-radius: 6px; padding: 5px 0; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -70px; opacity: 0; transition: opacity 0.3s; }
    .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
</style>
""", unsafe_allow_html=True)

# --- Carga y Preparación de Datos ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel('historial_talleres.xlsx')
    except FileNotFoundError:
        st.error("Error: No se encontró el archivo 'historial_talleres.xlsx'. Asegúrate de que esté en la misma carpeta.")
        st.stop()
        
    df.columns = df.columns.str.strip()
    if 'Penales' not in df.columns:
        df['Penales'] = None
    required_columns = ['Torneo', 'Categoría', 'Rival', 'Condición', 'Goles_Local', 'Goles_Visitante', 'Resultado', 'Instancia']
    for col in required_columns:
        if col not in df.columns:
            st.error(f"Error: Tu archivo de Excel debe tener una columna llamada '{col}'.")
            st.stop()
    
    df['Goles_Local'] = df['Goles_Local'].fillna(0).astype(int)
    df['Goles_Visitante'] = df['Goles_Visitante'].fillna(0).astype(int)
    df['Resultado (G-E-P)'] = df['Resultado']
    df['Resultado'] = df['Goles_Local'].astype(str) + '-' + df['Goles_Visitante'].astype(str)
    df['Torneo'] = df['Torneo'].str.replace('_', ' ')
    df['Penales'] = df['Penales'].astype(str).replace('nan', '')
    return df

df = load_data()

# --- Diccionario de Colores de Equipo (ACTUALIZADO) ---
team_colors = {
    # Equipos Principales
    "Boca Juniors": ("#000080", "#FFD700"), "River Plate": ("#FF0000", "#FFFFFF"), "Rosario Central": ("#000080", "#FFD700"),
    "San Lorenzo": ("#000080", "#FF0000"), "Belgrano": ("#00BFFF", "#333333"), "Instituto": ("#FF0000", "#FFFFFF"),
    "Racing": ("#87CEEB", "#FFFFFF"), "Independiente": ("#FF0000", "#FFFFFF"), "Newell's": ("#FF0000", "#000000"),
    "Estudiantes (LP)": ("#FF0000", "#FFFFFF"), "Gimnasia (LP)": ("#FFFFFF", "#000080"), "Velez Sarsfield": ("#000080", "#FFFFFF"),
    "Huracán": ("#FF0000", "#FFFFFF"), "Argentinos Juniors": ("#FF0000", "#FFFFFF"), "Unión (SF)": ("#FF0000", "#FFFFFF"),
    "Colón": ("#000000", "#FF0000"), "Lanus": ("#800000", "#FFFFFF"), "Banfield": ("#008000", "#FFFFFF"), "Talleres": ("#0056B3", "#FFFFFF"),
    # Lista Completa
    "9 de Julio (M)": ("#87CEEB", "#FFFFFF"), "Alianza Lima": ("#000080", "#FFFFFF"), "Aldosivi": ("#008000", "#FFFF00"),
    "All Boys": ("#FFFFFF", "#000000"), "Almagro": ("#000080", "#000000"), "Almirante Brown": ("#000000", "#FFFF00"),
    "Alumni": ("#FF0000", "#FFFFFF"), "Alvarado": ("#000080", "#FFFFFF"), "América": ("#FFFF00", "#000080"),
    "Arsenal": ("#87CEEB", "#FF0000"), "Atlanta": ("#000080", "#FFFF00"), "Atlético Rafaela": ("#87CEEB", "#FFFFFF"),
    "Atlético Paraná": ("#FF0000", "#FFFFFF"), "Atlético Tucumán": ("#87CEEB", "#FFFFFF"), "Barcelona": ("#FFFF00", "#FF0000"),
    "Ben Hur": ("#FFFFFF", "#000080"), "Boca Unidos": ("#FF0000", "#FFFF00"), "Bragantino": ("#FFFFFF", "#000000"),
    "Brown": ("#87CEEB", "#FF0000"), "CAI": ("#000080", "#FFFFFF"), "Central Córdoba (R)": ("#000080", "#FFFFFF"),
    "Central Córdoba (SdE)": ("#000000", "#FFFFFF"), "Central Norte (S)": ("#000000", "#FFFFFF"),
    "Centro Sportivo Alagoano": ("#000080", "#FFFFFF"), "Chacarita": ("#FF0000", "#000000"),
    "Chaco For Ever": ("#000000", "#FFFFFF"), "Cipolletti": ("#000000", "#FFFFFF"), "Cobresal": ("#FFA500", "#FFFFFF"),
    "Cortuluá": ("#FF0000", "#008000"), "Crucero del Norte": ("#FFFF00", "#FF0000"), "Defensa y Justicia": ("#008000", "#FFFF00"),
    "Defensores de Belgrano (BA)": ("#FF0000", "#000000"), "Defensores de Belgrano (VR)": ("#FF0000", "#FFFFFF"),
    "Deportes Concepción": ("#8A2BE2", "#FFFFFF"), "Deportes Tolima": ("#FFFF00", "#A52A2A"), "Deportivo Laferrere": ("#008000", "#FFFFFF"),
    "Deportivo Maipú": ("#FF0000", "#FFFFFF"), "Deportivo Morón": ("#FF0000", "#FFFFFF"), "Deportivo Roca": ("#FFA500", "#FFFFFF"),
    "Desamparados": ("#008000", "#FFFFFF"), "Douglas Haig": ("#FF0000", "#000000"), "El Porvenir": ("#FFFFFF", "#000000"),
    "Emelec": ("#000080", "#FFFFFF"), "Estudiantes (BA)": ("#FFFFFF", "#000000"), "Estudiantes (RC)": ("#87CEEB", "#FFFFFF"),
    "Estudiantes (SL)": ("#008000", "#FFFFFF"), "Ferro": ("#008000", "#FFFFFF"), "Ferro Carril Oeste (GP)": ("#008000", "#FFFFFF"),
    "Flamengo": ("#FF0000", "#000000"), "Gimnasia y Esgrima (CdU)": ("#87CEEB", "#FFFFFF"), "Gimnasia y Esgrima (J)": ("#87CEEB", "#FFFFFF"),
    "Gimnasia y Esgrima (M)": ("#87CEEB", "#FFFFFF"), "Gimnasia y Tiro (S)": ("#87CEEB", "#FFFFFF"),
    "Godoy Cruz": ("#000080", "#FFFFFF"), "Grêmio": ("#000080", "#000000"), "Guaraní Antonio Franco": ("#FF0000", "#000080"),
    "Guillermo Brown": ("#000080", "#FFFFFF"), "Gutiérrez SC": ("#87CEEB", "#FFFFFF"), "Huracán Corrientes": ("#FF0000", "#FFFFFF"),
    "Huracán (TA)": ("#FF0000", "#FFFFFF"), "Independiente (Ch)": ("#FF0000", "#FFFFFF"), "Independiente Petrolero": ("#FF0000", "#FFFFFF"),
    "Independiente Rivadavia": ("#000080", "#FFFFFF"), "Ituzaingó": ("#008000", "#FFFFFF"), "Juventud Antoniana": ("#000080", "#FFFFFF"),
    "Juventud Unida (G)": ("#87CEEB", "#FFFFFF"), "Juventud Unida Universitario": ("#FFFF00", "#000080"),
    "Libertad": ("#000000", "#FFFFFF"), "Los Andes": ("#FF0000", "#FFFFFF"), "Mitre (SdE)": ("#FFFF00", "#000000"),
    "Nueva Chicago": ("#000000", "#008000"), "Olimpo": ("#FFFF00", "#000000"), "Palestino": ("#FF0000", "#008000"),
    "Paraná": ("#FF0000", "#000080"), "Patronato": ("#FF0000", "#000000"), "Peñarol": ("#FFFF00", "#000000"),
    "Platense": ("#FFFFFF", "#A52A2A"), "Quilmes": ("#FFFFFF", "#000080"), "Racing (CBA)": ("#87CEEB", "#FFFFFF"),
    "Racing (O)": ("#87CEEB", "#FFFFFF"), "San Jorge (T)": ("#008000", "#FFFFFF"), "San Martín (M)": ("#FF0000", "#FFFFFF"),
    "San Martín (SJ)": ("#008000", "#000000"), "San Martín (T)": ("#FF0000", "#FFFFFF"), "Santamaria": ("#FFFF00", "#000000"),
    "Sao Paulo (BRA)": ("#FF0000", "#000000"), "Sarmiento": ("#008000", "#FFFFFF"), "Sol de América": ("#000080", "#FFFFFF"),
    "Sporting Cristal": ("#87CEEB", "#FFFFFF"), "Sportivo Belgrano (SF)": ("#008000", "#008000"), "Sportivo Italiano": ("#000080", "#FFFFFF"),
    "Sportivo Las Parejas": ("#FF0000", "#008000"), "Talleres (RdE)": ("#FF0000", "#FFFFFF"), "Tigre": ("#000080", "#FF0000"),
    "Tiro Federal (BB)": ("#FFFF00", "#000000"), "Tiro Federal (R)": ("#000080", "#FFFFFF"), "Unión Aconquija": ("#A52A2A", "#87CEEB"),
    "Unión (MdP)": ("#87CEEB", "#FFFFFF"), "Unión (S)": ("#008000", "#FFFFFF"), "Unión (VK)": ("#008000", "#FFFFFF"),
    "Universidad Católica": ("#000080", "#FFFFFF"), "Villa Dálmine": ("#8A2BE2", "#FFFFFF"),
    "Villa Mitre": ("#008000", "#000000"), "Villa San Carlos": ("#87CEEB", "#FFFFFF"),
}

def get_team_badge_html(team_name):
    color1, color2 = team_colors.get(team_name, ("#808080", "#C0C0C0"))
    return f"""<div style="display: flex; align-items: center; gap: 12px;"><div style="width: 24px; height: 24px; border-radius: 50%; background: linear-gradient(45deg, {color1} 50%, {color2} 50%); flex-shrink: 0; box-shadow: 0 0 5px rgba(0,0,0,0.2);"></div><span>{team_name}</span></div>"""

def style_resultado(row):
    resultado_gep = row['Resultado (G-E-P)']
    resultado_num = row['Resultado']
    penales = row['Penales']
    color_map = {'Victoria': '#34D399', 'Empate': '#FBBF24', 'Derrota': '#F87171'}
    color = color_map.get(resultado_gep, '#E0E0E0')
    base_html = f'<span style="color:{color}; font-weight:600;">{resultado_num}</span>'
    if pd.notna(penales) and str(penales).strip() != '':
        return f'<div class="tooltip">⚽ {base_html}<span class="tooltiptext">Penales: {penales}</span></div>'
    return base_html

# --- Título Principal con Escudo ---
col1, col2 = st.columns([1, 8])
with col1:
    try:
        st.image("escudotalleres.png", width=70)
    except Exception as e:
        st.warning("No se encontró 'escudotalleres.png'")
with col2:
    st.title('Estadísticas Históricas del Club Atlético Talleres')

# --- Creación de Pestañas ---
tab1, tab2 = st.tabs(["Historial por Rival", "Campaña por Torneo"])

with tab1:
    st.header("Historial Completo por Rival")
    historial = df.groupby('Rival')['Resultado (G-E-P)'].value_counts().unstack(fill_value=0)
    for col in ['Victoria', 'Empate', 'Derrota']:
        if col not in historial.columns:
            historial[col] = 0
    resumen_rivales = pd.DataFrame(index=historial.index)
    resumen_rivales['CLUB'] = [get_team_badge_html(rival) for rival in resumen_rivales.index]
    resumen_rivales['PJ'] = historial.sum(axis=1)
    resumen_rivales['G'] = historial['Victoria'].apply(lambda x: f'<span style="color:#34D399; font-weight:600;">{x}</span>')
    resumen_rivales['E'] = historial['Empate'].apply(lambda x: f'<span style="color:#FBBF24; font-weight:600;">{x}</span>')
    resumen_rivales['P'] = historial['Derrota'].apply(lambda x: f'<span style="color:#F87171; font-weight:600;">{x}</span>')
    resumen_rivales['Saldo'] = (historial['Victoria'] - historial['Derrota']).apply(
        lambda x: f'<span style="color:{"#34D399" if x > 0 else "#F87171" if x < 0 else "#E0E0E0"}; font-weight:600;">{x}</span>'
    )
    
    st.markdown(
        resumen_rivales[['CLUB', 'PJ', 'G', 'E', 'P', 'Saldo']].sort_values(by='PJ', ascending=False).to_html(
            escape=False, index=False, classes="custom-table"
        ), 
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    col_selector, col_detail = st.columns([1, 2])
    with col_selector:
        lista_rivales = sorted(df['Rival'].unique())
        rival_seleccionado = st.selectbox('Selecciona un rival:', options=lista_rivales, index=None, placeholder="Buscar rival...")
    with col_detail:
        if rival_seleccionado:
            partidos_rival = df[df['Rival'] == rival_seleccionado].copy()
            st.subheader(f"Desglose vs. {rival_seleccionado}")
            
            st.markdown("##### 🏟️ Por Condición")
            local_games = partidos_rival[partidos_rival['Condición'] == 'Local']
            if not local_games.empty:
                g = (local_games['Resultado (G-E-P)'] == 'Victoria').sum(); e = (local_games['Resultado (G-E-P)'] == 'Empate').sum(); p = (local_games['Resultado (G-E-P)'] == 'Derrota').sum()
                st.write(f"**Talleres como Local ({len(local_games)} PJ):** Ganó {g}, empató {e} y perdió {p}.")
            visit_games = partidos_rival[partidos_rival['Condición'] == 'Visitante']
            if not visit_games.empty:
                g = (visit_games['Resultado (G-E-P)'] == 'Victoria').sum(); e = (visit_games['Resultado (G-E-P)'] == 'Empate').sum(); p = (visit_games['Resultado (G-E-P)'] == 'Derrota').sum()
                st.write(f"**Talleres como Visitante ({len(visit_games)} PJ):** Ganó {g}, empató {e} y perdió {p}.")
            neutral_games = partidos_rival[partidos_rival['Condición'] == 'Neutral']
            if not neutral_games.empty:
                g = (neutral_games['Resultado (G-E-P)'] == 'Victoria').sum(); e = (neutral_games['Resultado (G-E-P)'] == 'Empate').sum(); p = (neutral_games['Resultado (G-E-P)'] == 'Derrota').sum()
                st.write(f"**En Cancha Neutral ({len(neutral_games)} PJ):** Ganó {g}, empató {e} y perdió {p}.")

            st.markdown("##### 🏆 Por Categoría")
            categorias = sorted(partidos_rival['Categoría'].unique())
            for cat in categorias:
                cat_games = partidos_rival[partidos_rival['Categoría'] == cat]
                t_wins = (cat_games['Resultado (G-E-P)'] == 'Victoria').sum(); r_wins = (cat_games['Resultado (G-E-P)'] == 'Derrota').sum(); empates = (cat_games['Resultado (G-E-P)'] == 'Empate').sum()
                st.write(f"**En {cat} ({len(cat_games)} PJ):** Talleres ganó {t_wins}, empataron {empates}, {rival_seleccionado} ganó {r_wins}.")
            
            st.markdown("---")
            st.markdown("**Listado de partidos:**")
            partidos_rival['Resultado Coloreado'] = partidos_rival.apply(style_resultado, axis=1)
            st.markdown(partidos_rival[['Torneo', 'Condición', 'Resultado Coloreado']].rename(columns={'Resultado Coloreado': 'Resultado'}).to_html(escape=False, index=False, classes="custom-table"), unsafe_allow_html=True)
        else:
            st.info("Selecciona un rival de la lista para ver el detalle completo.")

with tab2:
    st.header("🏆 Campaña por Torneo")
    lista_torneos = sorted(df['Torneo'].unique(), reverse=True)
    torneo_seleccionado_tab2 = st.selectbox('Selecciona un torneo:', options=lista_torneos, index=None, placeholder="Escribe o selecciona un torneo...", key="selector_torneo")
    
    if torneo_seleccionado_tab2:
        partidos_torneo = df[df['Torneo'] == torneo_seleccionado_tab2].copy()
        partidos_torneo['Rival'] = partidos_torneo['Rival'].apply(get_team_badge_html)
        partidos_torneo['Resultado Coloreado'] = partidos_torneo.apply(style_resultado, axis=1)
        st.markdown(
            partidos_torneo[['Instancia', 'Rival', 'Condición', 'Resultado Coloreado']].rename(columns={'Resultado Coloreado': 'Resultado'}).to_html(escape=False, index=False, classes="custom-table"),
            unsafe_allow_html=True
        )