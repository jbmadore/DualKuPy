"""
menu.py
This module manages the interactive menu displayed on an LCD screen.
"""
import time
from lcd_display import display_image
from buttons import wait_for_button
from PIL import Image, ImageDraw, ImageFont
from data_io.file_writer import record_measurement
from radar.radar import fetch_radar_data

# === Global Variables ===

last_filename = "No measurement yet"  # Stores the last saved filename

menu_values = {
    "Site name": "    ",  # Four spaces by default
    "Measure #": "00",
    "Angle": "00",
    "Pol": "V",
}

# Menu structure defining each option and its type
# menu_structure = [
#     {"title": "Site name", "options": [" ", " ", " ", " "], "type": "chars"},
#     {"title": "Measure #", "options": ["0", "0"], "type": "digits"},
#     {"title": "Angle", "options": ["0", "0"], "type": "digits"},
#     {"title": "Pol", "options": ["V", "H"], "type": "choice"},  # Choice between "V" and "H"
#     {"title": "Measurement", "options": "", "type": "action"}  # This menu triggers an action
# ]

menu_structure = [
    {"title": "Site name", "options": [" ", " ", " ", " "], "type": "chars"},
    {"title": "Measure #", "options": ["0", "0"], "type": "digits"},
    {"title": "Angle", "options": ["0", "0"], "type": "numbers"},
    {"title": "Pol", "options": ["V", "H"], "type": "choice"},  # Choice between "V" and "H"
    {"title": "Measurement", "options": "", "type": "action"}  # This menu triggers an action
]

# Track menu state
selected_menu = 0
edit_mode = False
edit_position = 0  # Position of the letter/number currently being modified
current_time = time.strftime("%H:%M")
current_date = time.strftime("%Y/%m/%d")
# Available characters for selection
CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

NUMBERS = "0123456789"

def process_data(rx_values):
    """
    Extrait et réduit les valeurs d'amplitude des signaux radar.
    - Prend les valeurs entre l'index **20 et 100**
    - Garde **1 valeur sur 2** pour éviter trop de points sur l'écran
    
    Args:
        rx_values (list): Données brutes du radar.

    Returns:
        tuple: (amplitudes traitées, distances correspondantes)
    """
    rx_values = [abs(item) for item in rx_values[20:100]]  # Valeurs absolues
    distances = list(range(len(rx_values)))  # Associe une distance en pixels

    return rx_values[::2], distances[::2]  # Sélection 1 valeur sur 2


