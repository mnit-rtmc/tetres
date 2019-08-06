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
import ticas.common.log.TICASLogger;
import ticas.tetres.admin.TeTRESConfig;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SnowEventInfo extends InfoBase {

    public String start_time;
    public String end_time;

    public SnowEventInfo() {
        this.setTypeInfo(TeTRESConfig.INFO_TYPE_SNOWEVENT);
    }

    public void setDuration(Date sdt, Date edt) {
        this.start_time = this.DateToString(sdt);
        this.end_time = this.DateToString(edt);
    }

    public String getDuration() {
        Calendar sdt = this.toCalendar(this.start_time);
        Calendar edt = this.toCalendar(this.end_time);

        int syear = sdt.get(Calendar.YEAR);
        int smonth = sdt.get(Calendar.MONTH)+1;
        int sday = sdt.get(Calendar.DAY_OF_MONTH);

        int eyear = edt.get(Calendar.YEAR);
        int emonth = edt.get(Calendar.MONTH)+1;
        int eday = edt.get(Calendar.DAY_OF_MONTH);

        String sstr = String.format("%4d-%02d-%02d", syear, smonth, sday);
        String estr = null;
        if (syear == eyear && smonth == emonth) {
            estr = String.format("%02d", eday);
        } else if (syear == eyear) {
            estr = String.format("%02d-%02d", emonth, eday);
        } else {
            estr = String.format("%02d-%02d-%02d", eyear, emonth, eday);
        }
        return String.format("%s ~ %s", sstr, estr);
    }

    private Calendar toCalendar(String dts) {
        try {
            Date dt = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").parse(dts);
            Calendar cal = Calendar.getInstance();
            cal.setTime(dt);
            return cal;
        } catch (ParseException ex) {
            TICASLogger.getLogger(this.getClass().getName()).error("fail to change date string to Date");
            return null;
        }
    }

    private String DateToString(Date dt) {
        SimpleDateFormat formatter = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
        return formatter.format(dt);
    }

    @Override
    public SnowEventInfo clone() {
        Gson gson = new GsonBuilder().create();
        String json = gson.toJson(this);
        return gson.fromJson(json, SnowEventInfo.class);
    }
}
