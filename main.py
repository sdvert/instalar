import os
import shutil
import asyncio
import json
import webbrowser
import random
import csv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError, PeerFloodError, FloodWaitError, UserPrivacyRestrictedError
from telethon.tl.functions.channels import JoinChannelRequest, InviteToChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, AddChatUserRequest
from telethon.tl.types import UserStatusOnline, UserStatusRecently, UserStatusLastWeek

# ==========================================
# DIRETÓRIOS DE SESSÕES E ARQUIVOS
# ==========================================
PASTA_SESSOES = 'sessoes'
PASTA_ATENCAO = 'sessoes atencao'
ARQUIVO_MENSAGEM = 'mensagem.txt'
ARQUIVO_TAREFAS = 'tarefas.json'
ARQUIVO_APIS = 'api.csv'
ARQUIVO_MAPEAMENTO_API = 'conta_api.json'

# Criação automática das pastas
os.makedirs(PASTA_SESSOES, exist_ok=True)
os.makedirs(PASTA_ATENCAO, exist_ok=True)

# ==========================================
# GESTÃO INTELIGENTE DE APIs (1:1 EXCLUSIVO)
# ==========================================
def carregar_mapeamento_api():
    """Carrega o vínculo permanente entre números e APIs."""
    if os.path.exists(ARQUIVO_MAPEAMENTO_API):
        try:
            with open(ARQUIVO_MAPEAMENTO_API, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def salvar_mapeamento_api(dados):
    """Salva o vínculo permanente no arquivo JSON."""
    with open(ARQUIVO_MAPEAMENTO_API, 'w', encoding='utf-8') as f:
        json.dump(dados, f, ensure_ascii=False, indent=4)

def obter_api_para_conta(numero):
    """Retorna a API vinculada à conta ou pega uma nova livre no CSV."""
    mapeamento = carregar_mapeamento_api()
    
    if numero in mapeamento:
        return mapeamento[numero]['api_id'], mapeamento[numero]['api_hash']
        
    apis_totais = []
    if os.path.exists(ARQUIVO_APIS):
        try:
            with open(ARQUIVO_APIS, 'r', encoding='utf-8') as f:
                leitor = csv.reader(f)
                for linha in leitor:
                    if len(linha) >= 2:
                        try:
                            apis_totais.append((int(linha[0].strip()), linha[1].strip()))
                        except ValueError:
                            continue
        except Exception as e:
            print(f"⚠️ Erro ao ler '{ARQUIVO_APIS}': {e}")
            
    apis_em_uso = [(dados['api_id'], dados['api_hash']) for dados in mapeamento.values()]
    apis_livres = [api for api in apis_totais if api not in apis_em_uso]
    
    if apis_livres:
        nova_api = random.choice(apis_livres)
        mapeamento[numero] = {"api_id": nova_api[0], "api_hash": nova_api[1]}
        salvar_mapeamento_api(mapeamento)
        print(f"🔗 Nova API ({nova_api[0]}) vinculada exclusivamente à conta {numero}.")
        return nova_api[0], nova_api[1]
    else:
        print(f"⚠️ ATENÇÃO: Nenhuma API LIVRE encontrada para a conta {numero}! Usando API padrão genérica.")
        return 25708349, 'cc1da8ef8e9e6a60c6f9863c00c7da06'

def liberar_api_conta(numero):
    """Remove o vínculo da API quando a conta for excluída."""
    mapeamento = carregar_mapeamento_api()
    if numero in mapeamento:
        api_liberada = mapeamento[numero]['api_id']
        del mapeamento[numero]
        salvar_mapeamento_api(mapeamento)
        print(f"🔓 A API {api_liberada} foi desconectada do número e está livre novamente.")

# ==========================================
# GERADOR DE DISPOSITIVOS FALSOS (SPOOFING)
# ==========================================
def obter_dispositivo_aleatorio():
    modelos = [
        "SamsungGalaxy S20", "Xiaomi13T", "MotorolaMoto G Pro", "XiaomiRedmi 9C NFC",
        "XiaomiMi 10 Pro 5G", "XiaomiMi 10T Pro 5G", "SamsungGalaxy S20+", "MotorolaMoto G23",
        "SamsungGalaxy A24 4G", "SamsungGalaxy S22 5G", "MotorolaEdge 40", "SamsungGalaxy A02s",
        "SamsungGalaxy A14 5G", "XiaomiPoco X5", "MotorolaMoto G14", "SamsungGalaxy A51 5G UW",
        "MotorolaEdge 40 Neo", "SamsungGalaxy Z Fold3 5G", "SamsungGalaxy Tab A9",
        "SamsungGalaxy A32 5G", "MotorolaMoto G32", "MotorolaDefy", "SamsungGalaxy A91",
        "XiaomiPoco F2 Pro", "XiaomiBlack Shark 4", "SamsungGalaxy S21 Ultra 5G",
        "SamsungGalaxy A03", "MotorolaEdge 20", "SamsungGalaxy M21", "SamsungGalaxy Tab A7 10.4",
        "SamsungGalaxy Note20 5G", "SamsungGalaxy Z Fold5", "MotorolaMoto G22", "MotorolaMoto G22",
        "Xiaomi12 Lite NE", "SamsungGalaxy Tab S8", "MotorolaMoto G10 Power", "XiaomiCivi 3",
        "MotorolaMoto X40", "SamsungGalaxy M31 Prime", "XiaomiRedmi Note 9 Pro Max",
        "MotorolaMoto G Stylus 5G", "XiaomiPoco M5s", "MotorolaEdge 40", "MotorolaEdge S30",
        "MotorolaEdge 30", "XiaomiPoco M6", "MotorolaMoto G Play", "XiaomiRedmi Note 11",
        "MotorolaMoto G84", "XiaomiMix Fold 2", "XiaomiPoco M5s", "SamsungGalaxy M31",
        "XiaomiRedmi Note 10 Pro Max", "XiaomiBlack Shark 3", "MotorolaMoto G9 Play",
        "MotorolaMoto G53", "MotorolaMoto G32", "XiaomiRedmi Note 10", "MotorolaMoto G100",
        "XiaomiRedmi 13C 5G", "Xiaomi12", "XiaomiPoco M2 Reloaded", "MotorolaEdge 40",
        "XiaomiRedmi 12C", "MotorolaMoto G34", "MotorolaMoto G9 Play", "XiaomiMi 11X Pro",
        "XiaomiPoco M4 Pro", "SamsungGalaxy S20 5G UW", "SamsungGalaxy S20 5G",
        "XiaomiRedmi Note 11R", "MotorolaMoto G23", "XiaomiMix Fold 2", "SamsungGalaxy A41",
        "MotorolaRazr 40 Ultra", "XiaomiBlack Shark 3", "MotorolaMoto G54", "SamsungGalaxy S20+",
        "XiaomiRedmi Note 12 Pro Speed", "MotorolaMoto G Stylus", "SamsungGalaxy Tab A9",
        "MotorolaMoto G Play", "MotorolaMoto G52", "MotorolaMoto G52", "SamsungGalaxy F02s",
        "SamsungGalaxy F34", "MotorolaMoto G40 Fusion", "MotorolaRazr 40 Ultra", "MotorolaEdge 40",
        "MotorolaEdge 30 Neo", "SamsungGalaxy A01 Core", "XiaomiRedmi 9T", "XiaomiPoco M2 Reloaded",
        "MotorolaEdge 30 Pro", "MotorolaMoto G71 5G", "XiaomiMi 10 Pro 5G", "XiaomiRedmi 13C",
        "SamsungGalaxy Tab S9 Ultra", "MotorolaEdge 30 Fusion"
    ]
    versoes_android = ["11.0.0", "12.0.0", "13.0.0", "14.0.0"]

    return {
        "device_model": random.choice(modelos),
        "system_version": f"Android {random.choice(versoes_android)}",
        "app_version": "12.5.2 (65979)"
    }

# ==========================================
# BANCO DE DADOS (JSON)
# ==========================================
def carregar_tarefas():
    if os.path.exists(ARQUIVO_TAREFAS):
        try:
            with open(ARQUIVO_TAREFAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def salvar_tarefas(tarefas):
    with open(ARQUIVO_TAREFAS, 'w', encoding='utf-8') as f:
        json.dump(tarefas, f, ensure_ascii=False, indent=4)

# ==========================================
# INTERFACE E MENUS
# ==========================================
def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_banner_grande():
    limpar_tela()
    print(r"""

 
        ROBÔ DE LEADS PARA IPHONE
        CRIADO POR INSTAGRAM: @JV.BOTS                                        
        YOUTUBE : @jvtrader6595

    Você só receberá atualizações dessa ferramenta
    Caso tenha comprado de @JV.BOTS e esteja na
    área de membros da PERFECT ACADEMY
    Para dúvidas fale com (84) 9849-3595 (JVBOTS)
        
    """)

def mostrar_banner_pequeno():
    limpar_tela()
    print("===============================================")
    print("                                              ")
    print("      ROBÔ DE LEADS PARA IPHONE | @JV.BOTS")
    print("      COMPRE SESSÕES EM: T.ME/SESSOESBOT_BOT")
    print("      CLONA GRUPOS: T.ME/autorepassejvbots_bot")
    print("                                              ")
    print("===============================================")

# ==========================================
# FUNÇÕES AUXILIARES DE PROCESSAMENTO
# ==========================================
def usuario_passou_no_filtro(usuario, filtro_escolhido):
    if getattr(usuario, 'bot', False) or not getattr(usuario, 'username', None):
        return False
    status = getattr(usuario, 'status', None)
    if filtro_escolhido == '1' and isinstance(status, UserStatusOnline): return True
    if filtro_escolhido == '2' and isinstance(status, (UserStatusOnline, UserStatusRecently)): return True
    if filtro_escolhido == '3' and isinstance(status, (UserStatusOnline, UserStatusRecently, UserStatusLastWeek)): return True
    return False

async def triagem_contas():
    """Verifica e retorna apenas as contas logadas, movendo as limitadas."""
    sessoes_arquivos = [arq for arq in os.listdir(PASTA_SESSOES) if arq.endswith('.session')]
    if not sessoes_arquivos:
        return []
    print("🔍 Verificando status das contas...\n")
    contas_ativas = []
    for arquivo in sessoes_arquivos:
        numero = arquivo.replace('.session', '')
        disp = obter_dispositivo_aleatorio()
        api_id_atual, api_hash_atual = obter_api_para_conta(numero)
        
        client = TelegramClient(
            os.path.join(PASTA_SESSOES, numero), 
            api_id_atual, 
            api_hash_atual,
            device_model=disp['device_model'],
            system_version=disp['system_version'],
            app_version=disp['app_version']
        )
        try:
            await client.connect()
            if not await client.is_user_authorized():
                await client.disconnect()
                shutil.move(os.path.join(PASTA_SESSOES, arquivo), os.path.join(PASTA_ATENCAO, arquivo))
                print(f"❌ Conta {numero} desconectada. Movida para atenção.")
            else:
                contas_ativas.append((numero, client))
        except Exception:
            if client.is_connected(): await client.disconnect()
    return contas_ativas

async def mapeamento_inteligente(cliente_extrator, link_origem, opcao_filtro):
    """Extrai membros via Lista e Chat History, evitando duplicidade com set()."""
    try:
        if "+" in link_origem or "joinchat" in link_origem:
            hash_convite = link_origem.split('+')[-1].strip('/') if "+" in link_origem else link_origem.split('joinchat/')[-1].strip('/')
            await cliente_extrator(ImportChatInviteRequest(hash_convite))
        else:
            username = link_origem.split('/')[-1].replace('@', '').strip()
            await cliente_extrator(JoinChannelRequest(username))
        print("✅ Conta extratora ingressou no grupo de origem para leitura.")
    except Exception: pass
    
    alvos_set = set()
    try:
        grupo_entity = await cliente_extrator.get_entity(link_origem)
        
        print("🔍 Vasculhando lista de membros...")
        try:
            async for membro in cliente_extrator.iter_participants(grupo_entity):
                if usuario_passou_no_filtro(membro, opcao_filtro): alvos_set.add(membro.username)
            print(f"   ↳ Captados pela lista principal: {len(alvos_set)}")
        except Exception as e_lista:
            print(f"⚠️ Restrição na lista de membros: {e_lista}")

        print("🔍 Vasculhando histórico (5000 mensagens)...")
        try:
            async for msg in cliente_extrator.iter_messages(grupo_entity, limit=5000):
                rem = msg.sender
                if rem and usuario_passou_no_filtro(rem, opcao_filtro): alvos_set.add(rem.username)
        except Exception as e_msg:
            print(f"⚠️ Restrição na leitura de chat: {e_msg}")

        alvos_finais = list(alvos_set)
        print(f"\n✅ Mapeamento total concluído! {len(alvos_finais)} alvos ÚNICOS e filtrados.")
        return alvos_finais
    except Exception as e:
        print(f"❌ Erro crítico no mapeamento: {e}")
        return []

async def gerenciar_tarefas_interface():
    """Interface unificada para retomada/exclusão de tarefas salvas."""
    tarefas = carregar_tarefas()
    link_grupo = ""
    alvos_encontrados = []
    
    while tarefas:
        print("\n📂 TAREFAS ANTERIORES ENCONTRADAS:")
        chaves = list(tarefas.keys())
        for i, link in enumerate(chaves):
            print(f"[{i + 1}] - Retomar tarefa: {link} (Restam {len(tarefas[link])})")
            
        op_nova = len(chaves) + 1
        op_excluir = len(chaves) + 2
        
        print(f"[{op_nova}] - Iniciar uma NOVA tarefa do zero")
        print(f"[{op_excluir}] - EXCLUIR uma tarefa salva\n")
        
        try:
            esc = int(input("Escolha uma opção: "))
            if 1 <= esc <= len(chaves):
                link_grupo = chaves[esc - 1]
                alvos_encontrados = tarefas[link_grupo]
                print(f"\n✅ Retomando fila para {link_grupo}. {len(alvos_encontrados)} membros restantes.")
                break
            elif esc == op_nova:
                break
            elif esc == op_excluir:
                num_ex = int(input("\nQual tarefa deseja excluir? (Digite o número da lista acima): "))
                if 1 <= num_ex <= len(chaves):
                    rem = chaves[num_ex - 1]
                    del tarefas[rem]
                    salvar_tarefas(tarefas)
                    print(f"✅ Tarefa '{rem}' excluída com sucesso!")
                    if not tarefas: break
                else:
                    print("❌ Opção de exclusão inválida.")
            else:
                print("❌ Opção não reconhecida.")
        except ValueError:
            print("❌ Entrada inválida. Use apenas números.")
            
    return link_grupo, alvos_encontrados, tarefas

# ==========================================
# FUNÇÕES DE USUÁRIO (MENU 1 a 10)
# ==========================================
async def adicionar_numero():
    numero = input("Digite o número do Telegram com DDI e DDD (Ex: +5511999999999): ").strip()
    caminho_sessao = os.path.join(PASTA_SESSOES, numero)
    disp = obter_dispositivo_aleatorio()
    api_id_atual, api_hash_atual = obter_api_para_conta(numero)
    
    client = TelegramClient(
        caminho_sessao, 
        api_id_atual, 
        api_hash_atual,
        device_model=disp['device_model'],
        system_version=disp['system_version'],
        app_version=disp['app_version']
    )
    await client.connect()
    if not await client.is_user_authorized():
        try:
            await client.send_code_request(numero)
            codigo = input(f"Digite o código enviado pelo Telegram para {numero}: ")
            try:
                await client.sign_in(numero, codigo)
            except SessionPasswordNeededError:
                senha_2fa = input("Conta protegida por 2FA. Digite a senha: ")
                await client.sign_in(password=senha_2fa)
            print(f"\n✅ Sessão {numero} criada com sucesso.")
        except Exception as e:
            print(f"\n❌ Erro ao autenticar: {e}")
            if client.is_connected(): await client.disconnect()
            if os.path.exists(f"{caminho_sessao}.session"): os.remove(f"{caminho_sessao}.session")
            liberar_api_conta(numero) 
    else:
        print(f"\n✅ O número {numero} já está autenticado.")
    if client.is_connected(): await client.disconnect()

async def verificar_restricoes():
    sessoes_arquivos = [arq for arq in os.listdir(PASTA_SESSOES) if arq.endswith('.session')]
    if not sessoes_arquivos:
        print("⚠️ Nenhuma sessão encontrada."); return
    print(f"🔍 Verificando {len(sessoes_arquivos)} conta(s) no @SpamBot...\n")
    contas_verificadas = []
    for arquivo in sessoes_arquivos:
        numero = arquivo.replace('.session', '')
        contas_verificadas.append(arquivo)
        disp = obter_dispositivo_aleatorio()
        api_id_atual, api_hash_atual = obter_api_para_conta(numero)
        
        client = TelegramClient(
            os.path.join(PASTA_SESSOES, numero), 
            api_id_atual, 
            api_hash_atual,
            device_model=disp['device_model'],
            system_version=disp['system_version'],
            app_version=disp['app_version']
        )
        try:
            await client.connect()
            if not await client.is_user_authorized():
                print(f"❌ [{numero}] Desconectada."); await client.disconnect(); continue
            async with client.conversation('@SpamBot', timeout=15) as conv:
                await conv.send_message('/start')
                resposta = await conv.get_response()
                print(f"--- Relatório SpamBot: {numero} ---\n{resposta.text}\n" + "-" * 40)
            await client.disconnect()
        except Exception as e:
            print(f"❌ Erro na conta {numero}: {e}")
            if client.is_connected(): await client.disconnect()
            
    escolha_mover = input("Deseja mover alguma sessão para a pasta de atenção? (s/n): ").lower().strip()
    if escolha_mover == 's':
        for i, arq in enumerate(contas_verificadas): print(f"[{i + 1}] - {arq.replace('.session', '')}")
        try:
            indices = input("\nDigite os números separados por vírgula: ")
            lista_indices = [int(x.strip()) - 1 for x in indices.split(',')]
            for idx in lista_indices:
                if 0 <= idx < len(contas_verificadas):
                    arquivo_alvo = contas_verificadas[idx]
                    shutil.move(os.path.join(PASTA_SESSOES, arquivo_alvo), os.path.join(PASTA_ATENCAO, arquivo_alvo))
                    print(f"✅ {arquivo_alvo} movido.")
        except ValueError: print("❌ Entrada inválida.")

async def remover_numero():
    sessoes_arquivos = [arq for arq in os.listdir(PASTA_SESSOES) if arq.endswith('.session')]
    if not sessoes_arquivos: print("⚠️ Nenhuma sessão."); return
    for indice, arquivo in enumerate(sessoes_arquivos): print(f"[{indice + 1}] - {arquivo.replace('.session', '')}")
    try:
        escolha = int(input("\nNúmero da conta para excluir: "))
        if 1 <= escolha <= len(sessoes_arquivos):
            arquivo_excluir = sessoes_arquivos[escolha - 1]
            numero_excluir = arquivo_excluir.replace('.session', '')
            os.remove(os.path.join(PASTA_SESSOES, arquivo_excluir))
            print(f"\n🗑️ Sessão {numero_excluir} deletada dos arquivos.")
            liberar_api_conta(numero_excluir)
    except ValueError: print("\n❌ Opção inválida.")

async def entrar_em_grupo():
    contas = await triagem_contas()
    if not contas: print("\n⚠️ Nenhuma conta ativa."); return
    link_grupo = input("\nDigite o link do grupo público ou privado: ").strip()
    for numero, client in contas:
        try:
            if "+" in link_grupo or "joinchat" in link_grupo:
                hash_convite = link_grupo.split('+')[-1].strip('/') if "+" in link_grupo else link_grupo.split('joinchat/')[-1].strip('/')
                await client(ImportChatInviteRequest(hash_convite))
            else:
                username = link_grupo.split('/')[-1].replace('@', '').strip()
                await client(JoinChannelRequest(username))
            print(f"✅ Conta {numero} entrou no grupo!")
        except Exception as e: print(f"❌ Erro na conta {numero}: {e}")
        finally: await client.disconnect()

async def enviar_mensagens_pv():
    """Função 5: Enviar DM"""
    if not os.path.exists(ARQUIVO_MENSAGEM): print(f"⚠️ O arquivo '{ARQUIVO_MENSAGEM}' não foi encontrado."); return
    with open(ARQUIVO_MENSAGEM, 'r', encoding='utf-8') as f: texto_mensagem = f.read().strip()
    if not texto_mensagem: print(f"⚠️ O arquivo '{ARQUIVO_MENSAGEM}' está vazio."); return
    
    contas = await triagem_contas()
    if not contas: print("\n⚠️ Sem contas ativas para operar."); return
    print(f"\n✅ {len(contas)} contas prontas para uso.")

    link_tarefa, alvos_encontrados, tarefas = await gerenciar_tarefas_interface()
    
    try:
        limite = int(input("\nQuantidade de mensagens por sessão? "))
        delay = float(input("Delay entre os envios (segundos)? "))
    except ValueError:
        print("❌ Digite números válidos."); [await c.disconnect() for _, c in contas]; return

    if not alvos_encontrados:
        link_origem = input("\nLink do grupo para raspar membros: ").strip()
        print("\nFiltro: 1 - Online / 2 - Recente (3 dias) / 3 - Última Semana (7 dias)")
        op_f = input("Escolha a opção (1/2/3): ").strip()
        alvos_encontrados = await mapeamento_inteligente(contas[0][1], link_origem, op_f)
        if not alvos_encontrados:
            print("⚠️ Nenhum alvo captado."); [await c.disconnect() for _, c in contas]; return
        link_tarefa = link_origem
        tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)

    print("\n🚀 Iniciando disparos...")
    sucesso = 0; falha = 0
    try:
        for numero, client in contas:
            if not alvos_encontrados: break
            print(f"\n--- 📤 Rodada com a conta: {numero} ---")
            msgs_conta = 0
            while msgs_conta < limite and alvos_encontrados:
                alvo = alvos_encontrados.pop(0)
                try:
                    await client.send_message(alvo, texto_mensagem)
                    print(f"✅ [{numero}] Enviado para @{alvo}")
                    sucesso += 1; msgs_conta += 1
                    tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)
                    await asyncio.sleep(delay)
                except PeerFloodError:
                    print(f"⛔ [{numero}] Conta limitada por spam (PeerFloodError). Movendo para atenção...")
                    alvos_encontrados.insert(0, alvo)
                    await client.disconnect()
                    shutil.move(os.path.join(PASTA_SESSOES, f"{numero}.session"), os.path.join(PASTA_ATENCAO, f"{numero}.session"))
                    break
                except FloodWaitError as e:
                    print(f"⚠️ [{numero}] FloodWaitError ({e.seconds}s). Trocando de conta...")
                    alvos_encontrados.insert(0, alvo); break
                except Exception as e:
                    erro_str = str(e).lower()
                    if any(erro in erro_str for erro in ['banned', 'frozen', 'chat_member_add_failed']):
                        print(f"⛔ [{numero}] Conta banida/congelada ({e}). Movendo para atenção...")
                        alvos_encontrados.insert(0, alvo)
                        await client.disconnect()
                        try:
                            shutil.move(os.path.join(PASTA_SESSOES, f"{numero}.session"), os.path.join(PASTA_ATENCAO, f"{numero}.session"))
                        except: pass
                        break
                    else:
                        print(f"❌ [{numero}] Falha @{alvo}: {e}"); falha += 1
                        tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)
                        await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário!")
    finally:
        if not alvos_encontrados and link_tarefa in tarefas: del tarefas[link_tarefa]
        salvar_tarefas(tarefas); [await c.disconnect() for _, c in contas]
        print("\n" + "="*50 + f"\n📊 RELATÓRIO: ✅ {sucesso} Enviadas | ❌ {falha} Falhas | 👥 Fila: {len(alvos_encontrados)}\n" + "="*50)

