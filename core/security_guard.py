import re
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from core.config_manager import get_config

# =========================
# CONFIGURAÇÃO DE LOG
# =========================
logger = logging.getLogger(__name__)

# =========================
# EXCEÇÕES
# =========================
class SecurityViolation(Exception):
    """Exceção levantada quando um comando viola as regras de segurança."""
    pass


# =========================
# SECURITY GUARD
# =========================
class SecurityGuard:
    """
    Sentinela de segurança para validação de comandos perigosos.
    Implementa o Protocolo de Defesa Preditiva.
    """

    DEFAULT_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"DROP\s+TABLE",
        r"DELETE\s+FROM",
        r"TRUNCATE\s+TABLE",
        r"chmod\s+777",
        r"curl.*\|\s*sh",
        r"wget.*\|\s*sh"
    ]

    # Padrões de segredos para evitar exposição acidental em comandos
    SECRET_PATTERNS = [
        r"AIza[0-9A-Za-z-_]{35}",           # Google API Key
        r"sk-[0-9A-Za-z]{48}",              # OpenAI
        r"sk-ant-api03-[0-9A-Za-z-_]{93}",  # Anthropic
        r"ghp_[0-9A-Za-z]{36}",             # GitHub Personal Access Token
    ]

    def __init__(self):
        self.refresh_config()

    def refresh_config(self):
        """Atualiza as configurações do Security Guard a partir do config manager."""
        self.config = get_config()
        self.enabled = self.config.get("dangerousCommandBlocking.enabled", True)
        self.block_secrets = self.config.get("dangerousCommandBlocking.blockSecrets", True)
        self.patterns = self._compile_patterns()
        self.secret_regex = [re.compile(p) for p in self.SECRET_PATTERNS]

    # =========================
    # CONFIG
    # =========================
    def _compile_patterns(self) -> List[re.Pattern]:
        custom = self.config.get("dangerousCommandBlocking.customPatterns", [])
        
        # Extrair apenas os padrões se forem dicionários (compatibilidade com config atual)
        extracted_custom = []
        for c in custom:
            if isinstance(c, dict):
                extracted_custom.append(c.get("pattern", ""))
            elif isinstance(c, str):
                extracted_custom.append(c)
                
        all_patterns = self.DEFAULT_PATTERNS + [p for p in extracted_custom if p]

        compiled = []
        for pattern in all_patterns:
            try:
                compiled.append(re.compile(pattern, re.IGNORECASE))
            except re.error as e:
                logger.warning(f"Regex inválida ignorada: {pattern} | erro: {e}")
        return compiled

    # =========================
    # NORMALIZAÇÃO
    # =========================
    def _normalize(self, command: str) -> str:
        return command.strip().lower()

    # =========================
    # CLASSIFICAÇÃO
    # =========================
    def _classify_severity(self, command: str) -> str:
        if any(x in command for x in ["rm -rf", "drop table", "truncate"]):
            return "CRÍTICO"
        if any(x in command for x in ["delete from", "chmod", "curl", "wget"]):
            return "ALTO"
        return "MÉDIO"

    # =========================
    # LOG DE AUDITORIA
    # =========================
    def _log_event(self, command: str, status: str, reason: str, severity: str):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "command": command,
            "status": status,
            "reason": reason,
            "severity": severity
        }

        if status == "BLOCKED":
            logger.error(f"🛡️ [SECURITY GUARD] BLOQUEADO: {log_entry}")
        else:
            logger.info(f"🛡️ [SECURITY GUARD] PERMITIDO: {log_entry}")

    # =========================
    # VALIDAÇÃO PRINCIPAL
    # =========================
    def validate(self, command: str, user: str = "unknown") -> bool:
        """
        Valida se um comando é seguro para execução.
        
        Raises:
            SecurityViolation: Se o comando for considerado perigoso ou contiver segredos.
        """
        if not self.enabled:
            return True

        normalized = self._normalize(command)

        # 1. Verificar padrões de comandos perigosos
        for pattern in self.patterns:
            if pattern.search(normalized):
                severity = self._classify_severity(normalized)
                reason = f"Pattern match: {pattern.pattern}"

                self._log_event(command, "BLOCKED", reason, severity)

                raise SecurityViolation(
                    f"[{severity}] Comando bloqueado por segurança: {reason}"
                )

        # 2. Verificar exposição de segredos (se habilitado)
        if self.block_secrets:
            for pattern in self.secret_regex:
                if pattern.search(command): # Verifica o comando original para preservar case de chaves
                    reason = "Detecção de segredo/chave de API no comando"
                    self._log_event("[REDACTED COMMAND]", "BLOCKED", reason, "ALTO")
                    raise SecurityViolation(
                        f"[ALTO] Comando bloqueado: Possível vazamento de segredo detectado."
                    )

        self._log_event(command, "ALLOWED", "No threats detected", "BAIXO")
        return True

    # =========================
    # EXECUÇÃO SEGURA
    # =========================
    def execute(self, command: str, executor_func, user: str = "unknown"):
        """
        Wrapper para execução segura de comandos.
        
        executor_func: função que executa o comando real
        """
        try:
            self.validate(command, user=user)
            return executor_func(command)

        except SecurityViolation as e:
            return {
                "status": "blocked",
                "error": str(e)
            }

        except Exception as e:
            logger.exception("Erro na execução via Security Guard")
            return {
                "status": "error",
                "error": str(e)
            }

    # =========================
    # COMPATIBILIDADE (LEGACY)
    # =========================
    def validate_command(self, command: str):
        """Método de compatibilidade para a API antiga."""
        try:
            self.validate(command)
            return ValidationResult(True, command)
        except SecurityViolation as e:
            # Extrair severidade e descrição da mensagem da exceção
            msg = str(e)
            severity = "HIGH"
            if "[CRÍTICO]" in msg: severity = "CRITICAL"
            elif "[ALTO]" in msg: severity = "HIGH"
            
            violation = LegacyViolation(command, "regex_match", msg, severity)
            return ValidationResult(False, command, violation)

    def validate_env_vars(self, env: dict):
        """Método de compatibilidade para a API antiga."""
        # Implementação básica: apenas permite por enquanto ou valida se houver segredos nos valores
        if self.block_secrets:
            for k, v in env.items():
                for pattern in self.secret_regex:
                    if pattern.search(str(v)):
                        violation = LegacyViolation(f"{k}={v}", "secret_match", "Segredo detectado em variável de ambiente", "HIGH")
                        return ValidationResult(False, f"ENV:{k}", violation)
        return ValidationResult(True, "env_vars")

    def validate_file_path(self, path: str):
        """Método de compatibilidade para a API antiga."""
        return ValidationResult(True, path)

# =========================
# CLASSES DE SUPORTE (LEGACY)
# =========================
class ValidationResult:
    def __init__(self, is_safe, command, violation=None):
        self.is_safe = is_safe
        self.command = command
        self.violation = violation
    def __bool__(self): return self.is_safe

class LegacyViolation:
    def __init__(self, command, pattern, description, severity):
        self.command = command
        self.pattern = pattern
        self.description = description
        self.severity = severity

# Instância global para uso em todo o sistema
security_guard = SecurityGuard()
