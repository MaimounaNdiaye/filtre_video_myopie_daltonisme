import numpy as np
import cv2 as cv

# Qualité d'image choisit : 640x360
# URL obtenue grace à l'application (android) IP Webcam
IP = "192.168.1.79"
PORT = "8080"
URL= f"http://{IP}:{PORT}/video"

# Obtenir sigma en fonction de la dioptrie (correction du patient)
def get_sigma(diopter=-2):
    if (diopter < 0):
        return -6.921 * diopter + 0.0642 - 1
    else:
        return 0
    
# Obtenir la carte de profondeur
def get_depth_map(image, kernel_size=15):
    # Convertir l'image en niveaux de gris
    gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    
    # Calculer le laplacien de l'image en niveau de gris
    laplacian = cv.Laplacian(gray_image, cv.CV_64F)
    
    # Flouter le laplacien
    blurred_laplacian = cv.GaussianBlur(laplacian, (kernel_size, kernel_size), 0)
    
    # Normaliser le résultat
    normalized_depth_map = cv.normalize(blurred_laplacian, None, 0, 255, cv.NORM_MINMAX, dtype=cv.CV_8U)/100
    
    return normalized_depth_map

# Filtre de myopie
def myopie(im, diopter=-2):
    sigma = get_sigma(diopter) # obtention de sigma
    
    # Creating de la matrice de convolution / kernel
    sigma = int(sigma)  

    # Dimension du kernel
    if(sigma % 2 == 0):
        kernel_dim = sigma + 1
    else:
        kernel_dim = sigma
    
    max_blur_radius = kernel_dim

    # Création de la carte de profondeur
    depth_map = get_depth_map(im, kernel_dim)

    # Calculer le rayon de flou de chaque pixel en fonction de la carte de profondeur
    blur_radius = (1 - depth_map) * max_blur_radius

    # Création d'un kernel customisé prenant en compte la profondeur
    kernel_size = kernel_dim
    depth_aware_kernel = np.zeros((kernel_size, kernel_size), dtype=np.float32)
    for i in range(kernel_size):
        for j in range(kernel_size):
            radius = int(blur_radius[i, j])
            if (radius==0):
                radius=0.00001
            depth_aware_kernel[i, j] = np.exp(-0.5 * (i ** 2 + j ** 2) / (radius ** 2))

    # normaliser le kernel
    depth_gaussian_mask = depth_aware_kernel / np.sum(depth_aware_kernel)

    # Remplissage de la bordure de l'image
    pad_size = (5,5,5,5)  # Largeur de remplissage
    padded_im = cv.copyMakeBorder(im, *pad_size, cv.BORDER_REPLICATE) 
    # application du filtre à travers le produit de convolution
    frame = cv.filter2D(padded_im, -1, depth_gaussian_mask)
    # Rogne l'image pour enlever les bordures ajoutées avant
    cropped_frame = frame[4:-6, 4:-6]  

    return cropped_frame

diopter = -1.5 # Degré de myopie la valeur doit être négative (prescription du patient)

# Accède au flux vidéo à travers l'URL pour la capture vidéo
cap = cv.VideoCapture(URL)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

k=0 # utilisé pour ne traiter que une image sur 3
while True:
    ret, frame = cap.read() # Capture l'image 
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break
    
    # Réduit le nombre d'images traitées (1/3)
    if (k%3==0):
        frame = myopie(frame, diopter) # applique le filtre à l'image
        
        # Agrandis la fenêtre de diffusion du résultat
        ratio = 200
        largeur = int(frame.shape[1] * ratio / 100)
        hauteur = int(frame.shape[0] * ratio / 100)
        dimension = (largeur, hauteur)
        frame=cv.resize(frame,dimension, interpolation = cv.INTER_AREA)
        
        # affiche l'image traitée
        cv.imshow('frame', frame)
    k+=1    

    if cv.waitKey(1) & 0xFF == ord('s'):
        print('text')
    if cv.waitKey(1) == ord('q'): # il faut appuyer sur 'q' pour arreter le programme
        break

cap.release()
cv.destroyAllWindows()