async def adicionar_membros_grupo():
    """Função 6: Adicionar Membros (Adding) com Relatórios Detalhados e Antifraude"""
    contas = await triagem_contas()
    if not contas: print("\n⚠️ Sem contas ativas para operar."); return
    print(f"\n✅ {len(contas)} contas prontas para uso.")

    link_tarefa, alvos_encontrados, tarefas = await gerenciar_tarefas_interface()
    
    try:
        limite = int(input("\nQuantos membros adicionar por cada sessão? "))
        delay = float(input("Delay entre cada adição (segundos)? "))
    except ValueError:
        print("❌ Digite números válidos."); [await c.disconnect() for _, c in contas]; return

    if not alvos_encontrados:
        link_origem = input("\nLink do grupo de ORIGEM (para raspar): ").strip()
        print("\nFiltro: 1 - Online / 2 - Recente (3 dias) / 3 - Última Semana (7 dias)")
        op_f = input("Escolha a opção (1/2/3): ").strip()
        alvos_encontrados = await mapeamento_inteligente(contas[0][1], link_origem, op_f)
        if not alvos_encontrados:
            print("⚠️ Nenhum membro captado."); [await c.disconnect() for _, c in contas]; return
        link_tarefa = link_origem
        tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)

    link_destino = input("\nLink do grupo de DESTINO (Onde serão adicionados): ").strip()
    print("\n🚀 Iniciando processo de adição aos grupos...\n")
    
    sucesso = 0; falha = 0
    try:
        for numero, client in contas:
            if not alvos_encontrados: break
            
            print(f"\n--- 👥 Preparando a conta: {numero} ---")
            
            # PASSO DE VERIFICAÇÃO/ENTRADA ANTES DE ADICIONAR
            target_entity = None
            try:
                if "+" in link_destino or "joinchat" in link_destino:
                    hash_c = link_destino.split('+')[-1].strip('/') if "+" in link_destino else link_destino.split('joinchat/')[-1].strip('/')
                    try:
                        updates = await client(ImportChatInviteRequest(hash_c))
                        target_entity = updates.chats[0]
                        print(f"✅ [{numero}] Entrou no grupo privado de destino com sucesso.")
                    except Exception as e:
                        if 'UserAlreadyParticipant' in str(e) or 'already a participant' in str(e).lower():
                            target_entity = await client.get_entity(link_destino)
                            print(f"✅ [{numero}] Verificado: Já estava dentro do grupo privado.")
                        else:
                            raise e
                else:
                    target_entity = await client.get_entity(link_destino)
                    await client(JoinChannelRequest(target_entity))
                    print(f"✅ [{numero}] Entrou/Verificou o acesso ao grupo público.")
            except Exception as e:
                try: 
                    target_entity = await client.get_entity(link_destino)
                    print(f"✅ [{numero}] Acesso ao grupo confirmado.")
                except Exception as e2: 
                    print(f"❌ [{numero}] Falha crítica ao acessar o destino: {e2}")
                    continue

            print(f"🚀 Iniciando adições...\n")
            adds_conta = 0
            while adds_conta < limite and alvos_encontrados:
                alvo = alvos_encontrados.pop(0)
                
                # MENSAGEM ANTES DE TENTAR
                print(f"🔄 [{numero}] Processando @{alvo}...")
                
                try:
                    # Checa se o destino é um Grupo Normal ou Supergrupo/Canal
                    if type(target_entity).__name__ == 'Chat':
                        resultado = await client(AddChatUserRequest(chat_id=target_entity.id, user_id=alvo, fwd_limit=0))
                    else:
                        resultado = await client(InviteToChannelRequest(target_entity, [alvo]))
                        
                    # ====================================================
                    # A MÁGICA ANTIFRAUDE: DETECÇÃO DE SHADOWBAN
                    # ====================================================
                    if hasattr(resultado, 'updates') and not resultado.updates:
                        print(f"  ↳ 👻 SHADOWBAN DETECTADO! O Telegram bloqueou silenciosamente.")
                        print(f"  ↳ ⛔ Movendo conta para atenção e trocando de número...")
                        alvos_encontrados.insert(0, alvo) # Devolve o alvo para a fila
                        await client.disconnect()
                        shutil.move(os.path.join(PASTA_SESSOES, f"{numero}.session"), os.path.join(PASTA_ATENCAO, f"{numero}.session"))
                        break # Para a conta e vai para a próxima
                    # ====================================================

                    # RELATÓRIO DE SUCESSO REAL
                    print(f"  ↳ ✅ Adicionado com sucesso!")
                    sucesso += 1; adds_conta += 1
                    tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)
                    await asyncio.sleep(delay)
                    
                except UserPrivacyRestrictedError:
                    print(f"  ↳ ⚠️ Falha: Restrito pelas configurações de privacidade.")
                    falha += 1
                    tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)
                except PeerFloodError:
                    print(f"  ↳ ⛔ Falha: Conta limitada por spam (PeerFloodError). Trocando...")
                    alvos_encontrados.insert(0, alvo)
                    await client.disconnect()
                    shutil.move(os.path.join(PASTA_SESSOES, f"{numero}.session"), os.path.join(PASTA_ATENCAO, f"{numero}.session"))
                    break
                except FloodWaitError as e:
                    print(f"  ↳ ⏳ Falha: Restrição temporária FloodWait ({e.seconds}s). Trocando conta...")
                    alvos_encontrados.insert(0, alvo)
                    break
                except Exception as e:
                    erro_str = str(e).lower()
                    if 'already a participant' in erro_str or 'user_already_participant' in erro_str:
                        print(f"  ↳ ⚠️ Falha: O usuário @{alvo} já está no grupo.")
                        falha += 1
                        tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)
                    elif any(erro in erro_str for erro in ['banned', 'frozen', 'chat_member_add_failed']):
                        print(f"  ↳ ⛔ Falha Crítica: Conta banida ou congelada. Trocando...")
                        alvos_encontrados.insert(0, alvo)
                        await client.disconnect()
                        try:
                            shutil.move(os.path.join(PASTA_SESSOES, f"{numero}.session"), os.path.join(PASTA_ATENCAO, f"{numero}.session"))
                        except Exception: pass
                        break
                    else:
                        print(f"  ↳ ❌ Falha técnica: {e}")
                        falha += 1
                        tarefas[link_tarefa] = alvos_encontrados; salvar_tarefas(tarefas)
                        await asyncio.sleep(1)
                        
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário!")
    finally:
        if not alvos_encontrados and link_tarefa in tarefas: del tarefas[link_tarefa]
        salvar_tarefas(tarefas); [await c.disconnect() for _, c in contas]
        print("\n" + "="*50 + f"\n📊 RELATÓRIO: ✅ {sucesso} Adicionados | ❌ {falha} Erros | 👥 Fila: {len(alvos_encontrados)}\n" + "="*50)

