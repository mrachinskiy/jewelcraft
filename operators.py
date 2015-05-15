# ##### BEGIN MIT LICENSE BLOCK #####
#
# Copyright (c) 2015 Mikhail Rachinskiy
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ##### END MIT LICENSE BLOCK #####

import bpy
from bpy.types import Operator
from . import helpers



class IMPORT_GEM(Operator):
	'''Create selected gemstone'''
	bl_label = "Make Gemstone"
	bl_idname = "jewelcraft.import_gem"

	def execute(self, context):
		helpers.Import().gem()
		return {'FINISHED'}


class IMPORT_TYPE(Operator):
	'''Change type of selected gemstones'''
	bl_label = "Change Type"
	bl_idname = "jewelcraft.import_type"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		helpers.Import().type()
		return {'FINISHED'}


class IMPORT_CUT(Operator):
	'''Change cut of selected gemstones'''
	bl_label = "Change Cut and Size"
	bl_idname = "jewelcraft.import_cut"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		helpers.Import().cut()
		return {'FINISHED'}


class IMPORT_PRONGS(Operator):
	'''Create prongs for selected gemstones'''
	bl_label = "Change Cut and Size"
	bl_idname = "jewelcraft.import_prongs"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		helpers.Import().prongs()
		return {'FINISHED'}


class IMPORT_CUTTER(Operator):
	'''Create cutters for selected gemstones'''
	bl_label = "Change Cut and Size"
	bl_idname = "jewelcraft.import_cutter"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		helpers.Import().cutter()
		return {'FINISHED'}


class MAKE_DUPLIFACE(Operator):
	'''Create dupliface for selected objects'''
	bl_label = "Make Dupli-face"
	bl_idname = "jewelcraft.make_dupliface"

	@classmethod
	def poll(cls, context):
		return context.selected_objects

	def execute(self, context):
		helpers.Utils().make_dupliface()
		return {'FINISHED'}


class EXPORT_STATS(Operator):
	'''Export statistics for the project'''
	bl_label = "Export Stats"
	bl_idname = "jewelcraft.export_stats"

	def execute(self, context):
		helpers.Export()
		return {'FINISHED'}
