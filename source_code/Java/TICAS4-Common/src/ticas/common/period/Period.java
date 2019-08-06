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

package ticas.common.period;

import java.io.Serializable;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.Vector;

/**
 *
 * @author Chongmyung Park
 */
public class Period implements Serializable {
    public Date startDate;
    public Date endDate;
    public int start_year, start_month, start_date, start_hour, start_min;
    public int end_year, end_month, end_date, end_hour, end_min;
    public int interval = Interval.getMinTMCInterval();   // 30s data

    public Period(Date startDate, Date endDate, int interval) {
        this.setTimes(startDate, endDate);
        this.interval = interval;       
    }

    public Period(Period period) {
        this.setTimes(period.startDate, period.endDate);
        this.interval = period.interval;
    }
    
    private void setTimes(Date startDate, Date endDate)
    {
        this.startDate = startDate;
        this.endDate = endDate;

        Calendar c = Calendar.getInstance();
        c.setTime(startDate);
        this.start_year = c.get(Calendar.YEAR);
        this.start_month = c.get(Calendar.MONTH)+1;
        this.start_date = c.get(Calendar.DATE);
        this.start_hour = c.get(Calendar.HOUR_OF_DAY);
        this.start_min = c.get(Calendar.MINUTE);
        
        c.setTime(endDate);
        this.end_year = c.get(Calendar.YEAR);
        this.end_month = c.get(Calendar.MONTH)+1;
        this.end_date = c.get(Calendar.DATE);
        this.end_hour = c.get(Calendar.HOUR_OF_DAY);
        this.end_min = c.get(Calendar.MINUTE);        
    }

    public int getHowManyDays()
    {
        Calendar c = Calendar.getInstance();
        c.setTime(startDate);
        int count = 1;

        while(true)
        {
            if(isSameDay(c.getTime(), this.endDate)) return count;
            c.add(Calendar.DATE, 1);
            count++;
        }
    }
    
    public int getIntervalPeriod(){
        Calendar c = Calendar.getInstance();
        c.setTime(startDate);
        int count = 0;

        while(true)
        {
            if(isSameTime(c.getTime(), this.endDate)) return count;
            c.add(Calendar.SECOND, interval);
            count++;
        }
    }

    
    public String[] getTimeline()
    {
        if(this.getHowManyDays() > 1) return getTimelineWithDate();
        else return getTimelineJustTime();
    }
    
    public String[] getTimelineWithDate()
    {
        Vector<String> timeline = new Vector<String>();
        Calendar c = Calendar.getInstance();
        c.setTime(this.startDate);
        Calendar ce = Calendar.getInstance();
        ce.setTime(this.endDate);
        DecimalFormat df = new DecimalFormat("00");
        while(c.getTimeInMillis()/1000 < ce.getTimeInMillis()/1000)
        {
            c.add(Calendar.SECOND, interval);
            String time = c.get(Calendar.YEAR)+"-"+
                    df.format(c.get(Calendar.MONTH)+1)+"-"+
                    df.format(c.get(Calendar.DATE))+" "+
                    df.format(c.get(Calendar.HOUR_OF_DAY))+":"+
                    df.format(c.get(Calendar.MINUTE))+":"+
                    df.format(c.get(Calendar.SECOND))
                    ;
            timeline.add(time);
        }
        return timeline.toArray(new String[timeline.size()]);
    }

    public String[] getTimelineJustTime()
    {
        Vector<String> timeline = new Vector<String>();
        Calendar c = Calendar.getInstance();
        c.setTime(this.startDate);
        
        Calendar ce = Calendar.getInstance();
        ce.setTime(this.endDate);
        DecimalFormat df = new DecimalFormat("00");
        
        while(c.getTimeInMillis()/1000 < ce.getTimeInMillis()/1000)
        {
            c.add(Calendar.SECOND, interval);
            String time = df.format(c.get(Calendar.HOUR_OF_DAY))+":"+df.format(c.get(Calendar.MINUTE))+":"+df.format(c.get(Calendar.SECOND));
            timeline.add(time);
        }
        return timeline.toArray(new String[timeline.size()]);
    }

    boolean isSameDay(Date d1, Date d2) {
        Calendar c1 = Calendar.getInstance();
        Calendar c2 = Calendar.getInstance();
        c1.setTime(d1);
        c2.setTime(d2);
        if (c1.get(Calendar.YEAR) == c2.get(Calendar.YEAR) && c1.get(Calendar.MONTH) == c2.get(Calendar.MONTH) && c1.get(Calendar.DATE) == c2.get(Calendar.DATE)) {
            return true;
        } else {
            return false;
        }
    }
    
    boolean isSameTime(Date d1, Date d2) {
        if(!isSameDay(d1,d2)){
            return false;
        }
        
        Calendar c1 = Calendar.getInstance();
        Calendar c2 = Calendar.getInstance();
        c1.setTime(d1);
        c2.setTime(d2);
        if (c1.get(Calendar.HOUR) == c2.get(Calendar.HOUR) && c1.get(Calendar.MINUTE) == c2.get(Calendar.MINUTE) && c1.get(Calendar.SECOND) == c2.get(Calendar.SECOND)) {
            return true;
        } else {
            return false;
        }
    }
    
    public String getPeriodStringWithoutTime(){
        return String.format("%4d%02d%02d", 
                this.start_year, this.start_month, this.start_date);
    }
    
    public String getPeriodStringHWithoutTime(){
        return String.format("%4d-%02d-%02d", 
                this.start_year, this.start_month, this.start_date);
    }
    
    public String getPeriodString()
    {
        return String.format("%4d%02d%02d%02d%02d-%4d%02d%02d%02d%02d", 
                this.start_year, this.start_month, this.start_date, this.start_hour, this.start_min,
                this.end_year, this.end_month, this.end_date, this.end_hour, this.end_min
                );
    }
    
    public void setInterval(int interval)
    {
        this.interval = interval;
    }
    
    @Override
    public String toString()
    {
        return "START : " + this.startDate.toString() + "\nEND : " + this.endDate.toString();
    }

    public void addStartHour(int h) {
        Calendar c = Calendar.getInstance();
        c.setTime(this.startDate);
        c.add(Calendar.HOUR, h);
        this.setTimes(c.getTime(), this.endDate);
    }    
    
    public void addEndHour(int h) {
        Calendar c = Calendar.getInstance();
        c.setTime(this.endDate);
        c.add(Calendar.HOUR, h);
        this.setTimes(this.startDate, c.getTime());
    }
    
    @Override
    public Period clone()
    {
        return new Period(this);
    }

    public void syncInterval() {
        int gap = (start_min - end_min);
        int minterval = interval / 60;
//        System.out.println("gap : " +gap);
        int addTime = minterval == 0 ? gap : gap % minterval;
//        System.out.println("addTime : " +addTime);
        if(start_min < end_min)
            addTime = minterval - addTime;
//        System.out.println("interval - addTime : " +addTime);
        if(addTime == 0)
            return;
        
        Calendar c = Calendar.getInstance();
        c.setTime(endDate);
        SimpleDateFormat dateformatter = new SimpleDateFormat("yyyy.MM.dd HH:mm");
//        System.out.println("beforetime : "+dateformatter.format(c.getTime()));
        c.add(Calendar.MINUTE, addTime);
//        System.out.println("aftertime : "+dateformatter.format(c.getTime()));
        this.setTimes(startDate,c.getTime());
    }
}
