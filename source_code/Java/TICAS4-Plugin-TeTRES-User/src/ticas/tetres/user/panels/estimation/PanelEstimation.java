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
package ticas.tetres.user.panels.estimation;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.pyticas.HttpResult;
import ticas.tetres.user.panels.operatingconditions.OperatingConditionInfoHelper;
import ticas.tetres.user.TeTRESConfig;
import ticas.tetres.user.UIHelper;
import ticas.tetres.user.api.EstimationAPIClient;
import ticas.tetres.user.api.ReliabilityRouteAPIClient;
import ticas.tetres.user.filters.IFilterListChangeListener;
import ticas.tetres.user.panels.routegroup.IRouteGroupListChangeListener;
import ticas.tetres.user.panels.routegroup.RouteGroupInfoHelper;
import ticas.tetres.user.types.AbstractDataChangeListener;
import ticas.tetres.user.types.EstimationRequestInfo;
import ticas.tetres.user.types.IResultIsReady;
import ticas.tetres.user.types.OperatingConditionsInfo;
import ticas.tetres.user.types.ReliabilityRouteInfo;
import ticas.tetres.user.types.ReliabilityEstimationModeInfo;
import ticas.tetres.user.types.RouteGroupInfo;
import ticas.tetres.user.types.WeekdayConditionInfo;
import ticas.common.ui.CorridorSelector;
import ticas.common.ui.IInitializable;
import ticas.common.util.FileHelper;
import java.awt.Component;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.MouseEvent;
import java.awt.event.MouseListener;
import java.io.File;
import java.sql.Time;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.AbstractButton;
import javax.swing.JCheckBox;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.JTableHeader;
import javax.swing.table.TableCellRenderer;
import javax.swing.table.TableColumn;
import javax.swing.table.TableColumnModel;
import javax.swing.table.TableModel;
import org.jdesktop.swingx.mapviewer.GeoPosition;
import ticas.common.config.Config;
import ticas.common.ui.map.MapProvider;
import ticas.tetres.user.panels.operatingconditions.OCParamHelper;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class PanelEstimation extends javax.swing.JPanel implements IInitializable, IFilterListChangeListener, IRouteGroupListChangeListener {

    private final int initZoom = 10;
    private final double initLatitude = 44.974878;
    private final double initLongitude = -93.233414;
    private ReliabilityRouteAPIClient routeAPI;
    private EstimationAPIClient estimationAPI;
    private boolean isUIInitialized = false;
    private ReliabilityRouteInfo selectedRouteInfo;

    /**
     * Creates new form EstimationPanel
     */
    public PanelEstimation() {
        initComponents();
    }

    @Override
    public void init() {
        this.panMap.init();
        this.panMap.mapHelper.setCenter(this.initLatitude, this.initLongitude);
        this.panMap.mapHelper.jmKit.setZoom(this.initZoom);
        OperatingConditionInfoHelper.addChangeListener(this);
        OperatingConditionInfoHelper.loadOperatingConditionList();
        RouteGroupInfoHelper.addChangeListener(this);
        RouteGroupInfoHelper.loadRouteGroups();

        this.loadCorridors();
        this.estimationAPI = new EstimationAPIClient();
        this.routeAPI = new ReliabilityRouteAPIClient();
        this.routeAPI.addChangeListener(new AbstractDataChangeListener<ReliabilityRouteInfo>() {
            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of travel time route");
            }

            @Override
            public void listSuccess(List<ReliabilityRouteInfo> list) {
                updateRoute(list);
            }
        });

        this.cbxRoute.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                onSingleRouteSelected(false);
            }
        });

        this.cbxRouteGroups.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                onRouteGroupSelected(false);
            }
        });

        TableColumn tc = this.tblFilters.getColumnModel().getColumn(0);
        tc.setCellEditor(this.tblFilters.getDefaultEditor(Boolean.class));
        tc.setCellRenderer(this.tblFilters.getDefaultRenderer(Boolean.class));
        tc.setHeaderRenderer(new CheckBoxHeader(new ItemListener() {
            @Override
            public void itemStateChanged(ItemEvent e) {
                Object source = e.getSource();
                if (source instanceof AbstractButton == false) {
                    return;
                }
                boolean checked = e.getStateChange() == ItemEvent.SELECTED;
                for (int x = 0, y = tblFilters.getRowCount(); x < y; x++) {
                    tblFilters.setValueAt(new Boolean(checked), x, 0);
                }

            }
        }));
    }

    @Override
    public void refresh() {
        // do nothing
    }

    private void loadCorridors() {
        this.cbxCorridor.init(Infra.getInstance(), new CorridorSelector.CorridorSelectedListener() {
            @Override
            public void OnSelected(int selectedIndex, Corridor corridor) {
                routeAPI.listByCorridor(corridor);
            }
        });
    }

    @Override
    public void filterGroupUpdated(List<OperatingConditionsInfo> filterGroups) {
        DefaultTableModel model = (DefaultTableModel) this.tblFilters.getModel();
        List<String> selectedRegimes = new ArrayList<String>();
        for (int r = 0; r < model.getRowCount(); r++) {
            boolean isSelected = (boolean) model.getValueAt(r, 0);
            if (isSelected) {
                selectedRegimes.add(model.getValueAt(r, 1).toString());
            }
        }

        model.setRowCount(0);
        for (OperatingConditionsInfo fig : filterGroups) {
            model.addRow(new Object[]{false, fig, fig.desc});
        }

        if (!isUIInitialized) {
            loadRequestedInfo();
        } else {
            for (String regimeName : selectedRegimes) {
                for (int r = 0; r < model.getRowCount(); r++) {
                    OperatingConditionsInfo figInTable = (OperatingConditionsInfo) model.getValueAt(r, 1);
                    if (figInTable.name == null ? regimeName == null : figInTable.name.equals(regimeName)) {
                        model.setValueAt(true, r, 0);
                    }
                }
            }
        }
    }

    @Override
    public void routeGroupUpdated(List<RouteGroupInfo> groups) {
        this.cbxRouteGroups.removeAllItems();
        for (RouteGroupInfo routeGroupInfo : groups) {
            this.cbxRouteGroups.addItem(routeGroupInfo);
        }
    }

    private void updateRoute(List<ReliabilityRouteInfo> list) {
        this.cbxRoute.removeAllItems();
        for (ReliabilityRouteInfo rri : list) {
            this.cbxRoute.addItem(rri);
        }
    }

    private void doEstimate() {
        EstimationRequestInfo eri = this.getRequestOption();
        List<Integer> routeIDs = this.getSelectedRouteList();

        if (routeIDs.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Select travel time route");
            return;
        }

        if (eri.start_date == null || eri.end_date == null || eri.start_time == null || eri.end_time == null) {
            JOptionPane.showMessageDialog(this, "Set time frame");
            return;
        }

        Date startDate = this.dtStartDate.getDateObject();
        Date endDate = this.dtEndDate.getDateObject();
        long startDateTime = startDate.getTime();
        long endDateTime = endDate.getTime();
        long diffTime = endDateTime - startDateTime;
        long diffDays = diffTime / (1000 * 60 * 60 * 24);
        if (diffDays <= 0) {
            JOptionPane.showMessageDialog(this, "Set start-end date properly");
            return;
        }

        if (diffDays < 90) {
            if (JOptionPane.showConfirmDialog(this, "The selected duration is " + diffDays + " days.\nData can be not enough.\nDo you want to proceed?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
                return;
            }
        }

        Time startTime = this.dtStartTime.getTimeObject();
        Time endTime = this.dtStartTime.getTimeObject();
        long stime = startTime.getTime();
        long etime = endTime.getTime();
        long diffHours = (endDateTime - startDateTime) / (1000 * 60 * 60);
        if (diffHours <= 0) {
            JOptionPane.showMessageDialog(this, "Set Start-End time properly");
            return;
        }
        if (diffHours < 1) {
            if (JOptionPane.showConfirmDialog(this, "The selected time duration is " + diffHours + " hours.\nDo you want to proceed?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
                return;
            }
        }

        if (eri.weekdays.isNotSet()) {
            JOptionPane.showMessageDialog(this, "Select week days at least one");
            return;
        }

        if (eri.estmation_mode.isNotSet()) {
            JOptionPane.showMessageDialog(this, "Select a reliability type to estimate at least one");
            return;
        }

        if (eri.operating_conditions.isEmpty()) {
            JOptionPane.showMessageDialog(this, "Select an operating condition at least one");
            return;
        }

        if (!eri.write_graph_images && !eri.write_spreadsheets) {
            JOptionPane.showMessageDialog(this, "Select an output type at least one");
            return;
        }

        if(!OCParamHelper.validate(eri.oc_param)) {
            JOptionPane.showMessageDialog(this, "Update paramters for operating conditions");
            return;
        }

        this.estimationAPI.estimate(routeIDs, eri, new IResultIsReady() {
            @Override
            public void OnReady(String uid, String outputPath) {
                if(uid == null) {
                    JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to estimation");
                    return;
                }

                File oldOutputDir = new File(outputPath);

                // input output folder name
                String newFolderName = null;
                String newFolderPath = null;
                while(true) {
                    newFolderName = JOptionPane.showInputDialog(TeTRESConfig.mainFrame, "Output Folder Name :");
                    if(newFolderName == null || newFolderName.isEmpty()) {
                        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Empty Folder Name");
                        continue;
                    }
                    newFolderPath = oldOutputDir.getParent() + File.separator + newFolderName;

                    if(!FileHelper.isFilenameValid(newFolderName)) {
                        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Invalid Folder Name");
                    } else if(FileHelper.exists(newFolderPath)) {
                        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Existing Folder");
                    } else {
                        break;
                    }
                }

                // rename output folder
                File newOutputDir = new File(oldOutputDir.getParent() + File.separator + newFolderName);
                oldOutputDir.renameTo(newOutputDir);

                // open directory
                FileHelper.openDirectory(newOutputDir.getAbsolutePath());
            }
        });
        UIHelper.saveRequestInfo(eri);
    }

    private void loadRequestedInfo() {
        this.isUIInitialized = true;
        EstimationRequestInfo prevEri = UIHelper.getPreviousRequestInfo();
        if (prevEri == null) {
            return;
        }
        this.chkSunday.setSelected(prevEri.weekdays.sunday);
        this.chkMonday.setSelected(prevEri.weekdays.monday);
        this.chkTuesday.setSelected(prevEri.weekdays.tuesday);
        this.chkWednesday.setSelected(prevEri.weekdays.wednesday);
        this.chkThursday.setSelected(prevEri.weekdays.thursday);
        this.chkFriday.setSelected(prevEri.weekdays.friday);
        this.chkSaturday.setSelected(prevEri.weekdays.saturday);
        this.chkExceptHolidays.setSelected(prevEri.except_holiday);
        this.chkModeTimeOfDay.setSelected(prevEri.estmation_mode.mode_tod);
        this.chkModeWholeTime.setSelected(prevEri.estmation_mode.mode_whole);
        this.chkOutputSpreadsheets.setSelected(prevEri.write_spreadsheets);
        this.chkOutputGraphs.setSelected(prevEri.write_graph_images);
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        try {
            this.dtStartDate.setDateObject(sdf.parse(prevEri.start_date));
        } catch (ParseException ex) {
            Logger.getLogger(PanelEstimation.class.getName()).log(Level.SEVERE, null, ex);
        }
        try {
            this.dtEndDate.setDateObject(sdf.parse(prevEri.end_date));
        } catch (ParseException ex) {
            Logger.getLogger(PanelEstimation.class.getName()).log(Level.SEVERE, null, ex);
        }
        SimpleDateFormat sdf_time = new SimpleDateFormat("HH:mm");
        try {
            Date sdt = sdf_time.parse(prevEri.start_time);
            Time stime = new Time(sdt.getTime());
            this.dtStartTime.setTimeObject(stime);
        } catch (ParseException ex) {
            Logger.getLogger(PanelEstimation.class.getName()).log(Level.SEVERE, null, ex);
        }
        try {
            Date edt = sdf_time.parse(prevEri.end_time);
            Time etime = new Time(edt.getTime());
            this.dtEndTime.setTimeObject(etime);
        } catch (ParseException ex) {
            Logger.getLogger(PanelEstimation.class.getName()).log(Level.SEVERE, null, ex);
        }

        DefaultTableModel model = (DefaultTableModel) this.tblFilters.getModel();
        for (OperatingConditionsInfo fig : prevEri.operating_conditions) {
            for (int r = 0; r < model.getRowCount(); r++) {
                OperatingConditionsInfo figInTable = (OperatingConditionsInfo) model.getValueAt(r, 1);
                if (figInTable.name == null ? fig.name == null : figInTable.name.equals(fig.name)) {
                    model.setValueAt(true, r, 0);
                }
            }
        }
    }

    private List<Integer> getSelectedRouteList() {
        List<Integer> routeIds = new ArrayList<Integer>();

        if (this.tabRouteSelection.getSelectedIndex() == 0) {
            RouteGroupInfo routeGroup = (RouteGroupInfo) this.cbxRouteGroups.getSelectedItem();
            if (routeGroup != null) {
                for (ReliabilityRouteInfo rinfo : routeGroup.route_list) {
                    routeIds.add(rinfo.id);
                }
            }
        } else {
            routeIds.add(((ReliabilityRouteInfo) this.cbxRoute.getSelectedItem()).id);
        }
        return routeIds;
    }

    private EstimationRequestInfo getRequestOption() {
        SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd");
        EstimationRequestInfo eri = new EstimationRequestInfo();
        eri.start_date = sdf.format(this.dtStartDate.getDateObject());
        eri.end_date = sdf.format(this.dtEndDate.getDateObject());
        eri.start_time = this.dtStartTime.getTimeObject().toString();
        eri.end_time = this.dtEndTime.getTimeObject().toString();
        eri.weekdays = this.getSelectedWeekdays();
        eri.except_holiday = this.chkExceptHolidays.isSelected();
        eri.estmation_mode = this.getSelectedTypesOfReliability();
        eri.operating_conditions = this.getSelectedFilters();
        eri.write_spreadsheets = this.chkOutputSpreadsheets.isSelected();
        eri.write_graph_images = this.chkOutputGraphs.isSelected();
        eri.oc_param = OCParamHelper.loadParam();
        return eri;
    }

    private List<OperatingConditionsInfo> getSelectedFilters() {
        List<OperatingConditionsInfo> figs = new ArrayList<OperatingConditionsInfo>();
        TableModel model = this.tblFilters.getModel();
        for (int r = 0; r < this.tblFilters.getRowCount(); r++) {
            Boolean isChecked = (boolean) model.getValueAt(r, 0);
            if (isChecked) {
                OperatingConditionsInfo fig = (OperatingConditionsInfo) model.getValueAt(r, 1);
                figs.add(fig);
            }
        }
        return figs;
    }

    private WeekdayConditionInfo getSelectedWeekdays() {
        WeekdayConditionInfo weekdays = new WeekdayConditionInfo();
        weekdays.sunday = this.chkSunday.isSelected();
        weekdays.monday = this.chkMonday.isSelected();
        weekdays.tuesday = this.chkTuesday.isSelected();
        weekdays.wednesday = this.chkWednesday.isSelected();
        weekdays.thursday = this.chkThursday.isSelected();
        weekdays.friday = this.chkFriday.isSelected();
        weekdays.saturday = this.chkSaturday.isSelected();
        return weekdays;
    }

    private ReliabilityEstimationModeInfo getSelectedTypesOfReliability() {
        ReliabilityEstimationModeInfo mode = new ReliabilityEstimationModeInfo();
        mode.mode_tod = this.chkModeTimeOfDay.isSelected();
        mode.mode_whole = this.chkModeWholeTime.isSelected();
        return mode;
    }

    private void onSingleRouteSelected(boolean isTabChanged) {
        selectedRouteInfo = (ReliabilityRouteInfo) cbxRoute.getSelectedItem();
        if(isTabChanged && selectedRouteInfo == null) {
            return;
        }
        panMap.mapHelper.clear();
        if (selectedRouteInfo != null) {
            panMap.mapHelper.showRoute(selectedRouteInfo.route);
            panMap.mapHelper.setCenter(selectedRouteInfo.route.getRNodes().get(0));
        }
    }

    private void onRouteGroupSelected(boolean isTabChanged) {
        RouteGroupInfo routeGroupInfo = (RouteGroupInfo) cbxRouteGroups.getSelectedItem();
        if(isTabChanged && routeGroupInfo == null) {
            return;
        }
        panMap.mapHelper.clear();
        if (routeGroupInfo != null) {
            GeoPosition center = routeGroupInfo.getCenter();
            if(center != null) {
                panMap.mapHelper.showRoutes(routeGroupInfo.getRouteList());
                panMap.mapHelper.setCenter(center.getLatitude(), center.getLongitude());
            }
        }
    }

    private void onRouteSelectTabChanged() {
        int slt = this.tabRouteSelection.getSelectedIndex();
        if (slt == 0) {
            onRouteGroupSelected(true);
        } else if (slt == 1) {
            onSingleRouteSelected(true);
        }
    }



    class CheckBoxHeader extends JCheckBox implements TableCellRenderer, MouseListener {

        protected CheckBoxHeader rendererComponent;
        protected int column;
        protected boolean mousePressed = false;

        public CheckBoxHeader(ItemListener itemListener) {
            rendererComponent = this;
            rendererComponent.addItemListener(itemListener);
        }

        @Override
        public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
            if (table != null) {
                JTableHeader header = table.getTableHeader();
                if (header != null) {
                    header.setOpaque(false);
                    header.setBackground(header.getBackground());
                    header.addMouseListener(rendererComponent);
                }
            }
            setColumn(column);
            this.setHorizontalAlignment(JLabel.CENTER);
//            rendererComponent.setText("");
//            setBorder(UIManager.getBorder("TableHeader.cellBorder"));
            return rendererComponent;
        }

        protected void setColumn(int column) {
            this.column = column;
        }

        public int getColumn() {
            return column;
        }

        protected void handleClickEvent(MouseEvent e) {
            if (mousePressed) {
                mousePressed = false;
                JTableHeader header = (JTableHeader) (e.getSource());
                JTable tableView = header.getTable();
                TableColumnModel columnModel = tableView.getColumnModel();
                int viewColumn = columnModel.getColumnIndexAtX(e.getX());
                int column = tableView.convertColumnIndexToModel(viewColumn);

                if (viewColumn == this.column && e.getClickCount() == 1 && column != -1) {
                    doClick();
                }
            }
        }

        @Override
        public void mouseClicked(MouseEvent e) {
            handleClickEvent(e);
            ((JTableHeader) e.getSource()).repaint();
        }

        @Override
        public void mousePressed(MouseEvent e) {
            mousePressed = true;
        }

        @Override
        public void mouseReleased(MouseEvent e) {
        }

        @Override
        public void mouseEntered(MouseEvent e) {
        }

        @Override
        public void mouseExited(MouseEvent e) {
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

        panMap = new ticas.common.ui.map.MapPanel();
        jPanel3 = new javax.swing.JPanel();
        jPanel4 = new javax.swing.JPanel();
        tabRouteSelection = new javax.swing.JTabbedPane();
        jPanel7 = new javax.swing.JPanel();
        cbxRouteGroups = new javax.swing.JComboBox<>();
        jPanel2 = new javax.swing.JPanel();
        jLabel9 = new javax.swing.JLabel();
        cbxCorridor = new ticas.common.ui.CorridorSelector();
        cbxRoute = new javax.swing.JComboBox<>();
        jLabel10 = new javax.swing.JLabel();
        jLabel3 = new javax.swing.JLabel();
        dtStartDate = new ticas.common.ui.TICASDatePicker();
        jLabel4 = new javax.swing.JLabel();
        dtEndDate = new ticas.common.ui.TICASDatePicker();
        jLabel5 = new javax.swing.JLabel();
        dtStartTime = new ticas.common.ui.TICASTimePicker();
        jLabel6 = new javax.swing.JLabel();
        dtEndTime = new ticas.common.ui.TICASTimePicker();
        jLabel7 = new javax.swing.JLabel();
        jLabel8 = new javax.swing.JLabel();
        chkSunday = new javax.swing.JCheckBox();
        chkMonday = new javax.swing.JCheckBox();
        chkTuesday = new javax.swing.JCheckBox();
        chkWednesday = new javax.swing.JCheckBox();
        chkThursday = new javax.swing.JCheckBox();
        chkFriday = new javax.swing.JCheckBox();
        chkSaturday = new javax.swing.JCheckBox();
        chkExceptHolidays = new javax.swing.JCheckBox();
        jPanel6 = new javax.swing.JPanel();
        jLabel1 = new javax.swing.JLabel();
        chkModeTimeOfDay = new javax.swing.JCheckBox();
        chkModeWholeTime = new javax.swing.JCheckBox();
        jLabel2 = new javax.swing.JLabel();
        jScrollPane2 = new javax.swing.JScrollPane();
        tblFilters = new javax.swing.JTable();
        jLabel11 = new javax.swing.JLabel();
        chkOutputSpreadsheets = new javax.swing.JCheckBox();
        chkOutputGraphs = new javax.swing.JCheckBox();
        jButton4 = new javax.swing.JButton();

        jPanel4.setBorder(javax.swing.BorderFactory.createTitledBorder("Travel Time Route and Time Frame"));

        tabRouteSelection.addChangeListener(new javax.swing.event.ChangeListener() {
            public void stateChanged(javax.swing.event.ChangeEvent evt) {
                tabRouteSelectionStateChanged(evt);
            }
        });

        javax.swing.GroupLayout jPanel7Layout = new javax.swing.GroupLayout(jPanel7);
        jPanel7.setLayout(jPanel7Layout);
        jPanel7Layout.setHorizontalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(cbxRouteGroups, 0, 453, Short.MAX_VALUE)
                .addContainerGap())
        );
        jPanel7Layout.setVerticalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(cbxRouteGroups, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        tabRouteSelection.addTab("Route Group", jPanel7);

        jLabel9.setText("Corridor");

        jLabel10.setText("Route");

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel9)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(cbxCorridor, javax.swing.GroupLayout.PREFERRED_SIZE, 146, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jLabel10)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(cbxRoute, 0, 201, Short.MAX_VALUE)
                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(jLabel10)
                        .addComponent(cbxRoute, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addComponent(jLabel9)
                    .addComponent(cbxCorridor, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        tabRouteSelection.addTab("Single Route", jPanel2);

        jLabel3.setText("Start Date");

        jLabel4.setText("End Date");

        jLabel5.setText("Start Time");

        jLabel6.setText("End Time");

        jLabel7.setText("Week Days : ");

        jLabel8.setText("Holidays : ");

        chkSunday.setText("Sun.");

        chkMonday.setText("Mon.");

        chkTuesday.setSelected(true);
        chkTuesday.setText("Tue.");

        chkWednesday.setSelected(true);
        chkWednesday.setText("Wed.");

        chkThursday.setSelected(true);
        chkThursday.setText("Thu.");

        chkFriday.setText("Fri.");

        chkSaturday.setText("Sat.");

        chkExceptHolidays.setSelected(true);
        chkExceptHolidays.setText("except holidays");

        javax.swing.GroupLayout jPanel4Layout = new javax.swing.GroupLayout(jPanel4);
        jPanel4.setLayout(jPanel4Layout);
        jPanel4Layout.setHorizontalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel4Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(tabRouteSelection)
                    .addGroup(jPanel4Layout.createSequentialGroup()
                        .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                                .addGroup(jPanel4Layout.createSequentialGroup()
                                    .addComponent(jLabel3)
                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                    .addComponent(dtStartDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGap(18, 18, 18)
                                    .addComponent(jLabel4)
                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                    .addComponent(dtEndDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addGroup(jPanel4Layout.createSequentialGroup()
                                    .addComponent(jLabel5)
                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                    .addComponent(dtStartTime, javax.swing.GroupLayout.PREFERRED_SIZE, 154, javax.swing.GroupLayout.PREFERRED_SIZE)
                                    .addGap(18, 18, 18)
                                    .addComponent(jLabel6)
                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                    .addComponent(dtEndTime, javax.swing.GroupLayout.PREFERRED_SIZE, 156, javax.swing.GroupLayout.PREFERRED_SIZE)))
                            .addGroup(jPanel4Layout.createSequentialGroup()
                                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(jLabel8)
                                    .addComponent(jLabel7))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(jPanel4Layout.createSequentialGroup()
                                        .addComponent(chkSunday)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                        .addComponent(chkMonday)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(chkTuesday)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(chkWednesday)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(chkThursday)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(chkFriday)
                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                        .addComponent(chkSaturday))
                                    .addComponent(chkExceptHolidays))))
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel4Layout.setVerticalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel4Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(tabRouteSelection, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel4)
                    .addComponent(jLabel3)
                    .addComponent(dtStartDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(dtEndDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel6)
                    .addComponent(jLabel5)
                    .addComponent(dtStartTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(dtEndTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel7)
                    .addComponent(chkSunday)
                    .addComponent(chkMonday)
                    .addComponent(chkTuesday)
                    .addComponent(chkWednesday)
                    .addComponent(chkThursday)
                    .addComponent(chkFriday)
                    .addComponent(chkSaturday))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel8)
                    .addComponent(chkExceptHolidays))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jPanel6.setBorder(javax.swing.BorderFactory.createTitledBorder("Parameter for Reliability Estimation "));

        jLabel1.setText(" Reliability Type :");

        chkModeTimeOfDay.setText("Time of Day Reliability");

        chkModeWholeTime.setText("Whole Time Period Reliability");

        jLabel2.setText("Operating Conditions");

        tblFilters.setModel(new javax.swing.table.DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "", "Name", "Description"
            }
        ) {
            Class[] types = new Class [] {
                java.lang.Boolean.class, java.lang.Object.class, java.lang.String.class
            };
            boolean[] canEdit = new boolean [] {
                true, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types [columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jScrollPane2.setViewportView(tblFilters);
        if (tblFilters.getColumnModel().getColumnCount() > 0) {
            tblFilters.getColumnModel().getColumn(0).setMinWidth(40);
            tblFilters.getColumnModel().getColumn(0).setPreferredWidth(40);
            tblFilters.getColumnModel().getColumn(0).setMaxWidth(40);
            tblFilters.getColumnModel().getColumn(1).setMinWidth(80);
            tblFilters.getColumnModel().getColumn(1).setPreferredWidth(120);
            tblFilters.getColumnModel().getColumn(1).setMaxWidth(600);
        }

        jLabel11.setText("Output Type :");

        chkOutputSpreadsheets.setSelected(true);
        chkOutputSpreadsheets.setText("Spreadsheets");

        chkOutputGraphs.setSelected(true);
        chkOutputGraphs.setText("Graph Images");

        javax.swing.GroupLayout jPanel6Layout = new javax.swing.GroupLayout(jPanel6);
        jPanel6.setLayout(jPanel6Layout);
        jPanel6Layout.setHorizontalGroup(
            jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel6Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane2)
                    .addGroup(jPanel6Layout.createSequentialGroup()
                        .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel2)
                            .addGroup(jPanel6Layout.createSequentialGroup()
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                    .addComponent(jLabel1)
                                    .addComponent(jLabel11))
                                .addGap(18, 18, 18)
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                    .addGroup(jPanel6Layout.createSequentialGroup()
                                        .addComponent(chkModeWholeTime)
                                        .addGap(18, 18, 18)
                                        .addComponent(chkModeTimeOfDay))
                                    .addGroup(jPanel6Layout.createSequentialGroup()
                                        .addComponent(chkOutputSpreadsheets)
                                        .addGap(18, 18, 18)
                                        .addComponent(chkOutputGraphs)))))
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel6Layout.setVerticalGroup(
            jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel6Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel1)
                    .addComponent(chkModeTimeOfDay)
                    .addComponent(chkModeWholeTime))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel11)
                    .addComponent(chkOutputSpreadsheets)
                    .addComponent(chkOutputGraphs))
                .addGap(17, 17, 17)
                .addComponent(jLabel2)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 226, Short.MAX_VALUE)
                .addContainerGap())
        );

        jButton4.setText("Estimate");
        jButton4.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                jButton4ActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel3Layout = new javax.swing.GroupLayout(jPanel3);
        jPanel3.setLayout(jPanel3Layout);
        jPanel3Layout.setHorizontalGroup(
            jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel3Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel4, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jPanel6, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jButton4, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
        jPanel3Layout.setVerticalGroup(
            jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel3Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel4, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jPanel6, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addComponent(jButton4)
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(panMap, javax.swing.GroupLayout.DEFAULT_SIZE, 346, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jPanel3, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(panMap, javax.swing.GroupLayout.DEFAULT_SIZE, 691, Short.MAX_VALUE)
                    .addComponent(jPanel3, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
    }// </editor-fold>//GEN-END:initComponents

    private void jButton4ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_jButton4ActionPerformed
        doEstimate();
    }//GEN-LAST:event_jButton4ActionPerformed

    private void tabRouteSelectionStateChanged(javax.swing.event.ChangeEvent evt) {//GEN-FIRST:event_tabRouteSelectionStateChanged
        onRouteSelectTabChanged();
    }//GEN-LAST:event_tabRouteSelectionStateChanged


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private ticas.common.ui.CorridorSelector cbxCorridor;
    private javax.swing.JComboBox<ReliabilityRouteInfo> cbxRoute;
    private javax.swing.JComboBox<RouteGroupInfo> cbxRouteGroups;
    private javax.swing.JCheckBox chkExceptHolidays;
    private javax.swing.JCheckBox chkFriday;
    private javax.swing.JCheckBox chkModeTimeOfDay;
    private javax.swing.JCheckBox chkModeWholeTime;
    private javax.swing.JCheckBox chkMonday;
    private javax.swing.JCheckBox chkOutputGraphs;
    private javax.swing.JCheckBox chkOutputSpreadsheets;
    private javax.swing.JCheckBox chkSaturday;
    private javax.swing.JCheckBox chkSunday;
    private javax.swing.JCheckBox chkThursday;
    private javax.swing.JCheckBox chkTuesday;
    private javax.swing.JCheckBox chkWednesday;
    private ticas.common.ui.TICASDatePicker dtEndDate;
    private ticas.common.ui.TICASTimePicker dtEndTime;
    private ticas.common.ui.TICASDatePicker dtStartDate;
    private ticas.common.ui.TICASTimePicker dtStartTime;
    private javax.swing.JButton jButton4;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel11;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel6;
    private javax.swing.JPanel jPanel7;
    private javax.swing.JScrollPane jScrollPane2;
    private ticas.common.ui.map.MapPanel panMap;
    private javax.swing.JTabbedPane tabRouteSelection;
    private javax.swing.JTable tblFilters;
    // End of variables declaration//GEN-END:variables

}
