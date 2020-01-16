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

import common.infra.Corridor;
import common.infra.Infra;
import common.infra.InfraObject;
import common.infra.RNode;
import ncrtes.NCRTESConfig;
import ncrtes.api.TargetStationClient;
import ncrtes.types.AbstractDataChangeListener;
import ncrtes.types.ComboItem;
import ncrtes.types.TargetStationInfo;
import common.pyticas.HttpResult;
import common.ui.CorridorSelector;
import common.ui.IInitializable;
import java.awt.Point;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;

/**
 *
 * @author chong
 */
public class PanelTargetStation_backup extends javax.swing.JPanel implements IInitializable, ISetTargetStation {

    private Corridor selectedCorridor = null;
    private Integer selectedYear = null;
    private List<TargetStationInfo> selectedTargetStations = new ArrayList<TargetStationInfo>();
    private List<TargetStationInfo> targetStations = new ArrayList<TargetStationInfo>();
    private TargetStationClient api;

    /**
     * Creates new form PanelEstimation
     */
    public PanelTargetStation_backup() {
        initComponents();
    }

    @Override
    public void init() {

        this.panTSMap.init(this);

        this.api = new TargetStationClient();

        this.corridorSelector.init(Infra.getInstance(), new CorridorSelector.CorridorSelectedListener() {
            @Override
            public void OnSelected(int selectedIndex, Corridor corridor) {
                selectedCorridor = corridor;
                requestList();
            }
        });

        // when year filter is changed
        this.cbxYear.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                selectedYear = getSelectedYear();
                requestList();
            }
        });

        this.api.addChangeListener(new AbstractDataChangeListener<TargetStationInfo>() {

            @Override
            public void yearsFailed(HttpResult httpResult) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "fail to load year information for target station data");
            }

            @Override
            public void yearsSuccess(List<Integer> obj) {
                Integer sYear = selectedYear;
                cbxYear.removeAllItems();
                cbxYear.addItem("Select Year");
                Collections.sort(obj, Collections.reverseOrder());
                for (Integer i : obj) {
                    String yearString = i.toString();
                    Integer nextYear = i + 1;
                    String nextYearString = nextYear.toString();
                    cbxYear.addItem(new ComboItem(yearString, yearString + " - " + nextYearString));
                }
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to delete the selected target station");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                requestList();
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to get list of target station");
            }

            @Override
            public void listSuccess(List<TargetStationInfo> list) {
                targetStations = list;
                setTargetStationTable();
            }
        });

        // when route selected
        this.tblStationList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                onTargetStationClicked();
            }

            @Override
            public void mousePressed(MouseEvent me) {
                JTable table =(JTable) me.getSource();
                Point p = me.getPoint();
                int row = table.rowAtPoint(p);
                if (me.getClickCount() == 2) {
                    editTargetStation();
                }
            }            
            
        });
        
        
        this.api.years();
    }
    
    @Override
    public void refresh() {
        // do nothing
    }     

    private void requestList() {
        if (this.selectedCorridor == null) {
            return;
        }
        Infra infra = Infra.getInstance();
        this.panTSMap.mapHelper.clear();
        List<RNode> stations = new ArrayList<RNode>();
        for (String rnode_name : this.selectedCorridor.stations) {
            stations.add(infra.getRNode(rnode_name));
        }
        this.panTSMap.mapHelper.showRNodes(stations);
        if (this.selectedCorridor != null && this.selectedYear != null) {
            this.api.list(this.selectedYear, this.selectedCorridor.name);
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
            ComboItem item = (ComboItem) this.cbxYear.getSelectedItem();
            int year = Integer.parseInt(item.getValue());
            sYear = year;
        } else {
            sYear = null;
        }
        return sYear;
    }

    private void setTargetStationTable() {
        Infra infra = Infra.getInstance();
        final DefaultTableModel tm = (DefaultTableModel) this.tblStationList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (TargetStationInfo s : this.targetStations) {
            RNode station = infra.getRNode(s.station_id);
            tm.addRow(new Object[]{s, s.snowroute_name, s.detectors});
        }
        this.setTargetStationAsBlueMarker();
    }

    private void setTargetStationAsBlueMarker() {
        Infra infra = Infra.getInstance();
        List<RNode> stations = new ArrayList<RNode>();
        for (TargetStationInfo tsi : this.targetStations) {
            stations.add(infra.getRNode(tsi.station_id));
        }
        this.panTSMap.mapHelper.setRouteAsBlueMarker(stations.toArray(new InfraObject[stations.size()]));
    }

    @Override
    public void setTargetStation(RNode station) {
        if (!Infra.getInstance().isAvailableStation(station)) {
            return;
        }
        TargetStationInfo tsmi = new TargetStationInfo();
        tsmi.corridor_name = station.corridor;
        tsmi.station_id = station.station_id;
        this.api.insert(tsmi);
    }

    @Override
    public void unsetTargetStation(RNode station) {
        this.selectedTargetStations.clear();
        DefaultTableModel tm = (DefaultTableModel) tblStationList.getModel();
        for (TargetStationInfo s : this.targetStations) {
            if (s != null && s.station_id.equals(station.station_id)) {
                selectedTargetStations.add(s);
            }
        }
        this.removeTargetStation();
    }

    private void onTargetStationClicked() {
        this.selectedTargetStations.clear();

        DefaultTableModel tm = (DefaultTableModel) tblStationList.getModel();
        for (int row : tblStationList.getSelectedRows()) {
            TargetStationInfo s = targetStations.get(row);
            if (s != null) {
                selectedTargetStations.add(s);
            }
        }
    }

    private void removeTargetStation() {
        if (this.selectedTargetStations.isEmpty()) {
            return;
        }
        int res = JOptionPane.showConfirmDialog(NCRTESConfig.mainFrame, "Delete selected target stations ?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (TargetStationInfo snrgi : this.selectedTargetStations) {
                ids.add(snrgi.id);
            }
            this.api.delete(ids);
        }
    }

    private void editTargetStation() {
        if (this.selectedTargetStations.isEmpty() || this.selectedTargetStations.size() > 1) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Use it after selecting one item?");
            return;
        }
        TargetStationEditDialog tsed = new TargetStationEditDialog(NCRTESConfig.mainFrame, this.selectedYear, this.selectedTargetStations.get(0), true);
        tsed.setLocationRelativeTo(this);
        tsed.setVisible(true);
        if (tsed.isUpdated()) {
            this.updateTargetStationInfo(tsed.getTargetStationInfo());
        }
    }

    private void updateTargetStationInfo(TargetStationInfo tsi) {
        Infra infra = Infra.getInstance();
        final DefaultTableModel tm = (DefaultTableModel) this.tblStationList.getModel();       
        for (int i = 0; i < tm.getRowCount(); i++) {
            TargetStationInfo ex = (TargetStationInfo)tm.getValueAt(i, 0);
            if(ex.id.equals(tsi.id)) {
                tm.setValueAt(tsi.snowroute_name, i, 1);
                tm.setValueAt(tsi.detectors, i, 2);
                break;
            }
        }
        for(TargetStationInfo _tsi : this.targetStations)
        {
            if(_tsi.id.equals(tsi.id)) {
                _tsi.detectors = tsi.detectors;
                _tsi.snowroute_name = tsi.snowroute_name;
                _tsi.snowroute_id = tsi.snowroute_id;
            }
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

        jPanel1 = new javax.swing.JPanel();
        jLabel1 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane4 = new javax.swing.JScrollPane();
        tblStationList = new JTable();
        corridorSelector = new common.ui.CorridorSelector();
        btnDelete = new javax.swing.JButton();
        cbxYear = new javax.swing.JComboBox();
        jLabel3 = new javax.swing.JLabel();
        btnEdit = new javax.swing.JButton();
        panTSMap = new ncrtes.targetstation.map.TSMap();

        jLabel1.setText("Corridor");

        jLabel2.setText("Stations");

        tblStationList.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Station ID", "Truck Route", "Detectors"
            }
        ) {
            Class[] types = new Class [] {
                String.class, String.class, String.class
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
        tblStationList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane4.setViewportView(tblStationList);
        if (tblStationList.getColumnModel().getColumnCount() > 0) {
            tblStationList.getColumnModel().getColumn(0).setMinWidth(80);
            tblStationList.getColumnModel().getColumn(0).setPreferredWidth(80);
            tblStationList.getColumnModel().getColumn(0).setMaxWidth(80);
        }

        btnDelete.setText("Remove Selected Stations");
        btnDelete.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteActionPerformed(evt);
            }
        });

        jLabel3.setText("Year");

        btnEdit.setText("Edit");
        btnEdit.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEditActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane4, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                        .addComponent(btnEdit)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, 40, Short.MAX_VALUE)
                        .addComponent(btnDelete))
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel2)
                            .addComponent(jLabel1)
                            .addComponent(corridorSelector, javax.swing.GroupLayout.DEFAULT_SIZE, 0, Short.MAX_VALUE))
                        .addGap(10, 10, 10)
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, 118, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(jLabel3))))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel1)
                    .addComponent(jLabel3))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(corridorSelector, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addComponent(jLabel2)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jScrollPane4, javax.swing.GroupLayout.DEFAULT_SIZE, 420, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnDelete)
                    .addComponent(btnEdit))
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(panTSMap, javax.swing.GroupLayout.DEFAULT_SIZE, 524, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(panTSMap, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
    }private void btnDeleteActionPerformed(java.awt.event.ActionEvent evt) {
        removeTargetStation();
    }

    private void btnEditActionPerformed(java.awt.event.ActionEvent evt) {
        editTargetStation();
    }


    // Variables declaration - do not modify
    private javax.swing.JButton btnDelete;
    private javax.swing.JButton btnEdit;
    private javax.swing.JComboBox cbxYear;
    private common.ui.CorridorSelector corridorSelector;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JScrollPane jScrollPane4;
    private ncrtes.targetstation.map.TSMap panTSMap;
    private JTable tblStationList;
    // End of variables declaration

}
