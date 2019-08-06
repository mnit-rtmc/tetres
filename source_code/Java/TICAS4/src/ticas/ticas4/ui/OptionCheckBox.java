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
public class OptionCheckBox extends JCheckBox {
    
    private static HashMap<String, List<OptionCheckBox>> boxes = new HashMap<String, List<OptionCheckBox>>();    
        
    public String name;
    
    public OptionCheckBox(String groupId, String name) {
        super();
        this.name = name;       
        List checkList = boxes.get(groupId);
        if(checkList == null) {
            checkList = new ArrayList<OptionCheckBox>();
            boxes.put(groupId, checkList);
        }
        checkList.add(this);
    }

    public static List<OptionCheckBox> getCheckBoxes(String groupId) {
        List<OptionCheckBox> checkList = boxes.get(groupId);
        if(checkList == null) return new ArrayList<OptionCheckBox>();
        return checkList;
    }
    
    public static List<OptionCheckBox> getCheckedBoxes(String groupId) {
        List<OptionCheckBox> checkedList = new ArrayList<OptionCheckBox>();
        List<OptionCheckBox> chkboxList = OptionCheckBox.getCheckBoxes(groupId);
        for (OptionCheckBox chkbox : chkboxList) {
            if (chkbox.isSelected()) {
                checkedList.add(chkbox);
            }
        }
        return checkedList;
    }    

    public static List<String> getCheckedBoxeNames(String groupId) {
        List<String> checkedList = new ArrayList<String>();
        List<OptionCheckBox> chkboxList = OptionCheckBox.getCheckBoxes(groupId);
        for (OptionCheckBox chkbox : chkboxList) {
            if (chkbox.isSelected()) {
                checkedList.add(chkbox.name);
            }
        }
        return checkedList;
    }        
}
