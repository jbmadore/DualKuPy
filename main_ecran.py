import spidev 

import RPi.GPIO as GPIO 

import time 

from PIL import Image, ImageDraw, ImageFont

from radar.radar import init_radar, fetch_radar_data, close_radar

from data_io.file_writer import record_measurement


num_record_=150

# === Configuration des GPIO === 

CS = 8 

RESET = 25 

A0 = 24 

BTN_UP = 17 

BTN_DOWN = 27 

BTN_OK = 22 

BTN_CANCEL = 23 
  

# === Configuration des GPIO pour SPI === 
GPIO.setmode(GPIO.BCM) 

GPIO.setup(CS, GPIO.OUT) 

GPIO.setup(RESET, GPIO.OUT) 

GPIO.setup(A0, GPIO.OUT) 

  

# === Configuration des GPIO pour boutons === 

GPIO.setmode(GPIO.BCM) 

GPIO.setup(BTN_UP, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

GPIO.setup(BTN_DOWN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

GPIO.setup(BTN_OK, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

GPIO.setup(BTN_CANCEL, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

# === Initialisation SPI === 

spi = spidev.SpiDev() 

spi.open(0, 0) 

spi.max_speed_hz = 1000000  # 1 MHz 


# === Définition des menus === 

# Dictionnaire global pour stocker les valeurs 

menu_values = { 

    "Site name": "    ",  # Quatre espaces par défaut 

    "Measure #": "00", 

    "Angle": "00", 

    "Pol": "V", 

} 

 

 

menu_structure = [ 

    {"title": "Site name", "options": [" ", " ", " ", " "], "type": "chars"}, 

    {"title": "Measure #", "options": ["0", "0"], "type": "digits"}, 

    {"title": "Angle", "options": ["0", "0"], "type": "digits"}, 

    {"title": "Pol", "options": ["V", "H"], "type": "choice"},  # Choix entre "V" et "H" 

    {"title": "Measurement", "options": "", "type": "action"}  # Ce menu déclenchera une action plus tard 

] 

  

selected_menu = 0 

edit_mode = False 

edit_position = 0  # Position de la lettre/numéro en cours de modification 

  

# === Caractères disponibles pour le menu 1 === 

CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "

def display_welcome_screen(message="Loading..."): 

    """Affiche l'écran de bienvenue avec le logo et un message à droite.""" 

    try: 

        logo = Image.open("logo_white.png").convert('1')  # Charger le logo
#         logo = Image.open("logo.png").convert('RGBA')  # Charger le logo
#         
#         new_logo =Image.new("RGB", logo.size, "white")
#         new_logo.paste(logo, mask=logo.split()[3])

    except FileNotFoundError: 

        print("Erreur : fichier 'logo.png' non trouvé !") 

        logo = Image.new('1', (64, 128), 1)  # Image vide si le logo est absent 

  

    # Créer une image 128x64 pour l'écran d'affichage 

    image = Image.new('1', (128, 64), 1) 

    image.paste(logo, (0, 0))  # Insérer le logo à gauche 

  

    draw = ImageDraw.Draw(image) 

    font = ImageFont.load_default() 

  

    # Afficher le texte à droite 

    text_x = 70  # Décalage à droite 

    text_y = 20  # Ajuster la hauteur du texte 

    draw.text((text_x, text_y), message, font=font, fill=0) 

  

    display_image(image)  # Afficher sur l'écran 

  

    time.sleep(5)  # Pause avant d'afficher le menu principal
    


def draw_menu(): 

    image = Image.new('1', (128, 64), 1)  # Fond blanc 

    draw = ImageDraw.Draw(image) 

    font = ImageFont.load_default() 

  

    for i, menu in enumerate(menu_structure): 

        highlight = i == selected_menu 

        option_text = "".join(menu["options"]) if isinstance(menu["options"], list) else menu["options"]
        
        
#         if menu['title'] == 'Measurement':
#             text = f"{menu['title']}: {option_text}"
# 
#         text = f"{menu['title']}: {option_text}" 

  
        # Centrer le texte pour "Measurement" 

        if menu["title"] == "Measurement": 

            text_x = (128 - font.getsize(menu["title"])[0]) // 2 

            text = menu["title"] 

        else: 

            text = f"{menu['title']}: {option_text}" 

            text_x = 5
            
            
            
           
            

        # Zone sélectionnée en surbrillance 

        if highlight: 

            draw.rectangle((0, i * 12, 128, (i + 1) * 12), fill=0)  # Fond noir 

            draw.text((text_x, i * 12), text, font=font, fill=1)  # Texte blanc 

        else: 

            draw.text((text_x, i * 12), text, font=font, fill=0)  # Texte noir 
  

    # === Ajout de la barre sous la lettre en cours d'édition === 

    if edit_mode: 

        menu = menu_structure[selected_menu]
        print(menu)


        if menu["title"] ==  "Site name": 

            #char_x = 80 + (edit_position * 8)  # Position X de la lettre en cours d'édition 
            char_x = 70 + (edit_position * 6)  # Position X de la lettre en cours d'édition
            print(edit_position)
            bar_y = (selected_menu * 12) + 10  # Position Y sous la ligne 

            draw.line((char_x, bar_y, char_x + 6, bar_y), fill=1, width=1)  # Barre blanche sous la lettre
        
        elif menu["title"] ==  "Measure #": 

            #char_x = 80 + (edit_position * 8)  # Position X de la lettre en cours d'édition 
            char_x = 70 + (edit_position * 6)  # Position X de la lettre en cours d'édition
            print(edit_position)
            bar_y = (selected_menu * 12) + 10  # Position Y sous la ligne 

            draw.line((char_x, bar_y, char_x + 6, bar_y), fill=1, width=1)  # Barre blanche sous la lettre
            
        elif menu["title"] ==  "Angle": 

            #char_x = 80 + (edit_position * 8)  # Position X de la lettre en cours d'édition 
            char_x = 46 + (edit_position * 6)  # Position X de la lettre en cours d'édition
            print(edit_position)
            bar_y = (selected_menu * 12) + 9  # Position Y sous la ligne 

            draw.line((char_x, bar_y, char_x + 6, bar_y), fill=1, width=1)  # Barre blanche sous la lettr


    return image

def measurement_menu(): 

    measurement_options = ["Both", "13GHz", "17GHz"] 

    selected_measurement = 0 

  

    while True: 

        # Affichage du menu Measurement 

        image = Image.new('1', (128, 64), 1) 

        draw = ImageDraw.Draw(image) 

        font = ImageFont.load_default() 

  

        draw.text((40, 10), "Measurement", font=font, fill=0)  # Centrer "Measurement" 

  

        for i, option in enumerate(measurement_options): 

            highlight = i == selected_measurement 

            text_x = (128 - font.getsize(option)[0]) // 2  # Centrer le texte 

            if highlight: 

                draw.rectangle((0, 20 + i * 12, 128, 32 + i * 12), fill=0) 

                draw.text((text_x, 20 + i * 12), option, font=font, fill=1) 

            else: 

                draw.text((text_x, 20 + i * 12), option, font=font, fill=0) 

  

        display_image(image) 

  

        action = wait_for_button() 

  

        if action == "UP": 

            selected_measurement = (selected_measurement - 1) % len(measurement_options) 

        elif action == "DOWN": 

            selected_measurement = (selected_measurement + 1) % len(measurement_options) 

        elif action == "OK": 

            print(f"Measurement sélectionné : {measurement_options[selected_measurement]}")
                        options_1 = {
            "cmd": cmd[0],
            "site_name": '',  # Placeholder values
            "measure_id": '',
            "polarization": '',
            "additional_info": ""
            }
            options_2 = {
                "cmd": cmd[1],
                "site_name": '',  # Placeholder values
                "measure_id": '',
                "polarization": '',
                "additional_info": ""
            }
            options_1.update(recording_info)
            options_2.update(recording_info)
            record_measurement(num_records=num_record_, foldername="./data/", measure_number=1, options=options_1)
            record_measurement(num_records=num_record_, foldername="./data/", measure_number=1, options=options_2)
            

            return measurement_options[selected_measurement]  # Retourne le choix sélectionné 

        elif action == "CANCEL": 

            return None  # Retour au menu principal
        
        
# === Fonction pour afficher l'image sur l'écran LCD === 

def display_image(image): 

    image = image.convert('1')  # Noir & blanc 

    pixels = list(image.getdata()) 

  

    for page in range(8):  # 8 pages (chaque page = 8 lignes) 

        send_command(0xB0 + page) 

        send_command(0x10) 

        send_command(0x00) 

  

        for x in range(128): 

            byte = 0 

            for bit in range(8): 

                if pixels[(page * 8 + bit) * 128 + x] == 0: 

                    byte |= (1 << bit) 

            send_data(byte) 

  

# === Gestion des boutons === 

def wait_for_button(): 

    while True: 

        if GPIO.input(BTN_UP)== GPIO.LOW:
            time.sleep(0.1)
            while GPIO.input(BTN_UP)== GPIO.LOW:
                pass
            
            return "UP" 

        if GPIO.input(BTN_DOWN)== GPIO.LOW: 
            time.sleep(0.1)
            while GPIO.input(BTN_DOWN)== GPIO.LOW:
                pass
            return "DOWN" 

        if GPIO.input(BTN_OK)== GPIO.LOW: 
            time.sleep(0.1)
            while GPIO.input(BTN_OK)== GPIO.LOW:
                pass
            return "OK" 

        if not GPIO.input(BTN_CANCEL)== GPIO.LOW: 
            time.sleep(0.1)
            while GPIO.input(BTN_CANCEL)== GPIO.LOW:
                pass
            return "CANCEL" 

        time.sleep(0.1) 
 # === Configuration des GPIO pour l'écran === 

CS = 8 

RESET = 25 

A0 = 24 

  

GPIO.setup(CS, GPIO.OUT) 

GPIO.setup(RESET, GPIO.OUT) 

GPIO.setup(A0, GPIO.OUT) 

  

# === Initialisation SPI === 

spi = spidev.SpiDev() 

spi.open(0, 0) 

spi.max_speed_hz = 1000000  # 1 MHz 

  

# === Fonction pour envoyer une commande au LCD === 

def send_command(cmd): 

    GPIO.output(A0, GPIO.LOW)  # Mode commande 

    GPIO.output(CS, GPIO.LOW) 

    spi.xfer([cmd]) 

    GPIO.output(CS, GPIO.HIGH) 

  

# === Fonction pour envoyer des données au LCD === 

def send_data(data): 

    GPIO.output(A0, GPIO.HIGH)  # Mode data 

    GPIO.output(CS, GPIO.LOW) 

    spi.xfer([data]) 

    GPIO.output(CS, GPIO.HIGH) 

  

# === Réinitialisation de l'écran LCD === 

def reset_display(): 

    GPIO.output(RESET, GPIO.LOW) 

    time.sleep(0.1) 

    GPIO.output(RESET, GPIO.HIGH) 

  

# === Initialisation complète de l'écran LCD === 

def init_display(): 

    reset_display() 

    send_command(0xA0)  # Segment direction 

    send_command(0xA2)  # LCD Bias 

    send_command(0xC8)  # COM direction 

    send_command(0x2F)  # Power control 

    send_command(0x26)  # Resistor ratio 

    send_command(0x81)  # Contrast 

    send_command(0x11)  # Contrast value 

    send_command(0xAF)  # Display ON 

 

# === Fonction pour gérer le menu principal === 

def menu_navigation(): 

    global selected_menu, edit_mode, edit_position 

  

    while True: 

        img = draw_menu() 

        display_image(img) 

  

        action = wait_for_button() 

  

        if action == "UP": 

            selected_menu = (selected_menu - 1) % len(menu_structure) 

        elif action == "DOWN": 

            selected_menu = (selected_menu + 1) % len(menu_structure) 

        elif action == "OK": 
            print('Selected ', menu_structure[selected_menu]['title'])
            if menu_structure[selected_menu]['title'] == 'Measurement':
                measurement_result = measurement_menu()
                if measurement_result:
                    menu_values["Measurement"] = measurement_result #
                    print(menu_values)


#                 print("\n=== Lancement de Measure ===")
#                 print("Données enregistrées :", menu_values)
#                 time.sleep(2) # Pause pour voir le résultat 
                
            else:
                edit_mode = True 

                edit_position = 0 

                edit_menu() 

        elif action == "CANCEL": 

            return
        
        #elif menu_structure[selected_menu]["title"] == "Measurement": measurement_result = measurement_menu() if measurement_result: menu_values["Measurement"] = measurement_result #

  

# === Fonction pour modifier une valeur === 
def edit_menu(): 

    global edit_mode, edit_position 

  

    while edit_mode: 

        menu = menu_structure[selected_menu] 

  

        img = draw_menu() 

        display_image(img) 

  

        action = wait_for_button() 

  

        if menu["type"] == "chars":  # Sélection des 4 caractères
            char_to_edit = menu['options'][edit_position]
            
            if char_to_edit not in CHARACTERS:
                char_to_edit ='A'

            #index = CHARACTERS.index(menu["options"][edit_position]) 

            index = CHARACTERS.index(char_to_edit)

            if action == "UP": 

                index = (index + 1) % len(CHARACTERS) 

            elif action == "DOWN": 

                index = (index - 1) % len(CHARACTERS) 

            elif action == "OK": 

                edit_position += 1
                
                index = 0

                if edit_position >= 4: 

                    edit_mode = False  # Retour automatique au menu principal 

            elif action == "CANCEL": 

                edit_mode = False 

  

            if edit_mode == True:
                print(CHARACTERS[index] )
                print(menu["options"][edit_position])
                menu["options"][edit_position] = CHARACTERS[index]
            else:
                print(menu_values)

  

        elif menu["type"] == "digits":  # Sélection des chiffres 

            index = int(menu["options"][edit_position]) 

  

            if action == "UP": 

                index = (index + 1) % 10 

            elif action == "DOWN": 

                index = (index - 1) % 10 

            elif action == "OK": 

                edit_position += 1
                
                index = 0

                if edit_position >= 2: 

                    edit_mode = False 

            elif action == "CANCEL": 

                edit_mode = False 

  
            if edit_mode == True:
                
                menu["options"][edit_position] = str(index) 
            else:
                print(menu_values)
  

        elif menu["type"] == "choice":  # Choix entre "V" et "H" 

            if action == "UP" or action == "DOWN": 

                menu["options"] = "H" if menu["options"] == "V" else "V" 

            elif action == "OK": 

                edit_mode = False 

            elif action == "CANCEL": 

                edit_mode = False 
            
            if edit_mode == False:
                print(menu_values)
                
#         elif menu["title"] == "Measure":  
#             
#             print("\n=== Lancement de Measure ===")
#             print("Données enregistrées :", menu_values)
#             time.sleep(2) # Pause pour voir le résultat 

        # Mettre à jour les valeurs dans le dictionnaire avec les nouvelles clés 

        menu_values[menu["title"]] = "".join(menu["options"]) if isinstance(menu["options"], list) else menu["options"] 


# === Programme principal ===
radar1_ip = '192.168.0.13'
radar2_ip = '192.168.0.17'
radar1_host_port = 4100
radar2_host_port = 4101

# Initialize each radar
com1, cmd1, ok1 = init_radar(radar1_ip, host_port=radar1_host_port)
com2, cmd2, ok2 = init_radar(radar2_ip, host_port=radar2_host_port)

# Check each radar's connection status and print the IP of connected radars
if ok1 and ok2:
    print(f"Radar 13GHz connected at IP address {radar1_ip}")
    print(f"Radar 17GHz connected at IP address {radar2_ip}")
    fig, ax, lines,dashlines = init_plot(("13GHz", "17GHz"), two_radar=True)
    
    
elif ok1 and not ok2:
    print(f"Radar 13GHz connected at IP address {radar1_ip}")
    print(f"Failed 17GHz to connect radar at IP address {radar2_ip}")
    com2 =None
    fig, ax, lines,dashlines = init_plot("13GHz", two_radar=False)
    
elif ok2 and not ok1:
    print(f"Radar 17GHz connected at IP address {radar2_ip}")
    print(f"Failed 13GHz to connect radar at IP address {radar1_ip}")
    com1=None
    fig, ax, lines,dashlines = init_plot("17GHz", two_radar=False)
else:
    print("Failed to initialize both radars. Exiting...")
    return
    
    
    
init_display() 

display_welcome_screen(message="Loading...")

menu_navigation() 

print("Menu terminé") 



