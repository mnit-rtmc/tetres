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
package ticas.common.route;

import ticas.common.infra.Corridor;
import ticas.common.infra.Infra;
import ticas.common.infra.InfraObject;
import ticas.common.infra.RNode;
import ticas.common.ui.map.InfraInfoDialog;
import ticas.common.ui.map.InfraPoint;
import ticas.common.ui.map.MapHelper;
import ticas.common.ui.map.TMCProvider;
import ticas.common.ui.map.TileServerFactory;
import java.awt.Point;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import javax.swing.DefaultListModel;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JList;
import javax.swing.JMenuItem;
import javax.swing.JPopupMenu;
import org.jdesktop.swingx.JXMapKit;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RouteCreationHelper {

    public Infra infra;
    public MapHelper mapHelper;
    public final int initZoom = 4;
    public final double initLatitude = 44.974878;
    public final double initLongitude = -93.233414;
    public InfraPoint selectedPoint;
    public InfraPoint prevSelectedPoint;
    public Point clickedPoint;
    public final ArrayList<InfraObject> addedList = new ArrayList<>();
    public final List<RNode> routePointList = new ArrayList<>();
    public boolean isReady = false;

    // UI Components
    public JXMapKit compMap;
    public JComboBox compCorridors;
    public JPopupMenu compContextMenu;
    public JMenuItem compMenuItemRouteStart;
    public JMenuItem compMenuItemRouteThroughHere;
    public JMenuItem compMenuItemRouteEnd;
    public JMenuItem compMenuItemProperties;
    public JList compRouteInfo;
    public JComponent parent;
    public ItemListener corridorItemListener;

    public void init(JComponent comp, JXMapKit jmKit, JComboBox cbxCorridors, JList lbxRoutes) {
        this.parent = comp;
        this.compCorridors = cbxCorridors;
        this.compMap = jmKit;
        this.compRouteInfo = lbxRoutes;
        this.initContextMenu();
        this.initMap();
    }

    public void initMap() {
        this.infra = Infra.getInstance();
        this.mapHelper = new MapHelper(this.compMap);
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
                InfraPoint ip = mapHelper.getClickedMarker(e.getPoint());
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
                InfraPoint ip = mapHelper.getClickedMarker(e.getPoint());

                if (ip != null && e.isPopupTrigger()) {
                    InfraObject o = ip.getInfraObject();
                    RNode rnode = (RNode) o;
                    compMenuItemRouteStart.setEnabled(true);
                    compMenuItemRouteThroughHere.setEnabled(false);
                    compMenuItemRouteEnd.setEnabled(true);

                    // if there's no selected rnode
                    if (prevSelectedPoint == null) {
                        compMenuItemRouteEnd.setEnabled(false);
                    } else {
                        compMenuItemRouteStart.setEnabled(false);
                    }

                    if (o.getInfraType().isExit()) {
                        if (!routePointList.isEmpty() && !rnode.connected_to.isEmpty()) {
                            compMenuItemRouteThroughHere.setEnabled(true);
                        }
                    }
                    selectedPoint = ip;
                    clickedPoint = e.getLocationOnScreen();
                    compContextMenu.show(compMap.getMainMap(), e.getX(), e.getY());
                }
            }
        });

        loadCorridors();
        this.corridorItemListener = new ItemListener() {
            @Override
            public void itemStateChanged(ItemEvent evt) {
                resetMap();
            }
        };

        // when user changes corridor
        this.compCorridors.addItemListener(this.corridorItemListener);
    }

    public void reset() {
        resetMap();
    }

    public void loadCorridors() {
        this.compCorridors.addItem("Select Corridor");
        for (Corridor c : this.infra.getCorridors()) {
            this.compCorridors.addItem(c);
        }
    }

    public void resetMap() {
        this.mapHelper.clear();
        if (this.compCorridors.getSelectedIndex() != 0) {
            Corridor c = (Corridor) this.compCorridors.getSelectedItem();
            RNode rn = this.infra.getRNode(c.rnodes.get(0));
            this.mapHelper.setCenter(rn);
            this.mapHelper.showCorridor(c);
        }
        this.routePointList.clear();
        this.mapHelper.setRouteAsBlueMarker(null);
        this.prevSelectedPoint = null;
        this.compRouteInfo.setModel(new DefaultListModel());
        this.isReady = false;
        updateRoutes();
    }

    public void updateRoutes() {
        if (this.routePointList.isEmpty()) {
            return;
        }
        DefaultListModel listModel = new DefaultListModel();
        for (InfraObject obj : this.routePointList) {
            listModel.addElement(obj);
        }
        this.compRouteInfo.setModel(listModel);
    }

    public void onRouteStartClicked() {
        this.routePointList.clear();
        this.prevSelectedPoint = this.selectedPoint;
        InfraObject obj = this.selectedPoint.getInfraObject();
        RNode snode = (RNode) obj;
        this.routePointList.add(snode);
        ArrayList<InfraObject> downNodes = this.getDownstreamRNodes(this.infra.getCorridor(snode.corridor), snode, true);
        this.mapHelper.showInfraObjects(downNodes);
        this.mapHelper.setRouteAsBlueMarker(new InfraObject[]{this.selectedPoint.getInfraObject()});
        updateRoutes();
    }

    public void onRouteThroughHereClicked() {

        InfraObject obj = this.selectedPoint.getInfraObject();
        RNode ext = (RNode) obj;
        RNode rn = (RNode) this.prevSelectedPoint.getInfraObject();

        // add rnodes
        ArrayList<InfraObject> betweenPoints = this.getInfraPointBetweenTwoRNode(rn, ext);
        for (InfraObject _obj : betweenPoints) {
            this.routePointList.add((RNode) _obj);
        }
        routePointList.add(ext);

        String corrName = null;
        if (ext.connected_to.size() > 1) {
            CorridorSelectionDialog csd = new CorridorSelectionDialog(null, ext.connected_to);
            csd.setVisible(true);
            corrName = csd.getSelectedCorridor();
        } else {
            for (String cn : ext.connected_to.keySet()) {
                corrName = cn;
                break;
            }
        }

        String entName = ext.connected_to.get(corrName);
        System.out.println("Connected To : " + entName);
        //InfraPoint entrancePoint = findPointFromMap(this.infra.getRNode(entName));
        //RNode entrance = (RNode) entrancePoint.getInfraObject();
        RNode entrance = this.infra.getRNode(entName);
        this.routePointList.add(entrance);

        // add downstream nodes after update route information
        List<InfraObject> rnodesToBeDisplayed = new ArrayList<InfraObject>();
        rnodesToBeDisplayed.addAll(routePointList);
        rnodesToBeDisplayed.addAll(this.getDownstreamRNodes(this.infra.getCorridor(entrance.corridor), entrance, false));

        // display current added sub-routes
        this.mapHelper.showInfraObjects(rnodesToBeDisplayed);

        // make list to show blue-marke
        this.mapHelper.setRouteAsBlueMarker(routePointList.toArray(new InfraObject[routePointList.size()]));

        // update subroute list screen 
        updateRoutes();
        for (InfraPoint ip : this.mapHelper.getPoints()) {
            if (ip.getInfraObject().name.equals(entName)) {
                this.prevSelectedPoint = ip;
                break;
            }
        }
        //this.prevSelectedPoint = entrancePoint;
        //this.mapHelper.addShowInfraObjects(this.addedList.toArray(new InfraObject[this.addedList.size()]));
    }

    public void onRouteEndClicked() {
        InfraObject obj = this.selectedPoint.getInfraObject();
        RNode endRNode = (RNode) obj;
        RNode rn = (RNode) this.prevSelectedPoint.getInfraObject();

        // add rnodes
        ArrayList<InfraObject> betweenPoints = this.getInfraPointBetweenTwoRNode(rn, endRNode);
        for (InfraObject _obj : betweenPoints) {
            this.routePointList.add((RNode) _obj);
        }
        routePointList.add(endRNode);
        this.updateRoutes();

        // display current added sub-routes
        this.mapHelper.showRNodes(routePointList);

        // make list to show blue-marke
        this.mapHelper.setRouteAsBlueMarker(routePointList.toArray(new InfraObject[routePointList.size()]));

        this.isReady = true;
    }

    public ArrayList<InfraObject> getDownstreamRNodes(Corridor corridor, RNode rnode, boolean includeFirstNode) {
        ArrayList<InfraObject> list = new ArrayList<InfraObject>();
        boolean findThisNode = false;
        for (String rnode_name : corridor.rnodes) {
            RNode rn = this.infra.getRNode(rnode_name);
            if (rn.name.equals(rnode.name)) {
                findThisNode = true;
                if (!includeFirstNode) {
                    continue;
                }
            }
            if (!findThisNode) {
                continue;
            }
            if (this.infra.isAvailableStation(rn)) {
                list.add(rn);
            } else if (this.infra.isEntrance(rn) || this.infra.isExit(rn)) {
                list.add(rn);
            }
        }
        return list;
    }

    public ArrayList<InfraObject> getUpstreamRNodes(Corridor corridor, RNode rnode, boolean includeFirstNode) {
        ArrayList<InfraObject> list = new ArrayList<InfraObject>();
        for (String rnode_name : corridor.rnodes) {
            RNode rn = this.infra.getRNode(rnode_name);
            if (rn.name.equals(rnode.name)) {
                if (includeFirstNode) {
                    if (this.infra.isAvailableStation(rn) || this.infra.isEntrance(rn) || this.infra.isExit(rn)) {
                        list.add(rn);
                    }
                }
                break;
            }
            if (this.infra.isAvailableStation(rn) || this.infra.isEntrance(rn) || this.infra.isExit(rn)) {
                list.add(rn);
            }
        }
        return list;
    }

    public InfraPoint findPointFromMap(RNode rnode) {
        InfraPoint[] points = this.mapHelper.getPoints();
        if (points == null) {
            return null;
        }
        for (InfraPoint p : points) {
            if (p.getInfraObject().equals(rnode)) {
                return p;
            }
        }
        // add rnodes of corridor (just rnode's downstream side)
//        Corridor nextCorridor = infra.getCorridor(rnode.corridor);
//        this.addedList.addAll(getDownstreamRNodes(nextCorridor, rnode, true));
//        this.mapHelper.addShowInfraObjects(this.addedList.toArray(new InfraObject[this.addedList.size()]));
        // find again
        //return findPointFromMap(rnode);
        return null;
    }

    /**
     * Return infra objects list between two rnodes, but except two rnodes (the
     * two rnodes must be in same corridor)
     *
     * @param urn Upstream RNode
     * @param drn Downstream RNode
     * @return InfraPoint list
     */
    public ArrayList<InfraObject> getInfraPointBetweenTwoRNode(RNode urn, RNode drn) {
        // if urn's corridor and drn's corridor are different, return null
        if (!urn.corridor.equals(drn.corridor)) {
            return null;
        }

        ArrayList<InfraObject> pointList = new ArrayList<InfraObject>();
        RNode rn = this.infra.getRNode(urn.down_rnode);

        // add rnodes between last clicked marker and exit marker        
        while (rn != null) {
            if (rn.equals(drn)) {
                break;
            }
            if (this.infra.isAvailableStation(rn) || this.infra.isEntrance(rn) || this.infra.isExit(rn)) {
                pointList.add(rn);
            }
            rn = this.infra.getRNode(rn.down_rnode);
        }

        // if rn == null
        // it means that drn was not found in the corridor
        // drn might be upstream node of urn
        if (rn == null) {
            return null;
        } else {
            return pointList;
        }
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
        this.compMenuItemRouteStart = new javax.swing.JMenuItem();
        this.compMenuItemRouteThroughHere = new javax.swing.JMenuItem();
        this.compMenuItemRouteEnd = new javax.swing.JMenuItem();
        this.compMenuItemProperties = new javax.swing.JMenuItem();
        this.compContextMenu = new javax.swing.JPopupMenu();
        this.compContextMenu.add(this.compMenuItemRouteStart);
        this.compContextMenu.add(this.compMenuItemRouteThroughHere);
        this.compContextMenu.add(this.compMenuItemRouteEnd);
        this.compContextMenu.add(this.compMenuItemProperties);

        this.compMenuItemRouteStart.setText("Route start from here");
        this.compMenuItemRouteStart.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onRouteStartClicked();
            }
        });
        this.compMenuItemRouteThroughHere.setText("Through this exit");
        this.compMenuItemRouteThroughHere.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onRouteThroughHereClicked();
            }
        });
        this.compMenuItemRouteEnd.setText("Route end to here");
        this.compMenuItemRouteEnd.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onRouteEndClicked();
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
