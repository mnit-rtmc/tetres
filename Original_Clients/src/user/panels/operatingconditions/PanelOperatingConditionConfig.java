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
package user.panels.operatingconditions;

import user.TeTRESConfig;

import java.util.ArrayList;
import java.util.List;
import javax.swing.DefaultListModel;
import javax.swing.JOptionPane;
import javax.swing.JTable;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.event.ListSelectionEvent;
import javax.swing.event.ListSelectionListener;
import javax.swing.table.DefaultTableModel;
import user.filters.FilterEditController;
import user.filters.IFilterInfoConverter;
import user.filters.IFilterListChangeListener;
import user.filters.IncidentEditDialog;
import user.filters.SnowmanagementEditDialog;
import user.filters.SpecialEventDialog;
import user.filters.WeatherEditDialog;
import user.filters.WorkzoneEditDialog;
import user.types.FilterInfo;
import user.types.OperatingConditionsInfo;
import user.types.IncidentConditionInfo;
import user.types.SnowmanagementConditionInfo;
import user.types.SpecialeventConditionInfo;
import user.types.WeatherConditionInfo;
import user.types.WorkzoneConditionInfo;
import common.ui.IInitializable;
import java.awt.Color;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.FocusEvent;
import java.awt.event.FocusListener;
import javax.swing.JCheckBox;
import javax.swing.UIManager;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public final class PanelOperatingConditionConfig extends javax.swing.JPanel implements IInitializable {

    private final String NO_CONDITION = "No";
    private final String ANY_CONDITION = "Any";
    private FilterEditController weatherEditor;
    private FilterEditController incidentEditor;
    private FilterEditController workzoneEditor;
    private FilterEditController specialeventEditor;
    private FilterEditController snowmanagementEditor;
    private OperatingConditionsInfo selectedFilterInfoGroup;
    private boolean isChanged = false;

    public abstract class SimpleDocumentListener implements DocumentListener {

        public abstract void update(DocumentEvent e);

        @Override
        public void insertUpdate(DocumentEvent e) {
            update(e);
        }

        @Override
        public void removeUpdate(DocumentEvent e) {
            update(e);
        }

        @Override
        public void changedUpdate(DocumentEvent e) {
            update(e);
        }
    }

    /**
     * Creates new form PanelDataFilters
     */
    public PanelOperatingConditionConfig() {
        initComponents();
    }

    @Override
    public void init() {
        this.weatherEditor = new FilterEditController(new WeatherEditDialog(TeTRESConfig.mainFrame, true),
                this.tblWeather, this.btnAddWeather, this.btnDeleteWeather, this.chkNoWeather, this.chkAnyWeather, new IFilterInfoConverter() {
            @Override
            public List<FilterInfo> getFilterObjects(String[][] data, boolean hasNoCondition, boolean hasAnyCondition) {
                List<FilterInfo> res = new ArrayList<>();
                if (hasNoCondition) {
                    res.add(new WeatherConditionInfo(NO_CONDITION, NO_CONDITION));
                }
                if (hasAnyCondition) {
                    res.add(new WeatherConditionInfo(ANY_CONDITION, ANY_CONDITION));
                }
                for (String[] _data : data) {
                    res.add(new WeatherConditionInfo(_data[0], _data[1]));
                }
                return res;
            }

            @Override
            public void setFilterObjects(JTable table, JCheckBox chkNoCondition, JCheckBox chkAnyCondition, List<FilterInfo> filters) {
                List<WeatherConditionInfo> filterInfos = (List<WeatherConditionInfo>) (List<?>) filters;
                DefaultTableModel model = (DefaultTableModel) table.getModel();
                model.setRowCount(0);
                boolean hasNoCondition = false;
                boolean hasAnyCondition = false;
                for (WeatherConditionInfo fi : filterInfos) {
                    if (fi.type.equals(NO_CONDITION)) {
                        hasNoCondition = true;
                        continue;
                    }
                    if (fi.type.equals(ANY_CONDITION)) {
                        hasAnyCondition = true;
                        continue;
                    }
                    model.addRow(new Object[]{fi.type, fi.intensity});
                }
                chkNoCondition.setSelected(hasNoCondition);
                chkAnyCondition.setSelected(hasAnyCondition);
            }

        });

        this.incidentEditor = new FilterEditController(new IncidentEditDialog(TeTRESConfig.mainFrame, true),
                this.tblIncident, this.btnAddIncident, this.btnDeleteIncident, this.chkNoIncident, this.chkAnyIncident, new IFilterInfoConverter() {
            @Override
            public List<FilterInfo> getFilterObjects(String[][] data, boolean hasNoCondition, boolean hasAnyCondition) {
                List<FilterInfo> res = new ArrayList<>();
                if (hasNoCondition) {
                    res.add(new IncidentConditionInfo(NO_CONDITION, NO_CONDITION, NO_CONDITION));
                }
                if (hasAnyCondition) {
                    res.add(new IncidentConditionInfo(ANY_CONDITION, ANY_CONDITION, ANY_CONDITION));
                }
                for (String[] _data : data) {
                    res.add(new IncidentConditionInfo(_data[0], _data[1], _data[2]));
                }
                return res;
            }

            @Override
            public void setFilterObjects(JTable table, JCheckBox chkNoCondition, JCheckBox chkAnyCondition, List<FilterInfo> filters) {
                List<IncidentConditionInfo> filterInfos = (List<IncidentConditionInfo>) (List<?>) filters;
                DefaultTableModel model = (DefaultTableModel) table.getModel();
                model.setRowCount(0);
                boolean hasNoCondition = false;
                boolean hasAnyCondition = false;
                for (IncidentConditionInfo fi : filterInfos) {
                    if (fi.type.equals(NO_CONDITION)) {
                        hasNoCondition = true;
                        continue;
                    }
                    if (fi.type.equals(ANY_CONDITION)) {
                        hasAnyCondition = true;
                        continue;
                    }
                    model.addRow(new Object[]{fi.type, fi.impact, fi.severity});
                }
                chkNoCondition.setSelected(hasNoCondition);
                chkAnyCondition.setSelected(hasAnyCondition);
            }
        });

        this.workzoneEditor = new FilterEditController(new WorkzoneEditDialog(TeTRESConfig.mainFrame, true),
                this.tblWorkzone, this.btnAddWorkzone, this.btnDeleteWorkzone, this.chkNoWorkzone, this.chkAnyWorkzone, new IFilterInfoConverter() {
            @Override
            public List<FilterInfo> getFilterObjects(String[][] data, boolean hasNoCondition, boolean hasAnyCondition) {
                List<FilterInfo> res = new ArrayList<>();
                if (hasNoCondition) {
                    res.add(new WorkzoneConditionInfo(NO_CONDITION, NO_CONDITION, NO_CONDITION));
                }
                if (hasAnyCondition) {
                    res.add(new WorkzoneConditionInfo(ANY_CONDITION, ANY_CONDITION, ANY_CONDITION));
                }
                for (String[] _data : data) {
                    res.add(new WorkzoneConditionInfo(_data[0], _data[1], _data[2]));
                }
                return res;
            }

            @Override
            public void setFilterObjects(JTable table, JCheckBox chkNoCondition, JCheckBox chkAnyCondition, List<FilterInfo> filters) {
                List<WorkzoneConditionInfo> filterInfos = (List<WorkzoneConditionInfo>) (List<?>) filters;
                DefaultTableModel model = (DefaultTableModel) table.getModel();
                model.setRowCount(0);
                boolean hasNoCondition = false;
                boolean hasAnyCondition = false;
                for (WorkzoneConditionInfo fi : filterInfos) {
                    if (fi.lane_config.equals(NO_CONDITION)) {
                        hasNoCondition = true;
                        continue;
                    }
                    if (fi.lane_config.equals(ANY_CONDITION)) {
                        hasAnyCondition = true;
                        continue;
                    }
                    model.addRow(new Object[]{fi.lane_config, fi.lane_closed_length, fi.relative_location});
                }
                chkNoCondition.setSelected(hasNoCondition);
                chkAnyCondition.setSelected(hasAnyCondition);
            }
        });

        this.specialeventEditor = new FilterEditController(new SpecialEventDialog(TeTRESConfig.mainFrame, true),
                this.tblSpecialevent, this.btnAddSpecialevent, this.btnDeleteSpecialevent, this.chkNoSpeciaevent, this.chkAnySpecialevent, new IFilterInfoConverter() {
            @Override
            public List<FilterInfo> getFilterObjects(String[][] data, boolean hasNoCondition, boolean hasAnyCondition) {
                List<FilterInfo> res = new ArrayList<>();
                if (hasNoCondition) {
                    res.add(new SpecialeventConditionInfo(NO_CONDITION, NO_CONDITION, NO_CONDITION));
                }
                if (hasAnyCondition) {
                    res.add(new SpecialeventConditionInfo(ANY_CONDITION, ANY_CONDITION, ANY_CONDITION));
                }
                for (String[] _data : data) {
                    res.add(new SpecialeventConditionInfo(_data[0], _data[1], _data[2]));
                }
                return res;
            }

            @Override
            public void setFilterObjects(JTable table, JCheckBox chkNoCondition, JCheckBox chkAnyCondition, List<FilterInfo> filters) {
                List<SpecialeventConditionInfo> filterInfos = (List<SpecialeventConditionInfo>) (List<?>) filters;
                DefaultTableModel model = (DefaultTableModel) table.getModel();
                model.setRowCount(0);
                boolean hasNoCondition = false;
                boolean hasAnyCondition = false;
                for (SpecialeventConditionInfo fi : filterInfos) {
                    if (fi.distance.equals(NO_CONDITION)) {
                        hasNoCondition = true;
                        continue;
                    }
                    if (fi.distance.equals(ANY_CONDITION)) {
                        hasAnyCondition = true;
                        continue;
                    }
                    model.addRow(new Object[]{fi.distance, fi.event_size, fi.event_time});
              
                }
                chkNoCondition.setSelected(hasNoCondition);
                chkAnyCondition.setSelected(hasAnyCondition);
            }
        });
//changed the code in the next line by add button and tables
        this.snowmanagementEditor = new FilterEditController(new SnowmanagementEditDialog(TeTRESConfig.mainFrame, true),
                this.tblSnowmgmt,this.btnAddSnowmgmt, this.btnDeleteSnowmgmt, this.chkNoSnowmgmt, this.chkAnySnowmgmt, new IFilterInfoConverter() {
            @Override
            public List<FilterInfo> getFilterObjects(String[][] data, boolean hasNoCondition, boolean hasAnyCondition) {
                List<FilterInfo> res = new ArrayList<>();
                if (hasNoCondition) {
                    res.add(new SnowmanagementConditionInfo(NO_CONDITION));
                }
                if (hasAnyCondition) {
                    res.add(new SnowmanagementConditionInfo(ANY_CONDITION));
                }
                for (String[] _data : data) {
                    res.add(new SnowmanagementConditionInfo(_data[0]));
                }
                return res;
            }

            @Override
            public void setFilterObjects(JTable table, JCheckBox chkNoCondition, JCheckBox chkAnyCondition, List<FilterInfo> filters) {
                List<SnowmanagementConditionInfo> filterInfos = (List<SnowmanagementConditionInfo>) (List<?>) filters;
                boolean hasNoCondition = false;
                boolean hasAnyCondition = false;
                for (SnowmanagementConditionInfo fi : filterInfos) {
                    if (fi.road_condition.equals(NO_CONDITION)) {
                        hasNoCondition = true;
                        continue;
                    }
                    if (fi.road_condition.equals(ANY_CONDITION)) {
                        hasAnyCondition = true;
                        continue;
                    }
                   
                }
                chkNoCondition.setSelected(hasNoCondition);
                chkAnyCondition.setSelected(hasAnyCondition);
            }
        });

        this.listFilters.addListSelectionListener(new ListSelectionListener() {
            @Override
            public void valueChanged(ListSelectionEvent e) {
                if (e.getValueIsAdjusting() == false) {
                    if (listFilters.getSelectedIndex() == -1) {
                    } else {
                        editFilter(listFilters.getSelectedValue());
                    }
                }
            }
        });

        this.setEnableFilterPanel(false);
        this.tbxFilterName.getDocument().addDocumentListener(new SimpleDocumentListener() {
            @Override
            public void update(DocumentEvent e) {
                isChanged = true;
            }
        });
        this.tbxFilterDesc.getDocument().addDocumentListener(new SimpleDocumentListener() {
            @Override
            public void update(DocumentEvent e) {
                isChanged = true;
            }
        });

        OperatingConditionInfoHelper.addChangeListener(new IFilterListChangeListener() {
            @Override
            public void filterGroupUpdated(List<OperatingConditionsInfo> filterGroups) {
                DefaultListModel listModel = new DefaultListModel();
                listModel.removeAllElements();
                for (OperatingConditionsInfo fig : filterGroups) {
                    listModel.addElement(fig);
                }
                listFilters.setModel(listModel);
            }
        });

        FocusListener highlighter = new FocusListener() {
            @Override
            public void focusGained(FocusEvent e) {
                e.getComponent().setBackground(Color.LIGHT_GRAY);
            }

            @Override
            public void focusLost(FocusEvent e) {
                e.getComponent().setBackground(UIManager.getColor("TextField.background"));
            }
        };

        this.tbxFilterName.addFocusListener(highlighter);
        this.tbxFilterDesc.addFocusListener(highlighter);

        OperatingConditionInfoHelper.loadOperatingConditionList();

        this.setNoAnyCheckboxActions();
    }

    @Override
    public void refresh() {
        // do nothing
    }

    private void setNoAnyCheckboxActions() {
        this.chkNoWeather.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                noCheckboxChecked(tblWeather, chkAnyWeather, chkNoWeather);
            }
        });
        this.chkAnyWeather.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                anyCheckboxChecked(tblWeather, chkNoWeather, chkAnyWeather);
            }
        });
        this.chkNoIncident.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                noCheckboxChecked(tblIncident, chkAnyIncident, chkNoIncident);
            }
        });
        this.chkAnyIncident.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                anyCheckboxChecked(tblIncident, chkNoIncident, chkAnyIncident);
            }
        });
        this.chkNoWorkzone.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                noCheckboxChecked(tblWorkzone, chkAnyWorkzone, chkNoWorkzone);
            }
        });
        this.chkAnyWorkzone.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                anyCheckboxChecked(tblWorkzone, chkNoWorkzone, chkAnyWorkzone);
            }
        });
        this.chkNoSpeciaevent.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                noCheckboxChecked(tblSpecialevent, chkAnySpecialevent, chkNoSpeciaevent);
            }
        });
        this.chkAnySpecialevent.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                anyCheckboxChecked(tblSpecialevent, chkNoSpeciaevent, chkAnySpecialevent);
            }
        });
        this.chkNoSnowmgmt.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                noCheckboxChecked(null, chkAnySnowmgmt, chkNoSnowmgmt);
            }
        });
        this.chkAnySnowmgmt.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent ae) {
                anyCheckboxChecked(null, chkNoSnowmgmt, chkAnySnowmgmt);
            }
        });
    }

    private void noCheckboxChecked(JTable table, JCheckBox chkAny, JCheckBox chkNo) {
        if (table != null) {
            DefaultTableModel model = (DefaultTableModel) table.getModel();
            if (model.getRowCount() > 0) {
                if (JOptionPane.showConfirmDialog(this, "The added conditions will be removed.\nDo you want to continue?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
                    chkNo.setSelected(false);
                    return;
                }
            }
            model.setRowCount(0);
        }
        chkAny.setSelected(false);
    }

    private void anyCheckboxChecked(JTable table, JCheckBox chkNo, JCheckBox chkAny) {
        if (table != null) {
            DefaultTableModel model = (DefaultTableModel) table.getModel();
            if (model.getRowCount() > 0) {
                if (JOptionPane.showConfirmDialog(this, "The added conditions will be removed.\nDo you want to continue?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
                    chkAny.setSelected(false);
                    return;
                }
            }
            model.setRowCount(0);
        }
        chkNo.setSelected(false);
    }

    private void deleteFilter() {
        if (JOptionPane.showConfirmDialog(this, "Delete the selected filter?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
            return;
        }
		OperatingConditionInfoHelper.delete(this.selectedFilterInfoGroup);

        this.resetFilterPanel();
        OperatingConditionInfoHelper.loadOperatingConditionList();
    }

    private void copyFilter() {
        if (JOptionPane.showConfirmDialog(this, "Copy the selected filter?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
            return;
        }
        OperatingConditionsInfo clonedFilterGroup = this.selectedFilterInfoGroup.clone();
        clonedFilterGroup.name = clonedFilterGroup.name + " - Copied";
        this.writeFilterGroupInfo(clonedFilterGroup);
        this.resetFilterPanel();
        OperatingConditionInfoHelper.loadOperatingConditionList();
    }

    private void newFilter() {
        if (this.isDirty()) {
            if (JOptionPane.showConfirmDialog(this, "Do you want to make a new filter without saving?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
                return;
            }
        }

        OperatingConditionEditDialog oced = new OperatingConditionEditDialog(TeTRESConfig.mainFrame, true);
        oced.setLocationRelativeTo(TeTRESConfig.mainFrame);
        oced.setVisible(true);

        this.resetFilterPanel();
        this.setEnableFilterPanel(true);

        this.btnFilterDelete.setEnabled(false);
        this.btnFilterCopy.setEnabled(false);
        this.btnFilterSaveOrUpdate.setText("Save");
        this.btnFilterSaveOrUpdate.setEnabled(true);
        this.listFilters.clearSelection();
        this.tbxFilterName.requestFocusInWindow();
    }

    private void editFilter(OperatingConditionsInfo fig) {
        if (fig == this.selectedFilterInfoGroup) {
            return;
        }
        if (this.isDirty()) {
            if (JOptionPane.showConfirmDialog(this, "Do you want to edit the selected filter without saving?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
                this.listFilters.setSelectedValue(this.selectedFilterInfoGroup, true);
                return;
            }
        }
        this.resetFilterPanel();
        this.setEnableFilterPanel(true);

        this.tbxFilterName.setText(fig.name);
        this.tbxFilterDesc.setText(fig.desc);

        this.weatherEditor.setFilter(fig.weather_conditions);
        this.incidentEditor.setFilter(fig.incident_conditions);
        this.workzoneEditor.setFilter(fig.workzone_conditions);
        this.specialeventEditor.setFilter(fig.specialevent_conditions);
        this.snowmanagementEditor.setFilter(fig.snowmanagement_conditions);

        this.selectedFilterInfoGroup = fig;

        this.btnFilterDelete.setEnabled(true);
        this.btnFilterCopy.setEnabled(true);
        this.btnFilterSaveOrUpdate.setText("Update");
        this.btnFilterSaveOrUpdate.setEnabled(true);
        this.isChanged = false;
    }

    private void saveFilter() {
        if (this.tbxFilterName.getText().isEmpty()) {
            JOptionPane.showMessageDialog(this, "Enter filter name");
            return;
        }

		// Filter to write
        OperatingConditionsInfo fig = this.getFilter();
        if (fig.name == null ? this.selectedFilterInfoGroup.name != null : fig.name.equals(this.selectedFilterInfoGroup.name)) {
			OperatingConditionInfoHelper.delete(this.selectedFilterInfoGroup);
        }

        this.resetFilterPanel();
        this.setEnableFilterPanel(false);
		OperatingConditionInfoHelper.save(fig);
        OperatingConditionInfoHelper.loadOperatingConditionList();
    }

    private void writeFilterGroupInfo(OperatingConditionsInfo fig) {
        if (OperatingConditionInfoHelper.exists(fig.name)) {
            if (JOptionPane.showConfirmDialog(this, "The given filter name exists already. Do you want to override?", "Confirm", JOptionPane.YES_NO_OPTION) != JOptionPane.YES_OPTION) {
                return;
            }
        }
		OperatingConditionInfoHelper.save(fig);
        this.resetFilterPanel();
        OperatingConditionInfoHelper.loadOperatingConditionList();
    }

    private OperatingConditionsInfo getFilter() {
        OperatingConditionsInfo fig = new OperatingConditionsInfo();
        fig.name = this.tbxFilterName.getText().trim();
        
        fig.desc = this.tbxFilterDesc.getText().trim();
        fig.weather_conditions = this.weatherEditor.getFilterObjects();
        fig.incident_conditions = this.incidentEditor.getFilterObjects();
        fig.workzone_conditions = this.workzoneEditor.getFilterObjects();
        fig.specialevent_conditions = this.specialeventEditor.getFilterObjects();
        fig.snowmanagement_conditions = this.snowmanagementEditor.getFilterObjects();
        return fig;
    }

    private void resetFilterPanel() {
        this.btnFilterDelete.setEnabled(false);
        this.btnFilterCopy.setEnabled(false);
        this.tbxFilterName.setText("");
        this.tbxFilterDesc.setText("");
        this.weatherEditor.reset();
        this.incidentEditor.reset();
        this.workzoneEditor.reset();
        this.specialeventEditor.reset();
        this.snowmanagementEditor.reset();
        this.isChanged = false;
        this.selectedFilterInfoGroup = null;
    }

    private boolean isDirty() {
        return (this.weatherEditor.isDirty()
                || this.incidentEditor.isDirty()
                || this.workzoneEditor.isDirty()
                || this.specialeventEditor.isDirty()
                || this.snowmanagementEditor.isDirty()
                || this.isChanged);
    }

    private void setEnableFilterPanel(boolean v) {
        this.tbxFilterName.setEnabled(v);
        this.tbxFilterDesc.setEnabled(v);
        this.weatherEditor.setEnabled(v);
        this.incidentEditor.setEnabled(v);
        this.workzoneEditor.setEnabled(v);
        this.specialeventEditor.setEnabled(v);
        this.snowmanagementEditor.setEnabled(v);
        this.btnFilterSaveOrUpdate.setEnabled(v);
        if (!v) {
            this.btnFilterSaveOrUpdate.setText("Save or Update");
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

        jPanel7 = new javax.swing.JPanel();
        jLabel9 = new javax.swing.JLabel();
        btnFilterAdd = new javax.swing.JButton();
        jScrollPane1 = new javax.swing.JScrollPane();
        listFilters = new javax.swing.JList<>();
        btnFilterDelete = new javax.swing.JButton();
        btnFilterCopy = new javax.swing.JButton();
        jPanel8 = new javax.swing.JPanel();
        jLabel10 = new javax.swing.JLabel();
        tbxFilterName = new javax.swing.JTextField();
        jLabel11 = new javax.swing.JLabel();
        jScrollPane3 = new javax.swing.JScrollPane();
        tbxFilterDesc = new javax.swing.JTextArea();
        tabSubFilters = new javax.swing.JTabbedPane();
        jPanel10 = new javax.swing.JPanel();
        jScrollPane7 = new javax.swing.JScrollPane();
        tblWeather = new JTable();
        btnDeleteWeather = new javax.swing.JButton();
        btnAddWeather = new javax.swing.JButton();
        chkNoWeather = new JCheckBox();
        chkAnyWeather = new JCheckBox();
        jPanel11 = new javax.swing.JPanel();
        jScrollPane5 = new javax.swing.JScrollPane();
        tblIncident = new JTable();
        btnAddIncident = new javax.swing.JButton();
        btnDeleteIncident = new javax.swing.JButton();
        chkNoIncident = new JCheckBox();
        chkAnyIncident = new JCheckBox();
        jPanel12 = new javax.swing.JPanel();
        jScrollPane8 = new javax.swing.JScrollPane();
        tblWorkzone = new JTable();
        btnAddWorkzone = new javax.swing.JButton();
        btnDeleteWorkzone = new javax.swing.JButton();
        chkNoWorkzone = new JCheckBox();
        chkAnyWorkzone = new JCheckBox();
        jPanel13 = new javax.swing.JPanel();
        jScrollPane9 = new javax.swing.JScrollPane();
        tblSpecialevent = new JTable();
        btnAddSpecialevent = new javax.swing.JButton();
        btnDeleteSpecialevent = new javax.swing.JButton();
        chkAnySpecialevent = new JCheckBox();
        chkNoSpeciaevent = new JCheckBox();
        jPanel14 = new javax.swing.JPanel();
        chkNoSnowmgmt = new JCheckBox();
        chkAnySnowmgmt = new JCheckBox();
        jScrollPane2 = new javax.swing.JScrollPane();
        tblSnowmgmt = new JTable();
        btnAddSnowmgmt = new javax.swing.JButton();
        btnDeleteSnowmgmt = new javax.swing.JButton();
        btnFilterSaveOrUpdate = new javax.swing.JButton();

        jLabel9.setText("List of Defined Operating Conditions");

        btnFilterAdd.setText("+");
        btnFilterAdd.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                btnFilterAddActionPerformed(evt);
            }
        });

        jScrollPane1.setViewportView(listFilters);

        btnFilterDelete.setText("Delete");
        btnFilterDelete.setEnabled(false);
        btnFilterDelete.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                btnFilterDeleteActionPerformed(evt);
            }
        });

        btnFilterCopy.setText("Copy");
        btnFilterCopy.setEnabled(false);
        btnFilterCopy.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                btnFilterCopyActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel7Layout = new javax.swing.GroupLayout(jPanel7);
        jPanel7.setLayout(jPanel7Layout);
        jPanel7Layout.setHorizontalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1)
                    .addGroup(jPanel7Layout.createSequentialGroup()
                        .addComponent(jLabel9)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(btnFilterAdd))
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel7Layout.createSequentialGroup()
                        .addComponent(btnFilterCopy)
                        .addGap(18, 18, 18)
                        .addComponent(btnFilterDelete, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel7Layout.setVerticalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel9)
                    .addComponent(btnFilterAdd))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jScrollPane1)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnFilterDelete)
                    .addComponent(btnFilterCopy))
                .addContainerGap())
        );

        jLabel10.setText("Name");

        tbxFilterName.setEnabled(false);

        jLabel11.setText("Description");

        tbxFilterDesc.setColumns(20);
        tbxFilterDesc.setRows(5);
        tbxFilterDesc.setEnabled(false);
        jScrollPane3.setViewportView(tbxFilterDesc);

        tblWeather.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Type", "Intensity"
            }
        ) {
            Class[] types = new Class [] {
                String.class, String.class
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
        jScrollPane7.setViewportView(tblWeather);
        if (tblWeather.getColumnModel().getColumnCount() > 0) {
            tblWeather.getColumnModel().getColumn(0).setMinWidth(80);
            tblWeather.getColumnModel().getColumn(0).setPreferredWidth(80);
            tblWeather.getColumnModel().getColumn(0).setMaxWidth(160);
        }

        btnDeleteWeather.setText("Delete Condition");

        btnAddWeather.setText("Add Condition");

        chkNoWeather.setText("Normal dry day");

        chkAnyWeather.setText("Non-dry day");

        javax.swing.GroupLayout jPanel10Layout = new javax.swing.GroupLayout(jPanel10);
        jPanel10.setLayout(jPanel10Layout);
        jPanel10Layout.setHorizontalGroup(
            jPanel10Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel10Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel10Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane7, javax.swing.GroupLayout.DEFAULT_SIZE, 721, Short.MAX_VALUE)
                    .addGroup(jPanel10Layout.createSequentialGroup()
                        .addComponent(btnAddWeather, javax.swing.GroupLayout.PREFERRED_SIZE, 105, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnDeleteWeather)
                        .addGap(18, 18, 18)
                        .addComponent(chkNoWeather)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(chkAnyWeather)
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel10Layout.setVerticalGroup(
            jPanel10Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel10Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel10Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnAddWeather)
                    .addComponent(btnDeleteWeather)
                    .addComponent(chkNoWeather)
                    .addComponent(chkAnyWeather))
                .addGap(11, 11, 11)
                .addComponent(jScrollPane7, javax.swing.GroupLayout.DEFAULT_SIZE, 167, Short.MAX_VALUE)
                .addContainerGap())
        );

        tabSubFilters.addTab("Weather", jPanel10);

        tblIncident.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Type", "Impact", "Severity"
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
        jScrollPane5.setViewportView(tblIncident);
        if (tblIncident.getColumnModel().getColumnCount() > 0) {
            tblIncident.getColumnModel().getColumn(0).setMinWidth(80);
            tblIncident.getColumnModel().getColumn(0).setPreferredWidth(80);
            tblIncident.getColumnModel().getColumn(0).setMaxWidth(160);
            tblIncident.getColumnModel().getColumn(1).setMinWidth(100);
            tblIncident.getColumnModel().getColumn(1).setPreferredWidth(100);
            tblIncident.getColumnModel().getColumn(1).setMaxWidth(160);
        }

        btnAddIncident.setText("Add Condition");

        btnDeleteIncident.setText("Delete Condition");

        chkNoIncident.setText("Without any incident");

        chkAnyIncident.setText("With incident");

        javax.swing.GroupLayout jPanel11Layout = new javax.swing.GroupLayout(jPanel11);
        jPanel11.setLayout(jPanel11Layout);
        jPanel11Layout.setHorizontalGroup(
            jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel11Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane5, javax.swing.GroupLayout.DEFAULT_SIZE, 721, Short.MAX_VALUE)
                    .addGroup(jPanel11Layout.createSequentialGroup()
                        .addComponent(btnAddIncident, javax.swing.GroupLayout.PREFERRED_SIZE, 105, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnDeleteIncident)
                        .addGap(18, 18, 18)
                        .addComponent(chkNoIncident)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(chkAnyIncident)
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel11Layout.setVerticalGroup(
            jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel11Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(chkNoIncident)
                        .addComponent(chkAnyIncident))
                    .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(btnAddIncident)
                        .addComponent(btnDeleteIncident)))
                .addGap(11, 11, 11)
                .addComponent(jScrollPane5, javax.swing.GroupLayout.DEFAULT_SIZE, 167, Short.MAX_VALUE)
                .addContainerGap())
        );

        tabSubFilters.addTab("Incident", jPanel11);

        tblWorkzone.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Lane Config", "Lane Closed Length", "Relative Location"
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
        jScrollPane8.setViewportView(tblWorkzone);
        if (tblWorkzone.getColumnModel().getColumnCount() > 0) {
            tblWorkzone.getColumnModel().getColumn(0).setMinWidth(80);
            tblWorkzone.getColumnModel().getColumn(0).setPreferredWidth(80);
            tblWorkzone.getColumnModel().getColumn(0).setMaxWidth(160);
            tblWorkzone.getColumnModel().getColumn(1).setMinWidth(120);
            tblWorkzone.getColumnModel().getColumn(1).setPreferredWidth(120);
            tblWorkzone.getColumnModel().getColumn(1).setMaxWidth(200);
        }

        btnAddWorkzone.setText("Add Condition");

        btnDeleteWorkzone.setText("Delete Condition");

        chkNoWorkzone.setText("Without any workzone");

        chkAnyWorkzone.setText("With workzone");

        javax.swing.GroupLayout jPanel12Layout = new javax.swing.GroupLayout(jPanel12);
        jPanel12.setLayout(jPanel12Layout);
        jPanel12Layout.setHorizontalGroup(
            jPanel12Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel12Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel12Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane8, javax.swing.GroupLayout.DEFAULT_SIZE, 721, Short.MAX_VALUE)
                    .addGroup(jPanel12Layout.createSequentialGroup()
                        .addComponent(btnAddWorkzone, javax.swing.GroupLayout.PREFERRED_SIZE, 105, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnDeleteWorkzone)
                        .addGap(18, 18, 18)
                        .addComponent(chkNoWorkzone)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(chkAnyWorkzone)
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel12Layout.setVerticalGroup(
            jPanel12Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel12Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel12Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel12Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(chkNoWorkzone)
                        .addComponent(chkAnyWorkzone))
                    .addGroup(jPanel12Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(btnAddWorkzone)
                        .addComponent(btnDeleteWorkzone)))
                .addGap(11, 11, 11)
                .addComponent(jScrollPane8, javax.swing.GroupLayout.DEFAULT_SIZE, 167, Short.MAX_VALUE)
                .addContainerGap())
        );

        tabSubFilters.addTab("Workzone", jPanel12);

        tblSpecialevent.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Distance", "Event Size", "Event Time"
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
        jScrollPane9.setViewportView(tblSpecialevent);
        if (tblSpecialevent.getColumnModel().getColumnCount() > 0) {
            tblSpecialevent.getColumnModel().getColumn(0).setMinWidth(80);
            tblSpecialevent.getColumnModel().getColumn(0).setPreferredWidth(80);
            tblSpecialevent.getColumnModel().getColumn(0).setMaxWidth(160);
            tblSpecialevent.getColumnModel().getColumn(1).setMinWidth(80);
            tblSpecialevent.getColumnModel().getColumn(1).setPreferredWidth(80);
            tblSpecialevent.getColumnModel().getColumn(1).setMaxWidth(160);
        }

        btnAddSpecialevent.setText("Add Condition");

        btnDeleteSpecialevent.setText("Delete Condition");

        chkAnySpecialevent.setText("With special event");

        chkNoSpeciaevent.setText("Without any special event");

        javax.swing.GroupLayout jPanel13Layout = new javax.swing.GroupLayout(jPanel13);
        jPanel13.setLayout(jPanel13Layout);
        jPanel13Layout.setHorizontalGroup(
            jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel13Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane9)
                    .addGroup(jPanel13Layout.createSequentialGroup()
                        .addComponent(btnAddSpecialevent, javax.swing.GroupLayout.PREFERRED_SIZE, 105, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnDeleteSpecialevent)
                        .addGap(18, 18, 18)
                        .addComponent(chkNoSpeciaevent)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(chkAnySpecialevent)
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel13Layout.setVerticalGroup(
            jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel13Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(chkNoSpeciaevent)
                        .addComponent(chkAnySpecialevent))
                    .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(btnAddSpecialevent)
                        .addComponent(btnDeleteSpecialevent)))
                .addGap(11, 11, 11)
                .addComponent(jScrollPane9, javax.swing.GroupLayout.DEFAULT_SIZE, 167, Short.MAX_VALUE)
                .addContainerGap())
        );

        tabSubFilters.addTab("Special Event", jPanel13);

        chkNoSnowmgmt.setText("Lane lost time only");
        chkNoSnowmgmt.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                chkNoSnowmgmtActionPerformed(evt);
            }
        });

        chkAnySnowmgmt.setText("Not including lane lost time");
        chkAnySnowmgmt.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                chkAnySnowmgmtActionPerformed(evt);
            }
        });

        tblSnowmgmt.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Road Condition"
            }
        ));
        jScrollPane2.setViewportView(tblSnowmgmt);

        btnAddSnowmgmt.setText("Add Condition");

        btnDeleteSnowmgmt.setText("Delete Condition");

        javax.swing.GroupLayout jPanel14Layout = new javax.swing.GroupLayout(jPanel14);
        jPanel14.setLayout(jPanel14Layout);
        jPanel14Layout.setHorizontalGroup(
            jPanel14Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel14Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(btnAddSnowmgmt, javax.swing.GroupLayout.PREFERRED_SIZE, 101, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(btnDeleteSnowmgmt)
                .addGap(18, 18, 18)
                .addComponent(chkNoSnowmgmt)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(chkAnySnowmgmt)
                .addGap(0, 0, 0))
            .addGroup(jPanel14Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jScrollPane2)
                .addContainerGap())
        );
        jPanel14Layout.setVerticalGroup(
            jPanel14Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel14Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel14Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnAddSnowmgmt)
                    .addComponent(btnDeleteSnowmgmt)
                    .addComponent(chkNoSnowmgmt)
                    .addComponent(chkAnySnowmgmt))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane2, javax.swing.GroupLayout.DEFAULT_SIZE, 169, Short.MAX_VALUE)
                .addContainerGap())
        );

        tabSubFilters.addTab("Lane Condition during Snow Event", jPanel14);

        btnFilterSaveOrUpdate.setText("Save or Update");
        btnFilterSaveOrUpdate.setEnabled(false);
        btnFilterSaveOrUpdate.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                btnFilterSaveOrUpdateActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel8Layout = new javax.swing.GroupLayout(jPanel8);
        jPanel8.setLayout(jPanel8Layout);
        jPanel8Layout.setHorizontalGroup(
            jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel8Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(tabSubFilters)
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanel8Layout.createSequentialGroup()
                        .addComponent(jLabel10)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(tbxFilterName))
                    .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanel8Layout.createSequentialGroup()
                        .addComponent(jLabel11)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(jScrollPane3))
                    .addComponent(btnFilterSaveOrUpdate, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addGap(19, 19, 19))
        );
        jPanel8Layout.setVerticalGroup(
            jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel8Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel10)
                    .addComponent(tbxFilterName, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel11)
                    .addComponent(jScrollPane3, javax.swing.GroupLayout.PREFERRED_SIZE, 67, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addComponent(tabSubFilters)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(btnFilterSaveOrUpdate)
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel7, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jPanel8, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel7, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jPanel8, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                .addContainerGap())
        );
    }private void btnFilterSaveOrUpdateActionPerformed(ActionEvent evt) {
        this.saveFilter();
    }

    private void btnFilterAddActionPerformed(ActionEvent evt) {
        this.newFilter();
    }

    private void btnFilterDeleteActionPerformed(ActionEvent evt) {
        this.deleteFilter();
    }

    private void btnFilterCopyActionPerformed(ActionEvent evt) {
        this.copyFilter();
    }

    private void chkNoSnowmgmtActionPerformed(ActionEvent evt) {
        // TODO add your handling code here:
    }

    private void chkAnySnowmgmtActionPerformed(ActionEvent evt) {
        // TODO add your handling code here:
    }


    // Variables declaration - do not modify
    private javax.swing.JButton btnAddIncident;
    private javax.swing.JButton btnAddSnowmgmt;
    private javax.swing.JButton btnAddSpecialevent;
    private javax.swing.JButton btnAddWeather;
    private javax.swing.JButton btnAddWorkzone;
    private javax.swing.JButton btnDeleteIncident;
    private javax.swing.JButton btnDeleteSnowmgmt;
    private javax.swing.JButton btnDeleteSpecialevent;
    private javax.swing.JButton btnDeleteWeather;
    private javax.swing.JButton btnDeleteWorkzone;
    private javax.swing.JButton btnFilterAdd;
    private javax.swing.JButton btnFilterCopy;
    private javax.swing.JButton btnFilterDelete;
    private javax.swing.JButton btnFilterSaveOrUpdate;
    private JCheckBox chkAnyIncident;
    private JCheckBox chkAnySnowmgmt;
    private JCheckBox chkAnySpecialevent;
    private JCheckBox chkAnyWeather;
    private JCheckBox chkAnyWorkzone;
    private JCheckBox chkNoIncident;
    private JCheckBox chkNoSnowmgmt;
    private JCheckBox chkNoSpeciaevent;
    private JCheckBox chkNoWeather;
    private JCheckBox chkNoWorkzone;
    private javax.swing.JLabel jLabel10;
    private javax.swing.JLabel jLabel11;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JPanel jPanel10;
    private javax.swing.JPanel jPanel11;
    private javax.swing.JPanel jPanel12;
    private javax.swing.JPanel jPanel13;
    private javax.swing.JPanel jPanel14;
    private javax.swing.JPanel jPanel7;
    private javax.swing.JPanel jPanel8;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JScrollPane jScrollPane2;
    private javax.swing.JScrollPane jScrollPane3;
    private javax.swing.JScrollPane jScrollPane5;
    private javax.swing.JScrollPane jScrollPane7;
    private javax.swing.JScrollPane jScrollPane8;
    private javax.swing.JScrollPane jScrollPane9;
    private javax.swing.JList<user.types.OperatingConditionsInfo> listFilters;
    private javax.swing.JTabbedPane tabSubFilters;
    private JTable tblIncident;
    private JTable tblSnowmgmt;
    private JTable tblSpecialevent;
    private JTable tblWeather;
    private JTable tblWorkzone;
    private javax.swing.JTextArea tbxFilterDesc;
    private javax.swing.JTextField tbxFilterName;
    // End of variables declaration

}
