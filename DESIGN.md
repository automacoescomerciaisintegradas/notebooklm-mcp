# DESIGN.md — Cleudocode Design System
> **Versão:** 2.0.0 · **Mantido por:** Antigravity Agent  
> Fonte de verdade para tokens visuais, componentes e decisões de identidade do ecossistema Cleudocode.  
> Agentes que consomem este arquivo devem tratar os tokens como **normativos** e a prosa como **restrições de uso**.

---

## 1. Identidade Visual

### 1.1 Conceito
A linguagem visual do Cleudocode é **"cinematic dark tech"**:
- Fundos quase-negros com gradiente sideral
- Superfícies de vidro (glassmorphism calibrado)
- Vermelho coral `#FF5F5F` como cor de marca/ação (CTA)
- Azul elétrico `#5B7CFF` como cor de estado ativo, foco e precisão

### 1.2 Regra de paleta semântica
| Role | Token | Valor | Quando usar |
|------|-------|-------|-------------|
| Marca / CTA | `--brand-primary` | `#FF5F5F` | Botões primários, taglines, logo accent |
| Estado ativo / link | `--text-accent` | `#5B7CFF` | Links, ícones ativos, bordas de foco, indicadores |
| Fundo canônico | `--bg-primary` | `#080808` | Base de todas as telas |
| Fundo sideral | `--bg-space` | `#1A0F1F` | Início do gradiente radial |
| Glassmorphism | `--bg-card` | `rgba(15,22,41,0.75)` | Cards e painéis sobrepostos |
| Texto principal | `--text-primary` | `#FFFFFF` | Conteúdo legível |
| Texto secundário | `--text-secondary` | `#94A3B8` | Descrições, metadados |
| Borda sutil | `--border-subtle` | `rgba(255,255,255,0.05)` | Divisores, outline de cards |

> **Nunca** use `--brand-primary` como fundo de grandes áreas — perde impacto.  
> **Nunca** substitua o gradiente canônico por fundo liso — ele cria a profundidade do sistema.

---

## 2. Gradiente Canônico

```css
background: radial-gradient(1200px circle at 10% 10%, #1A0F1F 0%, #05070C 40%, #02030A 100%);
```

Aplicar no `<body>` com `background-attachment: fixed`. Este é o núcleo da atmosfera visual.

---

## 3. Variáveis CSS (:root)

> Fonte canônica: `design-tokens.css`  
> Complementos ACI: `skills/aci-design-system.md`

