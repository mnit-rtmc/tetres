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
package ticas.common.ui.map;

import ticas.common.config.AbstractConfigChangeListener;
import ticas.common.config.Config;
import ticas.common.ui.map.InfraPoint.LABEL_LOC;
import ticas.common.infra.Corridor;
import ticas.common.infra.Detector;
import ticas.common.infra.Infra;
import ticas.common.infra.InfraObject;
import ticas.common.infra.InfraType;
import ticas.common.infra.Meter;
import ticas.common.infra.RNode;
import ticas.common.route.Route;
import java.awt.Dimension;
import java.awt.Frame;
import java.awt.Image;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.Toolkit;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.awt.geom.Point2D;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;
import javax.swing.JFrame;
import javax.swing.JOptionPane;
import org.jdesktop.swingx.JXMapKit;
import org.jdesktop.swingx.JXMapViewer;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public final class MapHelper {

    private final JXMapViewer map;
    private final double initLatitude = 44.962950;
    private final double initLongitude = -93.167412;
    private final int initZoom = 5;
    private final Infra infra = Infra.getInstance();
    private Frame frame;
    private Set<InfraPoint> waypoints;
    private MouseAdapter mouseListner;
    private InfraObject[] routeList;
    private Route selected_route;
    private MapHelper thishelper;
    public final JXMapKit jmKit;

    /**
     * Constructor
     *
     * @param jmKit
     */
    public MapHelper(JXMapKit jmKit) {
        this.jmKit = jmKit;
        this.map = jmKit.getMainMap();
        this.init();
    }

    /**
     * Initialize - add mouse click event
     */
    public void init() {
        mouseListner = new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                InfraPoint ip = getClickedMarker(e.getPoint());
                if (ip == null) {
                    return;
                }
                if (e.getButton() == MouseEvent.BUTTON3) {
                    InfraObject io = ip.getInfraObject();
                    if (io != null) {
                        InfraInfoDialog rid = new InfraInfoDialog(io, frame, true);
                        int w = rid.getWidth();
                        int h = rid.getHeight();
                        int sx = e.getXOnScreen();
                        int sy = e.getYOnScreen();
                        Dimension dim = Toolkit.getDefaultToolkit().getScreenSize();
                        if (dim.width < sx + w) {
                            sx -= w;
                        }
                        if (dim.height < sy + h) {
                            sy -= h;
                        }
                        rid.setLocation(sx, sy);
                        rid.setVisible(true);
                    }
                } else if (ip.isShowLabel()) {
                    ip.setLabelVisible(false);
                } else {
                    ip.setLabelVisible(true);
                }
                map.repaint();
            }
        };
        jmKit.getMainMap().addMouseListener(mouseListner);
        GeoPosition initCenter = new GeoPosition(initLatitude, initLongitude);
        jmKit.setAddressLocation(initCenter);
        jmKit.setZoom(initZoom);
        Config.addConfigChangeListener(new AbstractConfigChangeListener() {
            @Override
            public void MapProviderChanged(MapProvider mapProvider) {
                GeoPosition loc = jmKit.getAddressLocation();
                
                jmKit.setTileFactory(mapProvider.getProvider().getTileFactory());
                jmKit.setAddressLocation(loc);
            }

        });
    }

    private void _setMarkers(Set<InfraPoint> markers) {
        waypoints = markers;
        if (this.routeList != null) {
            for (InfraObject ip : routeList) {
                for (InfraPoint wp : markers) {
                    if (!wp.getInfraObject().equals(ip)) {
                        continue;
                    }
                    wp.setMarkerType(InfraPoint.MarkerType.BLUE);
                    break;
                }
            }
        }
    }

    private void setMarkers(Set<InfraPoint> markers, Route route) {
        this._setMarkers(markers);
        this.jmKit.getMainMap().setOverlayPainter(new RoutePainter(markers, route, this.jmKit));
        this.jmKit.getMainMap().setOverlayPainter(new PointPainter(markers, this.jmKit));
    }

    /**
     * Set markers in the map (main renderer)
     *
     * @param markers
     */
    private void setMarkers(Set<InfraPoint> markers) {
        this._setMarkers(markers);
        this.jmKit.getMainMap().setOverlayPainter(new PointPainter(markers, this.jmKit));
    }

    /**
     * Return clicked marker
     *
     * @param point
     * @return
     */
    public InfraPoint getClickedMarker(Point point) {
        if (waypoints == null) {
            return null;
        }
        Iterator<InfraPoint> itr = waypoints.iterator();
        while (itr.hasNext()) {
            InfraPoint marker = itr.next();
            Rectangle markerRect = getMarkerRect(marker);
            if (markerRect.contains(point)) {
                return marker;
            }
        }
        return null;
    }

    /**
     * Set markers of infra object in given route
     *
     * @param route
     */
    public void showRoute(Route route) {
        Set<InfraPoint> markers = new HashSet<InfraPoint>();

        for (RNode rnode : route.getRNodes()) {
            if (rnode.label.isEmpty()) {
                continue;
            }
            InfraPoint ip = new InfraPoint(rnode);
            ip.setLabelLoc(getLabelLoc(infra.getCorridor(rnode.corridor).dir));
            markers.add(ip);

            if (infra.isEntrance(rnode) && rnode.meters.size() > 0) {
                List<String> meter_names = rnode.meters;
                ip.setName(ip.getName() + " - [" + meter_names.get(0) + "]");
            }
        }
        this.setMarkers(markers, route);
        this.selected_route = route;
    }

    /**
     * Set markers of infra object in given route
     *
     * @param routes
     */
    public void showRoutes(List<Route> routes) {
        Set<InfraPoint> markers = new HashSet<InfraPoint>();
        
        for(Route route : routes) {
            for (RNode rnode : route.getRNodes()) {
                if (rnode.label.isEmpty()) {
                    continue;
                }
                InfraPoint ip = new InfraPoint(rnode);
                ip.setLabelLoc(getLabelLoc(infra.getCorridor(rnode.corridor).dir));
                markers.add(ip);

                if (infra.isEntrance(rnode) && rnode.meters.size() > 0) {
                    List<String> meter_names = rnode.meters;
                    ip.setName(ip.getName() + " - [" + meter_names.get(0) + "]");
                }
            }
        }
        this.setMarkers(markers);
    }    
    
    /**
     * Set markers of corridor
     *
     * @param corridor
     */
    public void showCorridor(Corridor corridor) {
        ArrayList<InfraObject> objs = new ArrayList<InfraObject>();
        objs.addAll(getRNodesFromCorridor(corridor));
        this.showInfraObjects(objs);
    }

    /**
     * Set markers of corridors
     *
     * @param corridors
     */
    public void showCorridors(List<Corridor> corridors) {
        ArrayList<InfraObject> objs = new ArrayList<InfraObject>();
        for (Corridor c : corridors) {
            objs.addAll(getRNodesFromCorridor(c));
        }
        this.showInfraObjects(objs);
    }

    /**
     * Set markers of given infra objects
     *
     * @param objs
     */
    public void showInfraObjects(List<InfraObject> objs) {

        Set<InfraPoint> markers = getMarkers(objs);
        checkDuplicateLocation(markers);
        this.setMarkers(markers);
    }

    public void showInfraPoint(InfraPoint ip) {
        Set<InfraPoint> markers = new HashSet<InfraPoint>();
        markers.add(ip);
        this.setMarkers(markers);
    }

    public void showInfraPoints(List<InfraPoint> ips) {
        Set<InfraPoint> markers = new HashSet<InfraPoint>();
        markers.addAll(ips);
        this.setMarkers(markers);
    }

    /**
     * Set markers of given infra objects
     *
     * @param objs
     */
    public void showRNodes(List<RNode> objs) {
        List<InfraObject> cobjs = new ArrayList<InfraObject>();
        for (RNode obj : objs) {
            cobjs.add(obj);
        }
        this.showInfraObjects(cobjs);
    }
    
    /**
     * Add markers of given infra objects
     *
     * @param rnodes
     */
    public void addShowRNodes(List<RNode> rnodes) {
        ArrayList<InfraObject> objs = new ArrayList<InfraObject>();
        for(RNode rnode : rnodes) {
            objs.add(rnode);
        }
        this.waypoints.addAll(getMarkers(objs));
        checkDuplicateLocation(waypoints);
        this.setMarkers(waypoints);
    }    

    /**
     * Add markers of given infra objects
     *
     * @param objs
     */
    public void addShowInfraObjects(List<InfraObject> objs) {
        Set<InfraPoint> markers = getMarkers(objs);
        this.waypoints.addAll(getMarkers(objs));
        checkDuplicateLocation(waypoints);
        this.setMarkers(waypoints);
    }

    /**
     * Add markers of given infra objects
     *
     * @param c
     */
    public void addShowCorridor(Corridor c) {
        ArrayList<InfraObject> rnodes = getRNodesFromCorridor(c);
        this.waypoints.addAll(getMarkers(rnodes));
        checkDuplicateLocation(waypoints);
        this.setMarkers(waypoints);
    }

    /**
     * Return markers from infra object array
     *
     * @param objs
     * @return
     */
    public Set<InfraPoint> getMarkers(List<InfraObject> objs) {
        Set<InfraPoint> markers = new HashSet<InfraPoint>();

        for (InfraObject o : objs) {
            if (infra.isRNode(o)) {
                RNode rn = (RNode) o;
                InfraPoint ip = new InfraPoint(rn);
                Corridor c = infra.getCorridor(rn.corridor);
                ip.setLabelLoc(getLabelLoc(c.dir));
                markers.add(ip);
            } else if (infra.isDetector(o)) {
                Detector d = (Detector) o;
                RNode rn = infra.getRNode(d.rnode_name);
                InfraPoint ip = new InfraPoint(d.name, rn.lat, rn.lon);
                ip.setInfraObject(d);
                Corridor c = infra.getCorridor(rn.corridor);
                ip.setLabelLoc(getLabelLoc(c.dir));
                markers.add(ip);
            } else if (infra.isMeter(o)) {
                Meter m = (Meter) o;
                RNode rn = infra.getRNode(m.rnode_name);
                InfraPoint ip = new InfraPoint(m.name, rn.lat, rn.lon);
                ip.setInfraObject(m);
                Corridor c = infra.getCorridor(rn.corridor);
                ip.setLabelLoc(getLabelLoc(c.dir));
                markers.add(ip);
            }
        }
        return markers;
    }

    /**
     * Return rnode list from corridor
     *
     * @param corridor
     * @return
     */
    private ArrayList<InfraObject> getRNodesFromCorridor(Corridor corridor) {
        ArrayList<InfraObject> objs = new ArrayList<InfraObject>();
        for (String rnd_name : corridor.rnodes) {
            RNode rnode = infra.getRNode(rnd_name);
            if (infra.isAvailableStation(rnode)) {
                objs.add(rnode);
            } else if (infra.isEntrance(rnode) || infra.isExit(rnode)) {
                objs.add(rnode);
            }
        }
        return objs;
    }

    /**
     * Return label location of marker
     *
     * @param dir
     * @return
     */
    private LABEL_LOC getLabelLoc(String dir) {
        if ("EB".equals(dir)) {
            return LABEL_LOC.BOTTOM;
        }
        if ("WB".equals(dir)) {
            return LABEL_LOC.TOP;
        }
        if ("SB".equals(dir)) {
            return LABEL_LOC.LEFT;
        }
        return LABEL_LOC.RIGHT;
    }

    /**
     * Remove and integrate duplicated location from the marker list
     *
     * @param markers
     */
    private void checkDuplicateLocation(Set<InfraPoint> markers) {
        InfraPoint[] points = markers.toArray(new InfraPoint[markers.size()]);
        ArrayList<Integer> toRemoveIndex = new ArrayList<Integer>();
        for (int i = 0; i < points.length - 1; i++) {
            for (int j = i + 1; j < points.length; j++) {
                if (points[i].getInfraObject().equals(points[j].getInfraObject())) {
                    toRemoveIndex.add(j);
                }
                GeoPosition pos1 = points[i].getPosition();
                GeoPosition pos2 = points[j].getPosition();
                if (pos1.equals(pos2)) {
                    points[i].setName(points[i].getName() + ", " + points[j].getName());
                    toRemoveIndex.add(j);
                }
            }
        }
        for (int idx : toRemoveIndex) {
            markers.remove(points[idx]);
        }
    }

    /**
     * Set points to draw line
     *
     * @param list
     */
    public void setRouteAsBlueMarker(InfraObject[] list) {
        this.routeList = list;
        this.repaint();
    }

    /**
     * Return marker that indicate given infra object
     *
     * @param obj
     * @return
     */
    private InfraPoint findPointFromMap(InfraObject obj) {
        for (InfraPoint p : this.waypoints) {
            if (p.getInfraObject().equals(obj)) {
                return p;
            }
        }
        return null;
    }

    /**
     * Return rectangle of given marker
     *
     * @param marker
     * @return
     */
    private Rectangle getMarkerRect(InfraPoint marker) {
        int w, h, x, y;
        Image markerImg = marker.getMarkerImg();
        w = markerImg.getWidth(map);
        h = markerImg.getHeight(map);
        x = Math.round(-1 * ((float) w) / 2);
        y = Math.round(-1 * ((float) h));
        GeoPosition gp = marker.getPosition();
        Point2D gp_pt = map.getTileFactory().geoToPixel(gp, map.getZoom());
        Rectangle rect = map.getViewportBounds();
        Point converted_gp_pt = new Point((int) gp_pt.getX() - rect.x, (int) gp_pt.getY() - rect.y);
        return new Rectangle(converted_gp_pt.x + x, converted_gp_pt.y + y, w, h);
    }

    /**
     * Set center position
     *
     * @param infraObject
     */
    public void setCenter(InfraObject infraObject) {
        InfraType type = infraObject.getInfraType();
        RNode rnode = null;
        if (type.isRnode()) {
            rnode = (RNode) infraObject;
        } else if (type.isDetector()) {
            Detector d = (Detector) infraObject;
            rnode = infra.getRNode(d.rnode_name);
        } else if (type.isMeter()) {
            Meter m = (Meter) infraObject;
            Detector d = null;
            if (!m.passage.isEmpty()) {
                d = infra.getDetector(m.passage.get(0));
            }
            if (d == null && !m.merge.isEmpty()) {
                d = infra.getDetector(m.merge.get(0));
            }
            if (d == null) {
                JOptionPane.showMessageDialog(null, "Cannot identify " + m.name + "'s location");
                return;
            }
            rnode = infra.getRNode(d.rnode_name);
        }
        if (rnode != null) {
            map.setCenterPosition(new GeoPosition(rnode.lat, rnode.lon));
        }
    }

    public void setCenter(InfraPoint infraPoint) {
        map.setCenterPosition(infraPoint.getPosition());
    }

    public void setCenter(double lat, double lon) {
        map.setCenterPosition(new GeoPosition(lat, lon));
    }

    /**
     * Zoom as given zoom level and center the given point
     *
     * @param marker
     * @param zoomLevel
     */
    public void zoom(int zoomLevel) {
        map.setZoom(zoomLevel);
    }

    /**
     * Set main frame
     *
     * @param frame
     */
    public void setFrame(JFrame frame) {
        this.frame = frame;
    }

    /**
     * Remove mouse listener
     */
    public void removeMouseListener() {
        this.map.removeMouseListener(mouseListner);
    }

    /**
     * Return infra points that marked on the map
     *
     * @return
     */
    public InfraPoint[] getPoints() {
        if (this.waypoints == null) {
            return null;
        }
        return this.waypoints.toArray(new InfraPoint[this.waypoints.size()]);
    }

    public void repaint() {
        if (this.waypoints != null) {
            this.setMarkers(waypoints);
        }
    }

    public void clear() {
        this.setMarkers(new HashSet<InfraPoint>());
        this.routeList = null;
    }

    public GeoPosition getGeoPosition(Point2D d) {
        return map.convertPointToGeoPosition(d);
    }

}
