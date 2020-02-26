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
import common.infra.Infra;
import common.log.TICASLogger;
import common.pyticas.HttpResult;
import common.ui.map.InfraPoint;
import common.ui.map.MapHelper;
import common.ui.map.TileServerFactory;
import common.util.FileHelper;
import org.apache.logging.log4j.core.Logger;

import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;
import java.util.stream.Collectors;

/**
 * @author Chongmyung Park
 */
public class SEListPanel extends JPanel {

    private Infra infra;
    private MapHelper mapHelper;
    private Integer selectedYear;
    private final List<SpecialEventInfo> selectedSEs = new ArrayList<>();
    private List<SpecialEventInfo> seList = new ArrayList<>();
    private SpecialEventClient model;
    private Logger logger;

    public SEListPanel() {
        initComponents();
        this.jxMap.setTileFactory(TileServerFactory.getTileFactory());
    }

    /**
     * *
     * initialize variables and UI
     */
    public void init() {
        this.infra = Infra.getInstance();
        this.jxMap.getMiniMap().setVisible(false);
        this.mapHelper = new MapHelper(jxMap);
        this.logger = TICASLogger.getLogger(this.getClass().getName());
        this.model = new SpecialEventClient();

        // when year is selected
        this.cbxYear.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent evt) {
                selectedYear = getSelectedYear();
                loadListByYear();
            }
        });

        // when route is selected
        this.tbSEList.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                selectedSEs.clear();

                DefaultTableModel tm = (DefaultTableModel) tbSEList.getModel();
                for (int row : tbSEList.getSelectedRows()) {
                    SpecialEventInfo s = (SpecialEventInfo) tm.getValueAt(row, 1);
                    if (s != null) {
                        selectedSEs.add(s);
                    }
                }

                if (selectedSEs.isEmpty()) {
                    mapHelper.clear();
                    return;
                }

                List<InfraPoint> ips = new ArrayList<>();
                for (SpecialEventInfo sei : selectedSEs) {
                    ips.add(new InfraPoint(String.format("%s(%s, %d)", sei.name, sei.getDuration(), sei.attendance),
                                           sei.lat, sei.lon));
                }
                mapHelper.showInfraPoints(ips);
            }
        });

        // data change listener
        this.model.addChangeListener(new AbstractDataChangeListener<SpecialEventInfo>() {

            @Override
            public void yearsSuccess(List<Integer> obj) {
                Integer sYear = selectedYear;
                cbxYear.removeAllItems();
                cbxYear.addItem("Select Year");
                cbxYear.addItem("All years");
                for (Integer i : obj) {
                    cbxYear.addItem(i);
                }
                reset();
                setYear(sYear);
                loadListByYear();
            }

            @Override
            public void yearsFailed(HttpResult httpResult) {
                logger.error(httpResult.res_code + " / " + httpResult.res_msg);
                JOptionPane
                        .showMessageDialog(TeTRESConfig.mainFrame, "fail to load year information for special events");
            }

            @Override
            public void listFailed(HttpResult result) {
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to get list of special event");
            }

            @Override
            public void listSuccess(List<SpecialEventInfo> list) {
                seList = list;
                setTable();
            }

            @Override
            public void deleteSuccess(List<Integer> ids) {
                model.years();
            }

            @Override
            public void deleteFailed(HttpResult result, List<Integer> ids) {
                logger.warn(String.format("Fail to delete items : %s", ids.toString()));
                logger.debug(result.contents);
                JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Fail to delete the selected special event");
            }

        });

        this.model.years();
    }

    public void refresh() {
        if (this.cbxYear.getItemCount() == 0) {
            this.model.years();
        }
    }

    /**
     * *
     * open create dialog
     */
    private void createSpecialEvent() {
        SEEditDialog rcd = new SEEditDialog(TeTRESConfig.mainFrame, null);
        rcd.setLocationRelativeTo(TeTRESConfig.mainFrame);
        rcd.setVisible(true);
//        Integer year = rcd.getYear();
//        if(year != null) {
//            this.selectedYear = year;
//        }
        this.model.years();
    }

    /**
     * *
     * open edit dialog
     */
    protected void editSpecialEvent() {
        if (this.selectedSEs.isEmpty() || this.selectedSEs.size() > 1) {
            JOptionPane.showMessageDialog(TeTRESConfig.mainFrame, "Select a single route to edit information");
            return;
        }
        SEEditDialog red = new SEEditDialog(TeTRESConfig.mainFrame, this.selectedSEs.get(0));
        red.setLocationRelativeTo(TeTRESConfig.mainFrame);
        red.setVisible(true);
        this.model.years();
    }

    /**
     * delete selected items
     */
    protected void deleteSpecialEvents() {
        if (this.selectedSEs.isEmpty()) {
            return;
        }

        int res = JOptionPane.showConfirmDialog(TeTRESConfig.mainFrame, "Delete selected special events?", "Confirm",
                                                JOptionPane.YES_NO_OPTION);

        if (res == JOptionPane.YES_OPTION) {
            List<Integer> ids = new ArrayList<>();
            for (SpecialEventInfo se : this.selectedSEs) {
                ids.add(se.id);
            }
            this.model.delete(ids);
        }
    }

    /**
     * *
     * load list by selected year
     */
    protected void loadListByYear() {
        Integer sYear = getSelectedYear();
        if (sYear == null) {
            reset();
        } else if (sYear == 0) {
            model.list();
        } else if (sYear > 1) {
            model.listByYear(sYear);
        }
    }

    /**
     * *
     * reset map, list and selected item
     */
    protected void reset() {
        this.mapHelper.clear();
        this.seList.clear();
        this.selectedSEs.clear();
        setTable();
    }

    /**
     * *
     *
     * @return selected year of combo box
     */
    protected Integer getSelectedYear() {
        Integer sYear = null;
        int slt = this.cbxYear.getSelectedIndex();
        if (slt == 1) {
            sYear = 0;
        } else if (slt > 1) {
            int year = Integer.parseInt(this.cbxYear.getSelectedItem().toString());
            sYear = year;
        } else {
            sYear = null;
        }
        return sYear;
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
        } else if (sYear == 0) {
            this.cbxYear.setSelectedIndex(1);
        } else {
            for (int sidx = 2; sidx < nYears; sidx++) {
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
     * set list table
     */
    protected void setTable() {
        final DefaultTableModel tm = (DefaultTableModel) this.tbSEList.getModel();
        tm.getDataVector().removeAllElements();
        tm.fireTableDataChanged();
        for (SpecialEventInfo s : this.seList) {
            tm.addRow(new Object[]{s.getDuration(), s, s.attendance});
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

        asyncRequestAdapter1 = new org.jdesktop.http.async.event.AsyncRequestAdapter();
        jLabel2 = new JLabel();
        jScrollPane3 = new JScrollPane();
        tbSEList = new JTable();
        btnDeleteSelection = new JButton();
        btnEditRoute = new JButton();
        jxMap = new org.jdesktop.swingx.JXMapKit();
        jLabel1 = new JLabel();
        btnAddRoute = new JButton();
        cbxYear = new JComboBox();

        jLabel2.setText("Special Event List");

        tbSEList.setModel(new DefaultTableModel(
                new Object[][]{

                },
                new String[]{
                        "Duration", "Name", "Attendance"
                }
        ) {
            Class[] types = new Class[]{
                    String.class, Object.class, Integer.class
            };
            boolean[] canEdit = new boolean[]{
                    false, false, false
            };

            public Class getColumnClass(int columnIndex) {
                return types[columnIndex];
            }

            public boolean isCellEditable(int rowIndex, int columnIndex) {
                return canEdit[columnIndex];
            }
        });
        tbSEList.setSelectionMode(ListSelectionModel.MULTIPLE_INTERVAL_SELECTION);
        jScrollPane3.setViewportView(tbSEList);

        btnDeleteSelection.setText("Delete");
        btnDeleteSelection.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                btnDeleteSelectionActionPerformed(evt);
            }
        });

        btnEditRoute.setText("Edit Special Event Info");
        btnEditRoute.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                btnEditRouteActionPerformed(evt);
            }
        });

        jLabel1.setText("Filter");

        btnAddRoute.setText("Add Special Event");
        btnAddRoute.addActionListener(this::btnAddRouteActionPerformed);


        // faverolles 1/14/2020: Special Event Bulk Add From .csv File User Interface
        btnBulkAddSpecialEvents = new JButton();
        btnBulkAddSpecialEvents.setText("Add Special Events From CSV File");
        btnBulkAddSpecialEvents.addActionListener(this::onBulkAddSpecialEventsButtonPress);


        GroupLayout layout = new GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
                layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                      .addGroup(layout.createSequentialGroup()
                                      .addContainerGap()
                                      .addGroup(layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                                      .addComponent(btnAddRoute, GroupLayout.PREFERRED_SIZE,
                                                                    332, GroupLayout.PREFERRED_SIZE)
                                                      .addComponent(btnBulkAddSpecialEvents,
                                                                    GroupLayout.PREFERRED_SIZE, 332,
                                                                    GroupLayout.PREFERRED_SIZE)
                                                      .addComponent(jLabel1)
                                                      .addComponent(jLabel2)
                                                      .addGroup(layout.createParallelGroup(
                                                              GroupLayout.Alignment.TRAILING, false)
                                                                      .addComponent(cbxYear,
                                                                                    GroupLayout.Alignment.LEADING,
                                                                                    0,
                                                                                    GroupLayout.DEFAULT_SIZE,
                                                                                    Short.MAX_VALUE)
                                                                      .addGroup(
                                                                              GroupLayout.Alignment.LEADING,
                                                                              layout.createSequentialGroup()
                                                                                    .addComponent(btnDeleteSelection,
                                                                                                  GroupLayout.PREFERRED_SIZE,
                                                                                                  141,
                                                                                                  GroupLayout.PREFERRED_SIZE)
                                                                                    .addGap(18, 18, 18)
                                                                                    .addComponent(btnEditRoute,
                                                                                                  GroupLayout.DEFAULT_SIZE,
                                                                                                  GroupLayout.DEFAULT_SIZE,
                                                                                                  Short.MAX_VALUE))
                                                                      .addComponent(jScrollPane3,
                                                                                    GroupLayout.Alignment.LEADING,
                                                                                    GroupLayout.DEFAULT_SIZE,
                                                                                    330, Short.MAX_VALUE)))
                                      .addGap(18, 18, 18)
                                      .addComponent(jxMap, GroupLayout.DEFAULT_SIZE, 508, Short.MAX_VALUE)
                                      .addContainerGap())
        );
        layout.setVerticalGroup(
                layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                      .addGroup(layout.createSequentialGroup()
                                      .addContainerGap()
                                      .addGroup(layout.createParallelGroup(GroupLayout.Alignment.LEADING)
                                                      .addGroup(GroupLayout.Alignment.TRAILING,
                                                                layout.createSequentialGroup()
                                                                      .addComponent(btnAddRoute,
                                                                                    GroupLayout.PREFERRED_SIZE,
                                                                                    35,
                                                                                    GroupLayout.PREFERRED_SIZE)
                                                                      .addGap(18, 18, 18)
                                                                      .addComponent(btnBulkAddSpecialEvents,
                                                                                    GroupLayout.PREFERRED_SIZE,
                                                                                    35,
                                                                                    GroupLayout.PREFERRED_SIZE)
                                                                      .addGap(18, 18, 18)
                                                                      .addComponent(jLabel1)
                                                                      .addPreferredGap(
                                                                              LayoutStyle.ComponentPlacement.RELATED)
                                                                      .addComponent(cbxYear,
                                                                                    GroupLayout.PREFERRED_SIZE,
                                                                                    GroupLayout.DEFAULT_SIZE,
                                                                                    GroupLayout.PREFERRED_SIZE)
                                                                      .addGap(18, 18, 18)
                                                                      .addComponent(jLabel2)
                                                                      .addPreferredGap(
                                                                              LayoutStyle.ComponentPlacement.UNRELATED)
                                                                      .addComponent(jScrollPane3,
                                                                                    GroupLayout.PREFERRED_SIZE,
                                                                                    0, Short.MAX_VALUE)
                                                                      .addGap(18, 18, 18)
                                                                      .addGroup(layout.createParallelGroup(
                                                                              GroupLayout.Alignment.BASELINE)
                                                                                      .addComponent(btnDeleteSelection,
                                                                                                    GroupLayout.PREFERRED_SIZE,
                                                                                                    30,
                                                                                                    GroupLayout.PREFERRED_SIZE)
                                                                                      .addComponent(btnEditRoute,
                                                                                                    GroupLayout.PREFERRED_SIZE,
                                                                                                    30,
                                                                                                    GroupLayout.PREFERRED_SIZE)))
                                                      .addComponent(jxMap, GroupLayout.DEFAULT_SIZE, 438,
                                                                    Short.MAX_VALUE))
                                      .addContainerGap())
        );
    }

    private void btnDeleteSelectionActionPerformed(
            ActionEvent evt) {
        this.deleteSpecialEvents();
    }

    private void btnAddRouteActionPerformed(
            ActionEvent evt) {
        this.createSpecialEvent();
    }

    private void btnEditRouteActionPerformed(
            ActionEvent evt) {
        this.editSpecialEvent();
    }


    // Variables declaration - do not modify
    private org.jdesktop.http.async.event.AsyncRequestAdapter asyncRequestAdapter1;
    private JButton btnAddRoute;
    private JButton btnDeleteSelection;
    private JButton btnEditRoute;
    private JComboBox cbxYear;
    private JLabel jLabel1;
    private JLabel jLabel2;
    private JScrollPane jScrollPane3;
    private org.jdesktop.swingx.JXMapKit jxMap;
    private JTable tbSEList;
    // End of variables declaration:variables


    // faverolles 1/14/2020: Special Event Bulk Add From .csv File
    private JButton btnBulkAddSpecialEvents;

    private void onBulkAddSpecialEventsButtonPress(ActionEvent evt) {
        String filepath = FileHelper.chooseFileToOpen(
                ".", "Select CSV Special Event File", FileHelper.FileFilterForCSV);
        if (filepath != null) {
            this.showSpecialEventCSVDialog(filepath);
        }
    }

    private void showSpecialEventCSVDialog(String filePath) {
        BulkAddSpecialEventJDialog dialog = new BulkAddSpecialEventJDialog(
                new JFrame(), "Bulk Add Special Events From CSV File",
                "Loading Data...");
        // set the size of the window
        dialog.setSize(300, 150);
        dialog.startBulkAdd(filePath);
    }

    // faverolles 1/15/2020 TODO: Error Checking

}


