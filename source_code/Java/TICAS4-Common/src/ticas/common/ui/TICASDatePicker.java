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

import com.github.lgooddatepicker.datepicker.DatePicker;
import java.time.LocalDate;
import java.time.ZoneId;
import java.util.Date;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TICASDatePicker extends DatePicker {

    public Date getDateObject() {
        LocalDate ldt = this.getDate();
        if(ldt == null) {
            return null;
        }
        return Date.from(ldt.atStartOfDay(ZoneId.systemDefault()).toInstant());
    }

    public void setDateObject(Date dt) {
        this.setDate(dt.toInstant().atZone(ZoneId.systemDefault()).toLocalDate());
    }
}
