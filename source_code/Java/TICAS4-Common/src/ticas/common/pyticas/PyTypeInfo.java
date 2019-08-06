/*
 * Copyright (C) 2018 NATSRL @ UMD (University Minnesota Duluth)
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package ticas.common.pyticas;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class PyTypeInfo {
    public String __module__;
    public String __class__;

    public PyTypeInfo(String __module__, String __class__) {
        this.__module__ = __module__;
        this.__class__ = __class__;
    }    
}
