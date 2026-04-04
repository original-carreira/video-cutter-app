def parse_tempo(formato: str) -> float:
    if not isinstance(formato, str):
        raise ValueError("Tempo deve ser uma string")

    formato = formato.strip().replace(",", ".")

    partes = formato.split(":")
    if len(partes) != 3:
        raise ValueError("Formato inválido. Use HH:MM:SS")

    try:
        h = int(partes[0])
        m = int(partes[1])
        s = float(partes[2])
    except ValueError:
        raise ValueError("Tempo contém valores inválidos")

    if m < 0 or m >= 60:
        raise ValueError("Minutos devem estar entre 0 e 59")

    if s < 0 or s >= 60:
        raise ValueError("Segundos devem estar entre 0 e 59")

    if h < 0:
        raise ValueError("Horas não podem ser negativas")

    return h * 3600 + m * 60 + s


def validar_tempo(formato: str) -> bool:
    try:
        parse_tempo(formato)
        return True
    except ValueError:
        return False