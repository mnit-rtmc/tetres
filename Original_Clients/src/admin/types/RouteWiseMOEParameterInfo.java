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
package admin.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import admin.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RouteWiseMOEParameterInfo extends InfoBase {

    public int reference_tt_route_id;
    public Float moe_lane_capacity;
    public Float moe_critical_density;
    public Float moe_congestion_threshold_speed;
    public String start_time;
    public String end_time;
    public String update_time;
    public String status;
    public String reason;

    public RouteWiseMOEParameterInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_ROUTE_WISE_MOE_PARAMETER);
    }
    @Override
    public String toString() {
        return this.reference_tt_route_id + "";
    }

    @Override
    public RouteWiseMOEParameterInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, RouteWiseMOEParameterInfo.class);
    }
}
