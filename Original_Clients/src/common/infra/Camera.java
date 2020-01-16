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

package common.infra;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class Camera extends InfraObject {
    public String corridor_name;    
    public String description;      
    public String label;      
    public String up_station;          
    public String down_station;    
    public Float lat;
    public Float lon;
    public Float distance_from_first_station;
}