def generate_graph_image(data1, data2):
    """
    Génère une image 128x64 avec les données radar (13 GHz & 17 GHz).
    - **Amplitude en X**
    - **Distance en Y (inversée pour que le haut soit 0)**
    
    Args:
        data1 (list): Amplitudes du radar 13 GHz.
        data2 (list): Amplitudes du radar 17 GHz.

    Returns:
        Image (PIL): Image prête à être affichée sur l'écran LCD.
    """
    # Création de l’image 128x64 (blanc par défaut)
    image = Image.new('1', (128, 64), 1)
    draw = ImageDraw.Draw(image)
    
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)

    # **Processus des données**
    data1, distances1 = process_data(data1)
    data2, distances2 = process_data(data2)

    # **Paramètres du graph**
    graph_width = 50  # Largeur de chaque graphe
    graph_height = 40  # Hauteur
    margin_x = 10  # Décalage X pour le premier graph
    margin_y = 15  # Décalage Y pour ne pas toucher le titre

    # **Tracer les axes**
    # Axe Y (Distance) pour 13 GHz
    draw.line((margin_x, margin_y, margin_x, margin_y + graph_height), fill=0)
    # Axe X (Amplitude) pour 13 GHz
    draw.line((margin_x, margin_y + graph_height, margin_x + graph_width, margin_y + graph_height), fill=0)

    # Axe Y (Distance) pour 17 GHz
    draw.line((margin_x + graph_width + 10, margin_y, margin_x + graph_width + 10, margin_y + graph_height), fill=0)
    # Axe X (Amplitude) pour 17 GHz
    draw.line((margin_x + graph_width + 10, margin_y + graph_height, margin_x + 2 * graph_width + 10, margin_y + graph_height), fill=0)

    # **Tracer les labels "0" et "Max"**
    draw.text((margin_x - 3, margin_y + graph_height + 2), "0", font=small_font, fill=0)
    draw.text((margin_x + graph_width - 10, margin_y + graph_height + 2), "Max", font=small_font, fill=0)
    draw.text((margin_x + graph_width + 10, margin_y + graph_height + 2), "0", font=small_font, fill=0)
    draw.text((margin_x + 2 * graph_width, margin_y + graph_height + 2), "Max", font=small_font, fill=0)

    # **Tracer les données inversées pour que 0 soit en haut**
    max_amp_13 = max(data1) if data1 else 1
    max_amp_17 = max(data2) if data2 else 1
    if sum(data1) !=0:
        for i in range(len(distances1) - 1):
            #max_amp_13 = 60000
            x1 = margin_x + int((data1[i] / max_amp_13) * graph_width)
            y1 = margin_y + graph_height - int((distances1[i] / max(distances1)) * graph_height)
            x2 = margin_x + int((data1[i + 1] / max_amp_13) * graph_width)
            y2 = margin_y + graph_height - int((distances1[i + 1] / max(distances1)) * graph_height)
            draw.line((x1, y1, x2, y2), fill=0)
        # for i, (amp_13, dist_13) in enumerate(zip(data1, distances1)):
        #     points_13 = []
        #     x_13 = margin_x + int((amp_13 / max_amp_13) * graph_width)
        #     y_13 = margin_y + graph_height - int((dist_13 / max(distances1)) * graph_height)
        #     points_13.append((x_13, y_13))
        # draw.line(points_13, fill=0)  # Connect points with a line
            #draw.point((x_13, y_13), fill=0)
    if sum(data2) !=0:

        for i in range(len(distances2) - 1):
            #max_amp_17 = 10000
            x1 = margin_x + graph_width + 10 + int((data2[i] / max_amp_17) * graph_width)
            y1 = margin_y + graph_height - int((distances2[i] / max(distances2)) * graph_height)
            x2 = margin_x + graph_width + 10 + int((data2[i + 1] / max_amp_17) * graph_width)
            y2 = margin_y + graph_height - int((distances2[i + 1] / max(distances2)) * graph_height)
            draw.line((x1, y1, x2, y2), fill=0)

        # for i, (amp_17, dist_17) in enumerate(zip(data2, distances2)):
        #     points_17 = []
        #     x_17 = margin_x + graph_width + 10 + int((amp_17 / max_amp_17) * graph_width)
        #     y_17 = margin_y + graph_height - int((dist_17 / max(distances2)) * graph_height)
        #     draw.point((x_17, y_17), fill=0)
        #     points_17.append((x_17, y_17))
        # draw.line(points_17, fill=0)  # Connect points with a line

    # **Titres**
    draw.text((margin_x, 3), "13 GHz", font=small_font, fill=0)
    draw.text((margin_x + graph_width + 10, 3), "17 GHz", font=small_font, fill=0)

    return image


# def process_data(rx_values):
#     """
#     Extrait et réduit les valeurs d'amplitude des signaux radar.
#     - Prend les valeurs entre l'index **20 et 100**
#     - Garde **1 valeur sur 2** pour éviter trop de points sur l'écran
    
#     Args:
#         rx_values (list): Données brutes du radar.

#     Returns:
#         tuple: (amplitudes traitées, distance correspondante)
#     """
#     rx_values = [abs(item) for item in rx_values[20:100]]  # Valeurs absolues
#     distances = list(range(len(rx_values)))  # Associe une distance en pixels

#     return rx_values[::2], distances[::2]  # Sélection 1 valeur sur 2

# def scale_data(values, min_pixel, max_pixel):
#     """
#     Redimensionne les amplitudes pour qu'elles tiennent sur l'écran.
    
#     Args:
#         values (list): Amplitudes brutes.
#         min_pixel (int): Position min sur l'axe des X.
#         max_pixel (int): Position max sur l'axe des X.
    
#     Returns:
#         list: Valeurs redimensionnées en pixels.
#     """
#     if not values:
#         return []

#     min_val = min(values)
#     max_val = max(values)
    
#     if max_val - min_val == 0:
#         return [min_pixel] * len(values)  # Évite une division par zéro

