# -*- coding: utf-8 -*-
"""PEEK_BackEnd.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1jsRBJDOPqXYc9n1qlBiNmftHj2szUWVH

# Librerías
"""

# Commented out IPython magic to ensure Python compatibility.
###### Importación de librerías necesarias para el uso de PÉEK   #######
!ln -sf /opt/bin/nvidia-smi /usr/bin/nvidia-smi
!pip install gputil # GPUtil es un módulo de Python para obtener el estado de la GPU de NVIDA utilizando nvidia-smi
!pip install psutil # psutil es una módulo para recuperar información sobre los procesos en ejecución y la utilización
			              # del sistema (CPU, memoria, discos, red, sensores) en Python.
!pip install py-ecg-detectors # ECG Detectors es un módulo con funciones para el reconocimiento de picos R en un ECG
				                      # basados en los métodos de detección den mayor porcentaje y probados en la base de datos
				                      # MIT-BIH

# Utilidades
import time
import psutil
# %matplotlib inline

# Funciones para el procesamiento de la imagen y arreglos numéricos
import io
from PIL import Image
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import tensorflow as tf
import cv2
import cv2 as cv

# Funciones requeridas para el manejo del modelo y la imagen
import keras
from keras.preprocessing import image
from keras.applications.imagenet_utils import preprocess_input
from keras.models import Sequential
from keras.layers import Dense, Dropout, Flatten, Activation
from keras.layers import Conv2D, MaxPooling2D
from keras.models import Model
from keras import utils as np_utils 

# Función para
from ecgdetectors import Detectors

# Librería y funciones requeridas para el manejo de medios y conexión con Anvil
!pip install anvil-uplink
import anvil.server
import anvil.media
import anvil.tables as tables
from anvil.tables import app_tables
import anvil.media

"""# Obtener categorías"""

!ls /content/drive/MyDrive/AlexanderTesis/2021-1/Datasets/Image/Derivations/MLII

root = '/content/drive/MyDrive/AlexanderTesis/2021-1/Datasets/Image/Derivations/MLII'
exclude = ['Prueba']
train_split, val_split = 0.7, 0.15

categories = [x[0] for x in os.walk(root) if x[0]][1:]
categories = [c for c in categories if c not in [os.path.join(root, e) for e in exclude]]

print(categories)

"""# Conexión con Interfaz Gráfica"""

# Conexión cliente-servidor mediante el Anvil-Uplink ID
anvil.server.connect("G4SKKTLX4IJI2P45FWMBJK3J-7I6IYR6U2OJCTQUL")

"""# Obtener modelo"""

# Se clonan los parámetros y pesos del modelo previamente entrenado y almacenado en una dirección
model = keras.models.load_model('/content/drive/MyDrive/AlexanderTesis/2021-1/Datasets/model210821.h5')

"""# Procesamiento"""

####### Cargar imagen de ECG ############

