import os
from jinja2 import Template, Environment, FileSystemLoader
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class PromptModule(BaseModel):
    name: str
    content: str
    priority: int = 100
    description: Optional[str] = None

class ContextInfo(BaseModel):
    platform_os: str = "Windows"
    cwd: str = os.getcwd()
    git_state: Optional[str] = None
    available_agents: List[str] = []
    memory_files: List[str] = []

class PromptAssembler:
    """
    Sistema robusto de montagem de prompts modulares baseado na arquitetura observada do Claude Code.
    Dividido em Seção Fixa (Cacheable Prefix) e Seção Dinâmica (Dynamic Suffix).
    """
    def __init__(self, prompts_dir: str):
        self.prompts_dir = prompts_dir
        self.env = Environment(loader=FileSystemLoader(prompts_dir))
        self.static_modules: List[PromptModule] = []
        self.dynamic_modules: List[PromptModule] = []

    def add_static_module(self, name: str, priority: int = 100):
        content = self._load_prompt(name)
        self.static_modules.append(PromptModule(name=name, content=content, priority=priority))
        self.static_modules.sort(key=lambda x: x.priority)

    def add_dynamic_module(self, name: str, priority: int = 100):
        content = self._load_prompt(name)
        self.dynamic_modules.append(PromptModule(name=name, content=content, priority=priority))
        self.dynamic_modules.sort(key=lambda x: x.priority)

    def _load_prompt(self, name: str) -> str:
        # Tenta carregar do sistema de arquivos
        try:
            template = self.env.get_template(f"{name}.md")
            return template.render()
        except Exception:
            # Fallback para string dummy se não existir
            return f"# Content for {name} not found."

    def assemble(self, context: ContextInfo) -> str:
        sections = []

        # 1. Cacheable Prefix (Identity, Safety, rules)
        sections.append("=== CACHEABLE PREFIX ===")
        for module in self.static_modules:
            sections.append(module.content)
        
        # 2. Cache Boundary
        sections.append("\n--- CACHE BOUNDARY ---\n")

        # 3. Dynamic Suffix (Environment, Memory, Agents)
        sections.append("=== DYNAMIC SUFFIX ===")
        for module in self.dynamic_modules:
            sections.append(module.content)
        
        # 4. Context Metadata (Runtime Injection)
        sections.append(f"CURRENT_OS: {context.platform_os}")
        sections.append(f"CURRENT_DIR: {context.cwd}")
        if context.git_state:
            sections.append(f"GIT_STATE: {context.git_state}")
        
        return "\n\n".join(sections)

if __name__ == "__main__":
    # Teste rápido
    assembler = PromptAssembler(prompts_dir="research/claude_code/prompts")
    assembler.add_static_module("01_main_system_prompt", priority=10)
    assembler.add_static_module("04_cyber_risk_instruction", priority=20)
    
    assembler.add_dynamic_module(" उपलब्ध_agents", priority=10) # Exemplo
    
    context = ContextInfo()
    final_prompt = assembler.assemble(context)
    print("Prompt Montado com Sucesso!")
    # print(final_prompt)