#     return [
#         int(min_pixel + (val - min_val) / (max_val - min_val) * (max_pixel - min_pixel))
#         for val in values
#     ]


def take_measurement(cmd, menu_structure, measure_type=None):
    """Takes a measurement for the specified radar when paused."""
    global last_filename  # Make it accessible to draw_menu()
    
    num_record_ = 50
    menu_values = {
        "Site name": "    ",  # Four spaces by default
        "Measure #": "00",
        "Angle": "00",
        "Pol": "V",
    }
    menu_values_filled = menu_values
    menu_values_filled['Site name'] = "".join(menu_structure[0]['options'])
    menu_values_filled['Measure #'] = "".join(menu_structure[1]['options'])
    menu_values_filled['Angle'] = "".join(menu_structure[2]['options'])
    menu_values_filled['Pol'] = "".join(menu_structure[3]['options'])
    recording_info = menu_values_filled
    recording_info["site_name"] = recording_info.pop("Site name")
    recording_info["measure_id"] = recording_info.pop("Measure #")
    recording_info["polarization"] = recording_info.pop("Pol")
    recording_info["radar_angle"] = recording_info.pop("Angle")

    last_filename = f"{recording_info['site_name']}_{recording_info['measure_id']}_{recording_info['polarization']}_{recording_info['radar_angle']}deg.txt"
    # Display filename on screen
    image = Image.new('1', (128, 64), 1)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)  

    draw.text((5, 5), "Recording...", font=font, fill=0)
    draw.text((5, 20), "Saving as:", font=font, fill=0)
    draw.text((5, 35), last_filename[:18], font=font, fill=0)  # Truncate long filenames
    
    display_image(image)
    time.sleep(1)
    print(f"Starting measurement for {measure_type} at site {recording_info['site_name']} "
          f"with angle {recording_info['radar_angle']} and polarization {recording_info['polarization']}...")
    
    print(measure_type)
    
    if measure_type=='Both':
#         options_1 = {
#         "cmd": cmd[0],
#         "site_name": '',  # Placeholder values
#         "measure_id": '',
#         "polarization": '',
#         "additional_info": ""
#         }
#         options_2 = {
#             "cmd": cmd[1],
#             "site_name": '',  # Placeholder values
#             "measure_id": '',
#             "polarization": '',
#             "additional_info": ""
#         }
        options_1 = {"cmd": cmd[0], **recording_info}
        options_2 = {"cmd": cmd[1], **recording_info}
#         options_1.update(recording_info)
#         options_2.update(recording_info)
        print(options_1)
        print(options_2)
        record_measurement(num_records=num_record_, foldername="/mnt/usb/radar_data/", measure_number=1, options=options_1)
        record_measurement(num_records=num_record_, foldername="/mnt/usb/radar_data/", measure_number=1, options=options_2)
        data1 = fetch_radar_data(cmd[0])['data'][0]
        data2 = fetch_radar_data(cmd[1])['data'][0]

    # elif measure_type in ["13GHz", "17GHz"]:
    #     options = {"cmd": cmd, **recording_info}
    #     record_measurement(num_records=num_record_, foldername="/mnt/usb/radar_data/", measure_number=1, options=options)

    elif measure_type == "13GHz":
        options = {"cmd": cmd, **recording_info}
        record_measurement(num_records=num_record_, foldername="/mnt/usb/radar_data/", measure_number=1, options=options)        
        data1 = fetch_radar_data(cmd)['data'][0]
        data2 = [0] * len(data1)  # Placeholder pour 17 GHz

    elif measure_type == "17GHz":
        options = {"cmd": cmd, **recording_info}
        record_measurement(num_records=num_record_, foldername="/mnt/usb/radar_data/", measure_number=1, options=options)
        #amp_17ghz, dist_17ghz = process_data(data2['data'][0])
        data2 = fetch_radar_data(cmd)['data'][1]
        data1 = [0] * len(data2)  # Placeholder pour 13 GHz
