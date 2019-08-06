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
package ticas.tetres.admin.snowmgmt.truckroute;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.infra.RNode;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpResult;
import ticas.common.ui.map.MapHelper;
import ticas.common.route.Route;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.types.AbstractDataChangeListener;
import ticas.tetres.admin.api.SnowRouteClient;
import ticas.tetres.admin.types.SnowRouteInfo;
import ticas.common.ui.map.TileServerFactory;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;
import org.apache.logging.log4j.core.Logger;

/**
 *
 * @author Chongmyung Park
 */
public class SNRouteListPanel extends javax.swing.JPanel {

    private Infra infra;
    private List<Corridor> corridors = new ArrayList<>();
    private MapHelper mapHelper;
    private List<SnowRouteInfo> routeList;
    private List<SnowRouteInfo> selectedRoutes = new ArrayList<>();
    private boolean firstResize = true;
    private SnowRouteClient model;
    private Logger logger;

    /**
     * Creates new form RouteEditorPanel
     */
    public SNRouteListPanel() {
        initComponents();
    }

    /**
     * *
     * initialize variables and UI
     */
    public void init() {
        this.jxMap.setTileFactory(TileServerFactory.getTileFactory());
        this.infra = Infra.getInstance();
        this.corridors = infra.getCorridors();
        this.mapHelper = new MapHelper(jxMap);        
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.model = new SnowRouteClient();
        
        this.panRouteInfo.addComponentListener(new ComponentAdapter() {
            @Override
            public void componentResized(ComponentEvent e) {
                if (firstResize) {
                    panRouteInfo.setDividerLocation(0.5);
                    firstResize = false;
                }
            }
        });

        // add corridors
        this.cbxCorridors.addItem("All Corridors");
        for (Corridor c : this.infra.getCorridors()) {
            this.cbxCorridors.addItem(c);
        }

        // add corridor change listener
        this.cbxCorridors.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                setTable();
            }
        });

        // add click-event handler for a route list
        this.tbRouteList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                setProperties();
            }
        });
        
        // UI actions 
        this.model.addChangeListener(new AbstractDataChangeListener<SnowRouteInfo>() {
            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of travel time route");
            }

            @Override
            public void listSuccess(List<SnowRouteInfo> list) {
                selectedRoutes.clear();
                mapHelper.clear();
                routeList = list;
                tbxInfo1.setText("");
                tbxInfo2.setText("");
                setTable();
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                model.list();
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                logger.warn(String.format("Fail to delete items : %s", ids.toString()));
                logger.debug(result.contents);
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to delete the travel time route");
            }            
        });
        
        this.model.list();
    }
    
    public void refresh() {
        this.model.list();        
    }
    
    /***
     * open route creation dialog
     */
    private void createRoute() {
        SNRouteCreateDialog rcd = new SNRouteCreateDialog(TeTRESConfig.mainFrame, true);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
        this.model.list();
    }
    
    /***
     * open route edit dialog
     */
    protected void editRoute() {
        if (this.selectedRoutes.isEmpty() || this.selectedRoutes.size() > 1) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single route to edit information");
            return;
        }
        SNRouteEditDialog red = new SNRouteEditDialog(TeTRESConfig.mainFrame, this.selectedRoutes.get(0));
        red.setLocationRelativeTo(TeTRESConfig.mainFrame);
        red.setVisible(true);
        this.model.list();
    }

    /**
     * delete selected items
     */
    protected void deleteSnowRoutes() {
        if (this.routeList.isEmpty()) {
            return;
        }

        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected routes?", "Confirm", JOptionPane.YES_NO_OPTION);

        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (SnowRouteInfo snr : this.selectedRoutes) {
                ids.add(snr.id);
            }
            this.model.delete(ids);
        }
    }

    /**
     * *
     * reset map, list and selected item
     */
    protected void reset() {
        this.mapHelper.clear();
        this.routeList.clear();
        this.selectedRoutes.clear();
        this.tbxInfo1.setText("");
        this.tbxInfo2.setText("");
        setTable();
    }

    /**
     * *
     * set list table
     */
    protected void setTable() {
        int slt = this.cbxCorridors.getSelectedIndex();
        Corridor corr = null;
        if (slt > 0) {
            corr = (Corridor) this.cbxCorridors.getSelectedItem();
        }
        final DefaultTableModel tm = (DefaultTableModel) this.tbRouteList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SnowRouteInfo s : this.routeList) {
            if (corr == null || s.route1.getRNodes().get(0).corridor.equals(corr.name)) {
                tm.addRow(new Object[]{s});
            }            
        }
    }
    
    /***
     * set map and route info when route on table is clicked
     */
    protected void setProperties() {
        this.selectedRoutes.clear();

        DefaultTableModel tm = (DefaultTableModel) this.tbRouteList.getModel();
        for (int row : this.tbRouteList.getSelectedRows()) {
            SnowRouteInfo s = (SnowRouteInfo) tm.getValueAt(row, 0);
            if (s != null) {
                this.selectedRoutes.add(s);
            }
        }

        if (this.selectedRoutes.isEmpty()) {
            this.mapHelper.clear();
            this.tbxInfo1.setText("");
            this.tbxInfo2.setText("");
            return;
        }

        List<RNode> rnodes = new ArrayList<>();
        List<RNode> rnodes1 = new ArrayList<>();
        List<RNode> rnodes2 = new ArrayList<>();
        for (SnowRouteInfo snri : this.selectedRoutes) {
            for (RNode rn : snri.route1.getRNodes()) {
                rnodes1.add(rn);
                rnodes.add(rn);
            }
            for (RNode rn : snri.route2.getRNodes()) {
                rnodes2.add(rn);
                rnodes.add(rn);
            }

        }

        this.mapHelper.showRNodes(rnodes);
        this.mapHelper.setCenter(rnodes.get(0));

        if (this.selectedRoutes.size() > 1) {
            this.tbxInfo1.setText("Multiple routes are selected");
            this.tbxInfo2.setText("Multiple routes are selected");
        } else {
            this.tbxInfo1.setText(this.getRouteInfoString(this.selectedRoutes.get(0).route1));
            this.tbxInfo2.setText(this.getRouteInfoString(this.selectedRoutes.get(0).route2));
        }
    }
    
    /***
     * returns route information string
     * 
     * @param r route
     * @return rnode information
     */
    protected String getRouteInfoString(Route r) {
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("Name : %s", r.name));
        sb.append(System.getProperty("line.separator"));

        if (r.desc != null && !r.desc.isEmpty()) {
            sb.append("----------------");
            sb.append(System.getProperty("line.separator"));
            sb.append(r.desc);
            sb.append(System.getProperty("line.separator"));
        }

        sb.append("----------------");
        sb.append(System.getProperty("line.separator"));
        Infra infra = Infra.getInstance();
        int idx = 1;
        for (RNode rnode : r.getRNodes()) {
            if (infra.isStation(rnode)) {
                sb.append(String.format("[%02d] (S) %s (%s)", idx, rnode.label, rnode.station_id));
            } else if (infra.isEntrance(rnode)) {
                sb.append(String.format("[%02d] (E) %s (%s)", idx, rnode.label, rnode.name));
            } else if (infra.isExit(rnode)) {
                sb.append(String.format("[%02d] (X) %s (%s)", idx, rnode.label, rnode.name));
            }
            idx++;
            sb.append(System.getProperty("line.separator"));
        }
        sb.setLength(sb.length() - 2);
        return sb.toString();
    }
    

