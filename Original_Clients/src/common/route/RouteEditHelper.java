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
package common.route;

import common.infra.Infra;
import common.infra.InfraObject;
import common.infra.RNode;
import common.ui.map.InfraPoint;
import common.ui.map.MapHelper;
import common.ui.map.TileServerFactory;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JMenuItem;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class RouteEditHelper extends RouteCreationHelper {

    public JMenuItem compMenuItemExtendStart;
    public JMenuItem compMenuItemExtendEnd;
    public JMenuItem compMenuItemShrinkStart;
    public JMenuItem compMenuItemShrinkEnd;

    public List<RNode> onlyStations() {
        List<RNode> rnodes = new ArrayList<RNode>();
        for (RNode rn : this.routePointList) {
            if (infra.isStation(rn)) {
                rnodes.add(rn);
            }
        }

        return rnodes;
    }

    public int getOrderInCorridor(RNode rn) {
        List<String> allRNodeNames = infra.getCorridor(this.routePointList.get(0).corridor).rnodes;
        for (int i = 0; i < allRNodeNames.size(); i++) {
            String rnName = allRNodeNames.get(i);
            if (rnName.equals(rn.name)) {
                return i;
            }
        }
        return -1;
    }

    public boolean isUpstreamOfRoute(RNode rn) {
        int order = getOrderInCorridor(rn);
        int firstStationOrder = getOrderInCorridor(this.routePointList.get(0));
        return order < firstStationOrder;
    }

    public boolean isDownstreamOfRoute(RNode rn) {
        int order = getOrderInCorridor(rn);
        int lastStationOrder = getOrderInCorridor(this.routePointList.get(this.routePointList.size() - 1));
        return order > lastStationOrder;
    }

    @Override
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

                    compMenuItemExtendStart.setVisible(false);
                    compMenuItemExtendEnd.setVisible(false);
                    compMenuItemRouteStart.setVisible(false);
                    compMenuItemRouteEnd.setVisible(false);
                    compMenuItemRouteThroughHere.setVisible(false);

                    if (isUpstreamOfRoute(rnode)) {
                        compMenuItemExtendStart.setVisible(true);
                    } else if (isDownstreamOfRoute(rnode)) {
                        compMenuItemExtendEnd.setVisible(true);
                    } else {
                        compMenuItemRouteStart.setVisible(true);
                        compMenuItemRouteEnd.setVisible(true);
                    }
                    selectedPoint = ip;
                    clickedPoint = e.getLocationOnScreen();
                    compContextMenu.show(compMap.getMainMap(), e.getX(), e.getY());
                }
            }
        });

        loadCorridors();

        // when user changes corridor
        this.compCorridors.addItemListener(new ItemListener() {
            @Override
            public void itemStateChanged(ItemEvent evt) {
                resetMap();
            }
        });
    }

    @Override
    public void initContextMenu() {

        this.compMenuItemExtendStart = new JMenuItem();
        this.compMenuItemExtendEnd = new JMenuItem();

        this.compMenuItemRouteStart = new JMenuItem();
        this.compMenuItemRouteThroughHere = new JMenuItem();
        this.compMenuItemRouteEnd = new JMenuItem();
        this.compMenuItemProperties = new JMenuItem();
        this.compContextMenu = new javax.swing.JPopupMenu();

        this.compContextMenu.add(this.compMenuItemRouteStart);
        this.compContextMenu.add(this.compMenuItemRouteThroughHere);
        this.compContextMenu.add(this.compMenuItemRouteEnd);

        this.compContextMenu.add(this.compMenuItemExtendStart);
        this.compContextMenu.add(this.compMenuItemExtendEnd);

        this.compContextMenu.add(this.compMenuItemProperties);

        this.compMenuItemExtendStart.setVisible(false);
        this.compMenuItemExtendStart.setText("Extend the route to here");
        this.compMenuItemExtendStart.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onRouteExtendStartClicked();
            }
        });

        this.compMenuItemExtendEnd.setVisible(false);
        this.compMenuItemExtendEnd.setText("Extend the route to here");
        this.compMenuItemExtendEnd.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onRouteExtendEndClicked();
            }
        });

        this.compMenuItemRouteStart.setText("Route start from here");
        this.compMenuItemRouteStart.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                onRouteStartClicked();
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
    
    public void setMap(List<RNode> routeRNodes) {
        RNode firstStation = routeRNodes.get(0);
        RNode lastStation = routeRNodes.get(routeRNodes.size() - 1);
        ArrayList<InfraObject> upstreamRNodes = this.getUpstreamRNodes(infra.getCorridor(firstStation.corridor), firstStation, false);
        ArrayList<InfraObject> downstreamRNodes = this.getDownstreamRNodes(infra.getCorridor(lastStation.corridor), lastStation, false);

        List<InfraObject> allRNodes = new ArrayList<InfraObject>();
        allRNodes.addAll(upstreamRNodes);
        allRNodes.addAll(routeRNodes);
        allRNodes.addAll(downstreamRNodes);

        List<InfraObject> blues = new ArrayList<InfraObject>();
        blues.addAll(upstreamRNodes);
        blues.addAll(downstreamRNodes);

        this.reset();
        this.isReady = true;
        this.routePointList.clear();
        this.routePointList.addAll(routeRNodes);
        this.mapHelper.showInfraObjects(allRNodes);
        this.mapHelper.setRouteAsBlueMarker(blues.toArray(new InfraObject[blues.size()]));
        this.updateRoutes();      
        
        this.mapHelper.setCenter(selectedPoint);
//        this.mapHelper.setCenter(routeRNodes.get(0));
    }

    @Override
    public void onRouteStartClicked() {
        InfraObject obj = this.selectedPoint.getInfraObject();
        RNode snode = (RNode) obj;
        List<RNode> routeRNodes = new ArrayList<RNode>();
        boolean foundFirstRNode = false;
        for (int i = 0; i < this.routePointList.size(); i++) {
            RNode rn = this.routePointList.get(i);
            if (rn.name.equals(snode.name)) {
                foundFirstRNode = true;
            }
            if (foundFirstRNode) {
                routeRNodes.add(rn);
            }
        }
        this.setMap(routeRNodes);
    }

    @Override
    public void onRouteEndClicked() {
        InfraObject obj = this.selectedPoint.getInfraObject();
        RNode enode = (RNode) obj;
        List<RNode> routeRNodes = new ArrayList<RNode>();
        for (int i = 0; i < this.routePointList.size(); i++) {
            RNode rn = this.routePointList.get(i);
            if (rn.name.equals(enode.name)) {
                routeRNodes.add(rn);
                break;
            }
            routeRNodes.add(rn);
        }
        this.setMap(routeRNodes);
    }

    public void onRouteExtendStartClicked() {
        InfraObject obj = this.selectedPoint.getInfraObject();
        RNode snode = (RNode) obj;
        List<RNode> routeRNodes = new ArrayList<RNode>();
        RNode firstRNode = this.routePointList.get(0);
        ArrayList<InfraObject> upstreaRNodes = getUpstreamRNodes(infra.getCorridor(firstRNode.corridor), firstRNode, false);
        boolean foundFistRNode = false;
        for (int i = 0; i < upstreaRNodes.size() ; i++) {
            RNode rn = (RNode)upstreaRNodes.get(i);
            if (rn.name.equals(snode.name)) {
                foundFistRNode = true;
            }
            if(rn.name.equals(firstRNode.name)) {
                break;
            }
            
            if(foundFistRNode)
                routeRNodes.add(rn);
        }
        
        List<RNode> allRNodes = new ArrayList<RNode>();
        allRNodes.addAll(routeRNodes);
        allRNodes.addAll(this.routePointList);
        
        this.setMap(allRNodes);        
    }

    public void onRouteExtendEndClicked() {
        InfraObject obj = this.selectedPoint.getInfraObject();
        RNode enode = (RNode) obj;
        List<RNode> routeRNodes = new ArrayList<RNode>();
        RNode lastRNode = this.routePointList.get(this.routePointList.size()-1);
        ArrayList<InfraObject> downstreamRNodes = getDownstreamRNodes(infra.getCorridor(lastRNode.corridor), lastRNode, false);
        for (int i = 0; i < downstreamRNodes.size() ; i++) {
            RNode rn = (RNode)downstreamRNodes.get(i);
            if (rn.name.equals(enode.name)) {
                routeRNodes.add(rn);
                break;
            }
            routeRNodes.add(rn);
        }        
        List<RNode> allRNodes = new ArrayList<RNode>();
        allRNodes.addAll(this.routePointList);
        allRNodes.addAll(routeRNodes);
        
        this.setMap(allRNodes);   
    }

}
