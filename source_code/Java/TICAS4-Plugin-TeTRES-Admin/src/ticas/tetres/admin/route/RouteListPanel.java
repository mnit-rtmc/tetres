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
package ticas.tetres.admin.route;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.infra.RNode;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpResult;
import ticas.common.ui.map.MapHelper;
import ticas.common.route.Route;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.api.ReliabilityRouteClient;
import ticas.tetres.admin.types.AbstractDataChangeListener;
import ticas.tetres.admin.types.ReliabilityRouteInfo;
import ticas.common.ui.map.TileServerFactory;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.RowSorter;
import javax.swing.SortOrder;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableModel;
import javax.swing.table.TableRowSorter;
import org.apache.logging.log4j.core.Logger;

/**
 *
 * @author Chongmyung Park
 */
public class RouteListPanel extends javax.swing.JPanel {

    private Infra infra;
    private List<Corridor> corridors = new ArrayList<>();
    private MapHelper mapHelper;
    private List<ReliabilityRouteInfo> routeList = new ArrayList<>();
    private List<ReliabilityRouteInfo> selectedRoutes = new ArrayList<>();
    private Logger logger;
    private ReliabilityRouteClient model;

    /**
     * Creates new form RouteEditorPanel
     */
    public RouteListPanel() {
        initComponents();
    }

    /**
     * *
     * initialize variables and UI
     */
    public void init() {
        this.jxMap.setTileFactory(TileServerFactory.getTileFactory());
        this.mapHelper = new MapHelper(jxMap);
        this.infra = Infra.getInstance();
        this.corridors = infra.getCorridors();
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.model = new ReliabilityRouteClient();

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
        this.model.addChangeListener(new AbstractDataChangeListener<ReliabilityRouteInfo>() {

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of travel time route");
            }

            @Override
            public void listSuccess(List<ReliabilityRouteInfo> list) {
                selectedRoutes.clear();
                mapHelper.clear();
                routeList = list;
                tbxInfo.setText("");
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

        TableRowSorter<TableModel> sorter = new TableRowSorter<TableModel>(this.tbRouteList.getModel());
        this.tbRouteList.setRowSorter(sorter);

        List<RowSorter.SortKey> sortKeys = new ArrayList<>(25);
        sortKeys.add(new RowSorter.SortKey(0, SortOrder.ASCENDING));
        sortKeys.add(new RowSorter.SortKey(1, SortOrder.ASCENDING));
        sorter.setSortKeys(sortKeys);

        this.model.list();

    }

    public void refresh() {
        this.model.list();
    }

    /**
     * *
     * open route edit dialog
     */
    protected void editRoute() {
        if (this.selectedRoutes.isEmpty() || this.selectedRoutes.size() > 1) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single route to edit information");
            return;
        }
        RouteEditDialog red = new RouteEditDialog(TeTRESConfig.mainFrame, this.selectedRoutes.get(0));
        red.setLocationRelativeTo(TeTRESConfig.mainFrame);
        red.setVisible(true);
        this.model.list();
    }

    /**
     * *
     * open route creation dialog
     */
    private void createRoute() {
        Corridor corr = null;
        try {
            corr = (Corridor) this.cbxCorridors.getSelectedItem();
        } catch (java.lang.ClassCastException ex) {
        }

        RouteCreateDialog rcd = new RouteCreateDialog(TeTRESConfig.mainFrame, true, corr);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);

        rcd.setVisible(true);
        if (rcd.oppositeRouteId != null) {
            ReliabilityRouteInfo ttri = this.model.getSynced(rcd.oppositeRouteId.toString());
            RouteEditDialog red = new RouteEditDialog(TeTRESConfig.mainFrame, ttri);
            red.setLocationRelativeTo(TeTRESConfig.mainFrame);
            red.setVisible(true);
        }
        this.model.list();
    }

