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
package ticas.tetres.user.panels.routegroup;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.pyticas.HttpResult;
import ticas.tetres.user.TeTRESConfig;
import ticas.tetres.user.api.ReliabilityRouteAPIClient;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import ticas.tetres.user.types.AbstractDataChangeListener;
import ticas.tetres.user.types.ReliabilityRouteInfo;
import ticas.tetres.user.types.RouteGroupInfo;
import ticas.common.ui.CorridorSelector;
import ticas.common.ui.IInitializable;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import javax.swing.DefaultListModel;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public final class PanelRouteGroup extends javax.swing.JPanel implements IInitializable, IRouteGroupListChangeListener {

    private ReliabilityRouteAPIClient routeAPI;
    private final int initZoom = 10;
    private final double initLatitude = 44.974878;
    private final double initLongitude = -93.233414;
    private RouteGroupInfo selectedRouteGroup;
    private ReliabilityRouteInfo selectedRouteInfo;

    /**
     * Creates new form PanelDataFilters
     */
    public PanelRouteGroup() {
        initComponents();
    }

    @Override
    public void init() {
        DefaultListModel routeGroupModel = new DefaultListModel();
        this.lstRouteGroups.setModel(routeGroupModel);
        
        DefaultListModel routeModel = new DefaultListModel();
        this.lstRouteList.setModel(routeModel);
        
        this.panMap.init();
        this.panMap.mapHelper.setCenter(this.initLatitude, this.initLongitude);
        this.panMap.mapHelper.jmKit.setZoom(this.initZoom);
        this.routeAPI = new ReliabilityRouteAPIClient();
        
        RouteGroupInfoHelper.addChangeListener(this);
        
        // when RouteAPIClient gets route list from the server
        this.routeAPI.addChangeListener(new AbstractDataChangeListener<ReliabilityRouteInfo>() {
            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of travel time route");
            }

            @Override
            public void listSuccess(List<ReliabilityRouteInfo> list) {
                onRouteListSuccess(list);
            }
        });
        
        // a route is selected from the combobox
        this.cbxRoute.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                ReliabilityRouteInfo _selectedRouteInfo = (ReliabilityRouteInfo) cbxRoute.getSelectedItem();
                panMap.mapHelper.clear();
                if (_selectedRouteInfo != null) {
                    panMap.mapHelper.showRoute(_selectedRouteInfo.route);
                    panMap.mapHelper.setCenter(_selectedRouteInfo.route.getRNodes().get(0));
                }
            }
        });
        
        // a Route Group is selected
        this.lstRouteGroups.addListSelectionListener(new ListSelectionListener() {
            @Override
            public void valueChanged(ListSelectionEvent e) {
                selectedRouteGroup = lstRouteGroups.getSelectedValue();
                setRouteList();
            }
        });        
        
        // a Route is selected 
        this.lstRouteList.addListSelectionListener(new ListSelectionListener() {
            @Override
            public void valueChanged(ListSelectionEvent lse) {
                selectedRouteInfo = (ReliabilityRouteInfo) lstRouteList.getSelectedValue();
                panMap.mapHelper.clear();
                if (selectedRouteInfo != null) {
                    panMap.mapHelper.showRoute(selectedRouteInfo.route);
                    panMap.mapHelper.setCenter(selectedRouteInfo.route.getRNodes().get(0));
                }
            }
        });

        
        RouteGroupInfoHelper.loadRouteGroups();
        this.loadCorridors();
    }
    
    @Override
    public void refresh() {
        // do nothing
    }        

    private void loadCorridors() {
        this.cbxCorridor.init(Infra.getInstance(), new CorridorSelector.CorridorSelectedListener() {
            @Override
            public void OnSelected(int selectedIndex, Corridor corridor) {
                routeAPI.listByCorridor(corridor);
            }
        });
    }
    
    private void setRouteList() {
        if(this.selectedRouteGroup == null) {
            return;
        }
        DefaultListModel model = new DefaultListModel();
        model.removeAllElements();
        for(ReliabilityRouteInfo routeInfo : this.selectedRouteGroup.route_list) {
            model.addElement(routeInfo);
        }
        this.lstRouteList.setModel(model);
    }       

    private void onRouteListSuccess(List<ReliabilityRouteInfo> list) {
        this.cbxRoute.removeAllItems();
        for (ReliabilityRouteInfo rri : list) {
            this.cbxRoute.addItem(rri);
        }
    }

    private void addRouteGroup() {
        RouteGroupEditDialog rged = new RouteGroupEditDialog(TeTRESConfig.mainFrame, true);
        rged.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rged.setVisible(true);
    }
    
    private void deleteRouteGroup() {
        if(this.selectedRouteGroup == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a route group on the list");
            return;
        }
        if (JOptionPane.showConfirmDialog(this, "Delete the selected route group from the list?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
            return;
        }        
        RouteGroupInfoHelper.delete(this.selectedRouteGroup);
        
        this.reset();
        RouteGroupInfoHelper.loadRouteGroups();
    }

    private void editRouteGroup() {
        if(this.selectedRouteGroup == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a route group on the list");
            return;
        }
        RouteGroupEditDialog rged = new RouteGroupEditDialog(this.selectedRouteGroup, TeTRESConfig.mainFrame, true);
        rged.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rged.setVisible(true);
    }    
    
    private void addRouteList() {
        if(this.selectedRouteGroup == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a route group in the list");
            return;            
        }
        ReliabilityRouteInfo routeInfo = (ReliabilityRouteInfo)this.cbxRoute.getSelectedItem();
        if(routeInfo == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a route in the route combobox");
            return;
        }
        DefaultListModel model = (DefaultListModel)this.lstRouteList.getModel();
        if(model.contains(routeInfo)) {
            return;
        }
        model.addElement(routeInfo);       
        this.selectedRouteGroup.route_list.add(routeInfo);
        RouteGroupInfoHelper.save(this.selectedRouteGroup);
    }
    
    private void deleteRouteList() {
        if(this.selectedRouteGroup == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a route group in the list");
            return;            
        }        
        List<ReliabilityRouteInfo> selectedRoutes = this.lstRouteList.getSelectedValuesList();
        if(selectedRoutes.isEmpty()) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a route on the list");
            return;
        }
        if (JOptionPane.showConfirmDialog(this, "Delete the selected routes from the list?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
            return;
        }
        
        DefaultListModel model = (DefaultListModel)this.lstRouteList.getModel();
        for(ReliabilityRouteInfo routeInfo : selectedRoutes) 
        {
            model.removeElement(routeInfo);                    
            if(this.selectedRouteGroup != null) {
                this.selectedRouteGroup.route_list.remove(routeInfo);
            }
        }       
        RouteGroupInfoHelper.save(this.selectedRouteGroup);
    }    
    

    
    @Override
    public void routeGroupUpdated(List<RouteGroupInfo> groups) {
        DefaultListModel model = (DefaultListModel)this.lstRouteGroups.getModel();
        model.removeAllElements();
        for(RouteGroupInfo ginfo : groups) {
            model.addElement(ginfo);
        }
        this.reset();
    }    
    
    private void reset() {
        this.selectedRouteGroup = null;
        this.selectedRouteInfo = null;
        this.lstRouteList.removeAll();
        this.panMap.mapHelper.clear();
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jPanel7 = new javax.swing.JPanel();
        jLabel9 = new javax.swing.JLabel();
        btnAddRouteGroup = new javax.swing.JButton();
        jScrollPane1 = new javax.swing.JScrollPane();
        lstRouteGroups = new javax.swing.JList<>();
        btnDeleteRouteGroup = new javax.swing.JButton();
        btnEditRouteGroup = new javax.swing.JButton();
        jPanel1 = new javax.swing.JPanel();
        jLabel12 = new javax.swing.JLabel();
        btnDeleteRouteList = new javax.swing.JButton();
        jScrollPane2 = new javax.swing.JScrollPane();
        lstRouteList = new javax.swing.JList<>();
        jLabel10 = new javax.swing.JLabel();
        cbxCorridor = new ticas.common.ui.CorridorSelector();
        jLabel11 = new javax.swing.JLabel();
        cbxRoute = new javax.swing.JComboBox<>();
        btnAddRouteList = new javax.swing.JButton();
        jLabel1 = new javax.swing.JLabel();
        jSeparator1 = new javax.swing.JSeparator();
        panMap = new ticas.common.ui.map.MapPanel();

        jLabel9.setText("List of Defined Route Group");

        btnAddRouteGroup.setText("+");
        btnAddRouteGroup.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRouteGroupActionPerformed(evt);
            }
        });

        jScrollPane1.setViewportView(lstRouteGroups);

        btnDeleteRouteGroup.setText("Delete");
        btnDeleteRouteGroup.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteRouteGroupActionPerformed(evt);
            }
        });

        btnEditRouteGroup.setText("Edit");
        btnEditRouteGroup.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEditRouteGroupActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel7Layout = new javax.swing.GroupLayout(jPanel7);
        jPanel7.setLayout(jPanel7Layout);
        jPanel7Layout.setHorizontalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addGroup(jPanel7Layout.createSequentialGroup()
                        .addComponent(jLabel9)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 80, Short.MAX_VALUE)
                        .addComponent(btnAddRouteGroup))
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel7Layout.createSequentialGroup()
                        .addComponent(btnEditRouteGroup, javax.swing.GroupLayout.PREFERRED_SIZE, 65, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnDeleteRouteGroup, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel7Layout.setVerticalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel9)
                    .addComponent(btnAddRouteGroup))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jScrollPane1)
                .addGap(18, 18, 18)
                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnDeleteRouteGroup)
                    .addComponent(btnEditRouteGroup))
                .addContainerGap())
        );

        jLabel12.setText("Route List of the Selected Route Group");

        btnDeleteRouteList.setText("Delete");
        btnDeleteRouteList.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteRouteListActionPerformed(evt);
            }
        });

        jScrollPane2.setViewportView(lstRouteList);

        jLabel10.setText("Corridor");

        jLabel11.setText("Route");

        btnAddRouteList.setText("Add");
        btnAddRouteList.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRouteListActionPerformed(evt);
            }
        });

        jLabel1.setText("Add Route to the selected route group");

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jSeparator1)
                    .addComponent(jScrollPane2, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addComponent(btnDeleteRouteList, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGap(10, 10, 10)
                        .addComponent(jLabel10)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(cbxCorridor, javax.swing.GroupLayout.DEFAULT_SIZE, 0, Short.MAX_VALUE))
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGap(20, 20, 20)
                        .addComponent(jLabel11)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(cbxRoute, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addComponent(btnAddRouteList, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel12)
                            .addComponent(jLabel1))
                        .addGap(0, 26, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                .addGap(17, 17, 17)
                .addComponent(jLabel1)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel10)
                    .addComponent(cbxCorridor, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel11)
                    .addComponent(cbxRoute, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(btnAddRouteList)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jSeparator1, javax.swing.GroupLayout.PREFERRED_SIZE, 10, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(13, 13, 13)
                .addComponent(jLabel12)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 194, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addComponent(btnDeleteRouteList)
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel7, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(panMap, javax.swing.GroupLayout.DEFAULT_SIZE, 244, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel7, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(panMap, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE))
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

    private void btnAddRouteGroupActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddRouteGroupActionPerformed
        this.addRouteGroup();
    }//GEN-LAST:event_btnAddRouteGroupActionPerformed

    private void btnDeleteRouteGroupActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteRouteGroupActionPerformed
        this.deleteRouteGroup();
    }//GEN-LAST:event_btnDeleteRouteGroupActionPerformed

    private void btnEditRouteGroupActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEditRouteGroupActionPerformed
        this.editRouteGroup();
    }//GEN-LAST:event_btnEditRouteGroupActionPerformed

    private void btnDeleteRouteListActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteRouteListActionPerformed
        this.deleteRouteList();
    }//GEN-LAST:event_btnDeleteRouteListActionPerformed

    private void btnAddRouteListActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddRouteListActionPerformed
        this.addRouteList();
    }//GEN-LAST:event_btnAddRouteListActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnAddRouteGroup;
    private javax.swing.JButton btnAddRouteList;
    private javax.swing.JButton btnDeleteRouteGroup;
    private javax.swing.JButton btnDeleteRouteList;
    private javax.swing.JButton btnEditRouteGroup;
    private ticas.common.ui.CorridorSelector cbxCorridor;
    private javax.swing.JComboBox<ReliabilityRouteInfo> cbxRoute;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel11;
    private javax.swing.JLabel jLabel12;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel7;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JSeparator jSeparator1;
    private javax.swing.JList<ticas.tetres.user.types.RouteGroupInfo> lstRouteGroups;
    private javax.swing.JList<ticas.tetres.user.types.ReliabilityRouteInfo> lstRouteList;
    private ticas.common.ui.map.MapPanel panMap;
    // End of variables declaration//GEN-END:variables








}