@anvil.server.callable    # Esta línea define a la función como "llamable por Anvil"
def Upload_ECG(orECG, FqM, FST):

  #Transforma el archivo tipo multimedia de Anvil en formato CSV para leerlo con Pandas 
  with anvil.media.TempFile(orECG) as f:
    ECGv = pd.read_csv(f) # Vector a partir del archivo CSV

  # Si FST = 1, significa que la variable FqM se trata de ua Frecuencia de muestreo; de lo contrario,
  # se calcula la Frecuencia de muestreo en base a la duración del trazo ECG y el número de muestras.
  if FST == 1:
    FqM=int(FqM)
  if FST == 2:
    FqM=int(FqM)/len(ECGv)

  # Se multiplica la Frecuencia de muestreo por 20 para obtener el total de muestras en 20 segundos.
  TwSec=FqM*20
  t=np.arange(TwSec)

  # Se calcula el número de renglones que tendrá la imagen del reporte ECG que se mostrará en pantalla.
  Rows=int(len(ECGv)/TwSec) 
  Wrow=np.arange(Rows)

  ### Separar el trazo por segmentos de 20 segundos y mostrarlo en un plot ###
  for j in Wrow:
    ECGf = plt.figure()
    ECGf, axes = plt.subplots(figsize=(120,6))
    plt.axis('off')
    axes.plot(t,ECGv[(j*TwSec):((j+1)*TwSec)])

    # Eliminar los espacios blancos del plot
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())

    # Guardar plot en imagen y eliminar plot para la liberar RAM utilizada
    ECGf.savefig('/content/Ventana_'+str(j)+'.png',bbox_inches='tight', pad_inches=0)
    ECGf.clf() 
    plt.clf()
    plt.cla()
    plt.close()
    ECGf=plt.close()


  # Generar imagen del último renglón/segmento del ECG con una linea recta en el espacio vacío
  ECGtail=(ECGv[(Rows*TwSec):(len(ECGv))]).to_numpy()
  ECGtail=np.transpose(ECGtail)[0]
  DTz=np.zeros((TwSec-((len(ECGv))-(Rows*TwSec))))
  DTz=DTz+np.mean(ECGtail)
  ECGwhite=np.concatenate((ECGtail,DTz))
  ECGf = plt.figure()
  ECGf, axes = plt.subplots(figsize=(120,6))
  plt.axis('off')
  axes.plot(t,ECGwhite)

  # Eliminar los espacios blancos del plot
  plt.gca().set_axis_off()
  plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
  plt.margins(0,0)
  plt.gca().xaxis.set_major_locator(plt.NullLocator())
  plt.gca().yaxis.set_major_locator(plt.NullLocator())

  # Guardar plot en imagen y liberar RAM
  ECGf.savefig('/content/Ventana_'+str(Rows)+'.png',bbox_inches='tight', pad_inches=0)
  ECGf.clf()
  plt.clf()
  plt.cla()
  plt.close()
  ECGf=plt.close()

  ## Comienza la concatenación de renglones del trazo ECG ##
  ECGor = cv2.imread('/content/Ventana_0.png')
  for k in (Wrow):
    ECGadd = cv2.imread('/content/Ventana_'+str(k+1)+'.png')
    ECGor = cv2.vconcat([ECGor,ECGadd])
  
  # Tranformación del formaro array a imagen
  ECGor = Image.fromarray(ECGor, 'RGB')

  # Se almacena y se transforma a archivo multimedia Anvil como respuesta a la función Upload_ECG
  ECGor.save('/content/ECG_orig.png')
  img10 = anvil.media.from_file('/content/ECG_orig.png', "image/png")

  return  img10

####### ARRHYTMIA CLASSIFIER ############

