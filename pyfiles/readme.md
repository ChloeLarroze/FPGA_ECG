## Fonctionnement du fichier Python

Ce fichier définit une classe `FPGA` permettant d'interagir avec une FPGA via une liaison UART. 

- **Initialisation (`__init__`)** : Configure les paramètres de la liaison UART (port, baud rate, parité, stop bits, etc.).
- **Ouverture et fermeture de la connexion (`open_instrument`, `close_instrument`)** : Gère l'ouverture et la fermeture du port série.
- **Écriture et lecture en mémoire FPGA** :
  - `set_memory_addr(addr)`: Définit une adresse mémoire.
  - `write_val_mem(value)`: Écrit une valeur en mémoire.
  - `read_mem_val(addr)`: Lit une valeur à une adresse mémoire donnée.
- **Affichage sur les LEDs (`display_mem_vals_leds(addr)`)** : Demande à la FPGA d'afficher une valeur stockée en mémoire sur ses LEDs.

Le programme principal établit la connexion UART, envoie des commandes à la FPGA et lit des données avant de fermer proprement la connexion.

Par ailleurs, on ajoute une méthode `send_command()` qui ajoute un caractère de fin de ligne (\n) à la commande, envoie la commande encodée en bytes via UART et attend une réponse et la retourne après décodage, elle sert ensuite dans chacune des méthodes ( qui correspondent à une commande précise que nous avons codé)

---
Dans ce script, la bibliothèque `pyserial` est utilisée pour gérer cette communication via un port série, permettant d'envoyer des commandes sous forme de chaînes de caractères encodées en UTF-8.


On effectue donc les actions suivantes dans le code : 
- mettre la valeur de la mémoire à 0x00
- On écrit la valeur 0xF5 dans la mémoire à l'adresse indiquée
- On allume les leds correspondant à la valeur 
- On lit en retour la valeur avec la commande R