#     elif measure_type == "13GHz":
#         
#         options = {
#         "cmd": cmd,
#         "site_name": '',  # Placeholder values
#         "measure_id": '',
#         "polarization": '',
#         "additional_info": ""
#         }
#         options.update(recording_info)
#         print(options)
#         print('allo')
#         record_measurement(num_records=num_record_, foldername="/mnt/usb/radar_data/", measure_number=1, options=options)   
# 
#     elif measure_type == "17GHz":
#         
#         options = {
#         "cmd": cmd,
#         "site_name": '',  # Placeholder values
#         "measure_id": '',
#         "polarization": '',
#         "additional_info": ""
#         }
#         options.update(recording_info)
#         print(options)
#         record_measurement(num_records=num_record_, foldername="/mnt/usb/radar_data/", measure_number=1, options=options)   
    # Display completion message

    draw.rectangle((0, 0, 128, 64), fill=1)  # Clear screen
    draw.text((5, 20), "Measurement Done", font=font, fill=0)
    display_image(image)
    time.sleep(2)
    #return filename
        
    print(f"Measurement for {measure_type} complete.")
    # 🟢 5. EXTRAIRE & AFFICHER LES GRAPHES RADAR

    #if measure_type in ["Both", "13GHz"]:
    graph_image = generate_graph_image(data1, data2)
    display_image(graph_image)

    # if measure_type == "Both":

    #     data1 = fetch_radar_data(cmd[0])
    #     amp_13ghz, dist_13ghz = process_data(data1['data'][0])
    #     amp_13ghz = scale_data(amp_13ghz, 5, 55)
    #     data2 = fetch_radar_data(cmd[1])
    #     amp_17ghz, dist_17ghz = process_data(data2['data'][0])
    #     amp_17ghz = scale_data(amp_17ghz, 70, 123)

    # elif measure_type == " 13GHz":
    #     data1 = fetch_radar_data(cmd)
    #     amp_13ghz, dist_13ghz = process_data(data1['data'][0])
    #     amp_13ghz = scale_data(amp_13ghz, 5, 55)

    # elif measure_type == "17GHz":
    #     data2 = fetch_radar_data(cmd)
    #     amp_17ghz, dist_17ghz = process_data(data2['data'][0])
    #     amp_17ghz = scale_data(amp_17ghz, 70, 123)

    # image = Image.new('1', (128, 64), 1)
    # draw = ImageDraw.Draw(image)

    # draw.text((5, 2), "13GHz", fill=0)
    # draw.text((70, 2), "17GHz", fill=0)
    # draw.text((5, 55), "Press OK to return", font=small_font, fill=0)

    # if measure_type in ["Both", "13GHz"]:
    #     for i in range(len(dist_13ghz) - 1):
    #         draw.line((amp_13ghz[i], dist_13ghz[i] + 10, amp_13ghz[i+1], dist_13ghz[i+1] + 10), fill=0)

    # if measure_type in ["Both", "17GHz"]:
    #     for i in range(len(dist_17ghz) - 1):
    #         draw.line((amp_17ghz[i], dist_17ghz[i] + 10, amp_17ghz[i+1], dist_17ghz[i+1] + 10), fill=0)

    # display_image(image)

    # 🟢 6. ATTENDRE QUE "OK" SOIT PRESSÉ
    while True:
        action = wait_for_button()
        if action == "OK":
            break

# === Function to Draw the Menu ===
def draw_menu():
    """
    Draws the menu on the LCD screen.
    """
    global last_filename  # Access the last filename
    
    image = Image.new('1', (128, 64), 1)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
