#!/bin/bash
#
# setup_antigravity.sh — Setup automático do NotebookLM MCP para Antigravity
#
# Uso: ./setup_antigravity.sh [profile]
#
# Exemplos:
#   ./setup_antigravity.sh              # perfil 'default'
#   ./setup_antigravity.sh work         # perfil 'work'
#   ./setup_antigravity.sh personal     # perfil 'personal'
#

set -e

PROFILE="${1:-default}"
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Setup NotebookLM MCP para Antigravity${NC}"
echo ""

# 1. Verificar se uv está instalado
echo "📦 Verificando ferramentas..."
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv não encontrado. Instale em: https://docs.astral.sh/uv/getting-started/installation/${NC}"
    exit 1
fi

# 2. Instalar ou atualizar pacote
echo -e "${YELLOW}📥 Instalando notebooklm-mcp-cli...${NC}"
uv tool install notebooklm-mcp-cli --upgrade

# 3. Verificar versão
echo ""
echo "🔍 Versão instalada:"
uv tool list | grep notebooklm || echo "Error getting version"

# 4. Autenticar
echo ""
echo -e "${YELLOW}🔐 Autenticação NotebookLM (perfil: $PROFILE)${NC}"
echo "Seu navegador será aberto. Faça login com sua conta Google."
echo ""
nlm login --profile "$PROFILE" || {
    echo -e "${RED}❌ Erro na autenticação${NC}"
    exit 1
}

# 5. Verificar autenticação
echo ""
echo -e "${YELLOW}✅ Verificando autenticação...${NC}"
nlm login --check --profile "$PROFILE"

# 6. Configurar MCP para Antigravity
echo ""
echo -e "${YELLOW}⚙️  Configurando MCP para Antigravity...${NC}"
nlm setup add antigravity || {
    echo -e "${RED}⚠️  Aviso: Setup automático pode não ter funcionado${NC}"
    echo "Execute manualmente: nlm setup add antigravity"
}

# 7. Diagnosticar
echo ""
echo -e "${YELLOW}🏥 Diagnóstico...${NC}"
nlm doctor

# 8. Sucesso!
echo ""
echo -e "${GREEN}✅ Setup concluído!${NC}"
echo ""
echo "Próximos passos:"
echo "1. Reinicie Antigravity"
echo "2. Use @notebooklm nos seus prompts"
echo "3. Veja exemplos em: ./examples/"
echo ""
echo "Comandos úteis:"
echo "  nlm notebook list              # Listar notebooks"
echo "  nlm notebook create 'Projeto'  # Criar notebook"
echo "  nlm setup list                 # Ver configurações"
echo "  nlm login profile list         # Ver perfis"
echo ""
