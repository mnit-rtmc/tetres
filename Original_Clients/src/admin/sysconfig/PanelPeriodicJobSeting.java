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

import java.sql.Time;
import java.text.DateFormat;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.ComboBoxModel;
import javax.swing.JComboBox;
import common.ui.TICASTimePicker;
import common.ui.TICASTimePicker.TimeInterval;
import admin.types.SystemConfigInfo;

/**
 *
 * @author "Chongmyung Park <chongmyung.park@gmail.com>"
 */
public class PanelPeriodicJobSeting extends javax.swing.JPanel {

    /**
     * Creates new form PeriodicJobSetingPanel
     */
    public PanelPeriodicJobSeting() {
        initComponents();
        this.init();
    }

    private void init() {
        int currentYear = Calendar.getInstance().get(Calendar.YEAR);
        for (Integer year = currentYear; year >= 2008; year--) {
            this.cbxDataArchiveStartYear.addItem(year.toString());
        }
        for (Integer offset = 1; offset <= 31; offset++) {
            this.cbxDailyJobOffsetDays.addItem(offset.toString());
            this.cbxMonthlyJobStartDate.addItem(offset.toString());
        }
    }

    public void updateSettingInUI(SystemConfigInfo cfg) {
        this.setCombobox(this.cbxDataArchiveStartYear, cfg.data_archive_start_year);
        this.setTime(this.dtDailyJobStartTime, cfg.daily_job_start_time);
        this.setTime(this.dtWeeklyJobStartTime, cfg.weekly_job_start_time);
        this.setTime(this.dtMonthlyJobStartTime, cfg.monthly_job_start_time);
        this.setCombobox(this.cbxDailyJobOffsetDays, cfg.daily_job_offset_days);   
        this.setCombobox(this.cbxWeeklyJobStartDay, cfg.weekly_job_start_day);
        this.setCombobox(this.cbxMonthlyJobStartDate, cfg.monthly_job_start_date);
    }
    
    void fillSystemConfigInfo(SystemConfigInfo newSysConfig) {
        newSysConfig.data_archive_start_year = Integer.parseInt(this.cbxDataArchiveStartYear.getSelectedItem().toString());
        newSysConfig.daily_job_offset_days = Integer.parseInt(this.cbxDailyJobOffsetDays.getSelectedItem().toString());
        newSysConfig.daily_job_start_time = this.getTime(this.dtDailyJobStartTime);
        newSysConfig.weekly_job_start_time = this.getTime(this.dtWeeklyJobStartTime);
        newSysConfig.monthly_job_start_time = this.getTime(this.dtMonthlyJobStartTime);
        newSysConfig.weekly_job_start_day = this.cbxWeeklyJobStartDay.getSelectedItem().toString();
        newSysConfig.monthly_job_start_date = Integer.parseInt(this.cbxMonthlyJobStartDate.getSelectedItem().toString());
    }    

    private void setTime(TICASTimePicker timePicker, String timestring) {
        try {
            DateFormat sdf = new SimpleDateFormat("HH:mm");
            Time time = new Time(sdf.parse(timestring).getTime());
            timePicker.setTimeObject(time);
        } catch (ParseException ex) {
            Logger.getLogger(PanelPeriodicJobSeting.class.getName()).log(Level.SEVERE, null, ex);
        }
    }
    
    private String getTime(TICASTimePicker timePicker) {
        Time time = timePicker.getTimeObject();
        DateFormat sdf = new SimpleDateFormat("HH:mm");
        return sdf.format(time);        
    }

