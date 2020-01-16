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
package ncrtes.estimation;

import ncrtes.types.BarealaneRegainTimeInfo;
import common.util.FileHelper;
import java.io.IOException;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import javax.swing.JOptionPane;

/**
 *
 * @author chong
 */
public class ImportReportedTimeDialog extends javax.swing.JDialog {

    List<BarealaneRegainTimeInfo> barelaneinfo = null;

    /**
     * Creates new form SelectCorridorDialog
     */
    public ImportReportedTimeDialog(java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();
    }

    public void init() {
//        this.cbxCorridor.init(Infra.getInstance(), new CorridorSelector.CorridorSelectedListener() {    
//            @Override
//            public void OnSelected(int idx, Corridor corr) {
//                if(corr == null) {
//                    JOptionPane.showMessageDialog(null, "corridor selected : null");
//                } else {
//                    JOptionPane.showMessageDialog(null, "corridor selected : " + corr.toString());
//                }                
//            }
//        });           
    }

    private void selectCSVFile() {
        String filepath = FileHelper.chooseFileToOpen(".", "Select CSV File", FileHelper.FileFilterForCSV);
        if (filepath != null) {
            this.tbxBarelaneRegainTimeFile.setText(filepath);
        }
    }

    private void loadBarelaneRegainTimeInfo() {
        if (this.tabMain.getSelectedIndex() == 0) {
            String csvfile = this.tbxBarelaneRegainTimeFile.getText();
            if (csvfile.trim().isEmpty()) {
                JOptionPane.showMessageDialog(this, "Barelane Regain Time Information is not loaded");
                return;
            }            
            this.barelaneinfo = loadCSVFile(csvfile);
        } else {
            this.barelaneinfo = parseCSVContents(this.tbxCSVContents.getText());
        }

        if (this.barelaneinfo != null) {
            for (BarealaneRegainTimeInfo brt : this.barelaneinfo) {
                System.out.println(String.format("TruckRoute=%s, SST=%s, SET=%s, LLT=%s, BRT=%s", brt.truckroute_id, brt.snow_start_time, brt.snow_end_time, brt.lane_lost_time, brt.barelane_regain_time));
            }
            dispose();
        } else {
            JOptionPane.showMessageDialog(this, "Barelane Regain Time Information is not loaded");
        }        
    }

    private List<BarealaneRegainTimeInfo> loadCSVFile(String csvfile) {
        try {
            String[][] data = FileHelper.readCSV(csvfile, 0);
            return this.parse(data);
        } catch (IOException ex) {
            return null;
        }
    }

    private List<BarealaneRegainTimeInfo> parseCSVContents(String contents) {
        if(contents.trim().isEmpty()) {
            return null;
        }
        String eol = System.getProperty("line.separator");
        List<String[]> data = new ArrayList<String[]>();
        String[] lines = contents.split(eol);
        for (int r = 0; r < lines.length; r++) {
            data.add(lines[r].split(","));
        }
        String[][] array = data.toArray(new String[data.size()][0]);
        return this.parse(array);
    }

    private List<BarealaneRegainTimeInfo> parse(String[][] data) {
        List<BarealaneRegainTimeInfo> brtList = new ArrayList<BarealaneRegainTimeInfo>();
        for (int r = 1; r < data.length; r++) {
            String truckRouteId = data[r][0];
            Date snowStartTime = toDateTime(data[r][1]);
            Date snowEndTime = toDateTime(data[r][2]);
            Date lostTime = toDateTime(data[r][3]);
            Date regainTime = toDateTime(data[r][4]);
            if (truckRouteId.isEmpty()) {
                JOptionPane.showMessageDialog(this, "TruckRouteID is missing on line " + (r + 1));
                return null;
            }            
            if ((!data[r][0].isEmpty() && snowStartTime == null)
                    || (!data[r][1].isEmpty() && snowEndTime == null)
                    || (!data[r][2].isEmpty() && lostTime == null)
                    || (!data[r][3].isEmpty() && regainTime == null)) {
                System.out.println(String.format("Line%d : %s, %s, %s, %s, %s", r + 1, data[r][0], data[r][1], data[r][2], data[r][3], data[r][4]));
                JOptionPane.showMessageDialog(this, "Cannot parse datetime string on line " + (r + 1));
                return null;
            }
//            if (regainTime == null) {
//                JOptionPane.showMessageDialog(this, "Barelane regain time is missing on line " + (r + 1));
//                return null;
//            }
            BarealaneRegainTimeInfo brt = new BarealaneRegainTimeInfo(truckRouteId, snowStartTime, snowEndTime, lostTime, regainTime);
            brtList.add(brt);
        }
        return brtList;
    }

