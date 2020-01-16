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
package admin.wz;

import common.infra.Corridor;
import common.infra.Infra;
import common.infra.RNode;
import common.log.TICASLogger;
import common.pyticas.HttpResult;
import common.ui.map.MapHelper;
import common.route.Route;
import admin.TeTRESConfig;
import admin.api.WorkzoneClient;
import admin.api.WorkzoneGroupClient;
import admin.types.AbstractDataChangeListener;
import admin.types.WorkZoneGroupInfo;
import admin.types.WorkZoneInfo;
import common.ui.map.TileServerFactory;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;
import org.apache.logging.log4j.core.Logger;
import admin.wz.WZEditDialog;
import admin.wz.WZGroupEditDialog;

/**
 *
 * @author Chongmyung Park
 */
public class WZListPanel extends javax.swing.JPanel {

    protected Infra infra;
    protected List<Corridor> corridors = new ArrayList<>();
    protected MapHelper mapHelper;
    private List<WorkZoneGroupInfo> wzGroupList = new ArrayList<>();
    private List<WorkZoneInfo> wzList = new ArrayList<>();
    private List<WorkZoneGroupInfo> selectedWZGroups = new ArrayList<>();
    private List<WorkZoneInfo> selectedWZs = new ArrayList<>();
    private boolean firstResize = true;
    private Integer selectedYear;
    private WorkzoneClient wzApi;
    private WorkzoneGroupClient wzGroupApi;
    private Logger logger;
    private WorkZoneGroupInfo currentWorkzoneGroup;
    private WorkZoneInfo currentWorkzone;

    /**
     * Creates new form RouteEditorPanel
     */
    public WZListPanel() {
        initComponents();
    }

