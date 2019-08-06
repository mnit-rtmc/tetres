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
package ticas.common.pyticas.types;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RouteConfigInfo {
    public String __module__;
    public String __class__;    
    public Integer ramp_opened; // 1 : open, -1 : close, 0 : N/A
    public List<String> lane_types = new ArrayList<String>();
    public List<Integer> closed_lanes = new ArrayList<Integer>();
    public List<Integer> od_lanes = new ArrayList<Integer>();
    public List<Integer> co_lanes = new ArrayList<Integer>();
    public List<Integer> shifted_lanes = new ArrayList<Integer>();
    public Map<Integer, String> shift_dirs = new HashMap<Integer, String>();    
}