    private Date toDateTime(String datetimeString) {
        List<SimpleDateFormat> dateFormats = new ArrayList<SimpleDateFormat>();
        dateFormats.add(new SimpleDateFormat("yyyy-MM-dd HH:mm"));
        dateFormats.add(new SimpleDateFormat("MM/dd/yyyy HH:mm"));
        dateFormats.add(new SimpleDateFormat("yyyy/MM/dd HH:mm"));
        dateFormats.add(new SimpleDateFormat("dd MMMMM yyyy HH:mm"));

        dateFormats.add(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss"));
        dateFormats.add(new SimpleDateFormat("MM/dd/yyyy HH:mm:ss"));
        dateFormats.add(new SimpleDateFormat("yyyy/MM/dd HH:mm:ss"));
        dateFormats.add(new SimpleDateFormat("dd MMMMM yyyy HH:mm:ss"));

        for (SimpleDateFormat pattern : dateFormats) {
            try {
                return new Date(pattern.parse(datetimeString).getTime());

            } catch (ParseException ex) {
            }
        }
        return null;
    }

    /**
     * This method is called from within the constructor to initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is always
     * regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">
    private void initComponents() {

        tabMain = new javax.swing.JTabbedPane();
        jPanel1 = new javax.swing.JPanel();
        jLabel4 = new javax.swing.JLabel();
        tbxBarelaneRegainTimeFile = new javax.swing.JTextField();
        btnCSVFileBrowse = new javax.swing.JButton();
        jLabel3 = new javax.swing.JLabel();
        jLabel1 = new javax.swing.JLabel();
        jPanel2 = new javax.swing.JPanel();
        jScrollPane1 = new javax.swing.JScrollPane();
        tbxCSVContents = new javax.swing.JTextArea();
        jLabel6 = new javax.swing.JLabel();
        btnCancel = new javax.swing.JButton();
        btnOK = new javax.swing.JButton();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Barelane Regain Time Import Dialog");

        jLabel4.setText("Select CSV file");

        btnCSVFileBrowse.setText("Browse");
        btnCSVFileBrowse.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCSVFileBrowseActionPerformed(evt);
            }
        });

        jLabel3.setText("* CSV File Example");

        jLabel1.setIcon(new javax.swing.ImageIcon(getClass().getResource("/ncrtes/estimation/resource/barelane_regain_time_file.PNG"))); // NOI18N

        javax.swing.GroupLayout jPanel1Layout = new javax.swing.GroupLayout(jPanel1);
        jPanel1.setLayout(jPanel1Layout);
        jPanel1Layout.setHorizontalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addGroup(jPanel1Layout.createSequentialGroup()
                                .addComponent(jLabel4)
                                .addGap(0, 0, Short.MAX_VALUE))
                            .addComponent(tbxBarelaneRegainTimeFile))
                        .addGap(18, 18, 18)
                        .addComponent(btnCSVFileBrowse, javax.swing.GroupLayout.PREFERRED_SIZE, 75, javax.swing.GroupLayout.PREFERRED_SIZE))
                    .addGroup(jPanel1Layout.createSequentialGroup()
                        .addGap(23, 23, 23)
                        .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                            .addComponent(jLabel1)
                            .addComponent(jLabel3))
                        .addGap(0, 131, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel1Layout.setVerticalGroup(
            jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel1Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel4)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addGroup(jPanel1Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(tbxBarelaneRegainTimeFile, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(btnCSVFileBrowse))
                .addGap(18, 18, 18)
                .addComponent(jLabel3)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(jLabel1, javax.swing.GroupLayout.PREFERRED_SIZE, 103, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap(javax.swing.GroupLayout.DEFAULT_SIZE, Short.MAX_VALUE))
        );

        tabMain.addTab("CSV File Import", jPanel1);

        tbxCSVContents.setColumns(20);
        tbxCSVContents.setRows(5);
        jScrollPane1.setViewportView(tbxCSVContents);

        jLabel6.setText("Enter CSV data in the below textarea (without colume head)");

        javax.swing.GroupLayout jPanel2Layout = new javax.swing.GroupLayout(jPanel2);
        jPanel2.setLayout(jPanel2Layout);
        jPanel2Layout.setHorizontalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1)
                    .addGroup(jPanel2Layout.createSequentialGroup()
                        .addComponent(jLabel6)
                        .addGap(0, 243, Short.MAX_VALUE)))
                .addContainerGap())
        );
        jPanel2Layout.setVerticalGroup(
            jPanel2Layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(jPanel2Layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(jLabel6)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 169, Short.MAX_VALUE)
                .addContainerGap())
        );

        tabMain.addTab("User Input", jPanel2);

        btnCancel.setText("Cancel");
        btnCancel.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnCancelActionPerformed(evt);
            }
        });

        btnOK.setText("OK");
        btnOK.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                btnOKActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(tabMain)
                    .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                        .addGap(0, 0, Short.MAX_VALUE)
                        .addComponent(btnCancel)
                        .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                        .addComponent(btnOK, javax.swing.GroupLayout.PREFERRED_SIZE, 176, javax.swing.GroupLayout.PREFERRED_SIZE)))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(tabMain)
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(btnOK)
                    .addComponent(btnCancel))
                .addContainerGap())
        );

        pack();
    }private void btnCSVFileBrowseActionPerformed(java.awt.event.ActionEvent evt) {
        selectCSVFile();
    }

    private void btnOKActionPerformed(java.awt.event.ActionEvent evt) {
        loadBarelaneRegainTimeInfo();
    }

    private void btnCancelActionPerformed(java.awt.event.ActionEvent evt) {
        dispose();
    }


    // Variables declaration - do not modify
    private javax.swing.JButton btnCSVFileBrowse;
    private javax.swing.JButton btnCancel;
    private javax.swing.JButton btnOK;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JLabel jLabel3;
    private javax.swing.JLabel jLabel4;
    private javax.swing.JLabel jLabel6;
    private javax.swing.JPanel jPanel1;
    private javax.swing.JPanel jPanel2;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JTabbedPane tabMain;
    private javax.swing.JTextField tbxBarelaneRegainTimeFile;
    private javax.swing.JTextArea tbxCSVContents;
    // End of variables declaration

}
