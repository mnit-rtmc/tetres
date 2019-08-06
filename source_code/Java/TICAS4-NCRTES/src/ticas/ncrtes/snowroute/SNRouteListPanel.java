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
package ticas.ncrtes.snowroute;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.infra.RNode;
import ticas.common.log.TICASLogger;
import ticas.common.pyticas.HttpResult;
import ticas.common.ui.map.MapHelper;
import ticas.common.route.Route;
import ticas.ncrtes.NCRTESConfig;
import ticas.ncrtes.api.SnowRouteClient;
import ticas.ncrtes.api.SnowRouteGroupClient;
import ticas.ncrtes.types.AbstractDataChangeListener;
import ticas.ncrtes.types.ComboItem;
import ticas.ncrtes.types.SnowRouteGroupInfo;
import ticas.ncrtes.types.SnowRouteInfo;
import ticas.common.ui.map.TileServerFactory;
import java.awt.event.ComponentAdapter;
import java.awt.event.ComponentEvent;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Objects;
import javax.swing.JOptionPane;
import javax.swing.table.DefaultTableModel;
import org.apache.logging.log4j.core.Logger;

/**
 *
 * @author Chongmyung Park
 */
public class SNRouteListPanel extends javax.swing.JPanel {

    protected Infra infra;
    protected List<Corridor> corridors = new ArrayList<>();
    protected MapHelper mapHelper;
    private List<SnowRouteGroupInfo> snrGroupList = new ArrayList<>();
    private List<SnowRouteInfo> snrList = new ArrayList<>();
    private List<SnowRouteGroupInfo> selectedSNRGroup = new ArrayList<>();
    private List<SnowRouteInfo> selectedSNRoute = new ArrayList<>();
    private boolean firstResize = true;
    private Integer selectedYear;
    private SnowRouteClient snrApi;
    private SnowRouteGroupClient snrgApi;
    private Logger logger;
    private SnowRouteGroupInfo currentSNRGroupInfo;
    private SnowRouteInfo currentSNRoute;

    /**
     * Creates new form RouteEditorPanel
     */
    public SNRouteListPanel() {
        initComponents();
    }

    public void init() {
        this.infra = Infra.getInstance();
        this.corridors = infra.getCorridors();
        this.jxMap.setTileFactory(TileServerFactory.getTileFactory());
        this.jxMap.getMiniMap().setVisible(false);
        this.mapHelper = new MapHelper(jxMap);
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.snrApi = new SnowRouteClient();
        this.snrgApi = new SnowRouteGroupClient();

        // when year filter is changed
        this.cbxYear.addActionListener(new java.awt.event.ActionListener() {
            @Override
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                selectedYear = getSelectedYear();
                loadListByYear();
            }
        });

