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

import com.github.lgooddatepicker.datetimepicker.DateTimePicker;
import com.github.lgooddatepicker.timepicker.TimePickerSettings;
import com.github.lgooddatepicker.timepicker.TimePickerSettings.TimeIncrement;
import java.sql.Timestamp;
import java.time.Instant;
import java.time.LocalDateTime;
import java.time.LocalTime;
import java.time.ZoneId;
import java.util.Date;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TICASDateTimePicker extends DateTimePicker {

    public enum TimeInterval {
        FiveMinutes(TimeIncrement.FiveMinutes),
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

    public TICASDateTimePicker() {
        super(null, TimeInterval.FiveMinutes.getTimePickerSettings());
    }

    public TICASDateTimePicker(TimeInterval timeInterval) {
        super(null, timeInterval.getTimePickerSettings());
    }

    public static DateTimePicker create() {
        TimePickerSettings tps = new TimePickerSettings();
        tps.generatePotentialMenuTimes(TimeIncrement.FiveMinutes, LocalTime.of(0, 0, 0), LocalTime.of(23, 55, 0));
        return new DateTimePicker(null, tps);
    }

    public Date getDate() {
        LocalDateTime lsdt = this.getDateTime();
        if (lsdt == null) {
            return null;
        }
        return Timestamp.valueOf(lsdt);
    }

    public void setDate(Date dt) {
        LocalDateTime sdt = LocalDateTime.ofInstant(
                Instant.ofEpochMilli(dt.getTime()),
                ZoneId.systemDefault());
        this.setDateTime(sdt);
    }
}
