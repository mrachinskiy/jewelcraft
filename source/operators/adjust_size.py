def _round_to_step(value: float, step: float) -> float:
    if step == 0.0:
        return value

    return round(value / step) * step

class OBJECT_OT_adjust_size(Operator):
    bl_label = "Adjust Size"
    bl_description = "Adjust size by step within limits"
    bl_idname = "object.jewelcraft_adjust_size"
    bl_options = {"REGISTER", "UNDO"}

    dim_orig: tuple[float, float, float]
    pivot: tuple[float, float, float]

    min_size: FloatProperty(
        name="Minimum Size",
        default=0.69,
        description="Minimal allowed size of the object"
    )
    max_size: FloatProperty(
        name="Maximum Size",
        default=10.01,
        description="Maximum allowed size of the object"
    )
    step: FloatProperty(
        name="Step",
        default=0.1,
        description="Size change step (use negative value for decrement)"
    )


    def execute(self, context):
        obj = context.object
        if not obj:
            return {"CANCELLED"}

        step = abs(self.step)
        if step == 0.0:
            return {"FINISHED"}

        current_size = self.dim_orig[0]
        if current_size == 0.0:
            return {"FINISHED"}

        target_size = _round_to_step(current_size + self.step, step)

        if target_size < self.min_size or target_size > self.max_size:
            return {"FINISHED"}

        scale = target_size / current_size
        bpy.ops.transform.resize(value=(scale, scale, scale), center_override=self.pivot)

        return {"FINISHED"}

    def invoke(self, context, event):
        obj = context.object
        if not obj:
            return {"CANCELLED"}

        self.dim_orig = obj.dimensions.to_tuple()
        self.pivot = obj.matrix_world.translation.to_tuple()
        return self.execute(context)
