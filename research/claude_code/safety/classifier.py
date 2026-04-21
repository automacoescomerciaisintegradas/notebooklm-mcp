from pydantic import BaseModel
from typing import List, Literal

class SafetyAssessment(BaseModel):
    action: str
    risk_level: Literal["low", "medium", "high"]
    reasoning: str
    requires_approval: bool

class AutoModeClassifier:
    """
    Simula o classificador de segurança do Claude Code (YOLO vs Manual).
    Categoriza ações e decide se podem ser executadas autonomamente.
    """
    def __init__(self):
        self.dangerous_patterns = ["rm ", "delete", "push", "drop table", "chmod"]
        self.safe_patterns = ["ls", "cat", "grep", "read", "check", "run tests"]

    def classify(self, command: str) -> SafetyAssessment:
        command_low = command.lower()
        
        # Lógica simplificada de classificação
        if any(p in command_low for p in self.dangerous_patterns):
            return SafetyAssessment(
                action=command,
                risk_level="high",
                reasoning="Comando contém operações potencialmente destrutivas ou que afetam estado compartilhado.",
                requires_approval=True
            )
        
        if any(p in command_low for p in self.safe_patterns):
            return SafetyAssessment(
                action=command,
                risk_level="low",
                reasoning="Operação de leitura ou local/reversível.",
                requires_approval=False
            )
            
        return SafetyAssessment(
            action=command,
            risk_level="medium",
            reasoning="Ação ambígua. Requer monitoramento.",
            requires_approval=True
        )

if __name__ == "__main__":
    classifier = AutoModeClassifier()
    print(classifier.classify("ls -la"))
    print(classifier.classify("rm -rf /"))
