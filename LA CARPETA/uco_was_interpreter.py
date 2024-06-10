import re

# Solicitar al usuario el path del archivo
nameFile = input("Ingrese el nombre del archivo que se desea examinar: ")

# Variables globales
currentTokenPosition = 0
currentToken = ""
tokenPositions = []  # Para almacenar las posiciones de los tokens
seen_numbers = set()  # Para almacenar los numeros ya vistos
seen_emails = set()  # Para almacenar los correos electronicos ya vistos
html_response = "<html><head><title>Resultado del Analisis Sintactico</title></head><body><pre>\n"


def match(token):
    global currentTokenPosition
    global currentToken
    global vecTokenTypes
    global vecLexemes
    global tokenPositions
    global html_response

    currentToken = vecTokenTypes[currentTokenPosition]
    if currentToken == token:
        currentTokenPosition += 1
        html_response += f"Token {token} consumido.<br>\n"
    elif currentToken == "UNKNOWN":
        row, col = tokenPositions[currentTokenPosition]
        html_response += f"<h2>Error Sintáctico</h2><p>Fila {row}, Columna {col}: La cadena ingresada '{vecLexemes[currentTokenPosition]}' es desconocida.</p>"
        raise Exception(f"Error sintactico en fila {row}, columna {col}. La cadena ingresada '{vecLexemes[currentTokenPosition]}' es desconocida.")
    else:
        row, col = tokenPositions[currentTokenPosition]
        html_response += f"<h2>Error Sintáctico</h2><p>Fila {row}, Columna {col}: Se esperaba '{token}' pero se encontró '{currentToken}'.</p>"
        raise Exception(f"Error sintactico en fila {row}, columna {col}. Se esperaba '{token}' pero se encontro '{currentToken}'.")
        

def person():
    global currentTokenPosition
    global vecLexemes
    global html_response

    number = vecLexemes[currentTokenPosition]
    if number in seen_numbers:
        row, col = tokenPositions[currentTokenPosition]
        html_response += f"<h2>Error Sintactico</h2><p>Fila {row}, Columna {col}: El numero '{number}' ya ha sido utilizado en esta organizacion.</p>"
        raise Exception(f"Error sintactico en fila {row}, columna {col}. El numero '{number}' ya ha sido utilizado en esta organizacion.")
    seen_numbers.add(number)
    match("number")

    match(";")

    match("str")
    match(";")
    match("str")
    match(";")

    email = vecLexemes[currentTokenPosition]
    if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        row, col = tokenPositions[currentTokenPosition]
        html_response += f"<h2>Error Sintactico</h2><p>Fila {row}, Columna {col}: Se esperaba un correo electronico valido pero se encontro '{email}'.</p>"
        raise Exception(f"Error sintactico en fila {row}, columna {col}. Se esperaba un correo electronico valido pero se encontro '{email}'.")
    
    if email in seen_emails:
        row, col = tokenPositions[currentTokenPosition]
        html_response += f"<h2>Error Sintactico</h2><p>Fila {row}, Columna {col}: El correo electronico '{email}' ya ha sido utilizado en esta organización.</p>"
        raise Exception(f"Error sintactico en fila {row}, columna {col}. El correo electronico '{email}' ya ha sido utilizado en esta organizacion.")
    seen_emails.add(email)

    match("str")

    match(";")

def persons():
    global currentTokenPosition
    global currentToken
    global vecTokenTypes

    currentToken = vecTokenTypes[currentTokenPosition]
    if currentToken == "number":
        person()
        persons()

def workgroup():
    global html_response
    match("WG")
    html_response += "<h2>Workgroup</h2>\n"
    match("(")
    html_response += "<ul>\n"
    persons()
    html_response += "</ul>\n"
    match(")")

def workgroups():
    global currentTokenPosition
    global currentToken
    global vecTokenTypes
    global html_response

    currentToken = vecTokenTypes[currentTokenPosition]
    if currentToken == "WG":
        html_response += "<div class='workgroup'>\n"
        workgroup()
        workgroups()
        html_response += "</div>\n"

