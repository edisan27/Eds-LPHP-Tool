bl_info = {
    "name": "Ed's LPHP Tool",
    "author": "edisan27",
    "version": (0, 1),
    "blender": (4, 3, 2),
    "location": "View3D > Sidebar > Rename Tools",
    "description": "Bunch of tools I find useful",
    "category": "Object",
}

import bpy
import os

class ExportCollectionItem(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(name="Collection Name")
    enabled: bpy.props.BoolProperty(name="Enable", default=True)

class RenameSettings(bpy.types.PropertyGroup):
    base_name: bpy.props.StringProperty(name="Object Name", default="MyObject")
    lp_suffix: bpy.props.StringProperty(name="LP Suffix", default="_low")
    hp_suffix: bpy.props.StringProperty(name="HP Suffix", default="_high")
    find_text: bpy.props.StringProperty(name="Find", default="")
    replace_text: bpy.props.StringProperty(name="Replace", default="")
    export_path: bpy.props.StringProperty(name="Directory", subtype='DIR_PATH')

    export_collections: bpy.props.CollectionProperty(type=ExportCollectionItem)  # (optional legacy/general)
    highpoly_collections: bpy.props.CollectionProperty(type=ExportCollectionItem)
    lowpoly_collections: bpy.props.CollectionProperty(type=ExportCollectionItem)

    # New properties for export filenames
    highpoly_filename: bpy.props.StringProperty(name="Filename", default="MeshName_high.fbx")
    lowpoly_filename: bpy.props.StringProperty(name="Filename", default="MeshName_low.fbx")

# ------------------------
# Helper Function to Initialize Collections
# ------------------------

def initialize_export_collections(context):
    settings = context.scene.rename_settings
    # Only refresh if it's empty
    if not settings.export_collections:
        settings.export_collections.clear()
        for col in bpy.data.collections:
            item = settings.export_collections.add()
            item.name = col.name

def get_all_objects_from_collection(collection):
    objects = list(collection.objects)
    for child in collection.children:
        objects.extend(get_all_objects_from_collection(child))
    return objects

class REFRESH_OT_export_collections(bpy.types.Operator):
    bl_idname = "export_collections.refresh"
    bl_label = "Refresh Collections"
    bl_description = "Refresh collection lists for HP and LP export"

    def execute(self, context):
        settings = context.scene.rename_settings

        # Clear existing collections from both lists
        settings.highpoly_collections.clear()
        settings.lowpoly_collections.clear()

        # Add collections to both lists
        for col in bpy.data.collections:
            if col.objects:  # Only add collections that contain objects
                item_hp = settings.highpoly_collections.add()
                item_hp.name = col.name
                item_hp.enabled = False  # Default to disabled

                item_lp = settings.lowpoly_collections.add()
                item_lp.name = col.name
                item_lp.enabled = False  # Default to disabled

        self.report({'INFO'}, "Refreshed collection lists.")
        return {'FINISHED'}

class EXPORT_OT_highpoly(bpy.types.Operator):
    bl_idname = "export_collections.export_highpoly"
    bl_label = "Export High Poly Collections"

    def execute(self, context):
        settings = context.scene.rename_settings
        export_path = settings.export_path
        export_filename = settings.highpoly_filename

        if not export_path:
            self.report({'ERROR'}, "Export path is not set")
            return {'CANCELLED'}

        # Convert relative path (//) to absolute path
        if export_path.startswith('//'):
            export_path = bpy.path.abspath(export_path)

        # Ensure export path is absolute
        if not os.path.isabs(export_path):
            self.report({'ERROR'}, f"Invalid export path: {export_path}")
            return {'CANCELLED'}

        # Make sure the directory exists
        if not os.path.exists(export_path):
            self.report({'ERROR'}, f"Export path does not exist: {export_path}")
            return {'CANCELLED'}

        full_export_path = os.path.join(export_path, export_filename)

        # Make sure the file path exists
        all_mesh_objects = []
        for item in settings.highpoly_collections:
            if item.enabled:
                collection = bpy.data.collections.get(item.name)
                if collection:
                    all_mesh_objects.extend(get_all_objects_from_collection(collection))

        if not all_mesh_objects:
            self.report({'WARNING'}, "No mesh objects found to export")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_mesh_objects:
            obj.select_set(True)

        # Export the selected meshes as FBX
        bpy.ops.export_scene.fbx(
            filepath=full_export_path,
            use_selection=True,
            apply_unit_scale=True,
            bake_space_transform=True
        )

        self.report({'INFO'}, f"Exported High Poly FBX: {export_filename}")
        return {'FINISHED'}

class EXPORT_OT_lowpoly(bpy.types.Operator):
    bl_idname = "export_collections.export_lowpoly"
    bl_label = "Export Low Poly Collections"

    def execute(self, context):
        settings = context.scene.rename_settings
        export_path = settings.export_path
        export_filename = settings.lowpoly_filename

        if not export_path:
            self.report({'ERROR'}, "Export path is not set")
            return {'CANCELLED'}

        # Convert relative path (//) to absolute path
        if export_path.startswith('//'):
            export_path = bpy.path.abspath(export_path)

        # Ensure export path is absolute
        if not os.path.isabs(export_path):
            self.report({'ERROR'}, f"Invalid export path: {export_path}")
            return {'CANCELLED'}

        # Make sure the directory exists
        if not os.path.exists(export_path):
            self.report({'ERROR'}, f"Export path does not exist: {export_path}")
            return {'CANCELLED'}

        full_export_path = os.path.join(export_path, export_filename)

        # Make sure the file path exists
        all_mesh_objects = []
        for item in settings.lowpoly_collections:
            if item.enabled:
                collection = bpy.data.collections.get(item.name)
                if collection:
                    all_mesh_objects.extend(get_all_objects_from_collection(collection))

        if not all_mesh_objects:
            self.report({'WARNING'}, "No mesh objects found to export")
            return {'CANCELLED'}

        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_mesh_objects:
            obj.select_set(True)

        # Export the selected meshes as FBX
        bpy.ops.export_scene.fbx(
            filepath=full_export_path,
            use_selection=True,
            apply_unit_scale=True,
            bake_space_transform=True
        )

        self.report({'INFO'}, f"Exported Low Poly FBX: {export_filename}")
        return {'FINISHED'}

class OBJECT_OT_RefreshExportCollections(bpy.types.Operator):
    bl_idname = "object.refresh_export_collections"
    bl_label = "Refresh Export Collections"
    bl_description = "Refresh the list of collections for export"

    def execute(self, context):
        settings = context.scene.rename_settings
        settings.highpoly_collections.clear()
        settings.lowpoly_collections.clear()

        for col in bpy.data.collections:
            item_hp = settings.highpoly_collections.add()
            item_hp.name = col.name
            item_hp.enabled = False

            item_lp = settings.lowpoly_collections.add()
            item_lp.name = col.name
            item_lp.enabled = False

        self.report({'INFO'}, "Refreshed collection lists.")
        return {'FINISHED'}



class OBJECT_OT_RenameLPHP(bpy.types.Operator):
    bl_idname = "object.rename_lphp"
    bl_label = "Rename LP/HP"
    bl_description = "Rename two selected objects with LP/HP suffix based on polycount"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.rename_settings
        selected = context.selected_objects

        if len(selected) != 2:
            self.report({'ERROR'}, "Select exactly 2 objects")
            return {'CANCELLED'}

        obj1, obj2 = selected
        tris1 = sum(len(p.vertices) - 2 for p in obj1.data.polygons)
        tris2 = sum(len(p.vertices) - 2 for p in obj2.data.polygons)

        if tris1 <= tris2:
            lp_obj, hp_obj = obj1, obj2
        else:
            lp_obj, hp_obj = obj2, obj1

        new_lp_name = settings.base_name + settings.lp_suffix
        new_hp_name = settings.base_name + settings.hp_suffix

        # Check for name collisions in other objects (not the selected ones)
        for obj in bpy.data.objects:
            if obj not in (lp_obj, hp_obj):
                if obj.name == new_lp_name or obj.name == new_hp_name:
                    self.report({'ERROR'}, f"Name '{obj.name}' already exists in the scene.")
                    return {'CANCELLED'}

        lp_obj.name = new_lp_name
        hp_obj.name = new_hp_name

        self.report({'INFO'}, f"Renamed to: {lp_obj.name}, {hp_obj.name}")
        return {'FINISHED'}

class OBJECT_OT_SwapLPHP(bpy.types.Operator):
    bl_idname = "object.swap_lphp"
    bl_label = "Swap LP/HP"
    bl_description = "Swap LP and HP suffixes and collection positions of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.rename_settings
        selected = context.selected_objects

        lp_suffix = settings.lp_suffix
        hp_suffix = settings.hp_suffix

        def ends_with(obj, suffix):
            return obj.name.endswith(suffix)

        def strip_suffix(name, suffix):
            if name.endswith(suffix):
                return name[:-len(suffix)]
            return None

        if len(selected) == 1:
            obj = selected[0]
            if ends_with(obj, lp_suffix):
                base = strip_suffix(obj.name, lp_suffix)
                counterpart = next((o for o in bpy.data.objects
                                    if o != obj and o.name == base + hp_suffix), None)
                if not counterpart:
                    self.report({'ERROR'}, f"Matching HP object for '{obj.name}' not found.")
                    return {'CANCELLED'}
                lp_obj, hp_obj = obj, counterpart

            elif ends_with(obj, hp_suffix):
                base = strip_suffix(obj.name, hp_suffix)
                counterpart = next((o for o in bpy.data.objects
                                    if o != obj and o.name == base + lp_suffix), None)
                if not counterpart:
                    self.report({'ERROR'}, f"Matching LP object for '{obj.name}' not found.")
                    return {'CANCELLED'}
                hp_obj, lp_obj = obj, counterpart
            else:
                self.report({'ERROR'}, f"Object name must end with '{lp_suffix}' or '{hp_suffix}'")
                return {'CANCELLED'}

        elif len(selected) == 2:
            obj1, obj2 = selected
            if ends_with(obj1, lp_suffix) and ends_with(obj2, hp_suffix):
                lp_obj, hp_obj = obj1, obj2
            elif ends_with(obj2, lp_suffix) and ends_with(obj1, hp_suffix):
                lp_obj, hp_obj = obj2, obj1
            else:
                self.report({'ERROR'}, f"Objects must end with '{lp_suffix}' and '{hp_suffix}'")
                return {'CANCELLED'}

            base = strip_suffix(lp_obj.name, lp_suffix)
            if base != strip_suffix(hp_obj.name, hp_suffix):
                self.report({'ERROR'}, "Base names do not match")
                return {'CANCELLED'}
        else:
            self.report({'ERROR'}, "Select 1 or 2 objects")
            return {'CANCELLED'}

        # Check for name conflicts
        new_lp_name = base + hp_suffix
        new_hp_name = base + lp_suffix

        for obj in bpy.data.objects:
            if obj not in (lp_obj, hp_obj):
                if obj.name in (new_lp_name, new_hp_name):
                    self.report({'ERROR'}, f"Name '{obj.name}' already exists in the scene.")
                    return {'CANCELLED'}

        # Swap collections
        lp_cols = [col for col in lp_obj.users_collection]
        hp_cols = [col for col in hp_obj.users_collection]

        for col in lp_cols:
            col.objects.unlink(lp_obj)
        for col in hp_cols:
            col.objects.unlink(hp_obj)
        for col in lp_cols:
            col.objects.link(hp_obj)
        for col in hp_cols:
            col.objects.link(lp_obj)

        # Use temp names to avoid conflicts
        lp_obj.name = "__TEMP_SWAP_LP__"
        hp_obj.name = "__TEMP_SWAP_HP__"

        lp_obj.name = new_lp_name
        hp_obj.name = new_hp_name

        self.report({'INFO'}, f"Swapped: {lp_obj.name} <--> {hp_obj.name}")
        return {'FINISHED'}

class OBJECT_OT_FindReplaceNames(bpy.types.Operator):
    bl_idname = "object.find_replace_names"
    bl_label = "Find & Replace"
    bl_description = "Find and replace in names of selected objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.rename_settings
        find = settings.find_text
        replace = settings.replace_text

        if not find:
            self.report({'WARNING'}, "Nothing to find")
            return {'CANCELLED'}

        count = 0
        for obj in context.selected_objects:
            if find in obj.name:
                obj.name = obj.name.replace(find, replace)
                count += 1

        self.report({'INFO'}, f"Replaced in {count} object(s)")
        return {'FINISHED'}

class OBJECT_OT_VerifyLPPairs(bpy.types.Operator):
    bl_idname = "object.verify_lp_pairs"
    bl_label = "Verify LP/HP Pairs"
    bl_description = "Check if selected objects have their LP/HP counterparts"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = context.scene.rename_settings
        lp_suffix = settings.lp_suffix
        hp_suffix = settings.hp_suffix
        selected = context.selected_objects

        if not selected:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}

        missing_pairs = []
        verified_pairs = []
        ignored_objects = []

        def get_pair_name(obj_name):
            if obj_name.endswith(lp_suffix):
                return obj_name[:-len(lp_suffix)] + hp_suffix
            elif obj_name.endswith(hp_suffix):
                return obj_name[:-len(hp_suffix)] + lp_suffix
            else:
                return None

        for obj in selected:
            pair_name = get_pair_name(obj.name)
            if pair_name is None:
                ignored_objects.append(obj.name)
            elif pair_name in bpy.data.objects:
                verified_pairs.append(obj.name)
            else:
                missing_pairs.append(obj.name)

        msg_parts = []

        if verified_pairs:
            msg_parts.append(f"✔ Paired: {', '.join(verified_pairs)}")
        if missing_pairs:
            msg_parts.append(f"✘ Missing pairs: {', '.join(missing_pairs)}")
        if ignored_objects:
            msg_parts.append(f"⚠ No suffix: {', '.join(ignored_objects)}")

        full_msg = " | ".join(msg_parts)
        self.report({'INFO'}, full_msg if full_msg else "No matching LP/HP suffixes found.")
        return {'FINISHED'}