#     current_time = time.strftime("%H:%M")
#     current_date = time.strftime("%Y/%m/%d")
    
    for i, menu in enumerate(menu_structure):
        highlight = i == selected_menu
        option_text = "".join(menu["options"]) if isinstance(menu["options"], list) else menu["options"]

        # Center the text for "Measurement"
        if menu["title"] == "Measurement":
            #text_x = (128 - font.getsize(menu["title"])[0]) // 2
            #text = menu["title"]
            text_x = 5
            text = menu["title"]
            time_x = 95
            draw.text((time_x, i * 12), current_time, font=font, fill=0)
            
        elif menu["title"] == "Pol":
            #text_x = (128 - font.getsize(menu["title"])[0]) // 2
            #text = menu["title"]
            text_x = 5
            text = f"{menu['title']}: {option_text}"
            time_x = 68
            draw.text((time_x, i * 12), current_date, font=font, fill=0)
            
        else:
            text = f"{menu['title']}: {option_text}"
            text_x = 5

        # Highlight the selected option
        if highlight:
 
            if menu_structure[i]['title'] == 'Measurement':
                draw.rectangle((0, i * 12, 72, (i + 1) * 12), fill=0)  # Black background
                draw.text((text_x, i * 12), text, font=font, fill=1)
                #draw.text((time_x, i * 12), current_time, font=font, fill=1)
                
            elif menu_structure[i]['title'] == 'Pol':
                draw.rectangle((0, i * 12, 50, (i + 1) * 12), fill=0)  # Black background

                draw.text((text_x, i * 12), text, font=font, fill=1)
                #draw.text((time_x, i * 12), current_date, font=font, fill=1)
                
            else:
                draw.rectangle((0, i * 12, 128, (i + 1) * 12), fill=0)
                draw.text((text_x, i * 12), text, font=font, fill=1)# White text
                
             
        else:
            draw.text((text_x, i * 12), text, font=font, fill=0)  # Black text

    # Add an underline effect for character editing
    if edit_mode:
        menu = menu_structure[selected_menu]
        
        if menu["title"] == "Site name":
            char_x = 70 + (edit_position * 6)
            bar_y = (selected_menu * 12) + 10
            draw.line((char_x, bar_y, char_x + 6, bar_y), fill=1, width=1)
            
        elif menu["title"] == "Measure #":
            char_x = 70 + (edit_position * 6)
            bar_y = (selected_menu * 12) + 10
            draw.line((char_x, bar_y, char_x + 12, bar_y), fill=1, width=1)
    
        elif menu["title"] == "Angle":
            char_x = 46 + (edit_position * 6)
            bar_y = (selected_menu * 12) + 10
            draw.line((char_x, bar_y, char_x + 6, bar_y), fill=1, width=1)
            
        
    return image

# 


# === Function to Handle Menu Navigation ===
def menu_navigation(radar1,radar2):
    """
    Handles the main menu navigation.
    """
    global selected_menu, edit_mode, edit_position, current_time, current_date
    
    cmd1 = radar1[1]
    cmd2 = radar2[1]

    while True:
        img = draw_menu()
        display_image(img)
        action = wait_for_button(timeout=1.0)
        
        if action is None:
            # No button was pressed, update the time and refresh the menu
            new_time = time.strftime("%H:%M")
            
            if new_time != current_time:  # Only update if the time changed
                current_time = new_time
                current_date = time.strftime("%Y/%m/%d")
                #display_image(draw_menu())

        elif action == "UP":
            selected_menu = (selected_menu - 1) % len(menu_structure)
            
        elif action == "DOWN":
            selected_menu = (selected_menu + 1) % len(menu_structure)
            
        elif action == "OK":
            
            if menu_structure[selected_menu]['title'] == 'Measurement':
                measurement_result = measurement_menu(cmd1,cmd2, last_filename)
                
                if measurement_result:
                    menu_values["Measurement"] = measurement_result
                    
            else:
                edit_mode = True
                edit_position = 0
                #refresh_enabled = False  # Stop auto-refresh while editing
                edit_menu()
                #refresh_enabled = True  # Resume auto-refresh after editing
                
        elif action == "CANCEL":
            return


