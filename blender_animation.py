import bpy
import numpy as np

# Ruta del archivo NPZ
npz_file_path = "C:/Users/pablo/Desktop/Universidad/Cuarto/Visión por computador/Prácticas/Trabajo-VC/GAST-Net/output/fortnite.npz"

# Cargar el archivo NPZ
data = np.load(npz_file_path)


positions = data["reconstruction"]

if positions.ndim != 4 or positions.shape[0] != 1 or positions.shape[3] != 3:
    raise ValueError("Las dimensiones del array deben ser (1, n_frames, n_cuadrados, 3).")


positions = positions[0]  # (n_frames, n_cuadrados, 3)

n_frames, n_cuadrados, _ = positions.shape

# Crear un objeto padre para manejar más fácilmente el personaje
bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
parent_object = bpy.context.object
parent_object.name = "Joints_Parent"

# Crear los objetos (esferas) en Blender
objects = []
for i in range(n_cuadrados):
    # Las articulaciones 9 y 7 son redudantes, forman parte de la columna
    if i == 9 or i == 7:
        objects.append(None)
        continue
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0, 0))
    obj = bpy.context.object
    obj.name = f"Joint_{i}"
    obj.parent = parent_object
    objects.append(obj)

# Animar los objetos según las posiciones del archivo NPZ
for frame_idx in range(n_frames):
    for square_idx, obj in enumerate(objects):
        if obj is None:
            continue
        x, y, z = positions[frame_idx, square_idx]
        obj.location = (x, y, z)
        obj.keyframe_insert(data_path="location", frame=frame_idx + 1)

# Añadir una cámara
bpy.ops.object.camera_add(location=(0, 5.92, 1.72))
camera = bpy.context.object
camera.name = "Camera"
camera.rotation_euler = (1.466, 0, -3.1416)  # Orientar hacia el origen

bpy.context.scene.camera = camera

# Añadir iluminación
bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
sun_light = bpy.context.object
sun_light.name = "Sun_Light"

# Configurar fondo
world = bpy.context.scene.world
world.use_nodes = True

# Obtener nodos del mundo
nodes = world.node_tree.nodes
links = world.node_tree.links

# Limpiar nodos existentes
for node in nodes:
    nodes.remove(node)

# Añadir nodo de fondo
background_node = nodes.new(type="ShaderNodeBackground")
background_node.inputs[0].default_value = (0.5, 0.2, 0.1, 1.0)  # Color azul claro

# Añadir nodo de salida del mundo
output_node = nodes.new(type="ShaderNodeOutputWorld")

# Conectar los nodos
links.new(background_node.outputs[0], output_node.inputs[0])
if False:
    # Configuración de salida para MP4
    output_path = "C:/Users/pablo/Desktop/baseball.mp4"  # Cambia la ruta según lo desees
    bpy.context.scene.render.filepath = output_path

    # Establecer el formato de salida a FFmpeg (MP4)
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'MPEG4'

    # Ajustar resolución (opcional, en este caso 1920x1080)
    bpy.context.scene.render.resolution_x = 1920
    bpy.context.scene.render.resolution_y = 1080

    # Establecer la tasa de fotogramas (FPS)
    bpy.context.scene.render.fps = 30  # Ajusta esto según tus necesidades

    # Definir el rango de fotogramas a renderizar
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = n_frames

    # Hacer el renderizado de la animación
    bpy.ops.render.render(animation=True)

print("Animación guardada como MP4 exitosamente.")

