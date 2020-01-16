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
package admin.specialevent;

import admin.TeTRESConfig;
import admin.api.SpecialEventClient;
import admin.types.AbstractDataChangeListener;
import admin.types.SpecialEventInfo;
import common.pyticas.HttpResult;
import common.ui.map.InfraPoint;
import common.util.FormHelper;
import org.jdesktop.swingx.mapviewer.GeoPosition;

import javax.swing.*;
import java.awt.*;
import java.util.Calendar;
import java.util.Date;

/**
 * @author Chongmyung Park
 */
public final class SEEditDialog extends javax.swing.JDialog {

    private SpecialEventInfo sei;
    protected GeoPosition selectedCoordinate;
    private admin.specialevent.SEMapCtrl mapCtrl;
    private SpecialEventClient model;
    private Integer year;

    public SEEditDialog(Frame parent, SpecialEventInfo sei) {
        super(parent, true);
        initComponents();
        this.init(sei);
    }

    protected void init(SpecialEventInfo givenSEI) {

        this.sei = givenSEI;
        this.model = new SpecialEventClient();
        this.mapCtrl = new admin.specialevent.SEMapCtrl(jxMap);

        // coordinate changed event handler
        admin.specialevent.SEMapCtrl.ICoordinateUpdated coordinateChangeListener = new SEMapCtrl.ICoordinateUpdated() {
            @Override
            public void coordinateUpdated(GeoPosition coordinate) {
                selectedCoordinate = coordinate;
                tbxCoordinates.setText(String.format("%s, %s", coordinate.getLatitude(), coordinate.getLongitude()));
            }
        };
        this.mapCtrl.addCoordinateChangeListener(coordinateChangeListener);

        // set default values when editing
        if (this.sei != null) {
            this.tbxName.setText(this.sei.name);
            this.tbxDesc.setText(this.sei.description);

            this.dtStartDatetime.setDate(this.sei.getStartDate());
            this.dtEndDatetime.setDate(this.sei.getEndDate());

            this.tbxAttendance.setText(this.sei.attendance.toString());
            this.mapCtrl.setPoint(new InfraPoint("", this.sei.lat, this.sei.lon));
            coordinateChangeListener.coordinateUpdated(new GeoPosition(this.sei.lat, this.sei.lon));
            this.mapCtrl.setCenter(this.sei.lat, this.sei.lon);
            this.btnSave.setText("Apply Changes");
        } else {
            this.btnSave.setText("Save");
        }

        // Special Event data change listener
        this.model.addChangeListener(new AbstractDataChangeListener<SpecialEventInfo>() {
            @Override
            public void updateFailed(HttpResult result, SpecialEventInfo obj) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "fail to update special event information");
            }

            @Override
            public void updateSuccess(int id) {
                dispose();
            }

            @Override
            public void insertFailed(HttpResult result, SpecialEventInfo obj) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "fail to add special event information");
            }

            @Override
            public void insertSuccess(Integer insertedId) {
                Calendar c = Calendar.getInstance();
                Date dt = dtStartDatetime.getDate();
                c.setTime(dt);
                year = c.get(Calendar.YEAR);
                dispose();
            }
        });

    }

    /***
     * when clicking save button
     */
    private void saveOrUpdate() {
        String name = this.tbxName.getText().trim();
        if (name.isEmpty()) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame,
                                          "Name is required. Please enter the name of special event.");
            return;
        }
        String desc = this.tbxDesc.getText();
        Date sdt = this.dtStartDatetime.getDate();
        Date edt = this.dtEndDatetime.getDate();
        if (sdt == null || edt == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame,
                                          "Duration is required. Please enter select the start and end time.");
            return;
        }

        SpecialEventInfo seiToUpdate = new SpecialEventInfo();
        seiToUpdate.name = name;
        seiToUpdate.description = desc;
        seiToUpdate.attendance = FormHelper.getInteger(this.tbxAttendance.getText());
        if (seiToUpdate.attendance == null || seiToUpdate.attendance < 0) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame,
                                          "Attendance is required. Please enter the attendance of the special event as positive integer.");
            return;
        }
        if (this.selectedCoordinate == null) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame,
                                          "Coordinates are required. Please set the location on the map.");
            return;
        }
        seiToUpdate.lat = this.selectedCoordinate.getLatitude();
        seiToUpdate.lon = this.selectedCoordinate.getLongitude();

        seiToUpdate.setDuration(sdt, edt);

        if (this.sei != null) {
            seiToUpdate.id = this.sei.id;
            this.model.update(sei, seiToUpdate);
        } else {
            this.model.insert(seiToUpdate);
        }
    }


    /***
     * when clicking cancel button
     */
    protected void cancel() {
        dispose();
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">
    private void initComponents() {

        jLabel1 = new javax.swing.JLabel();
        jPanel1 = new javax.swing.JPanel();
        btnSave = new javax.swing.JButton();
        btnCancel = new javax.swing.JButton();
        jLabel4 = new javax.swing.JLabel();
        tbxName = new javax.swing.JTextField();
        jLabel5 = new javax.swing.JLabel();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxDesc = new javax.swing.JTextArea();
        jLabel6 = new javax.swing.JLabel();
        jLabel7 = new javax.swing.JLabel();
        jLabel8 = new javax.swing.JLabel();
        tbxAttendance = new javax.swing.JTextField();
        jLabel2 = new javax.swing.JLabel();
        tbxCoordinates = new javax.swing.JTextField();
        dtStartDatetime = new common.ui.TICASDateTimePicker();
        dtEndDatetime = new common.ui.TICASDateTimePicker();
        jxMap = new org.jdesktop.swingx.JXMapKit();

        jLabel1.setText("jLabel1");

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Edit");

        btnSave.setText("Apply Changes");
        btnSave.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnSaveActionPerformed(evt);
            }
        });

        btnCancel.setText("Cancel");
        btnCancel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCancelActionPerformed(evt);
            }
        });

        jLabel4.setText("Name");

        jLabel5.setText("Description");

        tbxDesc.setColumns(20);
        tbxDesc.setRows(5);
        jScrollPane1.setViewportView(tbxDesc);

        jLabel6.setText("Start Date Time");

        jLabel7.setText("End Date Time");

        jLabel8.setText("Attendance");

        jLabel2.setText("Coordinates (right click on the map)");

        tbxCoordinates.setEnabled(false);

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
                jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                             .addGroup(jPanel1Layout.createSequentialGroup()
                                                    .addContainerGap()
                                                    .addGroup(jPanel1Layout.createParallelGroup(
                                                            javax.swing.GroupLayout.Alignment.LEADING)
                                                                           .addComponent(jScrollPane1)
                                                                           .addGroup(
                                                                                   javax.swing.GroupLayout.Alignment.TRAILING,
                                                                                   jPanel1Layout.createSequentialGroup()
                                                                                                .addComponent(btnCancel,
                                                                                                              javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                                              156,
                                                                                                              Short.MAX_VALUE)
                                                                                                .addGap(18, 18, 18)
                                                                                                .addComponent(btnSave))
                                                                           .addComponent(tbxName)
                                                                           .addComponent(tbxAttendance)
                                                                           .addComponent(tbxCoordinates)
                                                                           .addComponent(dtStartDatetime,
                                                                                         javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                         javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                         Short.MAX_VALUE)
                                                                           .addGroup(
                                                                                   jPanel1Layout.createSequentialGroup()
                                                                                                .addGroup(jPanel1Layout
                                                                                                                  .createParallelGroup(
                                                                                                                          javax.swing.GroupLayout.Alignment.LEADING)
                                                                                                                  .addComponent(
                                                                                                                          jLabel4)
                                                                                                                  .addComponent(
                                                                                                                          jLabel5)
                                                                                                                  .addComponent(
                                                                                                                          jLabel6)
                                                                                                                  .addComponent(
                                                                                                                          jLabel7)
                                                                                                                  .addComponent(
                                                                                                                          jLabel8)
                                                                                                                  .addComponent(
                                                                                                                          jLabel2))
                                                                                                .addGap(0, 0,
                                                                                                        Short.MAX_VALUE))
                                                                           .addComponent(dtEndDatetime,
                                                                                         javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                         javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                         Short.MAX_VALUE))
                                                    .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
                jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                             .addGroup(jPanel1Layout.createSequentialGroup()
                                                    .addContainerGap()
                                                    .addComponent(jLabel4)
                                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                    .addComponent(tbxName, javax.swing.GroupLayout.PREFERRED_SIZE,
                                                                  javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                  javax.swing.GroupLayout.PREFERRED_SIZE)
                                                    .addPreferredGap(
                                                            javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                    .addComponent(jLabel5)
                                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                    .addComponent(jScrollPane1, javax.swing.GroupLayout.PREFERRED_SIZE,
                                                                  82, javax.swing.GroupLayout.PREFERRED_SIZE)
                                                    .addGap(18, 18, 18)
                                                    .addComponent(jLabel6)
                                                    .addPreferredGap(
                                                            javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                    .addComponent(dtStartDatetime,
                                                                  javax.swing.GroupLayout.PREFERRED_SIZE,
                                                                  javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                  javax.swing.GroupLayout.PREFERRED_SIZE)
                                                    .addGap(12, 12, 12)
                                                    .addComponent(jLabel7)
                                                    .addPreferredGap(
                                                            javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                    .addComponent(dtEndDatetime, javax.swing.GroupLayout.PREFERRED_SIZE,
                                                                  javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                  javax.swing.GroupLayout.PREFERRED_SIZE)
                                                    .addGap(17, 17, 17)
                                                    .addComponent(jLabel8)
                                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                                    .addComponent(tbxAttendance, javax.swing.GroupLayout.PREFERRED_SIZE,
                                                                  javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                  javax.swing.GroupLayout.PREFERRED_SIZE)
                                                    .addGap(18, 18, 18)
                                                    .addComponent(jLabel2)
                                                    .addPreferredGap(
                                                            javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                                    .addComponent(tbxCoordinates,
                                                                  javax.swing.GroupLayout.PREFERRED_SIZE,
                                                                  javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                  javax.swing.GroupLayout.PREFERRED_SIZE)
                                                    .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED,
                                                                     30, Short.MAX_VALUE)
                                                    .addGroup(jPanel1Layout.createParallelGroup(
                                                            javax.swing.GroupLayout.Alignment.LEADING, false)
                                                                           .addComponent(btnCancel,
                                                                                         javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                         javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                         Short.MAX_VALUE)
                                                                           .addComponent(btnSave,
                                                                                         javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                                         35, Short.MAX_VALUE))
                                                    .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
                layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                      .addGroup(layout.createSequentialGroup()
                                      .addContainerGap()
                                      .addComponent(jPanel1, javax.swing.GroupLayout.PREFERRED_SIZE,
                                                    javax.swing.GroupLayout.DEFAULT_SIZE,
                                                    javax.swing.GroupLayout.PREFERRED_SIZE)
                                      .addGap(18, 18, 18)
                                      .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE, 704, Short.MAX_VALUE)
                                      .addContainerGap())
        );
        layout.setVerticalGroup(
                layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                      .addGroup(layout.createSequentialGroup()
                                      .addContainerGap()
                                      .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                                      .addComponent(jPanel1, javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                    javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                    Short.MAX_VALUE)
                                                      .addComponent(jxMap, javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                    javax.swing.GroupLayout.DEFAULT_SIZE,
                                                                    Short.MAX_VALUE))
                                      .addContainerGap())
        );

        pack();
    }

    private void btnSaveActionPerformed(java.awt.event.ActionEvent evt) {
        saveOrUpdate();
    }

    private void btnCancelActionPerformed(java.awt.event.ActionEvent evt) {
        cancel();
    }

    // Variables declaration - do not modify
    private javax.swing.JButton btnCancel;
    private javax.swing.JButton btnSave;
    private common.ui.TICASDateTimePicker dtEndDatetime;
    private common.ui.TICASDateTimePicker dtStartDatetime;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JScrollPane jScrollPane1;
    private org.jdesktop.swingx.JXMapKit jxMap;
    private javax.swing.JTextField tbxAttendance;
    private javax.swing.JTextField tbxCoordinates;
    private javax.swing.JTextArea tbxDesc;
    private javax.swing.JTextField tbxName;
    // End of variables declaration

}
