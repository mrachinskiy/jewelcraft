# ##### BEGIN GPL LICENSE BLOCK #####
#
#  mod_update automatic add-on updates.
#  Copyright (C) 2019-2020  Mikhail Rachinskiy
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# ##### END GPL LICENSE BLOCK #####


CHECKING = 0
INSTALLING = 1
COMPLETED = 2
ERROR = 3

status: int = None
days_passed: int = None
update_version: str = None
download_url: str = None
changelog_url: str = None
error_msg: str = None

update_available: bool = False
