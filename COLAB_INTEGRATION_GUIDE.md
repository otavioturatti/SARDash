# Guia de Integração: Google Colab → Dashboard Replit

## 🎯 Visão Geral

Este dashboard agora está preparado para receber dados de análises do Google Earth Engine executadas no Google Colab. Os dados são enviados via requisição HTTP POST e exibidos automaticamente na nova view **"Google Earth Engine Data"**.

## 🚀 Como Enviar Dados do Google Colab

### 1. Estrutura do JSON

O Google Colab deve enviar um JSON com a seguinte estrutura:

```json
{
  "timestamp": "2024-10-04T14:30:00",
  "region": "Pantanal",
  "analysis_period": "2024-01 a 2024-09",
  "status": "updated",
  "metricas": {
    "ndvi_medio": 0.75,
    "area_vegetacao_km2": 15000,
    "mudanca_vegetacao_percent": -2.3,
    "agua_extent_km2": 3500,
    "total_alerts": 42,
    "sar_backscatter_mean": -12.5
  },
  "dados_detalhados": {
    "Estatísticas Mensais": [
      {
        "mes": "Janeiro",
        "ndvi": 0.78,
        "agua_km2": 4200,
        "alerts": 5
      },
      {
        "mes": "Fevereiro",
        "ndvi": 0.76,
        "agua_km2": 4100,
        "alerts": 3
      }
    ],
    "Parâmetros de Análise": {
      "resolucao_espacial_m": 10,
      "numero_imagens": 156,
      "cloud_coverage_max": 20
    }
  },
  "imagens": {
    "ndvi_timeseries.png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "water_extent_map.png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
    "sar_analysis.png": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
  }
}
```

### 2. Código Python para Enviar Dados (Google Colab)

```python
import requests
import json
import base64
from datetime import datetime

# URL do seu Replit (substitua pela URL real)
REPLIT_URL = "https://SEU-PROJETO.replit.app"  # Ou a URL do seu deployment
API_ENDPOINT = f"{REPLIT_URL}/api/update-data"

def encode_image_to_base64(image_path):
    """Converte uma imagem PNG para base64"""
    with open(image_path, 'rb') as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/png;base64,{encoded_string}"

def send_data_to_dashboard(metricas, dados_detalhados, imagens_paths, region="Pantanal", period="2024"):
    """
    Envia dados para o dashboard Replit
    
    Parameters:
    - metricas: dict com métricas principais (ex: {"ndvi_medio": 0.75, "area_km2": 15000})
    - dados_detalhados: dict com tabelas e dados complementares
    - imagens_paths: dict com caminhos das imagens (ex: {"ndvi_map.png": "/path/to/file.png"})
    - region: nome da região analisada
    - period: período da análise
    """
    
    # Codificar imagens para base64
    imagens_b64 = {}
    for filename, filepath in imagens_paths.items():
        try:
            imagens_b64[filename] = encode_image_to_base64(filepath)
            print(f"✓ Imagem codificada: {filename}")
        except Exception as e:
            print(f"✗ Erro ao codificar {filename}: {e}")
    
    # Montar payload
    payload = {
        "timestamp": datetime.now().isoformat(),
        "region": region,
        "analysis_period": period,
        "status": "updated",
        "metricas": metricas,
        "dados_detalhados": dados_detalhados,
        "imagens": imagens_b64
    }
    
    # Enviar para o dashboard
    try:
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("✓ Dados enviados com sucesso para o dashboard!")
            print(f"Resposta: {response.json()}")
            return True
        else:
            print(f"✗ Erro ao enviar dados: {response.status_code}")
            print(f"Detalhes: {response.text}")
            return False
            
    except Exception as e:
        print(f"✗ Erro na requisição: {e}")
        return False

# EXEMPLO DE USO
# ===============

# 1. Suas métricas calculadas
metricas = {
    "ndvi_medio": 0.75,
    "area_vegetacao_km2": 15000.5,
    "mudanca_vegetacao_percent": -2.3,
    "agua_extent_km2": 3500.2,
    "total_alerts": 42,
    "sar_backscatter_db": -12.5
}

# 2. Dados tabulares detalhados
dados_detalhados = {
    "Estatísticas Mensais": [
        {"mes": "Janeiro", "ndvi": 0.78, "agua_km2": 4200, "alerts": 5},
        {"mes": "Fevereiro", "ndvi": 0.76, "agua_km2": 4100, "alerts": 3},
        # ... mais meses
    ],
    "Parâmetros": {
        "resolucao_m": 10,
        "num_imagens": 156,
        "cloud_max": 20
    }
}

# 3. Caminhos das suas imagens geradas
imagens = {
    "ndvi_timeseries.png": "/content/ndvi_plot.png",
    "water_map.png": "/content/water_extent.png",
    "sar_analysis.png": "/content/sar_backscatter.png"
}

# 4. Enviar tudo
send_data_to_dashboard(
    metricas=metricas,
    dados_detalhados=dados_detalhados,
    imagens_paths=imagens,
    region="Pantanal",
    period="Janeiro-Setembro 2024"
)
```

