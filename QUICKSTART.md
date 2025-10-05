# ⚡ Quick Start - SAR Biome Dashboard

## 🚀 Deploy em 5 Minutos

### **Opção 1: Docker Local (Teste)**

```bash
# 1. Clone o projeto
git clone https://github.com/seu-usuario/sar-dashboard.git
cd sar-dashboard

# 2. Inicie com Docker Compose
docker-compose up --build

# 3. Acesse:
# Dashboard: http://localhost:8501
# API: http://localhost:8080/api/health
```

---

### **Opção 2: Easypanel (Produção)**

```bash
# 1. Faça upload para GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/seu-usuario/sar-dashboard.git
git push -u origin main

# 2. No Easypanel:
# - Create Service → App → From GitHub
# - Selecione o repositório
# - Build Method: Dockerfile
# - Portas: 8080 (API) e 8501 (Dashboard)
# - Deploy!

# 3. Configure domínios:
# - seu-dominio.com → porta 8501
# - api.seu-dominio.com → porta 8080
```

---

## 🧪 Testar Integração

### **1. Verificar API:**

```bash
curl https://api.seu-dominio.com/api/health
```

### **2. Enviar Dados do Colab:**

No Google Colab:

```python
import requests
from datetime import datetime

DASHBOARD_URL = "https://api.seu-dominio.com"

payload = {
    "timestamp": datetime.now().isoformat(),
    "region": "Pantanal",
    "analysis_period": "2024",
    "status": "updated",
    "metricas": {
        "area_queimada_km2": 150.5,
        "area_alagada_km2": 80.2
    },
    "dados_detalhados": {},
    "imagens": {}
}

response = requests.post(f"{DASHBOARD_URL}/api/update-data", json=payload)
print(response.json())
```

### **3. Visualizar no Dashboard:**

Acesse: `https://seu-dominio.com`

Menu lateral → **"🛰️ Google Earth Engine Data"**

---

## 📚 Próximos Passos

- Leia o [README.md](README.md) completo
- Veja o guia detalhado: [DEPLOY_EASYPANEL.md](DEPLOY_EASYPANEL.md)
- Configure variáveis de ambiente: [.env.example](.env.example)

---

## 🆘 Problemas?

**API não responde:**
```bash
docker logs sar-biome-dashboard
```

**Streamlit não carrega:**
- Aguarde 30-60 segundos após o deploy
- Verifique logs no Easypanel

**Dados não aparecem:**
- Verifique se enviou para a URL correta
- Teste o endpoint: `/api/health`

---

**Pronto! 🎉**
