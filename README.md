## Trabajo de curso: “Motion capture” con aprendizaje profundo aplicado a la visión por computador

En este trabajo se hace uso de GAST-Net (Fuente 1) para la detección de una persona y su esqueleto 2D y posteriormente una estimación del esqueleto 3D mediante el uso de un vídeo. Se usa el script "gen_skes.py" de GAST-Net.

Esos esqueletos 3D se utilizan posteriormente para recrear los movimientos de la persona del vídeo en una animación. La finalidad es poder disfrutar de las ventajas de "Motion Capture" sin requerir ningún equipamiento más que una cámara y un ordenador.

Esta animación se realiza en Blender (Fuente 2) con el script "blender_animation.py". 

Todo el proceso está explicado en mayor profundidad en la libreta principal del proyecto: "Trabajo-VC-G1.ipynb"

# Resultados
Algunos vídeos resultantes del proceso explicado previamente se pueden encontrar en la carpeta "output"

# Fuentes
1.- GAST-Net-3DPoseEstimation: https://github.com/fabro66/GAST-Net-3DPoseEstimation 

2.- Blender: https://www.blender.org/ 
