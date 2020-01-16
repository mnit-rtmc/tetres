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
package common.infra;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public class Detector extends InfraObject {

    public String label;
    public String rnode_name;
    public String station_id;
    public String category;
    public String controller;
    public Float field;
    public Integer lane;
    public Integer shift;
    public Boolean abandoned;

    public boolean is_abandoned() {
        return this.abandoned;
    }

    public boolean is_auxiliary_lane() {
        return this.abandoned;
    }

    public boolean is_HOVT_lane() {
        return this.abandoned;
    }

    public boolean is_wavetronics() {
        return this.abandoned;
    }

    public boolean is_CD_lane() {
        return this.abandoned;
    }

    public boolean is_mainline() {
        return this.abandoned;
    }

    public LaneType getLaneType() {
        return LaneType.valueOf(this.category);
    }
}
