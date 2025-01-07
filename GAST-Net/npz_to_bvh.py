import numpy as np
import argparse

def npz_to_bvh(input_file, output_file):
    """
    Convierte un archivo .npz con datos de esqueleto 3D a formato BVH compatible con Blender.
    :param input_file: Ruta del archivo .npz de entrada.
    :param output_file: Ruta del archivo .bvh de salida.
    """
    # Cargar datos del archivo .npz
    data = np.load(input_file)
    reconstruction = data['reconstruction']  # Extraer datos del esqueleto
    num_frames, num_joints, _ = reconstruction.shape[1:]

    # Definir una jerarquía simple
    joint_names = [f"Joint_{i}" for i in range(num_joints)]
    offsets = [[0, 0, 0] for _ in range(num_joints)]  # Placeholder para los offsets
    root_joint = joint_names[0]  # El primer joint será el ROOT

    # Crear el archivo BVH
    with open(output_file, "w") as f:
        # Escribir la jerarquía BVH
        f.write("HIERARCHY\n")
        f.write(f"ROOT {root_joint}\n")
        f.write("{\n")
        f.write("\tOFFSET 0.0 0.0 0.0\n")
        f.write("\tCHANNELS 6 Xposition Yposition Zposition Zrotation Xrotation Yrotation\n")

        # Añadir joints secundarios
        for i in range(1, num_joints):
            f.write(f"\tJOINT {joint_names[i]}\n")
            f.write("\t{\n")
            f.write("\t\tOFFSET 0.0 0.0 0.0\n")
            f.write("\t\tCHANNELS 3 Zrotation Xrotation Yrotation\n")
            f.write("\t\tEnd Site\n")
            f.write("\t\t{\n")
            f.write("\t\t\tOFFSET 0.0 0.0 0.0\n")
            f.write("\t\t}\n")
            f.write("\t}\n")
        f.write("}\n")

        # Escribir datos de movimiento
        f.write("MOTION\n")
        f.write(f"Frames: {num_frames}\n")
        f.write(f"Frame Time: {1.0 / 30}\n")  # Asumimos 30 FPS

        for frame_idx in range(num_frames):
            frame_data = reconstruction[0, frame_idx]
            # Escribir las posiciones y rotaciones para el ROOT
            root_position = frame_data[0]
            f.write(f"{root_position[0]} {root_position[1]} {root_position[2]} 0.0 0.0 0.0 ")
            
            # Escribir las rotaciones para los joints secundarios
            for joint in frame_data[1:]:
                f.write("0.0 0.0 0.0 ")  # Placeholder para las rotaciones
            f.write("\n")

    print(f"Archivo BVH generado: {output_file}")

if __name__ == "__main__":
    # Configurar el analizador de argumentos
    parser = argparse.ArgumentParser(description="Convierte un archivo .npz a formato BVH compatible con Blender.")
    parser.add_argument("input_file", type=str, help="Ruta al archivo .npz de entrada.")
    parser.add_argument("output_file", type=str, help="Ruta del archivo .bvh de salida.")
    args = parser.parse_args()

    # Convertir el archivo
    npz_to_bvh(args.input_file, args.output_file)