@anvil.server.callable
def arrhyt_classifier(orECG, FqM, FST):

  # Obtiene el tiempo inicial antes del procesamiento de la imagen
  tmpo = time.time()

  #Transforma el archivo tipo multimedia de Anvil en formato CSV para leerlo con Pandas 
  with anvil.media.TempFile(orECG) as f:
    ECGv = pd.read_csv(f)

  # Si FST = 1, significa que la variable FqM se trata de ua Frecuencia de muestreo; de lo contrario,
  # se calcula la Frecuencia de muestreo en base a la duración del trazo ECG y el número de muestras.
  if FST == 1:
    FqM=int(FqM)
  if FST == 2:
    FqM=int(FqM)/len(ECGv)

  # Se multiplica la Frecuencia de muestreo por 20 para obtener el total de muestras en 20 segundos.
  TwSec=FqM*20
  t=np.arange(TwSec)

  # Se calcula el número de renglones que tendrá la imagen del reporte ECG que se mostrará en pantalla.
  Rows=int(len(ECGv)/TwSec) 
  Wrow=np.arange(Rows)

  # Vector de tiempo para 298 píxeles de imagen
  t2=np.arange(298)

  # Se transforma el arreglo de ECG a vector de 1 dimensión
  A = np.squeeze(np.asarray(ECGv))

  # Se define la frecuencia de muestreo a utilizar con el detector de picos R
  detectors = Detectors(FqM)

  # Se extraen los picos R identificados en el trazo de ECG
  r_peaks = detectors.swt_detector(A)

  # Se crea arreglo de cantidad de categorías (3) por cantidad de picos identificados
  p1=np.zeros((int(len(r_peaks)-1),len(categories)))

  # Vector de caracteres con el tamaño de la cantidad de picos identificados
  p2 = ["" for i in range(len(r_peaks)-2)]

  # Vector numérico desde el 0 hasta el número de picos identificados menos 2
  p3=np.array(range(int((len(r_peaks)-2))))

  #Recortar la imagen y recorrerla de inicio a fin
  for i in (p3):
    ECGs = plt.figure()
    ECGs, axes = plt.subplots(figsize=(2.99,2.99))
    plt.axis('off')
    axes.plot(t2,A[(r_peaks[i]-120):(r_peaks[i]+178)])
    ECGs.savefig('/content/Prf.png',bbox_inches='tight', pad_inches=0)
    img = image.load_img('/content/Prf.png', target_size=(299, 299))
    ECGs.clf()
    plt.clf()
    plt.cla()
    plt.close()
    ECGs=plt.close()
    x = np.expand_dims(img, axis=0)
    x = preprocess_input(x)

    # Un ciclo cardiaco pasa por el modelo para clasificarlo entre alguna de las categorías
    probabilities_old = model.predict([x])

    # Se almacena en una posición del vector p1
    p1[i]=probabilities_old

    # Se identifica la categoría con mayor probabilidad
    mx=max(probabilities_old[0])

    # Se almacena el resultado de la categoría a la que pertenece el ciclo cardiaco
    if probabilities_old[0,0] == mx:
      print("Normal Sinus Rythm")
      Arr="Normal Sinus Rythm"
      p2[i]="NSR"
    elif probabilities_old[0,1] == mx:
      print("Premature Ventricular Contraction")
      Arr="Premature Ventricular Contraction"
      p2[i]="PVC"
    elif probabilities_old[0,2] == mx:
      print("Other")
      Arr="Other"
      p2[i]="Other"
    else:
      print("We dont find it")
      Arr="We dont find it" 

  # Parámetros iniciales para el recorrido de los ciclos
  p2v=np.array(range(len(p2)))
  j=0
  i=0

  # Se inicia con el primer renglon del trazo ECG almacenado previamente
  img_1=cv2.imread('/content/Ventana_'+str(j)+'.png')
  (h,w,c)=img_1.shape[:3]

  # Comienza el recorrido de ciclos para marcarlos en las imágenes de 20 segundos según su categoría
  for i in p2v:     # Se recorre cada posición de pico R identificada
    if r_peaks[(i+1)] < ((j+1)*TwSec):  # Mientras no se rebasen los 20 segundos, se hará el recorrido en el renglón actual

      if p2[i]=='NSR':  # Si el ciclo actual fue clasificado como normal, marcar el texto "NSR" en la imagen
        img_2 = cv2.putText(img_1, 'NSR', (int((r_peaks[(i+1)]-(j*TwSec))/(TwSec/w)),int(1*h/8)),cv2.FONT_HERSHEY_COMPLEX , 1.5, (0, 0, 255), 2)

      if p2[i]=='PVC':  # Si el ciclo fue clasificado como PVC, marcar un recuadro en la imagen con el texto PVC
        img_2 = cv2.rectangle(img_1,(int((r_peaks[(i+1)]-(j*TwSec)-120)/(TwSec/w)),1),(int((r_peaks[(i+1)]-(j*TwSec)+178)/(TwSec/w)),int(4*h/4)),(0,0,255),2)
        img_2 = cv2.putText(img_1, 'PVC', (int((r_peaks[(i+1)]-(j*TwSec))/(TwSec/w)),int(1*h/8)),cv2.FONT_HERSHEY_COMPLEX , 1.5, (0, 0, 255), 2)

      if p2[i]=='Other':  # Si el ciclo fue clasificado como "Other" (otro), marcar un recuadro en la imagen con el texto Other
        img_2 = cv2.rectangle(img_1,(int((r_peaks[(i+1)]-(j*TwSec)-120)/(TwSec/w)),1),(int((r_peaks[(i+1)]-(j*TwSec)+178)/(TwSec/w)),int(4*h/4)),(0,0,255),2)
        img_2 = cv2.putText(img_1, 'Other', (int((r_peaks[(i+1)]-(j*TwSec))/(TwSec/w)),int(1*h/8)),cv2.FONT_HERSHEY_COMPLEX , 1.5, (0, 0, 255), 2)
 
    else:     # Si se superaron los 20 segundos, pasar al siguiente renglón y comenzar nuevamente el recorrido
      img_3 = Image.fromarray(img_2, 'RGB')
      img_3.save('/content/ECG_Arr_'+str(j)+'.png')
      j=j+1
      img_1=cv2.imread('/content/Ventana_'+str(j)+'.png')
      (h,w,c)=img_1.shape[:3]

      if p2[i]=='NSR':  # Si el ciclo actual fue clasificado como normal, marcar el texto "NSR" en la imagen
        img_2 = cv2.putText(img_1, 'NSR', (int((r_peaks[(i+1)]-(j*TwSec))/(TwSec/w)),int(1*h/8)),cv2.FONT_HERSHEY_COMPLEX , 1.5, (0, 0, 255), 2)

      if p2[i]=='PVC':  # Si el ciclo fue clasificado como PVC, marcar un recuadro en la imagen con el texto PVC
        img_2 = cv2.rectangle(img_1,(int((r_peaks[(i+1)]-(j*TwSec)-120)/(TwSec/w)),1),(int((r_peaks[(i+1)]-(j*TwSec)+178)/(TwSec/w)),int(4*h/4)),(0,0,255),2)
        img_2 = cv2.putText(img_1, 'PVC', (int((r_peaks[(i+1)]-(j*TwSec))/(TwSec/w)),int(1*h/8)),cv2.FONT_HERSHEY_COMPLEX , 1.5, (0, 0, 255), 2)

      if p2[i]=='Other':  # Si el ciclo fue clasificado como "Other" (otro), marcar un recuadro en la imagen con el texto Other
        img_2 = cv2.rectangle(img_1,(int((r_peaks[(i+1)]-(j*TwSec)-120)/(TwSec/w)),1),(int((r_peaks[(i+1)]-(j*TwSec)+178)/(TwSec/w)),int(4*h/4)),(0,0,255),2)
        img_2 = cv2.putText(img_1, 'Other', (int((r_peaks[(i+1)]-(j*TwSec))/(TwSec/w)),int(1*h/8)),cv2.FONT_HERSHEY_COMPLEX , 1.5, (0, 0, 255), 2)
 
  # Pasar la imagen de su formato tipo arreglo a formato de imagen y almacenarla en PNG
  img_3 = Image.fromarray(img_2, 'RGB')
  img_3.save('/content/ECG_Arr_'+str(Rows)+'.png')

  # Comienza proceso de eliminación de imágenes creadas para vaciar el almacenamiento consumido
  ECGdiag = cv2.imread('/content/ECG_Arr_0.png')
  os.remove('/content/ECG_Arr_0.png')
  os.remove('/content/Ventana_0.png')

  # Antes de eliminar als imágenes de 20 segundos, se unen de forma vertical para crear una imagen
  # completa con el trazo completo y las marcas según la clasificación de cada ciclo
  for k in (Wrow):
    ECGadd = cv2.imread('/content/ECG_Arr_'+str(k+1)+'.png')
    ECGdiag = cv2.vconcat([ECGdiag,ECGadd])
    os.remove('/content/ECG_Arr_'+str(k+1)+'.png')
    os.remove('/content/Ventana_'+str(k+1)+'.png')
  
  # Pasar la imagen completa del diagnóstico de su formato tipo arreglo a formato de imagen y almacenarla en PNG
  ECGdiag = Image.fromarray(ECGdiag, 'RGB')
  ECGdiag.save('/content/ECG_diag.png')

  # Se almacena y se transforma a archivo multimedia Anvil como respuesta a la función Arrhyt_classifier
  imgarr = anvil.media.from_file('/content/ECG_diag.png', "image/png")
  print(time.time() - tmpo)

  return  imgarr

# Función de Anvil mantiene al servidor en un ciclo infinito, esperando la respuesta contínua de
# la interfaz web
anvil.server.wait_forever()