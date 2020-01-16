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

import common.infra.Infra;
import common.infra.InfraObject;
import common.infra.RNode;
import java.awt.Color;
import java.awt.Image;
import java.awt.Point;
import java.awt.Toolkit;
import java.net.URL;
import org.jdesktop.swingx.mapviewer.GeoPosition;
import org.jdesktop.swingx.mapviewer.Waypoint;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class InfraPoint extends Waypoint {

    public enum LABEL_LOC { TOP, BOTTOM, RIGHT, LEFT; }
        public enum MarkerType { RED("red"), BLUE("blue"), PURPLE("purple"), GREEN("green"), GRAY("gray"),JBLUE("jblue"),YELLOW("yellow"), SITENONE("gray"),SITEON("jblue");
        String desc;
        MarkerType(String desc) {
            this.desc = desc;
        }        
    }
    protected String name;
    protected Image markerImg;
    protected boolean showLabel = true;
    protected Color color = Color.black;
    protected LABEL_LOC labelLoc = LABEL_LOC.RIGHT;
    protected InfraObject infraObject;
    public int offset_x = 0;
    public int offset_y = 0;
    protected Infra infra = Infra.getInstance();
    public MarkerType markerType = null;
    
    public InfraPoint(String name, double latitude, double longitude) {
        super(latitude, longitude);
        this.name = name;
        setMarkerType(MarkerType.RED);
    }
    
    public void setMarkerType(MarkerType type) {
        Toolkit toolkit = Toolkit.getDefaultToolkit();
        URL imageUrl = getClass().getResource("/common/ui/map/resources/marker-" +type.desc+".png");
        if(imageUrl == null) {
            return;
        }
        this.markerType = type;        
        markerImg = toolkit.getImage(imageUrl);        
    }
    
    
    public InfraPoint(RNode rnode) {        
        this.setPosition(new GeoPosition(rnode.lat, rnode.lon));
        this.infraObject = rnode;
        if(infra.isStation(rnode)) {
            this.name = rnode.station_id;
        } else if(infra.isEntrance(rnode)) {
            this.name = "Ent (" + rnode.label + ")";
        } else if(infra.isExit(rnode)) {
            this.name = "Ext (" + rnode.label + ")";            
        } else {
            this.name = rnode.getInfraType() + "(" + rnode.label +")";
        }
        if(infra.isStation(rnode)) setMarkerType(MarkerType.RED);
        else if(infra.isEntrance(rnode)) setMarkerType(MarkerType.GREEN);
        else if(infra.isExit(rnode)) setMarkerType(MarkerType.PURPLE);
        else setMarkerType(MarkerType.GRAY);
    }
    
    public InfraPoint(String name, double latitude, double longitude, MarkerType mtype) {        
        this.setPosition(new GeoPosition(latitude, longitude));
        this.name = name;        
        setMarkerType(mtype);
    }
       
    public Image getMarkerImg() {
        return this.markerImg;
    }
    
    public String getName() {
        return name;
    }

    public boolean isShowLabel() {
        return showLabel;
    }

    public Color get_labelColor() {
        return this.color;
    }

    public void setName(String name) {
        this.name = name;
    }

    public void setLabelVisible(boolean b) {
        this.showLabel = b;
    }

    public void setLabelLoc(LABEL_LOC labelLoc) {
        this.labelLoc = labelLoc;
    }
    
    public LABEL_LOC getLabelLoc() {
            return this.labelLoc;
        }
    
    public Point getLabelLocation(int sw, int sh) {
        int x=0, y=0;
        int iw = this.markerImg.getWidth(null);
        int ih = this.markerImg.getHeight(null);
        if(this.labelLoc == LABEL_LOC.TOP) {
            x = -1 * sw/2;
            y = -1 * (ih + 5);
        }
        else if(this.labelLoc == LABEL_LOC.BOTTOM) {
            x = -1 * sw/2;
            y = 10;
        }        
        else if(this.labelLoc == LABEL_LOC.RIGHT) {
            x = 10;
            y = -5;
        }        
        else if(this.labelLoc == LABEL_LOC.LEFT) {
            x = -1 * (sw + 5 + iw/2);
            y = -5;
        }        
        return new Point(x, y);
    }

    public RNode getRNode() {
        if(infra.isRNode(this.infraObject)) {
            return (RNode)this.infraObject;
        }
        return null;
    }
    
    public void setInfraObject(InfraObject o) {
        this.infraObject = o;
    }

    public InfraObject getInfraObject() {
        return infraObject;
    }
}