    private void setCombobox(JComboBox comboBox, Object value) {
        ComboBoxModel model = comboBox.getModel();
        int size = model.getSize();
        String objStr = value.toString();
        for (int i = 0; i < size; i++) {
            Object element = model.getElementAt(i);
            if(element.toString().toLowerCase().equals(objStr)) {
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

        jLabel1 = new javax.swing.JLabel();
        jLabel2 = new javax.swing.JLabel();
        cbxWeeklyJobStartDay = new JComboBox<>();
        jLabel3 = new javax.swing.JLabel();
        cbxMonthlyJobStartDate = new JComboBox<>();
        jLabel4 = new javax.swing.JLabel();
        cbxDailyJobOffsetDays = new JComboBox<>();
        jLabel5 = new javax.swing.JLabel();
        jLabel6 = new javax.swing.JLabel();
        dtWeeklyJobStartTime = new TICASTimePicker(TimeInterval.TenMinutes);
        dtMonthlyJobStartTime = new TICASTimePicker(TimeInterval.TenMinutes);
        dtDailyJobStartTime = new TICASTimePicker(TimeInterval.TenMinutes);
        jLabel7 = new javax.swing.JLabel();
        cbxDataArchiveStartYear = new JComboBox<>();
        jLabel8 = new javax.swing.JLabel();

        jLabel1.setText("Daily Job Start Time:");

        jLabel2.setText("Weekly Job Start Time:");

        cbxWeeklyJobStartDay.setModel(new javax.swing.DefaultComboBoxModel<>(new String[] { "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" }));

        jLabel3.setText("Monthly Job Start Time:");

        jLabel4.setText("Date to process Daily Data:");

        jLabel5.setText("* Travel times of (today - N days) will be calculated in daily job");

        jLabel6.setText("days prior to today's date");

        jLabel7.setText("Data Archive Start Year:");

        jLabel8.setText("* Travel times will be calculated from the given year");

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel7)
                            .addComponent(jLabel1))
                        .addGap(28, 28, 28)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(cbxDataArchiveStartYear, javax.swing.GroupLayout.PREFERRED_SIZE, 88, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addGap(18, 18, 18)
                                .addComponent(jLabel8))
                            .addComponent(dtDailyJobStartTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addGroup(layout.createSequentialGroup()
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel2)
                            .addComponent(jLabel3))
                        .addGap(10, 10, 10)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addComponent(cbxWeeklyJobStartDay, 0, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(cbxMonthlyJobStartDate, javax.swing.GroupLayout.PREFERRED_SIZE, 88, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(18, 18, 18)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(dtWeeklyJobStartTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addComponent(dtMonthlyJobStartTime, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jLabel4)
                        .addGap(10, 10, 10)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel5)
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(cbxDailyJobOffsetDays, javax.swing.GroupLayout.PREFERRED_SIZE, 88, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(jLabel6)))))
                .addContainerGap(278, Short.MAX_VALUE))
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel7)
                    .addComponent(cbxDataArchiveStartYear, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(jLabel8))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(jLabel1)
                    .addComponent(dtDailyJobStartTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addGap(7, 7, 7)
                        .addComponent(jLabel4))
                    .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                        .addComponent(cbxDailyJobOffsetDays, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(jLabel6)))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jLabel5)
                .addGap(20, 20, 20)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jLabel2)
                        .addGap(30, 30, 30)
                        .addComponent(jLabel3))
                    .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                        .addGroup(layout.createSequentialGroup()
                            .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                                .addComponent(dtWeeklyJobStartTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                                .addComponent(cbxWeeklyJobStartDay, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addGap(18, 18, 18)
                            .addComponent(cbxMonthlyJobStartDate, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addComponent(dtMonthlyJobStartTime, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap(148, Short.MAX_VALUE))
        );
    }// Variables declaration - do not modify
    private JComboBox<String> cbxDailyJobOffsetDays;
    private JComboBox<String> cbxDataArchiveStartYear;
    private JComboBox<String> cbxMonthlyJobStartDate;
    private JComboBox<String> cbxWeeklyJobStartDay;
    private TICASTimePicker dtDailyJobStartTime;
    private TICASTimePicker dtMonthlyJobStartTime;
    private TICASTimePicker dtWeeklyJobStartTime;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel8;
    // End of variables declaration



}
