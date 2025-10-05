from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, FileResponse, RedirectResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import base64
import json
import re
from datetime import datetime
from pathlib import Path

app = FastAPI(title="SAR Biome Monitoring API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_FOLDER = 'uploaded_data'
DATA_FILE = 'uploaded_data/dashboard_data.json'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

dashboard_data = {
    "last_update": None,
    "region": "N/A",
    "analysis_period": "N/A",
    "metricas": {},
    "dados_detalhados": {},
    "imagens": {},
    "status": "waiting_for_data"
}

def load_data():
    """Carrega dados salvos do arquivo JSON"""
    global dashboard_data
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                dashboard_data = json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados: {e}")

def save_data():
    """Salva dados no arquivo JSON"""
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(dashboard_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Erro ao salvar dados: {e}")

def sanitize_filename(filename):
    """
    Sanitiza nome de arquivo para prevenir directory traversal e outros ataques.
    
    Args:
        filename: Nome do arquivo fornecido pelo usuário
        
    Returns:
        Nome de arquivo sanitizado (apenas basename) ou None se inválido
    """
    ALLOWED_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg'}
    
    safe_name = Path(filename).name
    
    if not safe_name or safe_name.startswith('.'):
        return None
    
    if '/' in safe_name or '\\' in safe_name or '..' in safe_name:
        return None
    
    safe_name = re.sub(r'[^a-zA-Z0-9._-]', '_', safe_name)
    
    file_ext = Path(safe_name).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return None
    
    return safe_name

load_data()

@app.post('/api/update-data')
async def update_data(request: Request):
    """Endpoint para receber dados do Google Colab"""
    global dashboard_data
    
    try:
        data = await request.json()
        
        dashboard_data.update({
            "last_update": data.get("timestamp", datetime.now().isoformat()),
            "region": data.get("region", "N/A"),
            "analysis_period": data.get("analysis_period", "N/A"),
            "metricas": data.get("metricas", {}),
            "dados_detalhados": data.get("dados_detalhados", {}),
            "imagens": {},
            "status": data.get("status", "updated")
        })
        
        if 'imagens' in data:
            for filename, b64_string in data['imagens'].items():
                if b64_string:
                    safe_filename = sanitize_filename(filename)
                    
                    if not safe_filename:
                        print(f"Nome de arquivo inválido ou inseguro rejeitado: {filename}")
                        continue
                    
                    if ";base64," in b64_string:
                        b64_string = b64_string.split(";base64,")[1]
                    
                    try:
                        image_bytes = base64.b64decode(b64_string)
                        image_path = os.path.join(UPLOAD_FOLDER, safe_filename)
                        with open(image_path, 'wb') as f:
                            f.write(image_bytes)
                        dashboard_data['imagens'][safe_filename] = f"/{UPLOAD_FOLDER}/{safe_filename}"
                        print(f"Imagem salva: {safe_filename}")
                    except Exception as e:
                        print(f"Erro ao decodificar/salvar imagem {safe_filename}: {e}")
        
        save_data()
        print(f"Dashboard atualizado em: {dashboard_data['last_update']}")
        
        return JSONResponse({
            "message": "Dados recebidos e dashboard atualizado com sucesso!",
            "status": "success",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Erro ao processar dados: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/api/get-data')
async def get_data():
    """Endpoint para obter os dados atuais do dashboard"""
    load_data()
    return JSONResponse(dashboard_data)

@app.get(f'/{UPLOAD_FOLDER}/{{filename}}')
async def get_image(filename: str):
    """Endpoint para servir arquivos de imagem estáticos"""
    safe_filename = sanitize_filename(filename)
    
    if not safe_filename:
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")
    
    file_path = os.path.join(UPLOAD_FOLDER, safe_filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Imagem não encontrada")
    
    real_path = os.path.realpath(file_path)
    upload_folder_real = os.path.realpath(UPLOAD_FOLDER)
    
    if not real_path.startswith(upload_folder_real):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    return FileResponse(file_path)

@app.get('/api/health')
async def health_check():
    """Endpoint de verificação de saúde"""
    load_data()
    return JSONResponse({
        "status": "healthy",
        "last_update": dashboard_data.get("last_update"),
        "data_available": dashboard_data["status"] != "waiting_for_data"
    })

@app.get('/')
async def root():
    """Redireciona automaticamente para o dashboard Streamlit"""
    html_content = """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>SAR Biome Monitoring Dashboard</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                background: linear-gradient(135deg, #0B1120 0%, #1a2332 100%);
                color: #E8EAED;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                min-height: 100vh;
            }
            .container {
                text-align: center;
                padding: 2rem;
                max-width: 800px;
            }
            h1 {
                font-size: 3rem;
                margin-bottom: 1rem;
                background: linear-gradient(135deg, #00D4FF 0%, #7B2FFF 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }
            .subtitle {
                font-size: 1.2rem;
                color: #B0B8C4;
                margin-bottom: 3rem;
            }
            .card {
                background: rgba(26, 35, 50, 0.6);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(0, 212, 255, 0.2);
                border-radius: 16px;
                padding: 2rem;
                margin: 1rem 0;
            }
            .btn {
                display: inline-block;
                background: linear-gradient(135deg, #00D4FF, #7B2FFF);
                color: white;
                text-decoration: none;
                padding: 1rem 3rem;
                border-radius: 8px;
                font-weight: 600;
                font-size: 1.1rem;
                margin: 1rem;
                transition: all 0.3s ease;
            }
            .btn:hover {
                transform: translateY(-3px);
                box-shadow: 0 12px 48px rgba(0, 212, 255, 0.4);
            }
            .icon {
                font-size: 4rem;
                margin-bottom: 1rem;
            }
            .endpoint {
                text-align: left;
                margin: 0.5rem 0;
                padding: 0.5rem;
                background: rgba(0, 0, 0, 0.2);
                border-radius: 4px;
            }
            code {
                background: rgba(0, 212, 255, 0.1);
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                color: #00D4FF;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="icon">🛰️</div>
            <h1>SAR Biome Monitoring Dashboard</h1>
            <p class="subtitle">Monitoramento de Biomas Brasileiros usando Dados SAR</p>
            
            <p style="color: #B0FFD9; background: rgba(0, 255, 136, 0.2); padding: 1.5rem; border-radius: 8px; border-left: 4px solid #00FF88; font-size: 1.1rem;">
                ✅ Redirecionando para o Dashboard Streamlit...<br>
                <strong>Se não redirecionar automaticamente, clique no botão abaixo:</strong>
            </p>
            
            <a href="https://workspace.breno5.repl.co:5000" class="btn" style="margin-top: 1rem;">🚀 Ir para o Dashboard</a>
            
            <div class="card" style="margin-top: 3rem;">
                <h2 style="color: #00D4FF; margin-bottom: 1rem;">📡 API Endpoints Disponíveis</h2>
                <div class="endpoint"><code>POST /api/update-data</code> - Recebe dados do Google Colab</div>
                <div class="endpoint"><code>GET /api/get-data</code> - Retorna dados atuais do dashboard</div>
                <div class="endpoint"><code>GET /api/health</code> - Verificação de saúde</div>
                <div class="endpoint"><code>GET /uploaded_data/{filename}</code> - Serve imagens estáticas</div>
            </div>
            
            <div class="card">
                <h3 style="color: #00FF88;">🚀 Para Desenvolvedores</h3>
                <p>Envie seus dados de análise SAR do Google Colab para:</p>
                <code>POST https://148.230.79.127:8090/api/update-data</code>
            </div>
        </div>
        
        <script>
            // Redirecionar automaticamente para o dashboard
            setTimeout(() => {
                window.location.href = 'https://workspace.breno5.repl.co:5000';
            }, 2000);
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
