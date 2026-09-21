def formatear_fecha(valor, formato="%d/%m/%Y %H:%M"):
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor
    return valor.strftime(formato)