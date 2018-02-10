import bpy
import bmesh

def triangulate_object(mesh):
    me = mesh
    # Get a BMesh representation
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces[:], quad_method=0, ngon_method=0)
    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(me)
    bm.free()


def write_mesh(context, filepath):
    print("Writing current mesh to {}".format(filepath))
    current_object = bpy.context.scene.objects.active
    assert current_object is not None, "No object is selected."
    mesh = current_object.to_mesh(bpy.context.scene, True, 'PREVIEW')
    triangulate_object(mesh)

    for i,face in mesh.polygons.items():
        assert len(face.vertices) == 3, "Make sure your mesh is triangulated"
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write("local v = {\n")
        for i,vertex in mesh.vertices.items():
            x,y,z = vertex.co
            f.write("{{{}, {}, {}}},\n".format(x,y,z))
    
        f.write("}\n")
        f.write("local f = {\n")        
    
        for i,face in mesh.polygons.items():
            a,b,c = face.vertices
            f.write("{{{}, {}, {}}},\n".format(a+1, b+1, c+1))
    
        f.write("}\n")
        

    bpy.data.meshes.remove(mesh)
    return {'FINISHED'}


# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class Pico8Exporter(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export.pico8"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export to Pico-8"

    # ExportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    def execute(self, context):
        return write_mesh(context, self.filepath)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(Pico8Exporter.bl_idname, text="Export to Pico8")


def register():
    bpy.utils.register_class(Pico8Exporter)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(Pico8Exporter)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export.pico8('INVOKE_DEFAULT')
