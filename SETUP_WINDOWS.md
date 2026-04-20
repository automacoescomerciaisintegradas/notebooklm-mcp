# 🚀 Setup — Qual Script Usar?

## Windows

### Opção 1: PowerShell (Recomendado)
```powershell
# Abra PowerShell e execute:
.\setup_antigravity.ps1

# Ou com perfil nomeado:
.\setup_antigravity.ps1 -Profile "work"
```

### Opção 2: Command Prompt (CMD)
```batch
REM Abra CMD (Prompt de Comando) e execute:
setup_antigravity.bat

REM Ou com perfil:
setup_antigravity.bat work
```

### Opção 3: Manual (Se os scripts não funcionarem)
```powershell
# PowerShell
uv tool install notebooklm-mcp-cli
nlm login
nlm setup add antigravity
nlm doctor
```

---

## macOS / Linux

```bash
# Terminal
chmod +x setup_antigravity.sh
./setup_antigravity.sh

# Ou com perfil
./setup_antigravity.sh work
```

---

## ✅ Verificar Se Funcionou

Após executar, verifique:

```bash
nlm doctor
# Deve mostrar: ✅ All systems operational

nlm notebook list
# Deve mostrar: lista de notebooks
```

---

## 🐛 Problemas?

### Erro de execução em PowerShell
```powershell
# Se receber erro de permissão, execute:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Comando nlm não encontrado
```powershell
# Reinstale:
uv tool install --force notebooklm-mcp-cli

# Verifique:
uv tool list | Select-String notebooklm
```

### Erro de autenticação
```bash
nlm login --force
```

---

## 📝 Próximos Passos

1. ✅ Execute o script apropriado
2. ✅ Faça login no navegador (automático)
3. ✅ Reinicie Antigravity
4. ✅ Use `@notebooklm` em prompts

---

**Dúvidas?** Consulte [GETTING_STARTED.md](GETTING_STARTED.md) ou execute `nlm doctor`
