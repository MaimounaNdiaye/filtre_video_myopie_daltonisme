import cv2 as cv

# Qualité d'image choisit : 352x288
# URL obtenue grace à l'application(android) IP Webcam
IP = "192.168.1.79"
PORT = "8080"
URL= f"http://{IP}:{PORT}/video"

# Pour choisir le type de daltonisme 
type = "di"    #'di', 'mono' ou 'tri'
color = 'b'    #'r', 'g' ou 'b' 
# pour : pourcentage de daltonisme pour cas trichrome
# Plus 'pour' est proche de 100 plus la vision est normale
pour = 25

# Appelle la fonction correspondante au trouble visuel choisi
def daltonisme(frame, type, color='r', percentage=100):
    if(type == "mono"):
        return monochrome(frame)
    if(type == "di"):
        return dichrome(frame, color)   
    if(type == "tri"):
        return trichrome(frame, color, percentage) 

# Filtre pour la vision en noir et blanc (monochromatisme)
def monochrome(frame):
    #le tableau de l'image n'est pas dans le sens RGB mais BGR
    #crée les tableaux rouge, vert et bleu
    red = frame[:,:,2] 
    green = frame[:,:,1]
    blue = frame[:,:,0]
    chrome = red

    for i in range (len(red) -1):
            for j in range (len(red[0])-1):
                chrome[i,j] = 0.299 * red[i,j] + 0.587 * blue[i,j] + 0.114 * green[i,j]
    return chrome

# Filtre pour l'incapacitée de voir le rouge, le vert ou le bleu totalement
def dichrome(frame, color):
    red=frame[:,:,2]
    green=frame[:,:,1]
    blue=frame[:,:,0]
        
    if(color == 'r'):
        # red = 1.05 * green - 0.05 * blue : Protanopie
        for i in range (len(green) -1):
            for j in range (len(green[0])-1):
                f1=1.05*green[i,j]-0.05*blue[i,j]
                # Si la valeur n'est pas dans l'intervalle [0, 255], elle n'est pas adaptée
                if (0<=f1 and f1<=255):
                    frame[i,j,2]=f1
                elif(f1>0):
                    frame[i,j,2]=255 
                elif(f1<255):
                    frame[i,j,2]=0
                    
    elif(color == 'g'):
        # green = 0.95 * red  + 0.05 * blue : Deutéranopie
        for i in range (len(red) -1):
            for j in range (len(red[0])-1):
                frame[i,j,1]=0.95*red[i,j]+0.05*blue[i,j]

    elif(color == 'b'):
        # Blue = 2.3 * green – 0.6 * red : Tritanopie
        for i in range (len(green) -1):
            for j in range (len(green[0])-1):
                f1=2.3*green[i,j]-0.6*red[i,j]
                if (0<=f1 and f1<=255):
                    frame[i,j,0]=f1
                elif(f1>0):
                    frame[i,j,0]=255 
                elif(f1<255):
                    frame[i,j,0]=0
        
    return frame

# Filtre pour l'incapacitée de voir le rouge, le vert ou le bleu partiellement
def trichrome(frame, color, percentage):
    inverse_per = 100 - percentage
    red = frame[:,:,2] 
    green = frame[:,:,1]
    blue = frame[:,:,0]

    # Modiffie le tableau de l'image en fonction de la formule
    if(color == 'r'):
        for i in range (len(green) -1):
            for j in range (len(green[0])-1):
                f1=red[i,j] * percentage/100 + (1.05 * green[i,j] - 0.05 * blue[i,j])*inverse_per/100
                if (f1<255):
                    frame[i,j,2]=f1
                else:
                    frame[i,j,2]=255
    
    elif(color == 'g'):
        for i in range (len(red) -1):
            for j in range (len(red[0])-1):
                frame[i,j,1]=green[i,j] * percentage/100 +(0.95*red[i,j]+0.05*blue[i,j])*inverse_per/100
    
   
    elif(color == 'b'):
        for i in range (len(green) -1):
            for j in range (len(green[0])-1):
                f1= blue[i,j] * percentage/100 + (2.3*green[i,j]-0.6*red[i,j])*inverse_per/100
                if(f1<255):
                    frame[i,j,0]=f1
                else:
                    frame[i,j,0]=255
    
    return frame

# Accède au flux vidéo à travers l'URL pour la capture vidéo
cap = cv.VideoCapture(URL)
if not cap.isOpened():
    print("Cannot open camera")
    exit()

k=0 # utilisée pour ne traiter que une image sur 10
while True:
    # Capture l'image 
    ret, frame = cap.read()
    if not ret:
        print("Can't receive frame (stream end?). Exiting ...")
        break

    # Réduit le nombre d'images traitées (1/10)
    if (k%10==0):
        frame = daltonisme(frame,type, color , pour) # applique le filtre à l'image

        # Agrandis la fenêtre de diffusion du résultat
        ratio = 200
        largeur = int(frame.shape[1] * ratio / 100)
        hauteur = int(frame.shape[0] * ratio / 100)
        dimension = (largeur, hauteur)
        frame=cv.resize(frame,dimension, interpolation = cv.INTER_AREA)
        
        # Affiche l'image traitée
        cv.imshow('frame', frame)
    k=k+1 

    if cv.waitKey(1) & 0xFF == ord('s'): 
            print('text')
    if cv.waitKey(1) == ord('q'): # il faut appuyer sur 'q' pour arreter le programme
        break

cap.release()
cv.destroyAllWindows()

