BAJO_STOCK = 5


def formatear_fecha(valor, formato="%d/%m/%Y %H:%M"):
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor
    return valor.strftime(formato)


def solo_numeros_y_punto(caracter, texto_actual, max_len=12):
    if caracter == '':
        return True
    return (caracter.isdigit() or caracter == '.') and len(texto_actual) <= max_len


def registrar_validador(ventana, max_len=12):
    return ventana.register(lambda c, t: solo_numeros_y_punto(c, t, max_len))