        // when snow management route group is selected
        this.tblSNRGroupList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                onSNRGroupClicked();
            }
        });

        // when route selected
        this.tblSNRList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                onSNRouteInfoClicked();
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
                cbxYear.addItem("Select Year");
                cbxYear.addItem("All years");
                Collections.sort(obj ,Collections.reverseOrder());
                for (Integer i : obj) {
                    String yearString = i.toString();
                    Integer nextYear = i + 1;
                    String nextYearString = nextYear.toString();
                    cbxYear.addItem(new ComboItem(yearString, yearString + " - " + nextYearString));
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
                resetSnowRouteInfo();
                setSNRGroupTable();
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to delete the selected snow management route groups");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
//                snrgApi.list();
                snrgApi.years();
            }

        });

        // add snow route change listener
        this.snrApi.addChangeListener(new AbstractDataChangeListener<SnowRouteInfo>() {
            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to get list of snow management route");
            }

            @Override
            public void listSuccess(List<SnowRouteInfo> list) {
                snrList = list;
                setSNRouteTable();
                setSnowRouteInfo(currentSNRoute);
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Fail to delete the selected workzones");
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                loadListByYear();
            }
        });
        
        snrgApi.years();
    }

    private void onSNRGroupClicked() {
        selectedSNRGroup.clear();

        DefaultTableModel tm = (DefaultTableModel) tblSNRGroupList.getModel();
        for (int row : tblSNRGroupList.getSelectedRows()) {
            SnowRouteGroupInfo s = (SnowRouteGroupInfo) tm.getValueAt(row, 0);
            if (s != null) {
                selectedSNRGroup.add(s);
            }
        }

        if (selectedSNRGroup.isEmpty()) {
            resetSnowRouteGroupInfo();
            return;
        }
        currentSNRGroupInfo = getSelectedSnowRouteGroupInfo();
        snrApi.list(currentSNRGroupInfo.id);
    }

    private void onSNRouteInfoClicked() {
        selectedSNRoute.clear();

        DefaultTableModel tm = (DefaultTableModel) tblSNRList.getModel();
        for (int row : tblSNRList.getSelectedRows()) {
            SnowRouteInfo s = snrList.get(row);
            if (s != null) {
                selectedSNRoute.add(s);
            }
        }

        if (selectedSNRoute.isEmpty()) {
            resetSnowRouteInfo();
            return;
        }

        List<RNode> rnodes = new ArrayList<RNode>();
        List<RNode> rnodes1 = new ArrayList<RNode>();
        List<RNode> rnodes2 = new ArrayList<RNode>();

        for (SnowRouteInfo wzi : selectedSNRoute) {
            for (RNode rn : wzi.route1.getRNodes()) {
                rnodes1.add(rn);
                rnodes.add(rn);
            }
            for (RNode rn : wzi.route2.getRNodes()) {
                rnodes2.add(rn);
                rnodes.add(rn);
            }

        }

        currentSNRoute = getSelectedSnowRouteInfo();

        mapHelper.showRNodes(rnodes);
        mapHelper.setCenter(rnodes.get(0));

    }

    /**
     * create snow management route group
     */
    private void createSNRGroup() {
        SNRouteGroupEditDialog rcd = new SNRouteGroupEditDialog(NCRTESConfig.mainFrame, null, true);
        rcd.setLocationRelativeTo(NCRTESConfig.mainFrame);
        rcd.setVisible(true);
        this.snrgApi.years();
    }

    /**
     * edit snow management route group
     */
    protected void editSNRGroup() {
        if (this.selectedSNRGroup.isEmpty() || this.selectedSNRGroup.size() > 1) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Select a single snow management route to edit information");
            return;
        }
        SNRouteGroupEditDialog red = new SNRouteGroupEditDialog(NCRTESConfig.mainFrame, this.selectedSNRGroup.get(0), true);
        red.setLocationRelativeTo(NCRTESConfig.mainFrame);
        red.setVisible(true);
        this.snrgApi.years();
    }
    
    /**
     * copy SNRouteGroup
     */
    protected void copySNRGroup() {
        if (this.selectedSNRGroup.isEmpty() || this.selectedSNRGroup.size() > 1) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Select a single work zone to copy information");
            return;
        }
        SnowRouteGroupInfo snrgi = this.selectedSNRGroup.get(0);
        SNRouteGroupEditDialog red = new SNRouteGroupEditDialog(NCRTESConfig.mainFrame, snrgi, true);
        red.setLocationRelativeTo(NCRTESConfig.mainFrame);
        red.setCopied(snrgi.clone());
        red.setVisible(true);
        this.snrgApi.years();
    }    

    /**
     * create work zone
     */
    private void createSNRoute() {
        if (this.selectedSNRGroup.isEmpty()) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Select a single snow management route to edit information");
            return;
        }
        SnowRouteGroupInfo snrgi = this.selectedSNRGroup.get(0);

        SNRouteEditDialog rcd = new SNRouteEditDialog(NCRTESConfig.mainFrame, snrgi, null, true);
        rcd.setLocationRelativeTo(NCRTESConfig.mainFrame);
        rcd.setVisible(true);
        this.snrgApi.years();
    }

    /**
     * edit work zone
     */
    private void editSNRoute() {
        if (this.selectedSNRoute.isEmpty()) {
            JOptionPane.showMessageDialog(NCRTESConfig.mainFrame, "Select a single work zone configuration to edit information");
            return;
        }
        SnowRouteGroupInfo snrgi = this.selectedSNRGroup.get(0);
        SnowRouteInfo snri = this.selectedSNRoute.get(0);

        SNRouteEditDialog rcd = new SNRouteEditDialog(NCRTESConfig.mainFrame, snrgi, snri, true);
        rcd.setLocationRelativeTo(NCRTESConfig.mainFrame);
        rcd.setVisible(true);

        this.snrgApi.years();
    }

    /**
     * delete snow management route groups
     */
    protected void deletedSNRGroup() {
        if (this.selectedSNRGroup.isEmpty()) {
            return;
        }
        int res = JOptionPane.showConfirmDialog(NCRTESConfig.mainFrame, "Delete selected snow management route groups ?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (SnowRouteGroupInfo snrgi : this.selectedSNRGroup) {
                ids.add(snrgi.id);
            }
            this.snrgApi.delete(ids);
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
                ComboItem item = (ComboItem)this.cbxYear.getItemAt(sidx);
                Integer y = Integer.parseInt(item.getValue());
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
        if (slt == 1) {
            sYear = 0;
        } else if (slt > 1) {
            ComboItem item = (ComboItem)this.cbxYear.getSelectedItem();
            int year = Integer.parseInt(item.getValue());
            sYear = year;
        } else {
            sYear = null;
        }
        return sYear;
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
     * delete work zones
     */
    protected void deleteSNRoutes() {
        if (this.selectedSNRoute.isEmpty()) {
            return;
        }
        int res = JOptionPane.showConfirmDialog(NCRTESConfig.mainFrame, "Delete selected work zones ?", "Confirm", JOptionPane.YES_NO_OPTION);
        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (SnowRouteInfo wzi : this.selectedSNRoute) {
                ids.add(wzi.id);
            }
            this.snrApi.delete(ids);
        }
    }

    /**
     * *
     * reset data
     */
    protected void resetSnowRouteGroupInfo() {
        this.mapHelper.clear();
        this.snrGroupList.clear();
        setSNRGroupTable();
        resetSnowRouteInfo();
    }

    /**
     * *
     * reset map, list and selected item
     */
    protected void resetSnowRouteInfo() {
        this.mapHelper.clear();
        this.snrList.clear();
        this.selectedSNRoute.clear();
        setSNRouteTable();
    }

    /**
     * returns selected snow management route group
     *
     * @return selected snow management route group
     */
    protected SnowRouteGroupInfo getSelectedSnowRouteGroupInfo() {
        for (int row : this.tblSNRGroupList.getSelectedRows()) {
            return this.snrGroupList.get(row);
        }
        return null;
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
            this.snrApi.list(snrgi.id);
        }
    }

    /**
     * returns selected work zone
     *
     * @return selected snow management route group
     */
    protected SnowRouteInfo getSelectedSnowRouteInfo() {
        for (int row : this.tblSNRList.getSelectedRows()) {
            return this.snrList.get(row);
        }
        return null;
    }

    /**
     * set selected work zone
     *
     */
    protected void setSnowRouteInfo(SnowRouteInfo snri) {
        if (snri == null) {
            if (!this.snrList.isEmpty()) {
                this.tblSNRList.setRowSelectionInterval(0, 0);
                onSNRouteInfoClicked();
            }
            return;
        }
        DefaultTableModel tm = (DefaultTableModel) tblSNRList.getModel();
        Integer sltIndex = null;
        for (int row = 0; row < this.snrList.size(); row++) {
            SnowRouteInfo s = this.snrList.get(row);
            if (Objects.equals(s.id, snri.id)) {
                sltIndex = row;
                break;
            }
        }
        if (sltIndex != null) {
            this.tblSNRList.setRowSelectionInterval(sltIndex, sltIndex);
            onSNRouteInfoClicked();
        } else {
            if (!this.snrList.isEmpty()) {
                this.tblSNRList.setRowSelectionInterval(0, 0);
                onSNRouteInfoClicked();
            }
            return;
        }
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
            tm.addRow(new Object[]{s, s.region, s.sub_region, s.year, s.description});
        }
        setSnowRouteGroupInfo(currentSNRGroupInfo);
    }

    /**
     * *
     * set work zone list table
     */
    protected void setSNRouteTable() {
        final DefaultTableModel tm = (DefaultTableModel) this.tblSNRList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SnowRouteInfo s : this.snrList) {
            tm.addRow(new Object[]{s.name, s.description});
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
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        asyncRequestAdapter1 = new org.jdesktop.http.async.event.AsyncRequestAdapter();
        jxMap = new org.jdesktop.swingx.JXMapKit();
        jPanel1 = new javax.swing.JPanel();
        jScrollPane3 = new javax.swing.JScrollPane();
        tblSNRGroupList = new javax.swing.JTable();
        btnDeleteSelection = new javax.swing.JButton();
        btnEditRoute = new javax.swing.JButton();
        btnAddRoute = new javax.swing.JButton();
        jLabel1 = new javax.swing.JLabel();
        jLabel3 = new javax.swing.JLabel();
        cbxYear = new javax.swing.JComboBox();
        btnCopySNRouteGroup = new javax.swing.JButton();
        jPanel2 = new javax.swing.JPanel();
        jScrollPane4 = new javax.swing.JScrollPane();
        tblSNRList = new javax.swing.JTable();
        btnDeleteSelection1 = new javax.swing.JButton();
        btnEditRoute1 = new javax.swing.JButton();
        btnAddRoute1 = new javax.swing.JButton();
        jLabel2 = new javax.swing.JLabel();

        tblSNRGroupList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "RouteID", "Region", "SubRegion", "Year", "Memo"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.String.class, java.lang.String.class, java.lang.String.class, java.lang.Integer.class, java.lang.String.class
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
        tblSNRGroupList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane3.setViewportView(tblSNRGroupList);
        if (tblSNRGroupList.getColumnModel().getColumnCount() > 0) {
            tblSNRGroupList.getColumnModel().getColumn(0).setMinWidth(80);
            tblSNRGroupList.getColumnModel().getColumn(0).setPreferredWidth(80);
            tblSNRGroupList.getColumnModel().getColumn(0).setMaxWidth(80);
            tblSNRGroupList.getColumnModel().getColumn(1).setMinWidth(70);
            tblSNRGroupList.getColumnModel().getColumn(1).setPreferredWidth(70);
            tblSNRGroupList.getColumnModel().getColumn(1).setMaxWidth(70);
            tblSNRGroupList.getColumnModel().getColumn(2).setMinWidth(100);
            tblSNRGroupList.getColumnModel().getColumn(2).setPreferredWidth(100);
            tblSNRGroupList.getColumnModel().getColumn(2).setMaxWidth(100);
            tblSNRGroupList.getColumnModel().getColumn(3).setMinWidth(40);
            tblSNRGroupList.getColumnModel().getColumn(3).setPreferredWidth(40);
            tblSNRGroupList.getColumnModel().getColumn(3).setMaxWidth(40);
        }

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

        btnAddRoute.setText("Add Truck Route");
        btnAddRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRouteActionPerformed(evt);
            }
        });

        jLabel1.setText("Snow Management Route");

        jLabel3.setText("Year");

        btnCopySNRouteGroup.setText("Copy");
        btnCopySNRouteGroup.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCopySNRouteGroupActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 467, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(jLabel1)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(jLabel3)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, 108, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(btnDeleteSelection)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnEditRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 91, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnCopySNRouteGroup, javax.swing.GroupLayout.PREFERRED_SIZE, 91, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnAddRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel1)
                    .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(cbxYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(jLabel3)))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane3, javax.swing.GroupLayout.DEFAULT_SIZE, 260, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(btnDeleteSelection, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(btnEditRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(btnAddRoute, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(btnCopySNRouteGroup, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                .addContainerGap())
        );

        tblSNRList.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Name", "Memo"
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
        tblSNRList.setSelectionMode(javax.swing.ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane4.setViewportView(tblSNRList);
        if (tblSNRList.getColumnModel().getColumnCount() > 0) {
            tblSNRList.getColumnModel().getColumn(0).setMinWidth(100);
            tblSNRList.getColumnModel().getColumn(0).setPreferredWidth(100);
            tblSNRList.getColumnModel().getColumn(0).setMaxWidth(100);
        }

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

        btnAddRoute1.setText("Add  Route Configuration");
        btnAddRoute1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnAddRoute1ActionPerformed(evt);
            }
        });

        jLabel2.setText("Route Configurations");

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane4)
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addComponent(jLabel2)
                        .addGap(0, 0, Short.MAX_VALUE))
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addComponent(btnDeleteSelection1, javax.swing.GroupLayout.PREFERRED_SIZE, 63, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(10, 10, 10)
                        .addComponent(btnEditRoute1, javax.swing.GroupLayout.PREFERRED_SIZE, 87, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnAddRoute1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel2)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jScrollPane4, javax.swing.GroupLayout.PREFERRED_SIZE, 95, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnAddRoute1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(btnEditRoute1)
                    .addComponent(btnDeleteSelection1))
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                    .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 417, Short.MAX_VALUE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jPanel2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addContainerGap())))
        );
    }// </editor-fold>//GEN-END:initComponents

        private void btnDeleteSelectionActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteSelectionActionPerformed
            this.deletedSNRGroup();
        }//GEN-LAST:event_btnDeleteSelectionActionPerformed

    private void btnAddRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddRouteActionPerformed
        this.createSNRGroup();
    }//GEN-LAST:event_btnAddRouteActionPerformed

    private void btnEditRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEditRouteActionPerformed
        this.editSNRGroup();
    }//GEN-LAST:event_btnEditRouteActionPerformed

    private void btnDeleteSelection1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnDeleteSelection1ActionPerformed
        this.deleteSNRoutes();
    }//GEN-LAST:event_btnDeleteSelection1ActionPerformed

    private void btnEditRoute1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnEditRoute1ActionPerformed
        this.editSNRoute();
    }//GEN-LAST:event_btnEditRoute1ActionPerformed

    private void btnAddRoute1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnAddRoute1ActionPerformed
        this.createSNRoute();
    }//GEN-LAST:event_btnAddRoute1ActionPerformed

    private void btnCopySNRouteGroupActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnCopySNRouteGroupActionPerformed
        this.copySNRGroup();
    }//GEN-LAST:event_btnCopySNRouteGroupActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private org.jdesktop.http.async.event.AsyncRequestAdapter asyncRequestAdapter1;
    private javax.swing.JButton btnAddRoute;
    private javax.swing.JButton btnAddRoute1;
    private javax.swing.JButton btnCopySNRouteGroup;
    private javax.swing.JButton btnDeleteSelection;
    private javax.swing.JButton btnDeleteSelection1;
    private javax.swing.JButton btnEditRoute;
    private javax.swing.JButton btnEditRoute1;
    private javax.swing.JComboBox cbxYear;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane4;
    private org.jdesktop.swingx.JXMapKit jxMap;
    private javax.swing.JTable tblSNRGroupList;
    private javax.swing.JTable tblSNRList;
    // End of variables declaration//GEN-END:variables

}
