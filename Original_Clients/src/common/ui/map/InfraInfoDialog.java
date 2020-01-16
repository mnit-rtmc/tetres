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

package common.ui.map;

import common.infra.InfraObject;
import common.infra.DMS;
import common.infra.Detector;
import common.infra.Infra;
import common.infra.Meter;
import common.infra.RNode;
import java.awt.event.ActionEvent;
import java.awt.event.KeyEvent;
import java.util.List;
import javax.swing.AbstractAction;
import javax.swing.Action;
import javax.swing.JComponent;
import javax.swing.KeyStroke;
import javax.swing.table.DefaultTableModel;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class InfraInfoDialog extends javax.swing.JDialog {
    
    Infra infra = Infra.getInstance();
    
    /** Creates new form RNodeInfoDialog */
    public InfraInfoDialog(InfraObject obj, java.awt.Frame parent, boolean modal) {
        super(parent, modal);
        initComponents();        
        setEscape();        
        this.setLocationRelativeTo(parent);
        if (infra.isRNode(obj)) {
            setRNode((RNode) obj);
        } else if (infra.isDetector(obj)) {
            setDetector((Detector)obj);
        } else if(infra.isMeter(obj)) {
            setMeter((Meter)obj);
        } else if(infra.isDMS(obj)){
            setDMSImpl((DMS)obj);
        }
    }

    private void setRNode(RNode rnode) {
        DefaultTableModel tm = (DefaultTableModel) this.tblProperty.getModel();
        String id = rnode.name;
        if (infra.isStation(rnode)) {
            id = id + "(" + rnode.station_id+ ")";
        }
        id = id + " - " + rnode.label;

        this.lbId.setText(id);

        tm.addRow(new Object[]{"id", rnode.name});
        tm.addRow(new Object[]{"type", rnode.getInfraType()});
        tm.addRow(new Object[]{"transition", rnode.transition});

        if (infra.isStation(rnode)) {
            tm.addRow(new Object[]{"station id", rnode.station_id});
            tm.addRow(new Object[]{"speed limit", rnode.s_limit});
            int dcnt = 1;
            for(String d : rnode.detectors){
                String dextend = "";                
                Detector det = infra.getDetector(d);
                if(det.is_abandoned())
                    dextend += "X,";
                if(det.is_auxiliary_lane())
                    dextend += "Aux,";
                if(det.is_HOVT_lane())
                    dextend += "Hov,";
                if(det.is_wavetronics())
                    dextend += "Wave,";
                if(det.is_mainline() || det.is_CD_lane())
                    dextend += "in Station";
                if(!dextend.equals("")){
                    dextend = "("+dextend+")";
                }
                tm.addRow(new Object[]{"detector "+dcnt, det.name + dextend});
                dcnt++;
            }
        }
        tm.addRow(new Object[]{"corridor", rnode.corridor});
        tm.addRow(new Object[]{"label", rnode.label});
        tm.addRow(new Object[]{"lanes", rnode.lanes});
        tm.addRow(new Object[]{"lat", rnode.lat});
        tm.addRow(new Object[]{"lon", rnode.lon});
        tm.addRow(new Object[]{"shift", rnode.shift});

        if (infra.isStation(rnode)) {
            List<String> detNames = rnode.detectors;
            if(detNames != null) {
                String dets = join(detNames.toArray(new String[detNames.size()]), ", ");
                tm.addRow(new Object[]{"detectors", dets});
            }
        } else {
            for (String d : rnode.detectors) {
                Detector det = infra.getDetector(d);
                tm.addRow(new Object[]{det.getLaneType().getName(), det.name});
            }
        }

        if (infra.isEntrance(rnode)) {
            List<String> meters = rnode.meters;
            if(!meters.isEmpty()) {
                Meter meter = infra.getMeter(meters.get(0));
                tm.addRow(new Object[]{"ramp meter", meter.name});
                tm.addRow(new Object[]{"ramp meter storage", meter.storage});
            }
        }
        
        String dNodeName = rnode.down_rnode;
        RNode dNode = infra.getRNode(dNodeName);
        if(dNode != null) {
            String dNodeId = dNode.name + " - " + dNode.toString();
            if(infra.isStation(dNode)) {
                dNodeId = dNode.name + "(Station)";
            }
            tm.addRow(new Object[]{"downstream (same corridor) ", dNodeId});
        }
        
        //dNode = rnode.getDownStreamNodeToOtherCorridor();
        List<String> forkTos = rnode.forks;
        for(String forkTo : forkTos) 
        {
            dNode = infra.getRNode(forkTo);
            String dNodeId = dNode.name+ " - " + dNode.toString();
            if(infra.isStation(dNode)) {
                dNodeId = dNode.station_id + "(Station)";
            }
            tm.addRow(new Object[]{"downstream (other corridor) ", dNodeId});
        }        
        
    }
    
    private void setDMSImpl(DMS dmsImpl) {
        DefaultTableModel tm = (DefaultTableModel) this.tblProperty.getModel();
        this.lbId.setText("DMS - "+dmsImpl.name);
        
        tm.addRow(new Object[]{"id", dmsImpl.name});
        tm.addRow(new Object[]{"type", dmsImpl.getInfraType()});
        tm.addRow(new Object[]{"lat", dmsImpl.lat});
        tm.addRow(new Object[]{"lon", dmsImpl.lon});
        tm.addRow(new Object[]{"DistanceFromFirstStation", dmsImpl.distance_from_first_station});
        
        int cnt = 1;
        for(String d : dmsImpl.dms_list) {
            tm.addRow(new Object[]{"DMS_"+cnt, d});
            cnt++;
        }
    }

    
    private void setDetector(Detector d) {
        DefaultTableModel tm = (DefaultTableModel) this.tblProperty.getModel();
        this.lbId.setText(d.name + " - " + d.label);
        
        tm.addRow(new Object[]{"id", d.name});
        tm.addRow(new Object[]{"type", d.getLaneType().getName() });
        tm.addRow(new Object[]{"label", d.label});
        tm.addRow(new Object[]{"lane", d.lane});        
        tm.addRow(new Object[]{"field length", d.field});
        
        RNode rnode = infra.getRNode(d.rnode_name);
        if(rnode != null) {
            if(infra.isStation(rnode)) tm.addRow(new Object[]{"r_node", rnode.name + "(" + rnode.station_id+")"});       
            else  tm.addRow(new Object[]{"r_node id", rnode.name + "(" + rnode.getInfraType()+")"});
            
            tm.addRow(new Object[]{"r_node rat", rnode.lat});
            tm.addRow(new Object[]{"r_node lon", rnode.lon});
            
            if(!infra.isStation(rnode)) 
            {
                for (String det : rnode.detectors) {
                    Detector dd = infra.getDetector(det);
                    tm.addRow(new Object[]{"r_node " + dd.getLaneType(), det});
                }
            }            
        }
    }    
    
    private void setMeter(Meter m) {
        DefaultTableModel tm = (DefaultTableModel) this.tblProperty.getModel();
        this.lbId.setText(m.name + " - " + m.label);
        
        tm.addRow(new Object[]{"id", m.name});
        tm.addRow(new Object[]{"label", m.label});
        tm.addRow(new Object[]{"storage", m.storage});
        
        String rnode_name = m.rnode_name;
        RNode rnode = infra.getRNode(rnode_name);
        if(rnode_name != null) {
            if(infra.isStation(rnode_name)) tm.addRow(new Object[]{"r_node", rnode.name + "(" + rnode.station_id+")"});       
            else  tm.addRow(new Object[]{"r_node id", rnode.name + "(" + rnode.getInfraType()+")"});
            
            tm.addRow(new Object[]{"r_node lat", rnode.lat});
            tm.addRow(new Object[]{"r_node lon", rnode.lon});
            
            if(!infra.isStation(rnode_name)) 
            {
                for (String det : rnode.detectors) {
                    Detector dd = infra.getDetector(det);
                    tm.addRow(new Object[]{"r_node " + dd.getLaneType(), det});
                }
            }            
        }        
    }

    

    private void setEscape() {
        KeyStroke escape = KeyStroke.getKeyStroke(KeyEvent.VK_ESCAPE, 0, false);
        Action escapeAction = new AbstractAction()
        {
            public void actionPerformed(ActionEvent e)
            {
                dispose();
            }
        };
        getRootPane().getInputMap(JComponent.WHEN_IN_FOCUSED_WINDOW).put(escape, "ESCAPE");
        getRootPane().getActionMap().put("ESCAPE", escapeAction);        
    }
    
    private String join(String[] strings, String separator) {
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < strings.length; i++) {
            if (i != 0) {
                sb.append(separator);
            }
            sb.append(strings[i]);
        }
        return sb.toString();
    }

    /** This method is called from within the constructor to
     * initialize the form.
     * WARNING: Do NOT modify this code. The content of this method is
     * always regenerated by the Form Editor.
     */
    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">
    private void initComponents() {

        jScrollPane1 = new javax.swing.JScrollPane();
        tblProperty = new javax.swing.JTable();
        lbId = new javax.swing.JLabel();
        btnClose = new javax.swing.JButton();

        setDefaultCloseOperation(javax.swing.WindowConstants.DISPOSE_ON_CLOSE);
        setTitle("Infra Information");
        setUndecorated(true);
        setResizable(false);
        addKeyListener(new java.awt.event.KeyAdapter() {
            public void keyPressed(KeyEvent evt) {
                formKeyPressed(evt);
            }
        });

        tblProperty.setModel(new DefaultTableModel(
            new Object [][] {

            },
            new String [] {
                "Property", "Value"
            }
        ));
        jScrollPane1.setViewportView(tblProperty);

        lbId.setText("RNODE ID");

        btnClose.setFont(new java.awt.Font("Verdana", 0, 12)); // NOI18N
        btnClose.setText("Close");
        btnClose.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(ActionEvent evt) {
                btnCloseActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(getContentPane());
        getContentPane().setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.TRAILING)
                    .addComponent(btnClose, javax.swing.GroupLayout.PREFERRED_SIZE, 93, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(lbId, javax.swing.GroupLayout.Alignment.LEADING)
                    .addComponent(jScrollPane1, javax.swing.GroupLayout.Alignment.LEADING, javax.swing.GroupLayout.DEFAULT_SIZE, 380, Short.MAX_VALUE))
                .addContainerGap())
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addComponent(lbId)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                .addComponent(jScrollPane1, javax.swing.GroupLayout.DEFAULT_SIZE, 251, Short.MAX_VALUE)
                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.UNRELATED)
                .addComponent(btnClose, javax.swing.GroupLayout.PREFERRED_SIZE, 34, javax.swing.GroupLayout.PREFERRED_SIZE)
                .addContainerGap())
        );

        pack();
    }private void formKeyPressed(KeyEvent evt) {

    }

    private void btnCloseActionPerformed(ActionEvent evt) {
        dispose();
    }

    // Variables declaration - do not modify
    private javax.swing.JButton btnClose;
    private javax.swing.JScrollPane jScrollPane1;
    private javax.swing.JLabel lbId;
    private javax.swing.JTable tblProperty;
    // End of variables declaration

    

}
