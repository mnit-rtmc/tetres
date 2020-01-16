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
package ncrtes.snowroute;

import common.infra.Corridor;
import common.infra.Infra;
import common.infra.InfraObject;
import common.infra.RNode;
import common.pyticas.HttpResult;
import common.route.Route;
import common.route.RouteCreationHelper;
import ncrtes.NCRTESConfig;
import ncrtes.api.SnowRouteClient;
import ncrtes.types.AbstractDataChangeListener;
import ncrtes.types.SnowRouteGroupInfo;
import ncrtes.types.SnowRouteInfo;
import common.route.RouteEditHelper;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SNRouteEditDialog extends javax.swing.JDialog {

    public Route route;
    private RouteCreationHelper routeCreationHelper;
    private SnowRouteGroupInfo snrgi;
    private SnowRouteInfo snri;    
    private SnowRouteClient snrApi;

    /**
     * Creates new form RouteCreateDialog
     */
    public SNRouteEditDialog(java.awt.Frame parent, SnowRouteGroupInfo snrgi, SnowRouteInfo snri, boolean modal) {
        super(parent, modal);
        initComponents();
        this.init(snrgi, snri);
    }

    private void init(SnowRouteGroupInfo snrgi, SnowRouteInfo snri) {
        if(snri == null) {
            this.routeCreationHelper = new RouteCreationHelper();
        } else {
            this.routeCreationHelper = new RouteEditHelper();
        }
        this.routeCreationHelper.init(null, this.jmKit, this.cbxCorridors, this.lbxRoutes);
        this.snrApi = new SnowRouteClient();
        this.snrgi = snrgi;
        this.snri = snri;

        if (this.snri != null) {
            this.tbxName.setText(this.snri.name);
            this.tbxDesc.setText(this.snri.description);

            List<RNode> rnodes = new ArrayList<>();
            for (RNode rn : snri.route1.getRNodes()) {
                rnodes.add(rn);
            }
            for (RNode rn : snri.route2.getRNodes()) {
                rnodes.add(rn);
            }
            this.route = snri.route1;
            Infra infra = Infra.getInstance();
            RNode firstStation = this.route.getRNodes().get(0);
            RNode lastStation = this.route.getRNodes().get(this.route.getRNodes().size()-1);
            ArrayList<InfraObject> upstreamRNodes = routeCreationHelper.getUpstreamRNodes(infra.getCorridor(firstStation.corridor), firstStation, false);
            ArrayList<InfraObject> downstreamRNodes = routeCreationHelper.getDownstreamRNodes(infra.getCorridor(lastStation.corridor), lastStation, false);
            
            List<InfraObject> allRNodes = new ArrayList<InfraObject>();
            allRNodes.addAll(upstreamRNodes);
            allRNodes.addAll(this.route.getRNodes());
            allRNodes.addAll(downstreamRNodes);
 
            List<InfraObject> blues = new ArrayList<InfraObject>();            
            blues.addAll(upstreamRNodes);            
            blues.addAll(downstreamRNodes);            
 
            
            this.cbxCorridors.removeItemListener(this.routeCreationHelper.corridorItemListener);
            cbxCorridors.setSelectedItem(infra.getCorridor(this.route.getRNodes().get(0).corridor));
            this.cbxCorridors.setEnabled(false);            
            routeCreationHelper.reset();
            routeCreationHelper.isReady = true;
            routeCreationHelper.routePointList.clear();
            routeCreationHelper.routePointList.addAll(this.route.getRNodes());
            routeCreationHelper.mapHelper.showInfraObjects(allRNodes);
            routeCreationHelper.mapHelper.setRouteAsBlueMarker(blues.toArray(new InfraObject[blues.size()]));
            routeCreationHelper.updateRoutes();          
            routeCreationHelper.mapHelper.setCenter(this.route.getRNodes().get(0));
        }

        this.snrApi.addChangeListener(new AbstractDataChangeListener<SnowRouteInfo>() {
            @Override
            public void insertFailed(HttpResult result, SnowRouteInfo obj) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to add snow management route data");
            }

            @Override
            public void insertSuccess(Integer id) {
                dispose();
            }
            
            
            @Override
            public void updateSuccess(int id) {
                dispose();
            }            

            @Override
            public void updateFailed(HttpResult result, SnowRouteInfo obj) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to update snow management route data");
            }
            
        });
 
    }


    private void saveOrUpdate() {
        if (!this.routeCreationHelper.isReady) {
            JOptionPane.showMessageDialog(null, "Please click after finishing snow management route creation");
            return;
        }
        
        Route r = new Route("tmp route", "temporary");
        for (RNode rn : this.routeCreationHelper.routePointList) {
            r.addRNode(rn);
        }
        
        if (r == null) {
            JOptionPane.showMessageDialog(null, "Please make lane configuration before saving route");
            return;
        }

        String desc = this.tbxDesc.getText();
        String name = this.tbxName.getText();        

        if (name.isEmpty()) {
            JOptionPane.showMessageDialog(null, "Please enter name");
            return;
        }
        
        SnowRouteInfo mSnri = null;
        
        if(this.snri != null) mSnri = this.snri.clone();        
        else mSnri = new SnowRouteInfo();
        
        mSnri.snowroute_group_id = this.snrgi.id;
        mSnri.name = name;
        mSnri.description = desc;
        mSnri.route1 = r;
        mSnri.route2 = null;
        
        if (this.snri == null) {            
            this.snrApi.insert(mSnri, r);
        } else {
            this.snrApi.update(this.snri, mSnri);
        }

    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">
    private void initComponents() {

        panInputs = new javax.swing.JPanel();
        jLabel2 = new javax.swing.JLabel();
        cbxCorridors = new javax.swing.JComboBox();
        jLabel3 = new javax.swing.JLabel();
        btnSave = new javax.swing.JButton();
        btnReset = new javax.swing.JButton();
        jScrollPane2 = new javax.swing.JScrollPane();
        lbxRoutes = new javax.swing.JList();
        jLabel4 = new javax.swing.JLabel();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxDesc = new javax.swing.JTextArea();
        btnCancel = new javax.swing.JButton();
        jLabel8 = new javax.swing.JLabel();
        tbxName = new javax.swing.JTextField();
        jmKit = new org.jdesktop.swingx.JXMapKit();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Snow Management Route Editor");
        setModal(true);

        jLabel2.setText("Select starting corridor :");

        cbxCorridors.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                cbxCorridorsActionPerformed(evt);
            }
        });

        jLabel3.setText("Station and Ramps included in Section");

        btnSave.setText("Save Configuration");
        btnSave.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSaveActionPerformed(evt);
            }
        });

        btnReset.setText("Reset");
        btnReset.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnResetActionPerformed(evt);
            }
        });

        jScrollPane2.setViewportView(lbxRoutes);

        jLabel4.setText("Memo");

        tbxDesc.setColumns(20);
        tbxDesc.setLineWrap(true);
        tbxDesc.setRows(5);
        tbxDesc.setWrapStyleWord(true);
        jScrollPane1.setViewportView(tbxDesc);

        btnCancel.setText("Cancel");
        btnCancel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCancelActionPerformed(evt);
            }
        });

        jLabel8.setText("Name");

        javax.swing.GroupLayout panInputsLayout = new javax.swing.GroupLayout(panInputs);
        panInputs.setLayout(panInputsLayout);
        panInputsLayout.setHorizontalGroup(
            panInputsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(panInputsLayout.createSequentialGroup()
                .addContainerGap()
                .addGroup(panInputsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, panInputsLayout.createSequentialGroup()
                        .addComponent(btnCancel, javax.swing.GroupLayout.PREFERRED_SIZE, 76, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(btnReset, javax.swing.GroupLayout.PREFERRED_SIZE, 76, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(btnSave))
                    .addComponent(jScrollPane2)
                    .addComponent(jScrollPane1)
                    .addComponent(cbxCorridors, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(panInputsLayout.createSequentialGroup()
                        .addGroup(panInputsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel3)
                            .addComponent(jLabel8)
                            .addComponent(jLabel4)
                            .addComponent(jLabel2))
                        .addGap(0, 0, Short.MAX_VALUE))
                    .addComponent(tbxName))
                .addContainerGap())
        );
        panInputsLayout.setVerticalGroup(
            panInputsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(panInputsLayout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel8)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(tbxName, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(13, 13, 13)
                .addComponent(jLabel4)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 82, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jLabel2)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(cbxCorridors, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jLabel3)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jScrollPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 336, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addGroup(panInputsLayout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(btnSave, javax.swing.GroupLayout.DEFAULT_SIZE, 35, Short.MAX_VALUE)
                    .addComponent(btnReset, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnCancel, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(panInputs, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jmKit, javax.swing.GroupLayout.DEFAULT_SIZE, 924, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(panInputs, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jmKit, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );

        pack();
    }private void cbxCorridorsActionPerformed(java.awt.event.ActionEvent evt) {

    }

    private void btnSaveActionPerformed(java.awt.event.ActionEvent evt) {
        saveOrUpdate();
    }

    private void btnResetActionPerformed(java.awt.event.ActionEvent evt) {
        this.routeCreationHelper.reset();
    }

    private void btnCancelActionPerformed(java.awt.event.ActionEvent evt) {
        dispose();
    }

    // Variables declaration - do not modify
    private javax.swing.JButton btnCancel;
    private javax.swing.JButton btnReset;
    private javax.swing.JButton btnSave;
    private javax.swing.JComboBox cbxCorridors;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private org.jdesktop.swingx.JXMapKit jmKit;
    private javax.swing.JList lbxRoutes;
    private javax.swing.JPanel panInputs;
    private javax.swing.JTextArea tbxDesc;
    private javax.swing.JTextField tbxName;
    // End of variables declaration

}
