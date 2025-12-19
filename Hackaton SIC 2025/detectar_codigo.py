def detectar_codigo(pregunta: str):
    p = pregunta.lower()

    if "trabajo" in p or "laboral" in p or "empleador" in p or "trabajador" in p:
        return "codigo_trabajo"

    if "penal" in p or "delito" in p or "pena" in p or "hurto" in p:
        return "codigo_penal"

    if "civil" in p or "contrato" in p or "obligación" in p or "responsabilidad" in p:
        return "codigo_civil"

    if "familia" in p or "matrimonio" in p or "divorcio" in p:
        return "codigo_familia"

    return None