    /**
     * delete selected items
     */
    protected void deleteTravelTimeRoutes() {
        if (this.routeList.isEmpty()) {
            return;
        }

        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected routes?", "Confirm", JOptionPane.YES_NO_OPTION);

        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (ReliabilityRouteInfo se : this.selectedRoutes) {
                ids.add(se.id);
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
        this.tbxInfo.setText("");
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
        for (ReliabilityRouteInfo s : this.routeList) {
            if (corr == null || s.corridor.equals(corr.name)) {
                tm.addRow(new Object[]{s.corridor, s});
            }
        }
    }

    /**
     * *
     * set map and route info when route on table is clicked
     */
    protected void setProperties() {
        this.selectedRoutes.clear();

        DefaultTableModel tm = (DefaultTableModel) this.tbRouteList.getModel();
        for (int row : this.tbRouteList.getSelectedRows()) {
            int modelRow = this.tbRouteList.convertRowIndexToModel(row);
            ReliabilityRouteInfo s = (ReliabilityRouteInfo) tm.getValueAt(modelRow, 1);
            if (s != null) {
                this.selectedRoutes.add(s);
            }
        }

        if (this.selectedRoutes.isEmpty()) {
            this.mapHelper.clear();
            this.tbxInfo.setText("");
            return;
        }

        List<RNode> rnodes = new ArrayList<RNode>();
        for (ReliabilityRouteInfo ttri : this.selectedRoutes) {
            for (RNode rn : ttri.route.getRNodes()) {
                rnodes.add(rn);
            }
        }

        this.mapHelper.showRNodes(rnodes);
        this.mapHelper.setCenter(rnodes.get(0));

        if (this.selectedRoutes.size() > 1) {
            this.tbxInfo.setText("Multiple routes are selected");
        } else {
            this.tbxInfo.setText(this.getRouteInfoString(this.selectedRoutes.get(0).route));
        }
    }

    /**
     * *
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
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxInfo = new javax.swing.JTextArea();
        jLabel1 = new javax.swing.JLabel();
        cbxCorridors = new javax.swing.JComboBox();
        btnAddRoute = new javax.swing.JButton();

        jLabel2.setText("Pre-defined Travel Time Route List");

        tbRouteList.setFont(new java.awt.Font("Verdana", 0, 10)); // NOI18N
        tbRouteList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {
                {null, null},
                {null, null},
                {null, null},
                {null, null}
            },
            new String [] {
                "Corridor", "Name"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.Object.class
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
        tbRouteList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane3.setViewportView(tbRouteList);
        if (tbRouteList.getColumnModel().getColumnCount() > 0) {
            tbRouteList.getColumnModel().getColumn(0).setMinWidth(100);
            tbRouteList.getColumnModel().getColumn(0).setPreferredWidth(100);
            tbRouteList.getColumnModel().getColumn(0).setMaxWidth(300);
        }

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

        tbxInfo.setColumns(20);
        tbxInfo.setFont(new java.awt.Font("Tahoma", 0, 11)); // NOI18N
        tbxInfo.setRows(5);
        jScrollPane1.setViewportView(tbxInfo);

        jLabel1.setText("Filter by Corridor");

        btnAddRoute.setText("Add Travel Time Route");
        btnAddRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRouteActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addGroup(layout.createSequentialGroup()
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(btnDeleteSelection, javax.swing.GroupLayout.PREFERRED_SIZE, 86, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(jLabel2)
                            .addComponent(jLabel1))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 62, Short.MAX_VALUE)
                        .addComponent(btnEditRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 125, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addComponent(cbxCorridors, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnAddRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addGap(18, 18, 18)
                .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 373, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 228, javax.swing.GroupLayout.PREFERRED_SIZE)
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
                    .addComponent(jScrollPane1)
                    .addComponent(jxMap, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, 604, Short.MAX_VALUE))
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

        private void btnDeleteSelectionActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteSelectionActionPerformed
            this.deleteTravelTimeRoutes();
        }//GEN-LAST:event_btnDeleteSelectionActionPerformed

    private void btnAddRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddRouteActionPerformed
        this.createRoute();
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
    private javax.swing.JScrollPane jScrollPane3;
    private org.jdesktop.swingx.JXMapKit jxMap;
    private javax.swing.JTable tbRouteList;
    private javax.swing.JTextArea tbxInfo;
    // End of variables declaration//GEN-END:variables

}
