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
package ticas.ncrtes.estimation;

import ticas.common.log.TICASLogger;
import ticas.ncrtes.NCRTESConfig;
import ticas.ncrtes.api.ListResponse;
import ticas.ncrtes.api.SnowRouteClient;
import ticas.ncrtes.api.SnowRouteGroupClient;
import ticas.ncrtes.types.AbstractDataChangeListener;
import ticas.ncrtes.types.SnowRouteGroupInfo;
import ticas.ncrtes.types.SnowRouteInfo;
import ticas.common.pyticas.HttpResult;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import javax.swing.DefaultListModel;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;
import org.apache.logging.log4j.core.Logger;

/**
 *
 * @author chong
 */
public final class SelectTargetTruckRouteDialog extends javax.swing.JDialog {

    DefaultListModel model;
    private SnowRouteGroupClient snrgApi;
    private Logger logger;
    private Integer selectedYear;
    private List<SnowRouteGroupInfo> snrGroupList = new ArrayList<>();
    private SnowRouteGroupInfo currentSNRGroupInfo;
    public ArrayList<SnowRouteGroupInfo> selectedSnowRouteGroupInfos;
    public ArrayList<SnowRouteInfo> selectedSnowRouteInfos;

    /**
     * Creates new form SelectCorridorDialog
     *
     * @param parent
     * @param modal
     */
    public SelectTargetTruckRouteDialog(java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();
        this.init();
    }

