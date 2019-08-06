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

import java.awt.Graphics2D;
import java.awt.Image;
import java.awt.Point;
import java.util.Set;
import org.jdesktop.swingx.JXMapKit;
import org.jdesktop.swingx.JXMapViewer;
import org.jdesktop.swingx.mapviewer.Waypoint;
import org.jdesktop.swingx.mapviewer.WaypointPainter;
import org.jdesktop.swingx.mapviewer.WaypointRenderer;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class TSPointPainter extends WaypointPainter {

    public TSPointPainter(Set<TSInfraPoint> markers, JXMapKit jmKit) {
        this.setWaypoints(markers);
        this.setRenderer(new WaypointRenderer() {
            @Override
            public boolean paintWaypoint(Graphics2D g, JXMapViewer map, Waypoint wp) {
                TSInfraPoint ip = (TSInfraPoint) wp;
                int markerX = 0, markerY = 0;
                Image markerImg = ip.getMarkerImg();
                if(markerImg == null) {
                    return false;
                }
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
                return true;
            }
        });
    }
}
