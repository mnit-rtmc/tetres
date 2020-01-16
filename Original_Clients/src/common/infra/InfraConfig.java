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

import java.util.List;
/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class InfraConfig {
    public Float RADIUS_IN_EARTH_FOR_MILE = 3955.7f;
    public Integer FEET_PER_MILE = 5280;
    public Integer MAX_OCCUPANCY;
    public Integer MAX_SCANS;
    public Integer MAX_SPEED;
    public Integer MAX_VOLUME;
    public Integer MISSING_DATA;
    public List<RWISGroup> RWIS_SITE_INFO;
    public Integer SAMPLES_PER_DAY;
    public Integer SAMPLES_PER_HOUR;
    public String TRAFFIC_DATA_URL;
  
    public String ROUTE_CLASS;
    public String ROUTE_MODULE;
}