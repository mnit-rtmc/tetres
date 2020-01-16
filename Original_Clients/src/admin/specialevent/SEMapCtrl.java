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

import common.ui.map.InfraPoint;
import common.ui.map.MapHelper;
import common.ui.map.TMCProvider;
import common.ui.map.TileServerFactory;
import java.awt.Point;
import java.awt.event.MouseAdapter;
import java.awt.event.MouseEvent;
import java.util.ArrayList;
import java.util.List;
import org.jdesktop.swingx.JXMapKit;
import org.jdesktop.swingx.mapviewer.GeoPosition;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class SEMapCtrl {

    public interface ICoordinateUpdated {

        public void coordinateUpdated(GeoPosition coordinate);
    }

    private JXMapKit compMap;
    private MapHelper mapHelper;
    protected final int initZoom = 4;
    protected final double initLatitude = 44.974878;
    protected final double initLongitude = -93.233414;
    protected GeoPosition selectedCoordinate;
    private List<ICoordinateUpdated> changeListeners = new ArrayList<>();

    public SEMapCtrl(JXMapKit jxMapKit) {
        this.compMap = jxMapKit;
        initMap();
    }

    public void initMap() {
        this.mapHelper = new MapHelper(this.compMap);
        this.compMap.setTileFactory(TileServerFactory.getTileFactory());
        GeoPosition initCenter = new GeoPosition(this.initLatitude, this.initLongitude);

        this.compMap.setAddressLocation(initCenter);
        this.compMap.setZoom(this.initZoom);
        this.compMap.getMiniMap().setVisible(false);

        this.mapHelper.removeMouseListener();

        this.compMap.getMainMap().addMouseListener(new MouseAdapter() {

            @Override
            public void mouseReleased(MouseEvent e) {
                if (!e.isPopupTrigger()) {
                    return;
                }
                mapHelper.clear();
                Point point = e.getPoint();
                selectedCoordinate = compMap.getMainMap().convertPointToGeoPosition(point);
                InfraPoint ip = new InfraPoint("", selectedCoordinate.getLatitude(), selectedCoordinate.getLongitude());
                mapHelper.showInfraPoint(ip);
                for (ICoordinateUpdated listener : changeListeners) {
                    listener.coordinateUpdated(selectedCoordinate);
                }
            }
        });
    }

    public void addCoordinateChangeListener(ICoordinateUpdated listener) {
        this.changeListeners.add(listener);
    }

    public void setPoint(InfraPoint point) {
        this.mapHelper.showInfraPoint(point);
    }

    public void setPoints(List<InfraPoint> points) {
        this.mapHelper.showInfraPoints(points);
    }

    void setCenter(Double lat, Double lon) {
        this.mapHelper.setCenter(lat, lon);
    }
}