//    protected void filterByCorridor() {
//        int slt = this.cbxCorridors.getSelectedIndex();
//        Corridor corr = null;
//        if (slt > 0) {
//            corr = (Corridor) this.cbxCorridors.getSelectedItem();
//        }
//        final DefaultTableModel tm = (DefaultTableModel) this.tbRouteList.getModel();
//        tm.getDataVector().removeAllElements();
//        tm.fireTableDataChanged();
//        boolean isAdded = false;
//        for (SnowRouteInfo s : this.snowRouteList) {
//            if (corr == null || s.route1.getRNodes().get(0).corridor.equals(corr.name)) {
//                tm.addRow(new Object[]{s});
//                isAdded = true;
//            }
//        }
//        if (isAdded) {
//            //this.compRouteListTable.selectAll();
//            //setProperties();
//        }
//        setProperties();
//
//    }
//
//    protected void setProperties() {
//        this.selectedSnowRoute.clear();
//
//        DefaultTableModel tm = (DefaultTableModel) this.tbRouteList.getModel();
//        for (int row : this.tbRouteList.getSelectedRows()) {
//            SnowRouteInfo s = (SnowRouteInfo) tm.getValueAt(row, 0);
//            if (s != null) {
//                this.selectedSnowRoute.add(s);
//            }
//        }
//
//        if (this.selectedSnowRoute.isEmpty()) {
//            this.mapHelper.clear();
//            this.tbxInfo1.setText("");
//            this.tbxInfo2.setText("");
//            return;
//        }
//
//        List<RNode> rnodes = new ArrayList<RNode>();
//        List<RNode> rnodes1 = new ArrayList<RNode>();
//        List<RNode> rnodes2 = new ArrayList<RNode>();
//        for (SnowRouteInfo snri : this.selectedSnowRoute) {
//            for (RNode rn : snri.route1.getRNodes()) {
//                rnodes1.add(rn);
//                rnodes.add(rn);
//            }
//            for (RNode rn : snri.route2.getRNodes()) {
//                rnodes2.add(rn);
//                rnodes.add(rn);
//            }
//
//        }
//
//        this.mapHelper.showRNodes(rnodes);
//        this.mapHelper.setCenter(rnodes.get(0));
//
//        if (this.selectedSnowRoute.size() > 1) {
//            this.tbxInfo1.setText("Multiple routes are selected");
//            this.tbxInfo2.setText("Multiple routes are selected");
//        } else {
//            this.tbxInfo1.setText(this.getRouteInfoString(this.selectedSnowRoute.get(0).route1));
//            this.tbxInfo2.setText(this.getRouteInfoString(this.selectedSnowRoute.get(0).route2));
//        }
//    }
//
//    protected String getRouteInfoString(Route r) {
//        StringBuilder sb = new StringBuilder();
//        sb.append(String.format("Name : %s", r.name));
//        sb.append(System.getProperty("line.separator"));
//
//        if (r.desc != null && !r.desc.isEmpty()) {
//            sb.append("----------------");
//            sb.append(System.getProperty("line.separator"));
//            sb.append(r.desc);
//            sb.append(System.getProperty("line.separator"));
//        }
//
//        sb.append("----------------");
//        sb.append(System.getProperty("line.separator"));
//        Infra infra = Infra.getInstance();
//        int idx = 1;
//        for (RNode rnode : r.getRNodes()) {
//            if (infra.isStation(rnode)) {
//                sb.append(String.format("[%02d] (S) %s (%s)", idx, rnode.label, rnode.station_id));
//            } else if (infra.isEntrance(rnode)) {
//                sb.append(String.format("[%02d] (E) %s (%s)", idx, rnode.label, rnode.name));
//            } else if (infra.isExit(rnode)) {
//                sb.append(String.format("[%02d] (X) %s (%s)", idx, rnode.label, rnode.name));
//            }
//            idx++;
//            sb.append(System.getProperty("line.separator"));
//        }
//        sb.setLength(sb.length() - 2);
//        return sb.toString();
//    }
//// TODO: update here
////    @Override
////    public void listLoaded(List<SnowRouteInfo> routeList) {
////        this.snowRouteList = routeList;
////        filterByCorridor();
////    }
//
//    protected void deleteRoutes() {
//        if (this.selectedSnowRoute.isEmpty()) {
//            return;
//        }
//
//        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected routes ?", "Confirm", JOptionPane.YES_NO_OPTION);
//
//        if (res == JOptionPane.YES_OPTION) {
//            for (SnowRouteInfo r : this.selectedSnowRoute) {
//                // TODO: update here
////                SnowRouteClient.getInstance().delete(r.id);
//            }
//// TODO: update here
////            SnowRouteClient.getInstance().list(null);
//        }
//    }
//
//    protected void saveRouteConfig(Route r) {
//        SNRouteLaneConfigDialog rlcd = new SNRouteLaneConfigDialog(r, null, true);
//        rlcd.setVisible(true);
//    }
//
//    protected void editRoute() {
//        if (this.selectedSnowRoute.isEmpty() || this.selectedSnowRoute.size() > 1) {
//            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single route to edit information");
//            return;
//        }
//        SNRouteEditDialog red = new SNRouteEditDialog(TeTRESConfig.mainFrame, this.selectedSnowRoute.get(0));
//        red.setVisible(true);
//    }
//
//    private void createRoute() {
//        SNRouteCreateDialog rcd = new SNRouteCreateDialog(TeTRESConfig.mainFrame, true);
//        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
//        rcd.setVisible(true);
//    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        asyncRequestAdapter1 = new org.jdesktop.http.async.event.AsyncRequestAdapter();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane3 = new javax.swing.JScrollPane();
        tbRouteList = new javax.swing.JTable();
        btnDeleteSelection = new javax.swing.JButton();
        btnEditRoute = new javax.swing.JButton();
        jxMap = new org.jdesktop.swingx.JXMapKit();
        jLabel1 = new javax.swing.JLabel();
        cbxCorridors = new javax.swing.JComboBox();
        btnAddRoute = new javax.swing.JButton();
        panRouteInfo = new javax.swing.JSplitPane();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxInfo1 = new javax.swing.JTextArea();
        jScrollPane2 = new javax.swing.JScrollPane();
        tbxInfo2 = new javax.swing.JTextArea();

        jLabel2.setText("Truck Route List");

        tbRouteList.setFont(new java.awt.Font("Verdana", 0, 10)); // NOI18N
        tbRouteList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null},
                {null},
                {null},
                {null}
            },
            new String [] {
                "Name"
            }
        ) {
            boolean[] canEdit = new boolean [] {
                false
            };

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        tbRouteList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane3.setViewportView(tbRouteList);

        btnDeleteSelection.setText("Delete");
        btnDeleteSelection.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteSelectionActionPerformed(evt);
            }
        });

        btnEditRoute.setText("Edit Route Info");
        btnEditRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEditRouteActionPerformed(evt);
            }
        });

        jLabel1.setText("Filter by Corridor");

        btnAddRoute.setText("Add Truck Route");
        btnAddRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRouteActionPerformed(evt);
            }
        });

        panRouteInfo.setOrientation(javax.swing.JSplitPane.VERTICAL_SPLIT);

        tbxInfo1.setColumns(20);
        tbxInfo1.setFont(new java.awt.Font("Tahoma", 0, 11)); // NOI18N
        tbxInfo1.setRows(5);
        jScrollPane1.setViewportView(tbxInfo1);

        panRouteInfo.setTopComponent(jScrollPane1);

        tbxInfo2.setColumns(20);
        tbxInfo2.setFont(new java.awt.Font("Tahoma", 0, 11)); // NOI18N
        tbxInfo2.setRows(5);
        jScrollPane2.setViewportView(tbxInfo2);

        panRouteInfo.setBottomComponent(jScrollPane2);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(btnDeleteSelection, javax.swing.GroupLayout.PREFERRED_SIZE, 86, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnEditRoute, javax.swing.GroupLayout.DEFAULT_SIZE, 125, Short.MAX_VALUE))
                    .addComponent(jLabel2)
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addComponent(jLabel1)
                    .addComponent(cbxCorridors, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnAddRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addGap(18, 18, 18)
                .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 504, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addComponent(panRouteInfo, javax.swing.GroupLayout.PREFERRED_SIZE, 228, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(btnAddRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 35, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(cbxCorridors, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel2)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                        .addGap(18, 18, 18)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(btnDeleteSelection, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(btnEditRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addComponent(jxMap, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, 604, Short.MAX_VALUE)
                    .addComponent(panRouteInfo))
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

        private void btnDeleteSelectionActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteSelectionActionPerformed
            this.deleteSnowRoutes();
        }//GEN-LAST:event_btnDeleteSelectionActionPerformed

    private void btnAddRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddRouteActionPerformed
        createRoute();
    }//GEN-LAST:event_btnAddRouteActionPerformed

    private void btnEditRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEditRouteActionPerformed
        this.editRoute();
    }//GEN-LAST:event_btnEditRouteActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private org.jdesktop.http.async.event.AsyncRequestAdapter asyncRequestAdapter1;
    private javax.swing.JButton btnAddRoute;
    private javax.swing.JButton btnDeleteSelection;
    private javax.swing.JButton btnEditRoute;
    private javax.swing.JComboBox cbxCorridors;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private org.jdesktop.swingx.JXMapKit jxMap;
    private javax.swing.JSplitPane panRouteInfo;
    private javax.swing.JTable tbRouteList;
    private javax.swing.JTextArea tbxInfo1;
    private javax.swing.JTextArea tbxInfo2;
    // End of variables declaration//GEN-END:variables

}
