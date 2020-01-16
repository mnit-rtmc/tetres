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
package ncrtes.targetstation.map;

import common.infra.RNode;
import common.route.Route;
import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.Point;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.geom.Point2D;
import java.util.ArrayList;
import java.util.Set;
import org.jdesktop.swingx.JXMapKit;
import org.jdesktop.swingx.JXMapViewer;
import org.jdesktop.swingx.mapviewer.GeoPosition;
import org.jdesktop.swingx.painter.Painter;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TSRoutePainter implements Painter<JXMapViewer> {

    private ArrayList<GeoPosition> region;
    private JXMapKit jmKit;
    private Set<TSInfraPoint> markers;

    public TSRoutePainter(Set<TSInfraPoint> markers, Route route, JXMapKit jmKit) {
        this.markers = markers;
        this.jmKit = jmKit;        
        this.region = new ArrayList<>();
        for (RNode rnode : route.getRNodes()) {
            region.add(new GeoPosition(rnode.lat, rnode.lon));
        }
    }

    @Override
    public void paint(Graphics2D g, JXMapViewer map, int w, int h) {

        // convert from viewport to world bitmap
        final Rectangle rect = this.jmKit.getMainMap().getViewportBounds();
        g.translate(-rect.x, -rect.y);

        for(TSInfraPoint wp : this.markers) {
            TSInfraPoint ip = (TSInfraPoint) wp;
            int markerX = 0, markerY = 0;
            Image markerImg = ip.getMarkerImg();
            markerX = Math.round(-1 * ((float) markerImg.getWidth(map)) / 2);
            markerY = Math.round(-1 * ((float) markerImg.getHeight(map)));
            g.drawImage(markerImg, markerX, markerY, null);

            if (ip.isShowLabel()) {
                String name = ip.getName();
                if (name == null) {
                    name = ip.getInfraObject().name;
                }
                Point p = ip.getLabelLocation(g.getFontMetrics().stringWidth(name), g.getFontMetrics().getHeight());
                g.setPaint(ip.get_labelColor());
                g.drawString(name, p.x + ip.offset_x, p.y + ip.offset_y);
            }        
        }
        

        // do the drawing
        g.setColor(Color.RED);
        g.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g.setStroke(new BasicStroke(2));

        int lastX = -1;
        int lastY = -1;
        for (final GeoPosition gp : this.region) {
            // convert geo to world bitmap pixel
            final Point2D pt = this.jmKit.getMainMap().getTileFactory().geoToPixel(gp, this.jmKit.getMainMap().getZoom());
            if (lastX != -1 && lastY != -1) {
                g.drawLine(lastX, lastY, (int) pt.getX(), (int) pt.getY());
            }
            lastX = (int) pt.getX();
            lastY = (int) pt.getY();
        }
    }

}
