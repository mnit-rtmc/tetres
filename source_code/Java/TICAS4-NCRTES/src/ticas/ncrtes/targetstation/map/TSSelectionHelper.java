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
package ticas.ncrtes.targetstation.map;

import ticas.common.infra.Infra;
import ticas.common.infra.InfraObject;
import ticas.common.infra.RNode;
import ticas.ncrtes.targetstation.ISetTargetStation;
import ticas.common.ui.map.InfraInfoDialog;
import ticas.common.ui.map.TileServerFactory;
import java.awt.Point;
import java.awt.event.ItemListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JComponent;
import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import org.jdesktop.swingx.JXMapKit;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TSSelectionHelper {

    public Infra infra;
    public TSMapHelper mapHelper;
    public final int initZoom = 7;
    public final double initLatitude = 44.974878;
    public final double initLongitude = -93.233414;
    public TSInfraPoint selectedPoint;
    public TSInfraPoint prevSelectedPoint;
    public Point clickedPoint;
    public final ArrayList<InfraObject> addedList = new ArrayList<>();
    public final List<RNode> routePointList = new ArrayList<>();
    public boolean isReady = false;

    // UI Components
    public JXMapKit compMap;

    public JPopupMenu compContextMenu;
//    public JMenuItem compMenuItemSetTS;
    public JMenuItem compMenuItemProperties;

    public JComponent parent;
    public ItemListener corridorItemListener;
    private ISetTargetStation tsSetCallback;
    private JMenuItem compMenuItemUnSetTS;

    public void init(JComponent comp, JXMapKit jmKit, ISetTargetStation tsSetCallback) {
        this.parent = comp;
        this.compMap = jmKit;
        this.tsSetCallback = tsSetCallback;
        this.initContextMenu();
        this.initMap();
    }

    public void initMap() {
        this.infra = Infra.getInstance();
        this.mapHelper = new TSMapHelper(this.compMap);
        this.compMap.setTileFactory(TileServerFactory.getTileFactory());
        GeoPosition initCenter = new GeoPosition(this.initLatitude, this.initLongitude);

        this.compMap.setAddressLocation(initCenter);
        this.compMap.setZoom(this.initZoom);
        this.compMap.getMiniMap().setVisible(false);

        this.mapHelper.removeMouseListener();

        this.compMap.getMainMap().addMouseListener(new MouseAdapter() {

            // toggle visibility of label on marker when marker is clicked
            @Override
            public void mouseClicked(MouseEvent e) {
                TSInfraPoint ip = mapHelper.getClickedMarker(e.getPoint());
                if (ip == null) {
                    return;
                }
                if (ip.isShowLabel()) {
                    ip.setLabelVisible(false);
                } else {
                    ip.setLabelVisible(true);
                }
                mapHelper.repaint();
            }

            // show popup menu when right button is clicked
            @Override
            public void mouseReleased(MouseEvent e) {
                TSInfraPoint ip = mapHelper.getClickedMarker(e.getPoint());

                if (ip != null && e.isPopupTrigger()) {
                    
//                    compMenuItemSetTS.setVisible(true);                    
//                    compMenuItemUnSetTS.setEnabled(true);
//                    
                    if(ip.markerType == TSInfraPoint.MarkerType.BLUE) {
//                        compMenuItemSetTS.setVisible(false);
                        compMenuItemUnSetTS.setVisible(true);
                    } else {
//                        compMenuItemSetTS.setVisible(true);
                        compMenuItemUnSetTS.setVisible(false);
                    }
                    InfraObject o = ip.getInfraObject();                    
                    RNode rnode = (RNode) o;
                    selectedPoint = ip;
                    clickedPoint = e.getLocationOnScreen();
                    compContextMenu.show(compMap.getMainMap(), e.getX(), e.getY());
                }
            }
        });
    }

    public void reset() {
        resetMap();
    }

    public void resetMap() {
        this.mapHelper.clear();
        this.routePointList.clear();
        this.mapHelper.setRouteAsBlueMarker(null);
        this.prevSelectedPoint = null;
        this.isReady = false;
    }

    private void onSetClicked() {
        RNode rnode = (RNode)this.selectedPoint.getInfraObject();
        this.tsSetCallback.setTargetStation(rnode);
    }
    
    private void onUnsetClicked() {
        RNode rnode = (RNode)this.selectedPoint.getInfraObject();
        this.tsSetCallback.unsetTargetStation(rnode);
    }    

    public void onPropertyClicked() {
        if (this.selectedPoint != null) {
            InfraInfoDialog rid = new InfraInfoDialog(this.selectedPoint.getInfraObject(), null, true);
            rid.setLocation(this.clickedPoint);
            rid.setVisible(true);
        }
    }

    public void menuItemPropertiesActionPerformed(java.awt.event.ActionEvent evt) {
        onPropertyClicked();
    }

    public void initContextMenu() {
//        this.compMenuItemSetTS = new javax.swing.JMenuItem();
        this.compMenuItemUnSetTS = new javax.swing.JMenuItem();
        this.compMenuItemProperties = new javax.swing.JMenuItem();
        this.compContextMenu = new javax.swing.JPopupMenu();
//        this.compContextMenu.add(this.compMenuItemSetTS);
        this.compContextMenu.add(this.compMenuItemUnSetTS);
        this.compContextMenu.add(this.compMenuItemProperties);

//        this.compMenuItemSetTS.setText("Set as Target Station");
//        this.compMenuItemSetTS.addActionListener(new java.awt.event.ActionListener() {
//            public void actionPerformed(java.awt.event.ActionEvent evt) {
//                onSetClicked();
//            }
//        });

        this.compMenuItemUnSetTS.setText("Remove from Target Station");
        this.compMenuItemUnSetTS.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onUnsetClicked();
            }
        });
        
        this.compMenuItemProperties.setText("Properties");
        this.compMenuItemProperties.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onPropertyClicked();
            }
        });

    }
}