def org():
    global html_response

    match("str")
    html_response += "<h1>Organización</h1>\n"
    match("(")
    html_response += "<div class='workgroups'>\n"
    workgroups()
    html_response += "</div>\n"
    match(")")

def get_token_positions(input_str):
    positions = []
    row, col = 1, 1
    for i, char in enumerate(input_str):
        if char == '\n':
            row += 1
            col = 1
        else:
            col += 1
        positions.append((row, col))
    return positions

def calculate_token_positions(input_str, tokens):
    positions = []
    current_position = 0
    for token in tokens:
        while current_position < len(input_str) and input_str[current_position] in " \n\t":
            current_position += 1
        start_position = current_position
        current_position += len(token)
        row = input_str.count('\n', 0, start_position) + 1
        col = start_position - input_str.rfind('\n', 0, start_position)
        positions.append((row, col))
    return positions

try:
    # Leer el contenido del archivo
    with open(nameFile, "r") as f:
        inputstr = f.read()

    # Obtener posiciones de tokens antes de eliminar espacios
    original_positions = get_token_positions(inputstr)

    # Eliminar los signos de espacio, tabulador y linea nueva de la entrada
    html_response += "1) Se eliminan los espacios, tabuladores y linea nueva, quedando asi: <br>\n"
    inputstr_cleaned = re.sub(r"[\n\t\s]*", "", inputstr)
    html_response += f"<code>{inputstr_cleaned}</code><br>\n"

    # Agregar nuevos espacios alrededor de (, ; y )
    html_response += "2) Ahora se agregan nuevos espacios, pero exclusivamente a partir de los (, ; y ): <br>\n"
    inputstr_spaced = re.sub(r"(\(|\)|;)", r" \1 ", inputstr_cleaned)
    inputstr_spaced = re.sub(r'\s+', ' ', inputstr_spaced).strip()
    html_response += f"<code>{inputstr_spaced}</code><br>\n"

    # Clasificacion de lexemas
    inputstr_split = inputstr_spaced.split(" ")
    html_response += "La lista de posibles lexemas es: <br>\n"
    html_response += f"<code>{inputstr_split}</code><br>\n"

    vecTokenTypes = []
    vecLexemes = []
    dic_directTokens = {
        'str': 'str',
        '(': '(',
        'WG': 'WG',
        ')': ')',
        'number': 'number',
        'email': 'email',
        ';': ';',
        'UNKNOWN': 'UNKNOWN'
    }

    # Clasificar lexemas y calcular posiciones
    for c in inputstr_split:
        if c in dic_directTokens:
            vecTokenTypes.append(dic_directTokens[c])
            vecLexemes.append(c)
        elif re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", c):
            vecTokenTypes.append('email')
            vecLexemes.append(c)
        elif re.match(r'^".*"$', c):
            vecTokenTypes.append('str')
            vecLexemes.append(c)
        elif re.match(r"^\d+$", c):
            vecTokenTypes.append('number')
            vecLexemes.append(c)
        else:
            vecTokenTypes.append('UNKNOWN')
            vecLexemes.append(c)

    # Calcular posiciones originales de los tokens
    tokenPositions = calculate_token_positions(inputstr, vecLexemes)

    html_response += "<h2>Tipos de Tokens resultantes:</h2>\n"
    html_response += f"<code>{vecTokenTypes}</code><br>\n"
    html_response += "<h2>Lexemas resultantes:</h2>\n"
    html_response += f"<code>{vecLexemes}</code><br>\n"

    # Comienza el analisis sintactico
    html_response += "<h2>Analisis sintactico:</h2>\n"
    org()
    html_response += "<h2>La cadena ingresada es valida sintacticamente.</h2>\n"

except Exception as exception:
    html_response += f"<h2>Error:</h2><p>{exception}</p>\n"

html_response += "</pre></body></html>"

# Imprimir el resultado final
print(html_response)

		
			
	
	
	

