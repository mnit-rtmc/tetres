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
package common.ui;

import common.infra.Infra;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.URL;
import java.net.UnknownHostException;
import java.util.*;

/**
 * 
 * @author Chongmyung Park
 */
public final class DateChecker implements IDateChecker {

    private static final DateChecker realInstance = new DateChecker();
    
    private final List<Integer> loadedYear = new ArrayList<Integer>();
    private final List<String> availableDates = new ArrayList<String>();
    private final Infra infra = Infra.getInstance();
    static private boolean hasError = false;
    
    private DateChecker() {
        Calendar c = Calendar.getInstance();
        int thisYear = c.get(Calendar.YEAR);
        loadDates(thisYear);
        //loadDates(new int[]{thisYear, thisYear-1, thisYear-2});
    }

    public static DateChecker getInstance() {
        return realInstance;
    }

    public void loadDates(int year) {
        try {
            if(hasError) return;
            
            URL url = new URL(infra.getConfig().TRAFFIC_DATA_URL + "/" + year);
            loadedYear.add(year);
            String str;
            BufferedReader br;
            br = new BufferedReader(new InputStreamReader(url.openStream()));
            while ((str = br.readLine()) != null) {
                availableDates.add(str);
            }
            br.close();
        } catch (UnknownHostException ex) {    
            ex.printStackTrace();
            hasError = true;
            loadedYear.remove(loadedYear.size()-1);
        } catch (IOException ex) {
            ex.printStackTrace();
            hasError = true;
            loadedYear.remove(loadedYear.size()-1);
        } catch (Exception ex) {
            ex.printStackTrace();
            hasError = true;
            loadedYear.remove(loadedYear.size()-1);
        }
    }
    
    public void loadDates(int[] years)
    {
        for(int y : years) loadDates(y);
    }

    @Override
    public boolean isAvailable(Calendar c) {
        String dateString = String.format("%4d%02d%02d", c.get(Calendar.YEAR), c.get(Calendar.MONTH) + 1, c.get(Calendar.DAY_OF_MONTH));
        int year = c.get(Calendar.YEAR);
        if(!loadedYear.contains(year)) {
            loadDates(year);
        }
        return availableDates.contains(dateString);
    }
    
    @Override
    public boolean isAvailable(Date date) {
        Calendar c = Calendar.getInstance();
        c.setTime(date);
        return isAvailable(c);
    }    
}
