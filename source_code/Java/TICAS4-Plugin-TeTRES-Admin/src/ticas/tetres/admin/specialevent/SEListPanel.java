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
package ticas.tetres.admin.specialevent;

import ticas.common.infra.Infra;
import ticas.common.log.TICASLogger;
import ticas.common.ui.map.InfraPoint;
import ticas.common.ui.map.MapHelper;
import ticas.common.pyticas.HttpResult;
import ticas.tetres.admin.TeTRESConfig;
import ticas.tetres.admin.api.SpecialEventClient;
import ticas.tetres.admin.types.SpecialEventInfo;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.table.DefaultTableModel;
import ticas.tetres.admin.types.AbstractDataChangeListener;
import ticas.common.ui.map.TileServerFactory;
import java.util.Objects;
import org.apache.logging.log4j.core.Logger;

/**
 *
 * @author Chongmyung Park
 */
public class SEListPanel extends JPanel {

    private Infra infra;
    private MapHelper mapHelper;
    private Integer selectedYear;
    private final List<SpecialEventInfo> selectedSEs = new ArrayList<>();
    private List<SpecialEventInfo> seList = new ArrayList<>();
    private SpecialEventClient model;
    private Logger logger;

    public SEListPanel() {
        initComponents();
        this.jxMap.setTileFactory(TileServerFactory.getTileFactory());
    }

