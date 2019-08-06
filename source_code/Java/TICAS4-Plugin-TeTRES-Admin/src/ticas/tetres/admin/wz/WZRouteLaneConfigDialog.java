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
package ticas.tetres.admin.wz;

import ticas.tetres.admin.types.WorkZoneInfo;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IHttpResultCallback;
import ticas.common.pyticas.IResponseCallback;
import ticas.common.pyticas.responses.ResponseRoute;
import ticas.common.route.Route;
import ticas.common.util.FileHelper;
import java.awt.Desktop;
import java.io.File;
import java.io.IOException;
import java.util.List;
import javax.swing.JOptionPane;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.api.RouteClient;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class WZRouteLaneConfigDialog extends javax.swing.JDialog {

    private Route route;
    public Route updatedRoute;
    private String filepath_rcfg;
    private String filepath_updated_rcfg;
    private boolean isReadyToSave = false;
    private WorkZoneInfo wzi;
    private RouteClient routeApi;

    /**
     * Creates new form RouteLaneConfigDialog
     */
    public WZRouteLaneConfigDialog(Route route, java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();
        this.setLocationRelativeTo(parent);
        this.route = route;
        this.routeApi = new RouteClient();
    }

    protected void saveFile() {
        this.filepath_rcfg = FileHelper.chooseFileToSave(FileHelper.currentPath(), "Save Route Config File", FileHelper.FileFilterForExcel);
        if (this.filepath_rcfg == null || this.filepath_rcfg.isEmpty()) {
            return;
        }

        this.routeApi.saveRouteConfig(this.route, this.filepath_rcfg, new IHttpResultCallback() {
            @Override
            public void ready(HttpResult res) {
                try {
                    Desktop.getDesktop().open(new File(filepath_rcfg));
                } catch (IOException ex) {
                    TICASLogger.getLogger(WZRouteLaneConfigDialog.class.getName()).warn(String.format("fail to open excel file : %s", filepath_rcfg));
                }
            }

            @Override
            public void fail(HttpResult res) {
                System.out.println(res.contents);
                TICASLogger.getLogger(WZRouteLaneConfigDialog.class.getName()).warn(String.format("fail to save route config file : %s", filepath_rcfg));
            }
        });
    }

    protected void loadFile() {
        String curPath = FileHelper.currentPath();
        if (this.filepath_rcfg != null) {
            curPath = this.filepath_rcfg;
        }
        this.filepath_updated_rcfg = FileHelper.chooseFileToOpen(curPath, "Select Updated Route Config File", FileHelper.FileFilterForExcel);
        if (this.filepath_updated_rcfg == null || this.filepath_updated_rcfg.isEmpty()) {
            return;
        }
        this._createWZ();
    }

    protected boolean isSameRoute(Route route1, Route route2) {
        List<String> rnames1 = route1.getRNodeNames();
        List<String> rnames2 = route2.getRNodeNames();
        if(rnames1.size() != rnames2.size())
            return false;
        
        int limit = rnames1.size();
        for(int idx=0; idx<limit; idx++) {
            if(rnames1.get(idx) == null ? rnames2.get(idx) != null : !rnames1.get(idx).equals(rnames2.get(idx))) {
                return false;
            }
        }
        return true;
    }
    
    protected void _createWZ() {
        this.routeApi.getFromRouteConfig(this.filepath_updated_rcfg, new IResponseCallback<ResponseRoute>() {
            @Override
            public void success(ResponseRoute res) {
                if (isSameRoute(res.obj, route)) {
                    isReadyToSave = true;
                    updatedRoute = res.obj;
                    if (updatedRoute.cfg == null) {
                        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "updatedRoute has no lane configurations");
                    }
                    JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "updatedRoute has been set");
                    dispose();
                } else {
                    JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "The selected route and the update route configuration file does not match.");
                    isReadyToSave = false;
                    dispose();
                }
            }

            @Override
            public void fail(HttpResult res) {
                TICASLogger.getLogger(WZRouteLaneConfigDialog.class.getName()).warn(String.format("could not load route information from the updated route configuration file : %s", filepath_updated_rcfg));
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
        btnSelectUpdatedFile = new javax.swing.JButton();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Work Zone Route Configuration Dialog");

        btnSaveFile.setText("Create the Route Configuration File");
        btnSaveFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSaveFileActionPerformed(evt);
            }
        });

        btnSelectUpdatedFile.setText("Open/update the existing Route Configuration File");
        btnSelectUpdatedFile.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSelectUpdatedFileActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(btnSaveFile, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnSelectUpdatedFile, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, 377, Short.MAX_VALUE))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(btnSaveFile, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 25, Short.MAX_VALUE)
                .addComponent(btnSelectUpdatedFile, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addContainerGap())
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void btnSaveFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSaveFileActionPerformed
        saveFile();
    }//GEN-LAST:event_btnSaveFileActionPerformed

    private void btnSelectUpdatedFileActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSelectUpdatedFileActionPerformed
        loadFile();
    }//GEN-LAST:event_btnSelectUpdatedFileActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnSaveFile;
    private javax.swing.JButton btnSelectUpdatedFile;
    private javax.swing.JPanel jPanel1;
    // End of variables declaration//GEN-END:variables

}
