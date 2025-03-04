import numpy as np
import cv2 as cv

# Qualité d'image choisit : 640x360
# URL obtenue grace à l'application (android) IP Webcam
IP = "192.168.244.202"
PORT = "8080"
URL= f"http://{IP}:{PORT}/video"

# Cylindre: degrée d'astigmatisme mesuré en dioptrie (variable diopter)
# Axe (entre 0° et 180°): Direction du flou (variable axis_angle)

# Filtre d'astigmatisme
def astigmatism(image, diopter=-2, axis_angle=0):
    sigma = abs(diopter)
    
    # Determine sigma_x et sigma_y en fonction de la direction
    if axis_angle == 0: # Astigmatisme horizontal
        sigma_x = sigma
        sigma_y = sigma * 5  
    elif axis_angle == 90: # Astigmatisme vertical
        sigma_x = sigma * 5 
        sigma_y = sigma
    else:
        sigma_x = sigma * np.cos(np.deg2rad(axis_angle)) * 5
        sigma_y = sigma * np.sin(np.deg2rad(axis_angle)) * 5
    
    # Taille du noyau en fonction de sigma
    size = max(int(max(sigma_x, sigma_y) * 3) // 2 * 2 + 1, 3)
    # print(f"kernel size: {size}")
    
    # Crée une grille de coordonnées utilisée pour créer le noyau
    x = np.linspace(-size // 2 + 1, size // 2, size)
    y = np.linspace(-size // 2 + 1, size // 2, size)
    x, y = np.meshgrid(x, y)
    
    # Création du kernel
    kernel = np.exp(-(x**2 / (2 * sigma_x**2) + y**2 / (2 * sigma_y**2)))
    
    # Normalisation du kernel
    kernel /= np.sum(kernel)

    # Remplissage des bords
    pad_size = (5,5,5,5)
    padded_im = cv.copyMakeBorder(image, *pad_size, cv.BORDER_REPLICATE)

    # application du filtre à travers le produit de convolution
    im = cv.filter2D(padded_im, -1, kernel) 

    return im

axis_angle = 90  # Direction en degrees (0 pour horizontal, 90 pour vertical)
# Degré d'astigmatisme
diopter = -1

# Accède au flux vidéo à travers l'URL pour la capture vidéo
cap = cv.VideoCapture(1)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

k = 0  # utilisé pour ne traiter que une image sur 3
while True:
    ret, frame = cap.read() # Capture l'image 
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    # Réduit le nombre d'images traitées (1/3)
    if (k%3==0):
        frame = astigmatism(frame, diopter) # applique le filtre à l'image
        cv.imshow('frame', frame) # affiche l'image traitée
   
    if cv.waitKey(1) & 0xFF == ord('s'):
        print('text')
    if cv.waitKey(1) == ord('q'): # il faut appuyer sur 'q' pour arreter le programme
        break
        
cap.release()
cv.destroyAllWindows()
