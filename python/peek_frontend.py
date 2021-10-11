from ._anvil_designer import PEEK_FrontEndTemplate
from anvil import *
import anvil.server

class PEEK_FrontEnd(PEEK_FrontEndTemplate):
  def __init__(self, **properties):
    # Se definen las propiedades del Form de PÉEK
    self.init_components(**properties)

    
  def arrhyt_class_click(self, **event_args):
    """Se activa cuando el botón es presionado"""
    self.Class_RowPanel.visible=True
    self.Segm_Panel.visible=False
    self.AlgEval_Panel.visible=False
    
    
  def segment_loc_click(self, **event_args):
    """Se activa cuando el botón es presionado"""
    self.Class_RowPanel.visible=False
    self.Segm_Panel.visible=True
    self.AlgEval_Panel.visible=False

  def algorithm_eval_click(self, **event_args):
    """Se activa cuando el botón es presionado"""
    self.Class_RowPanel.visible=False
    self.Segm_Panel.visible=False
    self.AlgEval_Panel.visible=True

######################################################################     
    
  
  ## Si el botón UPLOAD ECG  es presionado, se manda la información para Frecuencia de muestreo
  ## y el trazo hacia el servidor mediante el llamado de Anvil hacia la función Upload_ECG.
  ## regresando como respuesta el trazo ECG completo en una imagen con renglones del trazo
  ## cada 20 segundos
  def button_classifier_copy_click(self, **event_args):
    # Si el selector se encuentra en Frecuencia de muestreo, se manda la información del cuadro
    # de texto en Frecuencia de muestreo
    if (self.FreqM.selected==True):
      FS=self.text_box_FS.text 
      FST=1
    # Si el selector se encuentra en Duración del trazo, se manda la información del cuadro
    # de texto en tiempo en segundos
    if (self.TimeL.selected==True):
      FS=self.text_box_FS.text
      FST=2
      
    ## El archivo seleccionado se almacena en ECG_ORIG y se manda a llamar la función Upload_ECG
    ## del servidor, enviando el archivo multimedia y las variables FS y FST
    ECG_ORIG=self.file_loader_1.file
    self.original_ecg.source = anvil.server.call('Upload_ECG', 
                                ECG_ORIG,FS,FST)
    self.original_ecg.visible=True

            
  ## Si el botón Find arrhytmia es presionado, se envía la misma información que en la función
  ## Upload ECG, pero regresa el trazo con marcas en cada ciclo cardíaco según como fue clasificado.
  ## Este sería el diagóstico generado por PÉEK
  def button_classifier_click(self, **event_args):
    # Si el selector se encuentra en Frecuencia de muestreo, se manda la información del cuadro
    # de texto en Frecuencia de muestreo
    if (self.FreqM.selected==True):
      FS=self.text_box_FS.text 
      FST=1
    # Si el selector se encuentra en Duración del trazo, se manda la información del cuadro
    # de texto en tiempo en segundos
    if (self.TimeL.selected==True):
      FS=self.text_box_FS.text
      FST=2
      
    ## El archivo seleccionado se almacena en ECG_ORIG y se manda a llamar la función arrhyt_classifier
    ## del servidor, enviando el archivo multimedia y las variables FS y FST
    ECG_ORIG=self.file_loader_1.file
    self.arrhytmia_ecg.source = anvil.server.call('arrhyt_classifier', 
                                                  ECG_ORIG,FS,FST)
    self.arrhytmia_ecg.visible=True
    