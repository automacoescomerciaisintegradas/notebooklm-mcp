"""
SecurityGuard — Protocolo de Defesa Preditiva
Protecao de missao critica para operacoes do MCP Server Manager.

Valida comandos contra uma lista negra de padroes regex antes da execucao,
prevenindo operacoes destrutivas acidentais ou maliciosas.

(c) Automacoes Comerciais Integradas 2026
"""

import re
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger("SecurityGuard")

# === Padroes perigosos padrao ===
# Cada entrada: (regex_pattern, descricao, severidade)
DEFAULT_BLOCKED_PATTERNS: list[tuple[str, str, str]] = [
    # Destruicao de filesystem
    (r"rm\s+(-[a-zA-Z]*f[a-zA-Z]*\s+)?/", "Remocao recursiva na raiz", "CRITICAL"),
    (r"rm\s+-rf\s+", "rm -rf (remocao forcada recursiva)", "CRITICAL"),
    (r"rmdir\s+/s\s+/q", "rmdir /s /q (Windows - remocao silenciosa)", "CRITICAL"),
    (r"del\s+/[sfq]", "del com flags destrutivas (Windows)", "HIGH"),
    (r"format\s+[a-zA-Z]:", "Formatacao de disco (Windows)", "CRITICAL"),
    (r"mkfs\.", "Formatacao de filesystem (Linux)", "CRITICAL"),
    (r"dd\s+if=.+of=/dev/", "dd para dispositivo (sobrescrita direta)", "CRITICAL"),

    # Banco de dados
    (r"DROP\s+(TABLE|DATABASE|SCHEMA|INDEX)", "DROP de objetos SQL", "CRITICAL"),
    (r"DELETE\s+FROM\s+\w+\s*;?\s*$", "DELETE sem WHERE (apaga tudo)", "CRITICAL"),
    (r"TRUNCATE\s+TABLE", "TRUNCATE TABLE (limpeza total)", "HIGH"),
    (r"ALTER\s+TABLE\s+\w+\s+DROP", "ALTER TABLE DROP (remocao de coluna)", "MEDIUM"),

    # Git destrutivo
    (r"git\s+push\s+.*--force", "git push --force (sobrescrita de historico)", "HIGH"),
    (r"git\s+reset\s+--hard", "git reset --hard (perda de alteracoes)", "HIGH"),
    (r"git\s+clean\s+-[a-zA-Z]*f", "git clean -f (remocao de arquivos)", "MEDIUM"),

    # Rede / exfiltracao
    (r"curl\s+.*\|\s*(sh|bash|python)", "Pipe de URL para shell (RCE)", "CRITICAL"),
    (r"wget\s+.*\|\s*(sh|bash|python)", "Pipe de download para shell (RCE)", "CRITICAL"),
    (r"Invoke-Expression.*DownloadString", "PowerShell download + exec (RCE)", "CRITICAL"),
    (r"iex\s*\(.*Net\.WebClient", "PowerShell IEX WebClient (RCE)", "CRITICAL"),

    # Escalacao de privilegios / sistema
    (r"chmod\s+777\s+/", "chmod 777 na raiz", "HIGH"),
    (r"chown\s+-R\s+.+\s+/", "chown recursivo na raiz", "HIGH"),
    (r"passwd\s+root", "Alteracao de senha root", "HIGH"),
    (r"net\s+user\s+.*\s+/add", "Criacao de usuario (Windows)", "MEDIUM"),
    (r"reg\s+(add|delete)\s+HKLM", "Modificacao de registro HKLM", "HIGH"),

    # Processos / servicos
    (r"kill\s+-9\s+1\b", "kill -9 PID 1 (init)", "CRITICAL"),
    (r"taskkill\s+/f\s+/im\s+(csrss|lsass|winlogon)", "Kill de processo critico Windows", "CRITICAL"),
    (r"Stop-Service\s+.*-Force", "Parada forcada de servico Windows", "MEDIUM"),

    # Crypto / ransomware patterns
    (r"openssl\s+enc\s+-aes.*-in\s+/", "Criptografia de arquivos na raiz", "CRITICAL"),
    (r"gpg\s+--encrypt.*\*\.\*", "Criptografia em massa de arquivos", "CRITICAL"),

    # Env / credentials
    (r"echo\s+.*>>\s*~/?\.(bash_profile|bashrc|zshrc|profile)", "Injeccao em profile do shell", "HIGH"),
    (r"export\s+(AWS_SECRET|GITHUB_TOKEN|API_KEY)=", "Exposicao de credenciais em export", "HIGH"),
]

