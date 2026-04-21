from engine.assembler import PromptAssembler, ContextInfo
from utils.client import GeminiClient
import os
import sys

def interactive_agent_demo():
    print("🤖 Claude Code Research - Interação Real com Gemini")
    print("="*50)
    
    # 1. Setup
    base_path = os.path.dirname(os.path.abspath(__file__))
    prompts_dir = os.path.join(base_path, "prompts")
    assembler = PromptAssembler(prompts_dir=prompts_dir)
    
    # Adicionar módulos principais
    assembler.add_static_module("01_main_system_prompt", priority=10)
    assembler.add_static_module("04_cyber_risk_instruction", priority=20)
    
    # 2. Inicializar Cliente Gemini
    try:
        client = GeminiClient()
        print("✅ Conectado ao Gemini!")
    except Exception as e:
        print(f"❌ Falha crítica de conexão: {e}")
        return

    # 3. Loop de Interação
    context = ContextInfo(
        platform_os="Windows 11",
        cwd=os.getcwd(),
        available_agents=["Coordinator", "Verification", "Explore"]
    )
    
    print("\n[Sistema]: Prompt do Sistema Montado com sucesso.")
    print("[Dica]: Digite 'sair' para encerrar.\n")

    while True:
        user_input = input("Você: ")
        if user_input.lower() in ["sair", "exit", "quit"]:
            break
            
        # Remontar prompt se necessário (pode incluir histórico no futuro)
        system_prompt = assembler.assemble(context)
        
        print("\n[Gemini pensando...]")
        try:
            response = client.generate_response(system_prompt, user_input)
            print(f"\nAgente: {response}\n")
        except Exception as e:
            print(f"Erro na geração: {e}")

if __name__ == "__main__":
    interactive_agent_demo()
