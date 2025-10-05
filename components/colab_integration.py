import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

DATA_FILE = 'uploaded_data/dashboard_data.json'
UPLOAD_FOLDER = 'uploaded_data'

def load_colab_data():
    """Carrega dados recebidos do Google Colab"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Erro ao carregar dados do Colab: {e}")
            return None
    return None

def render_colab_integration():
    """Renderiza a view de integração com dados do Google Colab"""
    
    st.markdown('<h1 class="main-header">🛰️ SAR Biome Analysis - Real Data from Google Earth Engine</h1>', unsafe_allow_html=True)
    
    data = load_colab_data()
    
    if not data or data.get('status') == 'waiting_for_data':
        st.markdown("""
        <div style="text-align: center; padding: 60px 20px;">
            <div style="font-size: 4rem; margin-bottom: 20px;">⏳</div>
            <h2>Aguardando Dados do Google Colab</h2>
            <p style="opacity: 0.7; margin-top: 20px;">
                Este dashboard está pronto para receber análises do Google Earth Engine.<br>
                Execute o script Python no Google Colab para enviar os dados.
            </p>
            <div style="background: rgba(0, 212, 255, 0.1); border: 1px solid rgba(0, 212, 255, 0.3); 
                        border-radius: 10px; padding: 20px; margin: 30px auto; max-width: 600px; text-align: left;">
                <h4 style="color: #00D4FF; margin-bottom: 15px;">📡 Informações de Conexão</h4>
                <p><strong>Endpoint:</strong> <code style="background: rgba(0,0,0,0.3); padding: 2px 8px; border-radius: 4px;">POST https://turatteam.replit.app/api/update-data</code></p>
                <p><strong>Método:</strong> POST</p>
                <p><strong>Status da API:</strong> <span style="color: #00ff88;">✓ Online</span></p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <p style="opacity: 0.7;">
            📊 Análise da região: <strong>{data.get('region', 'N/A')}</strong> | 
            📅 Período: <strong>{data.get('analysis_period', 'N/A')}</strong> | 
            🕒 Última atualização: <strong>{format_timestamp(data.get('last_update'))}</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    metricas = data.get('metricas', {})
    if metricas:
        st.markdown('<h2 class="section-header">📈 Métricas Principais</h2>', unsafe_allow_html=True)
        
        cols = st.columns(4)
        metric_items = list(metricas.items())
        
        for idx, (key, value) in enumerate(metric_items[:4]):
            with cols[idx % 4]:
                render_metric_card(key, value)
        
        if len(metric_items) > 4:
            cols2 = st.columns(4)
            for idx, (key, value) in enumerate(metric_items[4:8]):
                with cols2[idx % 4]:
                    render_metric_card(key, value)
    
    imagens = data.get('imagens', {})
    if imagens:
        st.markdown('<h2 class="section-header">📊 Análises Visuais do Google Earth Engine</h2>', unsafe_allow_html=True)
        
        num_images = len(imagens)
        if num_images == 1:
            for filename, path in imagens.items():
                display_image(filename, path)
        elif num_images == 2:
            cols = st.columns(2)
            for idx, (filename, path) in enumerate(imagens.items()):
                with cols[idx]:
                    display_image(filename, path)
        else:
            for filename, path in imagens.items():
                display_image(filename, path)
    
    dados_detalhados = data.get('dados_detalhados', {})
    if dados_detalhados:
        st.markdown('<h2 class="section-header">📋 Dados Detalhados</h2>', unsafe_allow_html=True)
        
        tabs = st.tabs(list(dados_detalhados.keys()))
        
        for idx, (tabela_nome, tabela_dados) in enumerate(dados_detalhados.items()):
            with tabs[idx]:
                if isinstance(tabela_dados, dict):
                    display_dict_as_table(tabela_dados)
                elif isinstance(tabela_dados, list):
                    if tabela_dados and isinstance(tabela_dados[0], dict):
                        st.dataframe(tabela_dados, width='stretch')
                    else:
                        st.write(tabela_dados)
                else:
                    st.write(tabela_dados)
    
    with st.expander("🔍 Ver Dados Brutos (JSON)"):
        st.json(data)

def render_metric_card(label, value):
    """Renderiza um card de métrica"""
    color_class = get_color_class(label, value)
    
    formatted_value = format_metric_value(value)
    
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-title">{format_label(label)}</div>
        <div class="metric-value {color_class}">{formatted_value}</div>
    </div>
    """, unsafe_allow_html=True)

def display_image(filename, path):
    """Exibe uma imagem salva"""
    full_path = path.replace(f'/{UPLOAD_FOLDER}/', '')
    image_path = os.path.join(UPLOAD_FOLDER, full_path)
    
    if os.path.exists(image_path):
        st.markdown(f"**{format_label(filename.replace('.png', ''))}**")
        st.image(image_path, use_container_width=True)
    else:
        st.warning(f"Imagem não encontrada: {filename}")

def display_dict_as_table(data_dict):
    """Exibe um dicionário como tabela"""
    if not data_dict:
        st.info("Sem dados disponíveis")
        return
    
    rows = []
    for key, value in data_dict.items():
        rows.append({"Parâmetro": format_label(key), "Valor": format_metric_value(value)})
    
    st.dataframe(rows, width='stretch', hide_index=True)

def format_label(label):
    """Formata labels para exibição"""
    replacements = {
        '_': ' ',
        'veg': 'Vegetação',
        'water': 'Água',
        'ndvi': 'NDVI',
        'sar': 'SAR',
        'area': 'Área',
        'change': 'Mudança',
        'mean': 'Média',
        'median': 'Mediana',
        'std': 'Desvio Padrão',
        'min': 'Mínimo',
        'max': 'Máximo'
    }
    
    result = label
    for old, new in replacements.items():
        result = result.replace(old, new)
    
    return result.title()

def format_metric_value(value):
    """Formata valores de métricas"""
    if isinstance(value, (int, float)):
        if abs(value) >= 1000000:
            return f"{value/1000000:.2f}M"
        elif abs(value) >= 1000:
            return f"{value/1000:.2f}K"
        elif abs(value) < 1 and value != 0:
            return f"{value:.4f}"
        else:
            return f"{value:.2f}"
    return str(value)

def get_color_class(label, value):
    """Determina a classe de cor baseada no label e valor"""
    label_lower = label.lower()
    
    if 'alert' in label_lower or 'desmatamento' in label_lower or 'deforestation' in label_lower:
        return 'status-warning'
    
    if 'ndvi' in label_lower or 'vegetation' in label_lower or 'vegetacao' in label_lower:
        if isinstance(value, (int, float)):
            if value > 0.6:
                return 'status-good'
            elif value > 0.3:
                return 'status-info'
            else:
                return 'status-negative'
    
    if 'water' in label_lower or 'agua' in label_lower:
        return 'status-info'
    
    if isinstance(value, (int, float)):
        if value > 0:
            return 'status-positive'
        elif value < 0:
            return 'status-negative'
    
    return 'status-info'

def format_timestamp(timestamp):
    """Formata timestamp para exibição"""
    if not timestamp:
        return "N/A"
    
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime('%d/%m/%Y %H:%M:%S')
    except:
        return timestamp
