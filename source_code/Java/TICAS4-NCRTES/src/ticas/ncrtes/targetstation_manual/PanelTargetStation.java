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
package ticas.ncrtes.targetstation_manual;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.infra.InfraObject;
import ticas.common.infra.RNode;
import ticas.ncrtes.NCRTESConfig;
import ticas.ncrtes.api.ManualTargetStationClient;
import ticas.ncrtes.types.AbstractDataChangeListener;
import ticas.ncrtes.types.TargetStationManualInfo;
import ticas.common.pyticas.HttpResult;
import ticas.common.ui.CorridorSelector;
import ticas.common.ui.IInitializable;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;

/**
 *
 * @author chong
 */
public class PanelTargetStation extends javax.swing.JPanel implements IInitializable, ISetTargetStation {

    private Corridor selectedCorridor = null;
    private List<TargetStationManualInfo> selectedTargetStations = new ArrayList<TargetStationManualInfo>();
    private List<TargetStationManualInfo> targetStations = new ArrayList<TargetStationManualInfo>();
    private ManualTargetStationClient api;

    /**
     * Creates new form PanelEstimation
     */
    public PanelTargetStation() {
        initComponents();
    }

    @Override
    public void init() {

        this.panTSMap.init(this);

        this.api = new ManualTargetStationClient();

        this.corridorSelector.init(Infra.getInstance(), new CorridorSelector.CorridorSelectedListener() {
            @Override
            public void OnSelected(int selectedIndex, Corridor corridor) {
                selectedCorridor = corridor;
                loadByCorridor();
            }
        });

        this.api.addChangeListener(new AbstractDataChangeListener<TargetStationManualInfo>() {
            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to delete the selected target station");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                loadByCorridor();
            }

            @Override
            public void insertFailed(HttpResult result, TargetStationManualInfo obj) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to insert target station info");
            }

            @Override
            public void insertSuccess(Integer id) {
                loadByCorridor();
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to get list of target station");
            }

            @Override
            public void listSuccess(List<TargetStationManualInfo> list) {
                targetStations = list;
                setTargetStationTable();
            }
        });

        // when route selected
        this.tblStationList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                onTargetStationClicked();
            }
        });
    }

    private void loadByCorridor() {
        if (this.selectedCorridor == null) {
            return;
        }
        Infra infra = Infra.getInstance();
        this.panTSMap.mapHelper.clear();
        List<RNode> stations = new ArrayList<RNode>();
        for (String rnode_name : this.selectedCorridor.stations) {
            stations.add(infra.getRNode(rnode_name));
        }
        this.panTSMap.mapHelper.showRNodes(stations);

        api.list(this.selectedCorridor.name);
    }

    private void setTargetStationTable() {
        Infra infra = Infra.getInstance();
        final DefaultTableModel tm = (DefaultTableModel) this.tblStationList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (TargetStationManualInfo s : this.targetStations) {
            RNode station = infra.getRNode(s.station_id);
            tm.addRow(new Object[]{s, station.label});
        }
        this.setTargetStationAsBlueMarker();
    }

    private void setTargetStationAsBlueMarker() {
        Infra infra = Infra.getInstance();
        List<RNode> stations = new ArrayList<RNode>();
        for (TargetStationManualInfo tsi : this.targetStations) {
            stations.add(infra.getRNode(tsi.station_id));
        }
        this.panTSMap.mapHelper.setRouteAsBlueMarker(stations.toArray(new InfraObject[stations.size()]));
    }

    @Override
    public void setTargetStation(RNode station) {
        if (!Infra.getInstance().isAvailableStation(station)) {
            return;
        }
        TargetStationManualInfo tsmi = new TargetStationManualInfo();
        tsmi.corridor_name = station.corridor;
        tsmi.station_id = station.station_id;
        this.api.insert(tsmi);
    }

    @Override
    public void unsetTargetStation(RNode station) {
        this.selectedTargetStations.clear();
        DefaultTableModel tm = (DefaultTableModel) tblStationList.getModel();
        for (TargetStationManualInfo s : this.targetStations) {
            if (s != null && s.station_id.equals(station.station_id)) {
                selectedTargetStations.add(s);
            }
        }        
        this.removeTargetStation();
    }
    
    
    private void onTargetStationClicked() {
        this.selectedTargetStations.clear();

        DefaultTableModel tm = (DefaultTableModel) tblStationList.getModel();
        for (int row : tblStationList.getSelectedRows()) {
            TargetStationManualInfo s = targetStations.get(row);
            if (s != null) {
                selectedTargetStations.add(s);
            }
        }
    }

    private void removeTargetStation() {
        if (this.selectedTargetStations.isEmpty()) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Use it after selecting at least one item?");
            return;
        }
        int res = JOptionPane.showConfirmDialog(NCRTESConfig.mainFrame, "Delete selected target stations ?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (TargetStationManualInfo snrgi : this.selectedTargetStations) {
                ids.add(snrgi.id);
            }
            this.api.delete(ids);
        }
    }
    
    @Override
    public void refresh() {
        // do nothing
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
        jLabel1 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane4 = new javax.swing.JScrollPane();
        tblStationList = new javax.swing.JTable();
        corridorSelector = new ticas.common.ui.CorridorSelector();
        btnDelete = new javax.swing.JButton();
        panTSMap = new ticas.ncrtes.targetstation_manual.map.TSMap();

        jLabel1.setText("Corridor");

        jLabel2.setText("Target Stations");

        tblStationList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Station ID", "Label"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class
            };
            boolean[] canEdit = new boolean [] {
                false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        tblStationList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane4.setViewportView(tblStationList);
        if (tblStationList.getColumnModel().getColumnCount() > 0) {
            tblStationList.getColumnModel().getColumn(0).setMinWidth(80);
            tblStationList.getColumnModel().getColumn(0).setPreferredWidth(80);
            tblStationList.getColumnModel().getColumn(0).setMaxWidth(80);
        }

        btnDelete.setText("Remove Selected Target Stations");
        btnDelete.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane4, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                        .addGap(0, 0, Short.MAX_VALUE)
                        .addComponent(btnDelete))
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel1)
                            .addComponent(jLabel2)
                            .addComponent(corridorSelector, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel1)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(corridorSelector, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(23, 23, 23)
                .addComponent(jLabel2)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jScrollPane4, javax.swing.GroupLayout.DEFAULT_SIZE, 353, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(btnDelete)
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(panTSMap, javax.swing.GroupLayout.DEFAULT_SIZE, 527, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(panTSMap, javax.swing.GroupLayout.DEFAULT_SIZE, 492, Short.MAX_VALUE))
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

    private void btnDeleteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteActionPerformed
        removeTargetStation();
    }//GEN-LAST:event_btnDeleteActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnDelete;
    private ticas.common.ui.CorridorSelector corridorSelector;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JScrollPane jScrollPane4;
    private ticas.ncrtes.targetstation_manual.map.TSMap panTSMap;
    private javax.swing.JTable tblStationList;
    // End of variables declaration//GEN-END:variables


}
