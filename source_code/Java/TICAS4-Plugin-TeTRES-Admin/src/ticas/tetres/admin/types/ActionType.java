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
package ticas.tetres.admin.types;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class ActionType {
    public static String INSERT = "insert";
    public static String UPDATE = "update";
    public static String DELETE = "delete";
    
    public static String DT_TTROUTE = "tt_route";
    public static String DT_WEATHER = "weather";
    public static String DT_INCIDENT = "incident";
    public static String DT_WORKZONE = "workzone";
    public static String DT_WORKZONE_GROUP = "workzone_group";
    public static String DT_SPECIALEVENT = "special_event";
    public static String DT_SNOWEVENT = "snow_event";
    public static String DT_SNOWROUTE = "snow_route";
    public static String DT_SNOWMGMT = "snow_management";
    
    public static String STATUS_WAIT = "wait";
    public static String STATUS_FAIL = "fail";
    public static String STATUS_RUNNING = "running";
    public static String STATUS_DONE = "done";
    
}
