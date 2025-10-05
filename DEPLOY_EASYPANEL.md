# 🚀 Guia de Deploy no Easypanel

## 📋 Pré-requisitos

- Conta no [Easypanel](https://easypanel.io)
- Servidor configurado no Easypanel
- Repositório Git (GitHub, GitLab, etc.) ou deploy via Docker

---

## 🎯 Métodos de Deploy

### **Método 1: Deploy via GitHub (Recomendado)**

#### **Passo 1: Preparar Repositório**

1. Crie um repositório no GitHub
2. Faça upload de todos os arquivos deste projeto
3. Certifique-se de que o `Dockerfile` está na raiz

#### **Passo 2: Configurar no Easypanel**

1. Acesse seu painel do Easypanel
2. Clique em **"Create Service"** → **"App"**
3. Escolha **"From GitHub"**
4. Selecione seu repositório
5. Configure:
   - **Name:** `sar-biome-dashboard`
   - **Branch:** `main` (ou sua branch principal)
   - **Build Method:** `Dockerfile`
   - **Dockerfile Path:** `./Dockerfile`

#### **Passo 3: Configurar Portas**

Adicione as portas:

| Nome | Porta Interna | Porta Externa | Público |
|------|---------------|---------------|---------|
| API | 8080 | 80 | ✅ Sim |
| Dashboard | 8501 | 3000 | ✅ Sim |

#### **Passo 4: Configurar Domínios**

1. Vá em **"Domains"**
2. Adicione seus domínios:
   - `seu-dominio.com` → porta 8501 (Dashboard)
   - `api.seu-dominio.com` → porta 8080 (API)

#### **Passo 5: Deploy**

1. Clique em **"Deploy"**
2. Aguarde o build (3-5 minutos)
3. Acesse seu domínio!

---

### **Método 2: Deploy via Docker Registry**

#### **Passo 1: Build Local**

```bash
# Build da imagem
docker build -t sar-biome-dashboard:latest .

# Tag para seu registry
docker tag sar-biome-dashboard:latest your-registry.com/sar-biome-dashboard:latest

# Push para registry
docker push your-registry.com/sar-biome-dashboard:latest
```

#### **Passo 2: Deploy no Easypanel**

1. Acesse Easypanel
2. **"Create Service"** → **"App"**
3. Escolha **"From Docker Image"**
4. Insira: `your-registry.com/sar-biome-dashboard:latest`
5. Configure portas e domínios (igual ao Método 1)

---

### **Método 3: Deploy Manual (Upload de Arquivos)**

#### **Passo 1: Compactar Projeto**

```bash
zip -r sar-dashboard.zip . -x "*.git*" "attached_assets/*" "__pycache__/*"
```

#### **Passo 2: Upload no Easypanel**

1. Acesse Easypanel
2. **"Create Service"** → **"App"**
3. Escolha **"From Archive"**
4. Faça upload do `sar-dashboard.zip`
5. Configure portas e domínios

---

## ⚙️ Configurações Avançadas

### **Variáveis de Ambiente**

No Easypanel, adicione estas variáveis em **"Environment Variables"**:

```
PYTHONUNBUFFERED=1
TZ=America/Sao_Paulo
LOG_LEVEL=INFO
```

### **Volumes Persistentes**

Para manter os dados entre deploys:

1. Vá em **"Volumes"**
2. Adicione volume:
   - **Name:** `data`
   - **Mount Path:** `/app/uploaded_data`
   - **Size:** 5GB

### **Health Checks**

Configure em **"Health Check"**:

```
Path: /api/health
Port: 8080
Initial Delay: 40s
Period: 30s
Timeout: 10s
```

### **Recursos**

Configure em **"Resources"**:

```
CPU Request: 0.5 cores
CPU Limit: 1 core
Memory Request: 512MB
Memory Limit: 2GB
```

---

## 🧪 Testar Localmente Antes do Deploy

### **Usando Docker Compose:**

```bash
# Build e iniciar
docker-compose up --build

# Acessar:
# Dashboard: http://localhost:8501
# API: http://localhost:8080/api/health
```

### **Usando Docker:**

```bash
# Build
docker build -t sar-dashboard .

# Run
docker run -d \
  -p 8080:8080 \
  -p 8501:8501 \
  --name sar-dashboard \
  sar-dashboard

# Ver logs
docker logs -f sar-dashboard

# Parar
docker stop sar-dashboard
docker rm sar-dashboard
```

---

## 🔍 Verificar Deploy

Após o deploy, teste:

### **1. Health Check da API:**
```bash
curl https://api.seu-dominio.com/api/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "last_update": null,
  "data_available": false
}
```

### **2. Dashboard:**
Acesse: `https://seu-dominio.com`

Deve carregar o dashboard Streamlit.

### **3. Envio de Dados do Colab:**

No Google Colab, atualize a URL:

```python
REPLIT_URL = "https://api.seu-dominio.com"
```

Execute a célula de integração.

---

## 🐛 Troubleshooting

### **Problema: Build falha**

**Erro:** `ERROR: failed to solve: process "/bin/sh -c pip install..."`

**Solução:**
1. Verifique se o `requirements.txt` está correto
2. Tente remover versões específicas (ex: `>=1.50.0` → sem versão)

### **Problema: Container não inicia**

**Erro:** `Container exited with code 1`

**Solução:**
1. Veja os logs no Easypanel
2. Verifique se as portas 8080 e 8501 estão disponíveis
3. Verifique se o `docker-entrypoint.sh` tem permissão de execução

### **Problema: API não responde**

**Erro:** `Connection refused` ou timeout

**Solução:**
1. Verifique se a porta 8080 está exposta
2. Verifique health check: `curl http://localhost:8080/api/health`
3. Veja logs: procure por erros do uvicorn

### **Problema: Streamlit não carrega**

**Erro:** Página em branco ou erro 502

**Solução:**
1. Verifique se a porta 8501 está exposta
2. Aguarde 30-60 segundos (Streamlit demora para iniciar)
3. Verifique logs do container

### **Problema: Dados não persistem**

**Erro:** Dados são perdidos após redeploy

**Solução:**
1. Configure volume persistente (veja seção "Volumes Persistentes")
2. Monte em `/app/uploaded_data`

---

## 📊 Monitoramento

### **Logs em Tempo Real:**

No Easypanel:
1. Vá em seu serviço
2. Clique em **"Logs"**
3. Veja logs em tempo real

### **Métricas:**

Monitore:
- **CPU Usage:** Deve ficar < 70%
- **Memory Usage:** Deve ficar < 1.5GB
- **Response Time:** API deve responder em < 500ms

---

## 🔄 Atualizar Deploy

### **Via GitHub:**

1. Faça commit das mudanças
2. Push para o repositório
3. No Easypanel, clique em **"Redeploy"**
4. Aguarde o novo build

### **Via Docker:**

1. Build nova imagem com nova tag
2. Push para registry
3. No Easypanel, atualize a imagem
4. Clique em **"Redeploy"**

---

## 🔐 Segurança

### **Recomendações:**

1. ✅ Use HTTPS (Easypanel fornece SSL grátis via Let's Encrypt)
2. ✅ Configure firewall para permitir apenas portas necessárias
3. ✅ Adicione autenticação se necessário (não incluído neste projeto)
4. ✅ Mantenha dependências atualizadas
5. ✅ Faça backup regular dos dados

### **Adicionar Autenticação Básica (Opcional):**

Edite `app.py` e adicione no início:

```python
import streamlit_authenticator as stauth

# Configurar autenticação
authenticator = stauth.Authenticate(
    {'usernames': {'admin': {'name': 'Admin', 'password': 'hashed_password'}}},
    'cookie_name',
    'signature_key',
    30
)

name, authentication_status, username = authenticator.login('Login', 'main')

if not authentication_status:
    st.stop()
```

---

## 📞 Suporte

- **Easypanel Docs:** https://easypanel.io/docs
- **Docker Docs:** https://docs.docker.com
- **Streamlit Docs:** https://docs.streamlit.io

---

## ✅ Checklist de Deploy

Antes de fazer deploy, confirme:

- [ ] Todos os arquivos estão no repositório
- [ ] `Dockerfile` está na raiz
- [ ] `requirements.txt` está completo
- [ ] `docker-entrypoint.sh` tem permissão de execução
- [ ] Portas 8080 e 8501 estão configuradas
- [ ] Domínios estão apontando para o servidor
- [ ] Health check está configurado
- [ ] Volume persistente está configurado (se necessário)
- [ ] Variáveis de ambiente estão definidas
- [ ] Testou localmente com Docker

---

**Boa sorte com o deploy! 🚀**
