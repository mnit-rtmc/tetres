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
package ticas.tetres.admin.snowmgmt;

import ticas.common.infra.Infra;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IResponseCallback;
import ticas.common.pyticas.responses.ResponseIntegerList;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.types.AbstractDataChangeListener;
import ticas.tetres.admin.api.SnowEventClient;
import ticas.tetres.admin.api.SnowManagementClient;
import ticas.tetres.admin.types.SnowEventInfo;
import ticas.tetres.admin.types.SnowManagementInfo;
import ticas.tetres.admin.types.SpecialEventInfo;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.table.DefaultTableModel;
import org.apache.logging.log4j.core.Logger;

/**
 *
 * @author Chongmyung Park
 */
public class SNListPanel extends JPanel {

    private Infra infra;
    private List<SnowManagementInfo> selectedSNMs = new ArrayList<>();
    private List<SnowEventInfo> selectedSNEs = new ArrayList<>();
    private Integer selectedYear;
    private List<SnowEventInfo> sneList = new ArrayList<>();
    private List<SnowManagementInfo> snmList = new ArrayList<>();
    private SnowEventClient snowEventModel;
    private SnowManagementClient snowMgmtModel;
    private Logger logger;

    /**
     * Creates new form RouteEditorPanel
     */
    public SNListPanel() {
        initComponents();
    }