    public void init() {
        this.infra = Infra.getInstance();
        this.corridors = infra.getCorridors();
        this.jxMap.setTileFactory(TileServerFactory.getTileFactory());
        this.jxMap.getMiniMap().setVisible(false);
        this.mapHelper = new MapHelper(jxMap);
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.wzApi = new WorkzoneClient();
        this.wzGroupApi = new WorkzoneGroupClient();

        // add corridors
        this.cbxCorridors.addItem("All Corridors");
        for (Corridor c : this.infra.getCorridors()) {
            this.cbxCorridors.addItem(c);
        }

        // when window size is changed
        this.panRouteInfo.addComponentListener(new ComponentAdapter() {
            @Override
            public void componentResized(ComponentEvent e) {
                if (firstResize) {
                    panRouteInfo.setDividerLocation(0.5);
                    firstResize = false;
                }
            }
        });

        // when year filter is changed
        this.cbxYear.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                selectedYear = getSelectedYear();
                loadListByYear();
            }
        });

        // when corridor is chnaged
        this.cbxCorridors.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                resetWorkzoneInfo();
                setWorkzoneGroupTable();
            }
        });

        // when work zone group is selected
        this.tblWZGroupList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                onWorkzoneGroupInfoClicked();
            }
        });

        // when work zone is selected
        this.tblWZList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                onWorkzoneInfoClicked();
            }
        });

        // add work zone group data change listener
        this.wzGroupApi.addChangeListener(new AbstractDataChangeListener<WorkZoneGroupInfo>() {
            @Override
            public void yearsFailed(HttpResult httpResult) {
                logger.error(httpResult.res_code + " / " + httpResult.res_msg);
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "fail to load year information for work zone group");
            }

            @Override
            public void yearsSuccess(List<Integer> obj) {
                Integer sYear = selectedYear;
                cbxYear.removeAllItems();
                cbxYear.addItem("Select Year");
                cbxYear.addItem("All years");
                cbxYear.addItem("No years yet");
                for (Integer i : obj) {
                    cbxYear.addItem(i);
                }
                resetWorkzoneGroupInfo();
                setYear(sYear);
                loadListByYear();
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of workzone group");
            }

            @Override
            public void listSuccess(List<WorkZoneGroupInfo> list) {
                wzGroupList = list;
                resetWorkzoneInfo();
                setWorkzoneGroupTable();
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to delete the selected workzone groups");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                wzGroupApi.years();
            }

        });

        // add work zone data change listener
        this.wzApi.addChangeListener(new AbstractDataChangeListener<WorkZoneInfo>() {
            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of workzone group");
            }

            @Override
            public void listSuccess(List<WorkZoneInfo> list) {
                wzList = list;
                setWorkzoneTable();
                setWorkzoneInfo(currentWorkzone);
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to delete the selected workzones");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                loadListByYear();
            }
        });

        this.wzGroupApi.years();
    }
    
    public void refresh() {
        if(this.cbxYear.getItemCount() == 0) {
            this.wzGroupApi.years();                    
        }
    }

    private void onWorkzoneGroupInfoClicked() {
        selectedWZGroups.clear();

        DefaultTableModel tm = (DefaultTableModel) tblWZGroupList.getModel();
        for (int row : tblWZGroupList.getSelectedRows()) {
            WorkZoneGroupInfo s = (WorkZoneGroupInfo) tm.getValueAt(row, 0);
            if (s != null) {
                selectedWZGroups.add(s);
            }
        }

        if (selectedWZGroups.isEmpty()) {
            resetWorkzoneGroupInfo();
            return;
        }
        currentWorkzoneGroup = getSelectedWorkzoneGroupInfo();
        wzApi.list(getSelectedWorkzoneGroupInfo().id);
    }

    private void onWorkzoneInfoClicked() {
        selectedWZs.clear();

        DefaultTableModel tm = (DefaultTableModel) tblWZList.getModel();
        for (int row : tblWZList.getSelectedRows()) {
            WorkZoneInfo s = wzList.get(row);
            if (s != null) {
                selectedWZs.add(s);
            }
        }

        if (selectedWZs.isEmpty()) {
            resetWorkzoneInfo();
            return;
        }

        List<RNode> rnodes = new ArrayList<RNode>();
        List<RNode> rnodes1 = new ArrayList<RNode>();
        List<RNode> rnodes2 = new ArrayList<RNode>();

        for (WorkZoneInfo wzi : selectedWZs) {
            for (RNode rn : wzi.route1.getRNodes()) {
                rnodes1.add(rn);
                rnodes.add(rn);
            }
            for (RNode rn : wzi.route2.getRNodes()) {
                rnodes2.add(rn);
                rnodes.add(rn);
            }

        }

        currentWorkzone = getSelectedWorkzoneInfo();

        mapHelper.showRNodes(rnodes);
        mapHelper.setCenter(rnodes.get(0));

        if (selectedWZGroups.size() > 1) {
            tbxInfo1.setText("Multiple routes are selected");
            tbxInfo2.setText("Multiple routes are selected");
        } else {
            tbxInfo1.setText(getRouteInfoString(selectedWZs.get(0).route1));
            tbxInfo2.setText(getRouteInfoString(selectedWZs.get(0).route2));
        }
    }

    /**
     * create work zone group
     */
    private void createWorkzoneGroup() {
        WZGroupEditDialog rcd = new WZGroupEditDialog(TeTRESConfig.mainFrame, null, true);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
        this.wzGroupApi.years();
    }

    /**
     * edit work zone group
     */
    protected void editWorkzoneGroup() {
        if (this.selectedWZGroups.isEmpty() || this.selectedWZGroups.size() > 1) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single work zone to edit information");
            return;
        }
        WZGroupEditDialog red = new WZGroupEditDialog(TeTRESConfig.mainFrame, this.selectedWZGroups.get(0), true);
        red.setLocationRelativeTo(TeTRESConfig.mainFrame);
        red.setVisible(true);
        this.wzGroupApi.years();
    }

    /**
     * create work zone
     */
    private void createWorkzone() {
        if (this.selectedWZGroups.isEmpty()) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single work zone to edit information");
            return;
        }
        WorkZoneGroupInfo wzgi = this.selectedWZGroups.get(0);

        WZEditDialog rcd = new WZEditDialog(TeTRESConfig.mainFrame, wzgi, null, true);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
        this.wzGroupApi.years();
    }

    /**
     * edit work zone
     */
    private void editWorkzone() {
        if (this.selectedWZs.isEmpty()) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single work zone configuration to edit information");
            return;
        }        
        WorkZoneGroupInfo wzgi = this.selectedWZGroups.get(0);
        WorkZoneInfo wzi = this.selectedWZs.get(0);
        
        WZEditDialog rcd = new WZEditDialog(TeTRESConfig.mainFrame, wzgi, wzi, true);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
        this.wzGroupApi.years();
    }

    /**
     * copy work zone data
     */
    protected void copyWorkzone() {
        if (this.selectedWZs.isEmpty() || this.selectedWZs.size() > 1) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single work zone to copy information");
            return;
        }
        WorkZoneGroupInfo wzgi = null;
        if (!this.selectedWZGroups.isEmpty()) {
            wzgi = this.selectedWZGroups.get(0);
        }
        WZEditDialog red = new WZEditDialog(TeTRESConfig.mainFrame, wzgi, null, true);
        red.setLocationRelativeTo(TeTRESConfig.mainFrame);
        red.setCopied(this.selectedWZs.get(0).clone());
        red.setVisible(true);
        this.wzGroupApi.years();
    }

    /**
     * delete work zone groups
     */
    protected void deleteWorkzoneGroups() {
        if (this.selectedWZGroups.isEmpty()) {
            return;
        }
        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected work zone groups ?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (WorkZoneGroupInfo wzgi : this.selectedWZGroups) {
                ids.add(wzgi.id);
            }
            this.wzGroupApi.delete(ids);
        }
    }

    /**
     * delete work zones
     */
    protected void deleteWorkzones() {
        if (this.selectedWZs.isEmpty()) {
            return;
        }
        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected work zones ?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (WorkZoneInfo wzi : this.selectedWZs) {
                ids.add(wzi.id);
            }
            this.wzApi.delete(ids);
        }
    }

    /**
     * *
     * load list by selected year
     */
    protected void loadListByYear() {
        Integer sYear = getSelectedYear();
        if (sYear == null) {
            resetWorkzoneGroupInfo();
        } else if (sYear == 0) {
            this.wzGroupApi.list();
        } else if (sYear == -1) {
            this.wzGroupApi.listByYear(null);
        } else if (sYear > 2) {
            this.wzGroupApi.listByYear(sYear);
        }
    }

    /**
     * *
     * reset data
     */
    protected void resetWorkzoneGroupInfo() {
        this.mapHelper.clear();
        this.wzGroupList.clear();
        setWorkzoneGroupTable();
        resetWorkzoneInfo();
    }

    /**
     * *
     * reset map, list and selected item
     */
    protected void resetWorkzoneInfo() {
        this.mapHelper.clear();
        this.tbxInfo1.setText("");
        this.tbxInfo2.setText("");
        this.wzList.clear();
        this.selectedWZs.clear();
        setWorkzoneTable();
    }

    /**
     *
     * @return selected year of combo box
     */
    protected Integer getSelectedYear() {
        Integer sYear = null;
        int slt = this.cbxYear.getSelectedIndex();
        if (slt == 1) {
            sYear = 0;
        } else if (slt == 2) {
            sYear = -1;
        } else if (slt > 2) {
            int year = Integer.parseInt(this.cbxYear.getSelectedItem().toString());
            sYear = year;
        } else {
            sYear = null;
        }
        return sYear;
    }

    /**
     * returns selected work zone group
     *
     * @return selected work zone group
     */
    protected WorkZoneGroupInfo getSelectedWorkzoneGroupInfo() {
        for (int row : this.tblWZGroupList.getSelectedRows()) {
            return this.wzGroupList.get(row);
        }
        return null;
    }

    /**
     * set selected work zone group
     *
     */
    protected void setWorkzoneGroupInfo(WorkZoneGroupInfo wzgi) {
        if (wzgi == null) {
            return;
        }
        Integer sltIndex = null;
        for (int row = 0; row < this.wzGroupList.size(); row++) {
            WorkZoneGroupInfo s = this.wzGroupList.get(row);
            if (Objects.equals(s.id, wzgi.id)) {
                sltIndex = row;
                break;
            }
        }
        if (sltIndex != null) {
            this.tblWZGroupList.setRowSelectionInterval(sltIndex, sltIndex);
            this.wzApi.list(wzgi.id);
        }
    }

    /**
     * returns selected work zone
     *
     * @return selected work zone group
     */
    protected WorkZoneInfo getSelectedWorkzoneInfo() {
        for (int row : this.tblWZList.getSelectedRows()) {
            return this.wzList.get(row);
        }
        return null;
    }

    /**
     * set selected work zone
     *
     */
    protected void setWorkzoneInfo(WorkZoneInfo wzi) {
        if (wzi == null) {
            return;
        }
        DefaultTableModel tm = (DefaultTableModel) tblWZList.getModel();
        Integer sltIndex = null;
        for (int row = 0; row < this.wzList.size(); row++) {
            WorkZoneInfo s = this.wzList.get(row);
            if (Objects.equals(s.id, wzi.id)) {
                sltIndex = row;
                break;
            }
        }
        if (sltIndex != null) {
            this.tblWZList.setRowSelectionInterval(sltIndex, sltIndex);
            onWorkzoneInfoClicked();
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
        if (nYears <= 2) {
            return;
        }
        if (sYear == null) {
            this.cbxYear.setSelectedIndex(0);
        } else if (sYear == -1) {
            this.cbxYear.setSelectedIndex(2);
        } else if (sYear == 0) {
            this.cbxYear.setSelectedIndex(1);
        } else {
            for (int sidx = 3; sidx < nYears; sidx++) {
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
     * set work zone group list table
     */
    protected void setWorkzoneGroupTable() {
        int slt = this.cbxCorridors.getSelectedIndex();
        Corridor corr = null;
        if (slt > 0) {
            corr = (Corridor) this.cbxCorridors.getSelectedItem();
        }
        final DefaultTableModel tm = (DefaultTableModel) this.tblWZGroupList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (WorkZoneGroupInfo s : this.wzGroupList) {
            if (corr == null || s.corridors.contains(corr.name)) {
                tm.addRow(new Object[]{s});
            }
        }
        setWorkzoneGroupInfo(currentWorkzoneGroup);
    }

    /**
     * *
     * set work zone list table
     */
    protected void setWorkzoneTable() {
        final DefaultTableModel tm = (DefaultTableModel) this.tblWZList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (WorkZoneInfo s : this.wzList) {
            tm.addRow(new Object[]{s.getDuration()});
        }
    }

    protected String getRouteInfoString(Route r) {
        StringBuilder sb = new StringBuilder();
        sb.append(String.format("Name : %s", r.name));
        sb.append(System.getProperty("line.separator"));

        if (r.desc != null && !r.desc.isEmpty()) {
            sb.append("----------------");
            sb.append(System.getProperty("line.separator"));
            sb.append(r.desc);
            sb.append(System.getProperty("line.separator"));
        }

        sb.append("----------------");
        sb.append(System.getProperty("line.separator"));
        Infra infra = Infra.getInstance();
        int idx = 1;
        for (RNode rnode : r.getRNodes()) {
            if (infra.isStation(rnode)) {
                sb.append(String.format("[%02d] (S) %s (%s)", idx, rnode.label, rnode.station_id));
            } else if (infra.isEntrance(rnode)) {
                sb.append(String.format("[%02d] (E) %s (%s)", idx, rnode.label, rnode.name));
            } else if (infra.isExit(rnode)) {
                sb.append(String.format("[%02d] (X) %s (%s)", idx, rnode.label, rnode.name));
            }
            idx++;
            sb.append(System.getProperty("line.separator"));
        }
        sb.setLength(sb.length() - 2);
        return sb.toString();
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">
    private void initComponents() {

        asyncRequestAdapter1 = new org.jdesktop.http.async.event.AsyncRequestAdapter();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane3 = new javax.swing.JScrollPane();
        tblWZGroupList = new javax.swing.JTable();
        btnDeleteSelection = new javax.swing.JButton();
        btnEditRoute = new javax.swing.JButton();
        jxMap = new org.jdesktop.swingx.JXMapKit();
        jLabel1 = new javax.swing.JLabel();
        cbxCorridors = new javax.swing.JComboBox();
        btnAddRoute = new javax.swing.JButton();
        cbxYear = new javax.swing.JComboBox();
        panRouteInfo = new javax.swing.JSplitPane();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxInfo1 = new javax.swing.JTextArea();
        jScrollPane2 = new javax.swing.JScrollPane();
        tbxInfo2 = new javax.swing.JTextArea();
        btnCopyWorkZone = new javax.swing.JButton();
        jScrollPane4 = new javax.swing.JScrollPane();
        tblWZList = new javax.swing.JTable();
        btnDeleteSelection1 = new javax.swing.JButton();
        btnEditRoute1 = new javax.swing.JButton();
        btnAddRoute1 = new javax.swing.JButton();
        jLabel3 = new javax.swing.JLabel();

        jLabel2.setText("Work Zone List");

        tblWZGroupList.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Name"
            }
        ) {
            boolean[] canEdit = new boolean [] {
                false
            };

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        tblWZGroupList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane3.setViewportView(tblWZGroupList);

        btnDeleteSelection.setText("Delete");
        btnDeleteSelection.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteSelectionActionPerformed(evt);
            }
        });

        btnEditRoute.setText("Edit");
        btnEditRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEditRouteActionPerformed(evt);
            }
        });

        jLabel1.setText("Filter");

        btnAddRoute.setText("Add Work Zone");
        btnAddRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRouteActionPerformed(evt);
            }
        });

        panRouteInfo.setOrientation(javax.swing.JSplitPane.VERTICAL_SPLIT);

        tbxInfo1.setColumns(20);
        tbxInfo1.setFont(new java.awt.Font("Tahoma", 0, 11)); // NOI18N
        tbxInfo1.setRows(5);
        jScrollPane1.setViewportView(tbxInfo1);

        panRouteInfo.setTopComponent(jScrollPane1);

        tbxInfo2.setColumns(20);
        tbxInfo2.setFont(new java.awt.Font("Tahoma", 0, 11)); // NOI18N
        tbxInfo2.setRows(5);
        jScrollPane2.setViewportView(tbxInfo2);

        panRouteInfo.setBottomComponent(jScrollPane2);

        btnCopyWorkZone.setText("Copy");
        btnCopyWorkZone.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCopyWorkZoneActionPerformed(evt);
            }
        });

        tblWZList.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Duration"
            }
        ) {
            Class[] types = new Class [] {
                String.class
            };
            boolean[] canEdit = new boolean [] {
                false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        tblWZList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane4.setViewportView(tblWZList);

        btnDeleteSelection1.setText("Delete");
        btnDeleteSelection1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnDeleteSelection1ActionPerformed(evt);
            }
        });

        btnEditRoute1.setText("Edit");
        btnEditRoute1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnEditRoute1ActionPerformed(evt);
            }
        });

        btnAddRoute1.setText("Add Work Zone Configurations");
        btnAddRoute1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRoute1ActionPerformed(evt);
            }
        });

        jLabel3.setText("Work Zone Configurations");

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jLabel1)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(btnDeleteSelection)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnEditRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addComponent(btnAddRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(layout.createSequentialGroup()
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(jLabel2)
                                .addGap(0, 21, Short.MAX_VALUE))
                            .addComponent(cbxYear, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(cbxCorridors, javax.swing.GroupLayout.PREFERRED_SIZE, 105, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jLabel3)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(btnDeleteSelection1, javax.swing.GroupLayout.PREFERRED_SIZE, 63, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnCopyWorkZone)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(btnEditRoute1, javax.swing.GroupLayout.PREFERRED_SIZE, 71, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(jScrollPane4, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addComponent(btnAddRoute1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 323, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(panRouteInfo, javax.swing.GroupLayout.PREFERRED_SIZE, 206, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(btnAddRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 35, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(btnAddRoute1, javax.swing.GroupLayout.PREFERRED_SIZE, 35, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(18, 18, 18)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(jLabel1)
                            .addComponent(jLabel3))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(layout.createSequentialGroup()
                                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                    .addComponent(cbxCorridors, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addGap(18, 18, 18)
                                .addComponent(jLabel2)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE))
                            .addComponent(jScrollPane4, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE))
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                            .addComponent(btnDeleteSelection, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(btnEditRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(btnCopyWorkZone, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(btnDeleteSelection1, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(btnEditRoute1, javax.swing.GroupLayout.PREFERRED_SIZE, 30, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 465, Short.MAX_VALUE)
                    .addComponent(panRouteInfo))
                .addContainerGap())
        );
    }private void btnDeleteSelectionActionPerformed(java.awt.event.ActionEvent evt) {
            this.deleteWorkzoneGroups();
        }

    private void btnAddRouteActionPerformed(java.awt.event.ActionEvent evt) {
        this.createWorkzoneGroup();
    }

    private void btnEditRouteActionPerformed(java.awt.event.ActionEvent evt) {
        this.editWorkzoneGroup();
    }

    private void btnCopyWorkZoneActionPerformed(java.awt.event.ActionEvent evt) {
        this.copyWorkzone();
    }

    private void btnDeleteSelection1ActionPerformed(java.awt.event.ActionEvent evt) {
        this.deleteWorkzones();
    }

    private void btnEditRoute1ActionPerformed(java.awt.event.ActionEvent evt) {
        this.editWorkzone();
    }

    private void btnAddRoute1ActionPerformed(java.awt.event.ActionEvent evt) {
        this.createWorkzone();
    }


    // Variables declaration - do not modify
    private org.jdesktop.http.async.event.AsyncRequestAdapter asyncRequestAdapter1;
    private javax.swing.JButton btnAddRoute;
    private javax.swing.JButton btnAddRoute1;
    private javax.swing.JButton btnCopyWorkZone;
    private javax.swing.JButton btnDeleteSelection;
    private javax.swing.JButton btnDeleteSelection1;
    private javax.swing.JButton btnEditRoute;
    private javax.swing.JButton btnEditRoute1;
    private javax.swing.JComboBox cbxCorridors;
    private javax.swing.JComboBox cbxYear;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private org.jdesktop.swingx.JXMapKit jxMap;
    private javax.swing.JSplitPane panRouteInfo;
    private javax.swing.JTable tblWZGroupList;
    private javax.swing.JTable tblWZList;
    private javax.swing.JTextArea tbxInfo1;
    private javax.swing.JTextArea tbxInfo2;
    // End of variables declaration

}
