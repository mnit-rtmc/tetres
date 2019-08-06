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
package ticas.ticas4.moe;

import ticas.common.config.Config;
import ticas.common.infra.RNode;
import ticas.common.period.Interval;
import ticas.common.period.Period;
import ticas.common.plugin.TICASPluginOption;
import ticas.common.pyticas.ApiURIs;
import ticas.common.pyticas.HttpClient;
import ticas.common.pyticas.HttpResult;
import ticas.common.pyticas.IResponseCallback;
import ticas.common.pyticas.LocalRouteClient;
import ticas.common.pyticas.PostData;
import ticas.common.pyticas.PyTICASServer;
import ticas.common.pyticas.responses.ResponseString;
import ticas.common.route.IRouteChanged;
import ticas.common.route.Route;
import ticas.ticas4.TICASMain;
import ticas.ticas4.ui.MOECheckBox;
import ticas.ticas4.ui.OptionCheckBox;
import ticas.ticas4.ui.TextBoxDialog;
import ticas.common.ui.DateChecker;
import ticas.common.util.FileHelper;
import java.util.ArrayList;
import java.util.Calendar;
import java.util.List;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.swing.JOptionPane;
import net.xeoh.plugins.base.PluginManager;
import org.jdesktop.swingx.mapviewer.GeoPosition;
import ticas.common.pyticas.IRequest;
import ticas.common.pyticas.RunningDialog;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class MOEPanel extends javax.swing.JPanel implements IRouteChanged {

    protected final int initZoom = 10;
    protected final double initLatitude = 44.974878;
    protected final double initLongitude = -93.233414;
    protected final boolean DEV_MODE = true;
    protected int nTryLoadInfra = 0;
    protected PluginManager pm;
    protected PyTICASServer server;
    protected TICASPluginOption ticasPluginOption;
    protected TICASMain mainWindow;

    // options
    public final String GROUP = "MOE";
    public final String EXCEL = "excel";
    public final String CSV = "csv";
    public final String CONTOUR = "contour";
    public final String WITH_LANE_CONFIG = "with_lane_config";
    public final String WITHOUT_LANE_CONFIG = "without_lane_config";
    private MOEUIState moeState;

    /**
     * Creates new form TICASMainPanel
     */
    public MOEPanel() {
        initComponents();
    }

    public void init() {

        // initialize map
        this.panMap.init();

        // load routes
        LocalRouteClient.getInstance().addChangeListener(this);
        LocalRouteClient.getInstance().loadList();

        DateChecker dc = DateChecker.getInstance();
        this.ticasCalendar.setDateChecker(dc);
        this.setInterval(Interval.getMinTMCInterval());

        // set duration
        this.panTimeConfig.cbxDuration.addItem("Select");
        for (int i = 1; i <= 32; i++) {
            this.panTimeConfig.cbxDuration.addItem(i);
        }

        moeState = MOEUIState.load();
        moeState.set(this.tbxOutputFolder, this.panTimeConfig);
    }

    protected void showRouteMap(Route route) {
        this.panMap.mapHelper.showRoute(route);
        RNode first = route.getRNodes().get(0);
        this.panMap.mapHelper.setCenter(first);
        this.panMap.mapHelper.zoom(5);
    }

    protected void changedRoute() {
        Object so = this.cbxRoute.getSelectedItem();
        if (so instanceof Route) {
            Route route = (Route) this.cbxRoute.getSelectedItem();
            if (route != null) {
                this.showRouteMap(route);
            } else if (this.panMap.mapHelper != null) {
                this.panMap.mapHelper.clear();
                this.panMap.mapHelper.jmKit.setAddressLocation(new GeoPosition(this.initLatitude, this.initLongitude));
                this.panMap.mapHelper.jmKit.setZoom(this.initZoom);
            }
        }
    }

    protected void setInterval(int runningInterval) {
        if (this.panTimeConfig.cbxInterval.getItemCount() > 0) {
            this.panTimeConfig.cbxInterval.removeAllItems();
        }
        for (Interval i : Interval.values()) {
            if (i.second >= runningInterval) {
                this.panTimeConfig.cbxInterval.addItem(i);
            }
        }
    }

    protected void runEstimation(final String outputPath) {
        final Route route = this.selectedRoute();
        if (route == null) {
            return;
        }

        final List<Period> periods = this.selectedPeriods();
        if (periods == null) {
            return;
        }

        final List<MOECheckBox> moes = this.checkedEstimationList();
        if (moes.isEmpty()) {
            return;
        }

        if (outputPath.isEmpty()) {
            JOptionPane.showMessageDialog(null, "Choose folder to save results", "Info", JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        RunningDialog.run(new IRequest() {
            @Override
            public void request() {
                List<String> moeNames = new ArrayList<String>();
                List<MOEWorker> workers = new ArrayList<MOEWorker>();
                for (MOECheckBox moe : moes) {
                    moeNames.add(moe.name);
                    MOEWorker er = new MOEWorker(moe.name, moe.uri, outputPath, route, periods);
                    workers.add(er);
                    er.start();
                }

                boolean hasError = false;
                boolean hasSuccess = false;
                StringBuilder res = new StringBuilder();
                for (MOEWorker worker : workers) {
                    try {
                        worker.join();
                        res.append(worker.resultMessage).append("\n");
                        hasError = hasError || worker.hasError;
                        hasSuccess = hasSuccess || !worker.hasError;
                    } catch (InterruptedException ex) {
                    }
                }

                if (hasError) {
                    TextBoxDialog tbd = new TextBoxDialog(TICASMain.mainFrame, true);
                    tbd.setLocationRelativeTo(TICASMain.mainFrame);
                    tbd.setData("Measure of Effectiveness", "Error(s) on MOE processing", res.toString());
                    tbd.setVisible(true);
                }
                if (hasSuccess) {
                    if (JOptionPane.showConfirmDialog(null, "MOE process has been done.\nWould you like to open output folder?", "Complete", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
                        FileHelper.openDirectory(getOutputPath());
                    }
                }
            }
        });
    }

    protected void runEstimationWIthCheckingCfgDate(final String outputPath) {
        final Route route = this.selectedRoute();
        if (route == null) {
            return;
        }

        final List<Period> periods = this.selectedPeriods();
        if (periods == null) {
            return;
        }

        final List<MOECheckBox> moes = this.checkedEstimationList();
        if (moes.isEmpty()) {
            return;
        }

        if (outputPath.isEmpty()) {
            JOptionPane.showMessageDialog(null, "Choose folder to save results", "Info", JOptionPane.INFORMATION_MESSAGE);
            return;
        }

        PostData pd = new PostData();
        pd.addData("cfg_date", route.infra_cfg_date);

        HttpClient.post(Config.getAPIUrl(ApiURIs.URI.CHECK_CFG_DATE), pd, new IResponseCallback<ResponseString>() {
            @Override
            public void success(ResponseString result) {
                String cfg_date = result.obj;
                if (!cfg_date.equals(route.infra_cfg_date)) {
                    JOptionPane.showMessageDialog(null, String.format("Roadway Network Configuration Date\nRoute : %s\nUsed : %s", route.infra_cfg_date, cfg_date));
                }
                List<String> moeNames = new ArrayList<String>();
                List<MOEWorker> workers = new ArrayList<MOEWorker>();
                for (MOECheckBox moe : moes) {
                    moeNames.add(moe.name);
                    MOEWorker er = new MOEWorker(moe.name, moe.uri, outputPath, route, periods);
                    workers.add(er);
                    er.start();
                }

                boolean hasError = false;
                boolean hasSuccess = false;
                StringBuilder res = new StringBuilder();
                for (MOEWorker worker : workers) {
                    try {
                        worker.join();
                        res.append(worker.resultMessage).append("\n");
                        hasError = hasError || worker.hasError;
                        hasSuccess = hasSuccess || !worker.hasError;
                    } catch (InterruptedException ex) {
                    }
                }

                if (hasError) {
                    TextBoxDialog tbd = new TextBoxDialog(TICASMain.mainFrame, true);
                    tbd.setLocationRelativeTo(TICASMain.mainFrame);
                    tbd.setData("Measure of Effectiveness", "Error(s) on MOE processing", res.toString());
                    tbd.setVisible(true);
                }
                if (hasSuccess) {
                    if (JOptionPane.showConfirmDialog(null, "MOE process has been done.\nWould you like to open output folder?", "Complete", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
                        FileHelper.openDirectory(getOutputPath());
                    }
                }

            }

            @Override
            public void fail(HttpResult result) {
                JOptionPane.showMessageDialog(null, "Fail to check configuration date of roadway network information");
            }
        }, ResponseString.class);

    }

    protected List<MOECheckBox> checkedEstimationList() {
        List<MOECheckBox> estList = MOECheckBox.getCheckedBoxes(this.GROUP);

        //JOptionPane.showMessageDialog(null, "Travel Time Estimation is only implemented in this development version of TICAS", "Info", JOptionPane.INFORMATION_MESSAGE);
        if (estList.isEmpty()) {
            JOptionPane.showMessageDialog(null, "Select measurment metrics before estimation", "Info", JOptionPane.INFORMATION_MESSAGE);
        }

        return estList;
    }

    protected Route selectedRoute() {
        if (this.cbxRoute.getSelectedIndex() == 0) {
            JOptionPane.showMessageDialog(null, "Select route before estimation", "Info", JOptionPane.INFORMATION_MESSAGE);
            return null;
        }
        return (Route) this.cbxRoute.getSelectedItem();
    }

    protected List<Period> selectedPeriods() {
        Calendar[] selectedDates = this.ticasCalendar.getSelectedDates();
        if (selectedDates.length == 0) {
            JOptionPane.showMessageDialog(null, "Select dates on the calendar before estimation", "Info", JOptionPane.INFORMATION_MESSAGE);
            return null;
        }
        Calendar c1, c2;
        List<Period> periods = new ArrayList<Period>();
        Period period;
        int interval = ((Interval) this.panTimeConfig.cbxInterval.getSelectedItem()).getSecond();
        int start_hour = Integer.parseInt(this.panTimeConfig.cbxStartHour.getSelectedItem().toString());
        int start_min = Integer.parseInt(this.panTimeConfig.cbxStartMin.getSelectedItem().toString());
        int end_hour = Integer.parseInt(this.panTimeConfig.cbxEndHour.getSelectedItem().toString());
        int end_min = Integer.parseInt(this.panTimeConfig.cbxEndMin.getSelectedItem().toString());

        for (Calendar date : selectedDates) {
            c1 = (Calendar) date.clone();
            c2 = (Calendar) date.clone();

            c1.set(Calendar.HOUR, start_hour);
            c1.set(Calendar.MINUTE, start_min);

            if (this.panTimeConfig.cbxDuration.getSelectedIndex() > 0) {
                c2.set(Calendar.HOUR, start_hour);
                c2.set(Calendar.MINUTE, start_min);
                c2.add(Calendar.HOUR, (Integer) this.panTimeConfig.cbxDuration.getSelectedItem());
            } else {
                c2.set(Calendar.HOUR, end_hour);
                c2.set(Calendar.MINUTE, end_min);
            }

            period = new Period(c1.getTime(), c2.getTime(), interval);
            periods.add(period);
        }
        return periods;
    }

    @Override
    public void routeChanged(List<Route> routeList) {
        cbxRoute.removeAllItems();
        cbxRoute.addItem("Select the route");
        for (Route s : routeList) {
            cbxRoute.addItem(s);
        }
    }

    protected void openOutputFolderDialog() {
        String outputPath = FileHelper.chooseDirectory(FileHelper.currentPath(), "Select Directory");
        if (outputPath != null) {
            this.tbxOutputFolder.setText(outputPath);
        }
    }

    protected String getOutputPath() {
        return this.tbxOutputFolder.getText();
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        jPanel4 = new javax.swing.JPanel();
        cbxRoute = new javax.swing.JComboBox();
        jLabel1 = new javax.swing.JLabel();
        panMap = new ticas.common.ui.map.MapPanel();
        jPanel3 = new javax.swing.JPanel();
        jPanel8 = new javax.swing.JPanel();
        jLabel3 = new javax.swing.JLabel();
        chkEstSpeed = new MOECheckBox(this.GROUP, "Speed", ApiURIs.URI.MOE_SPEED);
        chkEstAvgLaneFlow = new MOECheckBox(this.GROUP, "Average Lane Flow", ApiURIs.URI.MOE_AVG_FLOW);
        chkEstDensity = new MOECheckBox(this.GROUP, "Density", ApiURIs.URI.MOE_DENSITY);
        chkEstOccupancy = new MOECheckBox(this.GROUP, "Occupancy", ApiURIs.URI.MOE_OCCUPANCY);
        chkEstTotalFlow = new MOECheckBox(this.GROUP, "Total Flow", ApiURIs.URI.MOE_TOTAL_FLOW);
        chkEstAcceleration = new MOECheckBox(this.GROUP, "Acceleration", ApiURIs.URI.MOE_ACCELERATION);
        jPanel7 = new javax.swing.JPanel();
        jLabel5 = new javax.swing.JLabel();
        chkEstVMT = new MOECheckBox(this.GROUP, "Vehicle Miles Traveled", ApiURIs.URI.MOE_VMT);
        chkEstLVMT = new MOECheckBox(this.GROUP, "Lost VMT for Congestion", ApiURIs.URI.MOE_LVMT);
        chkEstVHT = new MOECheckBox(this.GROUP, "Vehicle Hour Traveled", ApiURIs.URI.MOE_VHT);
        chkEstDVH = new MOECheckBox(this.GROUP, "Delayed Vehicle Hours", ApiURIs.URI.MOE_DVH);
        chkEstMRF = new MOECheckBox(this.GROUP, "Mainlane and Ramp Flow Rates", ApiURIs.URI.MOE_MRF);
        chkEstTT = new MOECheckBox(this.GROUP, "Travel Time", ApiURIs.URI.MOE_TT);
        chkEstSTT = new MOECheckBox(this.GROUP, "Snapshot Total Flow", ApiURIs.URI.MOE_STT);
        chkEstSV = new MOECheckBox(this.GROUP, "Speed Variations", ApiURIs.URI.MOE_SV);
        chkEstCM = new MOECheckBox(this.GROUP, "Congested Miles", ApiURIs.URI.MOE_CM);
        chkEstCMH = new MOECheckBox(this.GROUP, "Congested Miles*Hours", ApiURIs.URI.MOE_CMH);
        chkEstRWIS = new MOECheckBox(this.GROUP, "RWIS Data", ApiURIs.URI.MOE_RWIS);
        jPanel6 = new javax.swing.JPanel();
        jLabel6 = new javax.swing.JLabel();
        chkEstWithLaneConfig = new OptionCheckBox(this.GROUP, this.WITH_LANE_CONFIG);
        chkEstWithoutLaneConfig = new OptionCheckBox(this.GROUP, this.WITHOUT_LANE_CONFIG);
        chkEstDetectorSpeed = new javax.swing.JCheckBox();
        jSeparator1 = new javax.swing.JSeparator();
        chkEstDetectorDensity = new javax.swing.JCheckBox();
        chkEstDetectorFlow = new javax.swing.JCheckBox();
        chkEstDetectorOccupancy = new javax.swing.JCheckBox();
        panTimeConfig = new ticas.common.ui.TimePanel();
        ticasCalendar = new ticas.common.ui.TICASCalendar();
        jLabel2 = new javax.swing.JLabel();
        btnExtract = new javax.swing.JButton();
        jPanel2 = new javax.swing.JPanel();
        jLabel4 = new javax.swing.JLabel();
        jLabel7 = new javax.swing.JLabel();
        chkOutExcel = new OptionCheckBox(this.GROUP, this.EXCEL);
        chkOutCSV = new OptionCheckBox(this.GROUP, this.CSV);
        chkOutContour = new OptionCheckBox(this.GROUP, this.CONTOUR);
        jLabel9 = new javax.swing.JLabel();
        chkOutTimeRange = new javax.swing.JComboBox();
        tbxOutputFolder = new javax.swing.JTextField();
        btnOutputFolder = new javax.swing.JButton();
        btnOpenOutputFolder = new javax.swing.JButton();

        cbxRoute.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                cbxRouteActionPerformed(evt);
            }
        });

        jLabel1.setText("Route");

        javax.swing.GroupLayout jPanel4Layout = new javax.swing.GroupLayout(jPanel4);
        jPanel4.setLayout(jPanel4Layout);
        jPanel4Layout.setHorizontalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel4Layout.createSequentialGroup()
                .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(panMap, javax.swing.GroupLayout.PREFERRED_SIZE, 0, Short.MAX_VALUE)
                    .addGroup(jPanel4Layout.createSequentialGroup()
                        .addGroup(jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel1)
                            .addComponent(cbxRoute, javax.swing.GroupLayout.PREFERRED_SIZE, 239, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addGap(0, 50, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel4Layout.setVerticalGroup(
            jPanel4Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel4Layout.createSequentialGroup()
                .addComponent(jLabel1)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(cbxRoute, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(panMap, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jLabel3.setFont(new java.awt.Font("Tahoma", 1, 11)); // NOI18N
        jLabel3.setText("Station Data");

        chkEstSpeed.setText("Speed");

        chkEstAvgLaneFlow.setText("Avg. Lane Flow");

        chkEstDensity.setText("Density");

        chkEstOccupancy.setText("Occupancy");

        chkEstTotalFlow.setText("Total Flow");

        chkEstAcceleration.setText("Acceleration");

        javax.swing.GroupLayout jPanel8Layout = new javax.swing.GroupLayout(jPanel8);
        jPanel8.setLayout(jPanel8Layout);
        jPanel8Layout.setHorizontalGroup(
            jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel8Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jLabel3)
                    .addGroup(jPanel8Layout.createSequentialGroup()
                        .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(chkEstDensity)
                            .addComponent(chkEstSpeed)
                            .addComponent(chkEstTotalFlow))
                        .addGap(18, 18, 18)
                        .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(chkEstAcceleration)
                            .addComponent(chkEstAvgLaneFlow)
                            .addComponent(chkEstOccupancy))))
                .addContainerGap(22, Short.MAX_VALUE))
        );
        jPanel8Layout.setVerticalGroup(
            jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel8Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel3)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(chkEstSpeed)
                    .addComponent(chkEstAvgLaneFlow))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(chkEstDensity)
                    .addComponent(chkEstOccupancy))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel8Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(chkEstTotalFlow)
                    .addComponent(chkEstAcceleration))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jLabel5.setFont(new java.awt.Font("Tahoma", 1, 11)); // NOI18N
        jLabel5.setText("Traffic Flow Measurements");

        chkEstVMT.setText("Vehicle Miles Traveled (VMT)");

        chkEstLVMT.setText("Lost VMT for congestion (LVMT)");

        chkEstVHT.setText("Vehicle Hour Traveled (VHT)");

        chkEstDVH.setText("Delayed Vehicle Hours (DVH)");

        chkEstMRF.setText("Mainlane and Ramp Flow Rates");

        chkEstTT.setText("Travel Time (TT)");

        chkEstSTT.setText("Snapshot Travel Time (STT)");

        chkEstSV.setText("Speed Variations (SV)");

        chkEstCM.setText("Congested Miles (CM)");

        chkEstCMH.setText("Congested Miles * Hours (CMH)");

        chkEstRWIS.setText("Weather Data (RWIS)");

        javax.swing.GroupLayout jPanel7Layout = new javax.swing.GroupLayout(jPanel7);
        jPanel7.setLayout(jPanel7Layout);
        jPanel7Layout.setHorizontalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(chkEstRWIS)
                    .addComponent(chkEstCMH)
                    .addComponent(chkEstCM)
                    .addComponent(chkEstSV)
                    .addComponent(chkEstSTT)
                    .addComponent(chkEstTT)
                    .addComponent(chkEstMRF)
                    .addComponent(chkEstDVH)
                    .addComponent(jLabel5)
                    .addComponent(chkEstVHT)
                    .addComponent(chkEstLVMT)
                    .addComponent(chkEstVMT))
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );
        jPanel7Layout.setVerticalGroup(
            jPanel7Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel7Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel5)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstVMT)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstLVMT)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstVHT)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstDVH)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstMRF)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstTT)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstSTT)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstSV)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstCM)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstCMH)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstRWIS)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        jLabel6.setFont(new java.awt.Font("Tahoma", 1, 11)); // NOI18N
        jLabel6.setText("Detector Data");

        chkEstWithLaneConfig.setText("With Lane Config");

        chkEstWithoutLaneConfig.setText("Without Lane Config");

        chkEstDetectorSpeed.setText("Speed");

        chkEstDetectorDensity.setText("Density");

        chkEstDetectorFlow.setText("Flow");

        chkEstDetectorOccupancy.setText("Occupancy");

        javax.swing.GroupLayout jPanel6Layout = new javax.swing.GroupLayout(jPanel6);
        jPanel6.setLayout(jPanel6Layout);
        jPanel6Layout.setHorizontalGroup(
            jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel6Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel6Layout.createSequentialGroup()
                        .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel6)
                            .addComponent(chkEstWithLaneConfig)
                            .addComponent(chkEstWithoutLaneConfig)
                            .addGroup(jPanel6Layout.createSequentialGroup()
                                .addComponent(chkEstDetectorSpeed)
                                .addGap(18, 18, 18)
                                .addComponent(chkEstDetectorDensity)))
                        .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
                    .addComponent(jSeparator1, javax.swing.GroupLayout.Alignment.TRAILING)
                    .addGroup(jPanel6Layout.createSequentialGroup()
                        .addComponent(chkEstDetectorFlow)
                        .addGap(26, 26, 26)
                        .addComponent(chkEstDetectorOccupancy, javax.swing.GroupLayout.PREFERRED_SIZE, 85, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addGap(0, 56, Short.MAX_VALUE))))
        );
        jPanel6Layout.setVerticalGroup(
            jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel6Layout.createSequentialGroup()
                .addGap(18, 18, 18)
                .addComponent(jLabel6)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstWithLaneConfig)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(chkEstWithoutLaneConfig)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jSeparator1, javax.swing.GroupLayout.PREFERRED_SIZE, 10, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(chkEstDetectorSpeed)
                    .addComponent(chkEstDetectorDensity))
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel6Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(chkEstDetectorFlow)
                    .addComponent(chkEstDetectorOccupancy))
                .addContainerGap(17, Short.MAX_VALUE))
        );

        jLabel2.setText("Date and Time");

        btnExtract.setText("Extract");
        btnExtract.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnExtractActionPerformed(evt);
            }
        });

        jLabel4.setText("Output Format");

        jLabel7.setText("Output Folder");

        chkOutExcel.setText("Excel");

        chkOutCSV.setText("CSV");

        chkOutContour.setText("Contour");

        jLabel9.setText("Time Range in ");

        chkOutTimeRange.setModel(new javax.swing.DefaultComboBoxModel(new String[] { "Column", "Row" }));

        btnOutputFolder.setText("Browse");
        btnOutputFolder.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnOutputFolderActionPerformed(evt);
            }
        });

        btnOpenOutputFolder.setText("Open Folder");
        btnOpenOutputFolder.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnOpenOutputFolderActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addComponent(tbxOutputFolder)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnOutputFolder)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnOpenOutputFolder))
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(jPanel2Layout.createSequentialGroup()
                                .addComponent(chkOutExcel)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(chkOutCSV)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(chkOutContour)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                                .addComponent(jLabel9)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(chkOutTimeRange, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                            .addComponent(jLabel4)
                            .addComponent(jLabel7))
                        .addGap(0, 415, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel4)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(chkOutExcel)
                    .addComponent(chkOutCSV)
                    .addComponent(chkOutContour)
                    .addComponent(jLabel9)
                    .addComponent(chkOutTimeRange, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addComponent(jLabel7)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(tbxOutputFolder, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(btnOutputFolder)
                    .addComponent(btnOpenOutputFolder))
                .addContainerGap(21, Short.MAX_VALUE))
        );

        javax.swing.GroupLayout jPanel3Layout = new javax.swing.GroupLayout(jPanel3);
        jPanel3.setLayout(jPanel3Layout);
        jPanel3Layout.setHorizontalGroup(
            jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addComponent(btnExtract, javax.swing.GroupLayout.Alignment.TRAILING, javax.swing.GroupLayout.PREFERRED_SIZE, 716, javax.swing.GroupLayout.PREFERRED_SIZE)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                .addComponent(jPanel2, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addGroup(javax.swing.GroupLayout.Alignment.LEADING, jPanel3Layout.createSequentialGroup()
                    .addGap(20, 20, 20)
                    .addGroup(jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                        .addGroup(jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel2)
                            .addComponent(ticasCalendar, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                        .addComponent(panTimeConfig, javax.swing.GroupLayout.PREFERRED_SIZE, 241, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGap(40, 40, 40)
                    .addGroup(jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                        .addComponent(jPanel6, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                        .addComponent(jPanel8, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGap(18, 18, 18)
                    .addComponent(jPanel7, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
        );
        jPanel3Layout.setVerticalGroup(
            jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel3Layout.createSequentialGroup()
                .addGap(16, 16, 16)
                .addGroup(jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel3Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                        .addGroup(jPanel3Layout.createSequentialGroup()
                            .addComponent(jPanel8, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                            .addComponent(jPanel6, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGap(10, 10, 10))
                        .addGroup(jPanel3Layout.createSequentialGroup()
                            .addComponent(jLabel2)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                            .addComponent(ticasCalendar, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                            .addComponent(panTimeConfig, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)))
                    .addComponent(jPanel7, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addComponent(jPanel2, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(btnExtract, javax.swing.GroupLayout.PREFERRED_SIZE, 46, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel4, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                .addComponent(jPanel3, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jPanel3, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addContainerGap())
                    .addGroup(layout.createSequentialGroup()
                        .addComponent(jPanel4, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addGap(29, 29, 29))))
        );
    }// </editor-fold>//GEN-END:initComponents

    private void cbxRouteActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_cbxRouteActionPerformed
        this.changedRoute();
    }//GEN-LAST:event_cbxRouteActionPerformed

    private void btnExtractActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnExtractActionPerformed
        String outputPath = this.getOutputPath();
        this.moeState.update(outputPath, this.panTimeConfig);
        this.runEstimation(outputPath);
    }//GEN-LAST:event_btnExtractActionPerformed

    private void btnOutputFolderActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnOutputFolderActionPerformed
        this.openOutputFolderDialog();
    }//GEN-LAST:event_btnOutputFolderActionPerformed

    private void btnOpenOutputFolderActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_btnOpenOutputFolderActionPerformed
        String outputPath = this.getOutputPath();
        if (outputPath.isEmpty()) {
            return;
        }
        FileHelper.openDirectory(this.getOutputPath());
    }//GEN-LAST:event_btnOpenOutputFolderActionPerformed


    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton btnExtract;
    private javax.swing.JButton btnOpenOutputFolder;
    private javax.swing.JButton btnOutputFolder;
    private javax.swing.JComboBox cbxRoute;
    private javax.swing.JCheckBox chkEstAcceleration;
    private javax.swing.JCheckBox chkEstAvgLaneFlow;
    private javax.swing.JCheckBox chkEstCM;
    private javax.swing.JCheckBox chkEstCMH;
    private javax.swing.JCheckBox chkEstDVH;
    private javax.swing.JCheckBox chkEstDensity;
    private javax.swing.JCheckBox chkEstDetectorDensity;
    private javax.swing.JCheckBox chkEstDetectorFlow;
    private javax.swing.JCheckBox chkEstDetectorOccupancy;
    private javax.swing.JCheckBox chkEstDetectorSpeed;
    private javax.swing.JCheckBox chkEstLVMT;
    private javax.swing.JCheckBox chkEstMRF;
    private javax.swing.JCheckBox chkEstOccupancy;
    private javax.swing.JCheckBox chkEstRWIS;
    private javax.swing.JCheckBox chkEstSTT;
    private javax.swing.JCheckBox chkEstSV;
    private javax.swing.JCheckBox chkEstSpeed;
    private javax.swing.JCheckBox chkEstTT;
    private javax.swing.JCheckBox chkEstTotalFlow;
    private javax.swing.JCheckBox chkEstVHT;
    private javax.swing.JCheckBox chkEstVMT;
    private javax.swing.JCheckBox chkEstWithLaneConfig;
    private javax.swing.JCheckBox chkEstWithoutLaneConfig;
    private javax.swing.JCheckBox chkOutCSV;
    private javax.swing.JCheckBox chkOutContour;
    private javax.swing.JCheckBox chkOutExcel;
    private javax.swing.JComboBox chkOutTimeRange;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel2;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel5;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JLabel jLabel7;
    private javax.swing.JLabel jLabel9;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JPanel jPanel3;
    private javax.swing.JPanel jPanel4;
    private javax.swing.JPanel jPanel6;
    private javax.swing.JPanel jPanel7;
    private javax.swing.JPanel jPanel8;
    private javax.swing.JSeparator jSeparator1;
    private ticas.common.ui.map.MapPanel panMap;
    private ticas.common.ui.TimePanel panTimeConfig;
    private javax.swing.JTextField tbxOutputFolder;
    private ticas.common.ui.TICASCalendar ticasCalendar;
    // End of variables declaration//GEN-END:variables

}
