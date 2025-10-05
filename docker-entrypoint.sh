#!/bin/bash
set -e

echo "🚀 Iniciando SAR Biome Monitoring Dashboard..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Verificar se o diretório de dados existe
if [ ! -d "uploaded_data" ]; then
    echo "📁 Criando diretório de dados..."
    mkdir -p uploaded_data
fi

# Iniciar API FastAPI em background
echo "📡 Iniciando API FastAPI na porta 8080..."
uvicorn api_server:app \
    --host 0.0.0.0 \
    --port 8080 \
    --log-level info &

API_PID=$!
echo "✅ API iniciada (PID: $API_PID)"

# Aguardar API iniciar
sleep 3

# Verificar se a API está rodando
if ! curl -s http://localhost:8080/api/health > /dev/null; then
    echo "❌ Erro: API não iniciou corretamente"
    exit 1
fi

echo "✅ API respondendo corretamente"

# Iniciar Streamlit
echo "🎨 Iniciando Dashboard Streamlit na porta 8501..."
streamlit run app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false \
    --browser.gatherUsageStats=false &

STREAMLIT_PID=$!
echo "✅ Streamlit iniciado (PID: $STREAMLIT_PID)"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Todos os serviços iniciados com sucesso!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📡 API FastAPI:      http://0.0.0.0:8080"
echo "🎨 Dashboard:        http://0.0.0.0:8501"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Função para cleanup ao sair
cleanup() {
    echo ""
    echo "🛑 Parando serviços..."
    kill $API_PID $STREAMLIT_PID 2>/dev/null || true
    echo "✅ Serviços parados"
    exit 0
}

# Capturar sinais de término
trap cleanup SIGTERM SIGINT

# Manter o container rodando
wait $API_PID $STREAMLIT_PID
