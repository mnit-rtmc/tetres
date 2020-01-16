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
package ncrtes.targetstation;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import common.infra.Detector;
import common.infra.Infra;
import common.infra.RNode;
import common.pyticas.HttpResult;
import ncrtes.NCRTESConfig;
import ncrtes.api.TargetStationClient;
import ncrtes.types.AbstractDataChangeListener;
import ncrtes.types.TargetStationInfo;
import common.pyticas.PostData;
import common.pyticas.responses.ResponseInteger;
import javax.swing.JOptionPane;
import javax.swing.WindowConstants;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TargetStationEditDialog extends javax.swing.JDialog {

    private TargetStationInfo tsi;
    private TargetStationClient api;
    private Integer year;
    private boolean isUpdated = false;

    /**
     * Creates new form RouteCreateDialog
     * @param parent
     * @param target_station
     * @param modal
     */
    public TargetStationEditDialog(java.awt.Frame parent, Integer year, TargetStationInfo target_station, boolean modal) {
        super(parent, modal);
//        this.setLocationRelativeTo(null);
        initComponents();        
        this.tsi = target_station;
        this.year = year;
        this.init();        
    }
    
    // initialize UI and variables
    private void init() {
        
        this.tbxStationID.setText(this.tsi.station_id);
        this.tbxTruckRouteID.setText(this.tsi.snowroute_name);
        this.tbxDetectors.setText(this.tsi.detectors);
        
        Infra infra = Infra.getInstance();
        RNode station = infra.getRNode(this.tsi.station_id);
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("StationID : %s\n", station.station_id));
        sb.append(String.format("Speed Limit : %d\n", station.s_limit));
        sb.append(String.format("Label : %s\n", station.label));
        sb.append(String.format("Lanes : %d\n", station.lanes));        
        sb.append(String.format("Lat : %s\n", station.lat));
        sb.append(String.format("Lon : %s\n", station.lon));
        sb.append("Detectors : \n");
        for(String det_name : station.detectors)
        {
            Detector det = infra.getDetector(det_name);
            sb.append(String.format("  - Lane %d : %s (", det.lane, det.name));
            if(!det.category.isEmpty()) 
                sb.append(String.format("category=%s, ", det.category));
            if(det.abandoned) 
                sb.append("abandoned, ");
            sb.append(String.format("fieldlength=%.1f)\n", det.field));
        }
        this.tbxInfo.setText(sb.toString());
        
        this.api = new TargetStationClient();
        
        this.api.addChangeListener(new AbstractDataChangeListener<TargetStationInfo>() {  
           
            @Override
            public void updateSuccess(int id) {
                isUpdated = true;
                dispose();
            }            

            @Override
            public void updateFailed(HttpResult result, TargetStationInfo obj) {
                if(result.isSuccess()) {
                    Gson gsonBuilder = new GsonBuilder().create();
                    ResponseInteger response = gsonBuilder.fromJson(result.contents, ResponseInteger.class);            
                    JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, response.message);
                } else {
                    JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to update");
                }
                dispose();
            }
        });
   
    }
    
    /**
     * save or update snow route group information
     */
    private void saveOrUpdate() {
        String detectors = this.tbxDetectors.getText();
        
        if(detectors.isEmpty()) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Detectors required");
            return;
        }
        
        TargetStationInfo mTSI = this.tsi.clone();        
        mTSI.detectors = detectors;        
        if(tsi.detectors.equals(detectors)) {
            return;
        }
        
        PostData extData = new PostData();
        extData.addData("id", this.tsi.id);
        extData.addData("station_id", this.tsi.station_id);
        extData.addData("year", this.year);
        extData.addData("detectors", detectors);    
        if(this.tsi.normal_function_id != null && !this.tsi.normal_function_id.isEmpty()) {
            int res = JOptionPane.showConfirmDialog(NCRTESConfig.mainFrame, "This station has normal U-K function.\nIf detector information is changed, normal U-K function will be calibrated again.\nAnd it will take some time.\nAre you going to proceed?");
            if(res != JOptionPane.YES_OPTION) {
                return;
            }
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Please wait until this dialog is closed automatically");
            this.btnCancel.setEnabled(false);
            this.btnSave.setEnabled(false);
            this.setDefaultCloseOperation(WindowConstants.DO_NOTHING_ON_CLOSE);            
        }
        this.api.updateWithExtra(this.tsi, mTSI, extData);
        this.tsi = mTSI;
    }
    
    /**
     * returns target station info entered in UI
     * 
     * @return target station info
     */
    public TargetStationInfo getTargetStationInfo() {
        return this.tsi;
    }
    
    public boolean isUpdated() {
        return this.isUpdated;
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
        tbxTruckRouteID = new javax.swing.JTextField();
        jLabel7 = new javax.swing.JLabel();
        jLabel1 = new javax.swing.JLabel();
        tbxDetectors = new javax.swing.JTextField();
        tbxStationID = new javax.swing.JTextField();
        jPanel2 = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxInfo = new javax.swing.JTextArea();

        setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Target Lane Editor");

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

        jLabel4.setText("Truck Route Name");

        tbxTruckRouteID.setEnabled(false);

        jLabel7.setText("Station ID");

        jLabel1.setText("Target Detectors");

        tbxStationID.setEditable(false);

        jPanel2.setBorder(javax.swing.BorderFactory.createTitledBorder("Station Information"));

        tbxInfo.setEditable(false);
        tbxInfo.setColumns(20);
        tbxInfo.setRows(5);
        jScrollPane1.setViewportView(tbxInfo);

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 483, Short.MAX_VALUE)
                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jScrollPane1)
                .addContainerGap())
        );

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(btnCancel, javax.swing.GroupLayout.PREFERRED_SIZE, 110, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(btnSave, javax.swing.GroupLayout.DEFAULT_SIZE, 84, Short.MAX_VALUE))
                    .addComponent(tbxDetectors)
                    .addComponent(tbxTruckRouteID)
                    .addComponent(jLabel7)
                    .addComponent(jLabel4)
                    .addComponent(jLabel1)
                    .addComponent(tbxStationID))
                .addGap(18, 18, 18)
                .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(jLabel7)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(tbxStationID, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jLabel4)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(tbxTruckRouteID, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(27, 27, 27)
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(tbxDetectors, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 85, Short.MAX_VALUE)
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addComponent(btnCancel, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(btnSave, javax.swing.GroupLayout.PREFERRED_SIZE, 35, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
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
            .addComponent(jPanel1, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
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
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JTextField tbxDetectors;
    private javax.swing.JTextArea tbxInfo;
    private javax.swing.JTextField tbxStationID;
    private javax.swing.JTextField tbxTruckRouteID;
    // End of variables declaration

}