    /**
     * *
     * initialize variables and UI
     */
    public void init() {
        this.infra = Infra.getInstance();
        this.jxMap.getMiniMap().setVisible(false);
        this.mapHelper = new MapHelper(jxMap);
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.model = new SpecialEventClient();

        // when year is selected
        this.cbxYear.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                selectedYear = getSelectedYear();
                loadListByYear();
            }
        });

        // when route is selected
        this.tbSEList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                selectedSEs.clear();

                DefaultTableModel tm = (DefaultTableModel) tbSEList.getModel();
                for (int row : tbSEList.getSelectedRows()) {
                    SpecialEventInfo s = (SpecialEventInfo) tm.getValueAt(row, 1);
                    if (s != null) {
                        selectedSEs.add(s);
                    }
                }

                if (selectedSEs.isEmpty()) {
                    mapHelper.clear();
                    return;
                }

                List<InfraPoint> ips = new ArrayList<>();
                for (SpecialEventInfo sei : selectedSEs) {
                    ips.add(new InfraPoint(String.format("%s(%s, %d)", sei.name, sei.getDuration(), sei.attendance), sei.lat, sei.lon));
                }
                mapHelper.showInfraPoints(ips);
            }
        });

        // data change listener
        this.model.addChangeListener(new AbstractDataChangeListener<SpecialEventInfo>() {

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
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "fail to load year information for special events");
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of special event");
            }

            @Override
            public void listSuccess(List<SpecialEventInfo> list) {
                seList = list;
                setTable();
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                model.years();
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                logger.warn(String.format("Fail to delete items : %s", ids.toString()));
                logger.debug(result.contents);
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to delete the selected special event");
            }

        });

        this.model.years();
    }
    
    public void refresh() {
        if(this.cbxYear.getItemCount() == 0) {
            this.model.years();
        }
    }
    
    /**
     * *
     * open create dialog
     */
    private void createSpecialEvent() {
        SEEditDialog rcd = new SEEditDialog(TeTRESConfig.mainFrame, null);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
//        Integer year = rcd.getYear();
//        if(year != null) {
//            this.selectedYear = year;
//        }
        this.model.years();
    }

    /**
     * *
     * open edit dialog
     */
    protected void editSpecialEvent() {
        if (this.selectedSEs.isEmpty() || this.selectedSEs.size() > 1) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single route to edit information");
            return;
        }
        SEEditDialog red = new SEEditDialog(TeTRESConfig.mainFrame, this.selectedSEs.get(0));
        red.setLocationRelativeTo(TeTRESConfig.mainFrame);
        red.setVisible(true);
        this.model.years();
    }

    /**
     * delete selected items
     */
    protected void deleteSpecialEvents() {
        if (this.selectedSEs.isEmpty()) {
            return;
        }

        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected special events?", "Confirm", JOptionPane.YES_NO_OPTION);

        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (SpecialEventInfo se : this.selectedSEs) {
                ids.add(se.id);
            }
            this.model.delete(ids);
        }
    }

    /**
     * *
     * load list by selected year
     */
    protected void loadListByYear() {
        Integer sYear = getSelectedYear();
        if (sYear == null) {
            reset();
        } else if (sYear == 0) {
            model.list();
        } else if (sYear > 1) {
            model.listByYear(sYear);
        }
    }

    /**
     * *
     * reset map, list and selected item
     */
    protected void reset() {
        this.mapHelper.clear();
        this.seList.clear();
        this.selectedSEs.clear();
        setTable();
    }

    /**
     * *
     *
     * @return selected year of combo box
     */
    protected Integer getSelectedYear() {
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
     * set combo box according to the given year
     *
     * @param sYear year
     */
    protected void setYear(Integer sYear) {
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
     * *
     * set list table
     */
    protected void setTable() {
        final DefaultTableModel tm = (DefaultTableModel) this.tbSEList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SpecialEventInfo s : this.seList) {
            tm.addRow(new Object[]{s.getDuration(), s, s.attendance});
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
        tbSEList = new javax.swing.JTable();
        btnDeleteSelection = new javax.swing.JButton();
        btnEditRoute = new javax.swing.JButton();
        jxMap = new org.jdesktop.swingx.JXMapKit();
        jLabel1 = new javax.swing.JLabel();
        btnAddRoute = new javax.swing.JButton();
        cbxYear = new javax.swing.JComboBox();

        jLabel2.setText("Special Event List");

        tbSEList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Duration", "Name", "Attendance"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.Object.class, java.lang.Integer.class
            };
            boolean[] canEdit = new boolean [] {
                false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        tbSEList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane3.setViewportView(tbSEList);

        btnDeleteSelection.setText("Delete");
        btnDeleteSelection.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteSelectionActionPerformed(evt);
            }
        });

        btnEditRoute.setText("Edit Special Event Info");
        btnEditRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEditRouteActionPerformed(evt);
            }
        });

        jLabel1.setText("Filter");

        btnAddRoute.setText("Add Special Event");
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
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(btnAddRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 332, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel1)
                    .addComponent(jLabel2)
                    .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                        .addComponent(cbxYear, javax.swing.GroupLayout.Alignment.LEADING, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addGroup(javax.swing.GroupLayout.Alignment.LEADING, layout.createSequentialGroup()
                            .addComponent(btnDeleteSelection, javax.swing.GroupLayout.PREFERRED_SIZE, 141, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGap(18, 18, 18)
                            .addComponent(btnEditRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                        .addComponent(jScrollPane3, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, 330, Short.MAX_VALUE)))
                .addGap(18, 18, 18)
                .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 508, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                        .addComponent(btnAddRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 35, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(18, 18, 18)
                        .addComponent(jLabel2)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                        .addGap(18, 18, 18)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(btnDeleteSelection, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(btnEditRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 438, Short.MAX_VALUE))
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

        private void btnDeleteSelectionActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteSelectionActionPerformed
            this.deleteSpecialEvents();
        }//GEN-LAST:event_btnDeleteSelectionActionPerformed

    private void btnAddRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddRouteActionPerformed
        this.createSpecialEvent();
    }//GEN-LAST:event_btnAddRouteActionPerformed

    private void btnEditRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEditRouteActionPerformed
        this.editSpecialEvent();
    }//GEN-LAST:event_btnEditRouteActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private org.jdesktop.http.async.event.AsyncRequestAdapter asyncRequestAdapter1;
    private javax.swing.JButton btnAddRoute;
    private javax.swing.JButton btnDeleteSelection;
    private javax.swing.JButton btnEditRoute;
    private javax.swing.JComboBox cbxYear;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JScrollPane jScrollPane3;
    private org.jdesktop.swingx.JXMapKit jxMap;
    private javax.swing.JTable tbSEList;
    // End of variables declaration//GEN-END:variables

}
