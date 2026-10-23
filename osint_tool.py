import anthropic
import base64
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic()

print("="*50)
print("🕵️  DELEGADO DIGITAL - FERRAMENTA DE OSINT GERAL")
print("="*50)
argumento_investigacao = input("Digite o caso/contexto da investigação:\n> ")

if not argumento_investigacao.strip():
    print("Erro: O argumento não pode estar vazio.")
    exit()

print("\nAnalisando a cena e cruzando com o contexto... aguarde.\n")

# --- PROMPT GENERALISTA (O Cérebro do Delegado) ---
system_prompt = f"""
Você é um Investigador Sênior e Analista de OSINT, atuando como um assistente para um Delegado Humano.
Sua função é analisar qualquer tipo de imagem (cenas de crime, escritórios, ruas, objetos) e extrair inteligência acionável, cruzando com o contexto fornecido.

**CONTEXTO DO CASO (Fornecido pelo Analista Humano):**
{argumento_investigacao}

Regras de Investigação:
1. **Leitura da Cena:** Descreva o ambiente e os elementos visíveis sem julgar. O que é o cenário? O que está fora do lugar?
2. **Nexos e Dedução:** Como os elementos se relacionam? Se há uma queda, há um objeto caído. Se há uma invasão, há marcas de arrombamento. Busque a lógica física e comportamental.
3. **Anomalias (O "Cachorro que não latiu"):** Aponte o que *deveria* estar ali mas não está, ou o que está ali mas não deveria (ex: uma xícara intacta em meio a uma briga, uma tela ligada numa cena de roubo).
4. **Confronto de Versões:** O argumento do humano é compatível com a evidência visual? Se não, aponte a contradição de forma técnica.
5. **Ética:** NUNCA tente identificar pessoas ou usar reconhecimento facial. Se houver humanos, descreva apenas vestimenta, postura e ação (ex: "indivíduo de camisa azul inclinado sobre a mesa").
6. **Formato:** Retorne ESTRITAMENTE um objeto JSON válido, sem Markdown.
"""

# JSON Generalista (Serve para carros, mesas, crimes, etc)
schema_json = """
{
  "resumo_da_cena": "Uma frase descrevendo o que a imagem mostra objetivamente.",
  "compatibilidade_do_contexto": "O relato/contexto faz sentido com a imagem? Sim, Não ou Parcialmente.",
  "analise_de_nexos": "Explique a lógica do que aconteceu (como os objetos chegaram àquela posição).",
  "anomalias_ou_pontos_cegos": ["O que está estranho ou fora de lugar na cena?", "O que falta?"],
  "hipoteses_investigativas": [
    {
      "categoria": "Ex: Dinâmica / Comportamento / Rastreamento",
      "deducao": "A hipótese do que pode ter ocorrido.",
      "nivel_confianca": "Alta / Média / Baixa",
      "justificativa": "Baseado em qual evidência visual (máx 15 palavras)."
    }
  ],
  "proximos_passos_para_o_delegado": ["O que o humano deve investigar agora?", "Qual perícia solicitar?"]
}
"""

image_path = "/media/sf_osint_share/teste2.jpeg" 

if not os.path.exists(image_path):
    print(f"ERRO: A imagem não foi encontrada no caminho: {image_path}")
    exit()

with open(image_path, "rb") as image_file:
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

inicio = time.time()

message = client.messages.create(
    model="claude-haiku-5-5", 
    max_tokens=4096,
    system=system_prompt,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": f"Analise a cena como um investigador e preencha o JSON: {schema_json}"
                }
            ],
        }
    ],
)

fim = time.time()
tempo_total = fim - inicio

print(f"--- RELATÓRIO DE INTELIGÊNCIA OSINT (Tempo: {tempo_total:.2f}s) ---\n")

texto_bruto = next((bloco.text for bloco in message.content if hasattr(bloco, 'text')), "{}")

try:
    texto_limpo = texto_bruto.replace("```json", "").replace("```", "").strip()
    dados = json.loads(texto_limpo)
    
    print(f"📌 RESUMO DA CENA: {dados.get('resumo_da_cena')}\n")
    print(f"⚖️  O CONTEXTO FAZ SENTIDO?: {dados.get('compatibilidade_do_contexto')}\n")
    print(f"🔗 ANÁLISE DE NEXOS: {dados.get('analise_de_nexos')}\n")
    
    print("🚩 ANOMALIAS E PONTOS CEGOS:")
    for anomalia in dados.get('anomalias_ou_pontos_cegos', []):
        print(f"  - {anomalia}")
        
    print("\n🕵️ HIPÓTESES INVESTIGATIVAS:")
    for hip in dados.get('hipoteses_investigativas', []):
        print(f"  - [{hip.get('categoria')}] {hip.get('deducao')}")
        print(f"    Confiança: {hip.get('nivel_confianca')} | Base: {hip.get('justificativa')}")
        
    print("\n🎯 PRÓXIMOS PASSOS PARA O DELEGADO:")
    for passo in dados.get('proximos_passos_para_o_delegado', []):
        print(f"  - {passo}")

except json.JSONDecodeError:
    print("⚠️ A IA não retornou um JSON válido. Texto bruto abaixo:\n")
    print(texto_bruto)