# Severidades e suas prioridades
SEVERITY_LEVELS = {
    "CRITICAL": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1,
    "INFO": 0,
}


class SecurityViolation:
    """Representa uma violacao de seguranca detectada."""

    def __init__(self, command: str, pattern: str, description: str, severity: str):
        self.command = command
        self.pattern = pattern
        self.description = description
        self.severity = severity
        self.timestamp = datetime.now().isoformat()
        self.blocked = True

    def to_dict(self) -> dict:
        return {
            "command": self.command[:200],  # Truncar para log seguro
            "pattern": self.pattern,
            "description": self.description,
            "severity": self.severity,
            "timestamp": self.timestamp,
            "blocked": self.blocked,
        }

    def __str__(self) -> str:
        return (
            f"[{self.severity}] {self.description}\n"
            f"  Comando: {self.command[:100]}...\n"
            f"  Padrao:  {self.pattern}"
        )


class SecurityGuard:
    """
    Sentinela de seguranca para operacoes do MCP Server Manager.

    Valida comandos contra padroes regex antes da execucao.
    Suporta padroes customizados via configuracao.

    Uso:
        guard = SecurityGuard()
        result = guard.validate_command("rm -rf /")
        if not result.is_safe:
            print(f"BLOQUEADO: {result.violation}")
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.blocked_patterns: list[tuple[re.Pattern, str, str]] = []
        self.violations_log: list[SecurityViolation] = []
        self.enabled = True
        self.log_path: Optional[Path] = None

        # Carregar padroes padrao
        self._load_default_patterns()

        # Carregar config customizada
        if config_path:
            self._load_custom_config(config_path)
        else:
            default_config = Path(__file__).parent.parent / "config" / "security.json"
            if default_config.exists():
                self._load_custom_config(default_config)

        # Configurar log de violacoes
        self.log_path = Path(__file__).parent.parent / "logs" / "security.log"
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def _load_default_patterns(self):
        """Carrega padroes perigosos padrao."""
        for pattern, desc, severity in DEFAULT_BLOCKED_PATTERNS:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
                self.blocked_patterns.append((compiled, desc, severity))
            except re.error as e:
                logger.warning(f"Padrao regex invalido ignorado: {pattern} -> {e}")

    def _load_custom_config(self, config_path: Path):
        """Carrega padroes customizados do arquivo de configuracao."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Habilitar/desabilitar
            security_config = config.get("dangerousCommandBlocking", config)
            self.enabled = security_config.get("enabled", True)

            # Padroes customizados
            custom_patterns = security_config.get("customPatterns", [])
            for entry in custom_patterns:
                if isinstance(entry, str):
                    pattern, desc, severity = entry, f"Padrao customizado: {entry}", "HIGH"
                elif isinstance(entry, dict):
                    pattern = entry.get("pattern", "")
                    desc = entry.get("description", f"Padrao customizado: {pattern}")
                    severity = entry.get("severity", "HIGH")
                else:
                    continue

                if pattern:
                    try:
                        compiled = re.compile(pattern, re.IGNORECASE)
                        self.blocked_patterns.append((compiled, desc, severity))
                    except re.error as e:
                        logger.warning(f"Padrao customizado invalido: {pattern} -> {e}")

            # Padroes para permitir (override de bloqueio)
            self.allowed_patterns: list[re.Pattern] = []
            for pattern in security_config.get("allowedPatterns", []):
                try:
                    self.allowed_patterns.append(re.compile(pattern, re.IGNORECASE))
                except re.error:
                    pass

            logger.info(
                f"SecurityGuard: {len(self.blocked_patterns)} padroes bloqueados, "
                f"{len(self.allowed_patterns)} permitidos"
            )
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Erro ao carregar config de seguranca: {e}")

    def validate_command(self, command: str) -> "ValidationResult":
        """
        Valida um comando contra os padroes de seguranca.

        Args:
            command: Comando a ser validado.

        Returns:
            ValidationResult com is_safe=True se permitido, False se bloqueado.
        """
        if not self.enabled:
            return ValidationResult(is_safe=True, command=command)

        if not command or not command.strip():
            return ValidationResult(is_safe=True, command=command)

        # Verificar se esta na lista de permitidos
        if hasattr(self, "allowed_patterns"):
            for pattern in self.allowed_patterns:
                if pattern.search(command):
                    return ValidationResult(is_safe=True, command=command)

        # Verificar contra padroes bloqueados
        for compiled_pattern, description, severity in self.blocked_patterns:
            if compiled_pattern.search(command):
                violation = SecurityViolation(
                    command=command,
                    pattern=compiled_pattern.pattern,
                    description=description,
                    severity=severity,
                )
                self.violations_log.append(violation)
                self._log_violation(violation)

                return ValidationResult(
                    is_safe=False,
                    command=command,
                    violation=violation,
                )

        return ValidationResult(is_safe=True, command=command)

    def validate_env_vars(self, env: dict) -> "ValidationResult":
        """Valida variaveis de ambiente por padroes suspeitos."""
        if not self.enabled:
            return ValidationResult(is_safe=True, command="[env vars]")

        suspicious_keys = [
            "LD_PRELOAD", "LD_LIBRARY_PATH", "DYLD_INSERT_LIBRARIES",
            "PYTHONSTARTUP", "PERL5OPT", "NODE_OPTIONS",
        ]

        for key in env:
            if key.upper() in suspicious_keys:
                violation = SecurityViolation(
                    command=f"ENV: {key}={env[key][:50]}",
                    pattern=f"Variavel suspeita: {key}",
                    description=f"Variavel de ambiente potencialmente perigosa: {key}",
                    severity="HIGH",
                )
                self.violations_log.append(violation)
                self._log_violation(violation)
                return ValidationResult(is_safe=False, command=f"ENV:{key}", violation=violation)

        return ValidationResult(is_safe=True, command="[env vars]")

    def validate_file_path(self, path: str) -> "ValidationResult":
        """Valida caminhos de arquivo por traversal ou acesso a areas criticas."""
        if not self.enabled:
            return ValidationResult(is_safe=True, command=path)

        dangerous_paths = [
            r"\.\./\.\./\.\.",          # Path traversal
            r"/etc/(passwd|shadow|sudoers)",
            r"C:\\Windows\\System32",
            r"/proc/self",
            r"~/.ssh/",
            r"\.env$",
            r"id_rsa",
        ]

        for pattern in dangerous_paths:
            try:
                if re.search(pattern, path, re.IGNORECASE):
                    violation = SecurityViolation(
                        command=f"PATH: {path}",
                        pattern=pattern,
                        description=f"Acesso a caminho critico: {path[:100]}",
                        severity="HIGH",
                    )
                    self.violations_log.append(violation)
                    self._log_violation(violation)
                    return ValidationResult(is_safe=False, command=path, violation=violation)
            except re.error:
                continue

        return ValidationResult(is_safe=True, command=path)

    def _log_violation(self, violation: SecurityViolation):
        """Registra violacao no arquivo de log."""
        try:
            if self.log_path:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(
                        f"[{violation.timestamp}] [{violation.severity}] "
                        f"{violation.description} | "
                        f"Comando: {violation.command[:150]}\n"
                    )
        except OSError:
            pass  # Nao falhar por causa de logging

    def get_violations_summary(self) -> dict:
        """Retorna resumo das violacoes detectadas na sessao."""
        by_severity = {}
        for v in self.violations_log:
            by_severity[v.severity] = by_severity.get(v.severity, 0) + 1

        return {
            "total": len(self.violations_log),
            "by_severity": by_severity,
            "recent": [v.to_dict() for v in self.violations_log[-10:]],
        }

    def clear_violations(self):
        """Limpa o historico de violacoes da sessao."""
        self.violations_log.clear()

    def add_pattern(self, pattern: str, description: str = "", severity: str = "HIGH") -> bool:
        """Adiciona um padrao de bloqueio em runtime."""
        try:
            compiled = re.compile(pattern, re.IGNORECASE)
            desc = description or f"Padrao dinamico: {pattern}"
            self.blocked_patterns.append((compiled, desc, severity))
            return True
        except re.error:
            return False

    def remove_pattern(self, pattern: str) -> bool:
        """Remove um padrao de bloqueio por string."""
        for i, (compiled, desc, sev) in enumerate(self.blocked_patterns):
            if compiled.pattern == pattern:
                self.blocked_patterns.pop(i)
                return True
        return False

    @property
    def pattern_count(self) -> int:
        return len(self.blocked_patterns)

    @property
    def violation_count(self) -> int:
        return len(self.violations_log)


class ValidationResult:
    """Resultado de uma validacao de seguranca."""

    def __init__(
        self,
        is_safe: bool,
        command: str,
        violation: Optional[SecurityViolation] = None,
    ):
        self.is_safe = is_safe
        self.command = command
        self.violation = violation

    def __bool__(self) -> bool:
        return self.is_safe

    def __str__(self) -> str:
        if self.is_safe:
            return f"[SAFE] {self.command[:80]}"
        return f"[BLOCKED] {self.violation}"
