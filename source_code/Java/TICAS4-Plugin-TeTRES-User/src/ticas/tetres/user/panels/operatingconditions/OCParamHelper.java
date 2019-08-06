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
package ticas.tetres.user.panels.operatingconditions;

import ticas.common.infra.Infra;
import ticas.tetres.user.TeTRESConfig;
import ticas.common.util.FileHelper;
import ticas.common.util.DataHelper;
import java.io.File;
import java.io.IOException;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;
import ticas.tetres.user.types.OperatingConditionParameterInfo;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class OCParamHelper {

    public static OperatingConditionParameterInfo loadParam() {
        String filePath = cfgFilePath();
        if(filePath == null) {
            return defaultParam();
        }
        File f = new File(filePath);
        if (!f.exists()) {
            return defaultParam();
        }
        try {
            String jsonContent = FileHelper.readTextFile(filePath);
            return OperatingConditionParameterInfo.fromJSON(jsonContent);
        } catch (IOException ex) {
            Logger.getLogger(PanelOperatingConditionConfig.class.getName()).log(Level.SEVERE, null, ex);
            return defaultParam();
        }
    }

    static boolean save(OperatingConditionParameterInfo ocParam) {
        String filePath = cfgFilePath();
        try {
            FileHelper.writeTextFile(ocParam.toJSON(), filePath);
        } catch (IOException ex) {
            Logger.getLogger(PanelOperatingConditionConfig.class.getName()).log(Level.SEVERE, null, ex);
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to save the operating condition parameters");
            return false;
        }
        return DataHelper.uploadData();
    }

    private static String cfgFilePath() {
        if(!Infra.getInstance().isInfraReady()) {
            return null;
        }
        String dataPath = Infra.getInstance().getDataPath();
        String filterDirPath = dataPath + File.separator + "tetres" + File.separator + "configs";
        if (!FileHelper.exists(filterDirPath)) {
            FileHelper.createDirs(filterDirPath);
        }
        String _filePath = filterDirPath + File.separator + "oc_param.json";
        return _filePath;
    }

    private static OperatingConditionParameterInfo defaultParam() {
        OperatingConditionParameterInfo ocParam = new OperatingConditionParameterInfo();
        ocParam.incident_downstream_distance_limit = 10f;
        ocParam.incident_upstream_distance_limit = 2f;
        ocParam.incident_keep_in_minute = 60;
        ocParam.workzone_downstream_distance_limit = 10f;
        ocParam.workzone_upstream_distance_limit = 2f;
        ocParam.workzone_length_short_from = 0f;
        ocParam.workzone_length_short_to = 5f;
        ocParam.workzone_length_medium_from = 5f;
        ocParam.workzone_length_medium_to = 10f;
        ocParam.workzone_length_long_from = 10f;
        ocParam.workzone_length_long_to = 9999f;
        ocParam.specialevent_size_small_from = 0;
        ocParam.specialevent_size_small_to = 20000;
        ocParam.specialevent_size_medium_from = 20000;
        ocParam.specialevent_size_medium_to = 40000;
        ocParam.specialevent_size_large_from = 40000;
        ocParam.specialevent_size_large_to = 999999999;
        ocParam.specialevent_distance_near_from = 0f;
        ocParam.specialevent_distance_near_to = 3f;
        ocParam.specialevent_distance_middle_from = 3f;
        ocParam.specialevent_distance_middle_to = 5f;
        ocParam.specialevent_distance_far_from = 5f;
        ocParam.specialevent_distance_far_to = 9999f;
        return ocParam;
    }

    static public boolean validate(OperatingConditionParameterInfo ocParam) {
        
        OperatingConditionParameterInfo defaultParam = defaultParam();
        
        if(ocParam.workzone_length_long_to > defaultParam.workzone_length_long_to
                || ocParam.specialevent_distance_far_to > defaultParam.specialevent_distance_far_to
                || ocParam.specialevent_size_large_to > defaultParam.specialevent_size_large_to) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Corrupt configurations");
            return false;
        }
        
        if(ocParam.incident_downstream_distance_limit < 0) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Maximum distance from downstream boundary of a given route for incident\nmust be greater than or equal to 0");
            return false;
        }
        if(ocParam.incident_upstream_distance_limit < 0) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Maximum distance from upstream boundary of a given route for incident\nmust be greater than or equal to 0");
            return false;
        }        
        if(ocParam.incident_keep_in_minute < 0) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Affected Time by Incident must be greater than or equal to 0");
            return false;
        }        
        if(ocParam.workzone_length_short_from >= ocParam.workzone_length_short_to
                || ocParam.workzone_length_short_to.compareTo(ocParam.workzone_length_medium_from) != 0
                || ocParam.workzone_length_medium_from >= ocParam.workzone_length_medium_to
                || ocParam.workzone_length_medium_to.compareTo(ocParam.workzone_length_long_from) != 0
                || ocParam.workzone_length_long_from >= ocParam.workzone_length_long_to) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Wrong configurations in Workzone Length");
            return false;
        }          
        if(ocParam.workzone_downstream_distance_limit < 0) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Maximum distance from downstream boundary of a given route for workzone\nmust be greater than or equal to 0");
            return false;
        }     
        if(ocParam.workzone_upstream_distance_limit < 0) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Maximum distance from upstream boundary of a given route for workzone\nmust be greater than or equal to 0");
            return false;
        }             
        if(ocParam.specialevent_size_small_from >= ocParam.specialevent_size_small_to
                || ocParam.specialevent_size_small_to.compareTo(ocParam.specialevent_size_medium_from) != 0
                || ocParam.specialevent_size_medium_from >= ocParam.specialevent_size_medium_to
                || ocParam.specialevent_size_medium_to.compareTo(ocParam.specialevent_size_large_from) != 0
                || ocParam.specialevent_size_large_from >= ocParam.specialevent_size_large_to) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Wrong configurations in Special Event Size");
            return false;
        }            
        if(ocParam.specialevent_distance_near_from >= ocParam.specialevent_distance_near_to
                || ocParam.specialevent_distance_near_to.compareTo(ocParam.specialevent_distance_middle_from) != 0
                || ocParam.specialevent_distance_middle_from >= ocParam.specialevent_distance_middle_to
                || ocParam.specialevent_distance_middle_to.compareTo(ocParam.specialevent_distance_far_from) != 0
                || ocParam.specialevent_distance_far_from >= ocParam.specialevent_distance_far_to) {
            JOptionPane.showMessageDialog(ticas.tetres.admin.TeTRESConfig.mainFrame, "Wrong configurations in Special Event Distance");
            return false;
        }    
        return true;
    }
}
