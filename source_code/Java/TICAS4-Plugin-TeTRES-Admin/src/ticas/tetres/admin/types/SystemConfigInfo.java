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

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import ticas.tetres.admin.TeTRESConfig;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SystemConfigInfo extends InfoBase {

    public Integer data_archive_start_year;
    public String daily_job_start_time;
    public Integer daily_job_offset_days;
    public String weekly_job_start_day;
    public String weekly_job_start_time;
    public Integer monthly_job_start_date;
    public String monthly_job_start_time;
    public Float incident_downstream_distance_limit;
    public Float incident_upstream_distance_limit;
    public Float workzone_downstream_distance_limit;
    public Float workzone_upstream_distance_limit;
    public Integer specialevent_arrival_window;
    public Integer specialevent_departure_window1;
    public Integer specialevent_departure_window2;

    public SystemConfigInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_SYSTEMCONFIG);
    }

    @Override
    public SystemConfigInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, SystemConfigInfo.class);
    }
}
