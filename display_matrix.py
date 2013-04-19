import bpy
import blf
from mathutils import Matrix, Vector
from bpy_extras.view3d_utils import location_3d_to_region_2d

bl_info = {
    "name": "Display Matrix",
    "author": "Adhi Hargo",
    "version": (1, 0, 0),
    "blender": (2, 64, 0),
    "location": "3D View > Properties Panel > Display Matrix",
    "description": "Display all available transformation matrices"\
        " for all selected object/bones",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development"}

OFFSET_X = 0
OFFSET_Y = 15
FLOAT_FMT = "%.3F"

def draw_pbone_matrices(self, context, obj, pbone):
    dm = context.window_manager.display_matrix
    pbone_location_world = pbone.matrix.to_translation()
    for p in pbone.parent_recursive:
        pbone_location_world = p.matrix_basis * pbone_location_world
    pbone_location_world = obj.matrix_world * pbone_location_world

    loc_x, loc_y = location_3d_to_region_2d(
        context.region,
        context.space_data.region_3d,
        pbone_location_world)
    loc_x += OFFSET_X

    texts = []

    if dm.show_matrix_pbone:
        texts.append(("Matrix:",
                      [", ".join([FLOAT_FMT % n for n in vec]) for vec in pbone.matrix]))
    if dm.show_matrix_basis_pbone:
        texts.append(("Matrix Basis:",
                      [", ".join([FLOAT_FMT % n for n in vec]) for vec in pbone.matrix_basis]))
    if dm.show_matrix_channel:
        texts.append(("Matrix Channel:",
                      [", ".join([FLOAT_FMT % n for n in vec]) for vec in pbone.matrix_channel]))

    for title, data in texts:
        blf.position(0, loc_x, loc_y, 0)
        blf.draw(0, title)
        loc_y -= OFFSET_Y
        for d in data:
            blf.position(0, loc_x + OFFSET_X, loc_y, 0)
            blf.draw(0, d)
            loc_y -= OFFSET_Y
        loc_y -= OFFSET_Y / 2

def draw_object_matrices(self, context, obj):
    dm = context.window_manager.display_matrix
    mode = obj.mode

    loc_x, loc_y = location_3d_to_region_2d(
        context.region,
        context.space_data.region_3d,
        obj.location)
    loc_x += OFFSET_X

    texts = []

    if mode == 'POSE':
        if context.selected_pose_bones:
            for pbone in context.selected_pose_bones:
                draw_pbone_matrices(self, context, obj, pbone)

    elif mode == 'OBJECT':
        if dm.show_matrix_basis_obj:
            texts.append(("Matrix Basis:",
                          [", ".join([FLOAT_FMT % n for n in vec])
                           for vec in obj.matrix_basis]))
        if dm.show_matrix_local_obj:
            texts.append(("Matrix Local:",
                          [", ".join([FLOAT_FMT % n for n in vec])
                           for vec in obj.matrix_local]))
        if dm.show_matrix_pinverse:
            texts.append(("Matrix Parent Inverse:",
                          [", ".join([FLOAT_FMT % n for n in vec])
                           for vec in obj.matrix_parent_inverse]))
        if dm.show_matrix_world:
            texts.append(("Matrix World:",
                          [", ".join([FLOAT_FMT % n for n in vec])
                           for vec in obj.matrix_world]))

    for title, data in texts:
        blf.position(0, loc_x, loc_y, 0)
        blf.draw(0, title)
        loc_y -= OFFSET_Y
        for d in data:
            blf.position(0, loc_x + OFFSET_X, loc_y, 0)
            blf.draw(0, d)
            loc_y -= OFFSET_Y
        loc_y -= OFFSET_Y / 2

def draw_matrix_callback(self, context):
    if context.window_manager.display_matrix.enabled:
        for obj in context.selected_objects:
            draw_object_matrices(self, context, obj)

class VIEW3D_OT_ADH_display_matrix(bpy.types.Operator):
    """Display all relevant matrices for active object"""
    bl_idname = "view3d.adh_display_matrix"
    bl_label = "Display Matrix"
    bl_options = {'REGISTER'}

    _handle = None

    def modal(self, context, event):
        context.area.tag_redraw()
        if not context.window_manager.display_matrix.enabled:
            # VIEW3D_OT_ADH_display_matrix.handle_remove(context)
            return {'CANCELLED'}
        return {'PASS_THROUGH'}

    @staticmethod
    def handle_add(self, context):
        VIEW3D_OT_ADH_display_matrix._handle = bpy.types.SpaceView3D.draw_handler_add(
            draw_matrix_callback,
            (self, context),
            'WINDOW', 'POST_PIXEL')

    @staticmethod
    def handle_remove(context):
        _handle = VIEW3D_OT_ADH_display_matrix._handle
        if _handle != None:
            bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        VIEW3D_OT_ADH_display_matrix._handle = None

    def cancel(self, context):
        if context.window_manager.display_matrix.enabled:
            VIEW3D_OT_ADH_display_matrix.handle_remove(context)
            context.window_manager.display_matrix.enabled = False
        return {'CANCELLED'}

    def invoke(self, context, event):
        if context.window_manager.display_matrix.enabled == False:
            context.window_manager.display_matrix.enabled = True
            context.window_manager.modal_handler_add(self)
            VIEW3D_OT_ADH_display_matrix.handle_add(self, context)

            return {'RUNNING_MODAL'}
        else:
            context.window_manager.display_matrix.enabled = False
            VIEW3D_OT_ADH_display_matrix.handle_remove(context)

            return {'CANCELLED'}

        return {'CANCELLED'}

class VIEW3D_PT_ADH_display_matrix(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Display Matrix"
    bl_options = {'DEFAULT_CLOSED'}

    show_matrix_display = bpy.props.BoolProperty(
        name = 'Show Matrix Display',
        description = '',
        default = False)

    @classmethod
    def poll(self, context):
        mode = context.mode
        if (context.area.type == 'VIEW_3D'
            and mode in ['EDIT_MESH', 'OBJECT', 'POSE']):
            return True

        return False

    def draw(self, context):
        layout = self.layout
        dm = context.window_manager.display_matrix

        if context.window_manager.display_matrix.enabled:        
            layout.operator('view3d.adh_display_matrix', text='Disable')
        else:
            layout.operator('view3d.adh_display_matrix', text='Enable')

        box = layout.box()
        col = box.column(align=True)
        col.label("Object:")
        col.prop(dm, 'show_matrix_local_obj')
        col.prop(dm, 'show_matrix_basis_obj')
        col.prop(dm, 'show_matrix_pinverse')
        col.prop(dm, 'show_matrix_world')
        
        box = layout.box()
        col = box.column(align=True)
        col.label("Pose Bone:")
        col.prop(dm, 'show_matrix_pbone')
        col.prop(dm, 'show_matrix_basis_pbone')
        col.prop(dm, 'show_matrix_channel')

class ADH_DisplayMatrixProps(bpy.types.PropertyGroup):
    enabled = bpy.props.BoolProperty(default=False)

    loc_x = bpy.props.IntProperty(name='LocX', default=0)
    loc_y = bpy.props.IntProperty(name='LocY', default=0)

    show_matrix_pbone = bpy.props.BoolProperty(name="Matrix", default=True)
    show_matrix_basis_pbone = bpy.props.BoolProperty(name="Matrix Basis", default=True)
    show_matrix_channel = bpy.props.BoolProperty(name="Matrix Channel", default=True)

    show_matrix_local_obj = bpy.props.BoolProperty(name="Matrix Local", default=True)
    show_matrix_basis_obj = bpy.props.BoolProperty(name="Matrix Basis", default=True)
    show_matrix_pinverse = bpy.props.BoolProperty(name="Matrix Parent Inverse", default=True)
    show_matrix_world = bpy.props.BoolProperty(name="Matrix World", default=True)

def register():
    bpy.utils.register_module(__name__)
    bpy.types.WindowManager.display_matrix = bpy.props.PointerProperty(type=ADH_DisplayMatrixProps)

def unregister():
    bpy.utils.unregister_module(__name__)
    VIEW3D_OT_ADH_display_matrix.handle_remove(bpy.context)
    del bpy.types.WindowManager.display_matrix

if __name__ == "__main__":
    register()