# === Function to Edit Menu Options ===
def edit_menu():
    """
    Handles editing of menu options.
    """
    global edit_mode, edit_position

    while edit_mode:
        menu = menu_structure[selected_menu]
        img = draw_menu()
        display_image(img)
        action = wait_for_button()

        if menu["type"] == "chars":
            # Character selection (4-character input)
            char_to_edit = menu['options'][edit_position]
            
            if char_to_edit not in CHARACTERS:
                char_to_edit = 'A'
                
            index = CHARACTERS.index(char_to_edit)
            
            if action == "UP":
                index = (index + 1) % len(CHARACTERS)
                
            elif action == "DOWN":
                index = (index - 1) % len(CHARACTERS)
                
            elif action == "OK":
                edit_position += 1
                index = 0
                
                if edit_position >= 4:
                    edit_mode = False
                    
            elif action == "CANCEL":
                edit_mode = False
                
            if edit_mode:
                menu["options"][edit_position] = CHARACTERS[index]

        elif menu["type"] == "digits":
            # Single-step selection for 01-99
            index = int("".join(menu["options"]))  # Convert to integer
            
            if action == "UP":
                #index = index + 1 if index < 99 else 1  # Wrap from 99 to 01
                index = index + 1 if index < 99 else 0 # Wrap from 99 to 01
                
            elif action == "DOWN":
                #index = index - 1 if index > 1 else 99  # Wrap from 01 to 99
                index = index - 1 if index > 0 else 99  # Wrap from 01 to 99
            elif action == "OK":
                edit_mode = False
                
            elif action == "CANCEL":
                edit_mode = False
                
            if edit_mode:
                menu["options"] = f"{index:02d}"  # Format as two-digit string

        elif menu["type"] == "choice":
            # Toggle between V and H
            if action in ["UP", "DOWN"]:
                menu["options"] = "H" if menu["options"] == "V" else "V"
                
            elif action == "OK":
                edit_mode = False
                
            elif action == "CANCEL":
                edit_mode = False

        elif menu["type"] == "numbers":
            # Character selection (4-character input)
            num_to_edit = menu['options'][edit_position]
            
            if num_to_edit not in NUMBERS:
                num_to_edit = '0'
                
            index = NUMBERS.index(num_to_edit)
            
            if action == "UP":
                index = (index + 1) % len(NUMBERS)
                
            elif action == "DOWN":
                index = (index - 1) % len(NUMBERS)
                
            elif action == "OK":
                edit_position += 1
                index = 0
                
                if edit_position >= 2:
                    edit_mode = False
                    
            elif action == "CANCEL":
                edit_mode = False
                
            if edit_mode:
                menu["options"][edit_position] = NUMBERS[index]
        # Update stored menu values
        menu_values[menu["title"]] = "".join(menu["options"]) if isinstance(menu["options"], list) else menu["options"]


# === Function for Measurement Selection Menu ===
def measurement_menu(cmd1,cmd2,last_filename="No measurement yet"):
    """
    Displays a submenu for measurement type selection.
    """
    measurement_options = ["Both", "13GHz", "17GHz"]
    selected_measurement = 0

    while True:
        # Create an image for the menu
        image = Image.new('1', (128, 64), 1)
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        text_x = (128 - font.getsize("Measurement")[0]) // 2
        small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 8)  
        
        # Display menu title
        #draw.text((40, 10), "Measurement", font=font, fill=0)
        draw.text((text_x, 10), "Measurement", font=font, fill=0)
        # Display measurement options
        for i, option in enumerate(measurement_options):
            highlight = i == selected_measurement
            text_x = (128 - font.getsize(option)[0]) // 2  # Center text
            
            if highlight:
                draw.rectangle((0, 20 + i * 12, 128, 32 + i * 12), fill=0)
                draw.text((text_x, 20 + i * 12), option, font=font, fill=1)
                
            else:
                draw.text((text_x, 20 + i * 12), option, font=font, fill=0)
                
        draw.rectangle((0, 54, 128, 64), fill=1)  # Black background
        draw.text((5, 55), f"Last: {last_filename}", font=small_font, fill=0)  # White text

        display_image(image)
        action = wait_for_button()

        if action == "UP":
            selected_measurement = (selected_measurement - 1) % len(measurement_options)
            
        elif action == "DOWN":
            selected_measurement = (selected_measurement + 1) % len(measurement_options)
            
        elif action == "OK":
        
            if measurement_options[selected_measurement] == 'Both':
                take_measurement((cmd1, cmd2), menu_structure, measure_type=measurement_options[selected_measurement])
            elif measurement_options[selected_measurement] == '13GHz':
                print('selected 13GHz')
                take_measurement(cmd1, menu_structure, measure_type=measurement_options[selected_measurement])
            elif measurement_options[selected_measurement] == '17GHz':
                take_measurement(cmd2, menu_structure, measure_type=measurement_options[selected_measurement])
            print(menu_structure)
            print(measurement_options[selected_measurement])
            return 
            #return measurement_options[selected_measurement]  # Return the selected option
        
        elif action == "CANCEL":
            return None  # Return to the main menu
