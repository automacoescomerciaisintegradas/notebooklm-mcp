from engine.assembler import PromptAssembler, ContextInfo
import os

def run_research_demo():
    print("🚀 Iniciando Demonstração de Pesquisa: Claude Code Architecture")
    
    # 1. Configurar Assembler
    base_path = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(base_path, "prompts")
    assembler = PromptAssembler(prompts_dir=prompts_dir)
    
    # 2. Adicionar Módulos de Identidade e Segurança (Seção Fixa)
    print("📦 Carregando Módulos de Identidade e Segurança...")
    assembler.add_static_module("01_main_system_prompt", priority=10)
    assembler.add_static_module("04_cyber_risk_instruction", priority=20)
    
    # 3. Adicionar Módulos Dinâmicos (Simulando Injeção de Contexto)
    print("🔄 Carregando Módulos Dinâmicos...")
    # assembler.add_dynamic_module("available_tools", priority=10)
    
    # 4. Configurar Contexto de Execução
    context = ContextInfo(
        platform_os="Windows 11",
        cwd="C:\\antigravity\\notebooklm-mcp",
        git_state="detached at HEAD",
        available_agents=["Coordinator", "Verification", "Explore"]
    )
    
    # 5. Montar Prompt Final
    print("🏗️ Montando Prompt do Sistema...")
    final_prompt = assembler.assemble(context)
    
    # 6. Exibir Resumo
    print("\n--- RESUMO DO PROMPT MONTADO ---")
    print(f"Comprimento Total: {len(final_prompt)} caracteres")
    print(f"Módulos Estáticos: {[m.name for m in assembler.static_modules]}")
    print(f"Módulos Dinâmicos: {[m.name for m in assembler.dynamic_modules]}")
    print("-" * 32)
    
    # Salvar para inspeção
    with open(os.path.join(base_path, "last_assembled_prompt.txt"), "w", encoding="utf-8") as f:
        f.write(final_prompt)
    print(f"\n✅ Prompt salvo em: research/claude_code/last_assembled_prompt.txt")

if __name__ == "__main__":
    run_research_demo()