class OBJECT_OT_ExportSelectedCollections(bpy.types.Operator):
    bl_idname = "object.export_selected_collections"
    bl_label = "Export Selected Collections"
    bl_description = "Export all mesh objects in selected collections as a single FBX file"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Ensure that we're working in a valid context
        settings = bpy.context.scene.rename_settings  # Access scene rename settings
        export_path = bpy.path.abspath(settings.export_path)

        if not export_path:
            self.report({'ERROR'}, "Export path is not set.")
            return {'CANCELLED'}

        # Collect selected collections based on checkbox list
        selected_collections = [
            bpy.data.collections.get(item.name)
            for item in settings.export_collections if item.include
        ]

        if not selected_collections:
            self.report({'ERROR'}, "No collections selected for export.")
            return {'CANCELLED'}

        # Collect all mesh objects from selected collections
        all_mesh_objects = []
        for col in selected_collections:
            for obj in get_all_objects_from_collection(col):
                if obj.type == 'MESH' and obj not in all_mesh_objects:
                    all_mesh_objects.append(obj)

        if not all_mesh_objects:
            self.report({'WARNING'}, "No mesh objects found in selected collections.")
            return {'CANCELLED'}

        # Prepare for export
        bpy.ops.object.select_all(action='DESELECT')
        for obj in all_mesh_objects:
            obj.select_set(True)
        context.view_layer.objects.active = all_mesh_objects[0]

        # Use the first collection's name as filename
        export_filename = selected_collections[0].name + ".fbx"
        full_export_path = os.path.join(export_path, export_filename)

        # Export as FBX
        bpy.ops.export_scene.fbx(
            filepath=full_export_path,
            use_selection=True,
            apply_unit_scale=True,
            bake_space_transform=True,
            object_types={'MESH'},
            mesh_smooth_type='OFF',
            use_mesh_modifiers=True,
            add_leaf_bones=False,
            path_mode='AUTO',
        )

        self.report({'INFO'}, f"Exported to {full_export_path}")
        return {'FINISHED'}


