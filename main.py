import time
from lcd_display import init_display, display_welcome_screen
from menu import menu_navigation
from buttons import init_buttons

def main():
    # Initialisation de l'écran LCD et affichage du logo d'accueil
    init_display()
    #display_welcome_screen("Loading...")
    radar1, radar2 = display_welcome_screen()
    # Initialisation des boutons
    init_buttons()

    # Lancer la navigation dans le menu
    menu_navigation(radar1, radar2)

    print("Programme terminé")

if __name__ == "__main__":
    main()
