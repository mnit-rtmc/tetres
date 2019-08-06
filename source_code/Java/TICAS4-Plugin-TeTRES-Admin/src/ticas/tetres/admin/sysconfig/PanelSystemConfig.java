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
package ticas.tetres.admin.sysconfig;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpResult;
import ticas.common.ui.map.MapHelper;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.types.ReliabilityRouteInfo;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;
import org.apache.logging.log4j.core.Logger;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.ui.IInitializable;
import ticas.tetres.admin.api.SystemConfigClient;
import ticas.tetres.admin.types.SystemConfigInfo;

/**
 *
 * @author Chongmyung Park
 */
public class PanelSystemConfig extends javax.swing.JPanel implements IInitializable {

    private Infra infra;
    private List<Corridor> corridors = new ArrayList<>();
    private MapHelper mapHelper;
    private List<ReliabilityRouteInfo> routeList = new ArrayList<>();
    private List<ReliabilityRouteInfo> selectedRoutes = new ArrayList<>();
    private Logger logger;
    private SystemConfigClient model;
    private SystemConfigInfo systemConfig;

    /**
     * Creates new form RouteEditorPanel
     */
    public PanelSystemConfig() {
        initComponents();
    }

    /**
     * *
     * initialize variables and UI
     */
    @Override
    public void init() {
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.model = new SystemConfigClient();
        this.getSystemConfigInfo();
    }

    @Override
    public void refresh() {
        this.getSystemConfigInfo();
    }

    private void getSystemConfigInfo() {
        this.model.get(new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {
                updateSettingInUI();
            }

            @Override
            public void fail(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get system configuration information");
            }
        });
    }

    private void updateSettingInUI() {
        this.systemConfig = this.model.getSystemConfig();
        this.periodicJobSetingPanel.updateSettingInUI(this.systemConfig);
        this.categorizationParameterPanel.updateSettingInUI(this.systemConfig);
    }

    private void applyConfiguration() {
        int reply = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Do you want to apply the updated configurations?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (reply != JOptionPane.YES_OPTION) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Aborted");
            return;
        }
        
        SystemConfigInfo newSysConfig = this.getUpdatedSystemConfigs();

        if (this.systemConfig.data_archive_start_year.compareTo(newSysConfig.data_archive_start_year) != 0) {
            if (this.systemConfig.data_archive_start_year < newSysConfig.data_archive_start_year) {
                reply = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame,
                        "DATA ARCHIVE START YEAR has been shrunk.\nThe calculated data before " + newSysConfig.data_archive_start_year + " will be deleted.\nDo you want to proceed?",
                        "Confirm", JOptionPane.YES_NO_OPTION);
                if (reply != JOptionPane.YES_OPTION) {
                    JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Aborted");
                    return;
                }
            }
            if (this.systemConfig.data_archive_start_year > newSysConfig.data_archive_start_year) {
                reply = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame,
                        "DATA ARCHIVE START YEAR has been extended.\nTravel time will be calculated after " + newSysConfig.data_archive_start_year + ".\nDo you want to proceed?",
                        "Confirm", JOptionPane.YES_NO_OPTION);
                if (reply != JOptionPane.YES_OPTION) {
                    JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Aborted");
                    return;
                }
            }
        }

        if (this.systemConfig.incident_downstream_distance_limit.compareTo(newSysConfig.incident_downstream_distance_limit) != 0
                || this.systemConfig.incident_upstream_distance_limit.compareTo(newSysConfig.incident_upstream_distance_limit) != 0
                || this.systemConfig.workzone_downstream_distance_limit.compareTo(newSysConfig.workzone_downstream_distance_limit) != 0
                || this.systemConfig.workzone_upstream_distance_limit.compareTo(newSysConfig.workzone_upstream_distance_limit) != 0
                || this.systemConfig.specialevent_arrival_window.compareTo(newSysConfig.specialevent_arrival_window) != 0
                || this.systemConfig.specialevent_departure_window1.compareTo(newSysConfig.specialevent_departure_window1) != 0
                || this.systemConfig.specialevent_departure_window2.compareTo(newSysConfig.specialevent_departure_window2) != 0) {
            
            reply = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame,
                    "Categorization Parameters have been changed.\nCategorization process will be performed.\nDo you want to proceed?",
                    "Confirm", JOptionPane.YES_NO_OPTION);
            if (reply != JOptionPane.YES_OPTION) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Aborted");
                return;
            }
        }

        this.model.update(newSysConfig, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Requested.\nThe process is running in the background process.");
                model.getSystemConfig();
            }

            @Override
            public void fail(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to apply");
                model.getSystemConfig();
            }
        });

    }

    private SystemConfigInfo getUpdatedSystemConfigs() {
        SystemConfigInfo newSysConfig = new SystemConfigInfo();
        this.periodicJobSetingPanel.fillSystemConfigInfo(newSysConfig);
        this.categorizationParameterPanel.fillSystemConfigInfo(newSysConfig);
        return newSysConfig;
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        asyncRequestAdapter1 = new org.jdesktop.http.async.event.AsyncRequestAdapter();
        jTabbedPane1 = new javax.swing.JTabbedPane();
        periodicJobSetingPanel = new ticas.tetres.admin.sysconfig.PanelPeriodicJobSeting();
        categorizationParameterPanel = new ticas.tetres.admin.sysconfig.PanelCategorizationParameter();
        btnApply = new javax.swing.JButton();

        jTabbedPane1.addTab("Periodic Job Setting", periodicJobSetingPanel);
        jTabbedPane1.addTab("Categorization Parameter Setting", categorizationParameterPanel);

        btnApply.setText("Apply Configuration");
        btnApply.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnApplyActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(jTabbedPane1)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addComponent(btnApply, javax.swing.GroupLayout.PREFERRED_SIZE, 190, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addComponent(jTabbedPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 537, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addComponent(btnApply)
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

    private void btnApplyActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnApplyActionPerformed
        this.applyConfiguration();
    }//GEN-LAST:event_btnApplyActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private org.jdesktop.http.async.event.AsyncRequestAdapter asyncRequestAdapter1;
    private javax.swing.JButton btnApply;
    private ticas.tetres.admin.sysconfig.PanelCategorizationParameter categorizationParameterPanel;
    private javax.swing.JTabbedPane jTabbedPane1;
    private ticas.tetres.admin.sysconfig.PanelPeriodicJobSeting periodicJobSetingPanel;
    // End of variables declaration//GEN-END:variables

}
