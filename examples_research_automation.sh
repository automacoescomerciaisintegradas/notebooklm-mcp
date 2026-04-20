#!/bin/bash
#
# research_automation.sh — Pesquisa + Podcast Semanal
#
# Automatiza:
# 1. Pesquisa web com IA sobre um tópico
# 2. Criação de notebook com os resultados
# 3. Geração de áudio podcast
# 4. Compartilhamento público
#
# Uso: ./research_automation.sh "Topic" [profile]
#
# Exemplos:
#   ./research_automation.sh "AI Trends"
#   ./research_automation.sh "Enterprise Cloud" work
#

set -e

TOPIC="${1:-AI Research}"
PROFILE="${2:-default}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
NOTEBOOK_NAME="$TOPIC - $TIMESTAMP"

YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🔬 Research + Podcast Automation${NC}"
echo -e "Topic: ${YELLOW}$TOPIC${NC}"
echo -e "Profile: ${YELLOW}$PROFILE${NC}"
echo ""

# 1. Criar notebook
echo -e "${BLUE}📚 Step 1: Criando notebook...${NC}"
NOTEBOOK_JSON=$(nlm notebook create "$NOTEBOOK_NAME" --profile "$PROFILE" --json)
NOTEBOOK_ID=$(echo "$NOTEBOOK_JSON" | jq -r '.id')
echo -e "${GREEN}✅ Notebook criado: $NOTEBOOK_ID${NC}"
echo ""

# 2. Pesquisar
echo -e "${BLUE}🔍 Step 2: Pesquisando por '$TOPIC'...${NC}"
RESEARCH_JSON=$(nlm research start "latest $TOPIC deep dive comprehensive" --profile "$PROFILE" --json)
SOURCE_COUNT=$(echo "$RESEARCH_JSON" | jq '.sources | length')
echo -e "${GREEN}✅ Encontradas $SOURCE_COUNT fontes${NC}"
echo ""

# 3. Adicionar fontes
echo -e "${BLUE}📎 Step 3: Adicionando fontes ao notebook...${NC}"
ADDED=0
FAILED=0
echo "$RESEARCH_JSON" | jq -r '.sources[].url' | while read URL; do
    if [ -n "$URL" ]; then
        if nlm source add "$NOTEBOOK_ID" --url "$URL" --profile "$PROFILE" 2>/dev/null; then
            ((ADDED++))
            echo -e "${GREEN}✓${NC} $URL"
        else
            ((FAILED++))
            echo -e "${RED}✗${NC} $URL (erro)"
        fi
    fi
done
echo -e "${GREEN}✅ Adicionadas fontes (alguns podem ter falhado)${NC}"
echo ""

# 4. Gerar áudio
echo -e "${BLUE}🎙️  Step 4: Gerando áudio podcast (deep-dive)...${NC}"
AUDIO_JSON=$(nlm audio create "$NOTEBOOK_ID" --format deep-dive --confirm --profile "$PROFILE" --json)
ARTIFACT_ID=$(echo "$AUDIO_JSON" | jq -r '.id // empty')

if [ -n "$ARTIFACT_ID" ]; then
    echo -e "${GREEN}✅ Áudio em processamento: $ARTIFACT_ID${NC}"
    echo ""
    
    # 5. Baixar arquivo
    echo -e "${BLUE}⬇️  Step 5: Aguardando conclusão e baixando...${NC}"
    OUTPUT_DIR="./podcasts"
    mkdir -p "$OUTPUT_DIR"
    
    OUTPUT_FILE="$OUTPUT_DIR/${TOPIC// /_}_${TIMESTAMP}.mp3"
    nlm download audio "$NOTEBOOK_ID" "$ARTIFACT_ID" --output "$OUTPUT_FILE" --profile "$PROFILE"
    
    echo -e "${GREEN}✅ Áudio baixado: $OUTPUT_FILE${NC}"
else
    echo -e "${YELLOW}⏳ Áudio em processamento (em background)${NC}"
fi
echo ""

# 6. Compartilhar
echo -e "${BLUE}🔗 Step 6: Compartilhando (link público)...${NC}"
SHARE_JSON=$(nlm share public "$NOTEBOOK_ID" --profile "$PROFILE" --json)
SHARE_URL=$(echo "$SHARE_JSON" | jq -r '.url // empty')

if [ -n "$SHARE_URL" ]; then
    echo -e "${GREEN}✅ Link público: $SHARE_URL${NC}"
else
    echo -e "${YELLOW}⚠️  Compartilhamento pode estar processando${NC}"
fi
echo ""

# 7. Resumo
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ CONCLUÍDO!${NC}"
echo -e "${GREEN}════════════════════════════════════════${NC}"
echo ""
echo "Detalhes:"
echo "  Nome: $NOTEBOOK_NAME"
echo "  ID: $NOTEBOOK_ID"
echo "  Tópico: $TOPIC"
echo "  Fontes adicionadas: $SOURCE_COUNT"
if [ -n "$ARTIFACT_ID" ]; then
    echo "  Áudio: $ARTIFACT_ID"
    echo "  Local: $OUTPUT_FILE"
fi
if [ -n "$SHARE_URL" ]; then
    echo "  Link: $SHARE_URL"
fi
echo ""
echo "Próximos passos:"
echo "  - Compartilhe o link"
echo "  - Faça perguntas via: nlm notebook query '$NOTEBOOK_ID' 'sua pergunta'"
echo "  - Monitore em: https://notebooklm.google.com"
echo ""