class BulkAddSpecialEventJDialog extends JDialog {
    // faverolles 1/15/2020: Created class to show dialog and parse CSV file
    // faverolles 1/15/2020 TODO: make the dialog look nicer

    private static final long serialVersionUID = 1L;
    private JLabel messageLabel = new JLabel("");

    public void startBulkAdd(String filePath) {
        ArrayList<String[]> allSpecialEventsList = parseSpecialEventsCSVFile(filePath);
        if (allSpecialEventsList != null && allSpecialEventsList.size() > 0) {
            this.postToServerApiEndpoint(allSpecialEventsList);
        }
    }

    private void updateMessageLabel(String message) {
        this.messageLabel.setText(message);
        this.revalidate();
    }

    private void postToServerApiEndpoint(ArrayList<String[]> allSpecialEventsList) {
        // faverolles 1/15/2020 TODO: Error checking
        // faverolles 1/15/2020 TODO: update these comments once format finalized
        // faverolles 1/15/2020: Current pending format of CSV file is:
        /*  "Date","Start Time","End Time","Title","Type","Attendance"
            EX. 09/18/2016,7:30 PM,10:45 PM,MN Vikings Vs Green Bay,Football,66813
            data={
              "name": "dev+event+test",
              "description": "development+event+test",
              "start_time": "2018-01-02+18:00:00",
              "end_time": "2018-01-02+19:00:00",
              "lat": 44.97641112589316,
              "lon": -93.22435855865479,
              "attendance": 45678,
              "__module__": "pyticas_tetres.ttypes",
              "__class__": "SpecialEventInfo"
            }
         */
        try {
            this.updateMessageLabel("Posting Events To Server...");
            SpecialEventClient client = new SpecialEventClient();
            client.insertAll(allSpecialEventsList.stream().map(
                    SpecialEventInfo::new).collect(Collectors.toList())
            );
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private ArrayList<String[]> parseSpecialEventsCSVFile(String filePath) {
        try {
            File csvFile = new File(filePath);
            if (csvFile.isFile()) {
                BufferedReader csvReader = new BufferedReader(new FileReader(filePath));
                String row;
                int rowsRead = 0;

                //each entry in this list is one row in the csv file and thus on special event
                ArrayList<String[]> allSpecialEventsList = new ArrayList<>();
                while ((row = csvReader.readLine()) != null) {
                    rowsRead++;
                    allSpecialEventsList.add(row.split(","));
                    this.updateMessageLabel("Rows Parsed: " + rowsRead);
                }
                csvReader.close();

                //remove the header row
                allSpecialEventsList.remove(allSpecialEventsList.get(0));
                return allSpecialEventsList;
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;
    }

    public BulkAddSpecialEventJDialog(JFrame parent, String title, String message) {
        super(parent, title);
        System.out.println("creating the window..");
        // set the position of the window
        Point p = new Point(400, 400);
        setLocation(p.x, p.y);

        // Create a message
        JPanel messagePane = new JPanel();
        messagePane.setLayout(new GridBagLayout());
        this.messageLabel.setText(message);
        messagePane.add(this.messageLabel);
        // get content pane, which is usually the
        // Container of all the dialog's components.
        getContentPane().add(messagePane);

        // Create a button
        JPanel buttonPane = new JPanel();
        JButton button = new JButton("Cancel");
        buttonPane.add(button);
        // set action listener on the button
        button.addActionListener(new MyActionListener());
        getContentPane().add(buttonPane, BorderLayout.PAGE_END);
        setDefaultCloseOperation(DISPOSE_ON_CLOSE);
        pack();
        setVisible(true);
    }

    // override the createRootPane inherited by the JDialog, to create the rootPane.
    // create functionality to close the window when "Escape" button is pressed
    public JRootPane createRootPane() {
        JRootPane rootPane = new JRootPane();
        KeyStroke stroke = KeyStroke.getKeyStroke("ESCAPE");
        Action action = new AbstractAction() {

            private static final long serialVersionUID = 1L;

            public void actionPerformed(ActionEvent e) {
                System.out.println("escaping..");
                setVisible(false);
                dispose();
            }
        };
        InputMap inputMap = rootPane.getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW);
        inputMap.put(stroke, "ESCAPE");
        rootPane.getActionMap().put("ESCAPE", action);
        return rootPane;
    }

    // an action listener to be used when an action is performed
    // (e.g. button is pressed)
    class MyActionListener implements ActionListener {

        //close and dispose of the window.
        public void actionPerformed(ActionEvent e) {
            System.out.println("disposing the window..");
            setVisible(false);
            dispose();
        }
    }
}