async def comprar_numeros():
    """Função 7: Redireciona para o bot de compra de números."""
    print("\n🌐 Abrindo o navegador para comprar números ou sessões...")
    webbrowser.open("https://t.me/sessoesbot_bot")
    print("✅ Navegador aberto com sucesso!")

async def comprar_membros():
    """Função 8: Redireciona para o site de compra de membros fake."""
    print("\n🌐 Abrindo o navegador para comprar membros fake...")
    webbrowser.open("https://leadsstore.me/")
    print("✅ Navegador aberto com sucesso!")

async def resgatar_codigo_login():
    """Função 9: Resgatar código de login da conta oficial do Telegram (777000)."""
    sessoes_arquivos = [arq for arq in os.listdir(PASTA_SESSOES) if arq.endswith('.session')]
    if not sessoes_arquivos:
        print("\n⚠️ Nenhuma sessão encontrada na pasta.")
        return

    print("\n📱 Contas disponíveis para resgatar código:")
    for indice, arquivo in enumerate(sessoes_arquivos):
        print(f"[{indice + 1}] - {arquivo.replace('.session', '')}")

    try:
        escolha = int(input("\nDigite o número da conta na lista acima: "))
        if 1 <= escolha <= len(sessoes_arquivos):
            arquivo_escolhido = sessoes_arquivos[escolha - 1]
            numero = arquivo_escolhido.replace('.session', '')
        else:
            print("\n❌ Opção inválida.")
            return
    except ValueError:
        print("\n❌ Entrada inválida. Por favor, digite o número correspondente à conta.")
        return

    disp = obter_dispositivo_aleatorio()
    api_id_atual, api_hash_atual = obter_api_para_conta(numero)

    client = TelegramClient(
        os.path.join(PASTA_SESSOES, numero), 
        api_id_atual, 
        api_hash_atual,
        device_model=disp['device_model'],
        system_version=disp['system_version'],
        app_version=disp['app_version']
    )

    print(f"\n🔍 Conectando à conta {numero} para buscar o código...")
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print("❌ Esta sessão não está mais autorizada/logada.")
            await client.disconnect()
            return

        print("📩 Lendo as últimas mensagens da conta oficial do Telegram...\n")
        mensagens = await client.get_messages(777000, limit=3)

        encontrou = False
        for msg in mensagens:
            if msg.text:
                print("=" * 50)
                data_msg = msg.date.strftime('%d/%m/%Y %H:%M:%S')
                print(f"📅 Data: {data_msg}")
                print(f"💬 Mensagem:\n{msg.text}")
                encontrou = True

        if not encontrou:
            print("⚠️ Nenhuma mensagem de código encontrada no histórico recente.")
        print("=" * 50)

    except Exception as e:
        print(f"❌ Erro ao buscar o código: {e}")
    finally:
        if client.is_connected():
            await client.disconnect()