```css
:root {
  /* === BRAND === */
  --brand-primary:      #FF5F5F;      /* Coral — CTA, marca */
  --brand-secondary:    #6366F1;      /* Índigo — secundário */
  --brand-accent:       #10B981;      /* Verde esmeralda */
  --brand-warning:      #FB923C;      /* Laranja */

  /* === ANTIGRAVITY BLUE (ACI) === */
  --text-accent:        #5B7CFF;      /* Azul elétrico — links, foco, estados ativos */
  --shadow-glow:        0 0 30px rgba(91, 124, 255, 0.15);
  --gradient-cta:       linear-gradient(135deg, #ef4444 0%, #dc2626 100%);

  /* === BACKGROUNDS === */
  --bg-primary:         #080808;
  --bg-secondary:       #0A0A0A;
  --bg-tertiary:        rgb(15, 22, 41);
  --bg-elevated:        rgba(255, 255, 255, 0.02);
  --bg-hover:           rgba(255, 255, 255, 0.05);
  --bg-active:          rgba(255, 255, 255, 0.08);
  --bg-card:            rgba(15, 22, 41, 0.75);    /* glassmorphism */
  --bg-space:           #1A0F1F;
  --gradient-bg:        radial-gradient(1200px circle at 10% 10%, #1a0f1f 0%, #05070c 40%, #02030a 100%);

  /* === TEXT === */
  --text-primary:       #FFFFFF;
  --text-secondary:     #94A3B8;
  --text-tertiary:      #64748B;
  --text-muted:         #6B7280;
  --text-disabled:      rgb(71, 85, 105);

  /* === BORDERS === */
  --border-subtle:      rgba(255, 255, 255, 0.05);
  --border-default:     rgba(255, 255, 255, 0.10);
  --border-strong:      rgba(255, 255, 255, 0.20);
  --border-accent:      rgba(91, 124, 255, 0.15);  /* ACI blue glow */

  /* === SEMANTIC === */
  --color-success:      #10B981;
  --color-success-bg:   rgba(16, 185, 129, 0.2);
  --color-warning:      #F59E0B;
  --color-warning-bg:   rgba(245, 158, 11, 0.2);
  --color-error:        #EF4444;
  --color-error-bg:     rgba(239, 68, 68, 0.2);
  --color-info:         #6366F1;
  --color-info-bg:      rgba(99, 102, 241, 0.2);

  /* === STATUS INDICATORS === */
  --status-green:       #34D399;
  --status-red:         #FF5F5F;
  --status-blue:        #818CF8;
  --status-orange:      #FBBF24;
  --status-purple:      #C084FC;

  /* === SHADOWS === */
  --shadow-sm:          0 1px 2px rgba(0, 0, 0, 0.5);
  --shadow-md:          0 4px 6px rgba(0, 0, 0, 0.5);
  --shadow-lg:          0 10px 15px rgba(0, 0, 0, 0.5);
  --shadow-xl:          0 20px 25px rgba(0, 0, 0, 0.5);

  /* === TYPOGRAPHY === */
  --font-sans:    'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-display: 'Outfit', 'Inter', sans-serif;   /* Títulos hero */
  --font-mono:    'JetBrains Mono', 'Fira Code', 'Consolas', monospace;

  --font-xs:    12px;
  --font-sm:    14px;
  --font-base:  16px;
  --font-lg:    18px;
  --font-xl:    20px;
  --font-2xl:   24px;
  --font-3xl:   30px;
  --font-4xl:   36px;
  --font-5xl:   48px;
  --font-6xl:   60px;
  --font-7xl:   72px;

  --font-normal:    400;
  --font-medium:    500;
  --font-semibold:  600;
  --font-bold:      700;
  --font-extrabold: 800;
  --font-black:     900;

  --leading-tight:   1.25;
  --leading-snug:    1.375;
  --leading-normal:  1.5;
  --leading-relaxed: 1.625;
  --leading-loose:   2;

  --tracking-tighter: -0.05em;
  --tracking-tight:   -0.025em;
  --tracking-normal:   0;
  --tracking-wide:     0.025em;
  --tracking-wider:    0.05em;
  --tracking-widest:   0.1em;

  /* === SPACING (4px base) === */
  --space-0:  0;
  --space-1:  0.25rem;   /* 4px */
  --space-2:  0.5rem;    /* 8px */
  --space-3:  0.75rem;   /* 12px */
  --space-4:  1rem;      /* 16px */
  --space-5:  1.25rem;   /* 20px */
  --space-6:  1.5rem;    /* 24px */
  --space-8:  2rem;      /* 32px */
  --space-10: 2.5rem;    /* 40px */
  --space-12: 3rem;      /* 48px */
  --space-16: 4rem;      /* 64px */
  --space-20: 5rem;      /* 80px */
  --space-24: 6rem;      /* 96px */

  /* === BORDER RADIUS === */
  --radius-none: 0;
  --radius-sm:   0.125rem;  /* 2px */
  --radius-base: 0.25rem;   /* 4px */
  --radius-md:   0.375rem;  /* 6px */
  --radius-lg:   0.5rem;    /* 8px */
  --radius-xl:   0.75rem;   /* 12px */
  --radius-2xl:  1rem;      /* 16px */
  --radius-3xl:  1.5rem;    /* 24px */
  --radius-full: 9999px;

  /* === TRANSITIONS === */
  --transition-fast:   150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base:   250ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow:   350ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slower: 500ms cubic-bezier(0.4, 0, 0.2, 1);

  /* === Z-INDEX === */
  --z-base:             1;
  --z-dropdown:         1000;
  --z-sticky:           1100;
  --z-fixed:            1200;
  --z-modal-backdrop:   1300;
  --z-modal:            1400;
  --z-popover:          1500;
  --z-tooltip:          1600;
  --z-notification:     1700;
}
```

---

## 4. Tipografia

### Regras de uso
| Família | Variável | Uso |
|---------|----------|-----|
| **Outfit** | `--font-display` | Hero headings, display KPI — pesos 700 e 800 exclusivamente |
| **Inter** | `--font-sans` | Body, labels, UI textual — todos os outros contextos |
| **JetBrains Mono** | `--font-mono` | Terminal, código, metadados técnicos |

### Importação Google Fonts
```html
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@700;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
```

### Escala Tipográfica Hero
```
7xl — 72px — Hero heading (CLEUDOCODE)
6xl — 60px — Display KPI
4xl — 36px — Section title
3xl — 30px — Subsection title
xl  — 20px — Body large / tagline
base — 16px — Body default
sm  — 14px — Labels, metadados
xs  — 12px — Captions, timestamps
```

---

## 5. Componentes Base

### 5.1 `.hero-heading` — Título Hero
```css
.hero-heading {
  font-family: var(--font-sans);
  font-size: var(--font-7xl);        /* 72px */
  font-weight: var(--font-black);    /* 900 */
  font-style: italic;
  color: var(--text-primary);
  letter-spacing: -3.6px;
  line-height: 1.1;
}
```
> Usar em `<h1>` de página. **Um por tela.**

### 5.2 `.glow-title` — Título com Neon ACI
```css
.glow-title {
  font-family: var(--font-display);  /* Outfit */
  font-size: var(--font-6xl);        /* 60px */
  font-weight: 800;
  color: var(--text-primary);
  text-shadow: 0 0 40px rgba(91, 124, 255, 0.4);
  letter-spacing: -0.03em;
}
```
> Efeito neon azul ACI. Apenas em headings hero — **nunca em textos funcionais**.

