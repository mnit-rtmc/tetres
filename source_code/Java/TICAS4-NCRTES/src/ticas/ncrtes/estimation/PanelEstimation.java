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
package ticas.ncrtes.estimation;

import ticas.common.config.Config;
import ticas.common.infra.Corridor;
import ticas.ncrtes.NCRTESConfig;
import ticas.ncrtes.api.EstimationClient;
import ticas.ncrtes.types.BarealaneRegainTimeInfo;
import ticas.ncrtes.types.EstimationRequestInfo;
import ticas.ncrtes.types.SnowRouteGroupInfo;
import ticas.ncrtes.types.SnowRouteInfo;
import ticas.common.ui.IInitializable;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import javax.swing.JOptionPane;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author chong
 */
public class PanelEstimation extends javax.swing.JPanel implements IInitializable {

    private List<Corridor> selectedCorridors = new ArrayList<Corridor>();
    private ArrayList<SnowRouteGroupInfo> selectedSnowRouteGroupInfos = new ArrayList<SnowRouteGroupInfo>();
    private ArrayList<SnowRouteInfo> selectedSnowRouteInfos = new ArrayList<SnowRouteInfo>();
    private List<BarealaneRegainTimeInfo> selectedBarelaneRegainInfos = null;
    private EstimationClient api;

    /**
     * Creates new form PanelEstimation
     */
    public PanelEstimation() {
        initComponents();
    }

    @Override
    public void init() {
        this.panMap.init();
        //this.panMap.mapHelper.jmKit.setTileFactory(TileServerFactory.getTileFactory());                
        GeoPosition loc = this.panMap.mapHelper.jmKit.getAddressLocation();
        this.panMap.mapHelper.jmKit.setTileFactory(Config.getMapProvider().getProvider().getTileFactory());
        this.panMap.mapHelper.jmKit.setAddressLocation(loc);
        this.panMap.mapHelper.zoom(7);
        this.api = new EstimationClient();
    }

    private void doEstimation() {
        EstimationRequestInfo eri = new EstimationRequestInfo();
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:00");
        Date startDate = this.dtStartDate.getDate();
        if (startDate == null) {
            JOptionPane.showMessageDialog(this, "Select snow start time");
            return;
        }
        Date endDate = this.dtEndDate.getDate();
        if (endDate == null) {
            JOptionPane.showMessageDialog(this, "Select snow end time");
            return;
        }

        eri.snow_start_time = sdf.format(startDate);
        eri.snow_end_time = sdf.format(endDate);

        if (this.selectedCorridors != null && !this.selectedCorridors.isEmpty()) {
            for (Corridor corr : this.selectedCorridors) {
                eri.target_corridors.add(corr.name);
            }
        } else if (this.selectedSnowRouteInfos != null && !this.selectedSnowRouteInfos.isEmpty()) {
            for(SnowRouteInfo sri : this.selectedSnowRouteInfos) {                
                eri.target_snow_routes.add(sri.id);
            }
        } else {
            JOptionPane.showMessageDialog(this, "Select target corridors or target truck routes");
            return;
        }
        eri.barelane_regain_time_infos = this.selectedBarelaneRegainInfos;
        this.api.estimate(eri);
//        JOptionPane.showMessageDialog(this, "Please wait until \"Done\" message is shown.\nResults can be found in \"Tools > Estimation Results\" menu on top");
    }

    @Override
    public void refresh() {
        // do nothing
    }     
    
    private void openSelectTargetCorridorDialog() {
        SelectTargetCorridorDialog scd = new SelectTargetCorridorDialog(NCRTESConfig.mainFrame, true);
        scd.setLocationRelativeTo(NCRTESConfig.mainFrame);
        scd.setVisible(true);
        StringBuilder sb = new StringBuilder();
        sb.append("# Selected Corridors");
        sb.append(System.getProperty("line.separator"));
        for (Corridor corr : scd.selectedCorridors) {
            sb.append(String.format(" - %s", corr.name));
            sb.append(System.getProperty("line.separator"));
        }
        this.selectedSnowRouteGroupInfos.clear();
        this.selectedSnowRouteInfos.clear();
        this.selectedCorridors = scd.selectedCorridors;
        this.tbxTargets.setText(sb.toString());
        this.updateMapByCorridor();
    }

