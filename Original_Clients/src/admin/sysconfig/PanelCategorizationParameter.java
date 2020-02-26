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

/**
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class PanelCategorizationParameter extends JPanel {

    /**
     * Creates new form PanelPeriodicJobSeting
     */
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

        // faverolles 1/12/2020: Adding MOE Configuration Parameters
        FormHelper.setDoubleFilter(this.moeTextFieldCD.getDocument(), false);
        FormHelper.setDoubleFilter(this.moeTextFieldLC.getDocument(), false);
        FormHelper.setDoubleFilter(this.moeTextFieldCTS.getDocument(), false);
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


    private void initComponents() {

        jTabbedPane1 = new JTabbedPane();
        jPanel2 = new JPanel();
        jPanel13 = new JPanel();
        jLabel25 = new JLabel();
        tbxINCDownstreamDistanceLimit = new JTextField();
        jLabel26 = new JLabel();
        jLabel28 = new JLabel();
        tbxINCUpstreamDistanceLimit = new JTextField();
        jLabel29 = new JLabel();
        jPanel3 = new JPanel();
        jPanel11 = new JPanel();
        jLabel1 = new JLabel();
        tbxWZDownstreamDistanceLimit = new JTextField();
        jLabel14 = new JLabel();
        jLabel4 = new JLabel();
        tbxWZUpstreamDistanceLimit = new JTextField();
        jLabel15 = new JLabel();
        jPanel4 = new JPanel();
        jPanel9 = new JPanel();
        jLabel46 = new JLabel();
        tbxSEArrialWindow = new JTextField();
        jLabel47 = new JLabel();
        jLabel55 = new JLabel();
        jLabel48 = new JLabel();
        tbxSEDepartureWindow1 = new JTextField();
        jLabel49 = new JLabel();
        jLabel56 = new JLabel();
        jLabel57 = new JLabel();
        jLabel51 = new JLabel();
        tbxSEDepartureWindow2 = new JTextField();
        jLabel52 = new JLabel();
        jLabel58 = new JLabel();
        jLabel59 = new JLabel();

        // faverolles 1/12/2020: Adding MOE Parameter Configuration Tab
        moePanel1 = new JPanel();
        moePanel2 = new JPanel();
//        moePanel3 = new javax.swing.JPanel();

        moeLabelCD = new JLabel();
        moeLabelLC = new JLabel();
        moeLabelCD1 = new JLabel();
        moeLabelLC1 = new JLabel();
        moeLabelCTS = new JLabel();
        moeLabelCTS1 = new JLabel();

        moeTextFieldCD = new JTextField();
        moeTextFieldLC = new JTextField();
        moeTextFieldCTS = new JTextField();

        moePanel1.setBorder(BorderFactory.createTitledBorder("MOE Configurable Parameters"));

        moeLabelCD.setText("Critical Density");
        moeLabelCD1.setText("vehs/mile/lane");

        moeLabelLC.setText("Lane Capacity");
        moeLabelLC1.setText("vehs/hr/lane");

        moeLabelCTS.setText("Congestion Threshold Speed");
        moeLabelCTS1.setText("miles/hr");

        GroupLayout moePanel1Layout = new GroupLayout(moePanel1);
        moePanel1.setLayout(moePanel1Layout);
        moePanel1Layout.setHorizontalGroup(
                moePanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(moePanel1Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(moePanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addComponent(moeLabelCD)
                                        .addComponent(moeLabelLC)
                                        .addComponent(moeLabelCTS)
                                )
                                .addGap(18, 18, 18)
                                .addGroup(moePanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addGroup(moePanel1Layout.createSequentialGroup()
                                                .addComponent(moeTextFieldCD, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(moeLabelCD1))
                                        .addGroup(moePanel1Layout.createSequentialGroup()
                                                .addComponent(moeTextFieldLC, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(moeLabelLC1))
                                        .addGroup(moePanel1Layout.createSequentialGroup()
                                                .addComponent(moeTextFieldCTS, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(moeLabelCTS1))
                                )
                                .addContainerGap(800, Short.MAX_VALUE))
        );
        moePanel1Layout.setVerticalGroup(
                moePanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(moePanel1Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(moePanel1Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(moeLabelCD)
                                        .addComponent(moeTextFieldCD, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(moeLabelCD1))
                                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(moePanel1Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(moeLabelLC)
                                        .addComponent(moeTextFieldLC, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(moeLabelLC1))
                                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(moePanel1Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(moeLabelCTS)
                                        .addComponent(moeTextFieldCTS, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(moeLabelCTS1))
                                .addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        )
        );

        GroupLayout moePanel2Layout = new GroupLayout(moePanel2);
        moePanel2.setLayout(moePanel2Layout);
        moePanel2Layout.setHorizontalGroup(
                moePanel2Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(moePanel2Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(moePanel1, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addContainerGap())
        );
        moePanel2Layout.setVerticalGroup(
                moePanel2Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(moePanel2Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(moePanel1, GroupLayout.PREFERRED_SIZE, 185, GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(800, Short.MAX_VALUE))
        );

        jTabbedPane1.addTab("MOE Parameters", moePanel2);
        // faverolles 1/12/2020: End


        jPanel13.setBorder(BorderFactory.createTitledBorder("Maximum distance affected by an incident"));

        jLabel25.setText("Maximum distance from downstream boundary of a given route :");

        jLabel26.setText("mile");

        jLabel28.setText("Maximum distance from upstream boundary of a given route :");

        jLabel29.setText("mile");

        GroupLayout jPanel13Layout = new GroupLayout(jPanel13);
        jPanel13.setLayout(jPanel13Layout);
        jPanel13Layout.setHorizontalGroup(
                jPanel13Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel13Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel13Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addComponent(jLabel25)
                                        .addComponent(jLabel28))
                                .addGap(18, 18, 18)
                                .addGroup(jPanel13Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel13Layout.createSequentialGroup()
                                                .addComponent(tbxINCDownstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel26))
                                        .addGroup(jPanel13Layout.createSequentialGroup()
                                                .addComponent(tbxINCUpstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel29)))
                                .addContainerGap(382, Short.MAX_VALUE))
        );
        jPanel13Layout.setVerticalGroup(
                jPanel13Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel13Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel13Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel25)
                                        .addComponent(tbxINCDownstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel26))
                                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(jPanel13Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel28)
                                        .addComponent(tbxINCUpstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel29))
                                .addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        GroupLayout jPanel2Layout = new GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
                jPanel2Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel2Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel13, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
                jPanel2Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel2Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel13, GroupLayout.PREFERRED_SIZE, 85, GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(415, Short.MAX_VALUE))
        );

        jTabbedPane1.addTab("Incident", jPanel2);

        jPanel11.setBorder(BorderFactory.createTitledBorder("Maximum distance affected by a work zone"));

        jLabel1.setText("Maximum distance from downstream boundary of a given route :");

        jLabel14.setText("mile");

        jLabel4.setText("Maximum distance from upstream boundary of a given route :");

        jLabel15.setText("mile");

        GroupLayout jPanel11Layout = new GroupLayout(jPanel11);
        jPanel11.setLayout(jPanel11Layout);
        jPanel11Layout.setHorizontalGroup(
                jPanel11Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel11Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel11Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addComponent(jLabel1)
                                        .addComponent(jLabel4))
                                .addGap(18, 18, 18)
                                .addGroup(jPanel11Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel11Layout.createSequentialGroup()
                                                .addComponent(tbxWZDownstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel14))
                                        .addGroup(jPanel11Layout.createSequentialGroup()
                                                .addComponent(tbxWZUpstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, 50, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel15)))
                                .addContainerGap(382, Short.MAX_VALUE))
        );
        jPanel11Layout.setVerticalGroup(
                jPanel11Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel11Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel11Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel1)
                                        .addComponent(tbxWZDownstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel14))
                                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                                .addGroup(jPanel11Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel4)
                                        .addComponent(tbxWZUpstreamDistanceLimit, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel15))
                                .addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        GroupLayout jPanel3Layout = new GroupLayout(jPanel3);
        jPanel3.setLayout(jPanel3Layout);
        jPanel3Layout.setHorizontalGroup(
                jPanel3Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel3Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel11, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addContainerGap())
        );
        jPanel3Layout.setVerticalGroup(
                jPanel3Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel3Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel11, GroupLayout.PREFERRED_SIZE, 85, GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(415, Short.MAX_VALUE))
        );

        jTabbedPane1.addTab("Workzone", jPanel3);

        jPanel9.setBorder(BorderFactory.createTitledBorder("Time Window Parameter"));

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

        GroupLayout jPanel9Layout = new GroupLayout(jPanel9);
        jPanel9.setLayout(jPanel9Layout);
        jPanel9Layout.setHorizontalGroup(
                jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel9Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addComponent(jLabel46)
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addComponent(jLabel48)
                                                .addGap(18, 18, 18)
                                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                .addComponent(tbxSEDepartureWindow1, GroupLayout.PREFERRED_SIZE, 51, GroupLayout.PREFERRED_SIZE)
                                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                                .addComponent(jLabel49))
                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                .addComponent(tbxSEArrialWindow, GroupLayout.PREFERRED_SIZE, 51, GroupLayout.PREFERRED_SIZE)
                                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                                .addComponent(jLabel47)
                                                                .addGap(18, 18, 18)
                                                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                                .addGap(10, 10, 10)
                                                                                .addComponent(jLabel59, GroupLayout.PREFERRED_SIZE, 161, GroupLayout.PREFERRED_SIZE))
                                                                        .addComponent(jLabel55, GroupLayout.PREFERRED_SIZE, 435, GroupLayout.PREFERRED_SIZE)))))
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addComponent(jLabel51)
                                                .addGap(18, 18, 18)
                                                .addComponent(tbxSEDepartureWindow2, GroupLayout.PREFERRED_SIZE, 51, GroupLayout.PREFERRED_SIZE)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addComponent(jLabel52)
                                                .addGap(18, 18, 18)
                                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                                        .addComponent(jLabel56, GroupLayout.PREFERRED_SIZE, 407, GroupLayout.PREFERRED_SIZE)
                                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                                .addGap(10, 10, 10)
                                                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                                                        .addComponent(jLabel58, GroupLayout.PREFERRED_SIZE, 382, GroupLayout.PREFERRED_SIZE)
                                                                        .addComponent(jLabel57, GroupLayout.PREFERRED_SIZE, 382, GroupLayout.PREFERRED_SIZE))))))
                                .addContainerGap(112, Short.MAX_VALUE))
        );
        jPanel9Layout.setVerticalGroup(
                jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel9Layout.createSequentialGroup()
                                .addContainerGap()
                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                        .addComponent(jLabel46)
                                        .addComponent(jLabel47)
                                        .addComponent(tbxSEArrialWindow, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                                        .addComponent(jLabel55))
                                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jLabel59)
                                .addGap(26, 26, 26)
                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                                        .addComponent(jLabel48)
                                                        .addComponent(jLabel49)
                                                        .addComponent(tbxSEDepartureWindow1, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE))
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                                                .addGroup(jPanel9Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                                                        .addComponent(jLabel51)
                                                        .addComponent(jLabel52)
                                                        .addComponent(tbxSEDepartureWindow2, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)))
                                        .addGroup(jPanel9Layout.createSequentialGroup()
                                                .addComponent(jLabel56)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                                                .addComponent(jLabel57)
                                                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                                                .addComponent(jLabel58)))
                                .addContainerGap(GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        GroupLayout jPanel4Layout = new GroupLayout(jPanel4);
        jPanel4.setLayout(jPanel4Layout);
        jPanel4Layout.setHorizontalGroup(
                jPanel4Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel4Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel9, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                                .addContainerGap())
        );
        jPanel4Layout.setVerticalGroup(
                jPanel4Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(jPanel4Layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jPanel9, GroupLayout.PREFERRED_SIZE, 154, GroupLayout.PREFERRED_SIZE)
                                .addContainerGap(346, Short.MAX_VALUE))
        );

        jTabbedPane1.addTab("Special Event", jPanel4);

        GroupLayout layout = new GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
                layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jTabbedPane1)
                                .addContainerGap())
        );
        layout.setVerticalGroup(
                layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                        .addGroup(layout.createSequentialGroup()
                                .addContainerGap()
                                .addComponent(jTabbedPane1)
                                .addContainerGap())
        );


    }


    // Variables declaration - do not modify
    private JLabel jLabel1;
    private JLabel jLabel14;
    private JLabel jLabel15;
    private JLabel jLabel25;
    private JLabel jLabel26;
    private JLabel jLabel28;
    private JLabel jLabel29;
    private JLabel jLabel4;
    private JLabel jLabel46;
    private JLabel jLabel47;
    private JLabel jLabel48;
    private JLabel jLabel49;
    private JLabel jLabel51;
    private JLabel jLabel52;
    private JLabel jLabel55;
    private JLabel jLabel56;
    private JLabel jLabel57;
    private JLabel jLabel58;
    private JLabel jLabel59;
    private JPanel jPanel11;
    private JPanel jPanel13;
    private JPanel jPanel2;
    private JPanel jPanel3;
    private JPanel jPanel4;
    private JPanel jPanel9;
    private JTabbedPane jTabbedPane1;
    private JTextField tbxINCDownstreamDistanceLimit;
    private JTextField tbxINCUpstreamDistanceLimit;
    private JTextField tbxSEArrialWindow;
    private JTextField tbxSEDepartureWindow1;
    private JTextField tbxSEDepartureWindow2;
    private JTextField tbxWZDownstreamDistanceLimit;
    private JTextField tbxWZUpstreamDistanceLimit;

    // faverolles 1/12/2020: Adding MOE Parameter Configuration Tab
//    private javax.swing.JPanel moeConfigJPanel;
    private JPanel moePanel1;
    private JPanel moePanel2;
//    private javax.swing.JPanel moePanel3;

    private JLabel moeLabelCD;
    private JLabel moeLabelLC;
    private JLabel moeLabelCD1;
    private JLabel moeLabelLC1;
    private JLabel moeLabelCTS;
    private JLabel moeLabelCTS1;

    private JTextField moeTextFieldCD;
    private JTextField moeTextFieldLC;
    private JTextField moeTextFieldCTS;
    // faverolles 1/12/2020: End
}
