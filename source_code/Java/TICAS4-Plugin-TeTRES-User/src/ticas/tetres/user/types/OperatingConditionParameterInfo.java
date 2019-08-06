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
package ticas.tetres.user.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.tetres.user.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class OperatingConditionParameterInfo extends InfoBase {

    public Float incident_downstream_distance_limit;
    public Float incident_upstream_distance_limit;
    public Integer incident_keep_in_minute;
    
    public Float workzone_downstream_distance_limit;
    public Float workzone_upstream_distance_limit;    
    public Float workzone_length_short_from;
    public Float workzone_length_short_to;
    public Float workzone_length_medium_from;
    public Float workzone_length_medium_to;
    public Float workzone_length_long_from;
    public Float workzone_length_long_to;
    
    public Integer specialevent_size_small_from;
    public Integer specialevent_size_small_to;
    public Integer specialevent_size_medium_from;
    public Integer specialevent_size_medium_to;
    public Integer specialevent_size_large_from;
    public Integer specialevent_size_large_to;
    public Float specialevent_distance_near_from;
    public Float specialevent_distance_near_to;
    public Float specialevent_distance_middle_from;
    public Float specialevent_distance_middle_to;
    public Float specialevent_distance_far_from;
    public Float specialevent_distance_far_to;

    public OperatingConditionParameterInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OPERATING_CONDITION_PARAM);
    }

    public static OperatingConditionParameterInfo fromJSON(String jsonString) {
        Gson gson = new GsonBuilder().create();
        return gson.fromJson(jsonString, OperatingConditionParameterInfo.class);
    }

    public String toJSON() {
        Gson gson = new GsonBuilder().create();
        return gson.toJson(this);
    }

    @Override
    public OperatingConditionParameterInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, OperatingConditionParameterInfo.class);
    }
}
