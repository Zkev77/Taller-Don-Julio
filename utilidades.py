BAJO_STOCK = 5


def formatear_fecha(valor, formato="%d/%m/%Y %H:%M"):
    if valor is None:
        return ""
    if isinstance(valor, str):
        return valor
    return valor.strftime(formato)


def solo_numeros_y_punto(caracter, texto_actual, longitud_maxima=12):
    if caracter == '':
        return True
    return (caracter.isdigit() or caracter == '.') and len(texto_actual) <= longitud_maxima


def registrar_validador(ventana, longitud_maxima=12):
    return ventana.register(lambda c, t: solo_numeros_y_punto(c, t, longitud_maxima))
