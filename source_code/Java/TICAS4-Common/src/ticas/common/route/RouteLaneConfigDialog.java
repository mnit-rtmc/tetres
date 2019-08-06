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
package ticas.common.route;

import ticas.common.log.TICASLogger;
import ticas.common.pyticas.LocalRouteClient;
import ticas.common.util.FileHelper;
import java.awt.Desktop;
import java.io.File;
import java.io.IOException;
import javax.swing.JOptionPane;
import ticas.common.config.Config;
import ticas.common.pyticas.IBooleanCallback;
import ticas.common.pyticas.IRouteCallback;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RouteLaneConfigDialog extends javax.swing.JDialog {

    private Route route;
    private String filepath_rcfg;
    private String filepath_updated_rcfg;
    private boolean isReadyToSave = false;

    /**
     * Creates new form RouteLaneConfigDialog
     */
    public RouteLaneConfigDialog(Route route, java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();
        this.setLocationRelativeTo(parent);
        this.route = route;
        this.panMap.init();
        this.panMap.mapHelper.showRoute(this.route);
        this.panMap.mapHelper.setCenter(this.route.getRNodes().get(0));
        this.panMap.mapHelper.zoom(6);
    }

    public void saveFile() {
        this.filepath_rcfg = FileHelper.chooseFileToSave(FileHelper.currentPath(), "Save Route Config File", FileHelper.FileFilterForExcel);
        if (this.filepath_rcfg == null || this.filepath_rcfg.isEmpty()) {
            return;
        }

        LocalRouteClient.getInstance().saveRouteXlsxFile(this.route, this.filepath_rcfg, new IBooleanCallback() {
            @Override
            public void callback(boolean isSaved, String reason) {
                if (isSaved) {
                    try {
                        Desktop.getDesktop().open(new File(filepath_rcfg));
                    } catch (IOException ex) {
                        TICASLogger.getLogger(RouteLaneConfigDialog.class.getName()).warn(String.format("fail to open excel file : %s", filepath_rcfg));
                    }
                } else {
                    TICASLogger.getLogger(RouteLaneConfigDialog.class.getName()).warn(String.format("fail to save route config file : %s", filepath_rcfg));
                }
            }
        });
    }

    public void loadFile() {
        String curPath = FileHelper.currentPath();
        if (this.filepath_rcfg != null) {
            curPath = this.filepath_rcfg;
        }
        this.filepath_updated_rcfg = FileHelper.chooseFileToOpen(curPath, "Select Updated Route Config File", FileHelper.FileFilterForExcel);
        if (this.filepath_updated_rcfg == null || this.filepath_updated_rcfg.isEmpty()) {
            return;
        }
        LocalRouteClient.getInstance().getRouteFromXlsxFile(this.filepath_updated_rcfg, new IRouteCallback() {
            @Override
            public void callback(Route r) {
                System.out.println("callback : " + r);
                if (r != null) {
                    isReadyToSave = true;
                } else {
                    JOptionPane.showMessageDialog(Config.mainFrame, "The selected route and the update route configuration file does not match.");
                    isReadyToSave = false;
                }
            }
        });
    }

    public void updateRCFG() {

        LocalRouteClient.getInstance().updateRouteConfig(this.route.name, this.filepath_updated_rcfg, new IBooleanCallback() {
            @Override
            public void callback(boolean v, String reason) {
                if (v) {
                    JOptionPane.showMessageDialog(Config.mainFrame, "Route has been updated");
                    LocalRouteClient.getInstance().loadList();
                } else {
                    if(!reason.isEmpty()) {
                        JOptionPane.showMessageDialog(Config.mainFrame, reason);
                    }
                    TICASLogger.getLogger(RouteLaneConfigDialog.class.getName()).warn(String.format("fail to apply route configuration into the existing route : %s", filepath_updated_rcfg));
                }
            }
        });
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jPanel1 = new javax.swing.JPanel();
        btnSaveFile = new javax.swing.JButton();
        jLabel3 = new javax.swing.JLabel();
        btnSelectUpdatedFile = new javax.swing.JButton();
        btnSaveRouteConfiguration = new javax.swing.JButton();
        jLabel1 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        jLabel4 = new javax.swing.JLabel();
        jLabel5 = new javax.swing.JLabel();
        jLabel6 = new javax.swing.JLabel();
        panMap = new ticas.common.ui.map.MapPanel();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);

        btnSaveFile.setText("1. Save the Route Configuration File");
        btnSaveFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSaveFileActionPerformed(evt);
            }
        });

        jLabel3.setFont(new java.awt.Font("Tahoma", 1, 11)); // NOI18N
        jLabel3.setText("Directions");

        btnSelectUpdatedFile.setText("2. Select the updated Route Configuration File");
        btnSelectUpdatedFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSelectUpdatedFileActionPerformed(evt);
            }
        });

        btnSaveRouteConfiguration.setText("3. Save Route Configuration");
        btnSaveRouteConfiguration.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSaveRouteConfigurationActionPerformed(evt);
            }
        });

        jLabel1.setText("(a). Save the route configuration as spread sheet file [button 1]");

        jLabel2.setText("(b). Open the spread sheet file (excel) and update the lane configurations");

        jLabel4.setText("(c). Select the updated route configuration file [button 2]");

        jLabel5.setText("(d). Update the route configurations to the saved route [button 3]");

        jLabel6.setText("* skip step (a), if you already have the route configuration file");

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(btnSaveFile, javax.swing.GroupLayout.PREFERRED_SIZE, 267, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(btnSelectUpdatedFile, javax.swing.GroupLayout.PREFERRED_SIZE, 267, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(btnSaveRouteConfiguration, javax.swing.GroupLayout.PREFERRED_SIZE, 267, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(39, 39, 39)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel5)
                    .addComponent(jLabel2)
                    .addComponent(jLabel3)
                    .addComponent(jLabel1)
                    .addComponent(jLabel4)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGap(10, 10, 10)
                        .addComponent(jLabel6)))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(btnSaveFile, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(btnSelectUpdatedFile, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(btnSaveRouteConfiguration, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(jLabel3)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(jLabel6)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel2)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jLabel4)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jLabel5)
                        .addGap(21, 21, 21))))
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(panMap, javax.swing.GroupLayout.DEFAULT_SIZE, 814, Short.MAX_VALUE))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(panMap, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void btnSaveFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSaveFileActionPerformed
        saveFile();
    }//GEN-LAST:event_btnSaveFileActionPerformed

    private void btnSelectUpdatedFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSelectUpdatedFileActionPerformed
        loadFile();
    }//GEN-LAST:event_btnSelectUpdatedFileActionPerformed

    private void btnSaveRouteConfigurationActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSaveRouteConfigurationActionPerformed
        updateRCFG();
    }//GEN-LAST:event_btnSaveRouteConfigurationActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnSaveFile;
    private javax.swing.JButton btnSaveRouteConfiguration;
    private javax.swing.JButton btnSelectUpdatedFile;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JPanel jPanel1;
    private ticas.common.ui.map.MapPanel panMap;
    // End of variables declaration//GEN-END:variables
}
