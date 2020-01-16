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
package common.period;

/**
 *
 * @author Chongmyung Park
 */
public enum Interval {
    
    I10SEC(10, "10 second"),
    I30SEC(30, "30 second"),
    I1MIN(60, "1 min"),
    I2MIN(120, "2 min"),
    I3MIN(180, "3 min"),
    I4MIN(240, "4 min"),
    I5MIN(300, "5 min"),
    I10MIN(600, "10 min"),
    I15MIN(900, "15 min"),
    I20MIN(1200, "20 min"),
    I30MIN(1800, "30 min"),
    I1HOUR(3600, "1 hour");

        public static int getMinInterval() {
                int cstep = Integer.MAX_VALUE;
                for(Interval in : Interval.values()){
                        cstep = Math.min(cstep, in.second);
                }
                return cstep;
        }
        
        public static int getMinTMCInterval(){
                return Interval.I30SEC.second;
        }
        
        public static int getMinSimulationInterval(){
                return getMinInterval();
//                return Interval.I30SEC.second;
        }
        
        public static Interval getDefaultSimulationInterval(){
                return Interval.I30SEC;
        }
    
    // interval in second
    public final int second;
    
    // string value for displaying
    public final String description;

    // construct
    private Interval(int second, String desc) {
        this.second = second;
        this.description = desc;
    }
    
    public static Interval get(int second)
    {
        for(Interval i : Interval.values())
        {
            if(i.second == second) return i;
        }
        return null;
    }
    
    @Override
    public String toString()
    {
        return this.description;
    }
    
    public int getSecond(){
            return second;
    }
}
