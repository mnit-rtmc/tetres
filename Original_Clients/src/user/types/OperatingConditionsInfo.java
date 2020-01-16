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
import java.util.ArrayList;
import java.util.List;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class OperatingConditionsInfo extends InfoBase {

    public String name;
    public String desc;
    public List<WeatherConditionInfo> weather_conditions;
    public List<IncidentConditionInfo> incident_conditions;
    public List<WorkzoneConditionInfo> workzone_conditions;
    public List<SpecialeventConditionInfo> specialevent_conditions;
    public List<SnowmanagementConditionInfo> snowmanagement_conditions;
    
    public OperatingConditionsInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OPERATING_CONDITIONS);
    }
    public OperatingConditionsInfo(String name, String desc) {
        this.name = name;
        this.desc = desc;
        this.weather_conditions = new ArrayList<WeatherConditionInfo>();
        this.incident_conditions = new ArrayList<IncidentConditionInfo>();
        this.workzone_conditions = new ArrayList<WorkzoneConditionInfo>();
        this.specialevent_conditions = new ArrayList<SpecialeventConditionInfo>();
        this.snowmanagement_conditions = new ArrayList<SnowmanagementConditionInfo>();
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OPERATING_CONDITIONS);        
    }
    
    public OperatingConditionsInfo(String name, String desc, 
            List<WeatherConditionInfo> weatherFilterInfos, 
            List<IncidentConditionInfo> incidentFilterInfos, 
            List<WorkzoneConditionInfo> workzoneFilterInfos, 
            List<SpecialeventConditionInfo> specialEventFilterInfos, 
            List<SnowmanagementConditionInfo> snowManagementFilterInfos) {
        this.name = name;
        this.desc = desc;
        this.weather_conditions = weatherFilterInfos;
        this.incident_conditions = incidentFilterInfos;
        this.workzone_conditions = workzoneFilterInfos;
        this.specialevent_conditions = specialEventFilterInfos;
        this.snowmanagement_conditions = snowManagementFilterInfos;
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_OPERATING_CONDITIONS);
    }

    public static OperatingConditionsInfo fromJSON(String jsonString) {
        Gson gson = new GsonBuilder().create();
        return gson.fromJson(jsonString, OperatingConditionsInfo.class);
    }

    public String toJSON() {
        Gson gson = new GsonBuilder().create();
        return gson.toJson(this);
    }

    @Override
    public String toString() {
        return this.name;
    }

    @Override
    public OperatingConditionsInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, OperatingConditionsInfo.class);
    }
}
