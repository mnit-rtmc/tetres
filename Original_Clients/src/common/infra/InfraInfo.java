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

import common.pyticas.ApiURIs;
import common.pyticas.PyTypeInfo;
import java.util.List;
import java.util.Map;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class InfraInfo {
    public InfraConfig config;
    public ApiURIs api_urls;
    public PyTypeInfo route_info;
    public List<Corridor> corridor_list;
    public Map<String, RNode> rnode_list;
    public Map<String, Detector> detector_list;
    public Map<String, DMS> dms_list;
    public Map<String, Camera> camera_list;
    public Map<String, Meter> meter_list;
}