    private void updateMapByCorridor() {
        this.panMap.mapHelper.clear();
        this.panMap.mapHelper.showCorridors(this.selectedCorridors);
    }

    private void openSelectTargetTruckRouteDialog() {
        SelectTargetTruckRouteDialog stcd = new SelectTargetTruckRouteDialog(NCRTESConfig.mainFrame, true);
        stcd.setLocationRelativeTo(NCRTESConfig.mainFrame);
        stcd.setVisible(true);
        StringBuilder sb = new StringBuilder();
        sb.append("# Selected Truck Routes");
        sb.append(System.getProperty("line.separator"));
        for (SnowRouteGroupInfo snrgi : stcd.selectedSnowRouteGroupInfos) {
            sb.append(String.format(" - %s (%s - %s)", snrgi.name, snrgi.region, snrgi.sub_region));
            sb.append(System.getProperty("line.separator"));
        }
        this.selectedCorridors.clear();
        this.selectedSnowRouteGroupInfos = stcd.selectedSnowRouteGroupInfos;
        this.selectedSnowRouteInfos = stcd.selectedSnowRouteInfos;
        this.tbxTargets.setText(sb.toString());
        this.updateMapByTruckRoutes();
    }

    private void updateMapByTruckRoutes() {
        this.panMap.mapHelper.clear();
        for (SnowRouteInfo snri : this.selectedSnowRouteInfos) {
            this.panMap.mapHelper.addShowRNodes(snri.route1.getRNodes());
        }
    }

