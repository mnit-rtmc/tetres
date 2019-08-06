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

package ticas.common.infra;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public enum InfraType {

    CORRIDOR(Corridor.class, "Corridor"),
    STATION(RNode.class, "Station"),
    ENTRANCE(RNode.class, "Entrance"),
    EXIT(RNode.class, "Exit"),
    METER(Meter.class, "Meter"),
    DETECTOR(Detector.class, "Detector"),
    RNODE(RNode.class, "RNode"),
    ACCESS(RNode.class, "Access"),
    INTERSECTION(RNode.class, "Intersection"),
    DMS(DMS.class, "DMS"),
    INTERCHANGE(RNode.class, "Interchange"), 
    NONE(null, "None");

    private Class typeClass;
    private String typeTag;

    InfraType(Class c, String tag) {
        this.typeClass = c;
        this.typeTag = tag;
    }

    public boolean isStation() {
        return (this == STATION);
    }

    public boolean isMeter() {
        return (this == METER);
    }

    public boolean isDetector() {
        return (this == DETECTOR);
    }

    public boolean isDMS() {
        return (this == DMS);
    }

    public boolean isEntrance() {
        return (this == ENTRANCE);
    }

    public boolean isExit() {
        return (this == EXIT);
    }

    public boolean isRnode() {
        return (this == RNODE || this == STATION || this == ENTRANCE || this == EXIT || this == INTERSECTION || this == INTERCHANGE || this == ACCESS);
    }

    @Override
    public String toString() {
        return this.typeTag;
    }
}
