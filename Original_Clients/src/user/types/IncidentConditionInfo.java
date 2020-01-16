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
public class IncidentConditionInfo extends FilterInfo {

    public String type;
    public String impact;
    public String severity;

    public IncidentConditionInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OC_INCIDENT);
    }
    
    public IncidentConditionInfo(String type, String intensity, String severity) {
        this.type = type;
        this.impact = intensity;
        this.severity = severity;
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OC_INCIDENT);
    }    

    @Override
    public IncidentConditionInfo fromJSON(String jsonString) {
        Gson gson = new GsonBuilder().create();
        return gson.fromJson(jsonString, IncidentConditionInfo.class);
    }
    
    @Override
    public String toJSON() {
        Gson gson = new GsonBuilder().create();
        return gson.toJson(this);
    }
    
    @Override
    public IncidentConditionInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, IncidentConditionInfo.class);
    }           
}