# ==========================================
# LOOP PRINCIPAL
# ==========================================
async def main():
    mostrar_banner_grande(); input("Pressione ENTER para iniciar...")
    while True:
        mostrar_banner_pequeno()
        print("1 - Adicionar número de Telegram")
        print("2 - Verificar por spam/restrições (@SpamBot)")
        print("3 - Remover número de Telegram")
        print("4 - Entrar com as contas em um Grupo")
        print("5 - Enviar mensagens no Privado (DM)")
        print("6 - Adicionar Membros em um Grupo (Adding)")
        print("7 - Compre números e sessões de telegram aqui")
        print("8 - Compre membros fake para seu grupo")
        print("9 - Resgatar Código de Login (Acesso Web/App)")
        print("10 - Fechar Programa\n")
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == '1': await adicionar_numero()
        elif opcao == '2': await verificar_restricoes()
        elif opcao == '3': await remover_numero()
        elif opcao == '4': await entrar_em_grupo()
        elif opcao == '5': await enviar_mensagens_pv()
        elif opcao == '6': await adicionar_membros_grupo()
        elif opcao == '7': await comprar_numeros()
        elif opcao == '8': await comprar_membros()
        elif opcao == '9': await resgatar_codigo_login()
        elif opcao == '10': print("\nEncerrando LEADSROBOT... Até logo!"); break
        else: print("\n❌ Opção não reconhecida. Tente novamente.")
        
        input("\nPressione ENTER para continuar...")

if __name__ == '__main__':
    asyncio.run(main())
