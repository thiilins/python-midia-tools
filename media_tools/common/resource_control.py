"""
Controle de recursos para processamento de mídia.
Limita uso de CPU, memória e GPU para evitar sobrecarga do sistema.
"""

import os
import platform
import psutil
import time
from typing import Optional


def obter_cores_disponiveis() -> int:
    """
    Obtém o número de cores disponíveis no sistema.

    Returns:
        int: Número de cores lógicos.
    """
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1


def calcular_threads_seguros(cores_totais: int, percentual: float = 0.5) -> int:
    """
    Calcula número seguro de threads para usar.

    Args:
        cores_totais: Número total de cores.
        percentual: Percentual de cores a usar (padrão: 50%).

    Returns:
        int: Número de threads seguras (mínimo 1, máximo cores_totais).
    """
    threads = max(1, int(cores_totais * percentual))
    return min(threads, cores_totais)


def obter_uso_cpu() -> float:
    """
    Obtém o uso atual de CPU em percentual.

    Returns:
        float: Uso de CPU (0-100).
    """
    try:
        return psutil.cpu_percent(interval=0.1)
    except Exception:
        return 0.0


def obter_uso_memoria() -> float:
    """
    Obtém o uso atual de memória em percentual.

    Returns:
        float: Uso de memória (0-100).
    """
    try:
        return psutil.virtual_memory().percent
    except Exception:
        return 0.0


def verificar_recursos_disponiveis(
    limite_cpu: float = 85.0, limite_memoria: float = 85.0
) -> bool:
    """
    Verifica se há recursos disponíveis para processamento.

    Args:
        limite_cpu: Limite de uso de CPU (padrão: 85%).
        limite_memoria: Limite de uso de memória (padrão: 85%).

    Returns:
        bool: True se há recursos disponíveis, False caso contrário.
    """
    try:
        cpu = obter_uso_cpu()
        memoria = obter_uso_memoria()
        return cpu < limite_cpu and memoria < limite_memoria
    except Exception:
        return True  # Se não conseguir verificar, permite continuar


def aguardar_recursos_disponiveis(
    limite_cpu: float = 85.0,
    limite_memoria: float = 85.0,
    intervalo: float = 2.0,
    timeout: float = 60.0,
) -> bool:
    """
    Aguarda até que recursos estejam disponíveis.

    Args:
        limite_cpu: Limite de uso de CPU (padrão: 85%).
        limite_memoria: Limite de uso de memória (padrão: 85%).
        intervalo: Intervalo entre verificações em segundos (padrão: 2.0).
        timeout: Tempo máximo de espera em segundos (padrão: 60.0).

    Returns:
        bool: True se recursos ficaram disponíveis, False se timeout.
    """
    inicio = time.time()
    while not verificar_recursos_disponiveis(limite_cpu, limite_memoria):
        if time.time() - inicio > timeout:
            return False
        time.sleep(intervalo)
    return True


def definir_prioridade_processo(nice: int = 5) -> bool:
    """
    Define a prioridade do processo atual (apenas Linux/macOS).

    Args:
        nice: Valor nice (padrão: 5, valores maiores = menor prioridade).

    Returns:
        bool: True se conseguiu definir, False caso contrário.
    """
    if platform.system() not in ["Linux", "Darwin"]:
        return False

    try:
        processo = psutil.Process()
        processo.nice(nice)
        return True
    except (psutil.AccessDenied, AttributeError):
        return False


def pausar_entre_processamentos(segundos: float = 1.0) -> None:
    """
    Pausa entre processamentos para dar tempo ao sistema se recuperar.

    Args:
        segundos: Tempo de pausa em segundos (padrão: 1.0).
    """
    time.sleep(segundos)


def obter_configuracao_threads() -> int:
    """
    Obtém configuração de threads do ambiente ou calcula valor seguro.

    Returns:
        int: Número de threads a usar.
    """
    # Tenta obter do ambiente
    env_threads = os.getenv("FFMPEG_THREADS")
    if env_threads:
        try:
            return max(1, int(env_threads))
        except ValueError:
            pass

    # Calcula valor seguro (50% dos cores, mínimo 2, máximo 8)
    cores = obter_cores_disponiveis()
    threads = calcular_threads_seguros(cores, 0.5)
    # Limita a máximo 8 threads para evitar sobrecarga
    return min(threads, 8)


def obter_configuracao_limite_cpu() -> float:
    """
    Obtém limite de CPU do ambiente ou usa padrão.

    Returns:
        float: Limite de CPU (0-100).
    """
    env_cpu = os.getenv("LIMITE_CPU")
    if env_cpu:
        try:
            return max(50.0, min(95.0, float(env_cpu)))
        except ValueError:
            pass
    return 85.0


def obter_configuracao_limite_memoria() -> float:
    """
    Obtém limite de memória do ambiente ou usa padrão.

    Returns:
        float: Limite de memória (0-100).
    """
    env_mem = os.getenv("LIMITE_MEMORIA")
    if env_mem:
        try:
            return max(50.0, min(95.0, float(env_mem)))
        except ValueError:
            pass
    return 85.0


def usar_aceleracao_hardware() -> bool:
    """
    Verifica se deve usar aceleração de hardware (GPU).

    Returns:
        bool: True se deve usar, False caso contrário.
    """
    # Por padrão, desabilita aceleração de hardware
    # (pode ser fraca ou não disponível)
    env_hw = os.getenv("USAR_GPU", "").lower()
    return env_hw in ["true", "1", "yes", "on"]


def obter_pausa_entre_videos() -> float:
    """
    Obtém tempo de pausa entre vídeos do ambiente ou usa padrão.

    Returns:
        float: Tempo de pausa em segundos.
    """
    env_pausa = os.getenv("PAUSA_ENTRE_VIDEOS")
    if env_pausa:
        try:
            return max(0.0, float(env_pausa))
        except ValueError:
            pass
    return 1.0

