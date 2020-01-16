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
package user.types;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import user.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SnowmanagementConditionInfo extends FilterInfo {

    public String road_condition;

    public SnowmanagementConditionInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OC_SNOWMGMT);
    }
    
    public SnowmanagementConditionInfo(String road_condition) {
        this.road_condition = road_condition;
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OC_SNOWMGMT);
    }    

    @Override
    public SnowmanagementConditionInfo fromJSON(String jsonString) {
        Gson gson = new GsonBuilder().create();
        return gson.fromJson(jsonString, SnowmanagementConditionInfo.class);
    }
    
    @Override
    public String toJSON() {
        Gson gson = new GsonBuilder().create();
        return gson.toJson(this);
    }
    
    @Override
    public SnowmanagementConditionInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, SnowmanagementConditionInfo.class);
    }        
}
