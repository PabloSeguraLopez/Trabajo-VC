import bpy
import numpy as np
import argparse
import sys

def load_npz(npz_file_path):
    """
    Load the NPZ file and extract the positions.
    """
    data = np.load(npz_file_path)
    positions = data["reconstruction"]
    return positions[0]  # (n_frames, n_squares, 3)

def clear_scene():
    """
    Clears all objects, lights and cameras from the scene.
    """
    # Eliminar todos los objetos en la escena
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Eliminar todas las luces
    bpy.ops.object.light_add(type='POINT', location=(0, 0, 0))
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    # Eliminar todas las cámaras
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
def create_objects(positions):
    """
    Create objects (joints) in Blender and return them.
    """
    # Crear un material negro
    black_material = bpy.data.materials.new(name="Black_Material")
    black_material.use_nodes = True
    nodes = black_material.node_tree.nodes
    principled_node = nodes.get("Principled BSDF")
    if principled_node:
        # Establecer el color a negro (RGBA)
        principled_node.inputs["Base Color"].default_value = (0.0, 0.0, 0.0, 1.0)  # Negro
        principled_node.inputs["Roughness"].default_value = 1.0  # Opcional: Sin reflejos

    n_frames, n_joints, _ = positions.shape
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, 0, 0))
    parent_object = bpy.context.object
    parent_object.name = "Joints_Parent"

    objects = []
    for i in range(n_joints):
        # Joints 9 and 7 are redundant, part of the column
        if i == 9 or i == 7:
            objects.append(None)
            continue
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0, 0))
        obj = bpy.context.object
        obj.name = f"Joint_{i}"
        obj.parent = parent_object
        objects.append(obj)
        if obj.data.materials:
            obj.data.materials[0] = black_material
        else:
            obj.data.materials.append(black_material)

    return objects

def animate_objects(positions, objects):
    """
    Animate the objects according to the positions from the NPZ.
    """
    n_frames, n_squares, _ = positions.shape
    for frame_idx in range(n_frames):
        for square_idx, obj in enumerate(objects):
            if obj is None:
                continue
            x, y, z = positions[frame_idx, square_idx]
            obj.location = (x, y, z)
            obj.keyframe_insert(data_path="location", frame=frame_idx + 1)

def setup_camera():
    bpy.ops.object.camera_add(location=(0, 5.92, 1.72))
    camera = bpy.context.object
    camera.name = "Camera"
    camera.rotation_euler = (1.466, 0, -3.1416)  # Orient it towards the origin

    bpy.context.scene.camera = camera

def setup_light():
    bpy.ops.object.light_add(type='SUN', location=(5, -5, 10))
    sun_light = bpy.context.object
    sun_light.name = "Sun_Light"

def setup_world_background(background_color):
    world = bpy.context.scene.world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links

    # Clean existing nodes
    for node in nodes:
        nodes.remove(node)

    background_node = nodes.new(type="ShaderNodeBackground")
    # Convert color string to RGB
    color_dict = {
        "red": (1.0, 0.0, 0.0, 1.0),
        "green": (0.0, 1.0, 0.0, 1.0),
        "blue": (0.0, 0.0, 1.0, 1.0),
        "white": (1.0, 1.0, 1.0, 1.0),
    }
    background_node.inputs[0].default_value = color_dict.get(background_color, (0.5, 0.2, 0.1, 1.0))  # Default to custom color if not found

    output_node = nodes.new(type="ShaderNodeOutputWorld")
    links.new(background_node.outputs[0], output_node.inputs[0])

def setup_render(output_path, n_frames, quality):
    bpy.context.scene.render.filepath = output_path
    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'MPEG4'
    if quality == "low":
        bpy.context.scene.render.resolution_x = 640
        bpy.context.scene.render.resolution_y = 360
    else:
        bpy.context.scene.render.resolution_x = 1920
        bpy.context.scene.render.resolution_y = 1080
    bpy.context.scene.render.fps = 30
    bpy.context.scene.frame_start = 1
    bpy.context.scene.frame_end = n_frames
    bpy.context.view_layer.update()

def render_animation():
    bpy.ops.render.render(animation=True)
    print("Animation successfully saved as MP4.")

def main(npz_file_path, background_color, output_path, quality):
    clear_scene()
    positions = load_npz(npz_file_path)
    n_frames, n_squares, _ = positions.shape

    objects = create_objects(positions)

    animate_objects(positions, objects)

    setup_camera()
    setup_light()

    setup_world_background(background_color)

    setup_render(output_path, n_frames, quality)

    render_animation()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Animate and render a 3D character based on 3D skeletons from an NPZ file.")
    parser.add_argument('-f', '--file', required=True, help="Path to the NPZ file.")
    parser.add_argument('-c', '--color', default="white", help="Background color (e.g., 'red', 'green', 'blue').")
    parser.add_argument('-o', '--output', required=True, help="Path for the output video file.")
    parser.add_argument('-q', '--quality', default="low", help="Quality for the output video.")
    
    args,_ = parser.parse_known_args(sys.argv[sys.argv.index("--") + 1:])

    main(args.file, args.color, args.output, args.quality)
