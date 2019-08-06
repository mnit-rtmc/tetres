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
package ticas.ticas4.ui;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import javax.swing.JCheckBox;

/**
 * Custom Checkbox Class inherited from JCheckBox for TICAS Interface
 * @author Chongmyung Park
 */
public class MOECheckBox extends JCheckBox {
    
    private static HashMap<String, List<MOECheckBox>> boxes = new HashMap<String, List<MOECheckBox>>();    
    public String name;
    public String uri;
    
    public MOECheckBox(String groupId, String name, String uri) {
        super();
        this.name = name;
        this.uri = uri;
        
        List checkList = boxes.get(groupId);
        if(checkList == null) {
            checkList = new ArrayList<MOECheckBox>();
            boxes.put(groupId, checkList);
        }
        checkList.add(this);
    }

    public static List<MOECheckBox> getCheckBoxes(String groupId) {
        List<MOECheckBox> checkList = boxes.get(groupId);
        if(checkList == null) return new ArrayList<MOECheckBox>();
        return checkList;
    }
    
    public static List<MOECheckBox> getCheckedBoxes(String groupId) {
        List<MOECheckBox> estList = new ArrayList<MOECheckBox>();
        List<MOECheckBox> chkboxList = MOECheckBox.getCheckBoxes(groupId);
        for (MOECheckBox chkbox : chkboxList) {
            if (chkbox.isSelected()) {
                estList.add(chkbox);
            }
        }
        return estList;
    }    
    
    public static List<String> getCheckedBoxeNames(String groupId) {
        List<String> estList = new ArrayList<String>();
        List<MOECheckBox> chkboxList = MOECheckBox.getCheckBoxes(groupId);
        for (MOECheckBox chkbox : chkboxList) {
            if (chkbox.isSelected()) {
                estList.add(chkbox.name);
            }
        }
        return estList;
    }       
    
}