### 3. Endpoints Disponíveis

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/update-data` | POST | Recebe dados do Colab e atualiza dashboard |
| `/api/get-data` | GET | Retorna dados atuais armazenados |
| `/api/health` | GET | Verificação de saúde da API |
| `/uploaded_data/{filename}` | GET | Serve imagens estáticas |

### 4. Verificar Status da API

```python
# Verificar se a API está online
response = requests.get(f"{REPLIT_URL}/api/health")
print(response.json())
# Saída esperada: {"status": "healthy", "last_update": "...", "data_available": false}
```

### 5. Obter URL do seu Replit

A URL do seu projeto Replit pode ser encontrada:
- Durante desenvolvimento: `https://SEU-PROJETO-SEU-USERNAME.replit.dev`
- Após publicação: `https://SEU-PROJETO.replit.app` (ou domínio customizado)

**⚠️ IMPORTANTE**: Em desenvolvimento local do Replit, você pode usar a porta 8080 diretamente:
```python
REPLIT_URL = "https://SEU-PROJETO-SEU-USERNAME.replit.dev"
```

## 📊 Visualização no Dashboard

Após enviar os dados:

1. Acesse o dashboard Replit
2. Navegue até **"🛰️ Google Earth Engine Data"** no menu lateral
3. Você verá:
   - ✅ Métricas principais em cards coloridos
   - 📊 Gráficos e mapas gerados no Colab
   - 📋 Tabelas com dados detalhados
   - 🕒 Timestamp da última atualização

## 🔧 Troubleshooting

### Erro: "Connection refused"
- Verifique se o dashboard Replit está rodando
- Confirme a URL correta do projeto

### Erro: 413 "Payload Too Large"
- As imagens em base64 estão muito grandes
- Reduza a resolução das imagens antes de enviar
- Use compressão PNG

### Imagens não aparecem
- Verifique se as imagens foram codificadas corretamente em base64
- Confirme que os nomes dos arquivos incluem a extensão `.png`

### Dados não atualizam
- Verifique o console do Colab para erros na requisição
- Use `/api/get-data` para confirmar que os dados foram recebidos

## 📝 Exemplo Completo de Workflow

```python
# No Google Colab, após suas análises GEE:

# 1. Calcular métricas
ndvi_mean = image_collection.mean().reduceRegion(...).get('NDVI')
area_vegetacao = calcular_area_vegetacao()

# 2. Gerar gráficos
fig = criar_grafico_ndvi_temporal()
fig.savefig('ndvi_temporal.png', dpi=150, bbox_inches='tight')

fig2 = criar_mapa_water_extent()
fig2.savefig('water_map.png', dpi=150, bbox_inches='tight')

# 3. Organizar dados
metricas = {
    "ndvi_medio": float(ndvi_mean),
    "area_vegetacao_km2": float(area_vegetacao),
    # ... mais métricas
}

imagens = {
    "ndvi_temporal.png": "ndvi_temporal.png",
    "water_extent.png": "water_map.png"
}

# 4. Enviar para dashboard
send_data_to_dashboard(metricas, dados_detalhados, imagens, "Amazon", "2024")

# 5. Verificar no dashboard Replit!
```

## 🌟 Dicas

- **Frequência de Atualização**: Você pode enviar dados sempre que quiser. Os dados mais recentes sobrescrevem os anteriores.
- **Múltiplas Regiões**: Envie dados de diferentes biomas separadamente. O campo `region` identifica qual foi analisado.
- **Formato das Imagens**: Use PNG para melhor qualidade. JPEG também funciona se você ajustar o MIME type.
- **Validação**: Sempre verifique a resposta da API para confirmar que os dados foram recebidos.

---

**Pronto!** Agora você pode executar análises no Google Earth Engine via Colab e visualizar os resultados automaticamente no seu dashboard SAR Biome Monitoring! 🛰️🌎
