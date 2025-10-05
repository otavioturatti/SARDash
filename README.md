# 🛰️ SAR Biome Monitoring Dashboard

Dashboard web interativo para monitoramento de biomas brasileiros usando dados SAR (Synthetic Aperture Radar) e integração com Google Earth Engine.

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Docker](https://img.shields.io/badge/docker-ready-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## 🌟 Características

- 📊 **Dashboard Interativo** - Visualização em tempo real de métricas ambientais
- 🛰️ **Integração Google Earth Engine** - Recebe dados de análises SAR do Colab
- 🗺️ **Mapas Interativos** - Visualização geoespacial com Folium
- 📈 **Análise Temporal** - Séries temporais e comparações
- 🔥 **Detecção de Queimadas** - Monitoramento de áreas afetadas
- 🌊 **Monitoramento de Alagamentos** - Detecção de mudanças hídricas
- 🌿 **Análise de Vegetação** - NDVI e cobertura vegetal
- 🚀 **API REST** - Endpoint para receber dados externos

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────┐
│         Google Colab (Earth Engine)         │
│  Análise SAR → Métricas → Visualizações     │
└─────────────────┬───────────────────────────┘
                  │ HTTP POST
                  ↓
┌─────────────────────────────────────────────┐
│           FastAPI (Porta 8080)              │
│  /api/update-data → Recebe e salva dados    │
│  /api/health → Health check                 │
└─────────────────┬───────────────────────────┘
                  │ JSON File
                  ↓
┌─────────────────────────────────────────────┐
│         Streamlit (Porta 8501)              │
│  Dashboard → Visualizações → Insights       │
└─────────────────────────────────────────────┘
```

---

## 🚀 Deploy Rápido

### **Easypanel (Recomendado)**

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sar-dashboard.git

# 2. Siga o guia de deploy
cat DEPLOY_EASYPANEL.md
```

### **Docker Local**

```bash
# Build e iniciar
docker-compose up --build

# Acessar:
# Dashboard: http://localhost:8501
# API: http://localhost:8080
```

---

## 📦 Instalação Local (Desenvolvimento)

### **Pré-requisitos:**
- Python 3.11+
- pip

### **Passos:**

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sar-dashboard.git
cd sar-dashboard

# 2. Instale dependências
pip install -r requirements.txt

# 3. Inicie a API
uvicorn api_server:app --host 0.0.0.0 --port 8080 &

# 4. Inicie o Dashboard
streamlit run app.py --server.port 8501
```

---

## 🔧 Configuração

### **Variáveis de Ambiente**

Copie `.env.example` para `.env` e ajuste:

```bash
cp .env.example .env
```

Edite as variáveis conforme necessário.

### **Portas**

- **8080:** API FastAPI
- **8501:** Dashboard Streamlit

---

## 📊 Uso

### **1. Acessar Dashboard**

Abra o navegador em: `http://localhost:8501`

### **2. Integração com Google Colab**

No seu notebook do Colab, adicione:

```python
import requests
from datetime import datetime

DASHBOARD_URL = "http://seu-dominio.com"  # Ou localhost:8080

metricas = {
    "area_queimada_km2": 150.5,
    "area_alagada_km2": 80.2,
    "ndvi_medio": 0.75
}

payload = {
    "timestamp": datetime.now().isoformat(),
    "region": "Pantanal",
    "analysis_period": "2024",
    "status": "updated",
    "metricas": metricas,
    "dados_detalhados": {},
    "imagens": {}
}

response = requests.post(
    f"{DASHBOARD_URL}/api/update-data",
    json=payload
)

print(response.json())
```

### **3. Visualizar Dados**

No dashboard, navegue até: **"🛰️ Google Earth Engine Data"**

---

## 📁 Estrutura do Projeto

```
sar-dashboard/
├── app.py                      # Aplicação Streamlit principal
├── api_server.py               # API FastAPI
├── Dockerfile                  # Configuração Docker
├── docker-compose.yml          # Orquestração Docker
├── docker-entrypoint.sh        # Script de inicialização
├── requirements.txt            # Dependências Python
├── easypanel.yml              # Configuração Easypanel
├── .env.example               # Exemplo de variáveis de ambiente
├── components/                 # Componentes do dashboard
│   ├── colab_integration.py   # Integração Colab
│   ├── main_dashboard.py      # Dashboard principal
│   ├── time_series.py         # Análise temporal
│   └── ...
├── utils/                      # Utilitários
│   ├── data_processor.py      # Processamento de dados
│   ├── map_utils.py           # Mapas
│   └── visualization.py       # Visualizações
├── uploaded_data/             # Dados recebidos (persistente)
│   └── dashboard_data.json    # Dados estruturados
└── DEPLOY_EASYPANEL.md        # Guia de deploy
```

---

## 🛠️ Tecnologias

### **Backend**
- **FastAPI** - API REST moderna e rápida
- **Uvicorn** - Servidor ASGI

### **Frontend**
- **Streamlit** - Framework para dashboards
- **Plotly** - Gráficos interativos
- **Folium** - Mapas interativos

### **Processamento**
- **Pandas** - Manipulação de dados
- **NumPy** - Computação numérica
- **GeoPandas** - Dados geoespaciais

### **Deploy**
- **Docker** - Containerização
- **Easypanel** - Plataforma de deploy

---

## 📊 Métricas Monitoradas

### **Principais Indicadores:**
- 🔥 **Área de Queimadas** (km²)
- 🌊 **Extensão de Água** (km²)
- 🌿 **NDVI Médio** (Índice de Vegetação)
- 📉 **Mudança de Vegetação** (%)
- ⚠️ **Total de Alertas**
- 📡 **SAR Backscatter** (dB)
- 🌲 **Cobertura Florestal** (%)

---

## 🧪 Testes

### **Health Check:**

```bash
curl http://localhost:8080/api/health
```

### **Enviar Dados de Teste:**

```bash
curl -X POST http://localhost:8080/api/update-data \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-10-05T00:00:00",
    "region": "Pantanal",
    "analysis_period": "2024",
    "status": "updated",
    "metricas": {
      "area_queimada_km2": 150.5
    },
    "dados_detalhados": {},
    "imagens": {}
  }'
```

---

## 🐛 Troubleshooting

### **Problema: API não responde**
```bash
# Verificar se está rodando
curl http://localhost:8080/api/health

# Ver logs
docker logs sar-biome-dashboard
```

### **Problema: Streamlit não carrega**
```bash
# Verificar porta
netstat -tulpn | grep 8501

# Reiniciar container
docker-compose restart
```

---

## 🤝 Contribuindo

Contribuições são bem-vindas!

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

## 👥 Autores

- **Equipe SAR Biome Monitoring**
- Desenvolvido para o NASA Space Apps Challenge 2025

---

## 📞 Suporte

- **Documentação:** [DEPLOY_EASYPANEL.md](DEPLOY_EASYPANEL.md)
- **Issues:** https://github.com/seu-usuario/sar-dashboard/issues
- **Email:** contato@seu-dominio.com

---

## 🌟 Agradecimentos

- NASA Space Apps Challenge
- Google Earth Engine
- Sentinel-1 SAR Data
- Comunidade Open Source

---

**Desenvolvido com ❤️ para monitoramento ambiental**
