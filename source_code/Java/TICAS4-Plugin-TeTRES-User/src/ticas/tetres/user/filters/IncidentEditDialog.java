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
package ticas.tetres.user.filters;

import ticas.tetres.user.TeTRESConfig;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public final class IncidentEditDialog extends FilterEditDialog {

    private final String IMPACT_ROAD_CLOSED = "Road Closed";
    private final String IMPACT_2PLUS_LANE_CLOSED = "2+ Lane Closed";
    private final String IMPACT_1LANE_CLOSED = "1 Lane Closed";
    private final String IMPACT_NOT_BLOCKING = "Not Blocking";
    private final String IMPACT_ONLY_ON_SHOULDER ="Only on Shoulder";
    private final String IMPACT_ANY ="Any";    
    private final String SEVERITY_FATAL= "Fatal";
    private final String SEVERITY_SERIOUS_INSURY = "Serious Injury";
    private final String SEVERITY_PERSONAL_INSURY = "Personal Injury";
    private final String SEVERITY_PROPERTY_DEMAGE = "Property Damage";
    private final String SEVERITY_ANY = "Any";
    private final String[] impacts;
    private final String[] severities;
    
    /**
     * Creates new form IncidentEditDialog
     *
     * @param parent
     * @param modal
     */
    public IncidentEditDialog(java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();
                
        this.cbxImpact.removeAllItems();
        this.cbxImpact.addItem(IMPACT_ROAD_CLOSED);
        this.cbxImpact.addItem(IMPACT_2PLUS_LANE_CLOSED);
        this.cbxImpact.addItem(IMPACT_1LANE_CLOSED);
        this.cbxImpact.addItem(IMPACT_NOT_BLOCKING);        
        this.cbxImpact.addItem(IMPACT_ONLY_ON_SHOULDER);        
        this.cbxImpact.addItem(IMPACT_ANY);        
        
        this.cbxSeverity.removeAllItems();
        this.cbxSeverity.addItem(SEVERITY_FATAL);
        this.cbxSeverity.addItem(SEVERITY_SERIOUS_INSURY);
        this.cbxSeverity.addItem(SEVERITY_PERSONAL_INSURY);
        this.cbxSeverity.addItem(SEVERITY_PROPERTY_DEMAGE);        
        this.cbxSeverity.addItem(SEVERITY_ANY);           
        
        this.impacts = new String[]{IMPACT_ROAD_CLOSED, IMPACT_2PLUS_LANE_CLOSED, IMPACT_1LANE_CLOSED, IMPACT_NOT_BLOCKING, IMPACT_ONLY_ON_SHOULDER};
        this.severities = new String[]{SEVERITY_FATAL, SEVERITY_SERIOUS_INSURY, SEVERITY_PERSONAL_INSURY, SEVERITY_PROPERTY_DEMAGE};
    }

    @Override
    public void reset() {
        this.cbxType.setSelectedIndex(0);
        this.cbxImpact.setSelectedIndex(0);
        this.cbxSeverity.setEnabled(false);
        this.setLocationRelativeTo(this.getParent());
        this.isChanged = false;
    }

    @Override
    public void updateDataTable() {
        String type = this.cbxType.getSelectedItem().toString();
        String impact = this.cbxImpact.getSelectedItem().toString();
        String severity = this.cbxSeverity.getSelectedItem().toString();        
        if (!this.shouldEnableSeverity()) {
            severity = "";
        }
                
        DefaultTableModel model = (DefaultTableModel) this.table.getModel();
        List<String> targetImpacts = new ArrayList<String>();
        List<String> targetSeverities = new ArrayList<String>();
        
        if(IMPACT_ANY.equals(impact)) {           
            for(String _impact : this.impacts) {
                targetImpacts.add(_impact);
            }
        } else {
            targetImpacts.add(impact);
        }
        
        if(SEVERITY_ANY.equals(severity)) {
            for(String _severity : this.severities) {
                targetSeverities.add(_severity);
            }
        } else {
            targetSeverities.add(severity);
        }
        
        int nAdded = 0;
        for(String _impact : targetImpacts) {
            for(String _severity : targetSeverities) {
                if(this.hasValueInTable(type, _impact, _severity)) {
                    continue;
                }
                nAdded += 1;
                model.addRow(new Object[]{type, _impact, _severity});
            }
        }
       
        if(nAdded == 0) {
//            JOptionPane.showMessageDialog(this, "Fail to add");
            return;
        }
        this.isChanged = true;
    }
     
    private boolean shouldEnableSeverity() {
        return this.cbxType.getSelectedIndex() == 3;
    }

    private boolean hasValueInTable(String type, String impact, String severity) {
        for (int i = 0; i < this.table.getRowCount(); i++) {
            String _type = this.table.getValueAt(i, 0).toString().trim();
            String _impact = this.table.getValueAt(i, 1).toString().trim();
            String _severity = this.table.getValueAt(i, 2).toString().trim();
            if(_type.equals(type) && _impact.equals(impact) && _severity.equals(severity)) {
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
        jLabel2 = new javax.swing.JLabel();
        cbxType = new javax.swing.JComboBox<>();
        jLabel3 = new javax.swing.JLabel();
        cbxImpact = new javax.swing.JComboBox<>();
        btnOK = new javax.swing.JButton();
        btnClose = new javax.swing.JButton();
        jLabel4 = new javax.swing.JLabel();
        cbxSeverity = new javax.swing.JComboBox<>();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Weather Filter Dialog");

        jLabel2.setText("Type");

        cbxType.setModel(new javax.swing.DefaultComboBoxModel<>(new String[] { "Hazard", "Roadwork", "Stall", "Crash" }));
        cbxType.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                cbxTypeActionPerformed(evt);
            }
        });

        jLabel3.setText("Intensity");

        cbxImpact.setModel(new javax.swing.DefaultComboBoxModel<>(new String[] { "Road Closed", "2+ Lane Closed", "1 Lane Closed", "Not Blocking", "Only on Shoulder" }));

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

        jLabel4.setText("Severity");

        cbxSeverity.setModel(new javax.swing.DefaultComboBoxModel<>(new String[] { "Fatal", "Serious Injury", "Personal Injury", "Property Damage" }));

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel3)
                    .addComponent(jLabel2)
                    .addComponent(btnClose)
                    .addComponent(jLabel4))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(btnOK, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(cbxType, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(cbxImpact, 0, 295, Short.MAX_VALUE)
                    .addComponent(cbxSeverity, 0, 295, Short.MAX_VALUE))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel2)
                    .addComponent(cbxType, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel3)
                    .addComponent(cbxImpact, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(cbxSeverity, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel4))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 19, Short.MAX_VALUE)
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

    private void cbxTypeActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_cbxTypeActionPerformed
        this.cbxSeverity.setEnabled(this.shouldEnableSeverity());
    }//GEN-LAST:event_cbxTypeActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnClose;
    private javax.swing.JButton btnOK;
    private javax.swing.JComboBox<String> cbxImpact;
    private javax.swing.JComboBox<String> cbxSeverity;
    private javax.swing.JComboBox<String> cbxType;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JPanel jPanel1;
    // End of variables declaration//GEN-END:variables


}
