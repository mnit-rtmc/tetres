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
public final class SpecialEventDialog extends FilterEditDialog {

    private final String EVENT_SIZE_SMALL = "Small";
    private final String EVENT_SIZE_MEDIUM = "Medium";
    private final String EVENT_SIZE_LARGE = "Large";
    private final String EVENT_SIZE_ANY = "Any";

    private final String EVENT_TIME_BEFORE = "Before";
    private final String EVENT_TIME_DURING_AFTER = "During-After";
    private final String EVENT_TIME_ANY = "Any";

    private final String[] eventSizes;
    private final String[] eventTimes;

    /**
     * Creates new form IncidentEditDialog
     *
     * @param parent
     * @param modal
     */
    public SpecialEventDialog(java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();

        this.cbxEventSize.removeAllItems();
        this.cbxEventSize.addItem(EVENT_SIZE_SMALL);
        this.cbxEventSize.addItem(EVENT_SIZE_MEDIUM);
        this.cbxEventSize.addItem(EVENT_SIZE_LARGE);
        this.cbxEventSize.addItem(EVENT_SIZE_ANY);

        this.cbxEventTime.removeAllItems();
        this.cbxEventTime.addItem(EVENT_TIME_BEFORE);
        this.cbxEventTime.addItem(EVENT_TIME_DURING_AFTER);
        this.cbxEventTime.addItem(EVENT_TIME_ANY);

        this.eventSizes = new String[]{EVENT_SIZE_SMALL, EVENT_SIZE_MEDIUM, EVENT_SIZE_LARGE};
        this.eventTimes = new String[]{EVENT_TIME_BEFORE, EVENT_TIME_DURING_AFTER};

    }

    @Override
    public void reset() {
        this.cbxDistance.setSelectedIndex(0);
        this.cbxEventSize.setSelectedIndex(0);
        this.cbxEventTime.setSelectedIndex(0);
        this.setLocationRelativeTo(this.getParent());
        this.isChanged = false;
    }

    @Override
    public void updateDataTable() {
        String distance = this.cbxDistance.getSelectedItem().toString();
        String event_size = this.cbxEventSize.getSelectedItem().toString();
        String event_time = this.cbxEventTime.getSelectedItem().toString();

        DefaultTableModel model = (DefaultTableModel) this.table.getModel();
        List<String> targetEventSizes = new ArrayList<String>();
        List<String> targetEventTimes = new ArrayList<String>();

        if (EVENT_SIZE_ANY.equals(event_size)) {
            for (String _eventSize : this.eventSizes) {
                targetEventSizes.add(_eventSize);
            }
        } else {
            targetEventSizes.add(event_size);
        }

        if (EVENT_TIME_ANY.equals(event_time)) {
            for (String _eventTime : this.eventTimes) {
                targetEventTimes.add(_eventTime);
            }
        } else {
            targetEventTimes.add(event_time);
        }

        int nAdded = 0;
        for (String _eventSize : targetEventSizes) {
            for (String _eventTime : targetEventTimes) {
                if (this.hasValueInTable(distance, _eventSize, _eventTime)) {
                    continue;
                }
                nAdded += 1;
                model.addRow(new Object[]{distance, _eventSize, _eventTime});
            }
        }

        if (nAdded == 0) {
//            JOptionPane.showMessageDialog(this, "Fail to add");
            return;
        }
        this.isChanged = true;
    }

    private boolean hasValueInTable(String distance, String event_size, String event_time) {
        for (int i = 0; i < this.table.getRowCount(); i++) {
            String _distance = this.table.getValueAt(i, 0).toString().trim();
            String _event_size = this.table.getValueAt(i, 1).toString().trim();
            String _event_time = this.table.getValueAt(i, 2).toString().trim();
            if (_distance.equals(distance) && _event_size.equals(event_size) && _event_time.equals(event_time)) {
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
        cbxDistance = new javax.swing.JComboBox<>();
        jLabel3 = new javax.swing.JLabel();
        cbxEventSize = new javax.swing.JComboBox<>();
        btnOK = new javax.swing.JButton();
        btnClose = new javax.swing.JButton();
        jLabel4 = new javax.swing.JLabel();
        cbxEventTime = new javax.swing.JComboBox<>();
        jScrollPane1 = new javax.swing.JScrollPane();
        jTextArea1 = new javax.swing.JTextArea();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Weather Filter Dialog");

        jLabel2.setText("Distance");

        cbxDistance.setModel(new javax.swing.DefaultComboBoxModel<>(new String[] { "Near", "Middle", "Far" }));

        jLabel3.setText("Event Size");

        cbxEventSize.setModel(new javax.swing.DefaultComboBoxModel<>(new String[] { "Small", "Medium", "Large" }));

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

        jLabel4.setText("Event Time");

        cbxEventTime.setModel(new javax.swing.DefaultComboBoxModel<>(new String[] { "Before", "During-After" }));

        jTextArea1.setEditable(false);
        jTextArea1.setBackground(java.awt.SystemColor.controlHighlight);
        jTextArea1.setColumns(20);
        jTextArea1.setFont(new java.awt.Font("Monospaced", 0, 11)); // NOI18N
        jTextArea1.setRows(5);
        jTextArea1.setText("# Distance\n   - Near : ~3mile\n   - Middle : 3-5mile\n   - Far : 5+mile\n# Event Size : attendance\n   - Small : ~20k\n   - Medium : 20-40k\n   - Large : 40k+");
        jTextArea1.setEnabled(false);
        jScrollPane1.setViewportView(jTextArea1);

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
                .addGap(18, 18, 18)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(btnOK, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(cbxDistance, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(cbxEventSize, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(cbxEventTime, 0, 187, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 307, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(cbxDistance, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(jLabel2))
                        .addGap(18, 18, 18)
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel3)
                            .addComponent(cbxEventSize, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(18, 18, 18)
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(cbxEventTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(jPanel1Layout.createSequentialGroup()
                                .addGap(3, 3, 3)
                                .addComponent(jLabel4)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(btnClose)
                            .addComponent(btnOK)))
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 150, Short.MAX_VALUE))
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
    private javax.swing.JComboBox<String> cbxDistance;
    private javax.swing.JComboBox<String> cbxEventSize;
    private javax.swing.JComboBox<String> cbxEventTime;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JTextArea jTextArea1;
    // End of variables declaration//GEN-END:variables

}
