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
public class SystemConfigInfo2 extends InfoBase {

    public Integer data_archive_start_year;
    public String daily_job_start_time;
    public Integer daily_job_offset_days;
    public String weekly_job_start_day;
    public String weekly_job_start_time;
    public String monthly_job_start_date;
    public String monthly_job_start_time;
    public Float incident_distance_limit;
    public Float workzone_distance_limit;
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
    public Float specialevent_arrival_window;
    public Float specialevent_departure_window1;
    public Float specialevent_departure_window2;
    public Float snowmgmt_distance_limit;

    public SystemConfigInfo2() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_SYSTEMCONFIG);
    }

    @Override
    public SystemConfigInfo2 clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, SystemConfigInfo2.class);
    }
}
