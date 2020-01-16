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
package common.route.editor;

import java.awt.Color;

/**
 *
 * @author Chongmyung Park <chongmyung.park@gmail.com>
 */
public enum CellFormat {

        DEFAULT("#FFFFFF"),
        DIR1_MAINLINE("#B0E1C0"),
        DIR1_RAMP("#83B092"),
        DIR2_MAINLINE("#D1EEF3"),
        DIR2_RAMP("#A1B9BD");

        private String color;

        CellFormat(String color) {
            this.color = color;
        }

        public Color getColor() {
            return new Color(
                    Integer.valueOf(this.color.substring(1, 3), 16),
                    Integer.valueOf(this.color.substring(3, 5), 16),
                    Integer.valueOf(this.color.substring(5, 7), 16));
        }

        @Override
        public String toString() {
            return this.color;
        }
}
