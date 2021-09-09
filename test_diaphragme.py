# -*- coding: utf-8 -*-
"""test_diaphragme.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rzY1k0n7uMCdzhgvxFMrjTEDpSsmmkZA

# Script exemple pour utiliser le réseau

Ce notebook a été conçu pour les données matlab de la forme (N,C,H,W,T), où


           N : la taille du lot c'est-à-dire le nombre d'images,
           C : nombre de canaux,
           H : hauteur de l'image,
           W : largeur de l'image,
           T : le temps en ms ici,

Exemple : une donnée de la forme (1, 1, 300, 300, 500)
signifie que c'est une image en nuance de gris car C = 1 (C = 3 donc en couleurs RGB) de taille 300x300 sur 500ms.

L'abréviation npy renvoie à numpy qui sont équivalents aux arrays dans matlab.

Les bibliothéques suivantes sont nécessaires au bon fonctionnement de ce notebook.
"""

import os                                 # pour manipuler et aller chercher les fichiers
import numpy as np                        # pour effectuer des opérations sur les array/tableaux
import matplotlib.pyplot as plt           # pour visualiser les images
import torch                              # pour construire le modèle de réseaux de neurones 
from scipy import ndimage                 # pour effectuer des rotations images
from torch.autograd import Variable       # pour transformer les tableaux numpy en tensors avec gradient
from torch.optim import Adam              # pour optimiser la fonction perte
from sklearn.model_selection import train_test_split, KFold # pour scinder les données en apprentissage et test
from torchsummary import summary          # pour avoir un aperçu du réseau et des paramètres 
import cv2                                # bibliothèque de traitement d'images
import time                               # calculer le temps de calcul
from skimage import img_as_float, exposure # augmente le contraste
import scipy.io

"""### Connexion avec le drive pour les data :"""

# Importation avec le compte drive
from google.colab import drive
drive.mount('/content/drive')

# pour savoir si je suis en gpu ou cpu le gpu accélère le calcul lors de la phase entraînement
# l'activer aller dans modifier -> param. notebook
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
print(device)

"""### Importation (en local) du fichier qui regroupe les fonctions nécessaires :"""

# importe le notebook qui regroupe toutes les fonctions nécessaires au traitement 
from google.colab import files
uploaded = files.upload()
for file in uploaded:
  print("file name : {} , length: {}".format(file,len(file)))

# Il existe différentes manières d'importer :
# Méthode 1 : import diaph_segmentation dans ce cas je dois écrire diaph_segmentation.
# avant chaque fonction par exemple diaph_segmentation.matlab_to_numpy(path)
# Méthode 2 : from diaph_segmentation import matlab_to_numpy dans ce cas je n'ai importé 
# que la matlab_to_numpy on peut aussi en appeler plusieurs d'affilée comme ceci
# from diaph_segmentation import matlab_to_numpy, numpy_to_tensor juste avec une virgule entre 2
# Méthode 3 : from diaph_segmentation import * dans ce cas j'ai tout importé comme ci-dessous
from diaph_segmentation import *

"""### Conversion données matlab en numpy :"""

# cette fonction prend en entrée un chemin de données matlab et renvoie un tableau 
# stocké dans une structure npy de plus la fonction télécharge automatiquement 
# la structure npy dans un dossier 'Data numpy' à toi de choisir ton chemin
path = '/content/drive/MyDrive/Colab Notebooks/Data matlab'
bmode = matlab_to_numpy(path)
print(bmode.shape)

# Vérifier si la forme des données est comme expliqué au-dessus
for i in range(len(bmode)):
  print(bmode[i].shape)

"""### Conversion données numpy en tensor :"""

# cette fonction prend en entrée un chemin de données npy et renvoie un tableau npy
# qui stocke un/des tensor de plus la fonction effectue un un pré-traitement en divisant
# par 255 si les pixels ne sont pas compris entre [0, 1] et aussi elle transforme 
# les images b-mode en m-mode 
path = '/content/drive/MyDrive/Colab Notebooks/Data numpy/bmode.npy'
mmode = numpy_to_tensor(path)
mmode.shape

for i in range(len(mmode)):
  print(mmode[i].size())

"""### Modèle sans les paramètres entraînés :"""

# ici on charge la structure du model ce sur quoi les paramtères vont pouvoir 
# "s'accrocher" pour faire tourner le modèle donc ici le modèle n'est pas entrainé
# mais juste initialisé
model = U_Net().to(device)
image = model(mmode[0][:,:,:,:300])
plt.imshow(image[0,0].detach().numpy())

model = U_Net().to(device)
for i in range(len(mmode)):
  image = model(mmode[i])
  plt.imshow(image[0,0].detach().numpy())
  plt.pause(1e-99)

"""### Modèle avec les paramètres entraînés :"""

# le chemin désigne l'endroit où sont stockées les poids 
path = '/content/drive/MyDrive/Colab Notebooks/Data/Weights/model_Unet_25.pth'
initialize_parameters(U_Net(), path)
image = model(mmode[0][:,:,:,:300])
plt.imshow(image[0,0].detach().numpy())

path = '/content/drive/MyDrive/Colab Notebooks/Data/Weights/model_u_net5.pth'
initialize_parameters(U_Net(), path)
for i in range(len(mmode)):
  image = model(mmode[i])
  plt.imshow(image[0,0].detach().numpy())
  plt.pause(1e-99)

img = image
mask = torch.load('/content/drive/MyDrive/Colab Notebooks/Data/mode228.pt')
alpha = 0.3                           # paramètres qui gère la transparence de l'image 
beta = 0.9                            # paramètres qui gère la transparence du mask
gam = 0.0                             # paramètres qui ajoute une valeur à chaque pixel
sp1, sp2 = superposition(img, mask, alpha, beta, gam) # sp1 désigne la sortie avec mask plein sp2 avec le mask ligne
for i in range(len(mmode)):
  image = model(mmode[i])
  plt.imshow(sp2[0])
  plt.pause(1e-99)

scipy.io.savemat('test.mat', sp2) # télécharge en fichier .mat