class VIEW3D_PT_RenamePanel(bpy.types.Panel):
    bl_label = "LP/HP Renamer"
    bl_idname = "VIEW3D_PT_rename_lphp"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ed's Tools"

    def draw(self, context):
        layout = self.layout
        settings = bpy.context.scene.rename_settings

        box1 = layout.box()
        box1.label(text="LP/HP Rename", icon="MODIFIER")
        box1.prop(settings, "base_name")
        box1.prop(settings, "lp_suffix")
        box1.prop(settings, "hp_suffix")
        box1.operator("object.rename_lphp", icon="FONT_DATA")
        box1.operator("object.swap_lphp", icon="FILE_REFRESH")
        box1.operator("object.verify_lp_pairs", icon="CHECKMARK")

        box2 = layout.box()
        box2.label(text="Find & Replace", icon="VIEWZOOM")
        box2.prop(settings, "find_text")
        box2.prop(settings, "replace_text")
        box2.operator("object.find_replace_names", icon="VIEWZOOM")

        layout.separator()


class VIEW3D_PT_ExportPanel(bpy.types.Panel):
    bl_label = "LP/HP Collections Exporter"
    bl_idname = "VIEW3D_PT_lp_hp_exporter"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Ed's Tools"

    def draw(self, context):
        layout = self.layout
        settings = bpy.context.scene.rename_settings

        box1 = layout.box()
        box1.label(text="LP/HP Export Collections", icon='EXPORT')
        # Export path field
        box1.prop(settings, "export_path")
        box1.operator("export_collections.refresh", icon='FILE_REFRESH')  # Refresh button

        # High Poly section
        box_hp = box1.box()
        box_hp.label(text="High Poly Collections:", icon='EVENT_UP_ARROW')
        for item in settings.highpoly_collections:
            box_hp.prop(item, "enabled", text=item.name)
        
        # Input for high poly export filename
        box_hp.prop(settings, "highpoly_filename")
        box_hp.operator("export_collections.export_highpoly", icon='EXPORT')

        # Low Poly section
        box_lp = box1.box()
        box_lp.label(text="Low Poly Collections:", icon='EVENT_DOWN_ARROW')
        for item in settings.lowpoly_collections:
            box_lp.prop(item, "enabled", text=item.name)

        # Input for low poly export filename
        box_lp.prop(settings, "lowpoly_filename")
        box_lp.operator("export_collections.export_lowpoly", icon='EXPORT')


classes = [
    ExportCollectionItem,
    RenameSettings, 
    OBJECT_OT_RenameLPHP, 
    OBJECT_OT_SwapLPHP, 
    OBJECT_OT_VerifyLPPairs, 
    OBJECT_OT_FindReplaceNames, 
    VIEW3D_PT_RenamePanel,
    VIEW3D_PT_ExportPanel,
    OBJECT_OT_ExportSelectedCollections,
    OBJECT_OT_RefreshExportCollections,
    REFRESH_OT_export_collections,
    EXPORT_OT_highpoly,
    EXPORT_OT_lowpoly,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.rename_settings = bpy.props.PointerProperty(type=RenameSettings)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.rename_settings
    del bpy.types.Scene.export_collection_names


if __name__ == "__main__":
    register()
