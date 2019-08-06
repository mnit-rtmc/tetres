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
package ticas.common.ui;

import com.github.lgooddatepicker.timepicker.TimePicker;
import com.github.lgooddatepicker.timepicker.TimePickerSettings;
import com.github.lgooddatepicker.timepicker.TimePickerSettings.TimeIncrement;
import java.sql.Time;
import java.time.LocalTime;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TICASTimePicker extends TimePicker {

    public enum TimeInterval {
        FiveMinutes(TimeIncrement.FiveMinutes),
        TenMinutes(TimeIncrement.TenMinutes),
        FifteenMinutes(TimeIncrement.FifteenMinutes),
        TwentyMinutes(TimeIncrement.TwentyMinutes),
        ThirtyMinutes(TimeIncrement.ThirtyMinutes),
        OneHour(TimeIncrement.OneHour);

        public final TimeIncrement timeIncrement;

        private TimeInterval(TimeIncrement timeIncrement) {
            this.timeIncrement = timeIncrement;
        }

        public TimePickerSettings getTimePickerSettings() {
            if(this.timeIncrement == null) return null;
            TimePickerSettings tps = new TimePickerSettings();
            tps.generatePotentialMenuTimes(this.timeIncrement, LocalTime.of(0, 0, 0), LocalTime.of(23, 59, 59));
            return tps;
        }
    }

    public TICASTimePicker() {
        super(TimeInterval.FiveMinutes.getTimePickerSettings());
    }

    public TICASTimePicker(TimeInterval timeInterval) {
        super(timeInterval.getTimePickerSettings());
    }

    public static TimePicker create() {
        TimePickerSettings tps = new TimePickerSettings();
        tps.generatePotentialMenuTimes(TimeIncrement.FiveMinutes, LocalTime.of(0, 0, 0), LocalTime.of(23, 55, 0));
        return new TimePicker(tps);
    }

    public Time getTimeObject() {
        LocalTime lsdt = this.getTime();        
        if (lsdt == null) {
            return null;
        }
        return Time.valueOf(lsdt);
    }

    public void setTimeObject(Time dt) {
        this.setTime(dt.toLocalTime());
    }
}
