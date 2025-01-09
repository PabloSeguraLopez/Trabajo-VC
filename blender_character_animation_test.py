import bpy
import numpy as np


skeleton_connections = [
    # Pierna izquierda
    (1, 2),  # Pelvis izquierda -> Rodilla izquierdo
    (2, 3),  # Rodilla izquierdo -> Tobillo izquierdo

    # Pierna derecha
    (4, 5),  
    (5, 6), 

     # Tronco
    (0, 8), 
    (8, 9),  # Tronco -> Cuello
    (9,10), # Cuello-> cabeza
    (8, 11),  # Tronco -> Hombro izquierdo
    (8, 14),  # Tronco -> Hombro derecho
    # Brazo izquierdo
    (11, 12),  # Hombro izquierdo -> Codo izquierdo
    (12, 13),  # Codo izquierdo -> Muñeca izquierda
    # Brazo derecho
    (14, 15),  # Hombro derecho -> Codo derecho
    (15, 16),  # Codo derecho -> Muñeca derecha
]
bone_names = [
    "L.upperLeg",
    "L.lowerLeg",
    "R.upperLeg",
    "R.lowerLeg",
    "lowerBody",
    "UpperChest",
    "head",
    "L.shoulder",
    "R.shoulder",
    "L.upperArm",
    "L.lowerArm",
    "R.upperArm",
    "R.lowerArm"
]

def import_fbx(filepath):
    """Importa el archivo FBX."""
    bpy.ops.import_scene.fbx(filepath=filepath)

def load_npz(filepath):
    """Carga el archivo NPZ con las posiciones de las articulaciones."""
    data = np.load(filepath)
    return data

def clear_keyframes(object_name):
    """Limpia las keyframes existentes de un objeto."""
    obj = bpy.data.objects.get(object_name)
    if obj and obj.animation_data:
        obj.animation_data_clear()
def animate_skeleton(npz_data, armature_name):
    """Aplica la animación al rig del personaje"""
    armature = bpy.data.objects.get(armature_name)
    if armature is None:
        raise ValueError(f"No se encontró un armature llamado '{armature_name}'")

    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    num_frames = npz_data.shape[1]
    num_joints = npz_data.shape[2]

    # Obtener la posición inicial de la cadera en el primer frame (articulación raíz)
    root_position = npz_data[0, 0, 0]
    npz_data = npz_data[:,:,:]-root_position

    for frame_idx in range(num_frames):
        for joint_idx, (start_joint, end_joint) in enumerate(skeleton_connections):
            bone_name = bone_names[joint_idx]
            bone = armature.pose.bones.get(bone_name)

            if bone is not None:
                joint_position = npz_data[0, frame_idx, end_joint]

                if frame_idx == 0:
                    # En el primer frame, coloca al personaje en coordenadas absolutas
                    bone.location = joint_position
                else:
                    # En los siguientes frames, usa posiciones relativas
                    parent_joint_pos = npz_data[0, frame_idx, start_joint]
                    relative_position = joint_position - parent_joint_pos
                    bone.location = relative_position

                # Inserta el keyframe
                bone.keyframe_insert(data_path="location", frame=frame_idx + 1)

    bpy.ops.object.mode_set(mode='OBJECT')


def main(fbx_path, npz_path, armature_name):
    # Importa el archivo FBX
    import_fbx(fbx_path)

    # Carga los datos del archivo NPZ
    npz_data = load_npz(npz_path)['reconstruction']

    # Limpia cualquier animación previa
    clear_keyframes(armature_name)

    # Anima el esqueleto
    animate_skeleton(npz_data, armature_name)


fbx_filepath = "C:/Users/pablo/Desktop/Universidad/Cuarto/Visión por computador/Prácticas/Trabajo-VC/Characters/Man.fbx"
npz_filepath = "C:/Users/pablo/Desktop/Universidad/Cuarto/Visión por computador/Prácticas/Trabajo-VC/GAST-Net/output/fortnite.npz"
armature_object_name = "Armature.001"
output_video_path = "C:/Users/pablo/Desktop/Universidad/Cuarto/Visión por computador/Prácticas/Trabajo-VC/output/animated_character.avi"  # Ruta del vídeo de salida

# Ejecuta el script
main(fbx_filepath, npz_filepath, armature_object_name)