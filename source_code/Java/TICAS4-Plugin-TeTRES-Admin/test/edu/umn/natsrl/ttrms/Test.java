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
/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */

package edu.umn.natsrl.ttrms;

public class Test {
    public static void main(String[] args) {
        long value = 1123200000;
        double diffMinutes = value / (60.0 * 1000) ;
        double diffHours = value / (60.0 * 1000 * 60) ;
        double diffDays = value / (60.0 * 1000 * 60 * 24) ;
        System.out.println("value=" + value + ", minute=" + diffMinutes + ", hours=" + diffHours + ", days=" + diffDays);
    }
}
