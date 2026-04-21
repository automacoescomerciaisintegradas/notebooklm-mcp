# Security Guard — Protocolo de Defesa Preditiva

O **SecurityGuard** é o sentinela de segurança do sistema, projetado para validar cada comando, variável de ambiente ou caminho de arquivo contra uma lista negra de padrões de expressões regulares (Regex) antes da execução. Isso impede operações perigosas, sejam elas acidentais ou maliciosas.

## Como Personalizar Padrões

Você pode estender as proteções do SecurityGuard adicionando seus próprios padrões ao arquivo de configuração global.

### ⚙️ Configuração via `config/security.json`

Para adicionar novos filtros, edite o arquivo `config/security.json` no diretório raiz do projeto. Adicione seus padrões dentro da lista `customPatterns`:

```json
{
  "dangerousCommandBlocking": {
    "enabled": true,
    "customPatterns": [
      {
        "pattern": "^my-dangerous-script",
        "description": "Bloqueia scripts específicos por nome",
        "severity": "HIGH"
      },
      {
        "pattern": "DROP TABLE",
        "description": "Proteção contra SQL Injection acidental",
        "severity": "CRITICAL"
      },
      "DELETE FROM"  // Você também pode passar apenas a string do padrão
    ],
    "allowedPatterns": [
      "^safe-command-prefix" // Padrões que não devem ser bloqueados nunca
    ]
  }
}
```

### 🛡️ Padrões Bloqueados por Padrão

O sistema já vem blindado contra:
- **Destruição de Filesystem**: `rm -rf /`, `format`, `mkfs`, etc.
- **Banco de Dados**: `DROP TABLE`, `DELETE FROM` (sem WHERE), `TRUNCATE`.
- **Git Destrutivo**: `push --force`, `reset --hard`.
- **RCE (Remote Code Execution)**: Pipes de `curl` ou `wget` para shell.
- **Escalação de Privilégios**: Modificações em `/etc/passwd`, `chmod 777` na raiz.

## Melhores Práticas de Publicação

Se o seu fluxo de trabalho envolver a publicação de pacotes (especialmente via npm):

- **Verificação de Pacotes**: Sempre rode `npm pack --dry-run` antes de cada release para validar quais arquivos serão incluídos.
- **Source Maps**: Lembre-se que source maps expõem seu código-fonte original. Eles **nunca** devem ser enviados para ambientes de produção ou incluídos em pacotes públicos, a menos que seja intencional.

---

# Security Policy

## Supported Versions

Use this section to tell people about which versions of your project are
currently being supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 5.1.x   | :white_check_mark: |
| 5.0.x   | :x:                |
| 4.0.x   | :white_check_mark: |
| < 4.0   | :x:                |

## Reporting a Vulnerability

Use this section to tell people how to report a vulnerability.

Tell them where to go, how often they can expect to get an update on a
reported vulnerability, what to expect if the vulnerability is accepted or
declined, etc.
