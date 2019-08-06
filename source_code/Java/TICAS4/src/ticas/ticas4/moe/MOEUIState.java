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
package ticas.ticas4.moe;

import ticas.common.ui.TimePanel;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JTextField;
import ticas.ticas4.ui.MOECheckBox;
import ticas.ticas4.ui.OptionCheckBox;
import java.util.Arrays;
import java.util.prefs.Preferences;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class MOEUIState {
    static final String prefNode = "ticas.moe";
    String groupID = "MOE";
    String outputPath = "";
    Integer time_interval_index = 0;
    Integer start_hour_index = 0;
    Integer start_min_index = 0;
    Integer end_hour_index = 0;
    Integer end_min_index = 0;
    Integer duration_index = 0;
    List<String> checkedOptions = new ArrayList<String>();
    List<String> checkedMOEs = new ArrayList<String>();
    
    public void update(String outputPath, TimePanel panTime) {        
        this.outputPath = outputPath;
        this.time_interval_index = panTime.cbxInterval.getSelectedIndex();
        this.start_hour_index = panTime.cbxStartHour.getSelectedIndex();
        this.start_min_index = panTime.cbxStartMin.getSelectedIndex();
        this.end_hour_index = panTime.cbxEndHour.getSelectedIndex();
        this.end_min_index = panTime.cbxEndMin.getSelectedIndex();
        this.duration_index = panTime.cbxDuration.getSelectedIndex();
        this.checkedMOEs = MOECheckBox.getCheckedBoxeNames(groupID);
        this.checkedOptions = OptionCheckBox.getCheckedBoxeNames(groupID);
        MOEUIState.save(this);
    }
    
    public void set(JTextField tbxOutputPath, TimePanel panTime) {
        tbxOutputPath.setText(this.outputPath);
        panTime.cbxInterval.setSelectedIndex(this.time_interval_index);
        panTime.cbxStartHour.setSelectedIndex(this.start_hour_index);
        panTime.cbxStartMin.setSelectedIndex(this.start_min_index);
        panTime.cbxEndHour.setSelectedIndex(this.end_hour_index);
        panTime.cbxEndMin.setSelectedIndex(this.end_min_index);
        panTime.cbxDuration.setSelectedIndex(this.duration_index);        
        for(MOECheckBox cbx : MOECheckBox.getCheckBoxes(groupID)) {
            if(this.checkedMOEs.contains(cbx.name)) {
                cbx.setSelected(true);
            }
        }        
        for(OptionCheckBox cbx : OptionCheckBox.getCheckBoxes(groupID)) {
            if(this.checkedOptions.contains(cbx.name)) {
                cbx.setSelected(true);
            }
        }        
    }
    
    private static void save(MOEUIState state) {
        Preferences prefs = Preferences.userRoot().node(prefNode);
        String checked_moes = state.checkedMOEs.toString().replaceAll(", ","\t");
        String checked_options = state.checkedOptions.toString().replaceAll(", ","\t");
        prefs.putInt("time_interval_index", state.time_interval_index);
        prefs.putInt("start_hour_index", state.start_hour_index);
        prefs.putInt("start_min_index", state.start_min_index);
        prefs.putInt("end_hour_index", state.end_hour_index);
        prefs.putInt("end_min_index", state.end_min_index);
        prefs.putInt("duration_index", state.duration_index);
        prefs.put("checked_moes", checked_moes);
        prefs.put("checked_options", checked_options);
        prefs.put("output_path", state.outputPath);
    }
    
    public static MOEUIState load() {
        Preferences prefs = Preferences.userRoot().node(prefNode);
        MOEUIState state = new MOEUIState();        
        state.time_interval_index = prefs.getInt("time_interval_index", 0);
        state.start_hour_index = prefs.getInt("start_hour_index", 0);
        state.start_min_index = prefs.getInt("start_min_index", 0);
        state.end_hour_index = prefs.getInt("end_hour_index", 0);
        state.end_min_index = prefs.getInt("end_min_index", 0);
        state.duration_index = prefs.getInt("duration_index", 0);
        String checked_moes_str = prefs.get("checked_moes", "");
        state.checkedMOEs.addAll(Arrays.asList(checked_moes_str.replaceAll("\\[|\\]", "").split("\t")));        
        String checked_options_str = prefs.get("checked_options", "");
        state.checkedOptions.addAll(Arrays.asList(checked_options_str.replaceAll("\\[|\\]", "").split("\t")));        
        state.outputPath = prefs.get("output_path", "");
        return state;
    }
}
