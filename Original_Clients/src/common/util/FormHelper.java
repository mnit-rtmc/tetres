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
package common.util;

import java.util.ArrayList;
import java.util.List;
import javax.swing.text.Document;
import javax.swing.text.PlainDocument;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class FormHelper {

    // only accept integer or blank (if 'acceptBlank' is set to true)
    public static void setIntegerFilter(Document doc, boolean acceptBlank) {
        PlainDocument pd = (PlainDocument) doc;
        pd.setDocumentFilter(new DocFilterInteger());
    }

    // only accept float or blank (if 'acceptBlank' is set to true)
    public static void setDoubleFilter(Document doc, boolean acceptBlank) {
        PlainDocument pd = (PlainDocument) doc;
        pd.setDocumentFilter(new DocFilterFloat());
    }

    public static Integer getInteger(String content) {
        if (content == null || content.equals("")) {
            return null;
        }
        return Integer.parseInt(content);
    }

    public static Double getDouble(String content) {
        if (content == null || content.equals("")) {
            return null;
        }
        return Double.parseDouble(content);
    }

    public static List<Integer> getIntegerList(String value) {
        List<Integer> vList = new ArrayList<Integer>();
        if (value.trim().isEmpty()) {
            return vList;
        }
        for (String v : value.split(",")) {
            try {
                vList.add(Integer.parseInt(v));
            } catch (Exception ex) {
                return null;
            }
        }
        return vList;
    }
    
    public static List<Double> getDoubleList(String value) {
        List<Double> vList = new ArrayList<Double>();
        if (value.trim().isEmpty()) {
            return vList;
        }
        for (String v : value.split(",")) {
            try {
                vList.add(Double.parseDouble(v));
            } catch (Exception ex) {
                return null;
            }
        }
        return vList;
    }    
}
