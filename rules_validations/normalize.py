def normalize_value(value) -> str:
    return value \
        .lower() \
        .replace('á', 'a').replace('ä', 'a') \
        .replace('é', 'e').replace('ë', 'e') \
        .replace('í', 'i').replace('ï', 'i') \
        .replace('ó', 'o').replace('ö', 'o') \
        .replace('ú', 'u').replace('ü', 'u') \
        .replace('ñ', 'n') \
        .replace('(', '_') \
        .replace(')', '_') \
        .replace('/', '_') \
        .replace('+', 'p') \
        .replace('.', '') \
        .replace(',', '_') \
        .replace(':', '') \
        .replace(';', '') \
        .replace('-', '_') \
        .replace(' ', '_')
