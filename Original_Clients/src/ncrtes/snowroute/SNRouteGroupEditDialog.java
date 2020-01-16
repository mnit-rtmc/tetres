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

import common.infra.Infra;
import common.infra.RNode;
import common.pyticas.HttpResult;
import common.route.Route;
import ncrtes.NCRTESConfig;
import ncrtes.RegionConfig;
import ncrtes.api.SnowRouteGroupClient;
import ncrtes.types.AbstractDataChangeListener;
import ncrtes.types.SnowRouteGroupInfo;
import common.util.FormHelper;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SNRouteGroupEditDialog extends javax.swing.JDialog {

    public Route route;
    private SnowRouteGroupInfo snrgi;
    private SnowRouteGroupClient api;
    private boolean isCopied = false;

    /**
     * Creates new form RouteCreateDialog
     */
    public SNRouteGroupEditDialog(java.awt.Frame parent, SnowRouteGroupInfo snrgi, boolean modal) {
        super(parent, modal);
        initComponents();        
        this.snrgi = snrgi;
        this.init();        
    }
    
    // initialize UI and variables
    private void init() {
        
        FormHelper.setIntegerFilter(this.tbxYear.getDocument(), false);
        
        for(String region : RegionConfig.getRegions())
            this.cbxRegion.addItem(region);
        
        for(String station : RegionConfig.getTruckStations())
            this.cbxTruckStation.addItem(station);        
        
        if(this.snrgi != null) {
            this.tbxName.setText(this.snrgi.name);
            this.cbxRegion.setSelectedItem(this.snrgi.region);
            this.cbxTruckStation.setSelectedItem(this.snrgi.sub_region);
            this.tbxDesc.setText(this.snrgi.description);
            this.tbxYear.setText(this.snrgi.year.toString());
        }
        this.api = new SnowRouteGroupClient();
        this.api.addChangeListener(new AbstractDataChangeListener<SnowRouteGroupInfo>() {  
            @Override
            public void copyFailed(HttpResult result, SnowRouteGroupInfo obj) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to copy snow route group data");
            }

            @Override
            public void copySuccess(int id) {
                System.out.println("Copy Success");
                dispose();
            }            
            
            @Override
            public void insertFailed(HttpResult result, SnowRouteGroupInfo obj) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to add snow route group data");
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
            public void updateFailed(HttpResult result, SnowRouteGroupInfo obj) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to update snow route group data");
            }
        });
    }
    
    public void setCopied(SnowRouteGroupInfo snrgi) {
        this.snrgi = snrgi;
        this.isCopied = true;
        this.tbxName.setText(this.snrgi.name);
        this.cbxRegion.setSelectedItem(this.snrgi.region);
        this.cbxTruckStation.setSelectedItem(this.snrgi.sub_region);
        this.tbxDesc.setText(this.snrgi.description);
        this.tbxYear.setText(this.snrgi.year.toString());
    }    
    
    /**
     * save or update snow route group information
     */
    private void saveOrUpdate() {
        String name = this.tbxName.getText();
        String desc = this.tbxDesc.getText();
        String region = this.cbxRegion.getSelectedItem().toString();
        String year = this.tbxYear.getText();        
        String sub_region = this.cbxTruckStation.getSelectedItem().toString();
        
        if(name.isEmpty()) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Name is required");
            return;
        }
        if(year.isEmpty()) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Year is required");
            return;
        }
        SnowRouteGroupInfo mSnrgi = new SnowRouteGroupInfo();
        mSnrgi.name = name;
        mSnrgi.description = desc;
        mSnrgi.sub_region = sub_region;
        mSnrgi.region = region;        
        mSnrgi.year = Integer.parseInt(year);
        
        if(this.snrgi != null) {
            if(this.isCopied) {
                this.api.copy(this.snrgi, mSnrgi);
            } else {
                this.api.update(this.snrgi, mSnrgi);
            }
        } else {
            this.api.insert(mSnrgi);
        }
    }
    
    /**
     * returns snow route group info entered in UI
     * 
     * @return snow route group info
     */
    public SnowRouteGroupInfo getSnowRouteGroupInfo() {
        return this.snrgi;
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">
    private void initComponents() {

        jPanel1 = new javax.swing.JPanel();
        btnSave = new javax.swing.JButton();
        btnCancel = new javax.swing.JButton();
        jLabel4 = new javax.swing.JLabel();
        tbxName = new javax.swing.JTextField();
        jLabel5 = new javax.swing.JLabel();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxDesc = new javax.swing.JTextArea();
        jLabel7 = new javax.swing.JLabel();
        cbxRegion = new javax.swing.JComboBox<>();
        jLabel8 = new javax.swing.JLabel();
        cbxTruckStation = new javax.swing.JComboBox<>();
        jLabel1 = new javax.swing.JLabel();
        tbxYear = new javax.swing.JTextField();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Snow Management Route Editor");

        btnSave.setText("Save");
        btnSave.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSaveActionPerformed(evt);
            }
        });

        btnCancel.setText("Cancel");
        btnCancel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCancelActionPerformed(evt);
            }
        });

        jLabel4.setText("Truck Route ID");

        jLabel5.setText("Memo");

        tbxDesc.setColumns(20);
        tbxDesc.setLineWrap(true);
        tbxDesc.setRows(5);
        tbxDesc.setWrapStyleWord(true);
        jScrollPane1.setViewportView(tbxDesc);

        jLabel7.setText("Region");

        jLabel8.setText("Sub-Region");

        jLabel1.setText("Year (e.g. enter 2017 for 2017 ~ 2018 winter)");

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1)
                    .addComponent(tbxName)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(btnCancel, javax.swing.GroupLayout.PREFERRED_SIZE, 120, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(btnSave, javax.swing.GroupLayout.DEFAULT_SIZE, 204, Short.MAX_VALUE))
                    .addComponent(cbxRegion, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(cbxTruckStation, javax.swing.GroupLayout.Alignment.TRAILING, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel1)
                            .addComponent(jLabel4)
                            .addComponent(jLabel5)
                            .addComponent(jLabel7)
                            .addComponent(jLabel8))
                        .addGap(0, 0, Short.MAX_VALUE))
                    .addComponent(tbxYear))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel4)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(tbxName, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jLabel7)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(cbxRegion, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jLabel8)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(cbxTruckStation, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jLabel1)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(tbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jLabel5)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 103, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(btnCancel, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnSave, javax.swing.GroupLayout.DEFAULT_SIZE, 35, Short.MAX_VALUE))
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
    }private void btnSaveActionPerformed(java.awt.event.ActionEvent evt) {
        saveOrUpdate();
    }

    private void btnCancelActionPerformed(java.awt.event.ActionEvent evt) {
        dispose();
    }

    // Variables declaration - do not modify
    private javax.swing.JButton btnCancel;
    private javax.swing.JButton btnSave;
    private javax.swing.JComboBox<String> cbxRegion;
    private javax.swing.JComboBox<String> cbxTruckStation;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JTextArea tbxDesc;
    private javax.swing.JTextField tbxName;
    private javax.swing.JTextField tbxYear;
    // End of variables declaration

}