    /**
     * *
     * initialize variables and UI
     */
    public void init() {
        System.out.println("SNListPanel.init()");
        this.infra = Infra.getInstance();
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.snowEventModel = new SnowEventClient();
        this.snowMgmtModel = new SnowManagementClient();

        // when year is selected
        this.cbxYear.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                selectedYear = getSelectedYear();
                loadListByYear();
            }
        });

        // when snow event is clicked
        this.tbSNEList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                // update
                selectedSNEs.clear();
                for (int row : tbSNEList.getSelectedRows()) {
                    selectedSNEs.add(sneList.get(row));
                }
                loadSnowMgmt();
            }
        });

        // when management data is clicked
        this.tbSnowMgmtInfo.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                // update selected snow management data
                selectedSNMs.clear();
                for (int row : tbSnowMgmtInfo.getSelectedRows()) {
                    selectedSNMs.add(snmList.get(row));
                }
            }
        });

        // snow event data change listener
        this.snowEventModel.addChangeListener(new AbstractDataChangeListener<SnowEventInfo>() {

            @Override
            public void yearsSuccess(List<Integer> obj) {
                Integer sYear = selectedYear;
                cbxYear.removeAllItems();
                cbxYear.addItem("Select Year");
                cbxYear.addItem("All years");
                for (Integer i : obj) {
                    cbxYear.addItem(i);
                }
                reset();
                setYear(sYear);
                loadListByYear();
            }

            @Override
            public void yearsFailed(HttpResult httpResult) {
                logger.error(httpResult.res_code + " / " + httpResult.res_msg);
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "fail to load year information for snow events");
            }

            @Override
            public void listSuccess(List<SnowEventInfo> list) {
                sneList = list;
                setEvtTable();
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of snow event");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                snowEventModel.years();
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                logger.warn(String.format("Fail to delete items : %s", ids.toString()));
                logger.debug(result.contents);
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to delete the selected snow event");
            }

        });

        // snow management data change listener
        this.snowMgmtModel.addChangeListener(new AbstractDataChangeListener<SnowManagementInfo>() {
            @Override
            public void listSuccess(List<SnowManagementInfo> list) {
                snmList = list;
                setMgmtTable();
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of snow management data");
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to delete the selected snow management data");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                setMgmtTable();
            }

        });

        // load snow event list
        this.snowEventModel.years();
    }

    public void refresh() {
        if(this.cbxYear.getItemCount() == 0) {
            this.snowEventModel.years();
        }
    }
    
    /**
     *
     * load list by selected year
     */
    private void loadListByYear() {
        Integer sYear = getSelectedYear();
        if (sYear == null) {
            reset();
        } else if (sYear == 0) {
            this.snowEventModel.list();
        } else if (sYear > 1) {
            this.snowEventModel.listByYear(sYear);
        }
    }
    
    /**
     * load snow management data for the selected snow event
     */
    private void loadSnowMgmt() {
        if (!selectedSNEs.isEmpty()) {
            snowMgmtModel.list(selectedSNEs.get(0).id);
        }
    }

        /**
     * open snow event creation dialog
     */
    private void addSnowEvent() {
        SNECreateDialog rcd = new SNECreateDialog(TeTRESConfig.mainFrame);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
        this.snowEventModel.years();
    }
    
    /**
     * open snow management data creation dialog
     */
    private void addSnowMgmtData() {
        if (this.selectedSNEs.isEmpty()) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please select a snow event");
            return;
        }
        SNMCreateDialog mcd = new SNMCreateDialog(TeTRESConfig.mainFrame, this.selectedSNEs.get(0));
        mcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        mcd.setVisible(true);
        loadSnowMgmt();
    }
        
    /**
     * open snow management data edit dialog
     */
    private void editSnowManagement() {
        if (this.selectedSNMs.isEmpty() || this.selectedSNMs.size() > 1) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please select one snow management data");
            return;
        }
        SNMEditDialog rcd = new SNMEditDialog(TeTRESConfig.mainFrame, this.selectedSNMs.get(0));
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
        loadSnowMgmt();
    }

    /**
     * delete snow event
     */
    private void deleteSnowEvent() {
        if (this.selectedSNEs.isEmpty()) {
            return;
        }
        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected snow event informations?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (SnowEventInfo se : this.selectedSNEs) {
                ids.add(se.id);
            }
            this.snowEventModel.delete(ids);
        }
    }
    
    /**
     * delete snow management data
     */
    private void deleteSnowManagement() {
        if (this.selectedSNMs.isEmpty()) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please select snow management data");
            return;
        }
        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected managment data ?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (SnowManagementInfo se : this.selectedSNMs) {
                ids.add(se.id);
            }
            this.snowMgmtModel.delete(ids);
            loadSnowMgmt();
        }
    }
    
    /**
     *
     * @return selected year of combo box
     */
    private Integer getSelectedYear() {
        Integer sYear = null;
        int slt = this.cbxYear.getSelectedIndex();
        if (slt == 1) {
            sYear = 0;
        } else if (slt > 1) {
            int year = Integer.parseInt(this.cbxYear.getSelectedItem().toString());
            sYear = year;
        } else {
            sYear = null;
        }
        return sYear;
    }

    /**
     * *
     * reset map, list and selected item
     */
    private void reset() {
        this.sneList.clear();
        this.snmList.clear();
        this.selectedSNEs.clear();
        this.selectedSNMs.clear();
        setEvtTable();
        setMgmtTable();
    }

    /**
     * *
     * set snow event list table
     */
    private void setEvtTable() {
        final DefaultTableModel tm = (DefaultTableModel) this.tbSNEList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SnowEventInfo s : this.sneList) {
            tm.addRow(new Object[]{s.start_time, s.end_time});
        }
    }

    /**
     *
     * set snow management list table
     */
    private void setMgmtTable() {
        final DefaultTableModel tm = (DefaultTableModel) this.tbSnowMgmtInfo.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SnowManagementInfo s : this.snmList) {
            tm.addRow(new Object[]{s._snowevent.getDuration(), s._snowroute.name, s.lane_lost_time, s.lane_regain_time, s.duration});
        }
    }

    /**
     *
     * set combo box according to the given year
     *
     * @param sYear year
     */
    private void setYear(Integer sYear) {
        int nYears = this.cbxYear.getItemCount();
        if (nYears <= 2) {
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
        tbSNEList = new javax.swing.JTable();
        btnDeleteSnowEvent = new javax.swing.JButton();
        jLabel1 = new javax.swing.JLabel();
        btnAdd = new javax.swing.JButton();
        cbxYear = new javax.swing.JComboBox();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbSnowMgmtInfo = new javax.swing.JTable();
        jLabel3 = new javax.swing.JLabel();
        btnEditMgmtInfo = new javax.swing.JButton();
        btnDeleteMgmtInfo = new javax.swing.JButton();
        btnAddSnowMgmt = new javax.swing.JButton();

        jLabel2.setText("Snow Event List");

        tbSNEList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Start Time", "End Time"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class
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
        tbSNEList.setSelectionMode(javax.swing.ListSelectionModel.SINGLE_SELECTION);
        jScrollPane3.setViewportView(tbSNEList);

        btnDeleteSnowEvent.setText("Delete Snow Event");
        btnDeleteSnowEvent.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteSnowEventActionPerformed(evt);
            }
        });

        jLabel1.setText("Filter");

        btnAdd.setText("Add Snow Event");
        btnAdd.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddActionPerformed(evt);
            }
        });

        tbSnowMgmtInfo.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Snow Event", "Snow Route", "Lane Lost Time", "Lane Regain Time", "Lane Lost Duration (hour)"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.Float.class
            };
            boolean[] canEdit = new boolean [] {
                false, false, false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jScrollPane1.setViewportView(tbSnowMgmtInfo);

        jLabel3.setText("Snow Management Information");

        btnEditMgmtInfo.setText("Edit Management Info");
        btnEditMgmtInfo.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEditMgmtInfoActionPerformed(evt);
            }
        });

        btnDeleteMgmtInfo.setText("Delete Management Info");
        btnDeleteMgmtInfo.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteMgmtInfoActionPerformed(evt);
            }
        });

        btnAddSnowMgmt.setText("Add Snow Management Info");
        btnAddSnowMgmt.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddSnowMgmtActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jLabel2)
                    .addComponent(cbxYear, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 330, Short.MAX_VALUE)
                    .addComponent(jLabel1)
                    .addComponent(btnAdd, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnDeleteSnowEvent, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 578, Short.MAX_VALUE)
                    .addGroup(layout.createSequentialGroup()
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(jLabel3)
                                .addGap(18, 18, 18)
                                .addComponent(btnAddSnowMgmt)
                                .addGap(0, 0, Short.MAX_VALUE))
                            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                                .addGap(0, 0, Short.MAX_VALUE)
                                .addComponent(btnEditMgmtInfo)))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnDeleteMgmtInfo)))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnAdd, javax.swing.GroupLayout.PREFERRED_SIZE, 35, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel3)
                    .addComponent(btnAddSnowMgmt))
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addGap(18, 18, 18)
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel2)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 213, Short.MAX_VALUE))
                    .addGroup(layout.createSequentialGroup()
                        .addGap(6, 6, 6)
                        .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(btnDeleteSnowEvent, javax.swing.GroupLayout.DEFAULT_SIZE, 30, Short.MAX_VALUE)
                    .addComponent(btnDeleteMgmtInfo, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnEditMgmtInfo, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

        private void btnDeleteSnowEventActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteSnowEventActionPerformed
            this.deleteSnowEvent();
        }//GEN-LAST:event_btnDeleteSnowEventActionPerformed

    private void btnAddActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddActionPerformed
        this.addSnowEvent();
    }//GEN-LAST:event_btnAddActionPerformed

    private void btnAddSnowMgmtActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddSnowMgmtActionPerformed
        this.addSnowMgmtData();
    }//GEN-LAST:event_btnAddSnowMgmtActionPerformed

    private void btnDeleteMgmtInfoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteMgmtInfoActionPerformed
        this.deleteSnowManagement();
    }//GEN-LAST:event_btnDeleteMgmtInfoActionPerformed

    private void btnEditMgmtInfoActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEditMgmtInfoActionPerformed
        this.editSnowManagement();
    }//GEN-LAST:event_btnEditMgmtInfoActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private org.jdesktop.http.async.event.AsyncRequestAdapter asyncRequestAdapter1;
    private javax.swing.JButton btnAdd;
    private javax.swing.JButton btnAddSnowMgmt;
    private javax.swing.JButton btnDeleteMgmtInfo;
    private javax.swing.JButton btnDeleteSnowEvent;
    private javax.swing.JButton btnEditMgmtInfo;
    private javax.swing.JComboBox cbxYear;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JTable tbSNEList;
    private javax.swing.JTable tbSnowMgmtInfo;
    // End of variables declaration//GEN-END:variables

}