    private void openImportReportedTimeDialog() {
        ImportReportedTimeDialog irtd = new ImportReportedTimeDialog(NCRTESConfig.mainFrame, true);
        irtd.setLocationRelativeTo(NCRTESConfig.mainFrame);
        irtd.setVisible(true);
        this.selectedBarelaneRegainInfos = irtd.barelaneinfo;
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
        jLabel2 = new javax.swing.JLabel();
        jLabel3 = new javax.swing.JLabel();
        dtStartDate = new ticas.common.ui.TICASDateTimePicker();
        dtEndDate = new ticas.common.ui.TICASDateTimePicker();
        jPanel6 = new javax.swing.JPanel();
        jLabel10 = new javax.swing.JLabel();
        btnSelectCorridor = new javax.swing.JButton();
        btnSelectTruckRoutes = new javax.swing.JButton();
        jLabel6 = new javax.swing.JLabel();
        jSeparator1 = new javax.swing.JSeparator();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxTargets = new javax.swing.JTextArea();
        jPanel4 = new javax.swing.JPanel();
        btnImportBareLaneRegainTime = new javax.swing.JButton();
        jLabel7 = new javax.swing.JLabel();
        panMap = new ticas.common.ui.map.MapPanel();
        btnEstimate = new javax.swing.JButton();

        jPanel1.setBorder(javax.swing.BorderFactory.createTitledBorder("Snow Event"));

        jLabel2.setText("From : ");

        jLabel3.setText("To : ");

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addGap(41, 41, 41)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabel3)
                    .addComponent(jLabel2))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(dtStartDate, javax.swing.GroupLayout.DEFAULT_SIZE, 320, Short.MAX_VALUE)
                    .addComponent(dtEndDate, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabel2)
                    .addComponent(dtStartDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabel3)
                    .addComponent(dtEndDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jPanel6.setBorder(javax.swing.BorderFactory.createTitledBorder("Target"));

        jLabel10.setText("- or -");

        btnSelectCorridor.setText("Select Corridors");
        btnSelectCorridor.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSelectCorridorActionPerformed(evt);
            }
        });

        btnSelectTruckRoutes.setText("Select Truck Routes");
        btnSelectTruckRoutes.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSelectTruckRoutesActionPerformed(evt);
            }
        });

        jLabel6.setText("Select target corridors or truck routes to estimate");

        tbxTargets.setEditable(false);
        tbxTargets.setColumns(20);
        tbxTargets.setRows(5);
        jScrollPane1.setViewportView(tbxTargets);

        javax.swing.GroupLayout jPanel6Layout = new javax.swing.GroupLayout(jPanel6);
        jPanel6.setLayout(jPanel6Layout);
        jPanel6Layout.setHorizontalGroup(
            jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel6Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 399, Short.MAX_VALUE)
                    .addGroup(jPanel6Layout.createSequentialGroup()
                        .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jSeparator1)
                            .addGroup(jPanel6Layout.createSequentialGroup()
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(jPanel6Layout.createSequentialGroup()
                                        .addComponent(btnSelectCorridor, javax.swing.GroupLayout.PREFERRED_SIZE, 127, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addGap(18, 18, 18)
                                        .addComponent(jLabel10)
                                        .addGap(18, 18, 18)
                                        .addComponent(btnSelectTruckRoutes))
                                    .addComponent(jLabel6))
                                .addGap(0, 0, Short.MAX_VALUE)))
                        .addContainerGap())))
        );
        jPanel6Layout.setVerticalGroup(
            jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel6Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel6)
                .addGap(18, 18, 18)
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnSelectCorridor)
                    .addComponent(jLabel10)
                    .addComponent(btnSelectTruckRoutes))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jSeparator1, javax.swing.GroupLayout.PREFERRED_SIZE, 11, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 169, Short.MAX_VALUE)
                .addContainerGap())
        );

        jPanel4.setBorder(javax.swing.BorderFactory.createTitledBorder("Options"));

        btnImportBareLaneRegainTime.setText("Import Bare Lane Regain Time");
        btnImportBareLaneRegainTime.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnImportBareLaneRegainTimeActionPerformed(evt);
            }
        });

        jLabel7.setText("Reported Bare Lane Regain Time Information");

        javax.swing.GroupLayout jPanel4Layout = new javax.swing.GroupLayout(jPanel4);
        jPanel4.setLayout(jPanel4Layout);
        jPanel4Layout.setHorizontalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel4Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                    .addComponent(btnImportBareLaneRegainTime, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jLabel7, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap(183, Short.MAX_VALUE))
        );
        jPanel4Layout.setVerticalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel4Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel7)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(btnImportBareLaneRegainTime)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        btnEstimate.setText("Estimate");
        btnEstimate.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEstimateActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jPanel6, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                        .addComponent(btnEstimate)
                        .addComponent(jPanel4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(18, 18, 18)
                .addComponent(panMap, javax.swing.GroupLayout.DEFAULT_SIZE, 542, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jPanel6, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addGap(18, 18, 18)
                        .addComponent(jPanel4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(btnEstimate)
                        .addGap(12, 12, 12))
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(panMap, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addContainerGap())))
        );
    }// </editor-fold>//GEN-END:initComponents

    private void btnSelectCorridorActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSelectCorridorActionPerformed
        openSelectTargetCorridorDialog();
    }//GEN-LAST:event_btnSelectCorridorActionPerformed

    private void btnSelectTruckRoutesActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnSelectTruckRoutesActionPerformed
        openSelectTargetTruckRouteDialog();
    }//GEN-LAST:event_btnSelectTruckRoutesActionPerformed

    private void btnImportBareLaneRegainTimeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnImportBareLaneRegainTimeActionPerformed
        openImportReportedTimeDialog();
    }//GEN-LAST:event_btnImportBareLaneRegainTimeActionPerformed

    private void btnEstimateActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEstimateActionPerformed
        doEstimation();
    }//GEN-LAST:event_btnEstimateActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnEstimate;
    private javax.swing.JButton btnImportBareLaneRegainTime;
    private javax.swing.JButton btnSelectCorridor;
    private javax.swing.JButton btnSelectTruckRoutes;
    private ticas.common.ui.TICASDateTimePicker dtEndDate;
    private ticas.common.ui.TICASDateTimePicker dtStartDate;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel6;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JSeparator jSeparator1;
    private ticas.common.ui.map.MapPanel panMap;
    private javax.swing.JTextArea tbxTargets;
    // End of variables declaration//GEN-END:variables

}