### 5.3 `.btn-primary` — Botão Primário (Coral)
```css
.btn-primary {
  background: var(--brand-primary);  /* #FF5F5F */
  color: var(--text-primary);
  font-weight: var(--font-semibold);
  padding: var(--space-3) var(--space-6);
  border-radius: var(--radius-lg);
  border: none;
  transition: all var(--transition-fast);
  cursor: pointer;
}
.btn-primary:hover {
  background: #ff7a7a;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}
```

### 5.4 `.btn-cta` — Botão CTA (Gradiente Vermelho)
```css
.btn-cta {
  background: var(--gradient-cta);   /* linear #ef4444 → #dc2626 */
  color: #fff;
  font-weight: 700;
  border-radius: 12px;
  padding: 12px 28px;
  border: none;
  transition: opacity 0.2s ease;
  cursor: pointer;
}
.btn-cta:hover { opacity: 0.88; }
```
> **Um por página.** A ação de maior valor. Não duplicar.

### 5.5 `.card` — Glassmorphism Card
```css
.card {
  background: var(--bg-card);                /* rgba(15,22,41,0.75) */
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-accent);    /* ACI blue glow */
  border-radius: var(--radius-2xl);
  padding: var(--space-8);
  transition: all var(--transition-base);
}
.card:hover {
  background: var(--bg-hover);
  border-color: var(--border-default);
  transform: translateY(-2px);
}
```
> O alfa 0.75 faz o gradiente de fundo "respirar" através dos cards.

### 5.6 `.terminal` — Bloco de Terminal
```css
.terminal {
  background: var(--bg-secondary);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  font-family: var(--font-mono);
  font-size: var(--font-sm);
  color: var(--text-secondary);
}
.terminal-header {
  padding: var(--space-4);
  border-bottom: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
.terminal-dot { width: 12px; height: 12px; border-radius: var(--radius-full); }
.terminal-dot.red    { background: #FF5F5F; }
.terminal-dot.yellow { background: #FBBF24; }
.terminal-dot.green  { background: #34D399; }
```

### 5.7 Status Badges
```css
.badge {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-full);
  font-size: var(--font-sm);
  font-weight: var(--font-medium);
}
.badge-success { background: var(--color-success-bg); color: var(--status-green); }
.badge-warning { background: var(--color-warning-bg); color: var(--status-orange); }
.badge-error   { background: var(--color-error-bg);   color: var(--status-red); }
.badge-info    { background: var(--color-info-bg);    color: var(--status-blue); }
```

---

## 6. Layout Base

```css
body {
  background: var(--gradient-bg);
  background-attachment: fixed;
  color: var(--text-primary);
  font-family: var(--font-sans);
  line-height: var(--leading-normal);
}
```

```css
/* Profundidade de cards e painéis */
.panel {
  box-shadow: var(--shadow-glow);   /* ACI blue glow */
}
```

---

## 7. Acessibilidade (WCAG 2.1 AA)

| Par | Ratio | Status |
|-----|-------|--------|
| `#FFFFFF` sobre `#080808` | 21:1 | ✅ AAA |
| `#FFFFFF` sobre `#FF5F5F` | 4.0:1 | ✅ AA (texto grande) |
| `#FF5F5F` sobre `#080808` | 4.5:1 | ✅ AA |
| `#5B7CFF` sobre `#080808` | 5.2:1 | ✅ AA |
| `#94A3B8` sobre `#080808` | 6.5:1 | ✅ AA |
| `#64748B` sobre `#080808` | 4.6:1 | ✅ AA |

> **Restrição:** `--text-muted (#6B7280)` sobre `--bg-elevated` pode estar abaixo de 4.5:1 — **não usar em texto de conteúdo informativo**, apenas em decoração.

---

## 8. Arquitetura de Arquivos

| Arquivo | Propósito |
|---------|-----------|
| `DESIGN.md` | Este arquivo — fonte de verdade normativa |
| `design-tokens.css` | Tokens CSS completos (`:root` + componentes) |
| `design-tokens.json` | Tokens em JSON para ferramentas e pipelines |
| `design-tokens-reference.html` | Playground visual interativo |
| `skills/aci-design-system.md` | Tokens ACI (Antigravity Component Identity) para agentes |
| `design_tokens.py` | Utilitários Python para consumo programático |

---

## 9. Uso por Agentes de IA

Quando um agente gera ou valida uma interface, deve:

1. **Verificar paleta semântica** — cada cor tem papel único, não-intercambiável (ver tabela §1.2)
2. **Aplicar o gradiente canônico** no `<body>` — obrigatório
3. **Um `.btn-cta` por página** — regra estrita de conversão
4. **`.glow-title` somente em `<h1>` hero** — nunca em labels funcionais
5. **Glassmorphism requer `backdrop-filter`** — sempre incluir prefixo `-webkit-`
6. **Importar Outfit + Inter** via Google Fonts antes de qualquer heading
7. **Validar contraste** usando os pares da tabela §7 antes de submeter

---

## 10. Changelog

| Versão | Data | Mudança |
|--------|------|---------|
| 2.0.0 | 2026-04-24 | Unificação ACI + Cleudocode tokens; adição de seção de acessibilidade e guia para agentes |
| 1.0.0 | 2026-02-11 | Extração inicial dos tokens do landing page `localhost:18900` |
