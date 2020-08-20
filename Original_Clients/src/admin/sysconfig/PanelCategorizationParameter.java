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
package admin.sysconfig;

import admin.types.SystemConfigInfo;
import common.ui.TICASTimePicker;
import common.util.FormHelper;

import javax.swing.*;
import java.sql.Time;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.logging.Level;
import java.util.logging.Logger;
import java.util.ArrayList;
import java.util.List;
import java.util.Date;
import admin.api.ReliabilityRouteClient;
import admin.api.RouteWiseMOEParameterClient;
import admin.types.ReliabilityRouteInfo;
import admin.types.RouteWiseMOEParameterInfo;
import javax.swing.table.DefaultTableModel;
import java.util.HashMap;
import java.util.Map;
/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class PanelCategorizationParameter extends javax.swing.JPanel {

    /**
     * Creates new form PanelPeriodicJobSeting
     */
    private ReliabilityRouteClient model;
    private RouteWiseMOEParameterClient modelMOE;

    private List<ReliabilityRouteInfo> routeList = new ArrayList<>();

    public PanelCategorizationParameter() {
        initComponents();
        this.init();
    }

    private void init() {

        FormHelper.setDoubleFilter(this.tbxINCDownstreamDistanceLimit.getDocument(), false);
        FormHelper.setDoubleFilter(this.tbxINCUpstreamDistanceLimit.getDocument(), false);

        FormHelper.setDoubleFilter(this.tbxWZDownstreamDistanceLimit.getDocument(), false);
        FormHelper.setDoubleFilter(this.tbxWZUpstreamDistanceLimit.getDocument(), false);

        FormHelper.setIntegerFilter(this.tbxSEArrialWindow.getDocument(), false);
        FormHelper.setIntegerFilter(this.tbxSEDepartureWindow1.getDocument(), false);
        FormHelper.setIntegerFilter(this.tbxSEDepartureWindow2.getDocument(), false);
    }

    public void updateSettingInUI(SystemConfigInfo cfg) {
        this.tbxINCDownstreamDistanceLimit.setText(cfg.incident_downstream_distance_limit.toString());
        this.tbxINCUpstreamDistanceLimit.setText(cfg.incident_upstream_distance_limit.toString());
        this.tbxWZDownstreamDistanceLimit.setText(cfg.workzone_downstream_distance_limit.toString());
        this.tbxWZUpstreamDistanceLimit.setText(cfg.workzone_upstream_distance_limit.toString());
        this.tbxSEArrialWindow.setText(cfg.specialevent_arrival_window.toString());
        this.tbxSEDepartureWindow1.setText(cfg.specialevent_departure_window1.toString());
        this.tbxSEDepartureWindow2.setText(cfg.specialevent_departure_window2.toString());

        // faverolles 1/12/2020: Adding MOE Configuration Parameters
        this.moeTextFieldCD.setText(cfg.moe_critical_density.toString());
        this.moeTextFieldLC.setText(cfg.moe_lane_capacity.toString());
        this.moeTextFieldCTS.setText(cfg.moe_congestion_threshold_speed.toString());

        this.RWmoeTextFieldCD.setText(cfg.moe_critical_density.toString());
        this.RWmoeTextFieldLC.setText(cfg.moe_lane_capacity.toString());
        this.RWmoeTextFieldCTS.setText(cfg.moe_congestion_threshold_speed.toString());
        Map <Integer, ReliabilityRouteInfo> idVsRouteMap = new HashMap<Integer, ReliabilityRouteInfo>();
        this.model = new ReliabilityRouteClient();
        this.model.list();
        this.routeList = this.model.dataList;
        for (ReliabilityRouteInfo r : this.routeList) {
            this.selectRoute.addItem(r.toString());
            idVsRouteMap.put(r.id, r);
        }
        this.modelMOE = new RouteWiseMOEParameterClient();
        this.modelMOE.list();
        DefaultTableModel model = (DefaultTableModel) this.RWMOETable.getModel();
        model.setRowCount(0);
        for (RouteWiseMOEParameterInfo r: this.modelMOE.dataList){
            if (idVsRouteMap.get(r.reference_tt_route_id) != null){
                model.addRow(new Object[]{ idVsRouteMap.get(r.reference_tt_route_id).name, r.moe_critical_density, r.moe_lane_capacity, r.moe_congestion_threshold_speed, r.start_time, r.end_time, r.update_time, r.status, r.reason});

            }
        }

    }


    void fillSystemConfigInfo(SystemConfigInfo newSysConfig) {
        newSysConfig.incident_downstream_distance_limit = Float.parseFloat(this.tbxINCDownstreamDistanceLimit.getText());
        newSysConfig.incident_upstream_distance_limit = Float.parseFloat(this.tbxINCUpstreamDistanceLimit.getText());
        newSysConfig.workzone_downstream_distance_limit = Float.parseFloat(this.tbxWZDownstreamDistanceLimit.getText());
        newSysConfig.workzone_upstream_distance_limit = Float.parseFloat(this.tbxWZUpstreamDistanceLimit.getText());
        newSysConfig.specialevent_arrival_window = Integer.parseInt(this.tbxSEArrialWindow.getText());
        newSysConfig.specialevent_departure_window1 = Integer.parseInt(this.tbxSEDepartureWindow1.getText());
        newSysConfig.specialevent_departure_window2 = Integer.parseInt(this.tbxSEDepartureWindow2.getText());

        // faverolles 1/12/2020: Adding MOE Configuration Parameters
        newSysConfig.moe_critical_density = Float.parseFloat(this.moeTextFieldCD.getText());
        newSysConfig.moe_lane_capacity = Float.parseFloat(this.moeTextFieldLC.getText());
        newSysConfig.moe_congestion_threshold_speed = Float.parseFloat(this.moeTextFieldCTS.getText());

        int selectedRouteIndex = this.selectRoute.getSelectedIndex();
        if (selectedRouteIndex == 0) {
            newSysConfig.reference_tt_route_id = 0;
        } else {
            selectedRouteIndex--;
            ReliabilityRouteInfo selectedRoute = this.routeList.get(selectedRouteIndex);
            newSysConfig.reference_tt_route_id = selectedRoute.id;
        }
        newSysConfig.rw_moe_critical_density = Float.parseFloat(this.RWmoeTextFieldCD.getText());
        newSysConfig.rw_moe_lane_capacity = Float.parseFloat(this.RWmoeTextFieldLC.getText());
        newSysConfig.rw_moe_congestion_threshold_speed = Float.parseFloat(this.RWmoeTextFieldCTS.getText());
        newSysConfig.rw_moe_start_date = this.getDateString(this.startDate.getDate());
        newSysConfig.rw_moe_end_date = this.getDateString(this.endDate.getDate());

    }

    private String getDateString(Date date) {
        String dateString = "";
        if (date != null){
            DateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
            dateString = sdf.format(date);

        }
        return dateString;

    }

    private void setTime(TICASTimePicker timePicker, String timestring) {
        try {
            DateFormat sdf = new SimpleDateFormat("hh:mm");
            Time time = new Time(sdf.parse(timestring).getTime());
            timePicker.setTimeObject(time);
        } catch (ParseException ex) {
            Logger.getLogger(PanelPeriodicJobSeting.class.getName()).log(Level.SEVERE, null, ex);
        }
    }

    private void setCombobox(JComboBox comboBox, Object value) {
        ComboBoxModel model = comboBox.getModel();
        int size = model.getSize();
        String objStr = value.toString();
        for (int i = 0; i < size; i++) {
            Object element = model.getElementAt(i);
            if (element.toString().equals(objStr)) {
                comboBox.setSelectedIndex(i);
                return;
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

        jTabbedPane1 = new javax.swing.JTabbedPane();
        jPanel2 = new javax.swing.JPanel();
        jPanel13 = new javax.swing.JPanel();
        jLabel25 = new javax.swing.JLabel();
        tbxINCDownstreamDistanceLimit = new javax.swing.JTextField();
        jLabel26 = new javax.swing.JLabel();
        jLabel28 = new javax.swing.JLabel();
        tbxINCUpstreamDistanceLimit = new javax.swing.JTextField();
        jLabel29 = new javax.swing.JLabel();
        jPanel3 = new javax.swing.JPanel();
        jPanel11 = new javax.swing.JPanel();
        jLabel1 = new javax.swing.JLabel();
        tbxWZDownstreamDistanceLimit = new javax.swing.JTextField();
        jLabel14 = new javax.swing.JLabel();
        jLabel4 = new javax.swing.JLabel();
        tbxWZUpstreamDistanceLimit = new javax.swing.JTextField();
        jLabel15 = new javax.swing.JLabel();
        jPanel4 = new javax.swing.JPanel();
        jPanel9 = new javax.swing.JPanel();
        jLabel46 = new javax.swing.JLabel();
        tbxSEArrialWindow = new javax.swing.JTextField();
        jLabel47 = new javax.swing.JLabel();
        jLabel55 = new javax.swing.JLabel();
        jLabel48 = new javax.swing.JLabel();
        tbxSEDepartureWindow1 = new javax.swing.JTextField();
        jLabel49 = new javax.swing.JLabel();
        jLabel56 = new javax.swing.JLabel();
        jLabel57 = new javax.swing.JLabel();
        jLabel51 = new javax.swing.JLabel();
        tbxSEDepartureWindow2 = new javax.swing.JTextField();
        jLabel52 = new javax.swing.JLabel();
        jLabel58 = new javax.swing.JLabel();
        jLabel59 = new javax.swing.JLabel();
        jTabbedPane2 = new javax.swing.JTabbedPane();
        jPanel1 = new javax.swing.JPanel();
        jPanel6 = new javax.swing.JPanel();
        moeLabelCD = new javax.swing.JLabel();
        moeLabelLC = new javax.swing.JLabel();
        moeLabelCTS = new javax.swing.JLabel();
        moeTextFieldCD = new javax.swing.JTextField();
        moeTextFieldLC = new javax.swing.JTextField();
        moeTextFieldCTS = new javax.swing.JTextField();
        moeLabelCD1 = new javax.swing.JLabel();
        moeLabelLC1 = new javax.swing.JLabel();
        moeLabelCTS1 = new javax.swing.JLabel();
        jPanel5 = new javax.swing.JPanel();
        jPanel7 = new javax.swing.JPanel();
        moeLabelCD2 = new javax.swing.JLabel();
        moeLabelLC2 = new javax.swing.JLabel();
        moeLabelCTS2 = new javax.swing.JLabel();
        RWmoeTextFieldCD = new javax.swing.JTextField();
        RWmoeTextFieldLC = new javax.swing.JTextField();
        RWmoeTextFieldCTS = new javax.swing.JTextField();
        moeLabelCD3 = new javax.swing.JLabel();
        moeLabelLC3 = new javax.swing.JLabel();
        moeLabelCTS3 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        selectRoute = new javax.swing.JComboBox<String>();
        jLabel3 = new javax.swing.JLabel();
        jLabel5 = new javax.swing.JLabel();
        startDate = new org.jdesktop.swingx.JXDatePicker();
        endDate = new org.jdesktop.swingx.JXDatePicker();
        jScrollPane1 = new javax.swing.JScrollPane();
        RWMOETable = new javax.swing.JTable();

        jPanel13.setBorder(javax.swing.BorderFactory.createTitledBorder("Maximum distance affected by an incident"));

        jLabel25.setText("Maximum distance from downstream boundary of a given route :");

        jLabel26.setText("mile");

        jLabel28.setText("Maximum distance from upstream boundary of a given route :");

        jLabel29.setText("mile");

        javax.swing.GroupLayout jPanel13Layout = new javax.swing.GroupLayout(jPanel13);
        jPanel13.setLayout(jPanel13Layout);
        jPanel13Layout.setHorizontalGroup(
                jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel13Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addComponent(jLabel25)
                                        .addComponent(jLabel28))
                                .addGap(18, 18, 18)
                                .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel13Layout.createSequentialGroup()
                                                .addComponent(tbxINCDownstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, 50, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel26))
                                        .addGroup(jPanel13Layout.createSequentialGroup()
                                                .addComponent(tbxINCUpstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, 50, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel29)))
                                .addContainerGap(494, Short.MAX_VALUE))
        );
        jPanel13Layout.setVerticalGroup(
                jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel13Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel25)
                                        .addComponent(tbxINCDownstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel26))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(jPanel13Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel28)
                                        .addComponent(tbxINCUpstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel29))
                                .addContainerGap(54, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
                jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel2Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel13, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
                jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel2Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel13, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(349, Short.MAX_VALUE))
        );

        jTabbedPane1.addTab("Incident", jPanel2);

        jPanel11.setBorder(javax.swing.BorderFactory.createTitledBorder("Maximum distance affected by a work zone"));

        jLabel1.setText("Maximum distance from downstream boundary of a given route :");

        jLabel14.setText("mile");

        jLabel4.setText("Maximum distance from upstream boundary of a given route :");

        jLabel15.setText("mile");

        javax.swing.GroupLayout jPanel11Layout = new javax.swing.GroupLayout(jPanel11);
        jPanel11.setLayout(jPanel11Layout);
        jPanel11Layout.setHorizontalGroup(
                jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel11Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addComponent(jLabel1)
                                        .addComponent(jLabel4))
                                .addGap(18, 18, 18)
                                .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel11Layout.createSequentialGroup()
                                                .addComponent(tbxWZDownstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, 50, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel14))
                                        .addGroup(jPanel11Layout.createSequentialGroup()
                                                .addComponent(tbxWZUpstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, 50, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel15)))
                                .addContainerGap(494, Short.MAX_VALUE))
        );
        jPanel11Layout.setVerticalGroup(
                jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel11Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel1)
                                        .addComponent(tbxWZDownstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel14))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(jPanel11Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel4)
                                        .addComponent(tbxWZUpstreamDistanceLimit, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel15))
                                .addContainerGap(32, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout jPanel3Layout = new javax.swing.GroupLayout(jPanel3);
        jPanel3.setLayout(jPanel3Layout);
        jPanel3Layout.setHorizontalGroup(
                jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel3Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel11, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addContainerGap())
        );
        jPanel3Layout.setVerticalGroup(
                jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel3Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel11, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(371, Short.MAX_VALUE))
        );

        jTabbedPane1.addTab("Workzone", jPanel3);

        jPanel9.setBorder(javax.swing.BorderFactory.createTitledBorder("Time Window Parameter"));

        jLabel46.setText("- Arrival Window:");

        jLabel47.setText("minutes");

        jLabel55.setText("* Travel time data from (event_start_time - arrival_window) to event_start_time");

        jLabel48.setText("- Departure Window1:");

        jLabel49.setText("minutes");

        jLabel56.setText("* Travel time data from (event_start_time + departure_window_1)");

        jLabel57.setText("to (event_start_time + departure_window_1 + departure_window_2)");

        jLabel51.setText("- Departure Window2:");

        jLabel52.setText("minutes");

        jLabel58.setText("are categorized 'Departure' type");

        jLabel59.setText("   are categorized 'Arrival' type");

        javax.swing.GroupLayout jPanel9Layout = new javax.swing.GroupLayout(jPanel9);
        jPanel9.setLayout(jPanel9Layout);
        jPanel9Layout.setHorizontalGroup(
                jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel9Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addComponent(jLabel46)
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addComponent(jLabel48)
                                                .addGap(18, 18, 18)
                                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                .addComponent(tbxSEDepartureWindow1, javax.swing.GroupLayout.PREFERRED_SIZE, 51, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                                .addComponent(jLabel49))
                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                .addComponent(tbxSEArrialWindow, javax.swing.GroupLayout.PREFERRED_SIZE, 51, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                                .addComponent(jLabel47)
                                                                .addGap(18, 18, 18)
                                                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                                .addGap(10, 10, 10)
                                                                                .addComponent(jLabel59, javax.swing.GroupLayout.PREFERRED_SIZE, 161, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                                        .addComponent(jLabel55, javax.swing.GroupLayout.PREFERRED_SIZE, 435, javax.swing.GroupLayout.PREFERRED_SIZE)))))
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addComponent(jLabel51)
                                                .addGap(18, 18, 18)
                                                .addComponent(tbxSEDepartureWindow2, javax.swing.GroupLayout.PREFERRED_SIZE, 51, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel52)
                                                .addGap(18, 18, 18)
                                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                                        .addComponent(jLabel56, javax.swing.GroupLayout.PREFERRED_SIZE, 407, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                .addGap(10, 10, 10)
                                                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                                                        .addComponent(jLabel58, javax.swing.GroupLayout.PREFERRED_SIZE, 382, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                                        .addComponent(jLabel57, javax.swing.GroupLayout.PREFERRED_SIZE, 382, javax.swing.GroupLayout.PREFERRED_SIZE))))))
                                .addContainerGap(305, Short.MAX_VALUE))
        );
        jPanel9Layout.setVerticalGroup(
                jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel9Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel46)
                                        .addComponent(jLabel47)
                                        .addComponent(tbxSEArrialWindow, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel55))
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabel59)
                                .addGap(26, 26, 26)
                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                        .addComponent(jLabel48)
                                                        .addComponent(jLabel49)
                                                        .addComponent(tbxSEDepartureWindow1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addGroup(jPanel9Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                        .addComponent(jLabel51)
                                                        .addComponent(jLabel52)
                                                        .addComponent(tbxSEDepartureWindow2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addComponent(jLabel56)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addComponent(jLabel57)
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                .addComponent(jLabel58)))
                                .addContainerGap(35, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout jPanel4Layout = new javax.swing.GroupLayout(jPanel4);
        jPanel4.setLayout(jPanel4Layout);
        jPanel4Layout.setHorizontalGroup(
                jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel4Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel9, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addContainerGap())
        );
        jPanel4Layout.setVerticalGroup(
                jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel4Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel9, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(284, Short.MAX_VALUE))
        );

        jTabbedPane1.addTab("Special Event", jPanel4);

        moeLabelCD.setText("Critical Density");

        moeLabelLC.setText("Lane Capacity");

        moeLabelCTS.setText("Congestion Threshold Speed");

        moeTextFieldCD.setText("jTextField1");

        moeTextFieldLC.setText("jTextField2");

        moeTextFieldCTS.setText("jTextField3");
        moeTextFieldCTS.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                moeTextFieldCTSActionPerformed(evt);
            }
        });

        moeLabelCD1.setText("vehs/mile/lane");

        moeLabelLC1.setText("vehs/hr/lane");

        moeLabelCTS1.setText("miles/hr");

        javax.swing.GroupLayout jPanel6Layout = new javax.swing.GroupLayout(jPanel6);
        jPanel6.setLayout(jPanel6Layout);
        jPanel6Layout.setHorizontalGroup(
                jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel6Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                                        .addGroup(jPanel6Layout.createSequentialGroup()
                                                .addComponent(moeLabelCTS)
                                                .addGap(37, 37, 37)
                                                .addComponent(moeTextFieldCTS, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                        .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING, false)
                                                .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanel6Layout.createSequentialGroup()
                                                        .addComponent(moeLabelLC)
                                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                                        .addComponent(moeTextFieldLC, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanel6Layout.createSequentialGroup()
                                                        .addComponent(moeLabelCD)
                                                        .addGap(117, 117, 117)
                                                        .addComponent(moeTextFieldCD, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))))
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel6Layout.createSequentialGroup()
                                                .addGap(57, 57, 57)
                                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                                        .addComponent(moeLabelCD1)
                                                        .addComponent(moeLabelLC1)))
                                        .addGroup(jPanel6Layout.createSequentialGroup()
                                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                                .addComponent(moeLabelCTS1)))
                                .addContainerGap(326, Short.MAX_VALUE))
        );
        jPanel6Layout.setVerticalGroup(
                jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel6Layout.createSequentialGroup()
                                .addGap(16, 16, 16)
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(moeLabelCD)
                                        .addComponent(moeTextFieldCD, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(moeLabelCD1))
                                .addGap(22, 22, 22)
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(moeLabelLC)
                                        .addComponent(moeTextFieldLC, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(moeLabelLC1))
                                .addGap(24, 24, 24)
                                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                        .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                .addComponent(moeLabelCTS)
                                                .addComponent(moeTextFieldCTS, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                        .addComponent(moeLabelCTS1))
                                .addContainerGap(284, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
                jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel1Layout.createSequentialGroup()
                                .addComponent(jPanel6, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(0, 284, Short.MAX_VALUE))
        );
        jPanel1Layout.setVerticalGroup(
                jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel1Layout.createSequentialGroup()
                                .addComponent(jPanel6, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(0, 63, Short.MAX_VALUE))
        );

        jTabbedPane2.addTab("Default MOE Paramters", jPanel1);

        moeLabelCD2.setText("Critical Density");

        moeLabelLC2.setText("Lane Capacity");

        moeLabelCTS2.setText("Congestion Threshold Speed");

        RWmoeTextFieldCD.setText("jTextField1");
        RWmoeTextFieldCD.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                RWmoeTextFieldCDActionPerformed(evt);
            }
        });

        RWmoeTextFieldLC.setText("jTextField2");

        RWmoeTextFieldCTS.setText("jTextField3");
        RWmoeTextFieldCTS.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                RWmoeTextFieldCTSActionPerformed(evt);
            }
        });

        moeLabelCD3.setText("vehs/mile/lane");

        moeLabelLC3.setText("vehs/hr/lane");

        moeLabelCTS3.setText("miles/hr");

        jLabel2.setText("Route");

        selectRoute.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Select One" }));
        selectRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                selectRouteActionPerformed(evt);
            }
        });

        jLabel3.setText("Start Date");

        jLabel5.setText("End Date");

        javax.swing.GroupLayout jPanel7Layout = new javax.swing.GroupLayout(jPanel7);
        jPanel7.setLayout(jPanel7Layout);
        jPanel7Layout.setHorizontalGroup(
                jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel7Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addComponent(moeLabelLC2)
                                        .addComponent(moeLabelCD2)
                                        .addGroup(jPanel7Layout.createSequentialGroup()
                                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                                        .addComponent(moeLabelCTS2)
                                                        .addComponent(jLabel2)
                                                        .addComponent(jLabel3)
                                                        .addComponent(jLabel5))
                                                .addGap(18, 18, 18)
                                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                                        .addComponent(selectRoute, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                        .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                                                                .addGroup(jPanel7Layout.createSequentialGroup()
                                                                        .addComponent(RWmoeTextFieldCD, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                                        .addGap(58, 58, 58)
                                                                        .addComponent(moeLabelCD3))
                                                                .addGroup(jPanel7Layout.createSequentialGroup()
                                                                        .addComponent(RWmoeTextFieldLC, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                                                        .addComponent(moeLabelLC3)))
                                                        .addGroup(jPanel7Layout.createSequentialGroup()
                                                                .addComponent(RWmoeTextFieldCTS, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                                .addGap(96, 96, 96)
                                                                .addComponent(moeLabelCTS3))
                                                        .addComponent(startDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                        .addComponent(endDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))))
                                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        jPanel7Layout.setVerticalGroup(
                jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel7Layout.createSequentialGroup()
                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel7Layout.createSequentialGroup()
                                                .addGap(21, 21, 21)
                                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                        .addComponent(jLabel2)
                                                        .addComponent(selectRoute, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                                .addGap(29, 29, 29)
                                                .addComponent(moeLabelCD2)
                                                .addGap(17, 17, 17))
                                        .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel7Layout.createSequentialGroup()
                                                .addContainerGap()
                                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                        .addComponent(RWmoeTextFieldCD, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                        .addComponent(moeLabelCD3))
                                                .addGap(18, 18, 18)))
                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                                        .addComponent(moeLabelLC2)
                                        .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                                .addComponent(RWmoeTextFieldLC, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                .addComponent(moeLabelLC3)))
                                .addGap(18, 18, 18)
                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(moeLabelCTS2)
                                        .addComponent(RWmoeTextFieldCTS, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                        .addComponent(moeLabelCTS3))
                                .addGap(30, 30, 30)
                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel3)
                                        .addComponent(startDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addGap(25, 25, 25)
                                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel5)
                                        .addComponent(endDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                                .addContainerGap(137, Short.MAX_VALUE))
        );

        RWMOETable.setModel(new javax.swing.table.DefaultTableModel(
                new Object [][] {

                },
                new String [] {
                        "Route", "Critical Density", "Lane Capacity", "Congestion Threshold Speed", "Start Date", "End Date", "Update Time", "Status", "Reason"
                }
        ) {
            boolean[] canEdit = new boolean [] {
                    false, false, false, false, false, false, false, false, false
            };

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit [columnIndex];
            }
        });
        jScrollPane1.setViewportView(RWMOETable);

        javax.swing.GroupLayout jPanel5Layout = new javax.swing.GroupLayout(jPanel5);
        jPanel5.setLayout(jPanel5Layout);
        jPanel5Layout.setHorizontalGroup(
                jPanel5Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel5Layout.createSequentialGroup()
                                .addComponent(jPanel7, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 592, Short.MAX_VALUE))
        );
        jPanel5Layout.setVerticalGroup(
                jPanel5Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel5Layout.createSequentialGroup()
                                .addComponent(jPanel7, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(0, 39, Short.MAX_VALUE))
                        .addGroup(jPanel5Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jScrollPane1)
                                .addContainerGap())
        );

        jTabbedPane2.addTab("Route Wise MOE Parameters", jPanel5);

        jTabbedPane1.addTab("MOE Parameters", jTabbedPane2);

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
                layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jTabbedPane1)
                                .addContainerGap())
        );
        layout.setVerticalGroup(
                layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addGroup(layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jTabbedPane1)
                                .addContainerGap())
        );
    }// </editor-fold>

    private void moeTextFieldCTSActionPerformed(java.awt.event.ActionEvent evt) {
        // TODO add your handling code here:
    }

    private void RWmoeTextFieldCTSActionPerformed(java.awt.event.ActionEvent evt) {
        // TODO add your handling code here:
    }

    private void RWmoeTextFieldCDActionPerformed(java.awt.event.ActionEvent evt) {
        // TODO add your handling code here:
    }

    private void selectRouteActionPerformed(java.awt.event.ActionEvent evt) {
        // TODO add your handling code here:
    }


    // Variables declaration - do not modify
    private javax.swing.JTable RWMOETable;
    private javax.swing.JTextField RWmoeTextFieldCD;
    private javax.swing.JTextField RWmoeTextFieldCTS;
    private javax.swing.JTextField RWmoeTextFieldLC;
    private org.jdesktop.swingx.JXDatePicker endDate;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel14;
    private javax.swing.JLabel jLabel15;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel25;
    private javax.swing.JLabel jLabel26;
    private javax.swing.JLabel jLabel28;
    private javax.swing.JLabel jLabel29;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel46;
    private javax.swing.JLabel jLabel47;
    private javax.swing.JLabel jLabel48;
    private javax.swing.JLabel jLabel49;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel51;
    private javax.swing.JLabel jLabel52;
    private javax.swing.JLabel jLabel55;
    private javax.swing.JLabel jLabel56;
    private javax.swing.JLabel jLabel57;
    private javax.swing.JLabel jLabel58;
    private javax.swing.JLabel jLabel59;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel11;
    private javax.swing.JPanel jPanel13;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel5;
    private javax.swing.JPanel jPanel6;
    private javax.swing.JPanel jPanel7;
    private javax.swing.JPanel jPanel9;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JTabbedPane jTabbedPane1;
    private javax.swing.JTabbedPane jTabbedPane2;
    private javax.swing.JLabel moeLabelCD;
    private javax.swing.JLabel moeLabelCD1;
    private javax.swing.JLabel moeLabelCD2;
    private javax.swing.JLabel moeLabelCD3;
    private javax.swing.JLabel moeLabelCTS;
    private javax.swing.JLabel moeLabelCTS1;
    private javax.swing.JLabel moeLabelCTS2;
    private javax.swing.JLabel moeLabelCTS3;
    private javax.swing.JLabel moeLabelLC;
    private javax.swing.JLabel moeLabelLC1;
    private javax.swing.JLabel moeLabelLC2;
    private javax.swing.JLabel moeLabelLC3;
    private javax.swing.JTextField moeTextFieldCD;
    private javax.swing.JTextField moeTextFieldCTS;
    private javax.swing.JTextField moeTextFieldLC;
    private javax.swing.JComboBox<String> selectRoute;
    private org.jdesktop.swingx.JXDatePicker startDate;
    private javax.swing.JTextField tbxINCDownstreamDistanceLimit;
    private javax.swing.JTextField tbxINCUpstreamDistanceLimit;
    private javax.swing.JTextField tbxSEArrialWindow;
    private javax.swing.JTextField tbxSEDepartureWindow1;
    private javax.swing.JTextField tbxSEDepartureWindow2;
    private javax.swing.JTextField tbxWZDownstreamDistanceLimit;
    private javax.swing.JTextField tbxWZUpstreamDistanceLimit;
    // End of variables declaration

}
