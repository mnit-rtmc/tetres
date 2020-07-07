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
package user.filters;

import java.util.ArrayList;
import java.util.List;
import javax.swing.table.DefaultTableModel;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public final class WorkzoneEditDialog extends FilterEditDialog {

//    private final String LANE_CONFIG_ANY = "Any";

//    private final String CLOSED_LENGTH_SHORT = "Short";
//    private final String CLOSED_LENGTH_MEDIUM = "Medium";
//    private final String CLOSED_LENGTH_LONG = "Long";

//    private final String CLOSED_LENGTH_ANY = "Any";

    private final String LENGTH_SHORT = "Short";
    private final String LENGTH_MEDIUM = "Medium";
    private final String LENGTH_LONG = "Long";
    private final String LENGTH_ANY = "Any";

    private final String LOCATION_UPSTREAM = "Upstream";
    private final String LOCATION_OVERLAPPED = "Overlapped";
    private final String LOCATION_DOWNSTREAM = "Downstream";
    private final String LOCATION_ANY = "Any";

    private final String IMPACT_LOW = "Low";
    private final String IMPACT_MEDIUM = "Medium";
    private final String IMPACT_HIGH = "High";
    private final String IMPACT_ANY = "Any";

//    private final String[] closedLengths;
    private final String[] lengths;
    private final String[] locations;
    private final String[] impacts;

//    private final String[] laneConfigs;

    /**
     * Creates new form WorkzoneEditDialog
     *
     * @param parent
     * @param modal
     */
    public WorkzoneEditDialog(java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();

//        for (int from_lane = 2; from_lane <= 5; from_lane++) {
//            int max_to = from_lane - 1;
//            for (int to_lane = 1; to_lane <= max_to; to_lane++) {
//                this.cbxLaneConfig.addItem(String.format("%d to %d", from_lane, to_lane));
//            }
//        }
//        this.laneConfigs = new String[this.cbxLaneConfig.getItemCount()];
//        for(int i=0; i<this.laneConfigs.length; i++) {
//            this.laneConfigs[i] = this.cbxLaneConfig.getItemAt(i);
//        }
//        this.cbxLaneConfig.addItem(LANE_CONFIG_ANY);


//        this.closedLengths = new String[]{CLOSED_LENGTH_SHORT, CLOSED_LENGTH_MEDIUM, CLOSED_LENGTH_LONG };
//        this.cbxLaneClosedLength.removeAllItems();
//        this.cbxLaneClosedLength.addItem(CLOSED_LENGTH_SHORT);
//        this.cbxLaneClosedLength.addItem(CLOSED_LENGTH_MEDIUM);
//        this.cbxLaneClosedLength.addItem(CLOSED_LENGTH_LONG);
//        this.cbxLaneClosedLength.addItem(CLOSED_LENGTH_ANY);

        this.lengths = new String[]{LENGTH_SHORT, LENGTH_MEDIUM, LENGTH_LONG };
        this.cbxWorkZoneLength.removeAllItems();
        this.cbxWorkZoneLength.addItem(LENGTH_SHORT);
        this.cbxWorkZoneLength.addItem(LENGTH_MEDIUM);
        this.cbxWorkZoneLength.addItem(LENGTH_LONG);
        this.cbxWorkZoneLength.addItem(LENGTH_ANY);

        this.locations = new String[]{LOCATION_UPSTREAM, LOCATION_OVERLAPPED, LOCATION_DOWNSTREAM };
        this.cbxRelLocation.removeAllItems();
        this.cbxRelLocation.addItem(LOCATION_UPSTREAM);
        this.cbxRelLocation.addItem(LOCATION_OVERLAPPED);
        this.cbxRelLocation.addItem(LOCATION_DOWNSTREAM);
        this.cbxRelLocation.addItem(LOCATION_ANY);
//        cbxRelLocation1 is impact
        this.impacts = new String[]{IMPACT_LOW, IMPACT_MEDIUM, IMPACT_HIGH };
        this.cbxImpact.removeAllItems();
        this.cbxImpact.addItem(IMPACT_LOW);
        this.cbxImpact.addItem(IMPACT_MEDIUM);
        this.cbxImpact.addItem(IMPACT_HIGH);
        this.cbxImpact.addItem(IMPACT_ANY);

    }


    @Override
    public void reset() {
//        this.cbxLaneConfig.setSelectedIndex(0);
//        this.cbxLaneClosedLength.setSelectedIndex(0);
        this.cbxWorkZoneLength.setSelectedIndex(0);
        this.cbxRelLocation.setSelectedIndex(0);
        this.cbxImpact.setSelectedIndex(0);
        this.setLocationRelativeTo(this.getParent());
        this.isChanged = false;
    }

    @Override
    public void updateDataTable() {
//        String lane_config = this.cbxLaneConfig.getSelectedItem().toString();
//        String closed_length = this.cbxLaneClosedLength.getSelectedItem().toString();

        String length = this.cbxWorkZoneLength.getSelectedItem().toString();
        String rel_location = this.cbxRelLocation.getSelectedItem().toString();
        String impact = this.cbxImpact.getSelectedItem().toString();

        DefaultTableModel model = (DefaultTableModel) this.table.getModel();

//        List<String> targetLaneConfigs = new ArrayList<String>();
        List<String> targetLengths = new ArrayList<String>();
        List<String> targetLocations = new ArrayList<String>();
        List<String> targetImpacts = new ArrayList<String>();

//        if(LANE_CONFIG_ANY.equals(lane_config)) {
//            for(String _laneConfig : this.laneConfigs) {
//                targetLaneConfigs.add(_laneConfig);
//            }
//        } else {
//            targetLaneConfigs.add(lane_config);
//        }
//        targetLaneConfigs.add(LANE_CONFIG_ANY);

//        if(CLOSED_LENGTH_ANY.equals(closed_length)) {
//            for(String _length : this.closedLengths) {
//                targetLengths.add(_length);
//            }
//        } else {
//            targetLengths.add(closed_length);
//        }
//        targetLengths.add(CLOSED_LENGTH_ANY);
//        if(LOCATION_ANY.equals(rel_location)) {
//            for(String _loc : this.locations) {
//                targetLocations.add(_loc);
//            }
//        } else {
//            targetLocations.add(rel_location);
//        }
        targetLengths.add(length);
        targetLocations.add(rel_location);

//        if(IMPACT_ANY.equals(impact)) {
//            for(String _impact : this.impacts) {
//                targetImpacts.add(_impact);
//            }
//        } else {
//            targetImpacts.add(impact);
//        }
        targetImpacts.add(impact);

        int nAdded = 0;
        for(String _length : targetLengths) {
            for(String _location: targetLocations){
                for(String _impact: targetImpacts){
                    if(this.hasValueInTable(_length, _location, _impact)) {
                        continue;
                    }
                    nAdded += 1;
                    model.addRow(new Object[]{_length, _location, _impact});
                }
            }
        }


        if(nAdded == 0) {
//            JOptionPane.showMessageDialog(this, "Fail to add");
            return;
        }

        this.isChanged = true;
    }

    private boolean hasValueInTable(String length, String rel_location, String impact) {
        for (int i = 0; i < this.table.getRowCount(); i++) {
            String _length = this.table.getValueAt(i, 0).toString().trim();
            String _rel_location = this.table.getValueAt(i, 1).toString().trim();
            String _impact = this.table.getValueAt(i, 2).toString().trim();
            if (_length.equals(length) && _rel_location.equals(rel_location) && _impact.equals(impact)) {
                return true;
            }
        }
        return false;
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
        btnOK = new javax.swing.JButton();
        btnClose = new javax.swing.JButton();
        jLabel4 = new javax.swing.JLabel();
        cbxRelLocation = new javax.swing.JComboBox<String>();
        cbxImpact = new javax.swing.JComboBox<String>();
        jLabel5 = new javax.swing.JLabel();
        jLabel6 = new javax.swing.JLabel();
        cbxWorkZoneLength = new javax.swing.JComboBox<String>();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Weather Filter Dialog");

        btnOK.setText("Ok");
        btnOK.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnOKActionPerformed(evt);
            }
        });

        btnClose.setText("Close");
        btnClose.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCloseActionPerformed(evt);
            }
        });

        jLabel4.setText("Relative Location");

        cbxRelLocation.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Upstream", "Overlapped", "Downstream" }));

        cbxImpact.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Upstream", "Overlapped", "Downstream" }));

        jLabel5.setText("Impact");

        jLabel6.setText("Workzone Length");

        cbxWorkZoneLength.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Upstream", "Overlapped", "Downstream" }));

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(btnClose)
                            .addComponent(jLabel4)
                            .addComponent(jLabel5))
                        .addGap(19, 19, 19)
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(cbxImpact, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(btnOK, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(cbxRelLocation, 0, 263, Short.MAX_VALUE)))
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(jLabel6)
                        .addGap(18, 18, 18)
                        .addComponent(cbxWorkZoneLength, 0, 261, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addGap(47, 47, 47)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel6)
                    .addComponent(cbxWorkZoneLength, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(24, 24, 24)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(cbxRelLocation, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel4))
                .addGap(18, 18, 18)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(cbxImpact, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel5))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 94, Short.MAX_VALUE)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnOK)
                    .addComponent(btnClose))
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

    private void btnOKActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnOKActionPerformed
        this.updateDataTable();
    }//GEN-LAST:event_btnOKActionPerformed

    private void btnCloseActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnCloseActionPerformed
        this.reset();
        this.setVisible(false);
    }//GEN-LAST:event_btnCloseActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnClose;
    private javax.swing.JButton btnOK;
    private javax.swing.JComboBox<String> cbxImpact;
    private javax.swing.JComboBox<String> cbxRelLocation;
    private javax.swing.JComboBox<String> cbxWorkZoneLength;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JPanel jPanel1;
    // End of variables declaration//GEN-END:variables

}