    public void init() {

        this.model = new DefaultListModel();
        this.snrgApi = new SnowRouteGroupClient();
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.selectedSnowRouteGroupInfos = new ArrayList<SnowRouteGroupInfo>();
        this.selectedSnowRouteInfos = new ArrayList<SnowRouteInfo>();

        // when year filter is changed
        this.cbxYear.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                selectedYear = getSelectedYear();
                loadListByYear();
            }
        });
        
        // add snow management route group data change listener
        this.snrgApi.addChangeListener(new AbstractDataChangeListener<SnowRouteGroupInfo>() {

            @Override
            public void yearsFailed(HttpResult httpResult) {
                logger.error(httpResult.res_code + " / " + httpResult.res_msg);
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "fail to load year information for snow management route group");
            }

            @Override
            public void yearsSuccess(List<Integer> obj) {
                Integer sYear = selectedYear;
                cbxYear.removeAllItems();
                Collections.sort(obj ,Collections.reverseOrder());
                cbxYear.addItem("Select Year");
                for (Integer i : obj) {
                    cbxYear.addItem(i);
                }
                resetSnowRouteGroupInfo();
                setYear(sYear);
                loadListByYear();
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to get list of snow management route group");
            }

            @Override
            public void listSuccess(List<SnowRouteGroupInfo> list) {
                snrGroupList = list;
                setSNRGroupTable();
            }
        });

        this.snrgApi.years();
    }

    /**
     * *
     * reset data
     */
    protected void resetSnowRouteGroupInfo() {
        this.snrGroupList.clear();
        setSNRGroupTable();
    }

    /**
     * *
     * set snow management route group list table
     */
    protected void setSNRGroupTable() {
        final DefaultTableModel tm = (DefaultTableModel) this.tblSNRGroupList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SnowRouteGroupInfo s : this.snrGroupList) {
            tm.addRow(new Object[]{s, s.region, s.sub_region, s.description});
        }
        setSnowRouteGroupInfo(currentSNRGroupInfo);
    }

    /**
     * set selected snow management route group
     *
     */
    protected void setSnowRouteGroupInfo(SnowRouteGroupInfo snrgi) {
        if (snrgi == null) {
            return;
        }
        Integer sltIndex = null;
        for (int row = 0; row < this.snrGroupList.size(); row++) {
            SnowRouteGroupInfo s = this.snrGroupList.get(row);
            if (Objects.equals(s.id, snrgi.id)) {
                sltIndex = row;
                break;
            }
        }
        if (sltIndex != null) {
            this.tblSNRGroupList.setRowSelectionInterval(sltIndex, sltIndex);
        }
    }

    /**
     * *
     * load list by selected year
     */
    protected void loadListByYear() {
        Integer sYear = getSelectedYear();
        if (sYear == null) {
            resetSnowRouteGroupInfo();
        } else if (sYear == 0) {
            this.snrgApi.list();
        } else if (sYear == -1) {
            this.snrgApi.listByYear(null);
        } else if (sYear > 2) {
            this.snrgApi.listByYear(sYear);
        }
    }

    /**
     * *
     * set combo box according to the given year
     *
     * @param sYear year
     */
    protected void setYear(Integer sYear) {
        int nYears = this.cbxYear.getItemCount();
        if (nYears <= 1) {
            return;
        }
        if (sYear == null) {
            this.cbxYear.setSelectedIndex(0);
        } else if (sYear == 0) {
            this.cbxYear.setSelectedIndex(1);
        } else {
            for (int sidx = 2; sidx < nYears; sidx++) {
                Integer y = Integer.parseInt(this.cbxYear.getItemAt(sidx).toString());
                if (Objects.equals(y, sYear)) {
                    this.cbxYear.setSelectedIndex(sidx);
                    break;
                }
            }
        }
    }

    /**
     *
     * @return selected year of combo box
     */
    protected Integer getSelectedYear() {
        Integer sYear = null;
        int slt = this.cbxYear.getSelectedIndex();
        if (slt >= 1) {
            int year = Integer.parseInt(this.cbxYear.getSelectedItem().toString());
            sYear = year;
        } else {
            sYear = null;
        }
        return sYear;
    }

    private void useSelectedItems() {
        final DefaultTableModel tm = (DefaultTableModel) this.tblSNRGroupList.getModel();
        SnowRouteClient snrApi = new SnowRouteClient();        
        this.selectedSnowRouteGroupInfos.clear();
        this.selectedSnowRouteInfos.clear();
        for(int slt : this.tblSNRGroupList.getSelectedRows()) {
            SnowRouteGroupInfo snrgi = (SnowRouteGroupInfo)tm.getValueAt(slt, 0);
            this.selectedSnowRouteGroupInfos.add(snrgi);
            ListResponse<SnowRouteInfo> res = snrApi.listSynced(snrgi.id);
            for(SnowRouteInfo snri : res.obj.list) {
                this.selectedSnowRouteInfos.add(snri);
            }
        }
        this.dispose();
    }

    private void cancel() {
        this.dispose();
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jLabel3 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        btnOK = new javax.swing.JButton();
        btnCancel = new javax.swing.JButton();
        cbxYear = new javax.swing.JComboBox();
        jLabel8 = new javax.swing.JLabel();
        jScrollPane3 = new javax.swing.JScrollPane();
        tblSNRGroupList = new javax.swing.JTable();
        jLabel7 = new javax.swing.JLabel();
        jLabel6 = new javax.swing.JLabel();
        jLabel5 = new javax.swing.JLabel();
        jLabel4 = new javax.swing.JLabel();
        jLabel1 = new javax.swing.JLabel();

        jLabel3.setText("Year");

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Target Truck Route Select Dialog");

        jLabel2.setText("Truck Routes");

        btnOK.setText("Use the Selected Corridors");
        btnOK.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnOKActionPerformed(evt);
            }
        });

        btnCancel.setText("Cancel");
        btnCancel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCancelActionPerformed(evt);
            }
        });

        jLabel8.setText("Year");

        tblSNRGroupList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "RouteID", "Region", "SubRegion", "Memo"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.String.class
            };
            boolean[] canEdit = new boolean [] {
                false, false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        tblSNRGroupList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane3.setViewportView(tblSNRGroupList);

        jLabel7.setText("      then click last file while pressing 'Shift' key");

        jLabel6.setText("   : click first item,");

        jLabel5.setText("* Selection sequenced items");

        jLabel4.setText("   : click items while helding down 'Ctrl' key");

        jLabel1.setText("* Selecting individual items");

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(layout.createSequentialGroup()
                        .addGap(0, 0, Short.MAX_VALUE)
                        .addComponent(btnCancel)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnOK, javax.swing.GroupLayout.PREFERRED_SIZE, 176, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jLabel2)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(jLabel8)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, 108, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 563, Short.MAX_VALUE))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel1)
                    .addComponent(jLabel5)
                    .addComponent(jLabel6)
                    .addComponent(jLabel4)
                    .addComponent(jLabel7))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel2)
                    .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel8))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 194, Short.MAX_VALUE)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jLabel4)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel5)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jLabel6)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(jLabel7)
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnOK)
                    .addComponent(btnCancel))
                .addContainerGap())
        );

        pack();
    }// </editor-fold>//GEN-END:initComponents

    private void btnOKActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnOKActionPerformed
        this.useSelectedItems();
    }//GEN-LAST:event_btnOKActionPerformed

    private void btnCancelActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnCancelActionPerformed
        this.cancel();
    }//GEN-LAST:event_btnCancelActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnCancel;
    private javax.swing.JButton btnOK;
    private javax.swing.JComboBox cbxYear;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JTable tblSNRGroupList;
    // End of variables declaration//GEN-END:variables

}
