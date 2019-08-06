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
package ticas.tetres.admin.snowmgmt;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.pyticas.HttpResult;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.api.SnowManagementClient;
import ticas.tetres.admin.api.SnowRouteClient;
import ticas.tetres.admin.types.AbstractDataChangeListener;
import ticas.tetres.admin.types.SnowEventInfo;
import ticas.tetres.admin.types.SnowManagementInfo;
import ticas.tetres.admin.types.SnowRouteInfo;
import java.awt.Frame;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;

/**
 *
 * @author Chongmyung Park
 */
public class SNMCreateDialog extends javax.swing.JDialog {

    private SnowEventInfo snowEvent;
    private List<SnowRouteInfo> snowRouteList = new ArrayList<>();
    private List<SnowRouteInfo> selectedSnowRoutes = new ArrayList<>();
    private SnowRouteClient snowRouteModel;
    private SnowManagementClient snowMgmtModel;

    public SNMCreateDialog(Frame parent, SnowEventInfo snowEvent) {
        super(parent, true);
        initComponents();
        this.init(snowEvent);
    }

    private void init(SnowEventInfo snowEvent) {
        this.snowRouteModel = new SnowRouteClient();
        this.snowMgmtModel = new SnowManagementClient();
        this.snowEvent = snowEvent;

        // set corridors
        this.cbxCorridors.addItem("All Corridors");
        for (Corridor c : Infra.getInstance().getCorridors()) {
            this.cbxCorridors.addItem(c);
        }

        // when corridor is selected
        this.cbxCorridors.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                setSnowRouteTable();
            }
        });
        
        // when route is selected
        this.tbSnowRoutes.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                // update selected snow routes
                selectedSnowRoutes.clear();
                DefaultTableModel tm = (DefaultTableModel) tbSnowRoutes.getModel();
                for (int row : tbSnowRoutes.getSelectedRows()) {
                    SnowRouteInfo s = (SnowRouteInfo) tm.getValueAt(row, 0);
                    if (s != null) {
                        selectedSnowRoutes.add(s);
                    }
                }
            }
        });

        // listener of snow management data 
        this.snowMgmtModel.addChangeListener(new AbstractDataChangeListener<SnowManagementInfo>() {
            
            @Override
            public void insertAllFailed(HttpResult result, List<SnowManagementInfo> dataList) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to insert management data");
            }

            @Override
            public void insertAllSuccess() {
                dispose();
            }                        
        });
        
        // listener of snow route data 
        this.snowRouteModel.addChangeListener(new AbstractDataChangeListener<SnowRouteInfo>() {
            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of snow route");
            }

            @Override
            public void listSuccess(List<SnowRouteInfo> list) {
                snowRouteList = list;
                setSnowRouteTable();
            }

        });

        this.snowMgmtModel.list(this.snowEvent.id);
        this.snowRouteModel.list();
    }

    /**
     * *
     * set snow route list table
     */
    protected void setSnowRouteTable() {
        int slt = this.cbxCorridors.getSelectedIndex();
        Corridor corr = null;
        if (slt > 0) {
            corr = (Corridor) this.cbxCorridors.getSelectedItem();
        }
        final DefaultTableModel tm = (DefaultTableModel) this.tbSnowRoutes.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SnowRouteInfo s : this.snowRouteList) {
            if (corr == null || s.route1.getRNodes().get(0).corridor.equals(corr.name)) {
                tm.addRow(new Object[]{s});
            }
        }
    }
    
    /**
     * save data
     */
    private void saveSnowMgmtData() {

        Date sdt = this.dtLaneLostTime.getDate();
        Date edt = this.dtLaneRegainTime.getDate();
        if (sdt == null || edt == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Duration is required. Please enter select the start and end time.");
            return;
        }

        if (this.selectedSnowRoutes.isEmpty()) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please select snow routes before saving");
            return;
        }
        
        List<SnowManagementInfo> snmiList = new ArrayList<>();
        for (SnowRouteInfo snri : this.selectedSnowRoutes) {
            SnowManagementInfo snmi = new SnowManagementInfo();
            snmi.sevent_id = this.snowEvent.id;
            snmi.sroute_id = snri.id;
            snmi.setDuration(sdt, edt);            
            snmiList.add(snmi);            
        }
        this.snowMgmtModel.insertAll(snmiList);
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jLabel1 = new javax.swing.JLabel();
        jPanel1 = new javax.swing.JPanel();
        jLabel7 = new javax.swing.JLabel();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbSnowRoutes = new javax.swing.JTable();
        cbxCorridors = new javax.swing.JComboBox();
        jPanel2 = new javax.swing.JPanel();
        jLabel10 = new javax.swing.JLabel();
        jLabel9 = new javax.swing.JLabel();
        btnCancel = new javax.swing.JButton();
        btnSave = new javax.swing.JButton();
        dtLaneLostTime = new ticas.common.ui.TICASDateTimePicker();
        dtLaneRegainTime = new ticas.common.ui.TICASDateTimePicker();

        jLabel1.setText("jLabel1");

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("New Snow Managment Data");

        jPanel1.setBorder(javax.swing.BorderFactory.createTitledBorder("Select Snow Routes"));

        jLabel7.setText("Corridor");

        tbSnowRoutes.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Snow Route"
            }
        ) {
            boolean[] canEdit = new boolean [] {
                false
            };

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jScrollPane1.setViewportView(tbSnowRoutes);

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 297, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(jLabel7)
                        .addGap(0, 0, Short.MAX_VALUE))
                    .addComponent(cbxCorridors, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel7)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(cbxCorridors, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(8, 8, 8)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                .addContainerGap())
        );

        jPanel2.setBorder(javax.swing.BorderFactory.createTitledBorder("Management Information"));

        jLabel10.setText("Lane Lost Time");

        jLabel9.setText("Lane Regain Time");

        btnCancel.setText("Cancel");
        btnCancel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCancelActionPerformed(evt);
            }
        });

        btnSave.setText("Save");
        btnSave.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSaveActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addComponent(btnCancel, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(btnSave, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addComponent(dtLaneLostTime, javax.swing.GroupLayout.DEFAULT_SIZE, 405, Short.MAX_VALUE)
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel10)
                            .addComponent(jLabel9))
                        .addGap(0, 0, Short.MAX_VALUE))
                    .addComponent(dtLaneRegainTime, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel10)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(dtLaneLostTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(12, 12, 12)
                .addComponent(jLabel9)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(dtLaneRegainTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 103, Short.MAX_VALUE)
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(btnCancel, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnSave, javax.swing.GroupLayout.PREFERRED_SIZE, 35, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void btnCancelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnCancelActionPerformed
        dispose();
    }//GEN-LAST:event_btnCancelActionPerformed

    private void btnSaveActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSaveActionPerformed
        saveSnowMgmtData();
    }//GEN-LAST:event_btnSaveActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnCancel;
    private javax.swing.JButton btnSave;
    private javax.swing.JComboBox cbxCorridors;
    private ticas.common.ui.TICASDateTimePicker dtLaneLostTime;
    private ticas.common.ui.TICASDateTimePicker dtLaneRegainTime;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JTable tbSnowRoutes;
    // End of variables declaration//GEN-END:variables

}
