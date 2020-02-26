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

import admin.TeTRESConfig;
import admin.api.RouteClient;
import admin.api.WorkzoneClient;
import admin.types.AbstractDataChangeListener;
import admin.types.WorkZoneGroupInfo;
import admin.types.WorkZoneInfo;
import common.infra.Infra;
import common.infra.RNode;
import common.log.TICASLogger;
import common.pyticas.HttpResult;
import common.pyticas.IResponseCallback;
import common.pyticas.responses.ResponseRoute;
import common.route.Route;
import common.route.RouteCreationHelper;
import common.util.FileHelper;

import javax.swing.*;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;

/**
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class WZEditDialog extends JDialog {

  public Route route;
  private RouteCreationHelper routeCreationHelper;
  private WorkZoneGroupInfo wzgi;
  private WorkZoneInfo wzi;
  private WorkzoneClient wzApi;
  private RouteClient routeApi;

  /**
   * Creates new form RouteCreateDialog
   */
  public WZEditDialog(java.awt.Frame parent, WorkZoneGroupInfo wzgi, WorkZoneInfo wzi, boolean modal) {
    super(parent, modal);
    initComponents();
    this.init(wzgi, wzi);
  }

  private void init(WorkZoneGroupInfo wzgi, WorkZoneInfo wzi) {
    this.routeCreationHelper = new RouteCreationHelper();
    this.routeCreationHelper.init(null, this.jmKit, this.cbxCorridors, this.lbxRoutes);
    this.wzApi = new WorkzoneClient();
    this.routeApi = new RouteClient();
    this.wzgi = wzgi;
    this.wzi = wzi;

    if (this.wzi != null) {
      this.tbxDesc.setText(this.wzi.memo);
      this.tbxDesc.setText(this.wzi.memo);
      this.dtStartDatetime.setDate(this.wzi.getStartDate());
      this.dtEndDatetime.setDate(this.wzi.getEndDate());

      List<RNode> rnodes = new ArrayList<>();
      for (RNode rn : wzi.route1.getRNodes()) {
        rnodes.add(rn);
      }
      for (RNode rn : wzi.route2.getRNodes()) {
        rnodes.add(rn);
      }
      this.route = wzi.route1;
      cbxCorridors.setSelectedItem(Infra.getInstance().getCorridor(route.getRNodes().get(0).corridor));
      routeCreationHelper.reset();
      routeCreationHelper.isReady = true;
      routeCreationHelper.routePointList.clear();
      routeCreationHelper.routePointList.addAll(route.getRNodes());
      routeCreationHelper.updateRoutes();
    }

    this.wzApi.addChangeListener(new AbstractDataChangeListener<WorkZoneInfo>() {
      @Override
      public void insertFailed(HttpResult result, WorkZoneInfo obj) {
        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to add workzone data");
      }

      @Override
      public void insertSuccess(Integer id) {
        dispose();
      }


      @Override
      public void updateSuccess(int id) {
        dispose();
      }

      @Override
      public void updateFailed(HttpResult result, WorkZoneInfo obj) {
        JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to update workzone data");
      }

    });

  }

  public void setCopied(WorkZoneInfo wzi) {

    this.route = wzi.route1;

    this.dtStartDatetime.setDate(wzi.getStartDate());
    this.dtEndDatetime.setDate(wzi.getEndDate());
    this.tbxDesc.setText(wzi.memo);

    this.routeCreationHelper.reset();
    List<RNode> rnodes = new ArrayList<RNode>();
    for (RNode rn : wzi.route1.getRNodes()) {
      rnodes.add(rn);
    }
    for (RNode rn : wzi.route2.getRNodes()) {
      rnodes.add(rn);
    }


    cbxCorridors.setSelectedItem(Infra.getInstance().getCorridor(route.getRNodes().get(0).corridor));
    routeCreationHelper.reset();
    routeCreationHelper.isReady = true;
    routeCreationHelper.routePointList.clear();
    routeCreationHelper.routePointList.addAll(route.getRNodes());
    routeCreationHelper.updateRoutes();
  }

  protected void openLaneConfigurationDialog() {
    if (!this.routeCreationHelper.isReady) {
      JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please click after finishing work zone route creation");
      return;
    }
    Route r = null;

    if (route != null) {
      r = route;
    } else {
      r = new Route("tmp route", "temporary");
      for (RNode rn : this.routeCreationHelper.routePointList) {
        r.addRNode(rn);
      }
    }

    WZRouteLaneConfigDialog wlcd = new WZRouteLaneConfigDialog(r, TeTRESConfig.mainFrame, true);
    wlcd.setVisible(true);

    if (wlcd.updatedRoute == null) {
      JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Lane configuration is not set");
      return;
    }

    this.route = wlcd.updatedRoute;
  }

  private void saveOrUpdate() {
    if (!this.routeCreationHelper.isReady) {
      JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please click after finishing work zone route creation");
      return;
    }

    if (this.route == null) {
      JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please make lane configuration before saving route");
      return;
    }

    String desc = this.tbxDesc.getText();
    Date sdt = this.dtStartDatetime.getDate();
    Date edt = this.dtEndDatetime.getDate();
    if (sdt == null || edt == null) {
      JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Please set construction duration");
      return;
    }

    WorkZoneInfo mWzi = null;

      if (this.wzi != null) {
          mWzi = this.wzi.clone();
      } else {
          mWzi = new WorkZoneInfo();
      }

    mWzi.wz_group_id = this.wzgi.id;
    mWzi.memo = desc;
    mWzi.setDuration(sdt, edt);
    mWzi.route1 = this.route;

    if (this.wzi == null) {
      this.wzApi.insert(mWzi, this.route);
    } else {
      this.wzApi.update(this.wzi, mWzi);
    }

  }

  private void importRoute() {
    final String filepath =
        FileHelper.chooseFileToOpen(".", "Select Lane Configuration File", FileHelper.FileFilterForExcel);
    if (filepath == null) {
      JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Canceled");
      return;
    }

    this.routeApi.getFromRouteConfig(filepath, new IResponseCallback<ResponseRoute>() {
      @Override
      public void success(ResponseRoute res) {
        route = res.obj;
        cbxCorridors.setSelectedItem(Infra.getInstance().getCorridor(route.getRNodes().get(0).corridor));
        routeCreationHelper.reset();
        routeCreationHelper.isReady = true;
        routeCreationHelper.routePointList.clear();
        routeCreationHelper.routePointList.addAll(route.getRNodes());
        routeCreationHelper.updateRoutes();
      }

      @Override
      public void fail(HttpResult res) {
        TICASLogger.getLogger(this.getClass().getName())
            .warn(String.format("could not load route information from the route configuration file : %s", filepath));
      }
    });
  }

  /**
   * This method is called from within the constructor to initialize the form.
   * WARNING: Do NOT modify this code. The content of this method is always
   * regenerated by the Form Editor.
   */
  @SuppressWarnings("unchecked")
  // <editor-fold defaultstate="collapsed" desc="Generated Code">
  private void initComponents() {

    jPanel1 = new JPanel();
    jLabel2 = new JLabel();
    cbxCorridors = new JComboBox();
    jLabel3 = new JLabel();
    btnSave = new JButton();
    btnReset = new JButton();
    jScrollPane2 = new JScrollPane();
    lbxRoutes = new JList();
    jLabel4 = new JLabel();
    jScrollPane1 = new JScrollPane();
    tbxDesc = new JTextArea();
    jLabel5 = new JLabel();
    jLabel6 = new JLabel();
    // faverolles 1/26/2020: removing the lane configuration option
    //  btnEditLaneConfig = new javax.swing.JButton();
    btnImportRoute = new JButton();
    dtStartDatetime = new common.ui.TICASDateTimePicker();
    dtEndDatetime = new common.ui.TICASDateTimePicker();
    btnCancel = new JButton();
    jmKit = new org.jdesktop.swingx.JXMapKit();

    setDefaultCloseOperation(WindowConstants.DISPOSE_ON_CLOSE);
    setTitle("Work Zone Editor");
    setModal(true);

    jLabel2.setText("Select starting corridor :");

    cbxCorridors.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        cbxCorridorsActionPerformed(evt);
      }
    });

    jLabel3.setFont(new java.awt.Font("Verdana", 0, 10)); // NOI18N
    jLabel3.setText("RNodes:");

    btnSave.setText("Save Work Zone Route");
    btnSave.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        btnSaveActionPerformed(evt);
      }
    });

    btnReset.setText("Reset");
    btnReset.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        btnResetActionPerformed(evt);
      }
    });

    jScrollPane2.setViewportView(lbxRoutes);

    jLabel4.setText("Memo");

    tbxDesc.setColumns(20);
    tbxDesc.setRows(5);
    jScrollPane1.setViewportView(tbxDesc);

    jLabel5.setText("Start Date Time");

    jLabel6.setText("End Date Time");

    // faverolles 1/26/2020: removing the lane configuration option
    //        btnEditLaneConfig.setText("Edit Lane Configuration");
    //        btnEditLaneConfig.addActionListener(new java.awt.event.ActionListener() {
    //            public void actionPerformed(java.awt.event.ActionEvent evt) {
    //                btnEditLaneConfigActionPerformed(evt);
    //            }
    //        });

    btnImportRoute.setText("Import Route");
    btnImportRoute.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        btnImportRouteActionPerformed(evt);
      }
    });

    btnCancel.setText("Cancel");
    btnCancel.addActionListener(new java.awt.event.ActionListener() {
      public void actionPerformed(java.awt.event.ActionEvent evt) {
        btnCancelActionPerformed(evt);
      }
    });

    GroupLayout jPanel1Layout = new GroupLayout(jPanel1);
    jPanel1.setLayout(jPanel1Layout);
    jPanel1Layout.setHorizontalGroup(
        jPanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1)
                    .addGroup(GroupLayout.Alignment.TRAILING, jPanel1Layout.createSequentialGroup()
                        .addComponent(btnCancel, GroupLayout.PREFERRED_SIZE, 76,
                            GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED,
                            GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(btnReset, GroupLayout.PREFERRED_SIZE, 76,
                            GroupLayout.PREFERRED_SIZE)
                        .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                        .addComponent(btnSave))
                    .addComponent(dtEndDatetime, GroupLayout.DEFAULT_SIZE,
                        GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    // faverolles 1/26/2020: removing the lane configuration option
                    //  .addComponent(btnEditLaneConfig, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing
                    //  .GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addComponent(jScrollPane2)
                    .addComponent(cbxCorridors, 0, GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addComponent(jLabel2)
                        .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED,
                            GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                        .addComponent(btnImportRoute))
                    .addComponent(dtStartDatetime, GroupLayout.DEFAULT_SIZE,
                        GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel4)
                            .addComponent(jLabel3)
                            .addComponent(jLabel5)
                            .addComponent(jLabel6))
                        .addGap(0, 0, Short.MAX_VALUE)))
                .addContainerGap())
    );
    jPanel1Layout.setVerticalGroup(
        jPanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel4)
                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, GroupLayout.PREFERRED_SIZE, 82,
                    GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jLabel5)
                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(dtStartDatetime, GroupLayout.PREFERRED_SIZE,
                    GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                .addGap(12, 12, 12)
                .addComponent(jLabel6)
                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(dtEndDatetime, GroupLayout.PREFERRED_SIZE,
                    GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                .addGap(22, 22, 22)
                .addGroup(jPanel1Layout.createParallelGroup(GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel2)
                    .addComponent(btnImportRoute))
                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(cbxCorridors, GroupLayout.PREFERRED_SIZE,
                    GroupLayout.DEFAULT_SIZE, GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jLabel3)
                .addPreferredGap(LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane2, GroupLayout.DEFAULT_SIZE, 124, Short.MAX_VALUE)
                .addGap(18, 18, 18)
                // faverolles 1/26/2020: removing the lane configuration option
                //  .addComponent(btnEditLaneConfig, javax.swing.GroupLayout.PREFERRED_SIZE, 40, javax.swing
                //  .GroupLayout.PREFERRED_SIZE)
                .addPreferredGap(LayoutStyle.ComponentPlacement.UNRELATED)
                .addGroup(jPanel1Layout.createParallelGroup(GroupLayout.Alignment.LEADING, false)
                    .addComponent(btnSave, GroupLayout.DEFAULT_SIZE, 35, Short.MAX_VALUE)
                    .addComponent(btnReset, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE,
                        Short.MAX_VALUE)
                    .addComponent(btnCancel, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE,
                        Short.MAX_VALUE))
                .addContainerGap())
    );

    GroupLayout layout = new GroupLayout(getContentPane());
    getContentPane().setLayout(layout);
    layout.setHorizontalGroup(
        layout.createParallelGroup(GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jPanel1, GroupLayout.PREFERRED_SIZE, GroupLayout.DEFAULT_SIZE,
                    GroupLayout.PREFERRED_SIZE)
                .addGap(18, 18, 18)
                .addComponent(jmKit, GroupLayout.DEFAULT_SIZE, 544, Short.MAX_VALUE)
                .addContainerGap())
    );
    layout.setVerticalGroup(
        layout.createParallelGroup(GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                    .addComponent(jPanel1, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE,
                        Short.MAX_VALUE)
                    .addComponent(jmKit, GroupLayout.DEFAULT_SIZE, GroupLayout.DEFAULT_SIZE,
                        Short.MAX_VALUE))
                .addContainerGap())
    );

    pack();
  }

  private void cbxCorridorsActionPerformed(java.awt.event.ActionEvent evt) {

  }

  private void btnSaveActionPerformed(java.awt.event.ActionEvent evt) {
    saveOrUpdate();
  }

  private void btnResetActionPerformed(java.awt.event.ActionEvent evt) {
    this.routeCreationHelper.reset();
  }

  private void btnEditLaneConfigActionPerformed(java.awt.event.ActionEvent evt) {
    openLaneConfigurationDialog();
  }

  private void btnImportRouteActionPerformed(java.awt.event.ActionEvent evt) {
    importRoute();
  }

  private void btnCancelActionPerformed(java.awt.event.ActionEvent evt) {
    dispose();
  }

  // Variables declaration - do not modify
  private JButton btnCancel;

  // faverolles 1/26/2020: removing the lane configuration option
  //    private javax.swing.JButton btnEditLaneConfig;

  private JButton btnImportRoute;
  private JButton btnReset;
  private JButton btnSave;
  private JComboBox cbxCorridors;
  private common.ui.TICASDateTimePicker dtEndDatetime;
  private common.ui.TICASDateTimePicker dtStartDatetime;
  private JLabel jLabel2;
  private JLabel jLabel3;
  private JLabel jLabel4;
  private JLabel jLabel5;
  private JLabel jLabel6;
  private JPanel jPanel1;
  private JScrollPane jScrollPane1;
  private JScrollPane jScrollPane2;
  private org.jdesktop.swingx.JXMapKit jmKit;
  private JList lbxRoutes;
  private JTextArea tbxDesc;
  // End of variables declaration

}
